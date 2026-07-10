import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import apiClient from '../api/client'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setIsSubmitting(true)

    try {
      const { data } = await apiClient.post('/auth/login', { email, password })
      await login(data.access_token, data.refresh_token)
      navigate('/')
    } catch (err: any) {
      console.error(err)
      setError(
        err.response?.data?.detail ??
        err.response?.data?.error?.message ??
        'Invalid email or password.'
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center p-4">
      <div className="w-full max-w-md animate-slide-up">
        <div className="card glow-brand-lg">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="w-12 h-12 rounded-xl bg-brand-600 flex items-center justify-center text-white font-bold text-xl mx-auto mb-4 glow-brand">
              F
            </div>
            <h1 className="text-2xl font-bold">Welcome back</h1>
            <p className="text-gray-400 text-sm mt-1">Sign in to your FailureAI account</p>
          </div>

          {error && (
            <div className="mb-6 p-4 rounded-lg bg-red-900/30 border border-red-500/50 text-red-200 text-sm">
              ⚠️ {error}
            </div>
          )}

          <form id="login-form" className="space-y-5" onSubmit={handleSubmit}>
            <div>
              <label htmlFor="login-email" className="block text-sm font-medium text-gray-300 mb-1.5">
                Email Address
              </label>
              <input
                id="login-email"
                type="email"
                required
                autoComplete="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="input"
                disabled={isSubmitting}
              />
            </div>

            <div>
              <div className="flex justify-between items-center mb-1.5">
                <label htmlFor="login-password" className="block text-sm font-medium text-gray-300">
                  Password
                </label>
              </div>
              <input
                id="login-password"
                type="password"
                required
                autoComplete="current-password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="input"
                disabled={isSubmitting}
              />
            </div>

            <button
              id="login-submit"
              type="submit"
              className="btn-primary w-full py-3"
              disabled={isSubmitting}
            >
              {isSubmitting ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="w-4 h-4 rounded-full border-2 border-white/30 border-t-white animate-spin" />
                  Signing in...
                </span>
              ) : (
                'Sign In'
              )}
            </button>
          </form>

          <div className="divider" />

          <p className="text-center text-sm text-gray-400">
            Don't have an account?{' '}
            <Link to="/register" className="text-brand-400 hover:text-brand-300 font-semibold transition-colors">
              Sign up
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
