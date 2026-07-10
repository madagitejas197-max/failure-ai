import { Link } from 'react-router-dom'

export default function RegisterPage() {
  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center p-4">
      <div className="w-full max-w-md animate-slide-up">
        <div className="card">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="w-12 h-12 rounded-xl bg-brand-600 flex items-center justify-center text-white font-bold text-xl mx-auto mb-4 glow-brand">
              F
            </div>
            <h1 className="text-2xl font-bold">Create your account</h1>
            <p className="text-gray-500 text-sm mt-1">Join the failure knowledge base</p>
          </div>

          {/* Form placeholder — wired up in Week 2 */}
          <form id="register-form" className="space-y-5" onSubmit={(e) => e.preventDefault()}>
            <div>
              <label htmlFor="register-name" className="block text-sm font-medium text-gray-300 mb-1.5">
                Display Name
              </label>
              <input
                id="register-name"
                type="text"
                autoComplete="name"
                placeholder="Jane Smith"
                className="input"
                disabled
              />
            </div>

            <div>
              <label htmlFor="register-email" className="block text-sm font-medium text-gray-300 mb-1.5">
                Email
              </label>
              <input
                id="register-email"
                type="email"
                autoComplete="email"
                placeholder="you@example.com"
                className="input"
                disabled
              />
            </div>

            <div>
              <label htmlFor="register-password" className="block text-sm font-medium text-gray-300 mb-1.5">
                Password
              </label>
              <input
                id="register-password"
                type="password"
                autoComplete="new-password"
                placeholder="••••••••"
                className="input"
                disabled
              />
            </div>

            <button
              id="register-submit"
              type="submit"
              className="btn-primary w-full"
              disabled
            >
              🚧 Registration coming in Week 2
            </button>
          </form>

          <div className="divider" />

          <p className="text-center text-sm text-gray-500">
            Already have an account?{' '}
            <Link to="/login" className="text-brand-400 hover:text-brand-300 font-medium transition-colors">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
