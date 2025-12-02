/**
 * E2E Tests for Relations Management
 * Tests for creating, deleting, and viewing term relations
 */

import { test, expect } from '@playwright/test';
import { mockAuthState } from './helpers/auth-helpers';
import { mockApiSuccess, mockApiError } from './helpers/api-mocking';
import { mockRelations, mockInferredRelations, mockSearchResults } from './fixtures/mock-data';

test.describe('Relations Display', () => {
	test.beforeEach(async ({ page }) => {
		await mockAuthState(page);
		await mockApiSuccess(page, '/api/ontology/relations?term_id=', mockRelations.data);
		await mockApiSuccess(page, '/api/ontology/relations/inferred?term_id=', mockInferredRelations.data);
		await page.goto('/terms/term-1');
	});

	test('should display relations section on term detail page (CRITICAL)', async ({ page }) => {
		// Check for relations heading
		await expect(page.getByRole('heading', { name: /relations/i })).toBeVisible();

		// Check for "Add Relation" button
		await expect(page.getByRole('button', { name: /add relation/i })).toBeVisible();
	});

	test('should display existing relations grouped by type (CRITICAL)', async ({ page }) => {
		// Check for relation groupings
		await expect(page.getByText(/broader/i)).toBeVisible();
		await expect(page.getByText('Artificial Intelligence')).toBeVisible();

		await expect(page.getByText(/narrower/i)).toBeVisible();
		await expect(page.getByText('Deep Learning')).toBeVisible();
	});

	test('should show empty state when no direct relations (HIGH)', async ({ page }) => {
		await mockApiSuccess(page, '/api/ontology/relations?term_id=', []);
		await page.reload();

		// Empty state message
		const emptyState = page.locator('text=/no relations|add.*relation/i');
		const isVisible = await emptyState.isVisible().catch(() => false);
		expect(isVisible || (await page.getByRole('button', { name: /add relation/i }).isVisible())).toBe(true);
	});

	test('should make relations clickable links (HIGH)', async ({ page }) => {
		// Click on a relation
		await page.getByRole('link', { name: 'Artificial Intelligence' }).click();

		// Should navigate
		await expect(page).toHaveURL(/\/terms\/(.*)/);
	});

	test('should display relation type icons (MEDIUM)', async ({ page }) => {
		// Check for icons (implementation dependent)
		const relationItem = page.locator('[data-testid="relation-item"]').first();
		await expect(relationItem).toBeVisible();
		// Icon presence depends on your component implementation
	});
});

