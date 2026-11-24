import { apiRequest } from './api'

import type {
  ApiResponse,
  LoginRequest,
  User,
} from '../types/auth.types'

export interface RegisterRequest {
  name: string
  email: string
  phone: string
  document_number: string
  password: string
}

export async function login(
  credentials: LoginRequest,
): Promise<void> {
  await apiRequest<
    ApiResponse<{
      authenticated: boolean
    }>
  >(
    '/auth/login',
    {
      method: 'POST',
      body: JSON.stringify(credentials),
    },
  )
}

export async function register(
  data: RegisterRequest,
): Promise<User> {
  const response = await apiRequest<
    ApiResponse<User>
  >(
    '/auth/register',
    {
      method: 'POST',
      body: JSON.stringify(data),
    },
  )

  return response.data
}

export async function getCurrentUser(): Promise<User> {
  const response = await apiRequest<ApiResponse<User>>(
    '/users/me',
    {
      method: 'GET',
    },
  )

  return response.data
}

export interface ProfileUpdateRequest {
  name?: string
  email?: string
  phone?: string
  document_number?: string
  password?: string
}

export async function updateMyProfile(
  data: ProfileUpdateRequest,
): Promise<User> {
  const response = await apiRequest<ApiResponse<User>>(
    '/users/me',
    {
      method: 'PUT',
      body: JSON.stringify(data),
    },
  )

  return response.data
}


// ---------------------------------------------------------------
// Recuperación de contraseña
// ---------------------------------------------------------------

/** Pide el enlace. Responde igual exista o no el correo. */
export async function forgotPassword(email: string): Promise<string> {
  const response = await apiRequest<ApiResponse<null>>(
    '/auth/password/forgot',
    {
      method: 'POST',
      body: JSON.stringify({ email }),
    },
  )

  return response.message
}

export interface ResetTokenStatus {
  valid: boolean
  /** Correo enmascarado del usuario (ej. "an*****@gmail.com") */
  email: string
}

/** Verifica que el enlace siga vigente; lanza error si venció o ya se usó. */
export async function validateResetToken(token: string): Promise<ResetTokenStatus> {
  const response = await apiRequest<ApiResponse<ResetTokenStatus>>(
    `/auth/password/reset/validate?token=${encodeURIComponent(token)}`,
    {
      method: 'GET',
    },
  )

  return response.data
}

export async function resetPassword(token: string, password: string): Promise<string> {
  const response = await apiRequest<ApiResponse<null>>(
    '/auth/password/reset',
    {
      method: 'POST',
      body: JSON.stringify({ token, password }),
    },
  )

  return response.message
}

export async function logout(): Promise<void> {
  await apiRequest<
    ApiResponse<{
      authenticated: boolean
    }>
  >(
    '/auth/logout',
    {
      method: 'POST',
    },
  )
}