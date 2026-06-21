const BASE = "";

export async function detectViolation(file) {
  const form = new FormData();
  form.append("image", file);
  const res = await fetch(`${BASE}/api/detect`, { method: "POST", body: form });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const err = new Error(body.detail || `Request failed (${res.status})`);
    err.status = res.status;
    throw err;
  }
  return res.json();
}

export async function getAnalyticsSummary() {
  const res = await fetch(`${BASE}/api/analytics/summary`);
  if (!res.ok) throw new Error("Failed to load analytics");
  return res.json();
}

export async function listViolations(limit = 20) {
  const res = await fetch(`${BASE}/api/violations?limit=${limit}`);
  if (!res.ok) throw new Error("Failed to load violations");
  return res.json();
}

export function imageUrl(path) {
  if (!path) return null;
  return path.startsWith("http") ? path : path;
}
