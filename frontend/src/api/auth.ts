export interface LoginPayload {
  username: string
  password: string
}

export interface LoginResult {
  access: string
  refresh: string
  user: {
    id: number
    username: string
    role: 'admin' | 'customer'
    customer_id: number | null
    display_name: string
  }
}

export interface CurrentUser {
  id: number
  username: string
  role: 'admin' | 'customer'
  customer_id: number | null
  display_name: string
  email?: string
}

const defaultBase =
  typeof window !== 'undefined' ? `${window.location.protocol}//${window.location.hostname}:8000/api` : 'http://127.0.0.1:8000/api'
const API_BASE = import.meta.env.VITE_API_BASE || defaultBase

function authHeaders(): Record<string, string> {
  const token = localStorage.getItem('crm-access-token')
  if (!token) return {}
  return { Authorization: `Bearer ${token}` }
}

export async function login(payload: LoginPayload): Promise<LoginResult> {
  const response = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  })

  const data = await response.json()

  if (!response.ok) {
    throw new Error(data?.detail || 'Login failed')
  }

  return data as LoginResult
}

export async function fetchCurrentUser(): Promise<CurrentUser> {
  const response = await fetch(`${API_BASE}/auth/me`, {
    headers: authHeaders(),
  })
  if (!response.ok) {
    throw new Error(`Failed to fetch user: ${response.status}`)
  }
  return (await response.json()) as CurrentUser
}
