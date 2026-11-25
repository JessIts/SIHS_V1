import { expect, type Locator, type Page } from '@playwright/test'

export const API_URL = 'http://localhost:8000/api/v1'

// El seed no crea administradores. Antes de correr las pruebas:
//   1. Registrar esta cuenta desde la pantalla "Registrarse".
//   2. En backend: python -m scripts.create_admin admin.sihs@example.com
const ADMIN = {
  email: 'admin.sihs@example.com',
  password: 'Admin123*',
}

export async function iniciarSesionComoAdmin(page: Page) {
  await page.goto('/login')
  await page.getByLabel('Correo electrónico').fill(ADMIN.email)
  await page.getByLabel('Contraseña').fill(ADMIN.password)
  await page.getByRole('button', { name: 'Iniciar sesión' }).click()
  await expect(page).toHaveURL(/\/admin$/)
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

export interface FichaApi {
  uuid: string
  codigo: string
  jornada: { nombre: string }
  modalidad: string
}

/**
 * Busca fichas activas por código exacto usando la API.
 * Se usa en lugar de la tabla porque el admin ve todas las fichas
 * y la tabla está paginada: la fila buscada puede no estar en la página 1.
 * page.request comparte las cookies del navegador, así que va autenticado.
 */
export async function buscarFichasPorCodigo(page: Page, codigo: string): Promise<FichaApi[]> {
  const respuesta = await page.request.get(`${API_URL}/fichas`, { params: { codigo } })
  expect(respuesta.ok()).toBeTruthy()
  return (await respuesta.json()).data.items
}
