import { Link } from 'react-router-dom'

export default function NotFoundPage() {
  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center p-4">
      <div className="text-center animate-slide-up">
        <div className="text-8xl font-black gradient-text mb-4">404</div>
        <h1 className="text-2xl font-bold mb-2">Page not found</h1>
        <p className="text-gray-500 mb-8 max-w-sm mx-auto">
          Looks like this failure wasn't documented. Let's get you back on track.
        </p>
        <Link to="/" id="back-home-btn" className="btn-primary">
          Back to Home
        </Link>
      </div>
    </div>
  )
}
