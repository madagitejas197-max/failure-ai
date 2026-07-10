import React, { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import apiClient from '../api/client'

interface User {
  id: string
  display_name: string
  avatar_url: string | null
}

interface Tag {
  id: string
  name: string
  category: string | null
}

interface Failure {
  id: string
  project_id: string | null
  author_id: string
  category: string
  tech_stack: string[]
  title: string
  problem: string
  root_cause: string
  solution: string
  lesson_learned: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  logs_redacted: string | null
  github_url: string | null
  time_to_detect_seconds: number | null
  time_to_resolve_seconds: number | null
  visibility: string
  status: string
  upvote_count: number
  created_at: string
  tags: Tag[]
}

interface Comment {
  id: string
  failure_id: string
  author_id: string
  body: string
  created_at: string
  author: User
}

export default function FailureDetailPage() {
  const { id } = useParams<{ id: string }>()
  const [failure, setFailure] = useState<Failure | null>(null)
  const [comments, setComments] = useState<Comment[]>([])
  const [newComment, setNewComment] = useState('')
  const [isLoading, setIsLoading] = useState(true)
  const [isSubmittingComment, setIsSubmittingComment] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchData = async () => {
    try {
      const [failureRes, commentsRes] = await Promise.all([
        apiClient.get(`/failures/${id}`),
        apiClient.get(`/failures/${id}/comments`),
      ])
      setFailure(failureRes.data)
      setComments(commentsRes.data)
    } catch (err: any) {
      console.error(err)
      setError(err.response?.data?.detail ?? 'Failed to load failure report.')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [id])

  const handleUpvote = async () => {
    if (!failure) return
    try {
      const { data } = await apiClient.post(`/failures/${id}/upvote`)
      setFailure(data)
    } catch (err) {
      console.error('Failed to upvote:', err)
    }
  }

  const handlePostComment = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newComment.trim() || !failure) return
    setIsSubmittingComment(true)

    try {
      const { data } = await apiClient.post(`/failures/${id}/comments`, {
        body: newComment,
      })
      setComments([...comments, data])
      setNewComment('')
    } catch (err) {
      console.error('Failed to post comment:', err)
      alert('Failed to post comment.')
    } finally {
      setIsSubmittingComment(false)
    }
  }

  if (isLoading) {
    return <div className="container-page py-20 text-center text-gray-500">Loading details...</div>
  }

  if (error || !failure) {
    return (
      <div className="container-page py-20 text-center">
        <h1 className="text-2xl font-bold text-red-400">⚠️ Error</h1>
        <p className="text-gray-500 mt-2">{error ?? 'Failure report not found.'}</p>
        <Link to="/failures" className="btn-primary mt-6 inline-block">
          Back to list
        </Link>
      </div>
    )
  }

  // Helpers for displaying severity badges
  const getSeverityClass = (sev: string) => {
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
    <div className="container-page py-12 animate-slide-up max-w-4xl">
      {/* Back button */}
      <Link to="/failures" className="text-sm text-brand-400 hover:text-brand-300 mb-6 inline-block">
        ← Back to failures list
      </Link>

      {/* ── Title block ──────────────────────────────────────────────── */}
      <div className="flex flex-col sm:flex-row justify-between items-start gap-4 mb-8">
        <div>
          <div className="flex flex-wrap items-center gap-2 mb-3">
            <span className={`badge ${getSeverityClass(failure.severity)} capitalize`}>
              {failure.severity} severity
            </span>
            <span className="badge badge-brand capitalize">{failure.category}</span>
            {failure.status === 'flagged' && (
              <span className="badge badge-yellow">⚠️ Log Redacted</span>
            )}
            {failure.status === 'draft' && (
              <span className="badge badge-brand bg-gray-800 text-gray-400 border-gray-700">Draft</span>
            )}
          </div>
          <h1 className="text-3xl font-extrabold text-gray-100">{failure.title}</h1>
          <p className="text-sm text-gray-500 mt-2">
            Published on {new Date(failure.created_at).toLocaleDateString()}
          </p>
        </div>

        {/* Upvote button */}
        <button
          onClick={handleUpvote}
          className="btn-secondary flex items-center gap-2.5 px-6 py-3 cursor-pointer"
        >
          <span>▲</span>
          <span className="font-bold">{failure.upvote_count}</span>
          <span className="text-xs text-gray-400">Upvotes</span>
        </button>
      </div>

      <div className="divider" />

      {/* ── Core postmortem contents ─────────────────────────────────── */}
      <div className="space-y-8">
        {/* Tech Stack */}
        <div>
          <h3 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Tech Stack</h3>
          <div className="flex flex-wrap gap-2">
            {failure.tags.map((tag) => (
              <span key={tag.id} className="badge-brand">
                {tag.name}
              </span>
            ))}
          </div>
        </div>

        {/* Problem */}
        <div className="card bg-surface-50/50">
          <h3 className="text-lg font-bold text-gray-200 mb-3">1. Symptoms & Impact</h3>
          <p className="text-gray-300 leading-relaxed whitespace-pre-line">{failure.problem}</p>
        </div>

        {/* Root Cause */}
        <div className="card bg-surface-50/50">
          <h3 className="text-lg font-bold text-gray-200 mb-3">2. Root Cause</h3>
          <p className="text-gray-300 leading-relaxed whitespace-pre-line">{failure.root_cause}</p>
        </div>

        {/* Solution */}
        <div className="card bg-surface-50/50">
          <h3 className="text-lg font-bold text-gray-200 mb-3">3. Resolution</h3>
          <p className="text-gray-300 leading-relaxed whitespace-pre-line">{failure.solution}</p>
        </div>

        {/* Lesson Learned */}
        <div className="card border-brand-500/20 bg-brand-950/5">
          <h3 className="text-lg font-bold text-brand-300 mb-3">4. Lesson Learned</h3>
          <p className="text-gray-300 leading-relaxed whitespace-pre-line">{failure.lesson_learned}</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 border-y border-white/10 py-6">
          <div>
            <h4 className="text-xs text-gray-500 uppercase font-bold mb-1">Time to Detect</h4>
            <span className="text-gray-200 font-semibold">
              {failure.time_to_detect_seconds
                ? `${Math.round(failure.time_to_detect_seconds / 60)} minutes`
                : 'N/A'}
            </span>
          </div>
          <div>
            <h4 className="text-xs text-gray-500 uppercase font-bold mb-1">Time to Resolve</h4>
            <span className="text-gray-200 font-semibold">
              {failure.time_to_resolve_seconds
                ? `${Math.round(failure.time_to_resolve_seconds / 60)} minutes`
                : 'N/A'}
            </span>
          </div>
          <div className="col-span-2 sm:col-span-1">
            <h4 className="text-xs text-gray-500 uppercase font-bold mb-1">External Resource</h4>
            {failure.github_url ? (
              <a
                href={failure.github_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-brand-400 hover:underline"
              >
                GitHub Link
              </a>
            ) : (
              <span className="text-gray-600">None</span>
            )}
          </div>
        </div>

        {/* Logs */}
        {failure.logs_redacted && (
          <div>
            <h3 className="text-sm font-bold text-gray-400 mb-2">Logs / Stack Trace</h3>
            <pre className="p-5 rounded-lg bg-black/60 border border-white/10 text-xs font-mono text-gray-400 overflow-x-auto whitespace-pre-wrap">
              {failure.logs_redacted}
            </pre>
          </div>
        )}
      </div>

      <div className="divider my-12" />

      {/* ── Comments thread ─────────────────────────────────────────── */}
      <section className="space-y-8">
        <h2 className="text-2xl font-bold text-gray-200">Discussion ({comments.length})</h2>

        {/* Add comment form */}
        <form onSubmit={handlePostComment} className="flex gap-4">
          <input
            type="text"
            required
            className="input flex-1 py-3"
            placeholder="Add to the discussion..."
            value={newComment}
            onChange={(e) => setNewComment(e.target.value)}
            disabled={isSubmittingComment}
          />
          <button type="submit" className="btn-primary px-6" disabled={isSubmittingComment}>
            {isSubmittingComment ? 'Posting...' : 'Comment'}
          </button>
        </form>

        {/* Comment list */}
        <div className="space-y-4">
          {comments.map((comment) => (
            <div key={comment.id} className="card p-5 flex items-start gap-4">
              <div className="w-10 h-10 rounded-xl bg-brand-700/50 flex items-center justify-center text-white font-bold shrink-0 border border-white/10">
                {comment.author.avatar_url ? (
                  <img
                    src={comment.author.avatar_url}
                    alt={comment.author.display_name}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  comment.author.display_name[0]?.toUpperCase()
                )}
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1.5">
                  <span className="font-bold text-sm text-gray-200">
                    {comment.author.display_name}
                  </span>
                  <span className="text-xs text-gray-500">
                    {new Date(comment.created_at).toLocaleDateString()}
                  </span>
                </div>
                <p className="text-sm text-gray-300 leading-relaxed whitespace-pre-line">
                  {comment.body}
                </p>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}
