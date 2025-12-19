"""
Example: How another agent can use the WAIMAKERS News Dashboard Agent
======================================================================

This script demonstrates how to interact with the dashboard agent.
Uses only built-in libraries (no external dependencies).
"""

import json
import urllib.request
import urllib.error
import time

# Dashboard agent base URL
BASE_URL = "http://localhost:8080"


def make_request(endpoint: str, method: str = "GET", data: dict = None):
    """Make HTTP request to the agent API"""
    url = f"{BASE_URL}{endpoint}"
    
    if data:
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method=method
        )
    else:
        req = urllib.request.Request(url, method=method)
    
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        return {"error": e.reason, "status": e.code}
    except urllib.error.URLError as e:
        return {"error": str(e.reason)}


def set_user_name(name: str):
    """Set the user name for the greeting"""
    return make_request("/api/user", "POST", {"name": name})


def set_podcast_link(url: str):
    """Set the podcast link"""
    return make_request("/api/podcast", "POST", {"url": url})


def load_articles(articles: list):
    """Load news articles into the dashboard"""
    return make_request("/api/articles", "POST", {"articles": articles})


def add_article(article: dict):
    """Add a single article"""
    return make_request("/api/article", "POST", {"article": article})


def clear_dashboard():
    """Clear all articles"""
    return make_request("/api/clear", "POST")


def get_state():
    """Get current dashboard state"""
    return make_request("/api/state", "GET")


# ============================================================
# Example usage
# ============================================================

if __name__ == '__main__':
    print("🚀 Connecting to WAIMAKERS News Dashboard Agent...")
    print(f"   Make sure the agent is running: python agent.py\n")
    
    # Wait a moment for connection
    time.sleep(1)
    
    # 1. Set user name
    print("1️⃣ Setting user name...")
    result = set_user_name("Martine")
    print(f"   Result: {result}\n")
    
    # 2. Set podcast link
    print("2️⃣ Setting podcast link...")
    result = set_podcast_link("https://open.spotify.com/show/example")
    print(f"   Result: {result}\n")
    
    # 3. Load sample articles
    print("3️⃣ Loading articles...")
    
    sample_articles = [
        {
            "id": 1,
            "source": "OpenAI Blog",
            "title": "GPT-5 Released with Major Improvements",
            "summary": "OpenAI announces the release of GPT-5, featuring enhanced reasoning capabilities and multimodal understanding.",
            "date": "2025-12-19T10:00:00Z",
            "link": "https://openai.com/blog/gpt-5",
            "highlights": ["GPT-5", "OpenAI"],
            "overview": [
                "50% improvement in reasoning benchmarks",
                "Native multimodal support for images, audio, and video",
                "Reduced hallucinations through new training methods",
                "Available via API starting January 2026"
            ]
        },
        {
            "id": 2,
            "source": "TechCrunch",
            "title": "Anthropic Raises $2B in Series D Funding",
            "summary": "AI safety startup Anthropic secures major funding round led by Google and Spark Capital.",
            "date": "2025-12-19T08:30:00Z",
            "link": "https://techcrunch.com/anthropic-funding",
            "highlights": ["Anthropic", "$2B"],
            "overview": [
                "Valuation reaches $20B",
                "Funds to expand Claude model capabilities",
                "New safety research initiatives announced"
            ]
        },
        {
            "id": 3,
            "source": "The Verge",
            "title": "Microsoft Integrates AI Copilot Across All Products",
            "summary": "Microsoft announces universal Copilot integration in Windows, Office, and Azure services.",
            "date": "2025-12-18T15:00:00Z",
            "link": "https://theverge.com/microsoft-copilot",
            "highlights": ["Microsoft", "Copilot"],
            "overview": [
                "Copilot now built into Windows 12",
                "Deep integration with Microsoft 365",
                "Enterprise features for Azure customers"
            ]
        },
        {
            "id": 4,
            "source": "Reuters",
            "title": "EU Passes Comprehensive AI Regulation Act",
            "summary": "European Parliament approves landmark AI legislation setting global standards for artificial intelligence governance.",
            "date": "2025-12-18T12:00:00Z",
            "link": "https://reuters.com/eu-ai-act",
            "highlights": ["EU", "AI Regulation"],
            "overview": [
                "Strict requirements for high-risk AI systems",
                "Mandatory transparency for generative AI",
                "Enforcement begins mid-2026"
            ]
        },
        {
            "id": 5,
            "source": "Client News",
            "title": "ACME Corp Launches AI-Powered Customer Service",
            "summary": "Your client ACME Corp has announced their new AI chatbot for customer support, built on the platform you helped develop.",
            "date": "2025-12-17T09:00:00Z",
            "link": "https://acmecorp.com/news/ai-launch",
            "highlights": ["ACME Corp", "AI-Powered"],
            "overview": [
                "80% reduction in response times",
                "Integration with existing CRM systems",
                "Positive early customer feedback"
            ]
        }
    ]
    
    result = load_articles(sample_articles)
    print(f"   Result: {result}\n")
    
    # 4. Check state
    print("4️⃣ Current dashboard state:")
    state = get_state()
    print(f"   User: {state['user_name']}")
    print(f"   Podcast: {state['podcast_link']}")
    print(f"   Articles: {len(state['articles'])}")
    print(f"   Ready: {state['ready']}\n")
    
    print("✅ Done! Open http://localhost:8080 and click Start to see the news.")