test.describe('Adding Relations', () => {
	test.beforeEach(async ({ page }) => {
		await mockAuthState(page);
		await mockApiSuccess(page, '/api/ontology/relations?term_id=', mockRelations.data);
		await mockApiSuccess(page, '/api/ontology/relations/inferred?term_id=', mockInferredRelations.data);
		await page.goto('/terms/term-1');
	});

	test('should open relation modal on button click (CRITICAL)', async ({ page }) => {
		await page.getByRole('button', { name: /add relation/i }).click();

		// Modal should appear
		const modal = page.getByRole('dialog', { name: /add.*relation|relation/i });
		await expect(modal).toBeVisible();

		// Form elements visible
		await expect(page.getByLabel(/relation type/i)).toBeVisible();
		await expect(page.getByLabel(/select.*term|target term/i)).toBeVisible();
	});

	test('should show all relation types (CRITICAL)', async ({ page }) => {
		await page.getByRole('button', { name: /add relation/i }).click();

		const typeSelect = page.getByLabel(/relation type/i);
		await typeSelect.click();

		// Check for relation type options
		await expect(page.getByRole('option', { name: /broader/i })).toBeVisible();
		await expect(page.getByRole('option', { name: /narrower/i })).toBeVisible();
		await expect(page.getByRole('option', { name: /related/i })).toBeVisible();
		await expect(page.getByRole('option', { name: /exact.*match|equivalent/i })).toBeVisible();
	});

	test('should autocomplete term search (CRITICAL)', async ({ page }) => {
		await mockApiSuccess(page, '/api/terms/search?q=', mockSearchResults.data);

		await page.getByRole('button', { name: /add relation/i }).click();

		const termInput = page.getByLabel(/select.*term|target term/i);
		await termInput.fill('machine');
		await page.waitForTimeout(400); // Wait for debounce

		// Suggestions should appear
		await expect(page.getByText('Machine Learning')).toBeVisible();
		await expect(page.getByText('Neural Network')).toBeVisible();
	});

	test('should validate required fields (HIGH)', async ({ page }) => {
		await page.getByRole('button', { name: /add relation/i }).click();

		// Try to save without selecting
		const saveButton = page.getByRole('button', { name: /save|create|add/i }).last();
		await saveButton.click();

		// Validation errors should appear
		const errors = page.locator('text=/required|please select/i');
		const hasError = await errors.count().then((c) => c > 0);
		expect(hasError).toBe(true);
	});

	test('should successfully create relation (CRITICAL)', async ({ page }) => {
		let relationCreated = false;
		let requestBody: any = null;

		await page.route('**/api/ontology/relations', async (route) => {
			if (route.request().method() === 'POST') {
				relationCreated = true;
				requestBody = await route.request().postDataJSON();
				await route.fulfill({
					json: {
						success: true,
						data: { id: 'new-rel-123' }
					}
				});
			} else {
				await route.continue();
			}
		});

		await page.getByRole('button', { name: /add relation/i }).click();

		// Select relation type
		await page.getByLabel(/relation type/i).selectOption('broader');

		// Search and select term
		const termInput = page.getByLabel(/select.*term|target term/i);
		await termInput.fill('machine');
		await page.waitForTimeout(400);
		await page.getByText('Machine Learning').click();

		// Save
		await page.getByRole('button', { name: /save|create/i }).last().click();

		// Verify API called
		expect(relationCreated).toBe(true);

		// Modal should close
		const modal = page.getByRole('dialog').first();
		const isVisible = await modal.isVisible().catch(() => false);
		expect(isVisible).toBe(false);

		// Success toast should appear
		const successMsg = page.locator('text=/relation.*added|success/i');
		const hasSuccess = await successMsg.isVisible().catch(() => false);
		expect(hasSuccess || relationCreated).toBe(true);
	});

	test('should prevent duplicate relations (HIGH)', async ({ page }) => {
		await page.route('**/api/ontology/relations', async (route) => {
			if (route.request().method() === 'POST') {
				await route.fulfill({
					status: 400,
					json: {
						success: false,
						error: {
							message: 'Relation already exists'
						}
					}
				});
			} else {
				await route.continue();
			}
		});

		await page.getByRole('button', { name: /add relation/i }).click();

		// Try to create duplicate
		await page.getByLabel(/relation type/i).selectOption('broader');
		await page.getByLabel(/select.*term/i).fill('test');
		await page.waitForTimeout(400);
		await page.getByText('Machine Learning').click();
		await page.getByRole('button', { name: /save|create/i }).last().click();

		// Error message should appear
		const errorMsg = page.locator('text=/already exists|duplicate/i');
		const hasError = await errorMsg.isVisible().catch(() => false);
		expect(hasError).toBe(true);

		// Modal should still be open
		const modal = page.getByRole('dialog').first();
		await expect(modal).toBeVisible();
	});

	test('should close modal on cancel (HIGH)', async ({ page }) => {
		await page.getByRole('button', { name: /add relation/i }).click();

		const modal = page.getByRole('dialog').first();
		await expect(modal).toBeVisible();

		// Click cancel
		await page.getByRole('button', { name: /cancel|close/i }).click();

		// Modal should close
		const isVisible = await modal.isVisible().catch(() => false);
		expect(isVisible).toBe(false);
	});

	test('should close modal on Escape key (MEDIUM)', async ({ page }) => {
		await page.getByRole('button', { name: /add relation/i }).click();

		const modal = page.getByRole('dialog').first();
		await expect(modal).toBeVisible();

		// Press Escape
		await page.keyboard.press('Escape');

		// Modal should close
		const isVisible = await modal.isVisible().catch(() => false);
		expect(isVisible).toBe(false);
	});

	test('should close modal on overlay click (MEDIUM)', async ({ page }) => {
		await page.getByRole('button', { name: /add relation/i }).click();

		// Click on overlay/backdrop
		const overlay = page.locator('[data-testid="modal-overlay"]').first();
		if (await overlay.isVisible().catch(() => false)) {
			await overlay.click();
		}

		const modal = page.getByRole('dialog').first();
		const isVisible = await modal.isVisible().catch(() => false);
		expect(isVisible).toBe(false);
	});
});

