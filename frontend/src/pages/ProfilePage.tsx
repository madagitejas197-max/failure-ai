import React, { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import apiClient from '../api/client'

export default function ProfilePage() {
  const { user, updateProfile } = useAuth()
  const [displayName, setDisplayName] = useState(user?.display_name ?? '')
  const [avatarUrl, setAvatarUrl] = useState(user?.avatar_url ?? '')
  const [bio, setBio] = useState(user?.bio ?? '')
  const [password, setPassword] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setMessage(null)
    setIsSubmitting(true)

    try {
      const payload: any = {
        display_name: displayName,
        avatar_url: avatarUrl || null,
        bio: bio || null,
      }
      if (password) {
        payload.password = password
      }

      const { data } = await apiClient.put('/users/me', payload)
      updateProfile(data)
      setPassword('')
      setMessage({ type: 'success', text: 'Profile updated successfully!' })
    } catch (err: any) {
      console.error(err)
      setMessage({
        type: 'error',
        text: err.response?.data?.detail ?? 'Failed to update profile.',
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  if (!user) {
    return (
      <div className="container-page py-20 text-center">
        <h1 className="text-2xl font-bold">Please sign in to view your profile.</h1>
      </div>
    )
  }

  return (
    <div className="container-page py-12 max-w-2xl animate-slide-up">
      <h1 className="text-3xl font-bold mb-2">My Profile</h1>
      <p className="text-gray-500 mb-8">Update your profile information and credentials</p>

      {message && (
        <div
          className={`mb-6 p-4 rounded-lg border text-sm ${
            message.type === 'success'
              ? 'bg-green-900/30 border-green-500/50 text-green-200'
              : 'bg-red-900/30 border-red-500/50 text-red-200'
          }`}
        >
          {message.text}
        </div>
      )}

      <div className="card">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="flex items-center gap-6 mb-8">
            <div className="w-20 h-20 rounded-2xl bg-brand-600 flex items-center justify-center text-white text-3xl font-bold overflow-hidden border border-white/10 glow-brand">
              {avatarUrl ? (
                <img src={avatarUrl} alt={displayName} className="w-full h-full object-cover" />
              ) : (
                displayName[0]?.toUpperCase()
              )}
            </div>
            <div>
              <h2 className="text-lg font-bold text-gray-200">{user.email}</h2>
              <span className="badge badge-brand mt-1 capitalize">{user.role}</span>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1.5">
              Display Name
            </label>
            <input
              type="text"
              required
              className="input"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              disabled={isSubmitting}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1.5">
              Avatar Image URL
            </label>
            <input
              type="url"
              className="input"
              placeholder="https://example.com/avatar.png"
              value={avatarUrl}
              onChange={(e) => setAvatarUrl(e.target.value)}
              disabled={isSubmitting}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1.5">
              Bio
            </label>
            <textarea
              className="input min-h-[100px]"
              placeholder="Tell us about yourself..."
              value={bio}
              onChange={(e) => setBio(e.target.value)}
              disabled={isSubmitting}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1.5">
              New Password (leave blank to keep current)
            </label>
            <input
              type="password"
              className="input"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={isSubmitting}
            />
          </div>

          <button type="submit" className="btn-primary w-full py-3" disabled={isSubmitting}>
            {isSubmitting ? 'Saving changes...' : 'Save Changes'}
          </button>
        </form>
      </div>
    </div>
  )
}
