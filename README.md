# 每日自动推送优质资源 — 完整方案

## 一、需求分析

### 你想做什么
一个每天自动帮你在网上筛选优质资源（技术文章、AI 资讯、开源项目等），然后推送给你看的小工具。

### 核心问题：微信小程序做不到
微信小程序 **没有主动推送能力**。规则如下：
- 用户不打开小程序，你就触达不了他
- "订阅消息"模板只有用户在小程序里点了"订阅"后，你才能发 **一次性** 通知
- 想做"每天自动推"？小程序做不到

### 可选方案对比

| 方案 | 推送频率 | 开发难度 | 审核门槛 | 费用 | 推荐 |
|------|----------|----------|----------|------|------|
| **飞书机器人** | 无限制 | 极低（POST 一个网址） | 无需审核 | 免费 | ⭐ 最强推荐 |
| 微信公众号（订阅号） | 每天1次 | 中 | 需认证（¥300/年） | 认证费 | 次选 |
| 微信服务号 | 每月4次 | 中 | 需认证（¥300/年） | 认证费 | 频率太低 |
| 钉钉机器人 | 无限制 | 极低 | 无需审核 | 免费 | 同类可选 |
| 邮件订阅 | 无限 | 中 | 无 | 服务器费用 | 国内用户习惯差 |
| Telegram Bot | 无限 | 低 | 无 | 免费 | 国内需翻墙 |

## 二、推荐方案：飞书机器人 + 云服务器

### 为什么要用飞书
- **免费**：个人使用完全免费
- **零审核**：不需要开发者资质，不需要认证费
- **无限推送**：一天发 100 条都行
- **手机端体验好**：飞书 App 装在手机上，跟收微信消息一样
- **开发超简单**：就是往一个网址 POST 一段 JSON 数据

### 系统架构

```
┌─────────────────────────────────────────┐
│              云服务器 (24h运行)            │
│                                          │
│  ┌──────────┐  ┌──────────┐  ┌────────┐ │
│  │ 定时任务  │→│ 内容获取  │→│ AI筛选  │ │
│  │ crontab  │  │ RSS/API  │  │ 质量判断 │ │
│  │ 每天9:00 │  │          │  │         │ │
│  └──────────┘  └──────────┘  └────────┘ │
│                       ↓                 │
│                  ┌──────────┐           │
│                  │ 推送模块  │           │
│                  │ POST请求 │           │
│                  └──────────┘           │
└──────────────────────┬──────────────────┘
                       │
                       ↓
              ┌─────────────────┐
              │   飞书 API        │
              │   接收消息        │
              └────────┬────────┘
                       ↓
              ┌─────────────────┐
              │  你的手机飞书App  │
              │  收到推送消息     │
              └─────────────────┘
```

### 费用估算

| 项目 | 费用 |
|------|------|
| 云服务器（腾讯云轻量应用服务器） | ¥68-88/年（活动价） |
| AI API（DeepSeek，每天调用约100次） | ¥1-2/天 ≈ ¥30-60/月 |
| 飞书 | 免费 |
| 域名（可选） | ¥50/年 |
| **合计** | **约 ¥150/月起步** |

省钱技巧：刚开始可以不用 AI，纯靠规则筛选（标题关键词、点赞数、来源权重），成本降到仅服务器 ¥68/年。

## 三、一步一步怎么做

### 第0步：准备工作（现在就能做）

#### 0.1 注册飞书，拿到机器人 Webhook

1. 打开 https://feishu.cn ，下载 Windows 桌面版
2. 用手机号注册飞书
3. 登录后会让你"创建团队"，随便起个名字如「我的资源助手」
4. 进入团队后，左侧消息栏点「+」→ 创建群聊，拉几个人（或只拉自己）
5. 进入群 → 右上角「设置」→「群机器人」→「添加机器人」→「自定义机器人」
6. 给机器人起名（如「资源推荐官」）→ 复制 **Webhook 地址**
7. Webhook 地址长这样：
   ```
   https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxxxxxxxxxxx
   ```

> **注意**：Webhook 地址就是你的"秘密钥匙"，**不要发给别人**。谁拿到都能往你群里发消息。

#### 0.2 验证 Webhook（我用 Python 帮你测）

保存以下代码为 `test_flybook.py`：
```python
import requests
import json

WEBHOOK_URL = "你刚才复制的Webhook地址，替换这里"

data = {
    "msg_type": "text",
    "content": {
        "text": "你好！我是资源推荐官 🤖\n从今天起，每天为你推送优质AI技术资源。"
    }
}

response = requests.post(WEBHOOK_URL, json=data)
print(f"状态码: {response.status_code}")
print(f"返回: {response.json()}")
```

运行后你的飞书群就会收到第一条消息。

### 第1步：搭建项目骨架（本地开发）

项目目录结构：
```
auto-resource-pusher/
├── main.py              # 主程序入口
├── sources.py           # 信息源配置（RSS、API）
├── filter.py            # 内容筛选逻辑
├── pusher.py            # 飞书推送模块
├── requirements.txt     # Python 依赖
├── config.py            # 配置文件
└── README.md            # 本文档
```

#### 1.1 信息源选择（白嫖优先）

