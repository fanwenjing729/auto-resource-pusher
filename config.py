import os
from dotenv import load_dotenv

load_dotenv()

FEISHU_WEBHOOK_URL = os.environ.get("FEISHU_WEBHOOK_URL", "")
FEISHU_KEYWORD = os.environ.get("FEISHU_KEYWORD", "")
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")

# 关键词权重：命中这些关键词的文章额外加分
KEYWORD_WEIGHTS = {
    "AI": 5, "LLM": 5, "大模型": 5, "GPT": 4, "Claude": 4,
    "机器学习": 4, "深度学习": 4, "Machine Learning": 4, "Deep Learning": 4,
    "安全": 4, "Security": 4, "漏洞": 4, "Vulnerability": 4,
    "开源": 3, "Open Source": 3,
    "Python": 3, "Rust": 3, "Go": 3, "TypeScript": 3,
    "架构": 3, "Architecture": 3, "分布式": 3, "Distributed": 3,
    "数据库": 3, "Database": 3,
    "前端": 2, "Frontend": 2, "后端": 2, "Backend": 2,
    "容器": 2, "Docker": 2, "Kubernetes": 2, "K8s": 2,
}

# 来源权重：不同信息源天然的可信度/价值
SOURCE_WEIGHTS = {
    "GitHub": 5,
    "HackerNews": 4,
    "Juejin": 4,
    "Toutiao": 5,
}
