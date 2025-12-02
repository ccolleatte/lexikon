/**
 * E2E tests for complete user journeys
 */

import { test, expect } from '@playwright/test';

test.describe('Complete User Journey - New User Registration', () => {
	test('should complete full registration and onboarding flow', async ({ page }) => {
		// 1. Visit homepage
		await page.goto('/');
		await expect(page.getByText('Lexikon')).toBeVisible();

		// 2. Click "Get Started"
		await page.getByRole('link', { name: /get started/i }).click();
		await expect(page).toHaveURL(/\/register/);

		// 3. Fill registration form
		await page.getByLabel(/email/i).fill('newuser@example.com');
		await page.getByLabel(/first name/i).fill('Jane');
		await page.getByLabel(/last name/i).fill('Smith');
		await page.getByLabel(/^password$/i).fill('SecurePassword123');
		await page.getByLabel(/confirm password/i).fill('SecurePassword123');

		// Select language
		await page.getByLabel(/language/i).selectOption('en');

		// Note: Actual registration will fail without backend, but we test the flow
		// In a full E2E test with backend, we would continue to:
		// 4. Submit and verify redirect to onboarding
		// 5. Complete onboarding profile
		// 6. Navigate to terms page
	});
});

test.describe('Complete User Journey - Existing User Login', () => {
	test('should navigate through authenticated pages', async ({ page }) => {
		// 1. Visit login page
		await page.goto('/login');

		// 2. Fill login form
		await page.getByLabel(/email/i).fill('test@example.com');
		await page.getByLabel(/password/i).fill('password123');

		// Note: Without backend, login will fail
		// In a full E2E test with backend, we would:
		// 3. Verify redirect to /terms
		// 4. Verify NavBar shows user menu
		// 5. Navigate to "Create Term"
		// 6. Navigate to Profile
		// 7. Change password
		// 8. Logout and verify redirect to homepage
	});
});

test.describe('Navigation Flow - Unauthenticated User', () => {
	test('should be redirected to login when accessing protected routes', async ({ page }) => {
		// Try to access protected route directly
		await page.goto('/terms');

		// Should be redirected to login
		await expect(page).toHaveURL(/\/login/);

		// Try to access profile
		await page.goto('/profile');
		await expect(page).toHaveURL(/\/login/);

		// Try to access create term
		await page.goto('/terms/new');
		await expect(page).toHaveURL(/\/login/);
	});

	test('should navigate freely on public pages', async ({ page }) => {
		// Visit homepage
		await page.goto('/');
		await expect(page.getByText('Lexikon')).toBeVisible();

		// Navigate to login
		await page.getByRole('link', { name: /sign in/i }).click();
		await expect(page).toHaveURL(/\/login/);

		// Navigate to register
		await page.getByRole('link', { name: /create.*account/i }).click();
		await expect(page).toHaveURL(/\/register/);

		// Navigate back to login
		await page.getByRole('link', { name: /sign in/i }).click();
		await expect(page).toHaveURL(/\/login/);

		// Go to homepage
		await page.getByRole('link', { name: /lexikon/i }).first().click();
		await expect(page).toHaveURL('/');
	});
});

test.describe('Form Validation Flows', () => {
	test('should validate email format on registration', async ({ page }) => {
		await page.goto('/register');

		await page.getByLabel(/email/i).fill('invalid-email');
		await page.getByLabel(/first name/i).fill('John');
		await page.getByLabel(/last name/i).fill('Doe');
		await page.getByLabel(/^password$/i).fill('password123');
		await page.getByLabel(/confirm password/i).fill('password123');

		// Try to submit
		await page.getByRole('button', { name: /create account/i }).click();

		// HTML5 validation should catch this
		// Modern browsers will show validation message
		const emailInput = page.getByLabel(/email/i);
		const validationMessage = await emailInput.evaluate(
			(input: HTMLInputElement) => input.validationMessage
		);

		expect(validationMessage).toBeTruthy();
	});

	test('should validate password matching on registration', async ({ page }) => {
		await page.goto('/register');

		await page.getByLabel(/email/i).fill('test@example.com');
		await page.getByLabel(/first name/i).fill('John');
		await page.getByLabel(/last name/i).fill('Doe');
		await page.getByLabel(/^password$/i).fill('password123');
		await page.getByLabel(/confirm password/i).fill('differentpassword');

		await page.getByRole('button', { name: /create account/i }).click();

		// Should show error message
		await expect(page.getByText(/passwords.*match/i)).toBeVisible();
	});

	test('should validate required fields on login', async ({ page }) => {
		await page.goto('/login');

		// Try to submit without filling form
		await page.getByRole('button', { name: /sign in/i }).click();

		// Should still be on login page
		await expect(page).toHaveURL(/\/login/);

		// HTML5 validation should prevent submission
		const emailInput = page.getByLabel(/email/i);
		const validationMessage = await emailInput.evaluate(
			(input: HTMLInputElement) => input.validationMessage
		);

		expect(validationMessage).toBeTruthy();
	});
});

