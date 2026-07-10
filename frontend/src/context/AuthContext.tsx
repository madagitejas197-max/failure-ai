import React, { createContext, useContext, useState, useEffect } from 'react'
import apiClient from '../api/client'

interface User {
  id: string
  email: string
  display_name: string
  avatar_url: string | null
  bio: string | null
  role: 'user' | 'moderator' | 'admin'
  github_id: string | null
  created_at: string
  updated_at: string
}

interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (token: string, refreshToken: string) => Promise<void>
  logout: () => void
  updateProfile: (updatedData: Partial<User>) => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const fetchProfile = async () => {
    try {
      const token = localStorage.getItem('access_token')
      if (token) {
        const { data } = await apiClient.get('/users/me')
        setUser(data)
      }
    } catch (error) {
      console.error('Failed to fetch user profile:', error)
      logout()
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchProfile()
  }, [])

  const login = async (token: string, refreshToken: string) => {
    localStorage.setItem('access_token', token)
    localStorage.setItem('refresh_token', refreshToken)
    await fetchProfile()
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    setUser(null)
    setIsLoading(false)
  }

  const updateProfile = (updatedData: Partial<User>) => {
    if (user) {
      setUser({ ...user, ...updatedData } as User)
    }
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        logout,
        updateProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
