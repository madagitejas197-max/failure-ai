import { Link } from 'react-router-dom'

export default function LoginPage() {
  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center p-4">
      <div className="w-full max-w-md animate-slide-up">
        <div className="card">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="w-12 h-12 rounded-xl bg-brand-600 flex items-center justify-center text-white font-bold text-xl mx-auto mb-4 glow-brand">
              F
            </div>
            <h1 className="text-2xl font-bold">Welcome back</h1>
            <p className="text-gray-500 text-sm mt-1">Sign in to your FailureAI account</p>
          </div>

          {/* Form placeholder — wired up in Week 2 */}
          <form id="login-form" className="space-y-5" onSubmit={(e) => e.preventDefault()}>
            <div>
              <label htmlFor="login-email" className="block text-sm font-medium text-gray-300 mb-1.5">
                Email
              </label>
              <input
                id="login-email"
                type="email"
                autoComplete="email"
                placeholder="you@example.com"
                className="input"
                disabled
              />
            </div>

            <div>
              <label htmlFor="login-password" className="block text-sm font-medium text-gray-300 mb-1.5">
                Password
              </label>
              <input
                id="login-password"
                type="password"
                autoComplete="current-password"
                placeholder="••••••••"
                className="input"
                disabled
              />
            </div>

            <button
              id="login-submit"
              type="submit"
              className="btn-primary w-full"
              disabled
            >
              🚧 Auth coming in Week 2
            </button>
          </form>

          <div className="divider" />

          <p className="text-center text-sm text-gray-500">
            Don't have an account?{' '}
            <Link to="/register" className="text-brand-400 hover:text-brand-300 font-medium transition-colors">
              Sign up
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
