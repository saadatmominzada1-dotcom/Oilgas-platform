import { useState, useEffect, useCallback } from 'react';
import { Toaster } from 'react-hot-toast';
import { Zap, Bookmark, Settings, Newspaper } from 'lucide-react';
import './index.css';

import PriceTicker from './components/PriceTicker';
import NewsFeed from './components/NewsFeed';
import AlertsPage from './components/AlertsPage';
import BookmarksPage from './components/BookmarksPage';
import SettingsPage from './components/SettingsPage';
import { fetchBookmarks } from './utils/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('feed');
  const [bookmarkIds, setBookmarkIds] = useState(new Set());
  const [backendReady, setBackendReady] = useState(null);

  // Check backend health
  useEffect(() => {
    fetch('http://localhost:8000/api/health')
      .then(r => r.ok ? setBackendReady(true) : setBackendReady(false))
      .catch(() => setBackendReady(false));
  }, []);

  const loadBookmarkIds = useCallback(async () => {
    try {
      const data = await fetchBookmarks();
      setBookmarkIds(new Set(data.map(b => b.article_id)));
    } catch (e) {}
  }, []);

  useEffect(() => { loadBookmarkIds(); }, [loadBookmarkIds]);

  const NAV = [
    { id: 'feed', label: 'News Feed', icon: Newspaper },
    { id: 'alerts', label: 'Alerts', icon: Zap },
    { id: 'bookmarks', label: 'Bookmarks', icon: Bookmark },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <div className="app">
      <Toaster
        position="bottom-right"
        toastOptions={{
          style: {
            background: 'var(--bg-card)',
            color: 'var(--text-primary)',
            border: '1px solid var(--border)',
            fontFamily: 'IBM Plex Sans',
            fontSize: 13,
          },
        }}
      />

      {/* Commodity Price Ticker */}
      <PriceTicker />

      {/* Header */}
      <header className="header">
        <div className="logo">
          <div className="logo-icon">🛢️</div>
          <div>
            <div className="logo-text">OilGas Intel</div>
            <div className="logo-sub">Real-Time Intelligence Platform</div>
          </div>
        </div>

        <nav className="header-nav">
          {NAV.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              className={`nav-btn ${activeTab === id ? 'active' : ''}`}
              onClick={() => setActiveTab(id)}
            >
              <Icon size={14} />
              {label}
            </button>
          ))}
        </nav>

        <div className="header-right">
          {backendReady === false && (
            <span style={{ fontSize: 11, color: 'var(--red)', fontFamily: 'IBM Plex Mono' }}>
              ⚠ Backend offline
            </span>
          )}
          {backendReady === true && (
            <div className="live-badge">
              <div className="live-dot" />
              LIVE
            </div>
          )}
        </div>
      </header>

      {/* Backend offline warning */}
      {backendReady === false && (
        <div style={{
          background: 'rgba(224,82,82,0.08)', borderBottom: '1px solid rgba(224,82,82,0.2)',
          padding: '10px 24px', fontSize: 13, color: 'var(--red)', display: 'flex', gap: 8
        }}>
          <strong>Backend not running.</strong> Start the backend first: run <code style={{ background: 'rgba(255,255,255,0.05)', padding: '1px 6px', borderRadius: 4 }}>python main.py</code> in the <code style={{ background: 'rgba(255,255,255,0.05)', padding: '1px 6px', borderRadius: 4 }}>backend/</code> folder.
        </div>
      )}

      {/* Main Content */}
      <div className="main-layout">
        {activeTab === 'feed' && (
          <NewsFeed
            bookmarkIds={bookmarkIds}
            onBookmarksChange={loadBookmarkIds}
          />
        )}
        {activeTab === 'alerts' && <AlertsPage />}
        {activeTab === 'bookmarks' && <BookmarksPage onBookmarksChange={loadBookmarkIds} />}
        {activeTab === 'settings' && <SettingsPage />}
      </div>
    </div>
  );
}
