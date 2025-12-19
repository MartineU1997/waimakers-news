// ============================================================
// WAIMAKERS News Dashboard
// ============================================================
// This dashboard waits for data from another agent.
// Call window.loadNewsData(articles) to populate it.
// ============================================================

// Placeholder for news articles
let newsArticles = [];

// State
let currentArticle = null;
let userName = 'there'; // Default name
let onStartCallback = null; // Callback when user clicks Start

// DOM Elements
const articlesList = document.getElementById('articles-list');
const articleDetail = document.getElementById('article-detail');
const btnBack = document.getElementById('btn-back');
const loadingState = document.getElementById('loading-state');
const welcomeScreen = document.getElementById('welcome-screen');
const mainContent = document.getElementById('main-content');
const header = document.querySelector('.header');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupDetailView();
    setupWelcomeScreen();
    updateHeaderDate();
    updateGreeting();
});

// ============================================================
// PUBLIC API - Roep deze functies aan om data te laden
// ============================================================

/**
 * Laad nieuwsartikelen in het dashboard
 * @param {Array} articles - Array van artikel objecten
 * 
 * Artikel structuur:
 * {
 *   id: number,
 *   source: string,           // bijv. "OpenAI Blog"
 *   title: string,            // bijv. "GPT-5.2 Released"
 *   summary: string,          // Korte samenvatting
 *   date: string,             // ISO date "2025-12-19"
 *   link: string,             // URL naar origineel artikel
 *   highlights: string[],     // Optioneel: woorden om oranje te highlighten
 *   overview: string[]        // Optioneel: bullet points voor detail view
 * }
 */
window.loadNewsData = function(articles) {
    newsArticles = articles;
    hideLoadingState();
    renderArticles();
    console.log(`✅ WAIMAKERS News: ${articles.length} articles loaded`);
};

/**
 * Clear all articles and show loading state
 */
window.clearNewsData = function() {
    newsArticles = [];
    showLoadingState();
    articlesList.innerHTML = '';
    console.log('🔄 WAIMAKERS News: Articles cleared');
};

/**
 * Add a single article
 */
window.addNewsArticle = function(article) {
    newsArticles.push(article);
    hideLoadingState();
    renderArticles();
    console.log(`➕ WAIMAKERS News: "${article.title}" added`);
};

/**
 * Get current articles
 */
window.getNewsData = function() {
    return newsArticles;
};

/**
 * Set the podcast link
 * @param {string} url - URL to the podcast
 */
window.setPodcastLink = function(url) {
    const podcastLink = document.getElementById('podcast-link');
    if (podcastLink) {
        podcastLink.href = url;
        console.log(`🎙️ WAIMAKERS News: Podcast link set to ${url}`);
    }
};

/**
 * Set the user's name for the greeting
 * @param {string} name - User's name
 */
window.setUserName = function(name) {
    userName = name;
    updateGreeting();
    console.log(`👤 WAIMAKERS News: User name set to ${name}`);
};

/**
 * Set the callback for when user clicks Start
 * This is called when the user wants to fetch news
 * @param {Function} callback - Function to call when start is clicked
 */
window.onStartFetchNews = function(callback) {
    onStartCallback = callback;
    console.log('📡 WAIMAKERS News: Start callback registered');
};

// ============================================================
// INTERNAL FUNCTIONS
// ============================================================

function showLoadingState() {
    loadingState.classList.remove('hidden');
    articlesList.classList.add('hidden');
}

function hideLoadingState() {
    loadingState.classList.add('hidden');
    articlesList.classList.remove('hidden');
}

// Setup welcome screen
function setupWelcomeScreen() {
    const btnStart = document.getElementById('btn-start');
    
    // Initially hide main content and header
    if (mainContent) mainContent.style.display = 'none';
    if (header) header.style.display = 'none';
    
    // Fetch initial state from agent API
    fetchStateFromAgent();
    
    btnStart.addEventListener('click', () => {
        // Hide welcome screen with animation
        welcomeScreen.classList.add('hidden');
        
        // Show main content and header
        setTimeout(() => {
            if (mainContent) mainContent.style.display = 'block';
            if (header) header.style.display = 'flex';
            showLoadingState();
            
            // Call the start callback if registered
            if (onStartCallback) {
                onStartCallback();
            }
            
            // Start polling for news data from agent
            startPollingForNews();
            
            console.log('▶️ WAIMAKERS News: Start clicked, fetching news...');
        }, 300);
    });
}

// Fetch state from the agent API
async function fetchStateFromAgent() {
    try {
        const response = await fetch('/api/state');
        if (response.ok) {
            const state = await response.json();
            
            // Apply state
            if (state.user_name) {
                userName = state.user_name;
                updateGreeting();
            }
            
            if (state.podcast_link) {
                const podcastLink = document.getElementById('podcast-link');
                if (podcastLink) podcastLink.href = state.podcast_link;
            }
            
            console.log('📡 Fetched state from agent:', state);
        }
    } catch (e) {
        // Agent API not available, using standalone mode
        console.log('📡 Running in standalone mode (no agent API)');
    }
}

// Poll for news data from agent
let pollingInterval = null;

function startPollingForNews() {
    // Check immediately
    checkForNewsData();
    
    // Then poll every 2 seconds
    pollingInterval = setInterval(checkForNewsData, 2000);
}

