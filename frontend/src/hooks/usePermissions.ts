import { useAuth } from './useAuth'

import { canScheduleHorarios, isAdmin } from '../utils/roles'

/**
 * Permisos derivados del rol del usuario autenticado.
 *  - canManage:   solo el admin registra y modifica datos no personales
 *                 (sedes, ambientes, programas, fichas, catálogos...).
 *  - canSchedule: admin y coordinador registran horarios (el coordinador
 *                 solo los de su coordinación).
 *  - isAdmin:     el admin además gestiona las cuentas de usuario.
 */
export function usePermissions() {
  const { user } = useAuth()

  return {
    role: user?.role,
    isAdmin: isAdmin(user?.role),
    isCoordinador: user?.role === 'coordinador',
    canManage: isAdmin(user?.role),
    canSchedule: canScheduleHorarios(user?.role),
  }
}
