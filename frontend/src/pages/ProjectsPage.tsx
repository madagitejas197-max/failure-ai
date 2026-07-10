import React, { useState, useEffect } from 'react'
import apiClient from '../api/client'
import { useAuth } from '../context/AuthContext'

interface Project {
  id: string
  name: string
  description: string | null
  tech_stack: string[]
  visibility: 'public' | 'org' | 'private'
  owner_id: string
  created_at: string
}

export default function ProjectsPage() {
  const { user } = useAuth()
  const [projects, setProjects] = useState<Project[]>([])
  const [selectedProject, setSelectedProject] = useState<Project | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [showCreateForm, setShowCreateForm] = useState(false)

  // Form State
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [techStackInput, setTechStackInput] = useState('')
  const [visibility, setVisibility] = useState<'public' | 'org' | 'private'>('public')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchProjects = async () => {
    try {
      const { data } = await apiClient.get('/projects')
      setProjects(data)
    } catch (err) {
      console.error('Failed to fetch projects:', err)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchProjects()
  }, [])

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setIsSubmitting(true)

    try {
      const tech_stack = techStackInput
        .split(',')
        .map((t) => t.trim())
        .filter((t) => t.length > 0)

      const { data } = await apiClient.post('/projects', {
        name,
        description: description || null,
        tech_stack,
        visibility,
      })

      setProjects([data, ...projects])
      setSelectedProject(data)
      setShowCreateForm(false)
      // Reset form
      setName('')
      setDescription('')
      setTechStackInput('')
      setVisibility('public')
    } catch (err: any) {
      console.error(err)
      setError(err.response?.data?.detail ?? 'Failed to create project.')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleDeleteProject = async (id: string) => {
    if (!window.confirm('Are you sure you want to delete this project? This will delete all associated failures.')) {
      return
    }

    try {
      await apiClient.delete(`/projects/${id}`)
      setProjects(projects.filter((p) => p.id !== id))
      if (selectedProject?.id === id) {
        setSelectedProject(null)
      }
    } catch (err) {
      console.error('Failed to delete project:', err)
      alert('Failed to delete project.')
    }
  }

  return (
    <div className="container-page py-12 animate-slide-up">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold">Projects</h1>
          <p className="text-gray-500 mt-1">Manage tech stacks and link failure reports</p>
        </div>
        <button
          onClick={() => {
            setShowCreateForm(!showCreateForm)
            setSelectedProject(null)
          }}
          className="btn-primary"
        >
          {showCreateForm ? 'View Projects' : '+ New Project'}
        </button>
      </div>

      {showCreateForm ? (
        // ── Create Project Form ───────────────────────────────────────────
        <div className="card max-w-xl mx-auto">
          <h2 className="text-xl font-bold mb-6">Create New Project</h2>
          {error && (
            <div className="mb-6 p-4 rounded-lg bg-red-900/30 border border-red-500/50 text-red-200 text-sm">
              ⚠️ {error}
            </div>
          )}
          <form onSubmit={handleCreateProject} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1.5">
                Project Name
              </label>
              <input
                type="text"
                required
                className="input"
                placeholder="e.g. FailureAI"
                value={name}
                onChange={(e) => setName(e.target.value)}
                disabled={isSubmitting}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1.5">
                Description
              </label>
              <textarea
                className="input min-h-[100px]"
                placeholder="Brief project details..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                disabled={isSubmitting}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1.5">
                Tech Stack (comma-separated list)
              </label>
              <input
                type="text"
                className="input"
                placeholder="e.g. React, FastAPI, PostgreSQL, Tailwind"
                value={techStackInput}
                onChange={(e) => setTechStackInput(e.target.value)}
                disabled={isSubmitting}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1.5">
                Visibility
              </label>
              <select
                className="input select-arrow"
                value={visibility}
                onChange={(e) => setVisibility(e.target.value as any)}
                disabled={isSubmitting}
              >
                <option value="public">Public</option>
                <option value="org">Organization</option>
                <option value="private">Private</option>
              </select>
            </div>

            <button type="submit" className="btn-primary w-full py-3" disabled={isSubmitting}>
              {isSubmitting ? 'Creating...' : 'Create Project'}
            </button>
          </form>
        </div>
      ) : (
        // ── Main Layout: List + Detail ─────────────────────────────────────
        <div className="grid md:grid-cols-3 gap-8">
          {/* List Pane */}
          <div className="md:col-span-1 space-y-4">
            <h2 className="text-lg font-bold text-gray-400 mb-2">My Projects</h2>
            {isLoading ? (
              <div className="text-center py-10 text-gray-500">Loading projects...</div>
            ) : projects.length === 0 ? (
              <div className="card text-center py-12 text-gray-500">
                <span className="text-3xl block mb-2">📁</span>
                No projects found.
              </div>
            ) : (
              projects.map((proj) => (
                <button
                  key={proj.id}
                  onClick={() => setSelectedProject(proj)}
                  className={`w-full text-left card-hover p-5 border cursor-pointer block ${
                    selectedProject?.id === proj.id
                      ? 'border-brand-500 bg-brand-950/20'
                      : 'border-white/10'
                  }`}
                >
                  <div className="flex justify-between items-start gap-2">
                    <span className="font-bold text-gray-100">{proj.name}</span>
                    <span className="badge badge-brand capitalize">{proj.visibility}</span>
                  </div>
                  <p className="text-xs text-gray-500 mt-2 line-clamp-2">
                    {proj.description || 'No description provided.'}
                  </p>
                </button>
              ))
            )}
          </div>

          {/* Detail Pane */}
          <div className="md:col-span-2">
            {selectedProject ? (
              <div className="card animate-in glow-brand-lg">
                <div className="flex justify-between items-start gap-4 mb-6">
                  <div>
                    <h2 className="text-2xl font-bold">{selectedProject.name}</h2>
                    <span className="badge badge-brand mt-2 capitalize">
                      {selectedProject.visibility} visibility
                    </span>
                  </div>
                  {selectedProject.owner_id === user?.id && (
                    <button
                      onClick={() => handleDeleteProject(selectedProject.id)}
                      className="btn-ghost text-red-400 hover:text-red-300 hover:bg-red-950/20"
                    >
                      Delete
                    </button>
                  )}
                </div>

                <div className="divider" />

                <div className="space-y-6">
                  <div>
                    <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-2">
                      Description
                    </h3>
                    <p className="text-gray-300 leading-relaxed">
                      {selectedProject.description || 'No description provided.'}
                    </p>
                  </div>

                  <div>
                    <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-2">
                      Tech Stack
                    </h3>
                    <div className="flex flex-wrap gap-2">
                      {selectedProject.tech_stack.length > 0 ? (
                        selectedProject.tech_stack.map((tech) => (
                          <span key={tech} className="badge-brand">
                            {tech}
                          </span>
                        ))
                      ) : (
                        <span className="text-gray-500 text-sm">No tech stack listed.</span>
                      )}
                    </div>
                  </div>

                  <div>
                    <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-2">
                      Created At
                    </h3>
                    <p className="text-gray-400 text-sm">
                      {new Date(selectedProject.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              </div>
            ) : (
              <div className="card h-full flex flex-col items-center justify-center py-20 text-center text-gray-500 border-dashed border-2 border-white/10">
                <span className="text-5xl mb-4">📂</span>
                <p className="text-lg font-medium">Select a project to view details</p>
                <p className="text-sm text-gray-600 mt-1">Or create a new one to get started.</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
