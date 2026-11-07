// Standalone frontend integration example. Configure this URL once for your app.
export const API_BASE_URL = 'http://127.0.0.1:8000';

export function createApiClient(baseUrl = API_BASE_URL) {
  let token = null;
  async function request(path, { method = 'GET', body } = {}) {
    const multipart = body instanceof FormData;
    const response = await fetch(`${baseUrl}${path}`, {
      method,
      headers: {
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...(body && !multipart ? { 'Content-Type': 'application/json' } : {}),
      },
      body: body ? (multipart ? body : JSON.stringify(body)) : undefined,
    });
    if (response.status === 204) return null;
    const data = await response.json();
    if (!response.ok) throw new Error(data.error?.message || 'Request failed');
    return data;
  }
  return {
    async register(name, language = 'ml') {
      const session = await request('/api/users', { method: 'POST', body: { name, language } });
      token = session.access_token;
      return session.user;
    },
    chat: (text, session_id = null, language = 'auto') => request('/api/assistant/chat', { method: 'POST', body: { text, session_id, language } }),
    history: id => request(`/api/assistant/history/${encodeURIComponent(id)}`),
    upload(file, language = 'ml') {
      const body = new FormData();
      body.append('file', file);
      body.append('language', language);
      return request('/api/assistant/upload', { method: 'POST', body });
    },
    async logout() {
      await request('/api/users/sessions', { method: 'DELETE' });
      token = null;
    },
    request,
  };
}
