import requests
from models import Article
from config import FEISHU_WEBHOOK_URL, FEISHU_KEYWORD


def _md_link(title: str, url: str) -> str:
    """构建 Markdown 链接，转义标题中的特殊字符防止语法破坏"""
    safe_title = title.replace("]", "\\]").replace(")", "\\)")
    return f"[{safe_title}]({url})"


def push_to_feishu(articles: list[Article]) -> bool:
    """推送文章列表到飞书，先试卡片格式，失败则降级为文本"""
    if not FEISHU_WEBHOOK_URL:
        print("  未配置 FEISHU_WEBHOOK_URL，跳过推送")
        return False

    card = _build_card(articles)
    resp = requests.post(FEISHU_WEBHOOK_URL, json=card, timeout=10)
    body = resp.json()

    if body.get("code") == 0:
        print("  推送成功（卡片）")
        return True

    if body.get("code") == 19024:
        print("  卡片被关键词拦截(code=19024)，尝试文本格式...")
        text = _build_text(articles)
        resp = requests.post(FEISHU_WEBHOOK_URL, json=text, timeout=10)
        body = resp.json()
        if body.get("code") == 0:
            print("  推送成功（文本）")
            return True

    print(f"  推送失败 [{resp.status_code}]: {body}")
    return False


def _build_card(articles: list[Article]) -> dict:
    keyword = f"「{FEISHU_KEYWORD}」" if FEISHU_KEYWORD else ""
    header_text = f"📚 今日资源推荐{keyword}"
    elements = []
    for i, a in enumerate(articles):
        label = a.source
        elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"**{i + 1}. {_md_link(a.title, a.url)}**  _{label}_"
            }
        })
        if a.summary:
            elements.append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": a.summary[:120]
                }
            })
        elements.append({"tag": "hr"})

    return {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {"tag": "plain_text", "content": header_text},
                "template": "blue"
            },
            "elements": elements,
        }
    }


def _build_text(articles: list[Article]) -> dict:
    keyword = f"「{FEISHU_KEYWORD}」" if FEISHU_KEYWORD else ""
    lines = [f"📚 今日资源推荐{keyword}\n"]
    for i, a in enumerate(articles):
        label = a.source
        lines.append(f"**{i + 1}. {_md_link(a.title, a.url)}**  _{label}_")
        if a.summary:
            lines.append(a.summary[:120])
        lines.append("")

    return {
        "msg_type": "text",
        "content": {"text": "\n".join(lines)}
    }
