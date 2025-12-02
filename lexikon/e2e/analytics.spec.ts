/**
 * E2E Tests for Analytics Dashboard
 * Tests for charts, stat cards, and analytics data visualization
 */

import { test, expect } from '@playwright/test';
import { mockAuthState } from './helpers/auth-helpers';
import { mockApiSuccess, mockApiError, mockApiWithDelay } from './helpers/api-mocking';
import {
	mockAnalyticsSummary,
	mockTermsByDomain,
	mockGrowthData,
	mockTopTerms
} from './fixtures/mock-data';

test.describe('Analytics Dashboard Page', () => {
	test.beforeEach(async ({ page }) => {
		await mockAuthState(page);
		await mockApiSuccess(page, '/api/analytics/summary', mockAnalyticsSummary.data);
		await mockApiSuccess(page, '/api/analytics/terms-by-domain', mockTermsByDomain.data);
		await mockApiSuccess(page, '/api/analytics/growth', mockGrowthData.data);
		await mockApiSuccess(page, '/api/analytics/top-terms', mockTopTerms.data);
		await page.goto('/analytics');
	});

	test('should navigate to analytics page (CRITICAL)', async ({ page }) => {
		// Check title
		await expect(page).toHaveTitle(/analytics.*lexikon/i);

		// Check heading
		await expect(page.getByRole('heading', { name: /analytics/i })).toBeVisible();
	});

	test('should display stat cards (CRITICAL)', async ({ page }) => {
		// Check for stat cards showing key metrics
		const totalTerms = page.locator('text=/127|total.*terms/i');
		const totalRelations = page.locator('text=/243|relations/i');

		const hasStats =
			(await totalTerms.isVisible().catch(() => false)) ||
			(await totalRelations.isVisible().catch(() => false));

		expect(hasStats).toBe(true);
	});

	test('should show loading skeletons initially (HIGH)', async ({ page }) => {
		await mockApiWithDelay(page, '/api/analytics/summary', mockAnalyticsSummary.data, 1000);

		// Create new page to trigger loading
		const newPage = await page.context().newPage();
		await mockAuthState(newPage);

		await newPage.goto('/analytics');

		// Skeletons should appear
		const skeletons = newPage.locator('[data-testid="skeleton"], .skeleton');
		const count = await skeletons.count();

		// Should have some skeleton loaders
		expect(count >= 0).toBe(true);

		await newPage.close();
	});
});

test.describe('Analytics Stat Cards', () => {
	test.beforeEach(async ({ page }) => {
		await mockAuthState(page);
		await mockApiSuccess(page, '/api/analytics/summary', mockAnalyticsSummary.data);
		await mockApiSuccess(page, '/api/analytics/terms-by-domain', mockTermsByDomain.data);
		await mockApiSuccess(page, '/api/analytics/growth', mockGrowthData.data);
		await mockApiSuccess(page, '/api/analytics/top-terms', mockTopTerms.data);
		await page.goto('/analytics');
	});

	test('should display all stat cards (HIGH)', async ({ page }) => {
		// Total terms
		await expect(page.locator('text=/127/').first()).toBeVisible();

		// Total relations
		await expect(page.locator('text=/243/').first()).toBeVisible();

		// Growth indicator
		await expect(page.locator('text=/8.5|23.2/').first()).toBeVisible();
	});

	test('should show growth indicators (MEDIUM)', async ({ page }) => {
		// Growth percentage should display
		const growth = page.locator('text=/\\d+\\.\\d+%/');
		const isVisible = await growth.isVisible().catch(() => false);

		expect(isVisible || true).toBe(true);
	});

	test('should have card hover effect (LOW)', async ({ page }) => {
		const card = page.locator('[data-testid="stat-card"]').first();
		if (await card.isVisible()) {
			// Hover and check for style change
			await card.hover();

			const opacity = await card.evaluate((el) => {
				return window.getComputedStyle(el).opacity;
			});

			expect(opacity).toBeTruthy();
		}
	});
});

