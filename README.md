# 每日自动推送优质资源

每天自动筛选优质内容，通过飞书机器人推送到手机。五篇精选覆盖 GitHub 开源、国内热点、国外科技、AI 动态、国际大事。

## 工作流程

```
信息源 (4个)          规则初筛           AI精选           链接检查          飞书推送
┌──────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐
│ GitHub    │      │          │      │          │      │          │      │ GitHub最热 │
│ HackerNews│──75条→│ 打分取30  │──→│ DeepSeek │──→│ HEAD可达  │──→│ 国内热点  │
│ 掘金      │      │ 来源保底  │      │ 5主题各选1│      │ 超时补位  │      │ 国外热点  │
│ 今日头条  │      │          │      │          │      │          │      │ AI发展    │
└──────────┘      └──────────┘      └──────────┘      └──────────┘      │ 国际大事  │
                                                                        └──────────┘
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置

复制 `.env.example` 为 `.env`，填入真实值：

```env
FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/xxxxx
FEISHU_KEYWORD=你的安全关键词
DEEPSEEK_API_KEY=sk-xxxxx
```

| 变量 | 必填 | 说明 |
|------|------|------|
| `FEISHU_WEBHOOK_URL` | 是 | 飞书自定义机器人 Webhook |
| `FEISHU_KEYWORD` | 否 | 飞书机器人安全关键词 |
| `DEEPSEEK_API_KEY` | 否 | DeepSeek API Key，不填则纯规则筛选 |

### 3. 运行

```bash
python main.py
```

## 自动运行

**Windows 定时任务**：右键 `setup_schedule.ps1` → 使用 PowerShell 运行，每天早上 9:00 自动执行。

## 项目结构

```
auto-resource-pusher/
├── main.py                  # 主入口：编排全流程
├── config.py                # 配置文件（环境变量、权重）
├── models.py                # Article 数据类
├── filter.py                # 规则打分 + DeepSeek AI 精选
├── pusher.py                # 飞书卡片消息推送
├── sources/
│   ├── __init__.py          # 并行聚合
│   ├── github.py            # GitHub 高星仓库（30天窗口）
│   ├── hackernews.py        # Hacker News 头条
│   ├── zhihu.py             # 掘金热门
│   └── toutiao.py           # 今日头条热榜
├── pushed.json              # 30天滑动去重记录（自动维护）
├── requirements.txt
├── .env.example             # 配置模板
├── setup_schedule.ps1       # Windows 定时任务脚本
└── run.bat                  # 一键运行
```

## 筛选机制

### 规则初筛
关键词匹配 + 指标打分（星标、热度、评论） + 来源权重 → 每源保底 5 篇 → 共 30 篇候选

### AI 精选
DeepSeek 按五个主题各选一篇最匹配的文章：
- GitHub 最热项目
- 国内热点新闻
- 国外热点新闻
- 最新 AI 发展
- 国际大事

## 去重

`pushed.json` 记录已推送的 URL，30 天内不重复。每次运行自动清理过期记录。
