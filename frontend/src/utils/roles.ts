import type { UserRole } from '../types/role.types'

export const ROLE_LABELS: Record<UserRole, string> = {
  admin: 'Administrador',
  coordinador: 'Coordinador',
  instructor: 'Instructor',
  aprendiz: 'Aprendiz',
  user: 'Usuario',
}

/**
 * Roles que entran a las vistas de gestión:
 *  - admin: registra y modifica todo.
 *  - coordinador: solo registra horarios de su coordinación;
 *    el resto (fichas, ambientes...) lo consulta.
 */
export const MANAGER_ROLES: UserRole[] = [
  'admin',
  'coordinador',
]

export const HOME_BY_ROLE: Record<UserRole, string> = {
  admin: '/admin',
  coordinador: '/coordinador',
  instructor: '/instructor',
  aprendiz: '/aprendiz',
  user: '/profile',
}

export function isManager(role?: UserRole): boolean {
  return role !== undefined && MANAGER_ROLES.includes(role)
}

export function isAdmin(role?: UserRole): boolean {
  return role === 'admin'
}

/** Pueden registrar, editar y eliminar casillas de horario. */
export function canScheduleHorarios(role?: UserRole): boolean {
  return isManager(role)
}