| 信息源 | 类型 | 接口 | 备注 |
|--------|------|------|------|
| GitHub Trending | 开源项目 | `https://api.github.com/search/repositories?q=stars:>100+created:>2025-01-01&sort=stars` | 免费，限额60次/小时 |
| Hacker News | 技术新闻 | `https://hacker-news.firebaseio.com/v0/topstories.json` | 免费 |
| 知乎热榜 | 综合 | 需抓取，建议用第三方聚合API | 免费 |
| 阮一峰周刊 | 技术博客 | RSS: `https://feeds.feedburner.com/ruanyifeng` | 免费 |
| 开发者头条 | 技术文章 | 需抓取 | 免费 |
| Product Hunt | 新产品 | API: `https://api.producthunt.com/v2/api/graphql` | 需申请Token |
| Reddit r/programming | 技术讨论 | JSON: `https://www.reddit.com/r/programming/hot.json` | 免费 |

#### 1.2 AI 筛选策略

初级阶段不用 AI，用规则筛选：
```python
# 规则示例
def score(item):
    score = 0
    if item['stars'] > 100:   score += 10   # GitHub高星
    if item['comments'] > 20:  score += 5    # 讨论热烈
    if 'AI' in item['title']:  score += 3    # AI相关权重
    if '安全' in item['title']: score += 3   # 安全相关
    return score
```

进阶后用 DeepSeek API 做语义判断：
```python
import requests

def ai_filter(articles):
    prompt = f"从以下文章标题中选出3篇最有价值的，返回编号：\n"
    for i, a in enumerate(articles):
        prompt += f"{i+1}. {a['title']}\n"
    
    resp = requests.post(
        "https://api.deepseek.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {DEEPSEEK_KEY}"},
        json={
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}]
        }
    )
    return resp.json()['choices'][0]['message']['content']
```

#### 1.3 飞书推送格式

飞书机器人支持富文本消息，你可以推送这样的卡片：

```python
def push_to_feishu(articles):
    content = "📚 **今日优质资源推荐**\n\n"
    for i, a in enumerate(articles):
        content += f"**{i+1}. {a['title']}**\n"
        content += f"{a['summary'][:100]}...\n"
        content += f"🔗 {a['url']}\n\n"
    
    requests.post(WEBHOOK_URL, json={
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {"tag": "plain_text", "content": "📚 今日资源推荐"},
                "template": "blue"
            },
            "elements": [
                {
                    "tag": "markdown",
                    "content": content
                }
            ]
        }
    })
```

### 第2步：部署到云服务器

推荐 **腾讯云轻量应用服务器**：
1. 等双11/618/周年庆买，最低 ¥68/年
2. 选 CentOS 7 或 Ubuntu 22.04
3. 选 2核2G 够用了
4. 地域选离你近的（贵州选成都/重庆节点）

部署步骤：
```bash
# SSH 登录服务器
ssh root@你的服务器IP

# 安装 Python
yum install python3 python3-pip -y   # CentOS
# 或
apt install python3 python3-pip -y   # Ubuntu

# 上传你的代码（在本地电脑执行）
scp -r ./auto-resource-pusher root@服务器IP:/root/

# 安装依赖
pip3 install -r /root/auto-resource-pusher/requirements.txt

# 设置定时任务
crontab -e
# 添加一行：每天早上9点执行
0 9 * * * cd /root/auto-resource-pusher && python3 main.py
```

### 第3步：以后怎么扩展

| 阶段 | 做什么 | 说明 |
|------|--------|------|
| **V1.0**（本周） | 飞书机器人 + 2个信息源 + 规则筛选 | 自己先用起来 |
| **V1.1**（第二周） | 接入 DeepSeek AI筛选 | 提高推荐质量 |
| **V1.2**（第三周） | 支持自定义关键词、信息源 | 个性化配置 |
| **V2.0**（一个月后） | 做成 SaaS，其他人也能订阅 | 接微信公众号 |

## 四、常见问题

### Q：不用电脑它还能推吗？
**能。** 脚本跑在云服务器上，24 小时不关机。你的电脑只用于写代码和部署，完成之后关了也没事。手机上飞书 App 正常收消息。

### Q：每天推多少条合适？
3-5 条。多了你看不过来，少了没价值。

### Q：能不能推给我的朋友们？
**能。** 把机器人加到其他飞书群就行。或者以后做成 SaaS，每人用自己的飞书群接收。

### Q：腾讯云服务器的活动在哪看？
- 腾讯云官网：https://cloud.tencent.com
- 关注"腾讯云服务器"公众号
- 或者去拼多多/淘宝搜"腾讯云轻量"

### Q：有没有不花钱的先跑起来？
有。用你现在的电脑 + GitHub Actions 做定时任务，完全免费：
1. 代码放在 GitHub 仓库
2. 用 `.github/workflows/push.yml` 设置定时触发
3. GitHub Actions 每天免费跑一次

但这个方案需要你电脑上有 Python 环境，且 GitHub Actions 的稳定性不如自有服务器。

## 五、需要我帮你什么

告诉我你现在最想做哪个：
1. **帮你写核心代码** — 我直接生成 `main.py`、`sources.py`、`pusher.py` 等全部文件
2. **先装飞书拿到 Webhook** — 我一步步指导你操作
3. **先用免费方案跑通** — 不花钱，本机 + GitHub Actions 先跑起来
4. **其他想法** — 有什么补充需求告诉我
