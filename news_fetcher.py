"""
WAIMAKERS News Fetcher
======================
Fetches AI news from configured sources via RSS feeds and web scraping.
"""

import json
import re
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from html.parser import HTMLParser
from xml.etree import ElementTree as ET
import ssl
import time

# SSL context for HTTPS requests
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# News sources configuration - verified working feeds
NEWS_SOURCES = [
    {
        "name": "TechCrunch AI",
        "url": "https://techcrunch.com/category/artificial-intelligence/feed/",
        "type": "rss",
        "keywords": ["AI", "artificial intelligence", "machine learning", "GPT", "LLM", "startup"]
    },
    {
        "name": "OpenAI",
        "url": "https://openai.com/blog/rss/",
        "type": "rss",
        "keywords": ["OpenAI", "GPT", "ChatGPT", "DALL-E", "Sora", "o1"]
    },
    {
        "name": "Google AI",
        "url": "https://blog.google/technology/ai/rss/",
        "type": "rss",
        "keywords": ["Google", "Gemini", "DeepMind", "Bard"]
    },
    {
        "name": "NVIDIA AI",
        "url": "https://blogs.nvidia.com/feed/",
        "type": "rss",
        "keywords": ["NVIDIA", "GPU", "CUDA", "AI hardware", "inference"]
    },
    {
        "name": "One Useful Thing",
        "url": "https://www.oneusefulthing.org/feed",
        "type": "rss",
        "keywords": ["AI", "education", "Ethan Mollick", "productivity"]
    },
    {
        "name": "The Verge AI",
        "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
        "type": "rss",
        "keywords": ["AI", "tech", "Google", "Microsoft", "OpenAI"]
    },
    {
        "name": "Ars Technica AI",
        "url": "https://feeds.arstechnica.com/arstechnica/technology-lab",
        "type": "rss",
        "keywords": ["AI", "tech", "science", "research"]
    },
    {
        "name": "MIT Tech Review AI",
        "url": "https://www.technologyreview.com/topic/artificial-intelligence/feed",
        "type": "rss",
        "keywords": ["AI", "research", "MIT", "innovation"]
    },
    {
        "name": "VentureBeat AI",
        "url": "https://venturebeat.com/category/ai/feed/",
        "type": "rss",
        "keywords": ["AI", "enterprise", "startup", "funding"]
    },
    {
        "name": "Wired AI",
        "url": "https://www.wired.com/feed/tag/ai/latest/rss",
        "type": "rss",
        "keywords": ["AI", "tech", "future", "ethics"]
    }
]

# Backup/alternative RSS feeds
BACKUP_FEEDS = [
    {
        "name": "Hacker News AI",
        "url": "https://hnrss.org/newest?q=AI+OR+LLM+OR+GPT&count=10",
        "type": "rss",
        "keywords": ["AI", "LLM", "GPT", "startup"]
    },
    {
        "name": "AI News",
        "url": "https://www.artificialintelligence-news.com/feed/",
        "type": "rss", 
        "keywords": ["AI", "machine learning", "deep learning"]
    }
]


class HTMLTextExtractor(HTMLParser):
    """Extract plain text from HTML"""
    def __init__(self):
        super().__init__()
        self.text_parts = []
        self.skip_data = False
        
    def handle_starttag(self, tag, attrs):
        if tag in ['script', 'style', 'head']:
            self.skip_data = True
            
    def handle_endtag(self, tag):
        if tag in ['script', 'style', 'head']:
            self.skip_data = False
            
    def handle_data(self, data):
        if not self.skip_data:
            self.text_parts.append(data.strip())
            
    def get_text(self):
        return ' '.join(filter(None, self.text_parts))


def strip_html(html_text):
    """Remove HTML tags and return plain text"""
    if not html_text:
        return ""
    try:
        parser = HTMLTextExtractor()
        parser.feed(html_text)
        return parser.get_text()
    except:
        # Fallback: simple regex
        return re.sub(r'<[^>]+>', '', html_text)


