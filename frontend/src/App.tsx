import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import { ProtectedRoute } from './components/auth/ProtectedRoute'
import { Layout } from './components/layout/Layout'
import { LoginPage } from './pages/LoginPage'
import { DashboardPage } from './pages/DashboardPage'
import { PlaintiffsPage } from './pages/PlaintiffsPage'
import { LawFirmsPage } from './pages/LawFirmsPage'
import { DocumentsPage } from './pages/DocumentsPage'
import { CommunicationsPage } from './pages/CommunicationsPage'
import { CasesPage } from './pages/CasesPage'
import { ReportsPage } from './pages/ReportsPage'
import { SettingsPage } from './pages/SettingsPage'
import { ErrorBoundary } from './components/ErrorBoundary'

function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/*"
          element={
            <ProtectedRoute>
              <Layout>
                <Routes>
                  <Route path="/" element={<Navigate to="/dashboard" replace />} />
                  <Route path="/dashboard" element={<DashboardPage />} />
                  <Route path="/plaintiffs" element={<PlaintiffsPage />} />
                  <Route path="/law-firms" element={<LawFirmsPage />} />
                  <Route path="/cases" element={<CasesPage />} />
                  <Route path="/documents" element={<DocumentsPage />} />
                  <Route path="/communications" element={<CommunicationsPage />} />
                  <Route path="/reports" element={<ReportsPage />} />
                  <Route path="/settings" element={
                    <ErrorBoundary>
                      <SettingsPage />
                    </ErrorBoundary>
                  } />
                </Routes>
              </Layout>
            </ProtectedRoute>
          }
        />
      </Routes>
    </AuthProvider>
  )
}

export default App