const API_BASE = '/api/v1';

async function jsonPost(path, body) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`${res.status} ${detail}`);
  }
  return res.json();
}

export async function sendChat(message, history = []) {
  const data = await jsonPost('/chat', { message, history });
  return data.reply;
}

export async function analyzeDeployment(repo, question) {
  const data = await jsonPost('/deployments/analyze', { repo, question });
  return data.reply;
}

export async function analyzeIncident(description, namespace = 'default') {
  const data = await jsonPost('/incidents/analyze', { description, namespace });
  return data.reply;
}

export async function listTools() {
  const res = await fetch(`${API_BASE}/tools`);
  if (!res.ok) throw new Error(`Tools list failed: ${res.status}`);
  const data = await res.json();
  return data.tools;
}
