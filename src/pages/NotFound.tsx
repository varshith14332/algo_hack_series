import { Link } from 'react-router-dom'
import { Layout } from '../components/shared/Layout'

export function NotFound() {
  return (
    <Layout>
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-6 text-center">
        <div className="text-8xl font-bold text-gray-100">404</div>
        <div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Page Not Found</h1>
          <p className="text-gray-500 text-sm">The page you're looking for doesn't exist.</p>
        </div>
        <Link
          to="/"
          className="bg-blue-600 hover:bg-blue-700 text-white rounded-xl px-6 py-2.5 text-sm font-medium transition"
        >
          Back to Marketplace
        </Link>
      </div>
    </Layout>
  )
}
