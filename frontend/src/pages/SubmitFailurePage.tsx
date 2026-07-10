import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import apiClient from '../api/client'

interface Project {
  id: string
  name: string
}

export default function SubmitFailurePage() {
  const navigate = useNavigate()
  const [projects, setProjects] = useState<Project[]>([])
  const [isLoading, setIsLoading] = useState(true)

  // Form State
  const [projectId, setProjectId] = useState('')
  const [category, setCategory] = useState('architecture')
  const [techStackInput, setTechStackInput] = useState('')
  const [title, setTitle] = useState('')
  const [problem, setProblem] = useState('')
  const [rootCause, setRootCause] = useState('')
  const [solution, setSolution] = useState('')
  const [lessonLearned, setLessonLearned] = useState('')
  const [severity, setSeverity] = useState('medium')
  const [logs, setLogs] = useState('')
  const [githubUrl, setGithubUrl] = useState('')
  const [detectTime, setDetectTime] = useState('')
  const [resolveTime, setResolveTime] = useState('')
  const [visibility, setVisibility] = useState('public')
  const [status, setStatus] = useState('published')

  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const { data } = await apiClient.get('/projects')
        setProjects(data)
      } catch (err) {
        console.error('Failed to load projects:', err)
      } finally {
        setIsLoading(false)
      }
    }
    fetchProjects()
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setIsSubmitting(true)

    try {
      const tech_stack = techStackInput
        .split(',')
        .map((t) => t.trim())
        .filter((t) => t.length > 0)

      const payload = {
        project_id: projectId || null,
        category,
        tech_stack,
        title,
        problem,
        root_cause: rootCause,
        solution,
        lesson_learned: lessonLearned,
        severity,
        logs: logs || null,
        github_url: githubUrl || null,
        time_to_detect_seconds: detectTime ? parseInt(detectTime) * 60 : null, // convert min to sec
        time_to_resolve_seconds: resolveTime ? parseInt(resolveTime) * 60 : null, // convert min to sec
        visibility,
        status,
      }

      const { data } = await apiClient.post('/failures', payload)

      if (data.status === 'flagged') {
        alert('Your submission was flagged for review due to potentially sensitive credentials in the logs. The secrets have been auto-redacted.')
      }

      navigate(`/failures/${data.id}`)
    } catch (err: any) {
      console.error(err)
      setError(err.response?.data?.detail ?? 'Failed to submit failure report.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="container-page py-12 max-w-3xl animate-slide-up">
      <h1 className="text-3xl font-bold mb-2">Submit Failure Report</h1>
      <p className="text-gray-500 mb-8">Document a software failure so others can learn from it.</p>

      {error && (
        <div className="mb-6 p-4 rounded-lg bg-red-900/30 border border-red-500/50 text-red-200 text-sm">
          ⚠️ {error}
        </div>
      )}

      <div className="card">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid md:grid-cols-2 gap-6">
            {/* Project Lookup */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1.5">
                Associated Project (Optional)
              </label>
              <select
                className="input select-arrow"
                value={projectId}
                onChange={(e) => setProjectId(e.target.value)}
                disabled={isLoading || isSubmitting}
              >
                <option value="">-- None (Standalone Submission) --</option>
                {projects.map((proj) => (
                  <option key={proj.id} value={proj.id}>
                    {proj.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Category */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1.5">
                Failure Category
              </label>
              <select
                className="input select-arrow"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                disabled={isSubmitting}
              >
                <option value="architecture">Architecture</option>
                <option value="security">Security</option>
                <option value="performance">Performance</option>
                <option value="deployment">Deployment</option>
                <option value="scaling">Scaling</option>
                <option value="data">Data</option>
                <option value="other">Other</option>
              </select>
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            {/* Severity */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1.5">
                Severity Level
              </label>
              <select
                className="input select-arrow"
                value={severity}
                onChange={(e) => setSeverity(e.target.value)}
                disabled={isSubmitting}
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </select>
            </div>

            {/* Visibility */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1.5">
                Visibility
              </label>
              <select
                className="input select-arrow"
                value={visibility}
                onChange={(e) => setVisibility(e.target.value)}
                disabled={isSubmitting}
              >
                <option value="public">Public</option>
                <option value="org">Organization Only</option>
                <option value="private">Private (Only Me)</option>
              </select>
            </div>
          </div>

          {/* Title */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1.5">
              Failure Title
            </label>
            <input
              type="text"
              required
              className="input"
              placeholder="e.g. Memory leak due to unclosed database connections"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              disabled={isSubmitting}
            />
          </div>

          {/* Tech Stack */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1.5">
              Tech Stack Used (comma-separated list)
            </label>
            <input
              type="text"
              required
              className="input"
              placeholder="e.g. node.js, redis, express, docker"
              value={techStackInput}
              onChange={(e) => setTechStackInput(e.target.value)}
              disabled={isSubmitting}
            />
          </div>

          {/* Problem */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1.5">
              1. What was the problem? (Symptoms & Impact)
            </label>
            <textarea
              required
              className="input min-h-[120px]"
              placeholder="Describe what went wrong, what services were down, error rates, user impact, etc."
              value={problem}
              onChange={(e) => setProblem(e.target.value)}
              disabled={isSubmitting}
            />
          </div>

          {/* Root Cause */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1.5">
              2. What was the root cause?
            </label>
            <textarea
              required
              className="input min-h-[120px]"
              placeholder="Explain the underlying technical trigger. E.g. Missing pool close in hook, wrong index in DB, etc."
              value={rootCause}
              onChange={(e) => setRootCause(e.target.value)}
              disabled={isSubmitting}
            />
          </div>

          {/* Solution */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1.5">
              3. How was it resolved? (Solution)
            </label>
            <textarea
              required
              className="input min-h-[120px]"
              placeholder="Detail the steps taken to fix the issue temporarily and permanently."
              value={solution}
              onChange={(e) => setSolution(e.target.value)}
              disabled={isSubmitting}
            />
          </div>

          {/* Lesson Learned */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1.5">
              4. What is the key lesson learned?
            </label>
            <textarea
              required
              className="input min-h-[100px]"
              placeholder="What should engineers do differently next time? How can this be prevented automatically?"
              value={lessonLearned}
              onChange={(e) => setLessonLearned(e.target.value)}
              disabled={isSubmitting}
            />
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            {/* Time to Detect */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1.5">
                Time to Detect (minutes - optional)
              </label>
              <input
                type="number"
                min="0"
                className="input"
                placeholder="e.g. 15"
                value={detectTime}
                onChange={(e) => setDetectTime(e.target.value)}
                disabled={isSubmitting}
              />
            </div>

            {/* Time to Resolve */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1.5">
                Time to Resolve (minutes - optional)
              </label>
              <input
                type="number"
                min="0"
                className="input"
                placeholder="e.g. 120"
                value={resolveTime}
                onChange={(e) => setResolveTime(e.target.value)}
                disabled={isSubmitting}
              />
            </div>
          </div>

          {/* GitHub URL */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1.5">
              GitHub Postmortem/Issue URL (Optional)
            </label>
            <input
              type="url"
              className="input"
              placeholder="https://github.com/org/repo/issues/123"
              value={githubUrl}
              onChange={(e) => setGithubUrl(e.target.value)}
              disabled={isSubmitting}
            />
          </div>

          {/* Logs */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1.5">
              Raw Logs / Stack Trace (Optional - will be scanned and redacted)
            </label>
            <textarea
              className="input min-h-[150px] font-mono text-xs"
              placeholder="Paste stack traces or log outputs here. Credentials will be auto-redacted."
              value={logs}
              onChange={(e) => setLogs(e.target.value)}
              disabled={isSubmitting}
            />
          </div>

          {/* Status buttons */}
          <div className="flex gap-4">
            <button
              type="button"
              onClick={() => {
                setStatus('draft')
                setTimeout(() => {
                  const form = document.querySelector('form')
                  form?.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }))
                }, 50)
              }}
              className="btn-secondary flex-1 py-3"
              disabled={isSubmitting}
            >
              Save as Draft
            </button>
            <button
              type="submit"
              onClick={() => setStatus('published')}
              className="btn-primary flex-1 py-3 glow-brand"
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Submitting...' : 'Publish Report'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
