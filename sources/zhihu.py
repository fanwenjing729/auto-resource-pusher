import requests
from models import Article


def fetch_zhihu() -> list[Article]:
    """获取掘金热门文章（国内可访问）"""
    try:
        url = "https://api.juejin.cn/recommend_api/v1/article/recommend_all_feed"
        headers = {
            "User-Agent": "AutoResourcePusher/1.0",
            "Content-Type": "application/json",
        }
        data = {"id_type": 2, "sort_type": 200, "cursor": "0", "limit": 15}
        resp = requests.post(url, headers=headers, json=data, timeout=10)
        resp.raise_for_status()
        body = resp.json()

        articles = []
        for item in body.get("data", []):
            info = item.get("item_info", {}).get("article_info") or {}
            author = item.get("item_info", {}).get("author_user_info") or {}
            title = info.get("title", "")
            article_id = info.get("article_id", "")
            brief = info.get("brief", "")[:150]
            articles.append(Article(
                title=title,
                url=f"https://juejin.cn/post/{article_id}",
                summary=brief,
                source="Juejin",
                metrics={
                    "views": info.get("view_count", 0),
                    "likes": info.get("digg_count", 0),
                    "comments": info.get("comment_count", 0),
                }
            ))
        return articles
    except Exception:
        return []
