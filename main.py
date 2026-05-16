import json
import os
import requests
from datetime import datetime, timedelta
from sources import fetch_all_sources
from filter import rule_filter, ai_filter
from pusher import push_to_feishu
from config import DEEPSEEK_API_KEY

HISTORY_FILE = os.path.join(os.path.dirname(__file__), "pushed.json")

# 五篇推送主题
THEMES = [
    ("GitHub最热", "星标最多的开源项目"),
    ("国内热点", "国内科技、经济、学术等方面关注度高的新闻"),
    ("国外热点", "国外科技、经济、学术等方面关注度高的新闻"),
    ("AI发展", "最新 AI 大事件、突破、产品发布"),
    ("国际大事", "国际政治、外交、经济大事件"),
]

SOURCE_EMOJI = {
    "GitHub": "🐙",
    "HackerNews": "🔶",
    "Juejin": "💡",
    "Toutiao": "📰",
    "Reddit": "🤖",
}


def _load_history() -> dict:
    if not os.path.exists(HISTORY_FILE):
        return {}
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        history = json.load(f)
    cutoff = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    return {url: date for url, date in history.items() if date >= cutoff}


def _save_history(articles: list):
    today = datetime.now().strftime("%Y-%m-%d")
    history = _load_history()
    for a in articles:
        history[a.url] = today
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def _check_url_accessible(url: str, source: str = "") -> bool:
    headers = {"User-Agent": "AutoResourcePusher/1.0"}
    timeout = 5
    retries = 1

    if source in ("Juejin", "Toutiao"):
        timeout = 3
    elif source == "GitHub":
        timeout = 8
        retries = 2

    for attempt in range(retries):
        try:
            resp = requests.head(url, headers=headers, timeout=timeout, allow_redirects=True)
            return resp.status_code < 500
        except Exception:
            if attempt < retries - 1:
                continue
    return False


def main():
    print(f"=== 资源推送任务开始 [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ===")

    history = _load_history()
    print(f"  历史记录: {len(history)} 条")

    # 1. 拉取所有信息源
    print("[1/5] 获取信息源...")
    articles = fetch_all_sources()
    print(f"  共获取到 {len(articles)} 篇文章")

    if not articles:
        print("  未获取到任何文章，任务结束")
        return

    # 去重
    new_articles = [a for a in articles if a.url not in history]
    dup_count = len(articles) - len(new_articles)
    if dup_count:
        print(f"  去重过滤: {dup_count} 篇已推送过")
    if not new_articles:
        print("  去重后无新文章，任务结束")
        return

    # 2. 规则初筛
    print("[2/5] 规则初筛...")
    candidates = rule_filter(new_articles)
    print(f"  初筛后保留 {len(candidates)} 篇候选")

    # 3. AI 按主题精选 + 可达性检查
    print("[3/5] AI 主题精选 & 链接检查...")
    if DEEPSEEK_API_KEY:
        picks = ai_filter(candidates, themes=THEMES)
    else:
        picks = candidates[:5]

    # 主题 → 备选来源偏好（按优先级排列）
    THEME_BACKUP_SOURCES = {
        "GitHub最热": ["GitHub"],
        "国内热点": ["Toutiao"],
        "国外热点": ["HackerNews"],
        "AI发展": ["Juejin", "GitHub", "HackerNews"],
        "国际大事": ["Toutiao", "HackerNews"],
    }

    final = []
    failed_themes = []
    for i, a in enumerate(picks):
        theme_name = THEMES[i][0] if i < len(THEMES) else "备选"
        ok = _check_url_accessible(a.url, a.source)
        display_emoji = SOURCE_EMOJI.get(a.source, "📌")
        print(f"  {'  OK' if ok else 'FAIL'} [{theme_name}] {display_emoji} {a.title[:60]}")
        if ok:
            final.append(a)
            a.source = f"{theme_name} {display_emoji}"
        else:
            failed_themes.append((i, theme_name))

    # 按主题补位
    for _, theme_name in failed_themes:
        preferred = THEME_BACKUP_SOURCES.get(theme_name, [])
        found = False
        # 先从偏好来源中找
        for src in preferred:
            for a in candidates:
                if a.source == src and a not in final and a not in picks:
                    if _check_url_accessible(a.url, a.source):
                        display_emoji = SOURCE_EMOJI.get(a.source, "📌")
                        a.source = f"{theme_name} {display_emoji}"
                        print(f"  补位 [{theme_name}] {display_emoji} {a.title[:60]}")
                        final.append(a)
                        found = True
                        break
            if found:
                break
        # 偏好来源没找到，随便补
        if not found:
            for a in candidates:
                if a not in final and a not in picks:
                    if _check_url_accessible(a.url, a.source):
                        display_emoji = SOURCE_EMOJI.get(a.source, "📌")
                        a.source = f"{theme_name} {display_emoji}"
                        print(f"  补位 [{theme_name}] {display_emoji} {a.title[:60]}")
                        final.append(a)
                        found = True
                        break

    print(f"  入选: {len(final)} 篇")

    # 4. 推送
    print("[4/5] 推送到飞书...")
    push_to_feishu(final)

    # 5. 保存记录
    print("[5/5] 保存推送记录...")
    _save_history(final)
    print(f"  已记录 {len(final)} 篇")

    print("=== 任务完成 ===")


if __name__ == "__main__":
    main()
