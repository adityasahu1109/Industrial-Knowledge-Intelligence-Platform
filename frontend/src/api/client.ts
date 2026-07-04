// Fetch API wrapper for JSON requests
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

export async function fetchJson(endpoint: string, options: RequestInit = {}) {
  const url = `${API_URL}${endpoint}`;
  
  const headers = new Headers(options.headers || {});
  if (!headers.has('Accept')) {
    headers.set('Accept', 'application/json');
  }
  if (!headers.has('Content-Type') && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }

  const response = await fetch(url, { ...options, headers });
  
  if (!response.ok) {
    const error = await response.text();
    throw new Error(error || `HTTP error ${response.status}`);
  }
  
  return response.json();
}
