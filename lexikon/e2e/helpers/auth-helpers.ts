import { Page } from '@playwright/test';

/**
 * Mock authentication state for tests
 * Sets up localStorage with authenticated user data
 */
export async function mockAuthState(page: Page, userData?: any) {
	const defaultUser = {
		id: 'test-user-1',
		email: 'test@example.com',
		first_name: 'Test',
		last_name: 'User',
		preferred_language: 'en'
	};

	const user = userData || defaultUser;

	await page.evaluate((userObj) => {
		localStorage.setItem(
			'lexikon-auth',
			JSON.stringify({
				user: userObj,
				accessToken: 'mock-token-12345',
				refreshToken: 'mock-refresh-token-12345',
				isAuthenticated: true,
				expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString()
			})
		);
	}, user);
}

/**
 * Clear all authentication state
 */
export async function clearAuthState(page: Page) {
	await page.evaluate(() => {
		localStorage.removeItem('lexikon-auth');
		localStorage.removeItem('lexikon-theme');
		localStorage.removeItem('lexikon-language');
	});
}

/**
 * Get current auth state from page
 */
export async function getAuthState(page: Page) {
	return await page.evaluate(() => {
		const auth = localStorage.getItem('lexikon-auth');
		return auth ? JSON.parse(auth) : null;
	});
}