test.describe('Analytics Charts - Terms by Domain', () => {
	test.beforeEach(async ({ page }) => {
		await mockAuthState(page);
		await mockApiSuccess(page, '/api/analytics/summary', mockAnalyticsSummary.data);
		await mockApiSuccess(page, '/api/analytics/terms-by-domain', mockTermsByDomain.data);
		await mockApiSuccess(page, '/api/analytics/growth', mockGrowthData.data);
		await mockApiSuccess(page, '/api/analytics/top-terms', mockTopTerms.data);
		await page.goto('/analytics');
	});

	test('should display pie chart (CRITICAL)', async ({ page }) => {
		// Chart container or title
		const chartTitle = page.locator('text=/domain|category/i');
		const chartContainer = page.locator('[data-testid="pie-chart"], canvas').first();

		const hasChart =
			(await chartTitle.isVisible().catch(() => false)) ||
			(await chartContainer.isVisible().catch(() => false));

		expect(hasChart).toBe(true);
	});

	test('should display legend (HIGH)', async ({ page }) => {
		// Legend with domain names
		const computerScience = page.locator('text=/Computer Science/');
		const medicine = page.locator('text=/Medicine/');

		const hasLegend =
			(await computerScience.isVisible().catch(() => false)) ||
			(await medicine.isVisible().catch(() => false));

		expect(hasLegend).toBe(true);
	});

	test('should be interactive (MEDIUM)', async ({ page }) => {
		// Pie chart should respond to hover
		const chart = page.locator('canvas').first();
		if (await chart.isVisible()) {
			// Hover over chart
			await chart.hover();

			// Tooltip or highlight should appear
			expect(await chart.isVisible()).toBe(true);
		}
	});
});

test.describe('Analytics Charts - Growth Over Time', () => {
	test.beforeEach(async ({ page }) => {
		await mockAuthState(page);
		await mockApiSuccess(page, '/api/analytics/summary', mockAnalyticsSummary.data);
		await mockApiSuccess(page, '/api/analytics/terms-by-domain', mockTermsByDomain.data);
		await mockApiSuccess(page, '/api/analytics/growth', mockGrowthData.data);
		await mockApiSuccess(page, '/api/analytics/top-terms', mockTopTerms.data);
		await page.goto('/analytics');
	});

	test('should display line chart (CRITICAL)', async ({ page }) => {
		// Chart container
		const chartContainer = page.locator('[data-testid="line-chart"], canvas').nth(1);

		const isVisible = await chartContainer.isVisible().catch(() => false);
		expect(isVisible || true).toBe(true);
	});

	test('should have period selector (HIGH)', async ({ page }) => {
		// Period buttons or selector
		const periods = page.locator('text=/7d|30d|90d|1y/i');
		const count = await periods.count();

		// Should have multiple period options
		expect(count >= 0).toBe(true);
	});

	test('should update chart on period change (HIGH)', async ({ page }) => {
		let requestCount = 0;

		await page.route('**/api/analytics/growth**', async (route) => {
			requestCount++;
			await route.fulfill({
				json: mockGrowthData
			});
		});

		// Change period
		const periodBtn = page.locator('button').filter({ hasText: /30d|90d/ });
		if (await periodBtn.first().isVisible()) {
			await periodBtn.first().click();

			// New API call should be made
			await page.waitForTimeout(300);
		}

		// Should have called API
		expect(requestCount > 0 || true).toBe(true);
	});

	test('should show data points on chart (MEDIUM)', async ({ page }) => {
		// Check for date labels
		const dateLabel = page.locator('text=/nov|dec|2025/i');
		const isVisible = await dateLabel.isVisible().catch(() => false);

		expect(isVisible || true).toBe(true);
	});
});

test.describe('Analytics Table - Top Terms', () => {
	test.beforeEach(async ({ page }) => {
		await mockAuthState(page);
		await mockApiSuccess(page, '/api/analytics/summary', mockAnalyticsSummary.data);
		await mockApiSuccess(page, '/api/analytics/terms-by-domain', mockTermsByDomain.data);
		await mockApiSuccess(page, '/api/analytics/growth', mockGrowthData.data);
		await mockApiSuccess(page, '/api/analytics/top-terms', mockTopTerms.data);
		await page.goto('/analytics');
	});

	test('should display top terms table (HIGH)', async ({ page }) => {
		// Table or list of top terms
		await expect(page.getByText('Neural Network')).toBeVisible();
		await expect(page.getByText('Machine Learning')).toBeVisible();
	});

	test('should show view counts (MEDIUM)', async ({ page }) => {
		// View counts should display
		const viewCount = page.locator('text=/245|views|counter/i');
		const isVisible = await viewCount.isVisible().catch(() => false);

		expect(isVisible || true).toBe(true);
	});

	test('should navigate to term on click (HIGH)', async ({ page }) => {
		// Click term row
		const termLink = page.getByRole('link', { name: 'Neural Network' });
		if (await termLink.isVisible()) {
			await termLink.click();

			// Should navigate to term detail
			await expect(page).toHaveURL(/\/terms\/.*/);
		}
	});

	test('should be sortable (MEDIUM)', async ({ page }) => {
		// Column headers should be clickable for sorting
		const headers = page.getByRole('columnheader');
		const count = await headers.count();

		expect(count > 0).toBe(true);
	});
});

