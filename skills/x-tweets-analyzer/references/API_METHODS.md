# X (Twitter) API Methods Reference

This document lists various methods to fetch tweets from X (Twitter) with their pros, cons, and use cases.

## Method 1: Jina.ai Reader ⭐ RECOMMENDED

**Endpoint:** `https://r.jina.ai/http://x.com/<username>`

**How it works:** Uses Jina.ai's web reader to convert X profile pages to readable markdown.

**Example:**
```bash
curl -s "https://r.jina.ai/http://x.com/elonmusk"
```

**Pros:**
- No API key required
- Returns clean, readable markdown format
- Works reliably for public profiles
- Includes tweet content and metadata

**Cons:**
- Cannot search tweets by keywords
- Limited to recent tweets (page load limit)
- No access to historical data
- May break if X changes page structure

**Best for:**
- Fetching recent tweets from specific users
- Quick prototyping and testing
- When you don't have API access

---

## Method 2: X API v2 (Official)

**Endpoints:**
- `GET /2/users/by/username/:username` - Get user ID
- `GET /2/users/:id/tweets` - Get user's tweets
- `GET /2/tweets/search/recent` - Search recent tweets

**Example:**
```bash
# Get user ID
curl -X GET "https://api.twitter.com/2/users/by/username/elonmusk" \
  -H "Authorization: Bearer YOUR_BEARER_TOKEN"

# Get tweets
curl -X GET "https://api.twitter.com/2/users/USER_ID/tweets?max_results=10" \
  -H "Authorization: Bearer YOUR_BEARER_TOKEN"

# Search tweets
curl -X GET "https://api.twitter.com/2/tweets/search/recent?query=AI" \
  -H "Authorization: Bearer YOUR_BEARER_TOKEN"
```

**Pros:**
- Official, stable API
- Access to historical data (with higher tier)
- Search by keywords, hashtags, users
- Comprehensive metadata (public_metrics, created_at, etc.)
- Rate limiting and pagination support

**Cons:**
- Requires API key (free tier has limitations)
- Free tier limited to recent tweets (7 days)
- API v1.1 endpoints require higher access level
- Can be expensive for large-scale data collection

**Access Levels:**
- **Free:** 500k tweets/month (recent search only)
- **Basic:** 10k tweets/month + write access
- **Pro:** 1M tweets/month + full search
- **Enterprise:** Custom limits

**Best for:**
- Production applications
- Searching tweets by keywords/hashtags
- Accessing historical data
- When you have API budget

---

## Method 3: Nitter (Open-source Twitter Frontend)

**Instance:** `https://nitter.net`, `https://nitter.poast.org`, `https://nitter.fdn.fr`

**Example:**
```bash
curl -s "https://nitter.net/elonmusk" | \
  grep -oP 'class="tweet-content".*?</div>'
```

**Pros:**
- No API key required
- Open-source and decentralized
- Multiple instances available
- Works like Twitter but without tracking

**Cons:**
- Many instances are slow or offline
- Parsing is fragile (HTML structure changes)
- No official support
- Rate limiting by instances
- Limited to recent tweets

**Best for:**
- When official API is unavailable
- Privacy-focused scraping
- Testing without API costs

---

## Method 4: Scraping with Selenium/Playwright

**Method:** Use headless browser to render JavaScript-heavy X pages

**Example (Python with Playwright):**
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('https://x.com/elonmusk')
    tweets = page.query_selector_all('[data-testid="tweet"]')
    for tweet in tweets:
        print(tweet.text_content())
    browser.close()
```

**Pros:**
- Can bypass some restrictions
- Works with JavaScript-heavy sites
- Can scroll to load more tweets

**Cons:**
- Slow (requires rendering)
- Resource-intensive
- May violate ToS
- Fragile to UI changes
- X has anti-scraping measures

**Best for:**
- Last resort when other methods fail
- Small-scale scraping
- Learning purposes

---

## Method 5: Third-party APIs

**Services:** Snipit, TweetDeck, RapidAPI Twitter APIs, etc.

**Example:**
```bash
# Using a third-party API
curl -X GET "https://api.example.com/v1/tweets?username=elonmusk" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Pros:**
- May provide features not in official API
- Easier integration sometimes
- Different pricing models

**Cons:**
- Not official, may break
- Cost can be higher
- Limited documentation
- Reliability concerns

**Best for:**
- When official API doesn't meet needs
- Testing prototypes
- When you need specific features

---

## Summary Comparison

| Method | API Key | Search | Historical | Cost | Reliability |
|--------|----------|--------|------------|------|-------------|
| Jina.ai | No | Limited user | No | Free | High |
| X API v2 | Yes | Full | Yes (paid) | $$ | Very High |
| Nitter | No | Basic | No | Free | Medium |
| Scraping | No | Possible | No | Free (slow) | Low |
| Third-party | Varies | Varies | Varies | $$$ | Varies |

---

## Recommended Workflow

1. **Quick Test:** Use Jina.ai reader
2. **Development:** Start with free X API tier
3. **Production:** Upgrade to Basic/Pro tier as needed
4. **Fallback:** Have Nitter instances as backup
5. **Large Scale:** Consider third-party APIs or Enterprise plan

---

## Rate Limits and Best Practices

### X API Rate Limits

**Free Tier:**
- Search: 450 requests / 15 min
- User tweets: 1500 requests / 15 min

**Basic Tier:**
- Search: 30 requests / 15 min (lower due to write access)
- User tweets: 1500 requests / 15 min

### Best Practices

1. **Cache results:** Don't fetch the same tweets repeatedly
2. **Use pagination:** Respect `next_token` for large datasets
3. **Handle errors:** Implement retry logic with exponential backoff
4. **Respect rate limits:** Monitor remaining quota
5. **Use filtering:** Request only needed fields (`tweet.fields=created_at,public_metrics`)

### Error Handling

Common errors and solutions:
- **429 Too Many Requests:** Implement rate limiting and backoff
- **401 Unauthorized:** Check API key is valid
- **403 Forbidden:** Verify access level permissions
- **503 Service Unavailable:** Retry with exponential backoff

---

## Sample Use Cases

### Use Case 1: Monitor a specific user
```bash
# Using Jina.ai (quick)
./scripts/fetch_tweets.sh elonmusk 10

# Using X API (reliable)
curl -X GET "https://api.twitter.com/2/users/by/username/elonmusk" \
  -H "Authorization: Bearer TOKEN" | jq -r '.data.id'
```

### Use Case 2: Search for keywords
```bash
# Using X API
curl -X GET "https://api.twitter.com/2/tweets/search/recent?query=AI%20OR%20ML" \
  -H "Authorization: Bearer TOKEN" | jq '.data[] | .text'
```

### Use Case 3: Analyze sentiment over time
```bash
# Fetch tweets → Save to file → Analyze
./scripts/fetch_tweets.sh username 50 > tweets.txt
./scripts/analyze_tweets.py tweets.txt
```
