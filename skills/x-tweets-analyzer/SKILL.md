---
name: x-tweets-analyzer
description: "Fetch and analyze X (Twitter) posts for trend analysis, sentiment analysis, keyword extraction, and engagement metrics. Use when the user requests: (1) Getting latest tweets from specific users, (2) Searching tweets by keywords/hashtags, (3) Analyzing tweet content and sentiment, (4) Tracking Twitter trends or mentions, (5) Extracting insights from tweet data"
---

# X Tweets Analyzer

Fetch and analyze X (Twitter) posts without requiring API keys (uses jina.ai reader). Provides trend analysis, sentiment analysis, keyword extraction, and basic statistics.

## Quick Start

### Fetch Latest Tweets from a User

```bash
# Fetch 10 most recent tweets from @elonmusk
python3 scripts/fetch_tweets.py elonmusk 10

# Fetch and save to file
python3 scripts/fetch_tweets.py username 20 > tweets.txt
```

### Analyze Tweet Content

```bash
# Analyze tweets from stdin
./scripts/fetch_tweets.sh elonmusk 10 | ./scripts/analyze_tweets.py

# Analyze tweets from file
./scripts/analyze_tweets.py tweets.txt
```

---

## Capabilities

### 1. Fetch Tweets by Username

Use `scripts/fetch_tweets.sh` to get recent tweets from any public X profile.

**Usage:**
```bash
python3 scripts/fetch_tweets.py <username> [limit]
```

**Parameters:**
- `username`: X username (without @)
- `limit`: Number of tweets to fetch (default: 10)

**Example:**
```bash
# Get latest 5 tweets from @OpenAI
python3 scripts/fetch_tweets.py OpenAI 5
```

**Method:** Uses jina.ai web reader (no API key required). See [API_METHODS.md](references/API_METHODS.md) for alternative methods.

---

### 2. Analyze Tweet Sentiment and Keywords

Use `scripts/analyze_tweets.py` to extract insights from tweet content.

**Usage:**
```bash
./scripts/analyze_tweets.py [tweets_file]
```

**If no file provided:** Reads tweets from stdin (one tweet per line)

**Output includes:**
- Top 10 keywords by frequency
- Sentiment score (positive/negative mentions)
- Tech/AI content percentage
- Overall tone assessment

**Example:**
```bash
# Fetch and analyze in one command
python3 scripts/fetch_tweets.py elonmusk 20 | python3 scripts/analyze_tweets.py
```

---

### 3. Search Tweets by Keywords

**Method 1: X API (Official)** - Requires API key
```bash
curl -X GET "https://api.twitter.com/2/tweets/search/recent?query=AI" \
  -H "Authorization: Bearer YOUR_TOKEN" | jq '.data[] | .text'
```

**Method 2: Jina.ai (Limited)** - No API key, user-specific only
```bash
# Jina.ai doesn't support keyword search, only user profiles
# Use X API or third-party services for keyword search
```

For detailed search methods and API options, see [API_METHODS.md](references/API_METHODS.md).

---

## Workflow: Complete Analysis Pipeline

**Use when:** User wants a comprehensive analysis of a user's tweets

```
1. Fetch tweets
   ↓
2. Save to file
   ↓
3. Analyze content
   ↓
4. Generate report
```

**Example:**
```bash
# Step 1: Fetch 50 tweets
python3 scripts/fetch_tweets.py username 50 > tweets.txt

# Step 2: Analyze
python3 scripts/analyze_tweets.py tweets.txt > analysis.txt

# Step 3: Review report
cat analysis.txt
```

---

## Advanced: Alternative Fetch Methods

When jina.ai is unavailable or insufficient, use alternative methods:

- **X API v2:** Official, stable, requires API key → See [API_METHODS.md](references/API_METHODS.md)
- **Nitter:** Open-source, no API key, slower → See [API_METHODS.md](references/API_METHODS.md)
- **Scraping:** Last resort, fragile → See [API_METHODS.md](references/API_METHODS.md)

**When to use alternatives:**
- Need historical data beyond recent tweets
- Want to search by keywords/hashtags
- Require official API reliability
- Building production application

---

## Understanding Analysis Results

### Sentiment Score
- **Positive:** Score > 0
- **Negative:** Score < 0
- **Neutral:** Score = 0

Based on keyword matching (see `analyze_tweets.py` for keyword lists).

### Tech/AI Percentage
Percentage of tweets mentioning technology or AI-related terms:
```
(Tech mentions / Total tweets) × 100
```

### Top Keywords
Most frequently appearing words (excluding common stopwords).

---

## Troubleshooting

**Problem:** No tweets fetched from `fetch_tweets.sh`
- **Solution:** Check username is correct, try alternative methods in [API_METHODS.md](references/API_METHODS.md)

**Problem:** Analysis shows "No tweets to analyze"
- **Solution:** Ensure tweets are in file or piped correctly (one tweet per line)

**Problem:** Jina.ai returns 503 error
- **Solution:** Service may be temporarily unavailable, retry later or use alternative method

---

## Resources

### scripts/
- **fetch_tweets.py:** Python script to fetch tweets using jina.ai reader
- **analyze_tweets.py:** Python script for sentiment/keyword analysis

### references/
- **API_METHODS.md:** Comprehensive guide to X API and alternative fetch methods
