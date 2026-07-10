import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import apiClient from '../api/client'
import { useAuth } from '../context/AuthContext'

interface Tag {
  id: string
  name: string
}

interface Failure {
  id: string
  category: string
  tech_stack: string[]
  title: string
  problem: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  upvote_count: number
  created_at: string
  tags: Tag[]
}

const categories = ['All', 'Architecture', 'Security', 'Performance', 'Deployment', 'Scaling', 'Data']

export default function FailuresPage() {
  const { isAuthenticated } = useAuth()
  const [failures, setFailures] = useState<Failure[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [activeCategory, setActiveCategory] = useState('All')
  const [searchQuery, setSearchQuery] = useState('')

  const fetchFailures = async () => {
    try {
      setIsLoading(true)
      const params: any = {}
      if (activeCategory !== 'All') {
        params.category = activeCategory.toLowerCase()
      }
      
      const { data } = await apiClient.get('/failures', { params })
      setFailures(data)
    } catch (err) {
      console.error('Failed to load failures:', err)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchFailures()
  }, [activeCategory])

  // Client-side search filtering (Week 2, semantic search is Week 3)
  const filteredFailures = failures.filter((f) => {
    const query = searchQuery.toLowerCase()
    return (
      f.title.toLowerCase().includes(query) ||
      f.problem.toLowerCase().includes(query) ||
      f.tech_stack.some((tech) => tech.toLowerCase().includes(query))
    )
  })

  const getSeverityBadgeClass = (sev: string) => {
    switch (sev) {
      case 'critical':
        return 'badge-red'
      case 'high':
        return 'badge-yellow'
      case 'medium':
        return 'badge-brand'
      default:
        return 'badge-green'
    }
  }

  return (
    <div className="container-page py-12 animate-slide-up">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-bold">Failure Reports</h1>
          <p className="text-gray-500 mt-1">Browse and learn from documented software failures</p>
        </div>
        {isAuthenticated ? (
          <Link to="/failures/submit" id="submit-failure-btn" className="btn-primary">
            + Submit Failure
          </Link>
        ) : (
          <Link to="/login" id="submit-failure-btn" className="btn-primary">
            Sign In to Submit
          </Link>
        )}
      </div>

      {/* Search Input */}
      <div className="mb-8">
        <input
          id="failures-search"
          type="search"
          placeholder="🔍  Search title, description, or tech stack..."
          className="input text-base py-3"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      {/* Category filter chips */}
      <div className="flex flex-wrap gap-2 mb-8">
        {categories.map((cat) => (
          <button
            key={cat}
            id={`filter-${cat.toLowerCase()}`}
            onClick={() => setActiveCategory(cat)}
            className={`px-5 py-2 rounded-full text-sm font-semibold border transition-all duration-150 cursor-pointer ${
              activeCategory === cat
                ? 'bg-brand-600 border-brand-600 text-white shadow-lg glow-brand'
                : 'bg-white/5 border-white/10 text-gray-400 hover:text-gray-200 hover:border-white/20'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* List content */}
      {isLoading ? (
        <div className="text-center py-20 text-gray-500">Loading failures...</div>
      ) : filteredFailures.length === 0 ? (
        <div className="card text-center py-20 text-gray-500">
          <div className="text-6xl mb-4">📋</div>
          <h2 className="text-xl font-semibold mb-2">No failure reports found</h2>
          <p className="text-gray-600 max-w-sm mx-auto">
            {searchQuery ? 'Try adjusting your search query.' : 'Be the first to submit a failure in this category!'}
          </p>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 gap-6">
          {filteredFailures.map((failure) => (
            <Link
              key={failure.id}
              to={`/failures/${failure.id}`}
              className="card-hover block border border-white/10 p-6 relative group"
            >
              <div className="flex justify-between items-start gap-4 mb-3">
                <span className="text-xs text-gray-500">
                  {new Date(failure.created_at).toLocaleDateString()}
                </span>
                <span className={`badge ${getSeverityBadgeClass(failure.severity)} capitalize`}>
                  {failure.severity}
                </span>
              </div>
              <h2 className="text-xl font-bold text-gray-100 group-hover:text-brand-300 transition-colors mb-2 line-clamp-1">
                {failure.title}
              </h2>
              <p className="text-gray-400 text-sm mb-4 line-clamp-2 leading-relaxed">
                {failure.problem}
              </p>
              
              <div className="flex justify-between items-center mt-auto">
                {/* Tech tags */}
                <div className="flex flex-wrap gap-1.5 max-w-[80%]">
                  {failure.tags.slice(0, 3).map((tag) => (
                    <span key={tag.id} className="badge badge-brand text-[10px] py-0.5 px-2">
                      {tag.name}
                    </span>
                  ))}
                  {failure.tags.length > 3 && (
                    <span className="text-xs text-gray-600 font-medium">+{failure.tags.length - 3} more</span>
                  )}
                </div>

                {/* Upvote indicator */}
                <div className="flex items-center gap-1 text-xs text-gray-400 bg-white/5 border border-white/10 rounded-lg px-2.5 py-1">
                  <span>▲</span>
                  <span className="font-bold text-gray-200">{failure.upvote_count}</span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
