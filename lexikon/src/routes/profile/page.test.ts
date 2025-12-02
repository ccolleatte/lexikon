/**
 * Component tests for Profile page
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/svelte';
import ProfilePage from './+page.svelte';
import { authStore } from '$lib/stores/auth';
import { logout, changePassword } from '$lib/utils/auth';
import { ApiError } from '$lib/utils/api';

// Mock auth utilities
vi.mock('$lib/utils/auth', () => ({
	logout: vi.fn(),
	changePassword: vi.fn()
}));

describe('Profile Page', () => {
	const mockUser = {
		id: 'user-123',
		email: 'john.doe@example.com',
		first_name: 'John',
		last_name: 'Doe',
		language: 'en',
		adoption_level: 'research-project' as const,
		is_active: true,
		created_at: '2025-01-15T10:30:00Z',
		institution: 'Test University'
	};

	beforeEach(() => {
		vi.clearAllMocks();
		authStore.login(mockUser, 'access-token', 'refresh-token');
	});

	describe('User Information Display', () => {
		it('should display user name', () => {
			render(ProfilePage);

			expect(screen.getByText('John Doe')).toBeInTheDocument();
		});

		it('should display user email', () => {
			render(ProfilePage);

			expect(screen.getByText('john.doe@example.com')).toBeInTheDocument();
		});

		it('should display user institution when available', () => {
			render(ProfilePage);

			expect(screen.getByText(/Test University/i)).toBeInTheDocument();
		});

		it('should display account creation date', () => {
			render(ProfilePage);

			// Check for formatted date (exact format may vary)
			expect(screen.getByText(/member since/i)).toBeInTheDocument();
		});

		it('should display adoption level', () => {
			render(ProfilePage);

			expect(screen.getByText(/research.*project/i)).toBeInTheDocument();
		});

		it('should display preferred language', () => {
			render(ProfilePage);

			expect(screen.getByText(/english/i)).toBeInTheDocument();
		});
	});

	describe('Change Password Feature', () => {
		it('should show change password button', () => {
			render(ProfilePage);

			expect(screen.getByRole('button', { name: /change password/i })).toBeInTheDocument();
		});

		it('should show password form when change password is clicked', async () => {
			render(ProfilePage);

			const changePasswordButton = screen.getByRole('button', { name: /change password/i });
			await fireEvent.click(changePasswordButton);

			await waitFor(() => {
				expect(screen.getByLabelText(/current password/i)).toBeVisible();
				expect(screen.getByLabelText(/^new password$/i)).toBeVisible();
				expect(screen.getByLabelText(/confirm.*password/i)).toBeVisible();
			});
		});

		it('should call changePassword with correct data', async () => {
			vi.mocked(changePassword).mockResolvedValue();
			render(ProfilePage);

			// Open change password form
			await fireEvent.click(screen.getByRole('button', { name: /change password/i }));

			// Fill in password fields
			await fireEvent.input(screen.getByLabelText(/current password/i), {
				target: { value: 'oldpassword123' }
			});
			await fireEvent.input(screen.getByLabelText(/^new password$/i), {
				target: { value: 'newpassword123' }
			});
			await fireEvent.input(screen.getByLabelText(/confirm.*password/i), {
				target: { value: 'newpassword123' }
			});

			// Submit
			await fireEvent.click(screen.getByRole('button', { name: /save.*password/i }));

			await waitFor(() => {
				expect(changePassword).toHaveBeenCalledWith('oldpassword123', 'newpassword123');
			});
		});

		it('should show error when passwords do not match', async () => {
			render(ProfilePage);

			await fireEvent.click(screen.getByRole('button', { name: /change password/i }));

			await fireEvent.input(screen.getByLabelText(/current password/i), {
				target: { value: 'oldpassword123' }
			});
			await fireEvent.input(screen.getByLabelText(/^new password$/i), {
				target: { value: 'newpassword123' }
			});
			await fireEvent.input(screen.getByLabelText(/confirm.*password/i), {
				target: { value: 'differentpassword' }
			});

			await fireEvent.click(screen.getByRole('button', { name: /save.*password/i }));

			await waitFor(() => {
				expect(screen.getByText(/passwords do not match/i)).toBeInTheDocument();
			});

			expect(changePassword).not.toHaveBeenCalled();
		});

		it('should show error when new password is too short', async () => {
			render(ProfilePage);

			await fireEvent.click(screen.getByRole('button', { name: /change password/i }));

			await fireEvent.input(screen.getByLabelText(/current password/i), {
				target: { value: 'oldpassword123' }
			});
			await fireEvent.input(screen.getByLabelText(/^new password$/i), {
				target: { value: 'short' }
			});
			await fireEvent.input(screen.getByLabelText(/confirm.*password/i), {
				target: { value: 'short' }
			});

			await fireEvent.click(screen.getByRole('button', { name: /save.*password/i }));

			await waitFor(() => {
				expect(screen.getByText(/at least 8 characters/i)).toBeInTheDocument();
			});

			expect(changePassword).not.toHaveBeenCalled();
		});

		it('should display API error when password change fails', async () => {
			const errorMessage = 'Current password is incorrect';
			vi.mocked(changePassword).mockRejectedValue(
				new ApiError('INVALID_PASSWORD', errorMessage)
			);

			render(ProfilePage);

			await fireEvent.click(screen.getByRole('button', { name: /change password/i }));

			await fireEvent.input(screen.getByLabelText(/current password/i), {
				target: { value: 'wrongpassword' }
			});
			await fireEvent.input(screen.getByLabelText(/^new password$/i), {
				target: { value: 'newpassword123' }
			});
			await fireEvent.input(screen.getByLabelText(/confirm.*password/i), {
				target: { value: 'newpassword123' }
			});

			await fireEvent.click(screen.getByRole('button', { name: /save.*password/i }));

			await waitFor(() => {
				expect(screen.getByText(errorMessage)).toBeInTheDocument();
			});
		});

		it('should show success message after successful password change', async () => {
			vi.mocked(changePassword).mockResolvedValue();
			render(ProfilePage);

			await fireEvent.click(screen.getByRole('button', { name: /change password/i }));

			await fireEvent.input(screen.getByLabelText(/current password/i), {
				target: { value: 'oldpassword123' }
			});
			await fireEvent.input(screen.getByLabelText(/^new password$/i), {
				target: { value: 'newpassword123' }
			});
			await fireEvent.input(screen.getByLabelText(/confirm.*password/i), {
				target: { value: 'newpassword123' }
			});

			await fireEvent.click(screen.getByRole('button', { name: /save.*password/i }));

			await waitFor(() => {
				expect(screen.getByText(/password changed successfully/i)).toBeInTheDocument();
			});
		});

		it('should clear password fields after successful change', async () => {
			vi.mocked(changePassword).mockResolvedValue();
			render(ProfilePage);

			await fireEvent.click(screen.getByRole('button', { name: /change password/i }));

			const currentPasswordInput = screen.getByLabelText(/current password/i) as HTMLInputElement;
			const newPasswordInput = screen.getByLabelText(/^new password$/i) as HTMLInputElement;
			const confirmPasswordInput = screen.getByLabelText(
				/confirm.*password/i
			) as HTMLInputElement;

			await fireEvent.input(currentPasswordInput, { target: { value: 'oldpassword123' } });
			await fireEvent.input(newPasswordInput, { target: { value: 'newpassword123' } });
			await fireEvent.input(confirmPasswordInput, { target: { value: 'newpassword123' } });

			await fireEvent.click(screen.getByRole('button', { name: /save.*password/i }));

			await waitFor(() => {
				expect(changePassword).toHaveBeenCalled();
			});

			// Form should be hidden after successful change
			await waitFor(() => {
				expect(screen.queryByLabelText(/current password/i)).not.toBeVisible();
			});
		});

		it('should show loading state during password change', async () => {
			vi.mocked(changePassword).mockImplementation(
				() => new Promise((resolve) => setTimeout(resolve, 100))
			);

			render(ProfilePage);

			await fireEvent.click(screen.getByRole('button', { name: /change password/i }));

			await fireEvent.input(screen.getByLabelText(/current password/i), {
				target: { value: 'oldpassword123' }
			});
			await fireEvent.input(screen.getByLabelText(/^new password$/i), {
				target: { value: 'newpassword123' }
			});
			await fireEvent.input(screen.getByLabelText(/confirm.*password/i), {
				target: { value: 'newpassword123' }
			});

			const submitButton = screen.getByRole('button', { name: /save.*password/i });
			await fireEvent.click(submitButton);

			expect(submitButton).toBeDisabled();
		});

		it('should allow canceling password change', async () => {
			render(ProfilePage);

			await fireEvent.click(screen.getByRole('button', { name: /change password/i }));

			await waitFor(() => {
				expect(screen.getByLabelText(/current password/i)).toBeVisible();
			});

			const cancelButton = screen.getByRole('button', { name: /cancel/i });
			await fireEvent.click(cancelButton);

			await waitFor(() => {
				expect(screen.queryByLabelText(/current password/i)).not.toBeVisible();
			});
		});
	});

	describe('Logout Functionality', () => {
		it('should show logout button', () => {
			render(ProfilePage);

			expect(screen.getByRole('button', { name: /logout/i })).toBeInTheDocument();
		});

		it('should call logout when logout button is clicked', async () => {
			vi.mocked(logout).mockResolvedValue();
			render(ProfilePage);

			const logoutButton = screen.getByRole('button', { name: /logout/i });
			await fireEvent.click(logoutButton);

			await waitFor(() => {
				expect(logout).toHaveBeenCalled();
			});
		});
	});

	describe('Accessibility', () => {
		it('should have proper heading hierarchy', () => {
			render(ProfilePage);

			// Should have main heading
			expect(screen.getByRole('heading', { level: 1 })).toBeInTheDocument();
		});

		it('should have accessible form labels in password change form', async () => {
			render(ProfilePage);

			await fireEvent.click(screen.getByRole('button', { name: /change password/i }));

			const currentPasswordInput = screen.getByLabelText(/current password/i);
			const newPasswordInput = screen.getByLabelText(/^new password$/i);
			const confirmPasswordInput = screen.getByLabelText(/confirm.*password/i);

			expect(currentPasswordInput).toHaveAttribute('type', 'password');
			expect(newPasswordInput).toHaveAttribute('type', 'password');
			expect(confirmPasswordInput).toHaveAttribute('type', 'password');
		});
	});

	describe('Error Handling', () => {
		it('should handle network errors gracefully', async () => {
			vi.mocked(changePassword).mockRejectedValue(new Error('Network error'));

			render(ProfilePage);

			await fireEvent.click(screen.getByRole('button', { name: /change password/i }));

			await fireEvent.input(screen.getByLabelText(/current password/i), {
				target: { value: 'oldpassword123' }
			});
			await fireEvent.input(screen.getByLabelText(/^new password$/i), {
				target: { value: 'newpassword123' }
			});
			await fireEvent.input(screen.getByLabelText(/confirm.*password/i), {
				target: { value: 'newpassword123' }
			});

			await fireEvent.click(screen.getByRole('button', { name: /save.*password/i }));

			await waitFor(() => {
				expect(screen.getByText(/failed to change password/i)).toBeInTheDocument();
			});
		});
	});
});
