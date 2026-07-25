import logging
import re

logger = logging.getLogger(__name__)


def cluster_keywords(df, categories):
    logger.info("開始關鍵字分群")
    df = df.copy()

    clusters = {}

    for idx, row in df.iterrows():
        norm = str(row.get("標準化關鍵字", "")).lower()
        product = str(row.get("產品大類", ""))

        # 以產品大類為主要群組
        group_name = product if product else "其他"
        if row["是否可能無關"]:
            group_name = "可能無關"

        # 尋找更精確的群組名稱
        material = str(row.get("材質", ""))
        usage = str(row.get("用途", ""))
        if material and material != "其他材質":
            group_name = material
        elif usage and usage != "其他用途":
            group_name = usage

        if group_name not in clusters:
            clusters[group_name] = {
                "keywords": [],
                "max_intent": 0,
                "total_search_volume": 0,
            }

        clusters[group_name]["keywords"].append(idx)

    cluster_rows = []
    for group_name, info in clusters.items():
        group_df = df.loc[info["keywords"]]
        total_sv = group_df["平均每月搜尋量"].apply(
            lambda x: int(str(x).replace(",", "").replace("<", "0").strip()) if str(x).replace(",", "").strip().lstrip("<").strip().isdigit() else 0
        ).sum()

        intent_order = {"高交易意圖": 5, "產品需求": 4, "用途需求": 3, "價格比較": 3, "廠商尋找": 3, "資訊研究": 2, "可能無關": 1}
        max_intent = ""
        max_intent_score = 0
        for intent, score in intent_order.items():
            if intent in group_df["搜尋意圖"].values:
                if score > max_intent_score:
                    max_intent_score = score
                    max_intent = intent

        primary = group_df.iloc[0]["標準化關鍵字"]
        secondary = [kw for kw in group_df["標準化關鍵字"] if kw != primary]
        priority = group_df["優先級"].value_counts().idxmax() if not group_df["優先級"].empty else "低"

        cluster_rows.append({
            "群組名稱": group_name,
            "主關鍵字": primary,
            "次要關鍵字": "、".join(secondary[:5]),
            "群組搜尋量": total_sv,
            "群組意圖": max_intent,
            "建議頁面": suggest_page_type(group_name, max_intent),
            "優先級": priority,
        })

    result = sorted(cluster_rows, key=lambda x: x["群組搜尋量"], reverse=True)
    logger.info(f"分群完成，共 {len(result)} 個群組")
    return result


def suggest_page_type(group_name, intent):
    pricing_words = ["價格", "報價", "估價", "費用"]
    if any(w in group_name for w in pricing_words) or intent == "價格比較":
        return "估價頁"
    usage_types = ["食品", "冷凍", "化妝品", "物流", "工業", "戶外", "保固", "藥品", "電子"]
    if any(w in group_name for w in usage_types):
        return "用途解決方案頁"
    if intent == "資訊研究":
        return "知識文章"
    if group_name and group_name not in ["可能無關", "其他"]:
        return "產品頁"
    return "產品頁"
