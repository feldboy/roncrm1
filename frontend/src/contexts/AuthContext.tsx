import React, { createContext, useContext, useEffect, useState } from 'react'
import { api } from '@/services/api'

interface User {
  id: string
  email: string
  role: string
  permissions: string[]
}

interface AuthContextType {
  user: User | null
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  isLoading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

interface AuthProviderProps {
  children: React.ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`
      checkAuth()
    } else {
      setIsLoading(false)
    }
  }, [])

  const checkAuth = async () => {
    try {
      const response = await api.get('/auth/me')
      setUser(response.data)
    } catch (error) {
      localStorage.removeItem('auth_token')
      delete api.defaults.headers.common['Authorization']
    } finally {
      setIsLoading(false)
    }
  }

  const login = async (email: string, password: string) => {
    const response = await api.post('/auth/login', { email, password })
    const { access_token, user: userData } = response.data
    
    localStorage.setItem('auth_token', access_token)
    api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
    setUser(userData)
  }

  const logout = () => {
    localStorage.removeItem('auth_token')
    delete api.defaults.headers.common['Authorization']
    setUser(null)
  }

  const value = {
    user,
    login,
    logout,
    isLoading,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}