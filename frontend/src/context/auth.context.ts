import { createContext } from 'react'

import type {
  LoginRequest,
  User,
} from '../types/auth.types'

// El contexto va en su propio archivo (no en AuthContext.tsx) porque
// Vite Fast Refresh exige que un .tsx exporte solo componentes.

export interface AuthContextValue {
  user: User | null
  isAuthenticated: boolean
  loading: boolean
  login: (credentials: LoginRequest) => Promise<void>
  logout: () => Promise<void>
  updateUser: (user: User) => void
}

export const AuthContext = createContext<AuthContextValue | undefined>(
  undefined,
)
