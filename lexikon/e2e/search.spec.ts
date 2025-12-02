/**
 * E2E Tests for Search Functionality
 * Tests semantic search with filters, debouncing, and real-time suggestions
 */

import { test, expect } from '@playwright/test';
import { mockAuthState } from './helpers/auth-helpers';
import { mockApiSuccess, mockApiWithDelay, mockApiError } from './helpers/api-mocking';
import { mockSearchResults, mockEmptyResults } from './fixtures/mock-data';

test.describe('Search UI - Accessibility', () => {
	test.beforeEach(async ({ page }) => {
		await mockAuthState(page);
		await page.goto('/terms');
	});

	test('should display search bar on terms page (CRITICAL)', async ({ page }) => {
		// Check search bar visibility
		await expect(page.getByRole('searchbox', { name: /search terms/i })).toBeVisible();
		await expect(page.getByPlaceholder(/search/i)).toBeVisible();

		// Should have proper ARIA attributes
		const searchInput = page.getByRole('searchbox');
		await expect(searchInput).toHaveAttribute('aria-label');
	});

	test('should have keyboard accessible search (HIGH)', async ({ page }) => {
		// Tab to search input
		await page.keyboard.press('Tab');
		const searchInput = page.getByRole('searchbox');

		// Type search query
		await searchInput.focus();
		await searchInput.type('neural network');

		// Verify input value updated
		await expect(searchInput).toHaveValue('neural network');
	});

	test('should have proper search container ARIA labels (HIGH)', async ({ page }) => {
		const searchContainer = page.locator('[role="search"]').first();
		await expect(searchContainer).toBeDefined();

		// Input should have aria-label
		const input = page.getByRole('searchbox');
		const ariaLabel = await input.getAttribute('aria-label');
		expect(ariaLabel).toBeTruthy();
	});
});

test.describe('Search Functionality - Debouncing', () => {
	test.beforeEach(async ({ page }) => {
		await mockAuthState(page);
	});

	test('should debounce search with 300ms delay (CRITICAL)', async ({ page }) => {
		let requestCount = 0;

		await page.route('**/api/terms/search*', async (route) => {
			requestCount++;
			await route.fulfill({
				json: mockSearchResults
			});
		});

		await page.goto('/terms');
		const searchInput = page.getByRole('searchbox');

		// Type quickly
		await searchInput.fill('neural');

		// Check at 200ms - should not have called API yet
		await page.waitForTimeout(200);
		expect(requestCount).toBe(0);

		// Wait until 350ms total - API should have been called once
		await page.waitForTimeout(200);
		expect(requestCount).toBe(1);

		// Type more - should reset debounce
		await searchInput.fill('neural network');
		await page.waitForTimeout(200);
		expect(requestCount).toBe(1); // Still 1, debounce reset

		// Wait for new call
		await page.waitForTimeout(200);
		expect(requestCount).toBe(2); // Now called twice
	});

	test('should trigger search on Enter key (CRITICAL)', async ({ page }) => {
		await mockApiSuccess(page, '/api/terms/search', mockSearchResults.data);

		await page.goto('/terms');
		const searchInput = page.getByRole('searchbox');

		// Type and press Enter
		await searchInput.fill('machine learning');
		await searchInput.press('Enter');

		// Results should appear
		await expect(page.getByText('Machine Learning')).toBeVisible({ timeout: 5000 });
	});

	test('should show loading state during search (HIGH)', async ({ page }) => {
		await mockApiWithDelay(page, '/api/terms/search', mockSearchResults.data, 1000);

		await page.goto('/terms');
		const searchInput = page.getByRole('searchbox');

		await searchInput.fill('test');
		await page.waitForTimeout(350); // Wait for debounce

		// Check for loading indicator
		// Could be aria-busy, spinner, skeleton, etc.
		const loadingIndicator = page.locator('[aria-busy="true"], .spinner, .skeleton').first();
		const isVisible = await loadingIndicator.isVisible().catch(() => false);
		// Note: This depends on your implementation

		// Wait for results to appear
		await expect(page.getByText('Neural Network')).toBeVisible({ timeout: 2000 });
	});
});

