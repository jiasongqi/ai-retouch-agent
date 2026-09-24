import { expect, test, type APIRequestContext } from '@playwright/test'

async function backendReady(request: APIRequestContext) {
  try {
    const response = await request.get('http://127.0.0.1:7302/api/health', { timeout: 3000 })
    if (!response.ok()) return false
    const body = (await response.json()) as { api?: string; database?: string }
    return body.api === 'ok' && body.database === 'ok'
  } catch {
    return false
  }
}

test.describe('工作台主路径', () => {
  test('登录 → 出图 → 修图 → 导出', async ({ page, request }) => {
    test.skip(!(await backendReady(request)), '后端未启动，跳过全链路。先起 7302 再跑 npm run test:e2e:full')
    test.setTimeout(90_000)

    const username = `e2e_${Date.now().toString(36)}`
    await page.goto('/auth?mode=register')
    await page.getByLabel('用户名').fill(username)
    await page.getByLabel('密码').fill('test1234')
    await page.getByRole('button', { name: '注册并进入' }).click()
    await expect(page).toHaveURL(/\/create/)

    await page.getByRole('button', { name: '白底主图' }).click()
    await page.getByRole('button', { name: '生成' }).click()
    await expect(page.getByRole('heading', { name: '选出一张' })).toBeVisible({ timeout: 60_000 })

    await page.getByRole('img', { name: '候选图 1' }).click()
    await page.getByRole('button', { name: '进入编辑' }).click()
    await expect(page).toHaveURL(/\/editor\//)
    await expect(page.locator('canvas').first()).toBeVisible({ timeout: 20_000 })

    const sessionId = page.url().split('/editor/')[1]?.split(/[?#]/)[0]
    expect(sessionId).toBeTruthy()
    await page.goto(`/marketing/${sessionId}`)
    await expect(page.getByText('四类营销图')).toBeVisible()
    await expect(page.getByRole('button', { name: '一键套图' })).toBeVisible()
  })
})
