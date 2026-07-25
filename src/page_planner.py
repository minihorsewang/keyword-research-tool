import logging
import re

logger = logging.getLogger(__name__)


def generate_slug(keyword):
    if not keyword:
        return ""
    slug = keyword.lower()
    slug = re.sub(r"[^a-z0-9\u4e00-\u9fff\s]", "", slug)
    slug = slug.replace(" ", "-")
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug


def suggest_h1(keyword, page_type):
    if page_type == "估價頁":
        return f"{keyword} | 線上估價"
    elif page_type == "用途解決方案頁":
        return f"{keyword} | 印刷解決方案"
    elif page_type == "知識文章":
        return f"{keyword} | 印刷知識"
    else:
        return f"{keyword} | 產品介紹"


def suggest_cta(page_type):
    cta_map = {
        "估價頁": "立即詢價",
        "用途解決方案頁": "瞭解更多",
        "知識文章": "閱讀全文",
        "產品頁": "查看產品",
    }
    return cta_map.get(page_type, "瞭解更多")


def plan_pages(clusters, df):
    logger.info("開始規劃網站頁面")
    pages = []

    for cluster in clusters:
        group_name = cluster["群組名稱"]
        page_type = cluster["建議頁面"]
        if page_type == "可能無關":
            continue
        if group_name in ["可能無關", "其他"]:
            continue

        primary = cluster["主關鍵字"]
        slug = generate_slug(primary)
        h1 = suggest_h1(group_name, page_type)
        cta = suggest_cta(page_type)

        content_direction = f"圍繞「{group_name}」介紹產品特色、適用場景、材質選擇與印刷注意事項。"

        pages.append({
            "頁面名稱": group_name,
            "頁面類型": page_type,
            "主關鍵字": primary,
            "次要關鍵字": cluster["次要關鍵字"],
            "Slug": slug,
            "H1": h1,
            "內容方向": content_direction,
            "CTA": cta,
            "優先級": cluster["優先級"],
            "狀態": "待建立",
            "備註": "",
        })

    pages.sort(key=lambda x: {"高": 0, "中": 1, "低": 2}.get(x["優先級"], 3))
    logger.info(f"頁面規劃完成，共 {len(pages)} 個建議頁面")
    return pages