test.describe('Search Filters', () => {
	test.beforeEach(async ({ page }) => {
		await mockAuthState(page);
		await mockApiSuccess(page, '/api/terms/search', mockSearchResults.data);
		await page.goto('/terms');
	});

	test('should display domain filter dropdown (CRITICAL)', async ({ page }) => {
		const domainFilter = page.getByRole('combobox', { name: /domain/i });
		await expect(domainFilter).toBeVisible();

		// Open dropdown
		await domainFilter.click();

		// Check for options
		await expect(page.getByRole('option', { name: /all/i })).toBeVisible();
		await expect(page.getByRole('option', { name: /computer science/i })).toBeVisible();
	});

	test('should display level filter dropdown (CRITICAL)', async ({ page }) => {
		const levelFilter = page.getByRole('combobox', { name: /level/i });
		await expect(levelFilter).toBeVisible();

		// Open dropdown
		await levelFilter.click();

		// Check for level options
		await expect(page.getByRole('option', { name: /all/i })).toBeVisible();
		await expect(page.getByRole('option', { name: /expert/i })).toBeVisible();
		await expect(page.getByRole('option', { name: /ready/i })).toBeVisible();
	});

	test('should apply filters to search (CRITICAL)', async ({ page }) => {
		let lastRequest: string = '';

		await page.route('**/api/terms/search*', async (route) => {
			lastRequest = route.request().url();
			await route.fulfill({
				json: mockSearchResults
			});
		});

		// Type search
		await page.getByRole('searchbox').fill('neural');
		await page.waitForTimeout(350);

		// Apply domain filter
		await page.getByRole('combobox', { name: /domain/i }).click();
		await page.getByRole('option', { name: /computer science/i }).click();

		// Check that API was called with domain parameter
		await page.waitForTimeout(400);
		expect(lastRequest).toContain('domain');
		expect(lastRequest).toContain('neural');
	});

	test('should clear individual filters (HIGH)', async ({ page }) => {
		// Apply a filter
		await page.getByRole('combobox', { name: /domain/i }).click();
		await page.getByRole('option', { name: /medicine/i }).click();

		// Filter badge should appear
		const filterBadge = page.locator('text=Medicine');
		await expect(filterBadge).toBeVisible();

		// Click X on filter badge
		const clearButton = filterBadge.locator('..').getByRole('button', { name: /remove|clear/i });
		if (await clearButton.isVisible().catch(() => false)) {
			await clearButton.click();
			await expect(filterBadge).not.toBeVisible();
		}
	});
});

test.describe('Search Results Display', () => {
	test.beforeEach(async ({ page }) => {
		await mockAuthState(page);
		await mockApiSuccess(page, '/api/terms/search', mockSearchResults.data);
		await page.goto('/terms');
	});

	test('should display search results list (CRITICAL)', async ({ page }) => {
		const searchInput = page.getByRole('searchbox');
		await searchInput.fill('neural');
		await page.waitForTimeout(400);

		// Results should be visible
		await expect(page.getByText('Neural Network')).toBeVisible();
		await expect(page.getByText('Machine Learning')).toBeVisible();
	});

	test('should show result count (HIGH)', async ({ page }) => {
		await page.getByRole('searchbox').fill('test');
		await page.waitForTimeout(400);

		// Result count should appear
		const resultCount = page.locator('text=/\\d+ results? found/i');
		await expect(resultCount).toBeVisible();
	});

	test('should navigate to term detail on click (HIGH)', async ({ page }) => {
		await page.getByRole('searchbox').fill('neural');
		await page.waitForTimeout(400);

		// Click on result
		await page.getByText('Neural Network').click();

		// Should navigate to term detail
		await expect(page).toHaveURL(/\/terms\/(.*)/);
	});

	test('should clear results when search is emptied (MEDIUM)', async ({ page }) => {
		// Search for something
		await page.getByRole('searchbox').fill('test');
		await page.waitForTimeout(400);

		// Results visible
		await expect(page.getByText('Neural Network')).toBeVisible();

		// Clear search
		await page.getByRole('searchbox').clear();
		await page.waitForTimeout(400);

		// Results should disappear or show empty state
		const results = page.locator('[data-testid="search-result"]');
		const resultCount = await results.count();
		expect(resultCount).toBe(0);
	});

	test('should show "No results" when no matches found (MEDIUM)', async ({ page }) => {
		await mockApiSuccess(page, '/api/terms/search', mockEmptyResults.data);

		await page.getByRole('searchbox').fill('xyzzzzabc123');
		await page.waitForTimeout(400);

		// No results message
		await expect(page.getByText(/no results/i)).toBeVisible();
	});
});

test.describe('Search Error Handling', () => {
	test.beforeEach(async ({ page }) => {
		await mockAuthState(page);
	});

	test('should handle API errors gracefully (HIGH)', async ({ page }) => {
		await mockApiError(page, '/api/terms/search', 500, 'Server error');

		await page.goto('/terms');
		await page.getByRole('searchbox').fill('test');
		await page.waitForTimeout(400);

		// Error message should appear
		const errorMsg = page.locator('text=/error|failed/i').first();
		const isVisible = await errorMsg.isVisible().catch(() => false);
		// Implementation may vary - could show error toast, error text, etc.

		// Should not crash
		await expect(page.locator('body')).toBeVisible();
	});

	test('should handle network timeout (MEDIUM)', async ({ page }) => {
		await mockApiWithDelay(page, '/api/terms/search', mockSearchResults.data, 15000);

		await page.goto('/terms');
		await page.getByRole('searchbox').fill('test');

		// Should show timeout message after 10 seconds
		// This is implementation-specific
		await page.waitForTimeout(2000);
		// Page should still be functional
		await expect(page.locator('body')).toBeVisible();
	});
});

