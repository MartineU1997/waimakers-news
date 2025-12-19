"""
WAIMAKERS News Dashboard Agent
==============================
This agent serves the news dashboard and provides an API for other agents to:
- Set user name for greeting
- Set podcast link
- Load news articles
- Trigger the dashboard to refresh
- Automatically fetch AI news from configured sources

Run with: python agent.py
Dashboard will be available at: http://localhost:8080
"""

import json
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

# Import the news fetcher
try:
    from news_fetcher import fetch_all_news
    NEWS_FETCHER_AVAILABLE = True
except ImportError:
    NEWS_FETCHER_AVAILABLE = False
    print("⚠️ news_fetcher.py not found - automatic news fetching disabled")

# Store state that will be injected into the dashboard
dashboard_state = {
    "user_name": "there",
    "podcast_link": "",
    "articles": [],
    "ready": False
}

class DashboardAgentHandler(SimpleHTTPRequestHandler):
    """Custom handler that serves the dashboard and handles API calls"""
    
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        # API endpoint to get current state
        if parsed_path.path == '/api/state':
            self.send_json_response(dashboard_state)
            return
        
        # Serve index.html for root
        if parsed_path.path == '/':
            self.path = '/index.html'
        
        # Serve static files
        return SimpleHTTPRequestHandler.do_GET(self)
    
    def do_POST(self):
        parsed_path = urlparse(self.path)
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
        
        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            self.send_error_response(400, "Invalid JSON")
            return
        
        # API: Set user name
        if parsed_path.path == '/api/user':
            if 'name' in data:
                dashboard_state['user_name'] = data['name']
                self.send_json_response({"success": True, "user_name": data['name']})
                print(f"👤 User name set to: {data['name']}")
            else:
                self.send_error_response(400, "Missing 'name' field")
            return
        
        # API: Set podcast link
        if parsed_path.path == '/api/podcast':
            if 'url' in data:
                dashboard_state['podcast_link'] = data['url']
                self.send_json_response({"success": True, "podcast_link": data['url']})
                print(f"🎙️ Podcast link set to: {data['url']}")
            else:
                self.send_error_response(400, "Missing 'url' field")
            return
        
        # API: Load articles
        if parsed_path.path == '/api/articles':
            if 'articles' in data:
                dashboard_state['articles'] = data['articles']
                dashboard_state['ready'] = True
                self.send_json_response({"success": True, "count": len(data['articles'])})
                print(f"📰 Loaded {len(data['articles'])} articles")
            else:
                self.send_error_response(400, "Missing 'articles' field")
            return
        
        # API: Add single article
        if parsed_path.path == '/api/article':
            if 'article' in data:
                dashboard_state['articles'].append(data['article'])
                dashboard_state['ready'] = True
                self.send_json_response({"success": True, "count": len(dashboard_state['articles'])})
                print(f"➕ Added article: {data['article'].get('title', 'Untitled')}")
            else:
                self.send_error_response(400, "Missing 'article' field")
            return
        
        # API: Clear all data
        if parsed_path.path == '/api/clear':
            dashboard_state['articles'] = []
            dashboard_state['ready'] = False
            self.send_json_response({"success": True})
            print("🗑️ Dashboard cleared")
            return
        
        # API: Fetch news (called when Start is clicked)
        if parsed_path.path == '/api/fetch':
            if NEWS_FETCHER_AVAILABLE:
                print("🔄 Start button clicked - fetching news...")
                # Fetch in background thread
                def fetch_and_update():
                    try:
                        articles = fetch_all_news(max_articles=10)
                        dashboard_state['articles'] = articles
                        dashboard_state['ready'] = True
                        print(f"✅ Loaded {len(articles)} articles into dashboard")
                    except Exception as e:
                        print(f"❌ Error fetching news: {e}")
                
                thread = threading.Thread(target=fetch_and_update)
                thread.start()
                self.send_json_response({"success": True, "message": "Fetching news..."})
            else:
                self.send_json_response({"success": False, "message": "News fetcher not available"})
            return
        
        self.send_error_response(404, "Unknown endpoint")
    
    def send_json_response(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def send_error_response(self, status, message):
        self.send_json_response({"error": message}, status)
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress default logging for cleaner output"""
        if '/api/' in args[0]:
            print(f"🌐 API: {args[0]}")


def run_server(port=8080):
    """Start the dashboard server"""
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    server = HTTPServer(('localhost', port), DashboardAgentHandler)
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║           🚀 WAIMAKERS News Dashboard Agent                  ║
╠══════════════════════════════════════════════════════════════╣
║  Dashboard:  http://localhost:{port}                          ║
║                                                              ║
║  API Endpoints:                                              ║
║  POST /api/user     - Set user name {{"name": "..."}}          ║
║  POST /api/podcast  - Set podcast {{"url": "..."}}             ║
║  POST /api/articles - Load articles {{"articles": [...]}}      ║
║  POST /api/article  - Add article {{"article": {{...}}}}         ║
║  POST /api/clear    - Clear all data                         ║
║  GET  /api/state    - Get current state                      ║
╚══════════════════════════════════════════════════════════════╝
    """)
    server.serve_forever()


# ============================================================
# AGENT INTERFACE - For other agents to call
# ============================================================

class WAIMAKERSNewsAgent:
    """
    Agent interface for programmatic control of the dashboard.
    
    Usage:
        agent = WAIMAKERSNewsAgent()
        agent.start()
        
        agent.set_user_name("Martine")
        agent.set_podcast_link("https://podcast.example.com")
        agent.load_articles([...])
    """
    
    def __init__(self, port=8080):
        self.port = port
        self.base_url = f"http://localhost:{port}"
        self._server_thread = None
    
    def start(self):
        """Start the dashboard server in background"""
        self._server_thread = threading.Thread(target=run_server, args=(self.port,), daemon=True)
        self._server_thread.start()
        print(f"✅ Dashboard agent started at {self.base_url}")
    
    def set_user_name(self, name: str):
        """Set the user name for the greeting"""
        dashboard_state['user_name'] = name
        print(f"👤 User name set to: {name}")
    
    def set_podcast_link(self, url: str):
        """Set the podcast link"""
        dashboard_state['podcast_link'] = url
        print(f"🎙️ Podcast link set to: {url}")
    
    def load_articles(self, articles: list):
        """
        Load news articles into the dashboard.
        
        Article structure:
        {
            "id": 1,
            "source": "OpenAI Blog",
            "title": "GPT-5 Released",
            "summary": "Short summary of the article",
            "date": "2025-12-19",
            "link": "https://...",
            "highlights": ["GPT-5"],  # Optional: words to highlight in orange
            "overview": ["Point 1", "Point 2"]  # Optional: bullet points
        }
        """
        dashboard_state['articles'] = articles
        dashboard_state['ready'] = True
        print(f"📰 Loaded {len(articles)} articles")
    
    def add_article(self, article: dict):
        """Add a single article"""
        dashboard_state['articles'].append(article)
        dashboard_state['ready'] = True
        print(f"➕ Added article: {article.get('title', 'Untitled')}")
    
    def clear(self):
        """Clear all articles"""
        dashboard_state['articles'] = []
        dashboard_state['ready'] = False
        print("🗑️ Dashboard cleared")
    
    def get_state(self) -> dict:
        """Get current dashboard state"""
        return dashboard_state.copy()


# ============================================================
# MAIN
# ============================================================

if __name__ == '__main__':
    run_server()

