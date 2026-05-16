import requests
from models import Article


def fetch_hackernews() -> list[Article]:
    """获取 Hacker News 首页热门文章"""
    base = "https://hacker-news.firebaseio.com/v0"
    ids = requests.get(f"{base}/topstories.json", timeout=10).json()
    if not ids:
        return []

    articles = []
    for item_id in ids[:30]:
        try:
            item = requests.get(
                f"{base}/item/{item_id}.json", timeout=5
            ).json()
            if item and item.get("title"):
                external_url = item.get("url", "")
                hn_url = f"https://news.ycombinator.com/item?id={item_id}"
                if external_url:
                    summary = f"HN讨论: {hn_url}"
                    url = external_url
                else:
                    summary = ""
                    url = hn_url
                articles.append(Article(
                    title=item.get("title", ""),
                    url=url,
                    summary=summary,
                    source="HackerNews",
                    metrics={
                        "score": item.get("score", 0),
                        "comments": item.get("descendants", 0),
                    }
                ))
        except Exception:
            continue
    return articles
