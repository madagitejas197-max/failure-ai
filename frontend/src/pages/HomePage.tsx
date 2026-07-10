import { Link } from 'react-router-dom'

const stats = [
  { label: 'Failures Documented', value: '0' },
  { label: 'Engineers Helped',    value: '0' },
  { label: 'Categories',          value: '7' },
]

const categories = [
  { name: 'Architecture',  icon: '🏗️', color: 'from-blue-600/20 to-blue-800/10',  border: 'border-blue-700/30' },
  { name: 'Security',      icon: '🔐', color: 'from-red-600/20 to-red-800/10',    border: 'border-red-700/30' },
  { name: 'Performance',   icon: '⚡', color: 'from-yellow-600/20 to-yellow-800/10', border: 'border-yellow-700/30' },
  { name: 'Deployment',    icon: '🚀', color: 'from-green-600/20 to-green-800/10', border: 'border-green-700/30' },
  { name: 'Scaling',       icon: '📈', color: 'from-purple-600/20 to-purple-800/10', border: 'border-purple-700/30' },
  { name: 'Data',          icon: '🗄️', color: 'from-orange-600/20 to-orange-800/10', border: 'border-orange-700/30' },
]

export default function HomePage() {
  return (
    <div className="animate-slide-up">
      {/* ── Hero ───────────────────────────────────────────────────── */}
      <section className="relative overflow-hidden">
        {/* Background glow */}
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[400px] bg-brand-600/10 blur-[120px] rounded-full" />
        </div>

        <div className="container-page pt-24 pb-20 text-center relative">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-brand-900/50 border border-brand-700/50 text-brand-300 text-sm font-medium mb-6">
            <span className="w-1.5 h-1.5 rounded-full bg-brand-400 animate-pulse-slow" />
            AI-Powered Software Failure Intelligence
          </div>

          {/* Headline */}
          <h1 className="text-5xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight text-balance mb-6 leading-[1.1]">
            Learn from every{' '}
            <span className="gradient-text">software failure</span>
            <br />before it hits you.
          </h1>

          <p className="text-xl text-gray-400 max-w-2xl mx-auto mb-10 leading-relaxed">
            Search thousands of real-world postmortems, get AI-powered prevention
            checklists, and predict risks before you ship.
          </p>

          {/* CTA buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/failures" id="cta-browse-failures" className="btn-primary text-base px-8 py-3 glow-brand">
              Browse Failures
            </Link>
            <Link to="/register" id="cta-submit-failure" className="btn-secondary text-base px-8 py-3">
              Submit a Failure →
            </Link>
          </div>
        </div>
      </section>

      {/* ── Stats ───────────────────────────────────────────────────── */}
      <section className="border-y border-white/10 py-10">
        <div className="container-page grid grid-cols-3 gap-6 text-center">
          {stats.map((s) => (
            <div key={s.label}>
              <div className="text-3xl font-extrabold gradient-text">{s.value}</div>
              <div className="text-sm text-gray-500 mt-1">{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* ── Categories ──────────────────────────────────────────────── */}
      <section className="container-page py-20">
        <h2 className="text-2xl font-bold text-center mb-2">Browse by Category</h2>
        <p className="text-gray-500 text-center mb-10">Every type of failure, documented and searchable.</p>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
          {categories.map((cat) => (
            <button
              key={cat.name}
              id={`category-${cat.name.toLowerCase()}`}
              className={`card-hover flex flex-col items-center gap-3 py-6 bg-gradient-to-br ${cat.color} ${cat.border} cursor-pointer`}
            >
              <span className="text-3xl">{cat.icon}</span>
              <span className="text-sm font-semibold text-gray-200">{cat.name}</span>
            </button>
          ))}
        </div>
      </section>

      {/* ── Features ────────────────────────────────────────────────── */}
      <section className="container-page pb-24">
        <div className="grid md:grid-cols-3 gap-6">
          {[
            {
              icon: '🔍',
              title: 'Semantic Search',
              desc: 'Find related failures even when the exact wording differs. Powered by vector embeddings.',
            },
            {
              icon: '🤖',
              title: 'AI Assistant',
              desc: 'Ask about failure patterns, get prevention checklists, and explore architecture suggestions.',
            },
            {
              icon: '📊',
              title: 'Risk Prediction',
              desc: 'Input your tech stack and get a risk score with ranked failure categories to watch for.',
            },
          ].map((f) => (
            <div key={f.title} className="card-hover">
              <div className="text-3xl mb-4">{f.icon}</div>
              <h3 className="text-lg font-bold mb-2">{f.title}</h3>
              <p className="text-gray-400 text-sm leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}
