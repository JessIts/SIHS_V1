import { test, expect } from '@playwright/test'

import {
  API_URL,
  esperarCreacionFicha,
  iniciarSesionComoCoordinador,
  llenarFormularioFicha,
} from './helpers'

test.describe('Registro de fichas', () => {
  let fichaUuid: string | null = null

  // ARRANGE común: sesión de coordinador y formulario abierto
  test.beforeEach(async ({ page }) => {
    await iniciarSesionComoCoordinador(page)
    await page.goto('/gestion/fichas')
    await page.getByRole('button', { name: 'Nueva ficha' }).click()
  })

  // Limpieza: solo hay algo que borrar si una prueba creó una ficha
  test.afterEach(async ({ page }) => {
    if (fichaUuid) {
      await page.request.delete(`${API_URL}/fichas/${fichaUuid}`)
      fichaUuid = null
    }
  })

  test('el coordinador registra una ficha nueva', async ({ page }) => {
    // ==================== ARRANGE ====================
    const formulario = page.getByRole('dialog', { name: 'Nueva ficha' })
    const codigo = `E2E-${Date.now()}`

    // ====================== ACT ======================
    await llenarFormularioFicha(formulario, {
      codigo,
      inicio: '2026-11-03',
      fin: '2028-11-03',
    })
    const respuestaCreacion = esperarCreacionFicha(page)
    await formulario.getByRole('button', { name: 'Crear', exact: true }).click()
    const respuesta = await respuestaCreacion

    // ===================== ASSERT ====================
    expect(respuesta.status()).toBe(201)
    fichaUuid = (await respuesta.json()).data.uuid

    await expect(page.getByText('Ficha creada correctamente.')).toBeVisible()
    await expect(formulario).toBeHidden()

    const fila = page.getByRole('row').filter({ hasText: codigo })
    await expect(fila).toBeVisible()
    await expect(fila).toContainText('TARDE')
    await expect(fila).toContainText('Presencial')
  })

  test('no permite registrar una ficha con un código existente', async ({ page }) => {
    // ==================== ARRANGE ====================
    const formulario = page.getByRole('dialog', { name: 'Nueva ficha' })
    const codigoExistente = '3141665' // creada por el seed

    // Precondición: la ficha ya existe en la tabla
    const filasExistentes = page.getByRole('row').filter({ hasText: codigoExistente })
    await expect(filasExistentes).toHaveCount(1)

    // ====================== ACT ======================
    await llenarFormularioFicha(formulario, {
      codigo: codigoExistente,
      inicio: '2026-11-03',
      fin: '2028-11-03',
    })
    const respuestaCreacion = esperarCreacionFicha(page)
    await formulario.getByRole('button', { name: 'Crear', exact: true }).click()
    const respuesta = await respuestaCreacion

    // ===================== ASSERT ====================
    // 1. El backend la rechaza por conflicto
    expect(respuesta.status()).toBe(409)
    expect((await respuesta.json()).message).toBe('Ya existe una ficha con ese código.')

    // 2. El usuario ve el error y el formulario sigue abierto con sus datos
    await expect(formulario.getByText('Ya existe una ficha con ese código.')).toBeVisible()
    await expect(formulario).toBeVisible()
    await expect(formulario.getByLabel('Código de ficha')).toHaveValue(codigoExistente)

    // 3. No se mostró éxito ni se duplicó la ficha
    await expect(page.getByText('Ficha creada correctamente.')).toBeHidden()
    await expect(filasExistentes).toHaveCount(1)
  })
})