// ============================================================
// WAIMAKERS News Dashboard
// ============================================================
// Dit dashboard wacht op data van een andere agent.
// Roep window.loadNewsData(articles) aan om het te vullen.
// ============================================================

// Placeholder voor nieuwsartikelen
let newsArticles = [];

// State
let currentArticle = null;

// DOM Elements
const articlesList = document.getElementById('articles-list');
const articleDetail = document.getElementById('article-detail');
const btnBack = document.getElementById('btn-back');
const loadingState = document.getElementById('loading-state');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupDetailView();
    showLoadingState();
    updateHeaderDate();
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
console.log('📡 Waiting for data... Call window.loadNewsData(articles)');
