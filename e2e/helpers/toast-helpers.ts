import { Page } from '@playwright/test';

/**
 * Trigger a success toast notification
 * Works by mocking a successful API response that triggers a toast
 */
export async function triggerSuccessToast(page: Page, message: string = 'Success') {
	// This is a placeholder - actual implementation depends on how your app
	// triggers toasts. Common approaches:
	// 1. Complete a form submission that succeeds
	// 2. Call a function through page.evaluate()
	// 3. Trigger an API call that succeeds
	//
	// You'll need to implement this based on your actual app

	await page.evaluate((msg) => {
		// Dispatch custom event or call store method
		// window.dispatchEvent(new CustomEvent('show-toast', { detail: { type: 'success', message: msg } }));
	}, message);
}

/**
 * Trigger an error toast notification
 */
export async function triggerErrorToast(page: Page, message: string = 'Error occurred') {
	await page.evaluate((msg) => {
		// Dispatch custom event or call store method
		// window.dispatchEvent(new CustomEvent('show-toast', { detail: { type: 'error', message: msg } }));
	}, message);
}

/**
 * Trigger a warning toast notification
 */
export async function triggerWarningToast(page: Page, message: string = 'Warning') {
	await page.evaluate((msg) => {
		// Dispatch custom event or call store method
		// window.dispatchEvent(new CustomEvent('show-toast', { detail: { type: 'warning', message: msg } }));
	}, message);
}

/**
 * Trigger an info toast notification
 */
export async function triggerInfoToast(page: Page, message: string = 'Info') {
	await page.evaluate((msg) => {
		// Dispatch custom event or call store method
		// window.dispatchEvent(new CustomEvent('show-toast', { detail: { type: 'info', message: msg } }));
	}, message);
}

/**
 * Get count of visible toasts
 */
export async function getVisibleToastCount(page: Page): Promise<number> {
	const count = await page.locator('[role="status"], [role="alert"]').count();
	return count;
}

/**
 * Wait for toast to appear
 */
export async function waitForToast(page: Page, message?: string) {
	if (message) {
		await page.locator(`text=${message}`).waitFor({ state: 'visible', timeout: 5000 });
	} else {
		await page.locator('[role="status"], [role="alert"]').first().waitFor({
			state: 'visible',
			timeout: 5000
		});
	}
}
