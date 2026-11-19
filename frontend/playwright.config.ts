import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './e2e',
  timeout: 30_000,
  reporter: 'html',

  use: {
    // Debe ser "localhost" (no 127.0.0.1) para que coincida con el CORS
    // del backend y la cookie de sesión funcione.
    baseURL: 'http://localhost:5173',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },

  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'], channel: 'chrome',} },
  ],

  // Playwright levanta el frontend antes de las pruebas
  // (o reutiliza el que ya tengas corriendo).
  webServer: {
    command: 'pnpm dev',
    url: 'http://localhost:5173',
    reuseExistingServer: true,
  },
})