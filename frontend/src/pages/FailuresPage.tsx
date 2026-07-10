export default function FailuresPage() {
  return (
    <div className="container-page py-12 animate-slide-up">
      {/* Page header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-bold">Failure Reports</h1>
          <p className="text-gray-500 mt-1">Browse and learn from documented software failures</p>
        </div>
        <button id="submit-failure-btn" className="btn-primary" disabled>
          + Submit Failure
        </button>
      </div>

      {/* Search bar placeholder */}
      <div className="mb-8">
        <input
          id="failures-search"
          type="search"
          placeholder="🔍  Search failures... (semantic search in Week 3)"
          className="input text-base py-3"
          disabled
        />
      </div>

      {/* Filter chips placeholder */}
      <div className="flex flex-wrap gap-2 mb-8">
        {['All', 'Architecture', 'Security', 'Performance', 'Deployment', 'Scaling', 'Data'].map((cat) => (
          <button
            key={cat}
            id={`filter-${cat.toLowerCase()}`}
            className={`px-4 py-1.5 rounded-full text-sm font-medium border transition-all duration-150 ${
              cat === 'All'
                ? 'bg-brand-600 border-brand-600 text-white'
                : 'bg-white/5 border-white/10 text-gray-400 hover:text-gray-200 hover:border-white/20'
            }`}
            disabled
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Empty state */}
      <div className="card text-center py-20">
        <div className="text-6xl mb-4">📋</div>
        <h2 className="text-xl font-semibold mb-2">No failures yet</h2>
        <p className="text-gray-500 max-w-sm mx-auto mb-6">
          The failure knowledge base is empty. CRUD endpoints and submission form
          are coming in <strong className="text-brand-400">Week 2</strong>.
        </p>
        <div className="badge-brand mx-auto">🚧 Week 2 — CRUD</div>
      </div>
    </div>
  )
}
