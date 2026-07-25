import csv
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def load_overrides(config_dir, input_dir):
    json_path = Path(config_dir) / "override_rules.json"
    csv_path = Path(input_dir) / "override.csv"

    classify_rules = {}
    cluster_rules = {}

    # 載入 JSON
    if json_path.exists():
        import json
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for entry in data.get("classify", []):
            kw = entry.get("keyword", "").strip().lower()
            if kw:
                classify_rules[kw] = {
                    "產品大類": entry.get("產品大類", "").strip(),
                    "材質": entry.get("材質", "").strip(),
                    "用途": entry.get("用途", "").strip(),
                    "加工": entry.get("加工", "").strip(),
                }
        for entry in data.get("cluster", []):
            kw = entry.get("keyword", "").strip().lower()
            if kw and entry.get("群組名稱", "").strip():
                cluster_rules[kw] = entry["群組名稱"].strip()
        logger.info(f"載入 JSON 覆寫規則: {len(classify_rules)} 分類, {len(cluster_rules)} 分群")

    # 載入 CSV
    if csv_path.exists():
        with open(csv_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                kw = row.get("keyword", "").strip().lower()
                if not kw:
                    continue
                if any(row.get(k, "").strip() for k in ["產品大類", "材質", "用途", "加工"]):
                    classify_rules[kw] = {
                        "產品大類": row.get("產品大類", "").strip(),
                        "材質": row.get("材質", "").strip(),
                        "用途": row.get("用途", "").strip(),
                        "加工": row.get("加工", "").strip(),
                    }
                group = row.get("群組名稱", "").strip()
                if group:
                    cluster_rules[kw] = group
        logger.info(f"載入 CSV 覆寫規則: 分類/分群合併完成")

    logger.info(f"總計: {len(classify_rules)} 分類覆寫, {len(cluster_rules)} 分群覆寫")
    return classify_rules, cluster_rules


def apply_classify_overrides(df, classify_rules):
    if not classify_rules:
        return df
    df = df.copy()
    matched = 0
    for idx, row in df.iterrows():
        norm = str(row.get("標準化關鍵字", "")).lower().strip()
        if norm in classify_rules:
            rule = classify_rules[norm]
            for field in ["產品大類", "材質", "用途", "加工"]:
                if rule.get(field):
                    df.at[idx, field] = rule[field]
            matched += 1
    if matched:
        logger.info(f"套用 {matched} 筆分類覆寫")
    return df


def apply_cluster_overrides(clusters, df, cluster_rules):
    if not cluster_rules:
        return clusters
    df = df.copy()
    # 收集每個關鍵字指定的群組
    keyword_group = {}
    for idx, row in df.iterrows():
        norm = str(row.get("標準化關鍵字", "")).lower().strip()
        if norm in cluster_rules:
            keyword_group[norm] = cluster_rules[norm]

    if not keyword_group:
        return clusters

    # 將被指定群組的關鍵字從原群組移除，加入新群組
    new_clusters = {}
    kept_keywords = set()

    for cluster in clusters:
        group_name = cluster["群組名稱"]
        all_kws = cluster["次要關鍵字"].split("、") if cluster["次要關鍵字"] else []
        if cluster["主關鍵字"]:
            all_kws = [cluster["主關鍵字"]] + all_kws

        remaining = []
        for kw in all_kws:
            kw_lower = kw.strip().lower()
            if kw_lower in keyword_group:
                target = keyword_group[kw_lower]
                if target not in new_clusters:
                    new_clusters[target] = []
                new_clusters[target].append(kw)
                kept_keywords.add(kw)
            else:
                remaining.append(kw)

        if remaining:
            cluster["次要關鍵字"] = "、".join(remaining[1:])
            cluster["主關鍵字"] = remaining[0]

    # 加入新的群組
    for group_name, kws in new_clusters.items():
        exists = any(c["群組名稱"] == group_name for c in clusters)
        if not exists:
            clusters.append({
                "群組名稱": group_name,
                "主關鍵字": kws[0],
                "次要關鍵字": "、".join(kws[1:]),
                "群組搜尋量": 0,
                "群組意圖": "",
                "建議頁面": "產品頁",
                "優先級": "中",
            })

    logger.info(f"套用 {len(new_clusters)} 個群組覆寫")
    return clusters
