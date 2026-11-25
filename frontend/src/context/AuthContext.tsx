import {
  useEffect,
  useState,
  type ReactNode,
} from 'react'

import { AuthContext } from './auth.context'

import {
  getCurrentUser,
  login as loginService,
  logout as logoutService,
} from '../services/auth.service'

import type {
  LoginRequest,
  User,
} from '../types/auth.types'

interface AuthProviderProps {
  children: ReactNode
}

export function AuthProvider({
  children,
}: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  const isAuthenticated = user !== null

  useEffect(() => {
    async function restoreSession() {
      try {
        const currentUser = await getCurrentUser()

        setUser(currentUser)
      } catch {
        setUser(null)
      } finally {
        setLoading(false)
      }
    }

    restoreSession()
  }, [])

  async function login(
    credentials: LoginRequest,
  ): Promise<void> {
    await loginService(credentials)

    const currentUser = await getCurrentUser()

    setUser(currentUser)
  }

  async function logout(): Promise<void> {
    try {
      await logoutService()
    } finally {
      setUser(null)
    }
  }

  function updateUser(updatedUser: User): void {
    setUser(updatedUser)
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated,
        loading,
        login,
        logout,
        updateUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}
