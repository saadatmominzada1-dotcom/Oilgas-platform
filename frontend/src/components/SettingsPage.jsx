import { useState, useEffect } from 'react';
import { fetchDigestConfig, updateDigestConfig, sendDigestNow, fetchSources } from '../utils/api';
import toast from 'react-hot-toast';

const REGIONS = ['Middle East', 'North America', 'Europe', 'Africa', 'Asia-Pacific', 'Latin America', 'Russia/FSU'];
const TOPICS = ['Upstream', 'Downstream', 'LNG', 'Prices', 'Geopolitics', 'Pipeline', 'Energy Transition'];

export default function SettingsPage() {
  const [config, setConfig] = useState(null);
  const [sources, setSources] = useState([]);
  const [saving, setSaving] = useState(false);
  const [sending, setSending] = useState(false);
  const [activeTab, setActiveTab] = useState('digest');

  useEffect(() => {
    loadConfig();
    loadSources();
  }, []);

  const loadConfig = async () => {
    try {
      const data = await fetchDigestConfig();
      setConfig(data ? {
        enabled: false, delivery_time: '07:00', timezone: 'UTC',
        regions: [], topics: [], slack_webhook: '', teams_webhook: '',
        slack_enabled: false, teams_enabled: false,
        telegram_enabled: false, telegram_bot_token: '', telegram_chat_id: '',
        ...data  // override defaults with whatever is in DB
      } : {
        enabled: false, delivery_time: '07:00', timezone: 'UTC',
        regions: [], topics: [], slack_webhook: '', teams_webhook: '',
        slack_enabled: false, teams_enabled: false,
        telegram_enabled: false, telegram_bot_token: '', telegram_chat_id: ''
      });
    } catch (e) {}
  };

  const loadSources = async () => {
    try { setSources(await fetchSources()); } catch (e) {}
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await updateDigestConfig(config);
      toast.success('Settings saved!');
    } catch (e) {
      toast.error('Failed to save');
    } finally {
      setSaving(false);
    }
  };

  const handleSendNow = async () => {
    setSending(true);
    try {
      await sendDigestNow();
      toast.success('Digest sending now! Check your Slack/Teams channel.');
    } catch (e) {
      toast.error('Failed to send digest');
    } finally {
      setSending(false);
    }
  };

  const toggleChip = (field, value) => {
    setConfig(c => ({
      ...c,
      [field]: c[field]?.includes(value)
        ? c[field].filter(v => v !== value)
        : [...(c[field] || []), value]
    }));
  };

  if (!config) return <div className="loading"><div className="spinner" /></div>;

  return (
    <div className="page-view">
      <h1 className="page-title">Settings</h1>
      <p className="page-subtitle">Configure your daily digest, notification channels, and data sources.</p>

      {/* Tab Bar */}
      <div style={{ display: 'flex', gap: 4, marginBottom: 28, borderBottom: '1px solid var(--border)', paddingBottom: 0 }}>
        {[['digest', '📊 Daily Digest'], ['sources', '📡 Sources']].map(([id, label]) => (
          <button
            key={id}
            onClick={() => setActiveTab(id)}
            style={{
              padding: '10px 20px', background: 'transparent',
              borderBottom: activeTab === id ? '2px solid var(--gold)' : '2px solid transparent',
              color: activeTab === id ? 'var(--gold)' : 'var(--text-secondary)',
              fontSize: 13, fontWeight: 500, marginBottom: -1,
              transition: 'all 0.15s'
            }}
          >
            {label}
          </button>
        ))}
      </div>

      {activeTab === 'digest' && (
        <>
          {/* Enable / Timing */}
          <div className="card">
            <div className="card-title" style={{ marginBottom: 16 }}>Daily Digest Schedule</div>

            <div className="form-group">
              <label style={{ display: 'flex', alignItems: 'center', gap: 10, cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  checked={config.enabled}
                  onChange={e => setConfig(c => ({ ...c, enabled: e.target.checked }))}
                  style={{ accentColor: 'var(--gold)', width: 16, height: 16 }}
                />
                <span style={{ fontSize: 14, fontWeight: 500 }}>Enable daily digest</span>
              </label>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
              <div className="form-group">
                <label className="form-label">Delivery Time</label>
                <input
                  type="time"
                  className="form-control"
                  value={config.delivery_time}
                  onChange={e => setConfig(c => ({ ...c, delivery_time: e.target.value }))}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Timezone</label>
                <input
                  className="form-control"
                  value={config.timezone}
                  onChange={e => setConfig(c => ({ ...c, timezone: e.target.value }))}
                  placeholder="e.g. Europe/London"
                />
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Regions to include (empty = all)</label>
              <div className="chip-group">
                {REGIONS.map(r => (
                  <button
                    type="button"
                    key={r}
                    className={`chip ${config.regions?.includes(r) ? 'selected' : ''}`}
                    onClick={() => toggleChip('regions', r)}
                  >
                    {r}
                  </button>
                ))}
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Topics to include (empty = all)</label>
              <div className="chip-group">
                {TOPICS.map(t => (
                  <button
                    type="button"
                    key={t}
                    className={`chip ${config.topics?.includes(t) ? 'selected' : ''}`}
                    onClick={() => toggleChip('topics', t)}
                  >
                    {t}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Slack */}
          <div className="card">
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
              <div className="card-title">Slack Integration</div>
              <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }}>
                <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>Enabled</span>
                <button
                  type="button"
                  className="toggle"
                  style={{ background: config.slack_enabled ? 'var(--gold)' : 'var(--border-bright)' }}
                  onClick={() => setConfig(c => ({ ...c, slack_enabled: !c.slack_enabled }))}
                >
                  <span style={{
                    display: 'block', width: 14, height: 14, background: 'white',
                    borderRadius: '50%', margin: 3,
                    marginLeft: config.slack_enabled ? 'auto' : 3,
                    marginRight: config.slack_enabled ? 3 : 'auto'
                  }} />
                </button>
              </label>
            </div>

            <div className="instruction-box">
              <h4>🔧 How to connect Slack</h4>
              <ol>
                <li>Go to <strong>api.slack.com/apps</strong> and create a new app (or use an existing one)</li>
                <li>Under <strong>Features</strong>, click <strong>Incoming Webhooks</strong> and toggle it ON</li>
                <li>Click <strong>Add New Webhook to Workspace</strong></li>
                <li>Select the channel where you want the digest to appear</li>
                <li>Copy the <strong>Webhook URL</strong> (starts with https://hooks.slack.com/...)</li>
                <li>Paste it below and save</li>
              </ol>
            </div>

            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label">Slack Webhook URL</label>
              <input
                className="form-control"
                placeholder="https://hooks.slack.com/services/XXX/YYY/ZZZ"
                value={config.slack_webhook || ''}
                onChange={e => setConfig(c => ({ ...c, slack_webhook: e.target.value }))}
              />
            </div>
          </div>

          {/* Teams */}
          <div className="card">
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
              <div className="card-title">Microsoft Teams Integration</div>
              <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }}>
                <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>Enabled</span>
                <button
                  type="button"
                  className="toggle"
                  style={{ background: config.teams_enabled ? 'var(--gold)' : 'var(--border-bright)' }}
                  onClick={() => setConfig(c => ({ ...c, teams_enabled: !c.teams_enabled }))}
                >
                  <span style={{
                    display: 'block', width: 14, height: 14, background: 'white',
                    borderRadius: '50%', margin: 3,
                    marginLeft: config.teams_enabled ? 'auto' : 3,
                    marginRight: config.teams_enabled ? 3 : 'auto'
                  }} />
                </button>
              </label>
            </div>

            <div className="instruction-box">
              <h4>🔧 How to connect Microsoft Teams</h4>
              <ol>
                <li>Open <strong>Microsoft Teams</strong> and navigate to the target channel</li>
                <li>Click the <strong>···</strong> (More options) button next to the channel name</li>
                <li>Select <strong>Connectors</strong> from the dropdown menu</li>
                <li>Search for <strong>Incoming Webhook</strong> and click <strong>Configure</strong></li>
                <li>Give the webhook a name like <em>"OilGas Daily Digest"</em> and optionally upload an icon</li>
                <li>Click <strong>Create</strong> and copy the generated URL</li>
                <li>Paste it below and click Save Settings</li>
              </ol>
            </div>

            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label">Teams Webhook URL</label>
              <input
                className="form-control"
                placeholder="https://outlook.office.com/webhook/..."
                value={config.teams_webhook || ''}
                onChange={e => setConfig(c => ({ ...c, teams_webhook: e.target.value }))}
              />
            </div>
          </div>

          {/* Telegram */}
          <div className="card">
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
              <div className="card-title">Telegram Integration</div>
              <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }}>
                <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>Enabled</span>
                <button
                  type="button"
                  className="toggle"
                  style={{ background: config.telegram_enabled ? 'var(--gold)' : 'var(--border-bright)' }}
                  onClick={() => setConfig(c => ({ ...c, telegram_enabled: !c.telegram_enabled }))}
                >
                  <span style={{
                    display: 'block', width: 14, height: 14, background: 'white',
                    borderRadius: '50%', margin: 3,
                    marginLeft: config.telegram_enabled ? 'auto' : 3,
                    marginRight: config.telegram_enabled ? 3 : 'auto'
                  }} />
                </button>
              </label>
            </div>

            <div className="instruction-box">
              <h4>🔧 How to connect Telegram</h4>
              <ol>
                <li>Open Telegram and search for <strong>@BotFather</strong></li>
                <li>Send <code>/newbot</code> and follow the prompts to create your bot</li>
                <li>BotFather gives you a <strong>Bot Token</strong> — copy it below</li>
                <li>Add your bot to the group/channel where you want digests sent</li>
                <li>To get your <strong>Chat ID</strong>: visit <code>https://api.telegram.org/bot&lt;YOUR_TOKEN&gt;/getUpdates</code> in your browser after sending a message to the bot — look for <code>"chat":&#123;"id": ...&#125;</code></li>
                <li>For a personal chat: just message your bot directly and use your personal chat ID</li>
              </ol>
            </div>

            <div className="form-group">
              <label className="form-label">Bot Token</label>
              <input
                className="form-control"
                placeholder="123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ"
                value={config.telegram_bot_token || ''}
                onChange={e => setConfig(c => ({ ...c, telegram_bot_token: e.target.value }))}
              />
            </div>
            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label">Chat ID</label>
              <input
                className="form-control"
                placeholder="-1001234567890 (group) or 123456789 (personal)"
                value={config.telegram_chat_id || ''}
                onChange={e => setConfig(c => ({ ...c, telegram_chat_id: e.target.value }))}
              />
              <p className="form-hint">Negative numbers are groups/channels. Positive numbers are personal chats.</p>
            </div>
          </div>

          {/* Actions */}
          <div style={{ display: 'flex', gap: 12 }}>
            <button className="btn-primary" onClick={handleSave} disabled={saving}>
              {saving ? 'Saving...' : 'Save Settings'}
            </button>
            <button
              className="toolbar-btn toolbar-btn-outline"
              onClick={handleSendNow}
              disabled={sending}
              style={{ padding: '10px 20px' }}
            >
              {sending ? 'Sending...' : '📤 Send Digest Now (Test)'}
            </button>
          </div>
        </>
      )}

      {activeTab === 'sources' && (
        <div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 1, background: 'var(--border)', borderRadius: 10, overflow: 'hidden', border: '1px solid var(--border)' }}>
            {/* Header */}
            {['Source', 'Region', 'Type'].map(h => (
              <div key={h} style={{
                padding: '10px 14px', background: 'var(--bg-card)',
                fontFamily: 'IBM Plex Mono', fontSize: 10, color: 'var(--text-muted)',
                textTransform: 'uppercase', letterSpacing: 1
              }}>
                {h}
              </div>
            ))}
            {sources.map((s, i) => (
              <>
                <div key={`n${i}`} style={{ padding: '10px 14px', background: 'var(--bg-secondary)', fontSize: 13 }}>{s.name}</div>
                <div key={`r${i}`} style={{ padding: '10px 14px', background: 'var(--bg-secondary)', fontSize: 12, color: 'var(--text-secondary)' }}>{s.region}</div>
                <div key={`t${i}`} style={{ padding: '10px 14px', background: 'var(--bg-secondary)', display: 'flex', gap: 6 }}>
                  <span className="meta-tag" style={{
                    background: s.source_type === 'Government' ? 'rgba(76,175,130,0.1)' : 'rgba(200,169,81,0.08)',
                    color: s.source_type === 'Government' ? '#4caf82' : 'var(--gold)',
                    fontFamily: 'IBM Plex Mono', fontSize: 10
                  }}>{s.source_type}</span>
                  {s.language !== 'en' && (
                    <span className="meta-tag tag-lang" style={{ fontFamily: 'IBM Plex Mono', fontSize: 10 }}>{s.language?.toUpperCase()}</span>
                  )}
                </div>
              </>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
