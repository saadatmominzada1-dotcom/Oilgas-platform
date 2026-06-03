import axios from 'axios';

const api = axios.create({
  baseURL: 'https://oilgas-platform-production.up.railway.app',
  timeout: 15000,
});

export const fetchArticles = (params = {}) =>
  api.get('/api/articles', { params }).then(r => r.data);

export const fetchStats = () =>
  api.get('/api/articles/stats').then(r => r.data);

export const fetchPrices = () =>
  api.get('/api/prices').then(r => r.data);

export const triggerFetch = () =>
  api.post('/api/fetch/trigger').then(r => r.data);

export const fetchSources = () =>
  api.get('/api/sources').then(r => r.data);

// Alerts
export const fetchAlerts = () =>
  api.get('/api/alerts').then(r => r.data);

export const createAlert = (data) =>
  api.post('/api/alerts', data).then(r => r.data);

export const updateAlert = (id, data) =>
  api.put(`/api/alerts/${id}`, data).then(r => r.data);

export const deleteAlert = (id) =>
  api.delete(`/api/alerts/${id}`).then(r => r.data);

export const toggleAlert = (id) =>
  api.patch(`/api/alerts/${id}/toggle`).then(r => r.data);

// Bookmarks
export const fetchBookmarks = () =>
  api.get('/api/bookmarks').then(r => r.data);

export const addBookmark = (article_id, note = null) =>
  api.post('/api/bookmarks', { article_id, note }).then(r => r.data);

export const removeBookmark = (article_id) =>
  api.delete(`/api/bookmarks/${article_id}`).then(r => r.data);

// Digest
export const fetchDigestConfig = () =>
  api.get('/api/digest').then(r => r.data);

export const updateDigestConfig = (data) =>
  api.put('/api/digest', data).then(r => r.data);

export const sendDigestNow = () =>
  api.post('/api/digest/send-now').then(r => r.data);

export default api;
