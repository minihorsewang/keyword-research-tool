import logging
import re

logger = logging.getLogger(__name__)


def classify(df, categories, intent_rules):
    logger.info("開始分類與意圖判斷")
    df = df.copy()

    df["產品大類"] = ""
    df["材質"] = ""
    df["用途"] = ""
    df["加工"] = ""
    df["搜尋意圖"] = ""
    df["地區"] = ""
    df["是否可能無關"] = False

    for idx, row in df.iterrows():
        keyword = str(row.get("原始關鍵字", "")).lower()
        norm = str(row.get("標準化關鍵字", "")).lower()
        text = keyword + " " + norm

        # 產品大類
        product = classify_category(text, categories["product_categories"])
        df.at[idx, "產品大類"] = product

        # 材質
        material = classify_category(text, categories["materials"])
        df.at[idx, "材質"] = material

        # 用途
        usage = classify_category(text, categories["usages"])
        df.at[idx, "用途"] = usage

        # 加工
        process = classify_category(text, categories["processes"])
        df.at[idx, "加工"] = process

        # 搜尋意圖
        intent, is_irrelevant = classify_intent(text, intent_rules)
        df.at[idx, "搜尋意圖"] = intent
        df.at[idx, "是否可能無關"] = is_irrelevant

        # 地區
        region = detect_region(text)
        df.at[idx, "地區"] = region

    logger.info(f"分類完成")
    return df


def classify_category(text, category_list):
    matched = []
    for cat in category_list:
        for kw in cat["keywords"]:
            if kw and kw.lower() in text:
                matched.append(cat["name"])
                break
    if not matched and category_list:
        last = category_list[-1]
        if "其他" in last["name"] or "無關" in last["name"]:
            return last["name"]
    return "、".join(matched) if matched else ""


def classify_intent(text, intent_rules):
    # 無關詞規則應優先檢查
    irrelevant_rules = intent_rules.get("irrelevant", {})
    for kw in irrelevant_rules.get("keywords", []):
        if kw and kw.lower() in text:
            return irrelevant_rules["label"], True
    # 其餘意圖
    for key, rule in intent_rules.items():
        if key == "irrelevant":
            continue
        for kw in rule["keywords"]:
            if kw and kw.lower() in text:
                return rule["label"], False
    return "產品需求", False


def detect_region(text):
    regions = {
        "台北": "台北",
        "新北": "新北",
        "桃園": "桃園",
        "台中": "台中",
        "台南": "台南",
        "高雄": "高雄",
        "基隆": "基隆",
        "新竹": "新竹",
        "苗栗": "苗栗",
        "彰化": "彰化",
        "南投": "南投",
        "雲林": "雲林",
        "嘉義": "嘉義",
        "屏東": "屏東",
        "宜蘭": "宜蘭",
        "花蓮": "花蓮",
        "臺東": "台東",
        "澎湖": "澎湖",
        "金門": "金門",
    }
    for name, label in regions.items():
        if name in text:
            return label
    return ""