def fetch_url(url, timeout=10):
    """Fetch URL content with error handling"""
    try:
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Accept': 'application/rss+xml, application/xml, text/xml, */*'
            }
        )
        with urllib.request.urlopen(req, timeout=timeout, context=ssl_context) as response:
            return response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"   ⚠️ Failed to fetch {url}: {e}")
        return None


def parse_rss_date(date_str):
    """Parse various RSS date formats"""
    if not date_str:
        return datetime.now().isoformat()
    
    formats = [
        '%a, %d %b %Y %H:%M:%S %z',
        '%a, %d %b %Y %H:%M:%S %Z',
        '%Y-%m-%dT%H:%M:%S%z',
        '%Y-%m-%dT%H:%M:%SZ',
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d',
    ]
    
    # Clean up the date string
    date_str = date_str.strip()
    date_str = re.sub(r'\s+', ' ', date_str)
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.isoformat()
        except ValueError:
            continue
    
    # If all parsing fails, return current time
    return datetime.now().isoformat()


def parse_rss_feed(content, source_name, keywords):
    """Parse RSS/Atom feed and extract articles"""
    articles = []
    
    try:
        root = ET.fromstring(content)
        
        # Handle different RSS/Atom formats
        items = root.findall('.//item')  # RSS 2.0
        if len(items) == 0:
            items = root.findall('.//{http://www.w3.org/2005/Atom}entry')  # Atom
        
        for item in items[:5]:  # Limit to 5 per source
            # Try different tag names for title
            title_elem = item.find('title')
            if title_elem is None:
                title_elem = item.find('{http://www.w3.org/2005/Atom}title')
            
            title = ""
            if title_elem is not None and title_elem.text:
                title = title_elem.text.strip()
            
            # Skip articles without title
            if not title or title == "Untitled":
                continue
            
            # Try different tag names for link
            link = ""
            link_elem = item.find('link')
            if link_elem is not None:
                link = link_elem.get('href') or link_elem.text or ""
            if not link:
                link_elem = item.find('{http://www.w3.org/2005/Atom}link')
                if link_elem is not None:
                    link = link_elem.get('href') or ""
            
            # Try different tag names for description/summary
            desc_elem = item.find('description')
            if desc_elem is None:
                desc_elem = item.find('{http://www.w3.org/2005/Atom}summary')
            if desc_elem is None:
                desc_elem = item.find('{http://www.w3.org/2005/Atom}content')
            
            description = ""
            if desc_elem is not None and desc_elem.text:
                description = strip_html(desc_elem.text)
            
            # Truncate description
            if len(description) > 300:
                description = description[:297] + "..."
            
            # Try different tag names for date
            date_elem = item.find('pubDate')
            if date_elem is None:
                date_elem = item.find('{http://www.w3.org/2005/Atom}published')
            if date_elem is None:
                date_elem = item.find('{http://www.w3.org/2005/Atom}updated')
            
            date_str = date_elem.text if date_elem is not None else None
            
            # Find keywords to highlight
            highlights = []
            title_lower = title.lower()
            for kw in keywords:
                if kw.lower() in title_lower:
                    highlights.append(kw)
            
            articles.append({
                "source": source_name,
                "title": title,
                "summary": description.strip() or f"Latest news from {source_name}",
                "date": parse_rss_date(date_str),
                "link": link.strip(),
                "highlights": highlights,
                "overview": []
            })
            
    except ET.ParseError as e:
        print(f"   ⚠️ XML parse error for {source_name}: {e}")
    except Exception as e:
        print(f"   ⚠️ Error parsing {source_name}: {e}")
    
    return articles


def fetch_news_from_source(source):
    """Fetch news from a single source"""
    print(f"   📡 Fetching from {source['name']}...")
    
    content = fetch_url(source['url'])
    if not content:
        return []
    
    if source['type'] == 'rss':
        return parse_rss_feed(content, source['name'], source['keywords'])
    
    return []


def generate_daily_summary(articles):
    """
    Generate a narrative summary of today's AI news.
    Groups articles by theme and creates a cohesive story.
    """
    if not articles:
        return "No news available yet. Click Start to fetch the latest AI updates."
    
    # Categorize articles by theme
    themes = {
        "big_tech": [],      # OpenAI, Google, Microsoft, Anthropic
        "funding": [],       # Funding, valuation, investment
        "products": [],      # New products, launches, features
        "research": [],      # Research, papers, breakthroughs
        "regulation": [],    # EU, regulation, policy
        "other": []
    }
    
    for article in articles:
        title_lower = article['title'].lower()
        source_lower = article['source'].lower()
        
        if any(x in title_lower for x in ['openai', 'google', 'microsoft', 'anthropic', 'nvidia', 'meta']):
            themes['big_tech'].append(article)
        elif any(x in title_lower for x in ['funding', 'raises', 'valuation', 'investment', 'billion', 'million']):
            themes['funding'].append(article)
        elif any(x in title_lower for x in ['launch', 'release', 'introduce', 'announce', 'new', 'update']):
            themes['products'].append(article)
        elif any(x in title_lower for x in ['research', 'study', 'paper', 'discover', 'breakthrough']):
            themes['research'].append(article)
        elif any(x in title_lower for x in ['eu', 'regulation', 'law', 'policy', 'government']):
            themes['regulation'].append(article)
        else:
            themes['other'].append(article)
    
    # Build narrative summary
    summary_parts = []
    
    # Opening
    today = datetime.now().strftime("%A, %B %d")
    summary_parts.append(f"Here's what's happening in the world of AI on {today}:")
    
    # Big Tech news
    if themes['big_tech']:
        companies = set()
        for a in themes['big_tech'][:3]:
            for company in ['OpenAI', 'Google', 'Microsoft', 'Anthropic', 'NVIDIA', 'Meta']:
                if company.lower() in a['title'].lower():
                    companies.add(company)
        
        if companies:
            company_list = ', '.join(sorted(companies))
            summary_parts.append(f"\n\n**Big Tech Moves:** {company_list} made headlines today. " + 
                               themes['big_tech'][0]['title'] + ".")
    
    # Funding news
    if themes['funding']:
        summary_parts.append(f"\n\n**Investment & Funding:** " + themes['funding'][0]['title'] + ".")
    
    # Product launches
    if themes['products']:
        summary_parts.append(f"\n\n**Product Updates:** " + themes['products'][0]['title'] + ".")
    
    # Research
    if themes['research']:
        summary_parts.append(f"\n\n**Research & Innovation:** " + themes['research'][0]['title'] + ".")
    
    # Regulation
    if themes['regulation']:
        summary_parts.append(f"\n\n**Policy & Regulation:** " + themes['regulation'][0]['title'] + ".")
    
    # Add interesting other news if we don't have much
    if len(summary_parts) < 4 and themes['other']:
        summary_parts.append(f"\n\n**Also noteworthy:** " + themes['other'][0]['title'] + ".")
    
    # Closing
    summary_parts.append(f"\n\nScroll down for more details on each story.")
    
    return ''.join(summary_parts)


def fetch_all_news(max_articles=10):
    """
    Fetch news from all configured sources.
    Returns a dict with 'articles' list and 'summary' string.
    """
    print("🔄 Fetching AI news from sources...")
    
    all_articles = []
    successful_sources = 0
    
    # Try main sources first
    for source in NEWS_SOURCES:
        articles = fetch_news_from_source(source)
        if articles:
            all_articles.extend(articles)
            successful_sources += 1
        time.sleep(0.5)  # Be nice to servers
    
    # If we didn't get enough, try backup sources
    if len(all_articles) < max_articles:
        print("   📡 Trying backup sources...")
        for source in BACKUP_FEEDS:
            if len(all_articles) >= max_articles * 2:
                break
            articles = fetch_news_from_source(source)
            if articles:
                all_articles.extend(articles)
                successful_sources += 1
            time.sleep(0.5)
    
    print(f"✅ Fetched {len(all_articles)} articles from {successful_sources} sources")
    
    # Sort by date (newest first)
    def parse_date_for_sort(article):
        try:
            date_str = article['date'].replace('Z', '+00:00')
            dt = datetime.fromisoformat(date_str)
            # Make timezone-naive for comparison
            if dt.tzinfo is not None:
                dt = dt.replace(tzinfo=None)
            return dt
        except:
            return datetime.now()
    
    all_articles.sort(key=parse_date_for_sort, reverse=True)
    
    # Add IDs and limit
    result = []
    for i, article in enumerate(all_articles[:max_articles]):
        article['id'] = i + 1
        result.append(article)
    
    # Generate summary
    summary = generate_daily_summary(all_articles[:max_articles])
    
    return {
        "articles": result,
        "summary": summary
    }


def fetch_news_async(callback):
    """
    Fetch news and call callback with results.
    Used by the agent when Start is clicked.
    """
    articles = fetch_all_news()
    callback(articles)


# ============================================================
# CLI for testing
# ============================================================

if __name__ == '__main__':
    print("=" * 60)
    print("WAIMAKERS News Fetcher - Test Run")
    print("=" * 60)
    
    result = fetch_all_news(max_articles=10)
    articles = result['articles']
    summary = result['summary']
    
    print("\n" + "=" * 60)
    print("TODAY'S AI BRIEFING")
    print("=" * 60)
    print(summary)
    
    print("\n" + "=" * 60)
    print(f"TOP {len(articles)} AI NEWS ARTICLES")
    print("=" * 60)
    
    for article in articles:
        print(f"\n{article['id']}. [{article['source']}]")
        print(f"   {article['title']}")
        print(f"   {article['date'][:10]} | {article['link'][:50]}...")
        if article['highlights']:
            print(f"   Highlights: {', '.join(article['highlights'])}")

