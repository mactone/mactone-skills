#!/usr/bin/env python3
"""
Analyze tweets for keywords, sentiment, and patterns
Usage: ./analyze_tweets.py [tweets_file]
If no file is provided, reads from stdin
"""

import sys
import re
from collections import Counter
from typing import List, Dict

# Simple sentiment keywords (positive and negative)
POSITIVE_KEYWORDS = [
    'good', 'great', 'awesome', 'excellent', 'amazing', 'wonderful',
    'love', 'happy', 'best', 'success', 'win', 'better', 'exciting',
    'yes', 'thanks', 'thank', 'positive', 'hope', 'future', 'opportunity'
]

NEGATIVE_KEYWORDS = [
    'bad', 'terrible', 'awful', 'horrible', 'worst', 'fail', 'failure',
    'hate', 'angry', 'sad', 'problem', 'issue', 'wrong', 'negative',
    'no', 'not', 'never', 'cannot', 'can\'t', 'don\'t', 'won\'t'
]

TECH_KEYWORDS = [
    'ai', 'artificial intelligence', 'machine learning', 'ml', 'deep learning',
    'neural', 'model', 'algorithm', 'data', 'code', 'programming',
    'technology', 'tech', 'software', 'hardware', 'robot', 'automation'
]

def extract_keywords(text: str, min_length: int = 3) -> List[str]:
    """Extract keywords from text, removing common stopwords"""
    # Simple stopwords list
    stopwords = {
        'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should',
        'can', 'could', 'may', 'might', 'must', 'shall', 'to', 'from', 'in',
        'on', 'at', 'by', 'for', 'with', 'about', 'as', 'of', 'and', 'or',
        'but', 'if', 'because', 'so', 'this', 'that', 'these', 'those',
        'it', 'he', 'she', 'they', 'we', 'you', 'i', 'me', 'him', 'her', 'them'
    }

    # Extract words, lowercase, filter stopwords
    words = re.findall(r'\b[a-z]+\b', text.lower())
    keywords = [w for w in words if w not in stopwords and len(w) >= min_length]

    return keywords

def calculate_sentiment(text: str) -> Dict[str, int]:
    """Calculate simple sentiment score based on keyword matching"""
    text_lower = text.lower()

    positive_count = sum(1 for kw in POSITIVE_KEYWORDS if kw in text_lower)
    negative_count = sum(1 for kw in NEGATIVE_KEYWORDS if kw in text_lower)
    tech_count = sum(1 for kw in TECH_KEYWORDS if kw in text_lower)

    return {
        'positive': positive_count,
        'negative': negative_count,
        'tech': tech_count,
        'sentiment_score': positive_count - negative_count
    }

def analyze_tweets(tweets: List[str]) -> Dict:
    """Analyze a list of tweets and return summary statistics"""

    all_keywords = []
    sentiments = []
    tech_mentions = 0

    for tweet in tweets:
        # Extract keywords
        keywords = extract_keywords(tweet)
        all_keywords.extend(keywords)

        # Calculate sentiment
        sentiment = calculate_sentiment(tweet)
        sentiments.append(sentiment)

        if sentiment['tech'] > 0:
            tech_mentions += 1

    # Count keyword frequency
    keyword_counter = Counter(all_keywords)
    top_keywords = keyword_counter.most_common(10)

    # Aggregate sentiment
    total_positive = sum(s['positive'] for s in sentiments)
    total_negative = sum(s['negative'] for s in sentiments)
    total_sentiment = total_positive - total_negative

    return {
        'tweet_count': len(tweets),
        'top_keywords': top_keywords,
        'total_positive_mentions': total_positive,
        'total_negative_mentions': total_negative,
        'sentiment_score': total_sentiment,
        'tech_mentions': tech_mentions,
        'tech_percentage': round((tech_mentions / len(tweets)) * 100, 1) if tweets else 0,
        'sentiments': sentiments
    }

def print_analysis(analysis: Dict):
    """Print analysis results in a readable format"""

    print("\n" + "="*60)
    print("TWEET ANALYSIS REPORT")
    print("="*60)

    print(f"\n📊 Total Tweets Analyzed: {analysis['tweet_count']}")

    print(f"\n🔥 Top Keywords:")
    for i, (keyword, count) in enumerate(analysis['top_keywords'], 1):
        print(f"   {i}. {keyword} ({count} mentions)")

    print(f"\n💭 Sentiment Analysis:")
    print(f"   Positive mentions: {analysis['total_positive_mentions']}")
    print(f"   Negative mentions: {analysis['total_negative_mentions']}")
    print(f"   Overall sentiment score: {analysis['sentiment_score']:+d}")

    if analysis['sentiment_score'] > 0:
        print("   → Overall tone: Positive")
    elif analysis['sentiment_score'] < 0:
        print("   → Overall tone: Negative")
    else:
        print("   → Overall tone: Neutral")

    print(f"\n🤖 Tech/AI Content:")
    print(f"   Tweets mentioning tech: {analysis['tech_mentions']} / {analysis['tweet_count']}")
    print(f"   Tech content percentage: {analysis['tech_percentage']}%")

    print("\n" + "="*60 + "\n")

def main():
    # Read tweets from file or stdin
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            tweets = [line.strip() for line in f if line.strip()]
    else:
        tweets = [line.strip() for line in sys.stdin if line.strip()]

    if not tweets:
        print("No tweets to analyze.")
        sys.exit(1)

    # Analyze tweets
    analysis = analyze_tweets(tweets)

    # Print results
    print_analysis(analysis)

if __name__ == '__main__':
    main()
