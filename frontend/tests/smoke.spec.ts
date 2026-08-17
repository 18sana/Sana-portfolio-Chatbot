import { test, expect } from "@playwright/test";

const base = process.env.PLAYWRIGHT_BASE_URL ?? "http://127.0.0.1:3000";

test("landing shows brand and enters chat", async ({ page }) => {
  await page.goto(base);
  await expect(page.getByRole("button", { name: /start conversation/i })).toBeVisible();
  await page.getByRole("button", { name: /start conversation/i }).click();
  await expect(page.getByPlaceholder(/ask about experience/i)).toBeVisible();
});

test("jd mode is reachable", async ({ page }) => {
  await page.goto(base);
  await page.getByRole("button", { name: /upload a job description/i }).click();
  await expect(page.getByText(/job-description fit/i)).toBeVisible();
});
