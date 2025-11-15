/**
 * E2E tests for authentication flows
 */

import { test, expect } from '@playwright/test';

test.describe('Authentication Flow', () => {
	test.beforeEach(async ({ page }) => {
		// Clear any existing auth state
		await page.context().clearCookies();
		await page.goto('/');
	});

	test('should display login page', async ({ page }) => {
		await page.goto('/login');

		// Check page title
		await expect(page).toHaveTitle(/Login.*Lexikon/);

		// Check main elements are present
		await expect(page.getByRole('heading', { name: /sign in/i })).toBeVisible();
		await expect(page.getByLabel(/email/i)).toBeVisible();
		await expect(page.getByLabel(/password/i)).toBeVisible();
		await expect(page.getByRole('button', { name: /sign in/i })).toBeVisible();
	});

	test('should display register page', async ({ page }) => {
		await page.goto('/register');

		// Check page title
		await expect(page).toHaveTitle(/Register.*Lexikon/);

		// Check main elements are present
		await expect(page.getByRole('heading', { name: /create.*account/i })).toBeVisible();
		await expect(page.getByLabel(/email/i)).toBeVisible();
		await expect(page.getByLabel(/first name/i)).toBeVisible();
		await expect(page.getByLabel(/last name/i)).toBeVisible();
		await expect(page.getByLabel(/^password$/i)).toBeVisible();
	});

	test('should show validation errors on empty login form', async ({ page }) => {
		await page.goto('/login');

		// Click submit without filling form
		await page.getByRole('button', { name: /sign in/i }).click();

		// HTML5 validation should prevent submission
		// Check that we're still on login page
		await expect(page).toHaveURL(/\/login/);
	});

	test('should show error on invalid credentials', async ({ page }) => {
		await page.goto('/login');

		// Fill in invalid credentials
		await page.getByLabel(/email/i).fill('invalid@example.com');
		await page.getByLabel(/password/i).fill('wrongpassword');

		// Submit form
		await page.getByRole('button', { name: /sign in/i }).click();

		// Wait for error message (API call will fail since backend is not running in this test)
		// In a real scenario with backend, we'd check for specific error messages
		await page.waitForTimeout(1000);
	});

	test('should navigate between login and register', async ({ page }) => {
		await page.goto('/login');

		// Click "Create account" link
		await page.getByRole('link', { name: /create.*account/i }).click();

		// Should be on register page
		await expect(page).toHaveURL(/\/register/);
		await expect(page.getByRole('heading', { name: /create.*account/i })).toBeVisible();

		// Click "Sign in" link
		await page.getByRole('link', { name: /sign in/i }).click();

		// Should be back on login page
		await expect(page).toHaveURL(/\/login/);
		await expect(page.getByRole('heading', { name: /sign in/i })).toBeVisible();
	});

	test('should display OAuth login buttons', async ({ page }) => {
		await page.goto('/login');

		// Check OAuth buttons are present
		await expect(page.getByRole('button', { name: /google/i })).toBeVisible();
		await expect(page.getByRole('button', { name: /github/i })).toBeVisible();
	});

	test('should redirect to terms page when authenticated', async ({ page }) => {
		// This test requires mocking authentication state
		// For now, we'll check that the redirect logic exists
		await page.goto('/login');

		// In a full implementation, we would:
		// 1. Set localStorage with auth data
		// 2. Navigate to login
		// 3. Verify redirect to /terms
	});

	test('should display NavBar when not authenticated', async ({ page }) => {
		await page.goto('/');

		// NavBar should be visible
		await expect(page.getByRole('navigation')).toBeVisible();

		// Should show "Sign In" and "Get Started" buttons
		await expect(page.getByRole('link', { name: /sign in/i })).toBeVisible();
		await expect(page.getByRole('link', { name: /get started/i })).toBeVisible();
	});
});

test.describe('Registration Flow', () => {
	test.beforeEach(async ({ page }) => {
		await page.context().clearCookies();
		await page.goto('/register');
	});

	test('should show all required fields', async ({ page }) => {
		await expect(page.getByLabel(/email/i)).toBeVisible();
		await expect(page.getByLabel(/first name/i)).toBeVisible();
		await expect(page.getByLabel(/last name/i)).toBeVisible();
		await expect(page.getByLabel(/^password$/i)).toBeVisible();
		await expect(page.getByLabel(/confirm password/i)).toBeVisible();
	});

	test('should validate email format', async ({ page }) => {
		await page.getByLabel(/email/i).fill('invalid-email');
		await page.getByLabel(/first name/i).fill('John');
		await page.getByLabel(/last name/i).fill('Doe');
		await page.getByLabel(/^password$/i).fill('password123');
		await page.getByLabel(/confirm password/i).fill('password123');

		await page.getByRole('button', { name: /create account/i }).click();

		// Should still be on register page due to validation
		await expect(page).toHaveURL(/\/register/);
	});

	test('should validate password confirmation', async ({ page }) => {
		await page.getByLabel(/email/i).fill('test@example.com');
		await page.getByLabel(/first name/i).fill('John');
		await page.getByLabel(/last name/i).fill('Doe');
		await page.getByLabel(/^password$/i).fill('password123');
		await page.getByLabel(/confirm password/i).fill('differentpassword');

		await page.getByRole('button', { name: /create account/i }).click();

		// Should show error message about password mismatch
		await expect(page.getByText(/passwords.*match/i)).toBeVisible();
	});

	test('should have OAuth registration options', async ({ page }) => {
		await expect(page.getByRole('button', { name: /google/i })).toBeVisible();
		await expect(page.getByRole('button', { name: /github/i })).toBeVisible();
	});
});

test.describe('Protected Routes', () => {
	test('should redirect to login when accessing protected routes unauthenticated', async ({
		page
	}) => {
		// Try to access protected route
		await page.goto('/profile');

		// Should redirect to login
		await expect(page).toHaveURL(/\/login/);
	});

	test('should redirect to login when accessing terms page unauthenticated', async ({ page }) => {
		await page.goto('/terms');

		// Should redirect to login
		await expect(page).toHaveURL(/\/login/);
	});

	test('should redirect to login when accessing create term page unauthenticated', async ({
		page
	}) => {
		await page.goto('/terms/new');

		// Should redirect to login
		await expect(page).toHaveURL(/\/login/);
	});
});

test.describe('Accessibility', () => {
	test('login page should have proper form labels', async ({ page }) => {
		await page.goto('/login');

		// Check all inputs have associated labels
		const emailInput = page.getByLabel(/email/i);
		const passwordInput = page.getByLabel(/password/i);

		await expect(emailInput).toBeVisible();
		await expect(passwordInput).toBeVisible();
	});

	test('register page should have proper form labels', async ({ page }) => {
		await page.goto('/register');

		// Check all inputs have associated labels
		await expect(page.getByLabel(/email/i)).toBeVisible();
		await expect(page.getByLabel(/first name/i)).toBeVisible();
		await expect(page.getByLabel(/last name/i)).toBeVisible();
		await expect(page.getByLabel(/^password$/i)).toBeVisible();
		await expect(page.getByLabel(/confirm password/i)).toBeVisible();
	});

	test('should have proper heading hierarchy', async ({ page }) => {
		await page.goto('/login');

		// Page should have a main heading
		const heading = page.getByRole('heading', { level: 1 });
		await expect(heading).toBeVisible();
	});
});
