#!/usr/bin/env python3
"""
Fetch tweets from X (Twitter) using jina.ai reader
Usage: ./fetch_tweets.py <username> [limit]
"""

import sys
import re
import requests
from typing import List

def fetch_tweets(username: str, limit: int = 10) -> List[str]:
    """Fetch tweets from X using jina.ai reader"""

    url = f"https://r.jina.ai/http://x.com/{username}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        content = response.text
    except requests.RequestException as e:
        print(f"Error fetching tweets: {e}", file=sys.stderr)
        return []

    # Extract the tweets section
    tweets = []

    # Find the start of the posts section
    # Try multiple patterns to handle different username formats
    # Need to include both regular apostrophe (U+0027) and smart quote (U+2019)
    smart_quote = chr(0x2019)
    patterns = [
        rf"{username}['{smart_quote}]s posts",  # Username's posts with both quotes
        rf"['{smart_quote}]s posts",  # Just "'s posts" (broader search)
    ]

    posts_match = None
    for pattern in patterns:
        posts_pattern = re.compile(pattern, re.IGNORECASE)
        posts_match = posts_pattern.search(content)
        if posts_match:
            break

    if not posts_match:
        return []

    # Extract content from posts section to "Who to follow"
    posts_section = content[posts_match.end():]
    end_match = re.search(r"Who to follow", posts_section)

    if end_match:
        posts_section = posts_section[:end_match.start()]

    # Split into lines
    lines = posts_section.split('\n')

    for line in lines:
        line = line.strip()

        # Skip empty lines
        if not line:
            continue

        # Skip lines that are too short
        if len(line) < 20:
            continue

        # Skip lines that look like metadata
        if re.match(r'^Image\s*\d+', line):
            continue
        if re.match(r'^https?://', line):
            continue
        if re.match(r'^\[!\[.*\]\]', line):
            continue
        if re.match(r'^@\w+', line):
            continue
        if re.match(r'^\d+[hm]$', line):
            continue
        if re.match(r'^[A-Z][a-z]* \d+$', line):
            continue
        if re.match(r'^Pinned', line):
            continue
        if re.match(r'^Show more', line):
            continue
        if re.match(r'^Quote', line):
            continue
        if re.match(r'^\d+K$', line):
            continue
        if re.match(r'^\d+K \d+K \d+K$', line):
            continue
        if re.match(r'^\d+$', line):
            continue
        if re.match(r'^---$', line):
            continue
        if re.match(r'^={3,}$', line):
            continue
        if 'profile_images' in line:
            continue
        if re.match(r'^\[[^\]]*\]\([^\)]*\)$', line):
            continue
        if 'Click to Follow' in line:
            continue
        if 'See new posts' in line:
            continue

        # Keep lines that look like actual tweet content
        tweets.append(line)

        if len(tweets) >= limit:
            break

    return tweets

def main():
    username = sys.argv[1] if len(sys.argv) > 1 else "elonmusk"
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10

    print(f"Fetching tweets from @{username}...")
    print("-" * 40)

    tweets = fetch_tweets(username, limit)

    for i, tweet in enumerate(tweets, 1):
        print(f"{i}. {tweet}")

    print("-" * 40)
    print(f"Fetched {len(tweets)} tweets from @{username}")

if __name__ == '__main__':
    main()
