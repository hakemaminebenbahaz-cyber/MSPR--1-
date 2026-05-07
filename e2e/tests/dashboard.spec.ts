import { test, expect } from '@playwright/test'

test.describe('ObRail Dashboard — Navigation', () => {
  test('la page Vue Globale se charge', async ({ page }) => {
    await page.goto('/')
    await expect(page).toHaveTitle(/ObRail/)
    await expect(page.getByText("Vue d'ensemble")).toBeVisible()
  })

  test('navigation vers la page Recherche', async ({ page }) => {
    await page.goto('/')
    await page.getByText('Recherche').click()
    await expect(page.getByText('Rechercher des gares')).toBeVisible()
  })

  test('navigation vers Données brutes', async ({ page }) => {
    await page.goto('/')
    await page.getByText('Données brutes').click()
    await expect(page.getByText('Explorer et naviguer')).toBeVisible()
  })

  test('le footer affiche ObRail Europe', async ({ page }) => {
    await page.goto('/')
    await expect(page.getByText('ObRail Europe').first()).toBeVisible()
  })
})

test.describe('ObRail Dashboard — Vue Globale', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
    await page.waitForTimeout(2000)
  })

  test('affiche des statistiques globales', async ({ page }) => {
    const stats = page.locator('text=/\\d+/')
    await expect(stats.first()).toBeVisible()
  })

  test('la section opérateurs est présente', async ({ page }) => {
    await expect(page.getByText(/opérateur/i).first()).toBeVisible()
  })

  test('la section gares est présente', async ({ page }) => {
    await expect(page.getByText(/gare/i).first()).toBeVisible()
  })
})

test.describe('ObRail Dashboard — Recherche', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
    await page.getByText('Recherche').click()
    await page.waitForTimeout(1000)
  })

  test('les onglets de recherche sont présents', async ({ page }) => {
    const hasOperateurs = await page.getByText(/opérateur/i).count() > 0
    const hasGares = await page.getByText(/gare/i).count() > 0
    expect(hasOperateurs || hasGares).toBeTruthy()
  })

  test('un champ de recherche est disponible', async ({ page }) => {
    const input = page.locator('input').first()
    await expect(input).toBeVisible()
  })

  test('la recherche retourne des résultats', async ({ page }) => {
    const input = page.locator('input').first()
    await input.fill('Paris')
    await page.keyboard.press('Enter')
    await expect(page.locator('table').first()).toBeVisible({ timeout: 10000 })
  })
})

test.describe('ObRail Dashboard — Données Brutes', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
    await page.getByText('Données brutes').click()
    await page.waitForTimeout(2000)
  })

  test('des données sont affichées', async ({ page }) => {
    await expect(page.locator('table').first()).toBeVisible({ timeout: 10000 })
  })
})

test.describe('ObRail API — Santé', () => {
  test('l\'API répond sur /health', async ({ request }) => {
    const response = await request.get('http://localhost:8001/health')
    expect(response.status()).toBe(200)
    const body = await response.json()
    expect(body.status).toBe('healthy')
  })

  test('l\'API retourne des opérateurs', async ({ request }) => {
    const response = await request.get('http://localhost:8001/api/v1/operateurs/?limit=5', {
      headers: { 'X-API-Key': 'obrail-api-key-2026' }
    })
    expect(response.status()).toBe(200)
    const body = await response.json()
    expect(Array.isArray(body)).toBeTruthy()
    expect(body.length).toBeGreaterThan(0)
  })

  test('l\'API retourne des gares', async ({ request }) => {
    const response = await request.get('http://localhost:8001/api/v1/gares/?limit=5', {
      headers: { 'X-API-Key': 'obrail-api-key-2026' }
    })
    expect(response.status()).toBe(200)
    const body = await response.json()
    expect(Array.isArray(body)).toBeTruthy()
    expect(body.length).toBeGreaterThan(0)
  })

  test('l\'API refuse sans clé API', async ({ request }) => {
    const response = await request.get('http://localhost:8001/api/v1/operateurs/')
    expect(response.status()).toBe(401)
  })

  test('l\'API retourne les stats globales', async ({ request }) => {
    const response = await request.get('http://localhost:8001/api/v1/comparisons/stats-globales', {
      headers: { 'X-API-Key': 'obrail-api-key-2026' }
    })
    expect(response.status()).toBe(200)
    const body = await response.json()
    expect(body.total_operateurs).toBeGreaterThan(0)
    expect(body.total_gares).toBeGreaterThan(0)
    expect(body.total_dessertes).toBeGreaterThan(0)
  })
})
