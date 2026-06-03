import { useState, useEffect } from 'react';
import { fetchAlerts, createAlert, deleteAlert, toggleAlert } from '../utils/api';
import { Zap, Trash2, Plus } from 'lucide-react';
import toast from 'react-hot-toast';

const REGIONS = ['Middle East', 'North America', 'Europe', 'Africa', 'Asia-Pacific', 'Latin America', 'Russia/FSU', 'Global'];
const TOPICS = ['Upstream', 'Downstream', 'LNG', 'Prices', 'Geopolitics', 'Pipeline', 'Energy Transition'];

const EMPTY_FORM = {
  name: '',
  description: '',
  regions: [],
  topics: [],
  min_relevance: 40,
  notify_slack: false,
  notify_teams: false,
  slack_webhook: '',
  teams_webhook: '',
  notify_telegram: false,
  telegram_bot_token: '',
  telegram_chat_id: '',
};

export default function AlertsPage() {
  const [alerts, setAlerts] = useState([]);
  const [form, setForm] = useState(EMPTY_FORM);
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => { load(); }, []);

  const load = async () => {
    try {
      const data = await fetchAlerts();
      setAlerts(data);
    } catch (e) {}
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.name || !form.description) {
      toast.error('Name and description are required');
      return;
    }
    setSaving(true);
    try {
      await createAlert(form);
      toast.success('Alert created!');
      setForm(EMPTY_FORM);
      setShowForm(false);
      load();
    } catch (e) {
      toast.error('Failed to create alert');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this alert?')) return;
    try {
      await deleteAlert(id);
      toast.success('Alert deleted');
      load();
    } catch (e) {}
  };

  const handleToggle = async (id) => {
    try {
      await toggleAlert(id);
      load();
    } catch (e) {}
  };

  const toggleChip = (field, value) => {
    setForm(f => ({
      ...f,
      [field]: f[field].includes(value)
        ? f[field].filter(v => v !== value)
        : [...f[field], value]
    }));
  };

  return (
    <div className="page-view">
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 32 }}>
        <div>
          <h1 className="page-title">Custom Alerts</h1>
          <p className="page-subtitle" style={{ marginBottom: 0 }}>
            Describe what you want to monitor in plain language — our AI matches relevant articles automatically.
          </p>
        </div>
        <button className="btn-primary" onClick={() => setShowForm(!showForm)}>
          <Plus size={14} style={{ display: 'inline', marginRight: 6 }} />
          New Alert
        </button>
      </div>

      {/* Create Form */}
      {showForm && (
        <div className="card" style={{ marginBottom: 32 }}>
          <div className="card-title" style={{ marginBottom: 20 }}>Create Alert</div>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">Alert Name</label>
              <input
                className="form-control"
                placeholder="e.g. OPEC Production Cuts"
                value={form.name}
                onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
              />
            </div>

            <div className="form-group">
              <label className="form-label">What do you want to monitor?</label>
              <textarea
                className="form-control"
                rows={3}
                placeholder="e.g. I want to know about any OPEC+ production cuts, Saudi Aramco announcements, and LNG shipments in Southeast Asia"
                value={form.description}
                onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
                style={{ resize: 'vertical' }}
              />
              <p className="form-hint">
                Write naturally — our system extracts keywords and uses semantic matching to find relevant articles.
              </p>
            </div>

            <div className="form-group">
              <label className="form-label">Regions (optional — leave empty for all)</label>
              <div className="chip-group">
                {REGIONS.map(r => (
                  <button
                    type="button"
                    key={r}
                    className={`chip ${form.regions.includes(r) ? 'selected' : ''}`}
                    onClick={() => toggleChip('regions', r)}
                  >
                    {r}
                  </button>
                ))}
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Topics (optional)</label>
              <div className="chip-group">
                {TOPICS.map(t => (
                  <button
                    type="button"
                    key={t}
                    className={`chip ${form.topics.includes(t) ? 'selected' : ''}`}
                    onClick={() => toggleChip('topics', t)}
                  >
                    {t}
                  </button>
                ))}
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Minimum Relevance Score: {form.min_relevance}</label>
              <input
                type="range"
                min={10}
                max={90}
                value={form.min_relevance}
                onChange={e => setForm(f => ({ ...f, min_relevance: Number(e.target.value) }))}
                style={{ width: '100%', accentColor: 'var(--gold)' }}
              />
              <p className="form-hint">Higher = fewer but more relevant alerts. 40 is a good starting point.</p>
            </div>

            <div className="divider" />
            <div className="card-title" style={{ marginBottom: 16, fontSize: 14 }}>Notification Channels</div>

            <div className="form-group">
              <label style={{ display: 'flex', alignItems: 'center', gap: 10, cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  checked={form.notify_slack}
                  onChange={e => setForm(f => ({ ...f, notify_slack: e.target.checked }))}
                  style={{ accentColor: 'var(--gold)', width: 16, height: 16 }}
                />
                <span className="form-label" style={{ margin: 0 }}>Send to Slack</span>
              </label>
              {form.notify_slack && (
                <div style={{ marginTop: 8 }}>
                  <input
                    className="form-control"
                    placeholder="https://hooks.slack.com/services/XXX/YYY/ZZZ"
                    value={form.slack_webhook}
                    onChange={e => setForm(f => ({ ...f, slack_webhook: e.target.value }))}
                  />
                  <div className="instruction-box" style={{ marginTop: 10 }}>
                    <h4>How to get your Slack Webhook URL</h4>
                    <ol>
                      <li>Go to your Slack workspace</li>
                      <li>Click <strong>Apps</strong> in the left sidebar</li>
                      <li>Search for <strong>Incoming WebHooks</strong> and add it</li>
                      <li>Choose the channel where alerts should appear</li>
                      <li>Copy the <strong>Webhook URL</strong> and paste it above</li>
                    </ol>
                  </div>
                </div>
              )}
            </div>

            <div className="form-group">
              <label style={{ display: 'flex', alignItems: 'center', gap: 10, cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  checked={form.notify_teams}
                  onChange={e => setForm(f => ({ ...f, notify_teams: e.target.checked }))}
                  style={{ accentColor: 'var(--gold)', width: 16, height: 16 }}
                />
                <span className="form-label" style={{ margin: 0 }}>Send to Microsoft Teams</span>
              </label>
              {form.notify_teams && (
                <div style={{ marginTop: 8 }}>
                  <input
                    className="form-control"
                    placeholder="https://outlook.office.com/webhook/..."
                    value={form.teams_webhook}
                    onChange={e => setForm(f => ({ ...f, teams_webhook: e.target.value }))}
                  />
                  <div className="instruction-box" style={{ marginTop: 10 }}>
                    <h4>How to get your Teams Webhook URL</h4>
                    <ol>
                      <li>Open Microsoft Teams and go to your target channel</li>
                      <li>Click the <strong>···</strong> (three dots) next to the channel name</li>
                      <li>Select <strong>Connectors</strong></li>
                      <li>Find <strong>Incoming Webhook</strong> and click <strong>Configure</strong></li>
                      <li>Give it a name (e.g. "OilGas Alerts"), click <strong>Create</strong></li>
                      <li>Copy the generated URL and paste it above</li>
                    </ol>
                  </div>
                </div>
              )}
            </div>

            <div className="form-group">
              <label style={{ display: 'flex', alignItems: 'center', gap: 10, cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  checked={form.notify_telegram}
                  onChange={e => setForm(f => ({ ...f, notify_telegram: e.target.checked }))}
                  style={{ accentColor: 'var(--gold)', width: 16, height: 16 }}
                />
                <span className="form-label" style={{ margin: 0 }}>Send to Telegram</span>
              </label>
              {form.notify_telegram && (
                <div style={{ marginTop: 8, display: 'flex', flexDirection: 'column', gap: 8 }}>
                  <input
                    className="form-control"
                    placeholder="Bot Token: 123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ"
                    value={form.telegram_bot_token || ''}
                    onChange={e => setForm(f => ({ ...f, telegram_bot_token: e.target.value }))}
                  />
                  <input
                    className="form-control"
                    placeholder="Chat ID: -1001234567890 (group) or 123456789 (personal)"
                    value={form.telegram_chat_id || ''}
                    onChange={e => setForm(f => ({ ...f, telegram_chat_id: e.target.value }))}
                  />
                  <div className="instruction-box" style={{ marginTop: 4 }}>
                    <h4>How to get Telegram Bot Token + Chat ID</h4>
                    <ol>
                      <li>Message <strong>@BotFather</strong> on Telegram → send <code>/newbot</code> → copy the Bot Token</li>
                      <li>Add your bot to the target group/channel</li>
                      <li>Visit <code>https://api.telegram.org/bot&lt;TOKEN&gt;/getUpdates</code> to find your Chat ID</li>
                    </ol>
                  </div>
                </div>
              )}
            </div>
            <div style={{ display: 'flex', gap: 12, marginTop: 8 }}>
              <button type="submit" className="btn-primary" disabled={saving}>
                {saving ? 'Saving...' : 'Create Alert'}
              </button>
              <button
                type="button"
                className="toolbar-btn toolbar-btn-outline"
                onClick={() => setShowForm(false)}
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Alert List */}
      {alerts.length === 0 ? (
        <div className="empty-state" style={{ background: 'var(--bg-card)', borderRadius: 12, border: '1px solid var(--border)', padding: 60 }}>
          <div className="empty-icon">🔔</div>
          <div>No alerts yet</div>
          <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Create your first alert to get notified about relevant news</div>
        </div>
      ) : (
        <div>
          {alerts.map(alert => (
            <div key={alert.id} className="card" style={{ display: 'flex', alignItems: 'flex-start', gap: 16 }}>
              <Zap size={18} style={{ color: alert.active ? 'var(--gold)' : 'var(--text-muted)', marginTop: 2, flexShrink: 0 }} />
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 4 }}>
                  <div className="card-title">{alert.name}</div>
                  {!alert.active && (
                    <span className="meta-tag" style={{ background: 'var(--bg-secondary)', color: 'var(--text-muted)', fontFamily: 'IBM Plex Mono', fontSize: 10 }}>PAUSED</span>
                  )}
                </div>
                <div style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 8 }}>{alert.description}</div>
                <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginBottom: 8 }}>
                  {alert.keywords_extracted?.slice(0, 6).map(kw => (
                    <span key={kw} className="chip" style={{ fontSize: 11, padding: '2px 8px' }}>{kw}</span>
                  ))}
                </div>
                <div style={{ display: 'flex', gap: 16, fontSize: 11, color: 'var(--text-muted)' }}>
                  {alert.regions?.length > 0 && <span>📍 {alert.regions.join(', ')}</span>}
                  {alert.topics?.length > 0 && <span>🏷️ {alert.topics.join(', ')}</span>}
                  <span>Min relevance: {alert.min_relevance}</span>
                  {alert.notify_slack && <span style={{ color: '#4caf82' }}>✓ Slack</span>}
                  {alert.notify_teams && <span style={{ color: '#5b8def' }}>✓ Teams</span>}
                  {alert.notify_telegram && <span style={{ color: '#29b6f6' }}>✓ Telegram</span>}
                </div>
              </div>
              <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexShrink: 0 }}>
                <button className="toggle on" style={{ background: alert.active ? 'var(--gold)' : 'var(--border-bright)' }} onClick={() => handleToggle(alert.id)}>
                  <span style={{
                    display: 'block', width: 14, height: 14, background: 'white', borderRadius: '50%',
                    margin: 3, marginLeft: alert.active ? 'auto' : 3, marginRight: alert.active ? 3 : 'auto'
                  }} />
                </button>
                <button className="btn-danger" onClick={() => handleDelete(alert.id)}>
                  <Trash2 size={12} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
