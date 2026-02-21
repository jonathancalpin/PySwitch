// @ts-check
const { test, expect } = require('@playwright/test');

/**
 * Emulator sync tests: confirm the localhost emulator loads, runs, and
 * reports connection state (no stuck hourglass). Run with the emulator
 * already served, e.g.:
 *   cd web-editor && npm run serve
 *   npm run test:emulator
 * Or: EMULATOR_URL=http://localhost:3000 npx playwright test
 */
test.describe('Emulator sync', () => {
  test('page loads and shows emulator UI', async ({ page }) => {
    await page.goto('/', { waitUntil: 'load' });
    await expect(page.locator('.container')).toBeVisible({ timeout: 30000 });
    await expect(page.locator('.application')).toBeVisible({ timeout: 10000 });
  });

  test('connection button is visible and not stuck on hourglass after load', async ({ page }) => {
    await page.goto('/', { waitUntil: 'load' });
    await page.waitForSelector('.application', { state: 'visible', timeout: 30000 });
    await page.waitForSelector('.client-select', { state: 'visible', timeout: 15000 });
    const hourglass = page.locator('.client-select.waiting .fa-hourglass-half');
    await expect(hourglass).not.toBeVisible({ timeout: 25000 });
  });

  test('live panel is visible and uses right third (no blank unused space)', async ({ page }) => {
    await page.goto('/', { waitUntil: 'load' });
    await page.waitForSelector('.application', { state: 'visible', timeout: 30000 });
    const livePanel = page.locator('#pyswitch-live-panel.pyswitch-live-panel');
    await expect(livePanel).toBeVisible({ timeout: 15000 });
    const box = await livePanel.boundingBox();
    expect(box).not.toBeNull();
    expect(box.width).toBeGreaterThanOrEqual(200);
  });

  test('live panel shows CC, Tap tempo, Combo (A+B, B+C), and Page up/down', async ({ page }) => {
    await page.goto('/', { waitUntil: 'load' });
    await page.waitForSelector('#pyswitch-live-panel', { state: 'visible', timeout: 15000 });
    const livePanel = page.locator('#pyswitch-live-panel');
    await expect(livePanel.getByText('CC messages')).toBeVisible();
    await expect(livePanel.getByText('Tap tempo')).toBeVisible();
    await expect(livePanel.getByRole('button', { name: 'A+B' })).toBeVisible();
    await expect(livePanel.getByRole('button', { name: 'B+C' })).toBeVisible();
    await expect(livePanel.getByRole('button', { name: 'Page up' })).toBeVisible();
    await expect(livePanel.getByRole('button', { name: 'Page down' })).toBeVisible();
  });

  test('display canvas has 240x240 when device is shown (skipped if no config loaded)', async ({ page }) => {
    await page.goto('/', { waitUntil: 'load' });
    await page.waitForSelector('.application', { state: 'visible', timeout: 30000 });
    const canvas = page.locator('#pyswitch-display');
    const visible = await canvas.waitFor({ state: 'visible', timeout: 5000 }).then(() => true).catch(() => false);
    if (!visible) {
      test.info().annotations.push({ type: 'skip', description: 'No config loaded – canvas appears after loading a config' });
      test.skip();
      return;
    }
    const w = await canvas.getAttribute('width');
    const h = await canvas.getAttribute('height');
    expect(Number(w)).toBe(240);
    expect(Number(h)).toBe(240);
  });
});
