# 🛢️ OilGas Intelligence Platform

A real-time oil & gas news aggregator with AI-powered alerts, daily digests to Slack/Teams, and global coverage from 40+ sources.

---

## Requirements

- **Python 3.10+** — [python.org](https://python.org)
- **Node.js 18+** — [nodejs.org](https://nodejs.org)

---

## Quick Start

### Mac / Linux

```bash
# 1. Unzip the folder, then open Terminal inside it
chmod +x setup.sh start.sh
./setup.sh        # one-time setup (takes 3-5 min first time)
./start.sh        # start the platform
```

### Windows

```
1. Unzip the folder
2. Double-click setup.bat   (one-time setup)
3. Double-click start.bat   (start the platform)
```

Then open **http://localhost:3000** in your browser.

---

## Optional API Keys (all free)

Edit `backend/.env` to add:

| Key | What it unlocks | Get it at |
|-----|----------------|-----------|
| `ANTHROPIC_API_KEY` | AI-written daily digests (much better summaries) | console.anthropic.com |
| `GNEWS_API_KEY` | Extra news sources (100 req/day free) | gnews.io |
| `NEWS_API_KEY` | NewsAPI.org additional coverage | newsapi.org |

The platform works without any of these — they just improve quality.

---

## Features

### 📰 News Feed
- **40+ RSS sources** — Reuters, EIA, IEA, OPEC, Rigzone, OilPrice, government agencies, regional press
- **Real-time updates** every 15 minutes
- **Deduplication** — clusters the same story from multiple outlets
- **Auto-translation** — non-English articles translated to English via MyMemory API
- **Relevance scoring** — AI-scored 0-100 for oil/gas relevance
- **Sentiment analysis** — positive / negative / neutral per article

### 🔍 Filters
- Region: Middle East, North America, Europe, Africa, Asia-Pacific, Latin America, Russia/FSU
- Topic: Upstream, Downstream, LNG, Refining, Prices, Geopolitics, Pipeline, Energy Transition
- Source type: Wire Service, Government, Analysis
- High Priority / Political-only quick filters

### ⚡ Alerts
- Create alerts in **plain language** ("I want to know about OPEC production cuts and LNG in Southeast Asia")
- System extracts keywords + uses semantic matching (sentence-transformers)
- Send alerts to Slack and/or Microsoft Teams instantly when matched
- Toggle alerts on/off

### 📊 Daily Digest
- Scheduled daily briefing at your chosen time
- Sent to Slack and/or Teams
- AI-powered summary if Anthropic API key provided

### 🔖 Bookmarks
- Save articles for later reference

### 💹 Live Price Ticker
- WTI Crude, Brent Crude, Natural Gas, RBOB Gasoline
- Refreshed every 5 minutes from Yahoo Finance (free, no key needed)

---

## Connecting Slack

1. Go to **api.slack.com/apps** → Create New App → From Scratch
2. Under **Features** → **Incoming Webhooks** → Toggle ON
3. Click **Add New Webhook to Workspace** → Choose channel → Copy URL
4. Paste URL in the app under **Alerts** (per-alert) or **Settings → Daily Digest**

## Connecting Microsoft Teams

1. Open Teams → Right-click your target channel → **Connectors**
2. Search **Incoming Webhook** → **Configure**
3. Name it "OilGas Intel" → **Create** → Copy the URL
4. Paste URL in the app under **Alerts** or **Settings → Daily Digest**

---

## Data Sources

**Wire Services:** Reuters, AP, MarketWatch, S&P Global Platts, OilPrice.com, Rigzone, World Oil, Oil & Gas Journal, Energy Intelligence, Offshore Technology

**Government / Official:** EIA (US), IEA, OPEC, Canada Energy Regulator, Norwegian Petroleum Directorate, North Sea Transition Authority, ANP Brazil, SHANA Iran

**Regional:** Arabian Business, The National UAE, MEES, Africa Oil & Gas Report, Euractiv Energy, Nikkei Asia, BNAmericas, TASS, Houston Chronicle Energy

**Political/Geopolitical:** Al Jazeera, BBC World, Deutsche Welle, France 24, Foreign Policy, Middle East Eye

---

## Architecture

```
backend/
  main.py          — FastAPI server + scheduler
  fetcher.py       — RSS crawler + processing pipeline
  nlp.py           — Relevance scoring, dedup, translation, sentiment
  notifier.py      — Slack/Teams webhooks + daily digest
  models.py        — SQLite database schema
  feeds_config.py  — All RSS feed URLs + keyword taxonomy

frontend/
  src/
    App.js                   — Main app shell
    components/
      PriceTicker.jsx        — Live commodity prices
      NewsFeed.jsx           — Main feed + filters + sidebar
      ArticleCard.jsx        — Individual article display
      AlertsPage.jsx         — Alert management
      BookmarksPage.jsx      — Saved articles
      SettingsPage.jsx       — Digest config + Slack/Teams setup
```

---

## Troubleshooting

**Backend won't start:** Make sure you're inside `backend/` with the virtual environment activated

**No articles loading:** The first fetch takes ~1-2 minutes. Click "Refresh Now" in the feed.

**Translation not working:** MyMemory has a daily free limit. Articles will show in original language as fallback.

**Sentence-transformer slow on first run:** The model (~80MB) downloads once on first start. Subsequent starts are instant.
