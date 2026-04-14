const defaultBase =
  typeof window !== 'undefined' ? `${window.location.protocol}//${window.location.hostname}:8000/api` : 'http://127.0.0.1:8000/api'
const API_BASE = import.meta.env.VITE_API_BASE || defaultBase

function authHeaders(): Record<string, string> {
  const token = localStorage.getItem('crm-access-token')
  if (!token) {
    return {}
  }
  return { Authorization: `Bearer ${token}` }
}

export async function refreshAccessToken(): Promise<boolean> {
  const refresh = localStorage.getItem('crm-refresh-token')
  if (!refresh) {
    return false
  }
  try {
    const response = await fetch(`${API_BASE}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh }),
    })
    if (!response.ok) {
      return false
    }
    const data = await response.json()
    localStorage.setItem('crm-access-token', data.access)
    return true
  } catch {
    return false
  }
}

export async function apiGet<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      ...authHeaders(),
    },
  })

  if (response.status === 401) {
    const refreshed = await refreshAccessToken()
    if (refreshed) {
      return apiGet(path)
    }
    localStorage.removeItem('crm-access-token')
    localStorage.removeItem('crm-refresh-token')
    localStorage.removeItem('crm-user-role')
    window.location.href = '/login'
    throw new Error('Unauthorized')
  }

  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`)
  }

  return (await response.json()) as T
}

export async function apiPost<T>(path: string, payload: unknown): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...authHeaders(),
    },
    body: JSON.stringify(payload),
  })

  if (response.status === 401) {
    const refreshed = await refreshAccessToken()
    if (refreshed) {
      return apiPost(path, payload)
    }
    localStorage.removeItem('crm-access-token')
    localStorage.removeItem('crm-refresh-token')
    localStorage.removeItem('crm-user-role')
    window.location.href = '/login'
    throw new Error('Unauthorized')
  }

  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`)
  }

  return (await response.json()) as T
}

export async function apiPut<T>(path: string, payload: unknown): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      ...authHeaders(),
    },
    body: JSON.stringify(payload),
  })

  if (response.status === 401) {
    const refreshed = await refreshAccessToken()
    if (refreshed) {
      return apiPut(path, payload)
    }
    localStorage.removeItem('crm-access-token')
    localStorage.removeItem('crm-refresh-token')
    localStorage.removeItem('crm-user-role')
    window.location.href = '/login'
    throw new Error('Unauthorized')
  }

  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`)
  }

  return (await response.json()) as T
}

export async function apiDelete(path: string): Promise<void> {
  const response = await fetch(`${API_BASE}${path}`, {
    method: 'DELETE',
    headers: {
      ...authHeaders(),
    },
  })

  if (response.status === 401) {
    const refreshed = await refreshAccessToken()
    if (refreshed) {
      return apiDelete(path)
    }
    localStorage.removeItem('crm-access-token')
    localStorage.removeItem('crm-refresh-token')
    localStorage.removeItem('crm-user-role')
    window.location.href = '/login'
    throw new Error('Unauthorized')
  }

  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`)
  }
}

export async function apiMultipartPost<T>(path: string, formData: FormData): Promise<T> {
  const token = localStorage.getItem('crm-access-token')
  const response = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body: formData,
  })

  if (response.status === 401) {
    const refreshed = await refreshAccessToken()
    if (refreshed) {
      return apiMultipartPost(path, formData)
    }
    localStorage.removeItem('crm-access-token')
    localStorage.removeItem('crm-refresh-token')
    localStorage.removeItem('crm-user-role')
    window.location.href = '/login'
    throw new Error('Unauthorized')
  }

  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`)
  }

  return (await response.json()) as T
}
