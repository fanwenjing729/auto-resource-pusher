from datetime import datetime, timedelta
import requests
from models import Article


def fetch_github() -> list[Article]:
    """获取 GitHub 近一周创建的高星仓库 (stars > 50)"""
    try:
        days_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        url = "https://api.github.com/search/repositories"
        params = {
            "q": f"stars:>50 created:>={days_ago}",
            "sort": "stars",
            "order": "desc",
            "per_page": 10,
        }
        headers = {"Accept": "application/vnd.github+json"}
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        articles = []
        for repo in data.get("items", []):
            desc = repo.get("description") or ""
            articles.append(Article(
                title=repo.get("full_name", ""),
                url=repo.get("html_url", ""),
                summary=desc[:150],
                source="GitHub",
                metrics={
                    "stars": repo.get("stargazers_count", 0),
                    "forks": repo.get("forks_count", 0),
                }
            ))
        return articles
    except Exception:
        return []
