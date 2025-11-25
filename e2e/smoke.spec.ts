/**
 * Smoke tests - Critical paths validation
 * Fast tests (~30s) to validate the most critical user journeys
 * Used in CI/CD and deployment verification
 */

import { test, expect } from '@playwright/test';

test.describe('Smoke Tests - Critical Paths', () => {
	test('homepage loads and renders', async ({ page }) => {
		await page.goto('/');

		// Page should have proper title
		await expect(page).toHaveTitle(/Lexikon/);

		// Main heading should be visible
		await expect(page.getByRole('heading', { name: /LEXIKON/i })).toBeVisible();

		// Page should load successfully
		await expect(page).toHaveURL('/');
	});

	test('navbar is present on homepage', async ({ page }) => {
		await page.goto('/');

		// Navigation should be visible
		await expect(page.getByRole('navigation')).toBeVisible();

		// Logo should be clickable
		await expect(page.getByRole('link', { name: /lexikon/i }).first()).toBeVisible();
	});

	test('can navigate to login page', async ({ page }) => {
		await page.goto('/');

		// Find and click the "Sign in" link
		const signInButton = page.getByRole('link', { name: /sign in/i });
		await expect(signInButton).toBeVisible();
		await signInButton.click();

		// Should be on login page
		await expect(page).toHaveURL(/\/login/);

		// Login form elements should be visible
		await expect(page.getByRole('heading', { name: /sign in/i })).toBeVisible();
	});

	test('can navigate to register page', async ({ page }) => {
		await page.goto('/');

		// Find and click the "Get started" button
		const getStartedButton = page.getByRole('link', { name: /get started/i });
		await expect(getStartedButton).toBeVisible();
		await getStartedButton.click();

		// Should be on register page
		await expect(page).toHaveURL(/\/register/);

		// Register form elements should be visible
		await expect(page.getByRole('heading', { name: /create.*account|register/i })).toBeVisible();
	});

	test('can navigate back from login to homepage', async ({ page }) => {
		// Navigate to login
		await page.goto('/login');
		await expect(page).toHaveURL(/\/login/);

		// Click logo to return to homepage
		await page.getByRole('link', { name: /lexikon/i }).first().click();

		// Should be back on homepage
		await expect(page).toHaveURL('/');
	});
});
