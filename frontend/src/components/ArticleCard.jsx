import { formatDistanceToNow } from 'date-fns';
import { Bookmark, BookmarkCheck, ExternalLink, Globe } from 'lucide-react';

const SENTIMENT_COLORS = {
  positive: '#4caf82',
  negative: '#e05252',
  neutral: '#555568',
};

const REGION_COLORS = {
  'Middle East': '#e8885a',
  'North America': '#5b8def',
  'Europe': '#8b6fd1',
  'Africa': '#4caf82',
  'Asia-Pacific': '#e8c96a',
  'Latin America': '#e05252',
  'Russia/FSU': '#9e9ebb',
  'Global': '#555568',
};

export default function ArticleCard({ article, bookmarked, onBookmark, onRemoveBookmark }) {
  const isBookmarked = bookmarked;
  const displayTitle = article.title_en || article.title;
  const displaySummary = article.summary_en || article.summary;
  const isTranslated = article.lang_original && article.lang_original !== 'en';

  const timeAgo = (() => {
    try {
      return formatDistanceToNow(new Date(article.published_at), { addSuffix: true });
    } catch {
      return '';
    }
  })();

  const relevancePct = Math.min(article.relevance_score || 0, 100);
  const relevanceColor = relevancePct >= 80 ? '#e05252' : relevancePct >= 50 ? '#c8a951' : '#2a2a48';

  return (
    <div
      className={`article-card ${article.is_geopolitical_trigger ? 'geo-trigger' : article.is_political ? 'political' : ''}`}
    >
      {/* Relevance bar */}
      <div
        className="relevance-bar"
        style={{ background: relevanceColor, opacity: 0.4 + relevancePct / 200 }}
      />

      {/* Meta row */}
      <div className="article-meta">
        {article.is_geopolitical_trigger && (
          <span className="meta-tag tag-alert">⚡ HIGH PRIORITY</span>
        )}
        {article.is_political && !article.is_geopolitical_trigger && (
          <span className="meta-tag tag-political">🏛️ Political</span>
        )}
        <span className="meta-tag tag-region" style={{ background: `${REGION_COLORS[article.region] || '#555'}18`, color: REGION_COLORS[article.region] || '#888' }}>
          {article.region}
        </span>
        {article.topic && article.topic !== 'General' && (
          <span className="meta-tag tag-topic">{article.topic}</span>
        )}
        {isTranslated && (
          <span className="meta-tag tag-lang">
            <Globe size={9} /> {article.lang_original?.toUpperCase()} → EN
          </span>
        )}
        <span className="meta-tag tag-source">{article.source}</span>
        {article.source_type === 'Government' && (
          <span className="meta-tag" style={{ background: 'rgba(76,175,130,0.1)', color: '#4caf82', fontFamily: 'IBM Plex Mono' }}>GOV</span>
        )}
      </div>

      {/* Title */}
      <div className="article-title">{displayTitle}</div>

      {/* Summary */}
      {displaySummary && (
        <div className="article-summary">{displaySummary}</div>
      )}

      {/* Cluster info */}
      {article.cluster_size > 1 && (
        <div className="cluster-badge">
          <span style={{ color: '#c8a951' }}>📰</span>
          Also covered by: {article.cluster_sources?.slice(0, 4).join(', ')}
          {article.cluster_size > 5 && ` +${article.cluster_size - 5} more`}
        </div>
      )}

      {/* Footer */}
      <div className="article-footer">
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <span
            className="sentiment-dot"
            style={{ background: SENTIMENT_COLORS[article.sentiment] || '#555' }}
            title={`Sentiment: ${article.sentiment}`}
          />
          <span className="article-time">{timeAgo}</span>
          {article.credibility >= 9 && (
            <span style={{ fontSize: 10, color: '#4caf82', fontFamily: 'IBM Plex Mono' }}>★ VERIFIED</span>
          )}
        </div>

        <div className="article-actions">
          <button
            className={`action-btn ${isBookmarked ? 'bookmarked' : ''}`}
            onClick={(e) => {
              e.stopPropagation();
              isBookmarked ? onRemoveBookmark(article.id) : onBookmark(article.id);
            }}
            title={isBookmarked ? 'Remove bookmark' : 'Bookmark'}
          >
            {isBookmarked ? <BookmarkCheck size={13} /> : <Bookmark size={13} />}
          </button>
          <a
            href={article.url}
            target="_blank"
            rel="noopener noreferrer"
            className="action-btn"
            onClick={(e) => e.stopPropagation()}
            title="Open article"
          >
            <ExternalLink size={13} /> Read
          </a>
        </div>
      </div>
    </div>
  );
}
