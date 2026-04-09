import { Component, type ReactNode } from 'react'
import { AlertTriangle } from 'lucide-react'

interface Props { children: ReactNode }
interface State { hasError: boolean; message: string }

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false, message: '' }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, message: error.message }
  }

  override render() {
    if (this.state.hasError) {
      return (
        <div className="flex flex-col items-center justify-center min-h-[400px] gap-4">
          <div className="p-4 bg-red-50 rounded-full">
            <AlertTriangle className="w-8 h-8 text-red-500" />
          </div>
          <div className="text-center">
            <h2 className="text-xl font-semibold text-gray-900 mb-1">Something went wrong</h2>
            <p className="text-sm text-gray-500">{this.state.message}</p>
          </div>
          <button
            onClick={() => this.setState({ hasError: false, message: '' })}
            className="px-4 py-2 bg-blue-600 text-white rounded-xl text-sm font-medium hover:bg-blue-700 transition"
          >
            Try again
          </button>
        </div>
      )
    }
    return this.props.children
  }
}
