import { expect, test } from '@playwright/test'

test.describe('落地页', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/api/auth/me', (route) =>
      route.fulfill({ status: 401, contentType: 'application/json', body: '{"detail":"未登录"}' }),
    )
    await page.goto('/')
  })

  test('首屏展示真实修前修后与提示词模板', async ({ page }) => {
    await expect(page.getByRole('heading', { name: /一句话，交付/ })).toBeVisible()
    await expect(page.locator('img[src="/landing/product-before.png"]').first()).toBeVisible()
    await expect(page.locator('img[src="/landing/product-after.png"]').first()).toBeVisible()

    await page.getByRole('button', { name: '白底主图', exact: true }).click()
    await expect(page.getByLabel('描述你想要的商品物料')).toHaveValue(/纯白背景/)
  })

  test('点免费开始进入登录', async ({ page }) => {
    await page.getByRole('link', { name: '免费开始' }).first().click()
    await expect(page).toHaveURL(/\/auth/)
    await expect(page.getByRole('heading', { name: '登录' })).toBeVisible()
  })

  test('编排演示可以手动切帧', async ({ page }) => {
    const demo = page.locator('#demo')
    await page.getByRole('link', { name: '编排' }).click()
    await expect(demo.getByRole('heading', { name: /五步变成投放物料/ })).toBeVisible()
    await demo.getByRole('button', { name: /场景氛围/ }).click()
    await expect(demo.getByText('场景氛围', { exact: true })).toBeVisible()
  })
})
