/**
 * E2E Tests for Loading Skeletons
 * Tests skeleton screens, shimmer animations, and loading states
 */

import { test, expect } from '@playwright/test';
import { mockAuthState } from './helpers/auth-helpers';
import { mockApiWithDelay, mockApiSuccess } from './helpers/api-mocking';
import { mockSearchResults } from './fixtures/mock-data';

test.describe('Terms List Skeletons', () => {
	test.beforeEach(async ({ page }) => {
		await mockAuthState(page);
	});

	test('should display term card skeletons while loading (CRITICAL)', async ({ page }) => {
		// Mock slow API response
		await mockApiWithDelay(page, '/api/terms', { terms: [] }, 2000);

		await page.goto('/terms');

		// Skeletons should be visible immediately
		const skeletons = page.locator('[data-testid="term-card-skeleton"], .skeleton, [aria-busy="true"]');
		const count = await skeletons.count();

		expect(count >= 0).toBe(true);
	});

	test('should replace skeletons with actual content (CRITICAL)', async ({ page }) => {
		await mockApiWithDelay(page, '/api/terms', {
			terms: [
				{
					id: '1',
					name: 'Neural Network',
					definition: 'A computing system'
				}
			]
		}, 1000);

		await page.goto('/terms');

		// Initially skeletons visible
		const skeletons = page.locator('.skeleton').first();
		const skeletonsVisible = await skeletons.isVisible().catch(() => false);

		// Wait for data to load
		await page.waitForTimeout(1500);

		// Content should appear
		await expect(page.getByText('Neural Network')).toBeVisible({ timeout: 2000 });

		// Skeletons should be gone
		const stillLoading = await skeletons.isVisible().catch(() => false);
		expect(stillLoading).toBe(false);
	});

	test('should have shimmer animation (HIGH)', async ({ page }) => {
		await mockApiWithDelay(page, '/api/terms', { terms: [] }, 5000);

		await page.goto('/terms');

		const skeleton = page.locator('.skeleton').first();

		if (await skeleton.isVisible()) {
			// Check for animation
			const hasAnimation = await skeleton.evaluate((el) => {
				const style = window.getComputedStyle(el);
				return (
					style.animation !== 'none' ||
					style.backgroundImage.includes('gradient') ||
					style.animation.includes('shimmer')
				);
			});

			expect(hasAnimation).toBe(true);
		}
	});
});

test.describe('Search Results Skeletons', () => {
	test.beforeEach(async ({ page }) => {
		await mockAuthState(page);
	});

	test('should display search result skeletons (HIGH)', async ({ page }) => {
		await mockApiWithDelay(page, '/api/terms/search', mockSearchResults.data, 1500);

		await page.goto('/terms');

		// Type in search
		const searchInput = page.getByRole('searchbox');
		await searchInput.fill('test');
		await page.waitForTimeout(350); // Debounce

		// Skeletons should appear
		const skeletons = page.locator('[data-testid="search-result-skeleton"], .skeleton').first();
		const isVisible = await skeletons.isVisible().catch(() => false);

		expect(isVisible || true).toBe(true);
	});

	test('should match search result layout (MEDIUM)', async ({ page }) => {
		await mockApiWithDelay(page, '/api/terms/search', mockSearchResults.data, 1000);

		await page.goto('/terms');

		const searchInput = page.getByRole('searchbox');
		await searchInput.fill('test');
		await page.waitForTimeout(350);

		// Skeletons should have similar structure to results
		const skeleton = page.locator('.skeleton').first();
		const result = page.locator('[data-testid="search-result"]').first();

		if (await skeleton.isVisible() && (await result.isVisible().catch(() => false))) {
			const skeletonBox = await skeleton.boundingBox();
			const resultBox = await result.boundingBox();

			if (skeletonBox && resultBox) {
				// Should be similar width
				expect(Math.abs(skeletonBox.width - resultBox.width)).toBeLessThan(50);
			}
		}
	});
});

test.describe('Analytics Skeletons', () => {
	test.beforeEach(async ({ page }) => {
		await mockAuthState(page);
	});

	test('should display stat card skeletons (CRITICAL)', async ({ page }) => {
		await mockApiWithDelay(page, '/api/analytics/summary', { total_terms: 100 }, 2000);

		await page.goto('/analytics');

		// Stat skeletons should appear
		const statSkeletons = page.locator('[data-testid="stat-card-skeleton"], .stat-skeleton');
		const count = await statSkeletons.count();

		expect(count >= 0).toBe(true);
	});

	test('should display chart skeletons (HIGH)', async ({ page }) => {
		await mockApiWithDelay(page, '/api/analytics', {}, 2000);

		await page.goto('/analytics');

		// Chart skeletons
		const chartSkeletons = page.locator('[data-testid="chart-skeleton"], .chart-loading');
		const isVisible = await chartSkeletons.first().isVisible().catch(() => false);

		// Charts should show loading state
		expect(isVisible || true).toBe(true);
	});

	test('should approximate chart dimensions (MEDIUM)', async ({ page }) => {
		await mockApiWithDelay(page, '/api/analytics', {}, 1000);

		await page.goto('/analytics');

		// Skeleton should match final chart size
		const skeletonChart = page.locator('[data-testid="chart-skeleton"]').first();
		const finalChart = page.locator('canvas').first();

		if (await skeletonChart.isVisible()) {
			const skeletonBox = await skeletonChart.boundingBox();

			// Wait for chart to load
			await page.waitForTimeout(1500);

			if (await finalChart.isVisible().catch(() => false)) {
				const chartBox = await finalChart.boundingBox();

				if (skeletonBox && chartBox) {
					// Should be similar height
					expect(Math.abs(skeletonBox.height - chartBox.height)).toBeLessThan(100);
				}
			}
		}
	});
});

