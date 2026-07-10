import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import apiClient from '../api/client'

export default function RegisterPage() {
  const [displayName, setDisplayName] = useState('')
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
      // 1. Register User
      await apiClient.post('/auth/register', {
        display_name: displayName,
        email,
        password,
      })

      // 2. Automatically log them in after registration
      const { data } = await apiClient.post('/auth/login', { email, password })
      await login(data.access_token, data.refresh_token)
      navigate('/')
    } catch (err: any) {
      console.error(err)
      setError(
        err.response?.data?.detail ??
        err.response?.data?.error?.message ??
        'Failed to create account. Please check inputs.'
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
            <h1 className="text-2xl font-bold">Create your account</h1>
            <p className="text-gray-400 text-sm mt-1">Join the failure knowledge base</p>
          </div>

          {error && (
            <div className="mb-6 p-4 rounded-lg bg-red-900/30 border border-red-500/50 text-red-200 text-sm">
              ⚠️ {error}
            </div>
          )}

          <form id="register-form" className="space-y-5" onSubmit={handleSubmit}>
            <div>
              <label htmlFor="register-name" className="block text-sm font-medium text-gray-300 mb-1.5">
                Display Name
              </label>
              <input
                id="register-name"
                type="text"
                required
                placeholder="Jane Smith"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                className="input"
                disabled={isSubmitting}
              />
            </div>

            <div>
              <label htmlFor="register-email" className="block text-sm font-medium text-gray-300 mb-1.5">
                Email Address
              </label>
              <input
                id="register-email"
                type="email"
                required
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="input"
                disabled={isSubmitting}
              />
            </div>

            <div>
              <label htmlFor="register-password" className="block text-sm font-medium text-gray-300 mb-1.5">
                Password
              </label>
              <input
                id="register-password"
                type="password"
                required
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="input"
                disabled={isSubmitting}
              />
            </div>

            <button
              id="register-submit"
              type="submit"
              className="btn-primary w-full py-3"
              disabled={isSubmitting}
            >
              {isSubmitting ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="w-4 h-4 rounded-full border-2 border-white/30 border-t-white animate-spin" />
                  Creating account...
                </span>
              ) : (
                'Create Account'
              )}
            </button>
          </form>

          <div className="divider" />

          <p className="text-center text-sm text-gray-400">
            Already have an account?{' '}
            <Link to="/login" className="text-brand-400 hover:text-brand-300 font-semibold transition-colors">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
