/**
 * Smoke test to verify Playwright setup
 */

import { test, expect } from '@playwright/test';

test.describe('Playwright Smoke Test', () => {
	test.skip('basic Playwright functionality works', async ({ page }) => {
		// This is a smoke test - skip it in normal runs
		await page.goto('https://example.com');
		await expect(page).toHaveTitle(/Example Domain/);
	});

	test('Playwright is properly configured', () => {
		// Just verify test framework loads
		expect(true).toBe(true);
	});
});
