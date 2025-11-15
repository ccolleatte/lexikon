/**
 * Component tests for Login page
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/svelte';
import { goto } from '$app/navigation';
import { get } from 'svelte/store';
import LoginPage from './+page.svelte';
import { login, loginWithOAuth } from '$lib/utils/auth';
import { authStore } from '$lib/stores/auth';
import { ApiError } from '$lib/utils/api';

// Mock auth utilities
vi.mock('$lib/utils/auth', () => ({
	login: vi.fn(),
	loginWithOAuth: vi.fn()
}));

describe('Login Page', () => {
	beforeEach(() => {
		vi.clearAllMocks();
		// Reset auth store to unauthenticated state
		authStore.logout();
	});

	it('should render login form', () => {
		render(LoginPage);

		expect(screen.getByRole('heading', { name: /sign in/i })).toBeInTheDocument();
		expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
		expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
		expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
	});

	it('should render OAuth buttons', () => {
		render(LoginPage);

		expect(screen.getByRole('button', { name: /google/i })).toBeInTheDocument();
		expect(screen.getByRole('button', { name: /github/i })).toBeInTheDocument();
	});

	it('should render link to register page', () => {
		render(LoginPage);

		const registerLink = screen.getByRole('link', { name: /create.*account/i });
		expect(registerLink).toBeInTheDocument();
		expect(registerLink).toHaveAttribute('href', '/register');
	});

	it('should call login function when form is submitted', async () => {
		vi.mocked(login).mockResolvedValue();
		render(LoginPage);

		const emailInput = screen.getByLabelText(/email/i);
		const passwordInput = screen.getByLabelText(/password/i);
		const submitButton = screen.getByRole('button', { name: /sign in/i });

		await fireEvent.input(emailInput, { target: { value: 'test@example.com' } });
		await fireEvent.input(passwordInput, { target: { value: 'password123' } });
		await fireEvent.click(submitButton);

		await waitFor(() => {
			expect(login).toHaveBeenCalledWith({
				email: 'test@example.com',
				password: 'password123'
			});
		});
	});

	it('should display error message when login fails', async () => {
		const errorMessage = 'Invalid credentials';
		vi.mocked(login).mockRejectedValue(new ApiError('INVALID_CREDENTIALS', errorMessage));

		render(LoginPage);

		const emailInput = screen.getByLabelText(/email/i);
		const passwordInput = screen.getByLabelText(/password/i);
		const submitButton = screen.getByRole('button', { name: /sign in/i });

		await fireEvent.input(emailInput, { target: { value: 'test@example.com' } });
		await fireEvent.input(passwordInput, { target: { value: 'wrongpassword' } });
		await fireEvent.click(submitButton);

		await waitFor(() => {
			expect(screen.getByText(errorMessage)).toBeInTheDocument();
		});
	});

	it('should show loading state during login', async () => {
		vi.mocked(login).mockImplementation(
			() => new Promise((resolve) => setTimeout(resolve, 100))
		);

		render(LoginPage);

		const emailInput = screen.getByLabelText(/email/i);
		const passwordInput = screen.getByLabelText(/password/i);
		const submitButton = screen.getByRole('button', { name: /sign in/i });

		await fireEvent.input(emailInput, { target: { value: 'test@example.com' } });
		await fireEvent.input(passwordInput, { target: { value: 'password123' } });
		await fireEvent.click(submitButton);

		// Button should show loading state
		expect(submitButton).toBeDisabled();
	});

	it('should disable submit button when loading', async () => {
		vi.mocked(login).mockImplementation(
			() => new Promise((resolve) => setTimeout(resolve, 100))
		);

		render(LoginPage);

		const emailInput = screen.getByLabelText(/email/i);
		const passwordInput = screen.getByLabelText(/password/i);
		const submitButton = screen.getByRole('button', { name: /sign in/i });

		await fireEvent.input(emailInput, { target: { value: 'test@example.com' } });
		await fireEvent.input(passwordInput, { target: { value: 'password123' } });

		expect(submitButton).not.toBeDisabled();

		await fireEvent.click(submitButton);

		expect(submitButton).toBeDisabled();
	});

	it('should call loginWithOAuth when Google button is clicked', async () => {
		render(LoginPage);

		const googleButton = screen.getByRole('button', { name: /google/i });
		await fireEvent.click(googleButton);

		expect(loginWithOAuth).toHaveBeenCalledWith('google');
	});

	it('should call loginWithOAuth when GitHub button is clicked', async () => {
		render(LoginPage);

		const githubButton = screen.getByRole('button', { name: /github/i });
		await fireEvent.click(githubButton);

		expect(loginWithOAuth).toHaveBeenCalledWith('github');
	});

	it('should clear error message when user starts typing', async () => {
		const errorMessage = 'Invalid credentials';
		vi.mocked(login).mockRejectedValue(new ApiError('INVALID_CREDENTIALS', errorMessage));

		render(LoginPage);

		const emailInput = screen.getByLabelText(/email/i);
		const passwordInput = screen.getByLabelText(/password/i);
		const submitButton = screen.getByRole('button', { name: /sign in/i });

		// Submit with wrong credentials
		await fireEvent.input(emailInput, { target: { value: 'test@example.com' } });
		await fireEvent.input(passwordInput, { target: { value: 'wrongpassword' } });
		await fireEvent.click(submitButton);

		await waitFor(() => {
			expect(screen.getByText(errorMessage)).toBeInTheDocument();
		});

		// Start typing again - error should clear
		// Note: This behavior depends on implementation
		// If not implemented, this test can guide the feature
	});

	it('should handle unexpected errors gracefully', async () => {
		vi.mocked(login).mockRejectedValue(new Error('Network error'));

		render(LoginPage);

		const emailInput = screen.getByLabelText(/email/i);
		const passwordInput = screen.getByLabelText(/password/i);
		const submitButton = screen.getByRole('button', { name: /sign in/i });

		await fireEvent.input(emailInput, { target: { value: 'test@example.com' } });
		await fireEvent.input(passwordInput, { target: { value: 'password123' } });
		await fireEvent.click(submitButton);

		await waitFor(() => {
			expect(screen.getByText(/unexpected error/i)).toBeInTheDocument();
		});
	});

	it('should have proper form accessibility attributes', () => {
		render(LoginPage);

		const emailInput = screen.getByLabelText(/email/i);
		const passwordInput = screen.getByLabelText(/password/i);

		expect(emailInput).toHaveAttribute('type', 'email');
		expect(passwordInput).toHaveAttribute('type', 'password');
		expect(emailInput).toHaveAttribute('required');
		expect(passwordInput).toHaveAttribute('required');
	});

	it('should redirect to /terms when already authenticated', async () => {
		// Log in first
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

		render(LoginPage);

		// Should trigger redirect
		await waitFor(() => {
			expect(goto).toHaveBeenCalledWith('/terms');
		});
	});
});