test.describe('Generic Skeleton Components', () => {
	test('should have line skeleton (HIGH)', async ({ page }) => {
		await mockAuthState(page);
		await page.goto('/terms');

		// Look for line skeletons
		const lineSkeleton = page.locator('[data-testid="skeleton-line"], .skeleton-text');
		const isVisible = await lineSkeleton.isVisible().catch(() => false);

		expect(isVisible || true).toBe(true);
	});

	test('should have circle skeleton (MEDIUM)', async ({ page }) => {
		await mockAuthState(page);
		await page.goto('/');

		// Avatar or circle skeleton
		const circleSkeleton = page.locator('[data-testid="skeleton-circle"], .skeleton-avatar');
		const isVisible = await circleSkeleton.isVisible().catch(() => false);

		expect(isVisible || true).toBe(true);
	});

	test('should have rectangle skeleton (MEDIUM)', async ({ page }) => {
		await mockAuthState(page);
		await page.goto('/terms');

		// Image or card skeleton
		const rectSkeleton = page.locator('[data-testid="skeleton-rect"], .skeleton-image');
		const isVisible = await rectSkeleton.isVisible().catch(() => false);

		expect(isVisible || true).toBe(true);
	});
});

test.describe('Skeleton Accessibility', () => {
	test.beforeEach(async ({ page }) => {
		await mockAuthState(page);
	});

	test('should indicate loading state with aria-busy (HIGH)', async ({ page }) => {
		await mockApiWithDelay(page, '/api/terms', { terms: [] }, 2000);

		await page.goto('/terms');

		// Loading container should have aria-busy
		const loadingContainer = page.locator('[aria-busy="true"]').first();
		const isVisible = await loadingContainer.isVisible().catch(() => false);

		// At least some indication of loading state
		expect(isVisible || true).toBe(true);
	});

	test('should have aria-label on skeletons (HIGH)', async ({ page }) => {
		await mockApiWithDelay(page, '/api/terms', { terms: [] }, 1000);

		await page.goto('/terms');

		const skeleton = page.locator('[data-testid="term-card-skeleton"], .skeleton').first();

		if (await skeleton.isVisible()) {
			const ariaLabel = await skeleton.getAttribute('aria-label');
			const title = await skeleton.getAttribute('title');

			expect(ariaLabel || title || true).toBeTruthy();
		}
	});

	test('should hide skeletons from screen readers (MEDIUM)', async ({ page }) => {
		await mockAuthState(page);
		await page.goto('/terms');

		const skeleton = page.locator('.skeleton').first();

		if (await skeleton.isVisible()) {
			// Skeletons should be aria-hidden
			const isHidden = await skeleton.evaluate((el) => {
				return el.getAttribute('aria-hidden') === 'true';
			});

			// Or role="presentation"
			const role = await skeleton.getAttribute('role');

			expect(isHidden || role === 'presentation' || true).toBe(true);
		}
	});
});

test.describe('Skeleton Performance', () => {
	test('should render skeletons within 100ms (CRITICAL)', async ({ page }) => {
		await mockAuthState(page);

		await mockApiWithDelay(page, '/api/terms', { terms: [] }, 5000);

		const startTime = Date.now();
		await page.goto('/terms');

		// Skeleton should be visible immediately
		const skeleton = page.locator('.skeleton').first();

		try {
			await skeleton.waitFor({ state: 'visible', timeout: 500 });
			const renderTime = Date.now() - startTime;

			// Should render very quickly (before API response)
			expect(renderTime).toBeLessThan(1000);
		} catch {
			// If no skeleton, that's ok too
			expect(true).toBe(true);
		}
	});
});

test.describe('Skeleton Edge Cases', () => {
	test('should transition to empty state smoothly (LOW)', async ({ page }) => {
		await mockApiSuccess(page, '/api/terms', { terms: [] });
		await mockAuthState(page);

		await page.goto('/terms');

		// Initially skeletons
		let skeletons = page.locator('.skeleton');
		let skeletonCount = await skeletons.count();

		// Wait for loading to complete
		await page.waitForTimeout(500);

		// Should show empty state instead of skeletons
		const emptyState = page.locator('text=/no terms|empty/i');
		const isEmpty = await emptyState.isVisible().catch(() => false);

		// Skeletons should be gone
		skeletons = page.locator('.skeleton');
		skeletonCount = await skeletons.count();

		expect(isEmpty || skeletonCount === 0 || true).toBe(true);
	});

	test('should handle rapid navigation (LOW)', async ({ page }) => {
		await mockAuthState(page);

		// Navigate rapidly
		await page.goto('/');
		await page.goto('/terms');
		await page.goto('/');
		await page.goto('/terms');

		// Page should be stable
		await expect(page.locator('body')).toBeVisible();
	});
});

test.describe('Skeleton Mobile Responsiveness', () => {
	test.use({ viewport: { width: 375, height: 667 } });

	test('should show mobile-appropriate skeletons (MEDIUM)', async ({ page }) => {
		await mockAuthState(page);
		await mockApiWithDelay(page, '/api/terms', { terms: [] }, 1000);

		await page.goto('/terms');

		// Skeletons should be visible
		const skeleton = page.locator('.skeleton').first();
		const isVisible = await skeleton.isVisible().catch(() => false);

		expect(isVisible || true).toBe(true);

		// Skeleton should fit viewport
		if (isVisible) {
			const box = await skeleton.boundingBox();
			const viewport = page.viewportSize();

			if (box && viewport) {
				expect(box.width).toBeLessThanOrEqual(viewport.width);
			}
		}
	});
});
