import { test, expect } from '@playwright/test';

const FRONTEND_URL = 'http://localhost:5173';

test.describe('Chatbot UI End-to-End', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(FRONTEND_URL);
  });

  test('renders chat UI components', async ({ page }) => {
    // Chat header and query type selector
    await expect(page.getByText('Chatbot')).toBeVisible();
    await expect(page.locator('select[aria-label="Query type"]')).toBeVisible();
    // Message input and send button
    await expect(page.locator('input[aria-label="Type your message"]')).toBeVisible();
    await expect(page.locator('button[aria-label="Send message"]')).toBeVisible();
  });

  test('toggle context provider and preview files', async ({ page }) => {
    // Open context panel
    await page.click('button.add-context-btn');
    await expect(page.getByText('Context Provider')).toBeVisible();
    // File list should display files
    const firstFile = page.locator('.file-list .file-item').first();
    await expect(firstFile).toBeVisible();
    const fileName = await firstFile.textContent();
    // Select a file
    await firstFile.click();
    // Preview panel shows file content for selected
    await expect(page.getByText(fileName + ':')).toBeVisible();
  });

  test('send message without context', async ({ page }) => {
    // Enter message
    await page.fill('input[aria-label="Type your message"]', 'Hello Playwright');
    await page.click('button[aria-label="Send message"]');
    // User message appears
    await expect(page.getByText('You')).toBeVisible();
    await expect(page.getByText('Hello Playwright')).toBeVisible();
    // Typing indicator appears
    await expect(page.getByText('Bot is typing')).toBeVisible();
  });
});
