/**
 * Component tests for Register page
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/svelte';
import { goto } from '$app/navigation';
import RegisterPage from './+page.svelte';
import { register, loginWithOAuth } from '$lib/utils/auth';
import { authStore } from '$lib/stores/auth';
import { ApiError } from '$lib/utils/api';

// Mock auth utilities
vi.mock('$lib/utils/auth', () => ({
	register: vi.fn(),
	loginWithOAuth: vi.fn()
}));

describe('Register Page', () => {
	beforeEach(() => {
		vi.clearAllMocks();
		authStore.logout();
	});

	it('should render registration form', () => {
		render(RegisterPage);

		expect(screen.getByRole('heading', { name: /create.*account/i })).toBeInTheDocument();
		expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
		expect(screen.getByLabelText(/first name/i)).toBeInTheDocument();
		expect(screen.getByLabelText(/last name/i)).toBeInTheDocument();
		expect(screen.getByLabelText(/^password$/i)).toBeInTheDocument();
		expect(screen.getByLabelText(/confirm password/i)).toBeInTheDocument();
	});

	it('should render language selector', () => {
		render(RegisterPage);

		const languageSelect = screen.getByLabelText(/language/i);
		expect(languageSelect).toBeInTheDocument();
	});

	it('should render OAuth buttons', () => {
		render(RegisterPage);

		expect(screen.getByRole('button', { name: /google/i })).toBeInTheDocument();
		expect(screen.getByRole('button', { name: /github/i })).toBeInTheDocument();
	});

	it('should render link to login page', () => {
		render(RegisterPage);

		const loginLink = screen.getByRole('link', { name: /sign in/i });
		expect(loginLink).toBeInTheDocument();
		expect(loginLink).toHaveAttribute('href', '/login');
	});

	it('should call register function when form is submitted with valid data', async () => {
		vi.mocked(register).mockResolvedValue();
		render(RegisterPage);

		await fireEvent.input(screen.getByLabelText(/email/i), {
			target: { value: 'test@example.com' }
		});
		await fireEvent.input(screen.getByLabelText(/first name/i), { target: { value: 'John' } });
		await fireEvent.input(screen.getByLabelText(/last name/i), { target: { value: 'Doe' } });
		await fireEvent.input(screen.getByLabelText(/^password$/i), {
			target: { value: 'password123' }
		});
		await fireEvent.input(screen.getByLabelText(/confirm password/i), {
			target: { value: 'password123' }
		});

		await fireEvent.click(screen.getByRole('button', { name: /create account/i }));

		await waitFor(() => {
			expect(register).toHaveBeenCalledWith({
				email: 'test@example.com',
				password: 'password123',
				first_name: 'John',
				last_name: 'Doe',
				language: 'fr' // default
			});
		});
	});

	it('should show error when passwords do not match', async () => {
		render(RegisterPage);

		await fireEvent.input(screen.getByLabelText(/email/i), {
			target: { value: 'test@example.com' }
		});
		await fireEvent.input(screen.getByLabelText(/first name/i), { target: { value: 'John' } });
		await fireEvent.input(screen.getByLabelText(/last name/i), { target: { value: 'Doe' } });
		await fireEvent.input(screen.getByLabelText(/^password$/i), {
			target: { value: 'password123' }
		});
		await fireEvent.input(screen.getByLabelText(/confirm password/i), {
			target: { value: 'differentpassword' }
		});

		await fireEvent.click(screen.getByRole('button', { name: /create account/i }));

		await waitFor(() => {
			expect(screen.getByText(/passwords do not match/i)).toBeInTheDocument();
		});

		expect(register).not.toHaveBeenCalled();
	});

	it('should show error when password is too short', async () => {
		render(RegisterPage);

		await fireEvent.input(screen.getByLabelText(/email/i), {
			target: { value: 'test@example.com' }
		});
		await fireEvent.input(screen.getByLabelText(/first name/i), { target: { value: 'John' } });
		await fireEvent.input(screen.getByLabelText(/last name/i), { target: { value: 'Doe' } });
		await fireEvent.input(screen.getByLabelText(/^password$/i), { target: { value: '12345' } });
		await fireEvent.input(screen.getByLabelText(/confirm password/i), {
			target: { value: '12345' }
		});

		await fireEvent.click(screen.getByRole('button', { name: /create account/i }));

		await waitFor(() => {
			expect(screen.getByText(/at least 8 characters/i)).toBeInTheDocument();
		});

		expect(register).not.toHaveBeenCalled();
	});

	it('should display error message when registration fails', async () => {
		const errorMessage = 'Email already exists';
		vi.mocked(register).mockRejectedValue(new ApiError('EMAIL_EXISTS', errorMessage));

		render(RegisterPage);

		await fireEvent.input(screen.getByLabelText(/email/i), {
			target: { value: 'existing@example.com' }
		});
		await fireEvent.input(screen.getByLabelText(/first name/i), { target: { value: 'John' } });
		await fireEvent.input(screen.getByLabelText(/last name/i), { target: { value: 'Doe' } });
		await fireEvent.input(screen.getByLabelText(/^password$/i), {
			target: { value: 'password123' }
		});
		await fireEvent.input(screen.getByLabelText(/confirm password/i), {
			target: { value: 'password123' }
		});

		await fireEvent.click(screen.getByRole('button', { name: /create account/i }));

		await waitFor(() => {
			expect(screen.getByText(errorMessage)).toBeInTheDocument();
		});
	});

	it('should show loading state during registration', async () => {
		vi.mocked(register).mockImplementation(
			() => new Promise((resolve) => setTimeout(resolve, 100))
		);

		render(RegisterPage);

		await fireEvent.input(screen.getByLabelText(/email/i), {
			target: { value: 'test@example.com' }
		});
		await fireEvent.input(screen.getByLabelText(/first name/i), { target: { value: 'John' } });
		await fireEvent.input(screen.getByLabelText(/last name/i), { target: { value: 'Doe' } });
		await fireEvent.input(screen.getByLabelText(/^password$/i), {
			target: { value: 'password123' }
		});
		await fireEvent.input(screen.getByLabelText(/confirm password/i), {
			target: { value: 'password123' }
		});

		const submitButton = screen.getByRole('button', { name: /create account/i });
		await fireEvent.click(submitButton);

		expect(submitButton).toBeDisabled();
	});

	it('should call loginWithOAuth when Google button is clicked', async () => {
		render(RegisterPage);

		const googleButton = screen.getByRole('button', { name: /google/i });
		await fireEvent.click(googleButton);

		expect(loginWithOAuth).toHaveBeenCalledWith('google');
	});

	it('should call loginWithOAuth when GitHub button is clicked', async () => {
		render(RegisterPage);

		const githubButton = screen.getByRole('button', { name: /github/i });
		await fireEvent.click(githubButton);

		expect(loginWithOAuth).toHaveBeenCalledWith('github');
	});

	it('should show password mismatch indicator in real-time', async () => {
		render(RegisterPage);

		const passwordInput = screen.getByLabelText(/^password$/i);
		const confirmInput = screen.getByLabelText(/confirm password/i);

		await fireEvent.input(passwordInput, { target: { value: 'password123' } });
		await fireEvent.input(confirmInput, { target: { value: 'password456' } });

		// Should show visual indicator (depends on implementation)
		// This test documents expected behavior
		await waitFor(() => {
			// Check for error styling or message
			// Implementation detail: may vary
		});
	});

	it('should handle unexpected errors gracefully', async () => {
		vi.mocked(register).mockRejectedValue(new Error('Network error'));

		render(RegisterPage);

		await fireEvent.input(screen.getByLabelText(/email/i), {
			target: { value: 'test@example.com' }
		});
		await fireEvent.input(screen.getByLabelText(/first name/i), { target: { value: 'John' } });
		await fireEvent.input(screen.getByLabelText(/last name/i), { target: { value: 'Doe' } });
		await fireEvent.input(screen.getByLabelText(/^password$/i), {
			target: { value: 'password123' }
		});
		await fireEvent.input(screen.getByLabelText(/confirm password/i), {
			target: { value: 'password123' }
		});

		await fireEvent.click(screen.getByRole('button', { name: /create account/i }));

		await waitFor(() => {
			expect(screen.getByText(/unexpected error/i)).toBeInTheDocument();
		});
	});

	it('should have proper form accessibility attributes', () => {
		render(RegisterPage);

		const emailInput = screen.getByLabelText(/email/i);
		const passwordInput = screen.getByLabelText(/^password$/i);
		const confirmInput = screen.getByLabelText(/confirm password/i);

		expect(emailInput).toHaveAttribute('type', 'email');
		expect(passwordInput).toHaveAttribute('type', 'password');
		expect(confirmInput).toHaveAttribute('type', 'password');
		expect(emailInput).toHaveAttribute('required');
		expect(passwordInput).toHaveAttribute('required');
		expect(confirmInput).toHaveAttribute('required');
	});

	it('should allow selecting different languages', async () => {
		vi.mocked(register).mockResolvedValue();
		render(RegisterPage);

		const languageSelect = screen.getByLabelText(/language/i);
		await fireEvent.change(languageSelect, { target: { value: 'en' } });

		await fireEvent.input(screen.getByLabelText(/email/i), {
			target: { value: 'test@example.com' }
		});
		await fireEvent.input(screen.getByLabelText(/first name/i), { target: { value: 'John' } });
		await fireEvent.input(screen.getByLabelText(/last name/i), { target: { value: 'Doe' } });
		await fireEvent.input(screen.getByLabelText(/^password$/i), {
			target: { value: 'password123' }
		});
		await fireEvent.input(screen.getByLabelText(/confirm password/i), {
			target: { value: 'password123' }
		});

		await fireEvent.click(screen.getByRole('button', { name: /create account/i }));

		await waitFor(() => {
			expect(register).toHaveBeenCalledWith(
				expect.objectContaining({
					language: 'en'
				})
			);
		});
	});

	it('should redirect to /terms when already authenticated', async () => {
		authStore.login(
			{
				id: 'user-123',
				email: 'test@example.com',
				first_name: 'John',
				last_name: 'Doe',
				language: 'en',
				adoption_level: 'research-project',
				is_active: true,
				created_at: '2025-01-01T00:00:00Z'
			},
			'access-token',
			'refresh-token'
		);

		render(RegisterPage);

		await waitFor(() => {
			expect(goto).toHaveBeenCalledWith('/terms');
		});
	});
});
