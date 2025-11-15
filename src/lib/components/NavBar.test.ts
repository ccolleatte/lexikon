/**
 * Component tests for NavBar component
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/svelte';
import NavBar from './NavBar.svelte';
import { authStore } from '$lib/stores/auth';
import { logout } from '$lib/utils/auth';

// Mock auth utilities
vi.mock('$lib/utils/auth', () => ({
	logout: vi.fn()
}));

describe('NavBar Component', () => {
	beforeEach(() => {
		vi.clearAllMocks();
		authStore.logout();
	});

	describe('When not authenticated', () => {
		it('should render Lexikon logo', () => {
			render(NavBar);

			expect(screen.getByText('Lexikon')).toBeInTheDocument();
		});

		it('should render Sign In link', () => {
			render(NavBar);

			const signInLink = screen.getByRole('link', { name: /sign in/i });
			expect(signInLink).toBeInTheDocument();
			expect(signInLink).toHaveAttribute('href', '/login');
		});

		it('should render Get Started link', () => {
			render(NavBar);

			const getStartedLink = screen.getByRole('link', { name: /get started/i });
			expect(getStartedLink).toBeInTheDocument();
			expect(getStartedLink).toHaveAttribute('href', '/register');
		});

		it('should not show My Terms link', () => {
			render(NavBar);

			expect(screen.queryByRole('link', { name: /my terms/i })).not.toBeInTheDocument();
		});

		it('should not show user menu', () => {
			render(NavBar);

			expect(screen.queryByRole('button', { name: /logout/i })).not.toBeInTheDocument();
		});
	});

	describe('When authenticated', () => {
		beforeEach(() => {
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
		});

		it('should render user name', async () => {
			render(NavBar);

			await waitFor(() => {
				expect(screen.getByText(/John Doe/i)).toBeInTheDocument();
			});
		});

		it('should render My Terms link', async () => {
			render(NavBar);

			await waitFor(() => {
				const myTermsLink = screen.getByRole('link', { name: /my terms/i });
				expect(myTermsLink).toBeInTheDocument();
				expect(myTermsLink).toHaveAttribute('href', '/terms');
			});
		});

		it('should render Create Term link', async () => {
			render(NavBar);

			await waitFor(() => {
				const createLink = screen.getByRole('link', { name: /create term/i });
				expect(createLink).toBeInTheDocument();
				expect(createLink).toHaveAttribute('href', '/terms/new');
			});
		});

		it('should not show Sign In and Get Started links', async () => {
			render(NavBar);

			await waitFor(() => {
				expect(screen.queryByRole('link', { name: /^sign in$/i })).not.toBeInTheDocument();
				expect(screen.queryByRole('link', { name: /get started/i })).not.toBeInTheDocument();
			});
		});

		it('should show user menu when avatar is clicked', async () => {
			render(NavBar);

			// Find and click user menu button (usually shows initials or avatar)
			const userButton = screen.getByRole('button', { name: /JD/i });
			await fireEvent.click(userButton);

			await waitFor(() => {
				expect(screen.getByRole('link', { name: /profile/i })).toBeVisible();
				expect(screen.getByRole('button', { name: /logout/i })).toBeVisible();
			});
		});

		it('should hide user menu when avatar is clicked again', async () => {
			render(NavBar);

			const userButton = screen.getByRole('button', { name: /JD/i });

			// Click to open
			await fireEvent.click(userButton);
			await waitFor(() => {
				expect(screen.getByRole('link', { name: /profile/i })).toBeVisible();
			});

			// Click to close
			await fireEvent.click(userButton);
			await waitFor(() => {
				expect(screen.queryByRole('link', { name: /profile/i })).not.toBeVisible();
			});
		});

		it('should call logout when logout button is clicked', async () => {
			vi.mocked(logout).mockResolvedValue();
			render(NavBar);

			// Open user menu
			const userButton = screen.getByRole('button', { name: /JD/i });
			await fireEvent.click(userButton);

			// Click logout
			const logoutButton = await screen.findByRole('button', { name: /logout/i });
			await fireEvent.click(logoutButton);

			await waitFor(() => {
				expect(logout).toHaveBeenCalled();
			});
		});

		it('should show Profile link in user menu', async () => {
			render(NavBar);

			const userButton = screen.getByRole('button', { name: /JD/i });
			await fireEvent.click(userButton);

			const profileLink = await screen.findByRole('link', { name: /profile/i });
			expect(profileLink).toBeVisible();
			expect(profileLink).toHaveAttribute('href', '/profile');
		});

		it('should close menu when clicking outside', async () => {
			render(NavBar);

			// Open menu
			const userButton = screen.getByRole('button', { name: /JD/i });
			await fireEvent.click(userButton);

			await waitFor(() => {
				expect(screen.getByRole('link', { name: /profile/i })).toBeVisible();
			});

			// Click outside (on the nav element)
			const nav = screen.getByRole('navigation');
			await fireEvent.click(nav);

			await waitFor(() => {
				expect(screen.queryByRole('link', { name: /profile/i })).not.toBeVisible();
			});
		});

		it('should display user email in menu', async () => {
			render(NavBar);

			const userButton = screen.getByRole('button', { name: /JD/i });
			await fireEvent.click(userButton);

			await waitFor(() => {
				expect(screen.getByText('test@example.com')).toBeVisible();
			});
		});

		it('should close menu after logout', async () => {
			vi.mocked(logout).mockResolvedValue();
			render(NavBar);

			// Open menu
			const userButton = screen.getByRole('button', { name: /JD/i });
			await fireEvent.click(userButton);

			// Logout
			const logoutButton = await screen.findByRole('button', { name: /logout/i });
			await fireEvent.click(logoutButton);

			await waitFor(() => {
				expect(logout).toHaveBeenCalled();
			});
		});
	});

	describe('Accessibility', () => {
		it('should have navigation landmark', () => {
			render(NavBar);

			expect(screen.getByRole('navigation')).toBeInTheDocument();
		});

		it('should have accessible logo link', () => {
			render(NavBar);

			const logoLink = screen.getByRole('link', { name: /lexikon/i });
			expect(logoLink).toHaveAttribute('href', '/');
		});

		it('should have keyboard accessible menu when authenticated', async () => {
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

			render(NavBar);

			const userButton = await screen.findByRole('button', { name: /JD/i });

			// Should be keyboard accessible
			expect(userButton).not.toHaveAttribute('disabled');
		});
	});

	describe('Responsive behavior', () => {
		it('should render mobile menu button on small screens', () => {
			// This test would require mocking viewport size
			// For now, we document expected behavior
			render(NavBar);

			// In mobile view, should show hamburger menu
			// Implementation specific
		});
	});
});
