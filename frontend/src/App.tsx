import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import HomePage from './pages/HomePage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import FailuresPage from './pages/FailuresPage'
import NotFoundPage from './pages/NotFoundPage'
import ProjectsPage from './pages/ProjectsPage'
import SubmitFailurePage from './pages/SubmitFailurePage'
import FailureDetailPage from './pages/FailureDetailPage'
import ProfilePage from './pages/ProfilePage'
import { AuthProvider, useAuth } from './context/AuthContext'

// Protected Route Wrapper
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="min-h-screen bg-surface flex items-center justify-center text-gray-500">
        Loading...
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            {/* Public Routes */}
            <Route path="/"          element={<HomePage />} />
            <Route path="/failures"  element={<FailuresPage />} />
            <Route path="/failures/:id" element={<FailureDetailPage />} />
            <Route path="/login"     element={<LoginPage />} />
            <Route path="/register"  element={<RegisterPage />} />
            <Route path="*"          element={<NotFoundPage />} />

            {/* Protected Routes */}
            <Route
              path="/failures/submit"
              element={
                <ProtectedRoute>
                  <SubmitFailurePage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/projects"
              element={
                <ProtectedRoute>
                  <ProjectsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/profile"
              element={
                <ProtectedRoute>
                  <ProfilePage />
                </ProtectedRoute>
              }
            />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}