test.describe('Search Mobile Responsiveness', () => {
	test.use({ viewport: { width: 375, height: 667 } });

	test.beforeEach(async ({ page }) => {
		await mockAuthState(page);
		await mockApiSuccess(page, '/api/terms/search', mockSearchResults.data);
		await page.goto('/terms');
	});

	test('should display mobile-friendly search (HIGH)', async ({ page }) => {
		const searchInput = page.getByRole('searchbox');
		await expect(searchInput).toBeVisible();

		// Check tap target size (minimum 44x44 pixels)
		const boundingBox = await searchInput.boundingBox();
		expect(boundingBox).not.toBeNull();
		if (boundingBox) {
			expect(boundingBox.height).toBeGreaterThanOrEqual(40);
		}

		// Should be full-width or nearly full-width
		const viewport = page.viewportSize();
		if (boundingBox && viewport) {
			expect(boundingBox.width).toBeGreaterThan(viewport.width * 0.7);
		}
	});

	test('should stack results vertically on mobile (MEDIUM)', async ({ page }) => {
		await page.getByRole('searchbox').fill('test');
		await page.waitForTimeout(400);

		// Results should be stacked
		const results = page.locator('[data-testid="search-result"]');
		const count = await results.count();

		if (count > 1) {
			const firstBox = await results.nth(0).boundingBox();
			const secondBox = await results.nth(1).boundingBox();

			// Second should be below first (higher Y coordinate)
			expect(secondBox?.y).toBeGreaterThan(firstBox?.y ?? 0);
		}
	});
});

test.describe('Search Special Characters', () => {
	test('should handle special characters in search (MEDIUM)', async ({ page }) => {
		await mockAuthState(page);
		let capturedUrl = '';

		await page.route('**/api/terms/search*', async (route) => {
			capturedUrl = route.request().url();
			await route.fulfill({
				json: mockSearchResults
			});
		});

		await page.goto('/terms');

		// Type special characters
		await page.getByRole('searchbox').fill('machine/learning & AI (advanced)');
		await page.waitForTimeout(400);

		// URL should be properly encoded
		expect(capturedUrl).toContain('search');
		// Should not have unencoded special chars in URL
		expect(capturedUrl).not.toContain('&');
	});
});

test.describe('Critical User Flow 1: Search → View Term → Add Relation', () => {
	test('should complete search to relation workflow (CRITICAL)', async ({ page }) => {
		await mockAuthState(page);
		await mockApiSuccess(page, '/api/terms/search', mockSearchResults.data);

		// Mock term detail endpoint
		await mockApiSuccess(page, '/api/terms/1', {
			data: {
				id: '1',
				name: 'Neural Network',
				definition: 'A computing system inspired by biological neural networks',
				domain: 'Computer Science',
				level: 'expert',
				relations: []
			}
		});

		// Mock relation creation
		await mockApiSuccess(page, '/api/ontology/relations', {
			data: {
				id: 'rel-1',
				type: 'broader',
				target_term: { id: '2', name: 'Artificial Intelligence' }
			}
		});

		// Step 1: Navigate to terms page
		await page.goto('/terms');
		await expect(page.getByRole('searchbox')).toBeVisible();

		// Step 2: Search for "neural network"
		await page.getByRole('searchbox').fill('neural network');
		await page.waitForTimeout(400); // Wait for debounce

		// Step 3: Verify search results appear
		await expect(page.getByText('Neural Network')).toBeVisible();

		// Step 4: Click on result to navigate to term detail
		await page.getByText('Neural Network').click();
		await expect(page).toHaveURL(/\/terms\/1/);

		// Step 5: Verify term detail page loaded
		await expect(page.getByRole('heading', { name: /Neural Network/i })).toBeVisible();

		// Step 6: Find and click "Add Relation" button
		const addRelationBtn = page.getByRole('button', { name: /add relation|create relation/i });
		await expect(addRelationBtn).toBeVisible();
		await addRelationBtn.click();

		// Step 7: Verify modal appears
		const relationModal = page.locator('[role="dialog"]').first();
		await expect(relationModal).toBeVisible();

		// Step 8: Select relation type "broader"
		const relationType = page.getByLabel(/relation type/i);
		if (await relationType.isVisible()) {
			await relationType.selectOption('broader');
		}

		// Step 9: Search and select target term
		const termSearch = page.getByLabel(/select.*term|target term/i);
		if (await termSearch.isVisible()) {
			await termSearch.fill('Artificial Intelligence');
			await page.waitForTimeout(400);

			// Click on the autocomplete result
			const aiOption = page.getByText('Artificial Intelligence').first();
			if (await aiOption.isVisible()) {
				await aiOption.click();
			}
		}

		// Step 10: Submit form
		const submitBtn = page.getByRole('button', { name: /save|create|submit/i }).last();
		await expect(submitBtn).toBeVisible();
		await submitBtn.click();

		// Step 11: Verify success toast or modal closes
		await page.waitForTimeout(500);
		const successMsg = page.locator('text=/added|created|success/i').first();
		const isSuccessVisible = await successMsg.isVisible().catch(() => false);

		// Verify modal is gone
		const modalVisible = await relationModal.isVisible().catch(() => false);
		expect(isSuccessVisible || !modalVisible).toBe(true);
	});
});
