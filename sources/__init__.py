from concurrent.futures import ThreadPoolExecutor, as_completed

from sources.github import fetch_github
from sources.hackernews import fetch_hackernews
from sources.zhihu import fetch_zhihu
from sources.toutiao import fetch_toutiao

FETCHERS = [fetch_github, fetch_hackernews, fetch_zhihu, fetch_toutiao]


def fetch_all_sources() -> list:
    articles = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(f): f.__module__ for f in FETCHERS}
        for future in as_completed(futures):
            try:
                result = future.result()
                articles.extend(result)
                print(f"  [{futures[future]}] 获取 {len(result)} 条")
            except Exception as e:
                print(f"  [{futures[future]}] 获取失败: {e}")
    return articles