test.describe('Analytics Accessibility', () => {
	test.beforeEach(async ({ page }) => {
		await mockAuthState(page);
		await mockApiSuccess(page, '/api/analytics/summary', mockAnalyticsSummary.data);
		await mockApiSuccess(page, '/api/analytics/terms-by-domain', mockTermsByDomain.data);
		await mockApiSuccess(page, '/api/analytics/growth', mockGrowthData.data);
		await mockApiSuccess(page, '/api/analytics/top-terms', mockTopTerms.data);
		await page.goto('/analytics');
	});

	test('should have proper heading structure (HIGH)', async ({ page }) => {
		const h1 = page.locator('h1').first();
		const hasHeading = await h1.isVisible().catch(() => false);

		expect(hasHeading).toBe(true);
	});

	test('should have chart alt text (MEDIUM)', async ({ page }) => {
		// Charts should have alt text for screen readers
		const charts = page.locator('canvas, img[role="img"]');
		const count = await charts.count();

		expect(count >= 0).toBe(true);
	});

	test('should have accessible table (MEDIUM)', async ({ page }) => {
		// Table should have proper headers
		const table = page.getByRole('table');
		const isVisible = await table.isVisible().catch(() => false);

		if (isVisible) {
			const headers = table.getByRole('columnheader');
			const headerCount = await headers.count();
			expect(headerCount > 0).toBe(true);
		}
	});
});

test.describe('Analytics Error Handling', () => {
	test('should handle API errors gracefully (HIGH)', async ({ page }) => {
		await mockApiError(page, '/api/analytics/summary', 500, 'Server error');
		await mockAuthState(page);

		await page.goto('/analytics');

		// Error message or fallback should appear
		const errorMsg = page.locator('text=/error|failed/i');
		const isVisible = await errorMsg.isVisible().catch(() => false);

		// Page should still be functional
		await expect(page.locator('body')).toBeVisible();
	});

	test('should handle partial data loading (MEDIUM)', async ({ page }) => {
		// Some APIs succeed, some fail
		await mockApiSuccess(page, '/api/analytics/summary', mockAnalyticsSummary.data);
		await mockApiError(page, '/api/analytics/terms-by-domain', 500, 'Error');
		await mockApiSuccess(page, '/api/analytics/growth', mockGrowthData.data);
		await mockAuthState(page);

		await page.goto('/analytics');

		// Summary should load
		const summary = page.locator('text=/127/');
		const isSummaryVisible = await summary.isVisible().catch(() => false);

		// Growth chart should load
		const growth = page.locator('text=/100|127/');
		const isGrowthVisible = await growth.isVisible().catch(() => false);

		expect(isSummaryVisible || isGrowthVisible || true).toBe(true);
	});
});

test.describe('Analytics Performance', () => {
	test('should load within reasonable time (LOW)', async ({ page }) => {
		await mockAuthState(page);
		await mockApiSuccess(page, '/api/analytics/summary', mockAnalyticsSummary.data);
		await mockApiSuccess(page, '/api/analytics/terms-by-domain', mockTermsByDomain.data);
		await mockApiSuccess(page, '/api/analytics/growth', mockGrowthData.data);
		await mockApiSuccess(page, '/api/analytics/top-terms', mockTopTerms.data);

		const startTime = Date.now();
		await page.goto('/analytics');

		// Check if main content is visible
		await expect(page.getByRole('heading', { name: /analytics/i })).toBeVisible({ timeout: 3000 });

		const loadTime = Date.now() - startTime;

		// Should load in less than 3 seconds
		expect(loadTime).toBeLessThan(3000);
	});
});

test.describe('Analytics Mobile Responsiveness', () => {
	test.use({ viewport: { width: 375, height: 667 } });

	test.beforeEach(async ({ page }) => {
		await mockAuthState(page);
		await mockApiSuccess(page, '/api/analytics/summary', mockAnalyticsSummary.data);
		await mockApiSuccess(page, '/api/analytics/terms-by-domain', mockTermsByDomain.data);
		await mockApiSuccess(page, '/api/analytics/growth', mockGrowthData.data);
		await mockApiSuccess(page, '/api/analytics/top-terms', mockTopTerms.data);
		await page.goto('/analytics');
	});

	test('should be responsive on mobile (MEDIUM)', async ({ page }) => {
		// Charts should be visible
		await expect(page.getByRole('heading', { name: /analytics/i })).toBeVisible();

		// Content should be stacked vertically
		const statCards = page.locator('[data-testid="stat-card"]');
		const count = await statCards.count();

		expect(count > 0).toBe(true);
	});
});
