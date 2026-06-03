import { useState, useEffect, useCallback, useRef } from 'react';
import { Search, RefreshCw, Zap, Globe } from 'lucide-react';
import { fetchArticles, fetchStats, triggerFetch, addBookmark, removeBookmark } from '../utils/api';
import ArticleCard from './ArticleCard';
import toast from 'react-hot-toast';

const REGIONS = ['All Regions', 'Middle East', 'North America', 'Europe', 'Africa', 'Asia-Pacific', 'Latin America', 'Russia/FSU'];
const TOPICS = ['All Topics', 'Upstream', 'Downstream', 'LNG', 'Refining', 'Prices', 'Geopolitics', 'Pipeline', 'Energy Transition'];
const SOURCE_TYPES = ['All Sources', 'Wire Service', 'Government', 'Analysis', 'Social'];

export default function NewsFeed({ bookmarkIds, onBookmarksChange }) {
  const [articles, setArticles] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [fetching, setFetching] = useState(false);
  const [search, setSearch] = useState('');
  const [region, setRegion] = useState('All Regions');
  const [topic, setTopic] = useState('All Topics');
  const [sourceType, setSourceType] = useState('All Sources');
  const [geoOnly, setGeoOnly] = useState(false);
  const [politicalOnly, setPoliticalOnly] = useState(false);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const searchTimeout = useRef(null);

  const loadArticles = useCallback(async (reset = true) => {
    try {
      setLoading(reset);
      const currentPage = reset ? 1 : page;
      const params = {
        page: currentPage,
        page_size: 25,
        hours: 72,
      };
      if (region !== 'All Regions') params.region = region;
      if (topic !== 'All Topics') params.topic = topic;
      if (sourceType !== 'All Sources') params.source_type = sourceType;
      if (search) params.search = search;
      if (geoOnly) params.geo_trigger_only = true;
      if (politicalOnly) params.political_only = true;

      const data = await fetchArticles(params);
      if (reset) {
        setArticles(data);
        setPage(2);
      } else {
        setArticles(prev => [...prev, ...data]);
        setPage(p => p + 1);
      }
      setHasMore(data.length === 25);
    } catch (e) {
      if (reset) setArticles([]);
    } finally {
      setLoading(false);
    }
  }, [region, topic, sourceType, search, geoOnly, politicalOnly, page]);

  // Reload on filter change
  useEffect(() => {
    setPage(1);
    loadArticles(true);
  }, [region, topic, sourceType, geoOnly, politicalOnly]);

  // Debounced search
  useEffect(() => {
    clearTimeout(searchTimeout.current);
    searchTimeout.current = setTimeout(() => {
      setPage(1);
      loadArticles(true);
    }, 400);
    return () => clearTimeout(searchTimeout.current);
  }, [search]);

  // Auto-refresh every 60 seconds
  useEffect(() => {
    loadStats();
    const interval = setInterval(() => {
      loadArticles(true);
      loadStats();
    }, 60000);
    return () => clearInterval(interval);
  }, []);

  const loadStats = async () => {
    try {
      const s = await fetchStats();
      setStats(s);
    } catch (e) {}
  };

  const handleFetchNow = async () => {
    setFetching(true);
    try {
      await triggerFetch();
      toast.success('Fetching latest news...');
      setTimeout(() => {
        loadArticles(true);
        setFetching(false);
      }, 5000);
    } catch (e) {
      toast.error('Fetch failed');
      setFetching(false);
    }
  };

  const handleBookmark = async (articleId) => {
    try {
      await addBookmark(articleId);
      onBookmarksChange();
      toast.success('Bookmarked');
    } catch (e) {}
  };

  const handleRemoveBookmark = async (articleId) => {
    try {
      await removeBookmark(articleId);
      onBookmarksChange();
      toast.success('Bookmark removed');
    } catch (e) {}
  };

  return (
    <>
      {/* Sidebar filters */}
      <aside className="sidebar">
        <div className="sidebar-section">
          <div className="sidebar-title">Overview</div>
          {stats && (
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-value">{stats.last_24h}</div>
                <div className="stat-label">24h Articles</div>
              </div>
              <div className="stat-card">
                <div className="stat-value" style={{ color: stats.geo_triggers_24h > 0 ? '#e05252' : '#c8a951' }}>
                  {stats.geo_triggers_24h}
                </div>
                <div className="stat-label">⚡ Alerts</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">{stats.total_articles}</div>
                <div className="stat-label">Total</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">{stats.sources_count}</div>
                <div className="stat-label">Sources</div>
              </div>
            </div>
          )}
        </div>

        <div className="sidebar-section">
          <div className="sidebar-title">Quick Filters</div>
          <button
            className={`filter-btn ${geoOnly ? 'active' : ''}`}
            onClick={() => { setGeoOnly(!geoOnly); setPoliticalOnly(false); }}
          >
            <span style={{ color: '#e05252' }}>⚡</span> High Priority Only
          </button>
          <button
            className={`filter-btn ${politicalOnly ? 'active' : ''}`}
            onClick={() => { setPoliticalOnly(!politicalOnly); setGeoOnly(false); }}
          >
            <span>🏛️</span> Political/Geopolitical
          </button>
        </div>

        <div className="sidebar-section">
          <div className="sidebar-title">Region</div>
          {REGIONS.map(r => (
            <button
              key={r}
              className={`filter-btn ${region === r ? 'active' : ''}`}
              onClick={() => setRegion(r)}
            >
              <Globe size={11} />
              {r}
            </button>
          ))}
        </div>

        <div className="sidebar-section">
          <div className="sidebar-title">Topic</div>
          {TOPICS.map(t => (
            <button
              key={t}
              className={`filter-btn ${topic === t ? 'active' : ''}`}
              onClick={() => setTopic(t)}
            >
              {t}
            </button>
          ))}
        </div>

        <div className="sidebar-section">
          <div className="sidebar-title">Source Type</div>
          {SOURCE_TYPES.map(s => (
            <button
              key={s}
              className={`filter-btn ${sourceType === s ? 'active' : ''}`}
              onClick={() => setSourceType(s)}
            >
              {s}
            </button>
          ))}
        </div>
      </aside>

      {/* Feed */}
      <main className="feed-area">
        <div className="feed-toolbar">
          <div className="search-wrap">
            <Search size={14} className="search-icon" />
            <input
              className="search-input"
              placeholder="Search articles..."
              value={search}
              onChange={e => setSearch(e.target.value)}
            />
          </div>

          <button
            className="toolbar-btn toolbar-btn-outline"
            onClick={handleFetchNow}
            disabled={fetching}
          >
            <RefreshCw size={13} className={fetching ? 'spin' : ''} />
            {fetching ? 'Fetching...' : 'Refresh Now'}
          </button>

          <span className="feed-count">
            {articles.length} articles
            {stats?.last_fetch && ` · Updated ${new Date(stats.last_fetch).toLocaleTimeString()}`}
          </span>
        </div>

        {loading ? (
          <div className="loading">
            <div className="spinner" />
            <span>Loading news...</span>
          </div>
        ) : articles.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">🛢️</div>
            <div>No articles found</div>
            <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
              Try adjusting filters or click Refresh Now
            </div>
          </div>
        ) : (
          <>
            {articles.map(article => (
              <ArticleCard
                key={article.id}
                article={article}
                bookmarked={bookmarkIds.has(article.id)}
                onBookmark={handleBookmark}
                onRemoveBookmark={handleRemoveBookmark}
              />
            ))}
            {hasMore && (
              <div style={{ padding: 20, textAlign: 'center' }}>
                <button
                  className="toolbar-btn toolbar-btn-outline"
                  onClick={() => loadArticles(false)}
                >
                  Load more
                </button>
              </div>
            )}
          </>
        )}
      </main>
    </>
  );
}
