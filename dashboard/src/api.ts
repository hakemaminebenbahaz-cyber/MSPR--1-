const API_URL = 'http://localhost:8001/api/v1'

export async function fetchApi<T>(endpoint: string): Promise<T | null> {
  try {
    const res = await fetch(`${API_URL}${endpoint}`)
    if (!res.ok) return null
    return res.json() as Promise<T>
  } catch {
    return null
  }
}

export async function checkHealth(): Promise<boolean> {
  try {
    const res = await fetch('http://localhost:8001/health')
    if (!res.ok) return false
    const data = await res.json()
    return data.status === 'healthy'
  } catch {
    return false
  }
}