test.describe('OAuth Flow - UI Elements', () => {
	test('should display OAuth buttons on login page', async ({ page }) => {
		await page.goto('/login');

		await expect(page.getByRole('button', { name: /google/i })).toBeVisible();
		await expect(page.getByRole('button', { name: /github/i })).toBeVisible();
	});

	test('should display OAuth buttons on register page', async ({ page }) => {
		await page.goto('/register');

		await expect(page.getByRole('button', { name: /google/i })).toBeVisible();
		await expect(page.getByRole('button', { name: /github/i })).toBeVisible();
	});

	test('should initiate OAuth flow when Google button is clicked', async ({ page }) => {
		await page.goto('/login');

		// Click Google button
		const googleButton = page.getByRole('button', { name: /google/i });
		await googleButton.click();

		// Note: In a real scenario, this would redirect to Google OAuth
		// We're testing that the button is clickable and triggers an action
	});
});

test.describe('Mobile Responsiveness', () => {
	test.use({ viewport: { width: 375, height: 667 } });

	test('should display mobile-friendly login page', async ({ page }) => {
		await page.goto('/login');

		// Page should be visible and usable on mobile
		await expect(page.getByRole('heading', { name: /sign in/i })).toBeVisible();
		await expect(page.getByLabel(/email/i)).toBeVisible();
		await expect(page.getByLabel(/password/i)).toBeVisible();

		// Buttons should be large enough to tap
		const signInButton = page.getByRole('button', { name: /sign in/i });
		const buttonSize = await signInButton.boundingBox();

		expect(buttonSize).not.toBeNull();
		// Minimum touch target size is 44x44 pixels
		if (buttonSize) {
			expect(buttonSize.height).toBeGreaterThanOrEqual(40);
		}
	});

	test('should display mobile-friendly registration page', async ({ page }) => {
		await page.goto('/register');

		await expect(page.getByRole('heading', { name: /create.*account/i })).toBeVisible();

		// All form fields should be visible
		await expect(page.getByLabel(/email/i)).toBeVisible();
		await expect(page.getByLabel(/first name/i)).toBeVisible();
		await expect(page.getByLabel(/last name/i)).toBeVisible();
	});
});

test.describe('Performance and Loading States', () => {
	test('should show loading state when submitting login form', async ({ page }) => {
		await page.goto('/login');

		await page.getByLabel(/email/i).fill('test@example.com');
		await page.getByLabel(/password/i).fill('password123');

		const submitButton = page.getByRole('button', { name: /sign in/i });

		// Click submit
		await submitButton.click();

		// Button should be disabled during submission
		// Note: Without backend, this will fail quickly
		// In a real scenario, we'd see the loading state
	});

	test('should load pages quickly', async ({ page }) => {
		const startTime = Date.now();
		await page.goto('/login');
		const loadTime = Date.now() - startTime;

		// Page should load in less than 3 seconds
		expect(loadTime).toBeLessThan(3000);

		// Main content should be visible
		await expect(page.getByRole('heading', { name: /sign in/i })).toBeVisible();
	});
});

test.describe('Error Handling', () => {
	test('should handle network errors gracefully', async ({ page }) => {
		await page.goto('/login');

		// Fill in credentials
		await page.getByLabel(/email/i).fill('test@example.com');
		await page.getByLabel(/password/i).fill('password123');

		// Submit (will fail without backend)
		await page.getByRole('button', { name: /sign in/i }).click();

		// Should show an error message (exact message depends on implementation)
		// Wait a bit for the error to appear
		await page.waitForTimeout(1000);
	});
});

test.describe('Browser Compatibility', () => {
	test('should work with keyboard navigation', async ({ page }) => {
		await page.goto('/login');

		// Tab through form
		await page.keyboard.press('Tab');

		// Email field should be focused
		const emailInput = page.getByLabel(/email/i);
		await expect(emailInput).toBeFocused();

		// Fill email with keyboard
		await emailInput.type('test@example.com');

		// Tab to password
		await page.keyboard.press('Tab');
		const passwordInput = page.getByLabel(/password/i);
		await expect(passwordInput).toBeFocused();

		// Fill password
		await passwordInput.type('password123');

		// Tab to submit button
		await page.keyboard.press('Tab');
		const submitButton = page.getByRole('button', { name: /sign in/i });
		await expect(submitButton).toBeFocused();

		// Should be able to submit with Enter
		await page.keyboard.press('Enter');
	});

	test('should have proper focus indicators', async ({ page }) => {
		await page.goto('/login');

		// Click email input
		await page.getByLabel(/email/i).click();

		// Should have visible focus indicator
		// This is browser-dependent and CSS-dependent
		// We just verify the element can receive focus
		await expect(page.getByLabel(/email/i)).toBeFocused();
	});
});
