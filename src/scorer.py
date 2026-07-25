import logging
import math

logger = logging.getLogger(__name__)


def score(df, business_rules):
    logger.info("開始評分")
    df = df.copy()
    scoring = business_rules["scoring"]
    sv_bins = scoring["search_volume"]["bins"]
    sv_scores = scoring["search_volume"]["scores"]

    competition_map = {}
    for k, v in scoring["competition"].items():
        competition_map[k] = v
        competition_map[k.lower()] = v
        competition_map[{"low": "低", "medium": "中", "high": "高"}.get(k, k)] = v

    def map_search_volume(val):
        try:
            cleaned = str(val).replace(",", "").replace(" ", "").strip()
            if cleaned == "< 10":
                val_num = 5
            else:
                val_num = float(cleaned)
        except (ValueError, TypeError):
            return 1
        for i in range(len(sv_bins) - 1):
            if sv_bins[i] <= val_num < sv_bins[i + 1]:
                return sv_scores[i]
        return 1

    def map_competition(val):
        if val is None or val == "" or (isinstance(val, float) and math.isnan(val)):
            return 3
        val_str = str(val).strip().lower()
        if val_str in competition_map:
            return competition_map[val_str]
        try:
            num = float(val_str)
            ci_bins = scoring["competition_index"]["bins"]
            ci_scores = scoring["competition_index"]["scores"]
            for i in range(len(ci_bins) - 1):
                if ci_bins[i] <= num <= ci_bins[i + 1]:
                    return ci_scores[i]
        except (ValueError, TypeError):
            pass
        return 3

    df["搜尋量分數"] = df["平均每月搜尋量"].apply(map_search_volume)
    df["競爭難度"] = df["競爭程度"].apply(map_competition)
    df["競爭指數分數"] = df["競爭指數"].apply(map_competition)

    df["交易意圖分數"] = df["搜尋意圖"].apply(lambda x: 5 if x == "高交易意圖" else (3 if x == "產品需求" or x == "用途需求" else 2))
    df["地區分數"] = df["地區"].apply(lambda x: 3 if x else 2)

    def get_capability(product):
        caps = business_rules.get("company_capabilities", {})
        primary = product.split("、")[0] if product else product
        if primary in caps:
            return caps[primary]
        return {"承接": True, "承接能力": 2, "毛利潛力": 2, "主力產品": False, "支援少量": True, "支援急件": False}

    df["承接能力"] = df["產品大類"].apply(lambda x: get_capability(x)["承接能力"])
    df["毛利潛力"] = df["產品大類"].apply(lambda x: get_capability(x)["毛利潛力"])
    df["是否主力產品"] = df["產品大類"].apply(lambda x: get_capability(x)["主力產品"])

    boost_words = business_rules.get("boost_words", [])
    exclude_words = business_rules.get("exclude_words", [])

    def calculate_opportunity(row):
        product = str(row.get("產品大類", ""))
        cap = get_capability(product)

        # 「是否承接」為 false 時分數歸零
        if product and not cap.get("承接", True):
            return 0

        base = (
            row["搜尋量分數"]
            * row["交易意圖分數"]
            * cap["承接能力"]
            * cap["毛利潛力"]
        )
        adjustment = 1.0

        competition_score = (row["競爭難度"] + row["競爭指數分數"]) / 2
        adjustment *= (competition_score / 3.0)

        if cap["主力產品"]:
            adjustment *= 1.2

        keyword_text = str(row.get("原始關鍵字", "")).lower()

        # exclude_words 降權
        for ew in exclude_words:
            if ew.lower() in keyword_text:
                adjustment *= 0.3
                break

        # boost_words 需對照產品支援性
        for bw in boost_words:
            if bw.lower() in keyword_text:
                if bw == "少量" and not cap.get("支援少量", True):
                    continue
                if bw == "急件" and not cap.get("支援急件", False):
                    continue
                adjustment *= 1.15
                break

        # 頁首出價加成（有出價數據代表商業價值較高）
        bid_low = row.get("頁首出價低", None)
        if bid_low is not None and str(bid_low).strip():
            try:
                bid_val = float(str(bid_low).replace(",", "").strip())
                if bid_val > 0:
                    adjustment *= 1.1
            except (ValueError, TypeError):
                pass

        # 三個月變化趨勢
        change = row.get("三個月變化", None)
        if change is not None and str(change).strip():
            change_str = str(change).strip()
            if change_str.startswith("+"):
                adjustment *= 1.05
            elif change_str.startswith("-"):
                adjustment *= 0.95

        return base * adjustment

    df["機會分數"] = df.apply(calculate_opportunity, axis=1)

    # 固定分數尺度：理論最大值約 288，以此為分母
    max_possible = 288.0
    df["標準化分數"] = df["機會分數"].apply(lambda x: min(round(x / max_possible * 100, 1), 100))

    def priority_label(row):
        if row["是否可能無關"]:
            return "可能無關"
        s = row["標準化分數"]
        if s >= 60:
            return "高"
        elif s >= 30:
            return "中"
        else:
            return "低"

    df["優先級"] = df.apply(priority_label, axis=1)

    def reason(row):
        if row["是否可能無關"]:
            return "可能與印刷無關"
        parts = []
        sv = row["搜尋量分數"]
        if sv >= 4:
            parts.append("搜尋量高")
        elif sv <= 2:
            parts.append("搜尋量低")

        intent = row["搜尋意圖"]
        if "交易" in intent:
            parts.append("交易意圖高")

        cap_val = row["承接能力"]
        if cap_val >= 4:
            parts.append("公司可承接")
        elif cap_val <= 1:
            parts.append("不承接")
        if row["競爭難度"] >= 4:
            parts.append("競爭度低")
        elif row["競爭難度"] <= 2:
            parts.append("競爭度高")

        return "、".join(parts) if parts else "一般關鍵字"

    df["評分原因"] = df.apply(reason, axis=1)

    logger.info(f"評分完成，高優先: {(df['優先級']=='高').sum()}，中優先: {(df['優先級']=='中').sum()}，低優先: {(df['優先級']=='低').sum()}")
    return df
