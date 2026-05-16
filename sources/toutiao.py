import requests
from models import Article


def fetch_toutiao() -> list[Article]:
    """获取今日头条热榜（国内+国际综合热点）"""
    try:
        url = "https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        articles = []
        for item in data.get("data", [])[:20]:
            title = item.get("Title", "")
            article_url = item.get("Url", "")
            hot_value = item.get("HotValue", 0)
            articles.append(Article(
                title=title,
                url=article_url if article_url else f"https://www.toutiao.com/trending/{item.get('ClusterId', '')}",
                summary="",
                source="Toutiao",
                metrics={"hot": hot_value},
            ))
        return articles
    except Exception:
        return []
