const API_URL = 'http://localhost:8000/api/v1'
const API_KEY = 'obrail-api-key-2026'

const HEADERS = {
  'X-API-Key': API_KEY,
  'Content-Type': 'application/json',
}

export async function fetchApi<T>(endpoint: string): Promise<T | null> {
  try {
    const res = await fetch(`${API_URL}${endpoint}`, { headers: HEADERS })
    if (!res.ok) return null
    return res.json() as Promise<T>
  } catch {
    return null
  }
}

export async function checkHealth(): Promise<boolean> {
  try {
    const res = await fetch('http://localhost:8000/health')
    if (!res.ok) return false
    const data = await res.json()
    return data.status === 'healthy'
  } catch {
    return false
  }
}
