/**
 * Axios API client — pre-configured for FailureAI backend.
 *
 * Features:
 * - Base URL from VITE_API_URL env var
 * - Automatic Bearer token injection
 * - 401 response handling (clears token)
 */
import axios, { type AxiosInstance, type InternalAxiosRequestConfig } from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL ?? '/api/v1'

export const apiClient: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15_000,
})

// ── Request interceptor: inject auth token ────────────────────────────────
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('access_token')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error),
)

// ── Response interceptor: handle 401 ─────────────────────────────────────
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear stale tokens — Week 2 will add refresh token logic here
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      // Redirect to login (avoid circular import — use window.location)
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  },
)

// ── Health check helper ───────────────────────────────────────────────────
export async function checkHealth(): Promise<{ status: string; version: string; environment: string }> {
  const { data } = await apiClient.get('/health')
  return data
}

export default apiClient
