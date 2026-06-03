import { useState, useEffect } from 'react';
import { fetchBookmarks, removeBookmark } from '../utils/api';
import { BookmarkX } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import toast from 'react-hot-toast';

export default function BookmarksPage({ onBookmarksChange }) {
  const [bookmarks, setBookmarks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => { load(); }, []);

  const load = async () => {
    setLoading(true);
    try {
      const data = await fetchBookmarks();
      setBookmarks(data);
    } catch (e) {}
    finally { setLoading(false); }
  };

  const handleRemove = async (articleId) => {
    try {
      await removeBookmark(articleId);
      toast.success('Bookmark removed');
      load();
      onBookmarksChange();
    } catch (e) {}
  };

  return (
    <div className="page-view">
      <h1 className="page-title">Bookmarks</h1>
      <p className="page-subtitle">Your saved articles for later reference.</p>

      {loading ? (
        <div className="loading"><div className="spinner" /></div>
      ) : bookmarks.length === 0 ? (
        <div className="empty-state" style={{ background: 'var(--bg-card)', borderRadius: 12, border: '1px solid var(--border)', padding: 60 }}>
          <div className="empty-icon">🔖</div>
          <div>No bookmarks yet</div>
          <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Click the bookmark icon on any article to save it here</div>
        </div>
      ) : (
        <div>
          {bookmarks.map(bm => (
            bm.article && (
              <div key={bm.id} className="card" style={{ position: 'relative' }}>
                <div style={{ display: 'flex', gap: 12, alignItems: 'flex-start' }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', gap: 8, marginBottom: 8, flexWrap: 'wrap' }}>
                      <span className="meta-tag tag-region">{bm.article.region}</span>
                      <span className="meta-tag tag-topic">{bm.article.topic}</span>
                      <span className="meta-tag tag-source">{bm.article.source}</span>
                    </div>
                    <div className="card-title" style={{ marginBottom: 6 }}>
                      {bm.article.title_en || bm.article.title}
                    </div>
                    {(bm.article.summary_en || bm.article.summary) && (
                      <div style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6, marginBottom: 10 }}>
                        {(bm.article.summary_en || bm.article.summary)?.slice(0, 280)}...
                      </div>
                    )}
                    <div style={{ display: 'flex', gap: 16, alignItems: 'center' }}>
                      <span style={{ fontFamily: 'IBM Plex Mono', fontSize: 11, color: 'var(--text-muted)' }}>
                        Saved {formatDistanceToNow(new Date(bm.created_at), { addSuffix: true })}
                      </span>
                      <a
                        href={bm.article.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{ fontSize: 12, color: 'var(--gold)' }}
                      >
                        Read article →
                      </a>
                    </div>
                  </div>
                  <button
                    className="btn-danger"
                    onClick={() => handleRemove(bm.article_id)}
                    title="Remove bookmark"
                  >
                    <BookmarkX size={13} />
                  </button>
                </div>
              </div>
            )
          ))}
        </div>
      )}
    </div>
  );
}
