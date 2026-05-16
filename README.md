# Auto Resource Pusher

Daily curated digest of quality content, delivered to your phone via Feishu bot. Five articles covering GitHub projects, domestic news, foreign tech, AI updates, and world affairs.

## Pipeline

```
Sources (4)          Rule Filter        AI Curate         Link Check        Push
┌──────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐
│ GitHub    │      │          │      │          │      │          │      │ Hottest  │
│ HackerNews│──75→│ Score 30 │──→│ DeepSeek │──→│ HEAD ok? │──→│ Domestic │
│ Juejin    │      │ Min/source│     │ 5 themes │      │ Fallback │      │ Foreign  │
│ Toutiao   │      │          │      │          │      │          │      │ AI News  │
└──────────┘      └──────────┘      └──────────┘      └──────────┘      │ World    │
                                                                        └──────────┘
```

## Quick Start

### 1. Install

```bash
pip install -r requirements.txt
```

### 2. Configure

Copy `.env.example` to `.env` and fill in your credentials:

```env
FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/xxxxx
FEISHU_KEYWORD=your-security-keyword
DEEPSEEK_API_KEY=sk-xxxxx
```

| Variable | Required | Description |
|----------|----------|-------------|
| `FEISHU_WEBHOOK_URL` | Yes | Feishu custom bot webhook URL |
| `FEISHU_KEYWORD` | No | Feishu bot security keyword |
| `DEEPSEEK_API_KEY` | No | DeepSeek API key; skips AI filtering if absent |

### 3. Run

```bash
python main.py
```

## Automation

**Windows Task Scheduler**: right-click `setup_schedule.ps1` → Run with PowerShell. Runs daily at 9:00 AM.

## Project Structure

```
auto-resource-pusher/
├── main.py                  # Orchestrator
├── config.py                # Environment config & weights
├── models.py                # Article dataclass
├── filter.py                # Rule scoring + DeepSeek AI curation
├── pusher.py                # Feishu card message builder
├── sources/
│   ├── __init__.py          # Parallel aggregator
│   ├── github.py            # GitHub trending repos (30-day window)
│   ├── hackernews.py        # Hacker News top stories
│   ├── zhihu.py             # Juejin hot feed
│   └── toutiao.py           # Toutiao trending board
├── pushed.json              # 30-day rolling dedup (auto-maintained)
├── requirements.txt
├── .env.example             # Config template
├── setup_schedule.ps1       # Windows Task Scheduler setup
└── run.bat                  # One-click launcher
```

## Filtering

### Rule Pre-filter
Keyword matching + metric scoring (stars, heat, comments) + source weighting → minimum 5 per source → 30 candidates.

### AI Curation
DeepSeek picks one article per theme:
- Hottest GitHub project
- Domestic news
- Foreign news
- AI developments
- World affairs

## Deduplication

`pushed.json` tracks pushed URLs. Articles from the past 30 days are skipped. Auto-prunes expired entries.
