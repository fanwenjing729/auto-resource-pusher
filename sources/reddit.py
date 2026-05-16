import requests
from models import Article


def fetch_reddit() -> list[Article]:
    """获取 Reddit r/programming 热门帖子"""
    url = "https://www.reddit.com/r/programming/hot.json"
    headers = {"User-Agent": "AutoResourcePusher/1.0"}
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    articles = []
    for child in data.get("data", {}).get("children", [])[:15]:
        post = child["data"]
        articles.append(Article(
            title=post.get("title", ""),
            url=f"https://www.reddit.com{post.get('permalink', '')}",
            summary=post.get("selftext", "")[:150],
            source="Reddit",
            metrics={
                "ups": post.get("ups", 0),
                "comments": post.get("num_comments", 0),
            }
        ))
    return articles
