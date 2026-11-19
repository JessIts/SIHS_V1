import { expect, type Locator, type Page } from '@playwright/test'

export const API_URL = 'http://localhost:8000/api/v1'

// Usuario creado por scripts/seed_horarios.py
const COORDINADOR = {
  email: 'coordinacion.mercadeo@example.com',
  password: 'Coordinador123*',
}

export async function iniciarSesionComoCoordinador(page: Page) {
  await page.goto('/login')
  await page.getByLabel('Correo electrónico').fill(COORDINADOR.email)
  await page.getByLabel('Contraseña').fill(COORDINADOR.password)
  await page.getByRole('button', { name: 'Iniciar sesión' }).click()
  await expect(page).toHaveURL(/\/coordinador$/)
}

export interface DatosFicha {
  codigo: string
  inicio: string
  fin: string
}

export async function llenarFormularioFicha(formulario: Locator, datos: DatosFicha) {
  await formulario.getByLabel('Código de ficha').fill(datos.codigo)
  await formulario.getByLabel('Jornada').selectOption({ label: 'TARDE' })
  await formulario.getByLabel('Programa').selectOption({
    label: 'PRG-MERC · DESARROLLO DE PROCESOS DE MERCADEO',
  })
  await formulario.getByLabel('Modalidad').selectOption({ label: 'Presencial' })
  await formulario.getByLabel('Estado').selectOption({ label: 'En formación' })
  await formulario.getByLabel('Inicio de formación').fill(datos.inicio)
  await formulario.getByLabel('Fin de formación').fill(datos.fin)
}

/** Empieza a escuchar el POST de creación. Llamar ANTES del clic. */
export function esperarCreacionFicha(page: Page) {
  return page.waitForResponse(
    (r) => r.url().endsWith('/api/v1/fichas') && r.request().method() === 'POST',
  )
}