async function checkForNewsData() {
    try {
        const response = await fetch('/api/state');
        if (response.ok) {
            const state = await response.json();
            
            if (state.ready && state.articles && state.articles.length > 0) {
                // Stop polling
                if (pollingInterval) {
                    clearInterval(pollingInterval);
                    pollingInterval = null;
                }
                
                // Load the articles
                newsArticles = state.articles;
                hideLoadingState();
                renderArticles();
                console.log(`✅ Received ${state.articles.length} articles from agent`);
            }
        }
    } catch (e) {
        // Agent not available
    }
}

// Update the greeting based on time of day and user name
function updateGreeting() {
    const welcomeTitle = document.querySelector('.welcome-title');
    const welcomeGreeting = document.getElementById('welcome-greeting');
    
    const hour = new Date().getHours();
    let timeGreeting = 'Good morning';
    
    if (hour >= 12 && hour < 17) {
        timeGreeting = 'Good afternoon';
    } else if (hour >= 17 || hour < 5) {
        timeGreeting = 'Good evening';
    }
    
    if (welcomeTitle) {
        welcomeTitle.textContent = `${timeGreeting}!`;
    }
    
    if (welcomeGreeting) {
        welcomeGreeting.textContent = `Hello ${userName}, here's your news today.`;
    }
}

function updateHeaderDate() {
    const headerDate = document.getElementById('header-date');
    if (headerDate) {
        const now = new Date();
        const options = { weekday: 'long', day: 'numeric', month: 'long' };
        headerDate.textContent = now.toLocaleDateString('en-US', options);
    }
}

// Render articles
function renderArticles() {
    if (newsArticles.length === 0) {
        articlesList.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📭</div>
                <h3>No news yet</h3>
                <p>Waiting for data from the news agent...</p>
            </div>
        `;
        return;
    }
    
    articlesList.innerHTML = newsArticles.map((article, index) => 
        createArticleCard(article, index + 1)
    ).join('');
    
    // Add click handlers
    document.querySelectorAll('.article-card').forEach(card => {
        card.addEventListener('click', () => openArticleDetail(card.dataset.id));
    });
}

// Create article card HTML
function createArticleCard(article, number) {
    const timeAgo = getTimeAgo(article.date);
    const titleWithHighlights = highlightKeywords(article.title, article.highlights || []);
    
    return `
        <article class="article-card" data-id="${article.id}" role="button" tabindex="0">
            <span class="article-number">${number}</span>
            <div class="article-content">
                <div class="article-source">
                    <span class="source-dot"></span>
                    ${article.source}
                </div>
                <h3 class="article-title">${titleWithHighlights}</h3>
                <p class="article-preview">${article.summary}</p>
                <span class="article-time">${timeAgo}</span>
            </div>
        </article>
    `;
}

// Highlight keywords in title
function highlightKeywords(title, keywords) {
    if (!keywords || keywords.length === 0) return title;
    
    let result = title;
    keywords.forEach(keyword => {
        const regex = new RegExp(`(${escapeRegex(keyword)})`, 'gi');
        result = result.replace(regex, '<span class="highlight">$1</span>');
    });
    return result;
}

// Escape regex special characters
function escapeRegex(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

// Get time ago string
function getTimeAgo(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays === 1) return 'yesterday';
    if (diffDays < 7) return `${diffDays}d ago`;
    return `${Math.floor(diffDays / 7)}w ago`;
}

// Setup detail view
function setupDetailView() {
    btnBack.addEventListener('click', closeArticleDetail);
    
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && articleDetail.classList.contains('active')) {
            closeArticleDetail();
        }
    });
}

// Open article detail
function openArticleDetail(articleId) {
    const article = newsArticles.find(a => a.id === parseInt(articleId));
    if (!article) return;
    
    currentArticle = article;
    
    document.getElementById('detail-source').textContent = article.source;
    document.getElementById('detail-time').textContent = getTimeAgo(article.date);
    document.getElementById('detail-title').innerHTML = highlightKeywords(article.title, article.highlights || []);
    document.getElementById('detail-summary').textContent = article.summary;
    document.getElementById('btn-read-full').href = article.link;
    
    // Render overview if available
    const overviewSection = document.getElementById('detail-overview-section');
    const overviewList = document.getElementById('overview-list');
    
    if (article.overview && article.overview.length > 0) {
        overviewSection.style.display = 'block';
        overviewList.innerHTML = article.overview.map(point => `<li>${point}</li>`).join('');
    } else {
        overviewSection.style.display = 'none';
    }
    
    articleDetail.classList.add('active');
    document.body.style.overflow = 'hidden';
}

// Close article detail
function closeArticleDetail() {
    articleDetail.classList.remove('active');
    document.body.style.overflow = '';
    currentArticle = null;
}

// ============================================================
// LOG
// ============================================================
console.log('🚀 WAIMAKERS News Dashboard ready');
console.log('📡 API Functions available:');
console.log('   - window.setUserName(name) - Set user name for greeting');
console.log('   - window.onStartFetchNews(callback) - Register callback for Start button');
console.log('   - window.loadNewsData(articles) - Load news articles');
console.log('   - window.setPodcastLink(url) - Set podcast link');
