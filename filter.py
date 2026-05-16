import requests
from models import Article
from config import KEYWORD_WEIGHTS, SOURCE_WEIGHTS, DEEPSEEK_API_KEY


def rule_filter(articles: list[Article]) -> list[Article]:
    """规则初筛：对文章打分排序，确保每个来源至少有一定数量进入候选"""
    MIN_PER_SOURCE = 5
    for a in articles:
        a.score = _compute_score(a)

    pools = {}
    for a in articles:
        pools.setdefault(a.source, []).append(a)
    for source in pools:
        pools[source].sort(key=lambda x: x.score, reverse=True)

    # 按优先级取每个来源的 Top N
    priority_sources = ["GitHub", "Toutiao", "Juejin", "HackerNews"]
    candidates = []
    for source in priority_sources:
        if source in pools:
            candidates.extend(pools[source][:MIN_PER_SOURCE])

    remaining = [a for a in articles if a not in candidates]
    remaining.sort(key=lambda x: x.score, reverse=True)
    candidates.extend(remaining[:30 - len(candidates)])
    return candidates


def _compute_score(article: Article) -> int:
    score = 0

    title_lower = article.title.lower()
    summary_lower = article.summary.lower()
    for kw, weight in KEYWORD_WEIGHTS.items():
        if kw.lower() in title_lower or kw.lower() in summary_lower:
            score += weight

    score += SOURCE_WEIGHTS.get(article.source, 0)

    m = article.metrics
    stars = m.get("stars", 0) or m.get("ups", 0)
    comments = m.get("comments", 0)
    hn_score = m.get("score", 0)
    views = m.get("views", 0)
    likes = m.get("likes", 0)
    try:
        hot = int(m.get("hot", 0))
    except (ValueError, TypeError):
        hot = 0

    if stars > 500:
        score += 10
    elif stars > 100:
        score += 7
    elif stars > 50:
        score += 3

    if comments > 100:
        score += 8
    elif comments > 20:
        score += 5

    if hn_score > 200:
        score += 8
    elif hn_score > 50:
        score += 4

    if views > 5000:
        score += 8
    elif views > 1000:
        score += 5

    if likes > 100:
        score += 7
    elif likes > 20:
        score += 4

    # 今日头条热度值（百万级）
    if hot > 40000000:
        score += 10
    elif hot > 20000000:
        score += 7
    elif hot > 5000000:
        score += 4

    return score


def ai_filter(articles: list[Article], themes: list = None) -> list[Article]:
    """AI 按主题精选：每个主题选一篇最匹配的文章"""
    if not DEEPSEEK_API_KEY or not articles:
        return articles[:5]

    if themes is None:
        themes = [("精选", "")]

    theme_lines = []
    for i, (name, desc) in enumerate(themes):
        theme_lines.append(f"  {i + 1}. {name}：{desc}")
    theme_text = "\n".join(theme_lines)

    prompt = f"""从以下文章中为每个类别各选一篇最匹配的文章。

类别：
{theme_text}

请返回 5 篇文章的编号，按类别顺序排列（用逗号分隔，如 3,7,12,5,9）。

文章列表：
"""
    for i, a in enumerate(articles):
        prompt += f"{i + 1}. [{a.source}] {a.title}\n"
        if a.summary:
            prompt += f"   摘要：{a.summary[:100]}\n"
        prompt += f"   链接：{a.url}\n\n"

    try:
        resp = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "deepseek-v4-flash",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
            },
            timeout=30,
        )
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        selected = _parse_ai_response(content, articles)
        return selected
    except Exception as e:
        print(f"  AI 筛选失败，回退到规则排序: {e}")
        return articles[:5]


def _parse_ai_response(text: str, articles: list[Article]) -> list[Article]:
    import re
    nums = re.findall(r'\d+', text)
    selected = []
    seen = set()
    for n in nums:
        idx = int(n) - 1
        if 0 <= idx < len(articles) and idx not in seen:
            selected.append(articles[idx])
            seen.add(idx)
    # 不足 5 篇时按规则排序补满
    if len(selected) < 5:
        for a in articles:
            if a not in selected:
                selected.append(a)
            if len(selected) >= 5:
                break
    return selected[:5]
