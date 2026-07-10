import { Outlet, NavLink, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Layout() {
  const { user, isAuthenticated, logout } = useAuth()

  const navLinks = [
    { to: '/',         label: 'Home' },
    { to: '/failures', label: 'Failures' },
    ...(isAuthenticated ? [{ to: '/projects', label: 'Projects' }] : []),
  ]

  return (
    <div className="min-h-screen flex flex-col">
      {/* ── Navbar ──────────────────────────────────────────────────── */}
      <header className="sticky top-0 z-50 glass border-b border-white/10">
        <nav className="container-page flex items-center justify-between h-16">
          {/* Logo */}
          <Link
            to="/"
            className="flex items-center gap-2.5 group"
            aria-label="FailureAI Home"
          >
            <span className="w-8 h-8 rounded-lg bg-brand-600 flex items-center justify-center text-white font-bold text-sm shadow-lg glow-brand transition-all duration-200 group-hover:scale-110">
              F
            </span>
            <span className="font-bold text-lg tracking-tight">
              <span className="gradient-text">Failure</span>
              <span className="text-gray-200">AI</span>
            </span>
          </Link>

          {/* Nav links */}
          <ul className="hidden md:flex items-center gap-1" role="navigation">
            {navLinks.map(({ to, label }) => (
              <li key={to}>
                <NavLink
                  to={to}
                  end={to === '/'}
                  className={({ isActive }) =>
                    `btn-ghost text-sm ${isActive ? 'text-brand-400 bg-brand-900/30' : ''}`
                  }
                >
                  {label}
                </NavLink>
              </li>
            ))}
          </ul>

          {/* Auth states */}
          <div className="flex items-center gap-3">
            {isAuthenticated && user ? (
              <div className="flex items-center gap-4">
                <Link
                  to="/profile"
                  className="flex items-center gap-2.5 hover:text-brand-300 transition-colors group"
                >
                  <div className="w-8 h-8 rounded-lg bg-brand-700 flex items-center justify-center text-white text-sm font-bold border border-white/10 overflow-hidden">
                    {user.avatar_url ? (
                      <img src={user.avatar_url} alt={user.display_name} className="w-full h-full object-cover" />
                    ) : (
                      user.display_name[0]?.toUpperCase()
                    )}
                  </div>
                  <span className="text-sm font-semibold text-gray-300 group-hover:text-brand-300">
                    {user.display_name}
                  </span>
                </Link>
                <button
                  onClick={logout}
                  className="btn-ghost text-sm text-gray-400 hover:text-red-400 transition-colors"
                >
                  Sign Out
                </button>
              </div>
            ) : (
              <>
                <Link to="/login" className="btn-ghost text-sm">
                  Sign in
                </Link>
                <Link to="/register" className="btn-primary text-sm">
                  Get Started
                </Link>
              </>
            )}
          </div>
        </nav>
      </header>

      {/* ── Page content ─────────────────────────────────────────────── */}
      <main className="flex-1 animate-in">
        <Outlet />
      </main>

      {/* ── Footer ──────────────────────────────────────────────────── */}
      <footer className="border-t border-white/10 py-8 mt-16">
        <div className="container-page flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-gray-500">
          <p>
            © {new Date().getFullYear()}{' '}
            <span className="gradient-text font-semibold">FailureAI</span>
            {' '}— Learn from failure, ship better software.
          </p>
          <div className="flex gap-6">
            <a href="#" className="hover:text-gray-300 transition-colors">Privacy</a>
            <a href="#" className="hover:text-gray-300 transition-colors">Terms</a>
            <a href="https://github.com" target="_blank" rel="noopener noreferrer" className="hover:text-gray-300 transition-colors">
              GitHub
            </a>
          </div>
        </div>
      </footer>
    </div>
  )
}
