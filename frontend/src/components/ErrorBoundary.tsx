import { Component, ErrorInfo, ReactNode } from 'react'

type ErrorBoundaryProps = { children: ReactNode }
type ErrorBoundaryState = { hasError: boolean }

export default class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  state: ErrorBoundaryState = { hasError: false }

  static getDerivedStateFromError(): ErrorBoundaryState {
    return { hasError: true }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('Frontend render error', error, info.componentStack)
  }

  render() {
    if (!this.state.hasError) return this.props.children

    return (
      <main className="auth-wrap">
        <section className="card auth-card" role="alert" aria-live="assertive">
          <h1>Something went wrong</h1>
          <p className="lede">This page could not be displayed. Reload to try again.</p>
          <button className="btn" type="button" onClick={() => window.location.reload()}>
            Reload page
          </button>
        </section>
      </main>
    )
  }
}