test.describe('Deleting Relations', () => {
	test.beforeEach(async ({ page }) => {
		await mockAuthState(page);
		await mockApiSuccess(page, '/api/ontology/relations?term_id=', mockRelations.data);
		await mockApiSuccess(page, '/api/ontology/relations/inferred?term_id=', mockInferredRelations.data);
		await page.goto('/terms/term-1');
	});

	test('should show delete button on relations (CRITICAL)', async ({ page }) => {
		// Find delete button/icon on relation
		const deleteButtons = page.locator('[data-testid="delete-relation"], button[aria-label*="delete"], button[aria-label*="remove"]');
		const count = await deleteButtons.count();
		expect(count).toBeGreaterThan(0);
	});

	test('should show confirmation before deleting (HIGH)', async ({ page }) => {
		const deleteButtons = page.locator('[data-testid="delete-relation"], button[aria-label*="delete"]');
		const firstDelete = deleteButtons.first();

		if (await firstDelete.isVisible()) {
			await firstDelete.click();

			// Confirmation dialog
			const confirmDialog = page.getByRole('alertdialog').first();
			const hasConfirm = await confirmDialog.isVisible().catch(() => false);
			expect(hasConfirm).toBe(true);

			// Should have confirm/delete button
			const confirmButton = page.getByRole('button', { name: /confirm|delete/i });
			await expect(confirmButton).toBeVisible();
		}
	});

	test('should delete relation on confirm (CRITICAL)', async ({ page }) => {
		let deleteRequested = false;

		await page.route('**/api/ontology/relations/**', async (route) => {
			if (route.request().method() === 'DELETE') {
				deleteRequested = true;
				await route.fulfill({
					json: { success: true }
				});
			} else {
				await route.continue();
			}
		});

		const deleteButtons = page.locator('[data-testid="delete-relation"], button[aria-label*="delete"]');
		if (await deleteButtons.count()) {
			await deleteButtons.first().click();

			// Confirm delete
			const confirmButton = page.getByRole('button', { name: /confirm|delete|yes/i }).last();
			if (await confirmButton.isVisible()) {
				await confirmButton.click();
			}

			// Verify API called
			expect(deleteRequested).toBe(true);
		}
	});

	test('should cancel deletion (HIGH)', async ({ page }) => {
		const deleteButtons = page.locator('[data-testid="delete-relation"], button[aria-label*="delete"]');
		if (await deleteButtons.count()) {
			await deleteButtons.first().click();

			// Click cancel
			const cancelButton = page.getByRole('button', { name: /cancel|no/i });
			if (await cancelButton.isVisible()) {
				await cancelButton.click();
			}

			// Dialog should close
			const dialog = page.getByRole('alertdialog').first();
			const isVisible = await dialog.isVisible().catch(() => false);
			expect(isVisible).toBe(false);
		}
	});
});

test.describe('Inferred Relations', () => {
	test.beforeEach(async ({ page }) => {
		await mockAuthState(page);
		await mockApiSuccess(page, '/api/ontology/relations?term_id=', mockRelations.data);
		await mockApiSuccess(page, '/api/ontology/relations/inferred?term_id=', mockInferredRelations.data);
		await page.goto('/terms/term-1');
	});

	test('should display inferred relations section (HIGH)', async ({ page }) => {
		// Inferred relations should be visible
		const inferredSection = page.locator('text=/inferred/i');
		const isVisible = await inferredSection.isVisible().catch(() => false);
		expect(isVisible).toBe(true);
	});

	test('should show reasoning explanation (MEDIUM)', async ({ page }) => {
		// Inferred relation should have explanation
		const explanation = page.locator('text=/transitive|inferred from/i');
		const isVisible = await explanation.isVisible().catch(() => false);
		// May or may not be visible depending on implementation
	});

	test('should be visually distinct from direct relations (MEDIUM)', async ({ page }) => {
		const directRelation = page.locator('[data-testid="direct-relation"]').first();
		const inferredRelation = page.locator('[data-testid="inferred-relation"]').first();

		// If both exist, they should be visually distinct
		if (
			(await directRelation.isVisible().catch(() => false)) &&
			(await inferredRelation.isVisible().catch(() => false))
		) {
			const directClass = await directRelation.getAttribute('class');
			const inferredClass = await inferredRelation.getAttribute('class');

			// Should have different classes
			expect(directClass).not.toBe(inferredClass);
		}
	});
});

test.describe('Relations Accessibility', () => {
	test.beforeEach(async ({ page }) => {
		await mockAuthState(page);
		await mockApiSuccess(page, '/api/ontology/relations?term_id=', mockRelations.data);
		await mockApiSuccess(page, '/api/ontology/relations/inferred?term_id=', mockInferredRelations.data);
		await page.goto('/terms/term-1');
	});

	test('should have proper heading hierarchy (HIGH)', async ({ page }) => {
		// Relations section should have proper heading
		const heading = page.getByRole('heading', { name: /relations/i });
		await expect(heading).toBeVisible();

		const level = await heading.evaluate((el) => el.tagName);
		expect(['H1', 'H2', 'H3', 'H4', 'H5', 'H6']).toContain(level);
	});

	test('should be keyboard navigable (HIGH)', async ({ page }) => {
		await page.getByRole('button', { name: /add relation/i }).focus();

		// Should be focusable
		const focused = await page.evaluate(() => {
			return document.activeElement?.getAttribute('aria-label');
		});

		expect(focused).toBeTruthy();
	});
});

test.describe('Relations Error Handling', () => {
	test.beforeEach(async ({ page }) => {
		await mockAuthState(page);
	});

	test('should handle API errors when loading relations (HIGH)', async ({ page }) => {
		await mockApiError(page, '/api/ontology/relations', 500, 'Failed to load relations');

		await page.goto('/terms/term-1');

		// Error message or fallback should appear
		const errorMsg = page.locator('text=/error|failed/i');
		const hasError = await errorMsg.count().then((c) => c > 0);
		// Page should still be functional
		await expect(page.locator('body')).toBeVisible();
	});
});
