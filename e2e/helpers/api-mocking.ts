import { Page, Route } from '@playwright/test';

/**
 * Mock a successful API response
 */
export async function mockApiSuccess(page: Page, endpoint: string, data: any, options?: any) {
	await page.route(`**${endpoint}*`, async (route: Route) => {
		// Only intercept GET and POST requests by default
		if (['GET', 'POST', 'PUT', 'DELETE'].includes(route.request().method())) {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				json: {
					success: true,
					data: data
				},
				...options
			});
		} else {
			await route.continue();
		}
	});
}

/**
 * Mock an API error response
 */
export async function mockApiError(
	page: Page,
	endpoint: string,
	status: number = 500,
	errorMessage: string = 'Internal Server Error'
) {
	await page.route(`**${endpoint}*`, async (route: Route) => {
		await route.fulfill({
			status: status,
			contentType: 'application/json',
			json: {
				success: false,
				error: {
					message: errorMessage,
					code: `ERROR_${status}`
				}
			}
		});
	});
}

/**
 * Mock API with delay (to test loading states)
 */
export async function mockApiWithDelay(
	page: Page,
	endpoint: string,
	data: any,
	delayMs: number = 1000
) {
	await page.route(`**${endpoint}*`, async (route: Route) => {
		await new Promise((resolve) => setTimeout(resolve, delayMs));
		await route.fulfill({
			status: 200,
			contentType: 'application/json',
			json: {
				success: true,
				data: data
			}
		});
	});
}

/**
 * Clear all route mocks
 */
export async function clearMocks(page: Page) {
	await page.unroute('**/*');
}

/**
 * Wait for API call and assert request body/params
 */
export async function waitForApiCall(
	page: Page,
	endpoint: string,
	timeout: number = 5000
): Promise<any> {
	return page.waitForResponse(
		(response) => response.url().includes(endpoint),
		{ timeout }
	);
}
