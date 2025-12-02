/**
 * Unit tests for auth utilities
 */

import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { get } from 'svelte/store';
import type { User } from '$lib/stores/auth';

// Mock modules before importing
vi.mock('$lib/utils/api', () => ({
	api: {
		get: vi.fn(),
		post: vi.fn()
	},
	ApiError: class ApiError extends Error {
		constructor(public code: string, message: string) {
			super(message);
			this.name = 'ApiError';
		}
	}
}));

vi.mock('$lib/stores/auth', () => {
	const mockStore = {
		subscribe: vi.fn(),
		login: vi.fn(),
		logout: vi.fn(),
		updateUser: vi.fn(),
		updateAccessToken: vi.fn(),
		setLoading: vi.fn()
	};

	return {
		authStore: mockStore
	};
});

vi.mock('$app/navigation', () => ({
	goto: vi.fn()
}));

// Import after mocks are set up
import {
	login,
	register,
	logout,
	refreshAccessToken,
	getCurrentUser,
	changePassword,
	loginWithOAuth,
	OAUTH_URLS
} from './auth';
import { api, ApiError } from '$lib/utils/api';
import { authStore } from '$lib/stores/auth';
import { goto } from '$app/navigation';

describe('auth utilities', () => {
	const mockUser: User = {
		id: 'user-123',
		email: 'test@example.com',
		first_name: 'John',
		last_name: 'Doe',
		language: 'en',
		adoption_level: 'quick-project',
		is_active: true,
		created_at: '2025-01-01T00:00:00Z'
	};

	const mockLoginResponse = {
		access_token: 'mock-access-token',
		refresh_token: 'mock-refresh-token',
		token_type: 'bearer',
		expires_in: 3600,
		user: mockUser
	};

	beforeEach(() => {
		vi.clearAllMocks();
	});

	afterEach(() => {
		vi.resetAllMocks();
	});

	describe('login()', () => {
		it('should call API with correct credentials', async () => {
			const credentials = {
				email: 'test@example.com',
				password: 'password123'
			};

			vi.mocked(api.post).mockResolvedValue(mockLoginResponse);

			await login(credentials);

			expect(api.post).toHaveBeenCalledWith('/auth/login', credentials);
		});

		it('should update authStore on successful login', async () => {
			const credentials = {
				email: 'test@example.com',
				password: 'password123'
			};

			vi.mocked(api.post).mockResolvedValue(mockLoginResponse);

			await login(credentials);

			expect(authStore.login).toHaveBeenCalledWith(
				mockUser,
				'mock-access-token',
				'mock-refresh-token'
			);
		});

		it('should set loading state during request', async () => {
			const credentials = {
				email: 'test@example.com',
				password: 'password123'
			};

			vi.mocked(api.post).mockResolvedValue(mockLoginResponse);

			await login(credentials);

			expect(authStore.setLoading).toHaveBeenCalledWith(true);
			expect(authStore.setLoading).toHaveBeenCalledWith(false);
		});

		it('should set loading to false even if API call fails', async () => {
			const credentials = {
				email: 'test@example.com',
				password: 'wrongpassword'
			};

			vi.mocked(api.post).mockRejectedValue(new ApiError('INVALID_CREDENTIALS', 'Invalid credentials'));

			await expect(login(credentials)).rejects.toThrow('Invalid credentials');

			expect(authStore.setLoading).toHaveBeenCalledWith(true);
			expect(authStore.setLoading).toHaveBeenCalledWith(false);
		});

		it('should propagate API errors', async () => {
			const credentials = {
				email: 'test@example.com',
				password: 'wrongpassword'
			};

			const error = new ApiError('INVALID_CREDENTIALS', 'Invalid email or password');
			vi.mocked(api.post).mockRejectedValue(error);

			await expect(login(credentials)).rejects.toThrow('Invalid email or password');
			expect(authStore.login).not.toHaveBeenCalled();
		});
	});

	describe('register()', () => {
		const registerData = {
			email: 'new@example.com',
			password: 'password123',
			first_name: 'Jane',
			last_name: 'Doe',
			language: 'fr'
		};

		it('should call API with registration data', async () => {
			vi.mocked(api.post).mockResolvedValue(mockLoginResponse);

			await register(registerData);

			expect(api.post).toHaveBeenCalledWith('/auth/register', registerData);
		});

		it('should default language to fr if not provided', async () => {
			const dataWithoutLanguage = {
				email: 'new@example.com',
				password: 'password123',
				first_name: 'Jane',
				last_name: 'Doe'
			};

			vi.mocked(api.post).mockResolvedValue(mockLoginResponse);

			await register(dataWithoutLanguage);

			expect(api.post).toHaveBeenCalledWith('/auth/register', {
				...dataWithoutLanguage,
				language: 'fr'
			});
		});

		it('should update authStore on successful registration', async () => {
			vi.mocked(api.post).mockResolvedValue(mockLoginResponse);

			await register(registerData);

			expect(authStore.login).toHaveBeenCalledWith(
				mockUser,
				'mock-access-token',
				'mock-refresh-token'
			);
		});

		it('should set loading state during registration', async () => {
			vi.mocked(api.post).mockResolvedValue(mockLoginResponse);

			await register(registerData);

			expect(authStore.setLoading).toHaveBeenCalledWith(true);
			expect(authStore.setLoading).toHaveBeenCalledWith(false);
		});

		it('should handle duplicate email error', async () => {
			const error = new ApiError('EMAIL_EXISTS', 'This email is already registered');
			vi.mocked(api.post).mockRejectedValue(error);

			await expect(register(registerData)).rejects.toThrow('This email is already registered');
			expect(authStore.login).not.toHaveBeenCalled();
		});

		it('should set loading to false on error', async () => {
			vi.mocked(api.post).mockRejectedValue(new ApiError('EMAIL_EXISTS', 'Email exists'));

			await expect(register(registerData)).rejects.toThrow();

			expect(authStore.setLoading).toHaveBeenCalledWith(true);
			expect(authStore.setLoading).toHaveBeenCalledWith(false);
		});
	});

	describe('logout()', () => {
		it('should call logout API endpoint', async () => {
			vi.mocked(api.post).mockResolvedValue({});

			await logout();

			expect(api.post).toHaveBeenCalledWith('/auth/logout');
		});

		it('should clear authStore', async () => {
			vi.mocked(api.post).mockResolvedValue({});

			await logout();

			expect(authStore.logout).toHaveBeenCalled();
		});

		it('should redirect to homepage', async () => {
			vi.mocked(api.post).mockResolvedValue({});

			await logout();

			expect(goto).toHaveBeenCalledWith('/');
		});

		it('should clear authStore even if API call fails', async () => {
			vi.mocked(api.post).mockRejectedValue(new Error('Network error'));

			await logout();

			expect(authStore.logout).toHaveBeenCalled();
			expect(goto).toHaveBeenCalledWith('/');
		});

		it('should not throw error if API call fails', async () => {
			vi.mocked(api.post).mockRejectedValue(new Error('Network error'));

			await expect(logout()).resolves.not.toThrow();
		});
	});

	describe('refreshAccessToken()', () => {
		const refreshToken = 'mock-refresh-token';

		it('should call refresh API with refresh token', async () => {
			const response = { access_token: 'new-access-token' };
			vi.mocked(api.post).mockResolvedValue(response);

			await refreshAccessToken(refreshToken);

			expect(api.post).toHaveBeenCalledWith('/auth/refresh', {
				refresh_token: refreshToken
			});
		});

		it('should update access token in store on success', async () => {
			const response = { access_token: 'new-access-token' };
			vi.mocked(api.post).mockResolvedValue(response);

			const result = await refreshAccessToken(refreshToken);

			expect(authStore.updateAccessToken).toHaveBeenCalledWith('new-access-token');
			expect(result).toBe('new-access-token');
		});

		it('should return new access token on success', async () => {
			const response = { access_token: 'new-access-token' };
			vi.mocked(api.post).mockResolvedValue(response);

			const result = await refreshAccessToken(refreshToken);

			expect(result).toBe('new-access-token');
		});

		it('should logout user if refresh fails', async () => {
			vi.mocked(api.post).mockRejectedValue(new ApiError('INVALID_REFRESH_TOKEN', 'Invalid token'));

			const result = await refreshAccessToken(refreshToken);

			expect(authStore.logout).toHaveBeenCalled();
			expect(result).toBeNull();
		});

		it('should return null if refresh fails', async () => {
			vi.mocked(api.post).mockRejectedValue(new Error('Network error'));

			const result = await refreshAccessToken(refreshToken);

			expect(result).toBeNull();
		});

		it('should not update token if refresh fails', async () => {
			vi.mocked(api.post).mockRejectedValue(new Error('Failed'));

			await refreshAccessToken(refreshToken);

			expect(authStore.updateAccessToken).not.toHaveBeenCalled();
		});
	});

	describe('getCurrentUser()', () => {
		it('should call API to get current user', async () => {
			vi.mocked(api.get).mockResolvedValue(mockUser);

			await getCurrentUser();

			expect(api.get).toHaveBeenCalledWith('/auth/me');
		});

		it('should update authStore with user data on success', async () => {
			vi.mocked(api.get).mockResolvedValue(mockUser);

			const result = await getCurrentUser();

			expect(authStore.updateUser).toHaveBeenCalledWith(mockUser);
			expect(result).toEqual(mockUser);
		});

		it('should return user data on success', async () => {
			vi.mocked(api.get).mockResolvedValue(mockUser);

			const result = await getCurrentUser();

			expect(result).toEqual(mockUser);
		});

		it('should return null if API call fails', async () => {
			vi.mocked(api.get).mockRejectedValue(new Error('Unauthorized'));

			const result = await getCurrentUser();

			expect(result).toBeNull();
		});

		it('should not update store if API call fails', async () => {
			vi.mocked(api.get).mockRejectedValue(new Error('Failed'));

			await getCurrentUser();

			expect(authStore.updateUser).not.toHaveBeenCalled();
		});

		it('should handle 401 errors gracefully', async () => {
			vi.mocked(api.get).mockRejectedValue(new ApiError('AUTHENTICATION_REQUIRED', 'Unauthorized'));

			const result = await getCurrentUser();

			expect(result).toBeNull();
		});
	});

	describe('changePassword()', () => {
		const currentPassword = 'oldpassword123';
		const newPassword = 'newpassword123';

		it('should call API with passwords', async () => {
			vi.mocked(api.post).mockResolvedValue({ message: 'Password changed' });

			await changePassword(currentPassword, newPassword);

			expect(api.post).toHaveBeenCalledWith('/auth/change-password', {
				current_password: currentPassword,
				new_password: newPassword
			});
		});

		it('should complete successfully on API success', async () => {
			vi.mocked(api.post).mockResolvedValue({ message: 'Success' });

			await expect(changePassword(currentPassword, newPassword)).resolves.not.toThrow();
		});

		it('should propagate API errors', async () => {
			const error = new ApiError('INVALID_PASSWORD', 'Current password is incorrect');
			vi.mocked(api.post).mockRejectedValue(error);

			await expect(changePassword(currentPassword, newPassword)).rejects.toThrow(
				'Current password is incorrect'
			);
		});

		it('should handle network errors', async () => {
			vi.mocked(api.post).mockRejectedValue(new Error('Network error'));

			await expect(changePassword(currentPassword, newPassword)).rejects.toThrow('Network error');
		});
	});

	describe('OAuth', () => {
		describe('OAUTH_URLS', () => {
			it('should have Google OAuth URL', () => {
				expect(OAUTH_URLS.google).toBeDefined();
				expect(typeof OAUTH_URLS.google).toBe('string');
			});

			it('should have GitHub OAuth URL', () => {
				expect(OAUTH_URLS.github).toBeDefined();
				expect(typeof OAUTH_URLS.github).toBe('string');
			});

			it('should use default URLs if env vars not set', () => {
				expect(OAUTH_URLS.google).toBe('/auth/oauth/google');
				expect(OAUTH_URLS.github).toBe('/auth/oauth/github');
			});
		});

		describe('loginWithOAuth()', () => {
			let originalLocation: Location;

			beforeEach(() => {
				// Mock window.location
				originalLocation = window.location;
				delete (window as any).location;
				window.location = { href: '' } as Location;
			});

			afterEach(() => {
				window.location = originalLocation;
			});

			it('should redirect to Google OAuth URL', () => {
				loginWithOAuth('google');

				expect(window.location.href).toBe('/auth/oauth/google');
			});

			it('should redirect to GitHub OAuth URL', () => {
				loginWithOAuth('github');

				expect(window.location.href).toBe('/auth/oauth/github');
			});
		});
	});

	describe('Error Handling', () => {
		it('should handle ApiError correctly', async () => {
			const apiError = new ApiError('TEST_ERROR', 'Test error message');
			vi.mocked(api.post).mockRejectedValue(apiError);

			await expect(login({ email: 'test@test.com', password: 'pass' })).rejects.toThrow(
				'Test error message'
			);
		});

		it('should handle generic errors', async () => {
			vi.mocked(api.post).mockRejectedValue(new Error('Generic error'));

			await expect(login({ email: 'test@test.com', password: 'pass' })).rejects.toThrow(
				'Generic error'
			);
		});

		it('should handle network failures gracefully in logout', async () => {
			vi.mocked(api.post).mockRejectedValue(new Error('Network failure'));

			// Should not throw, should still logout locally
			await expect(logout()).resolves.not.toThrow();
			expect(authStore.logout).toHaveBeenCalled();
		});
	});

	describe('Loading State Management', () => {
		it('should always reset loading state in login', async () => {
			vi.mocked(api.post).mockResolvedValue(mockLoginResponse);

			await login({ email: 'test@test.com', password: 'pass' });

			const setLoadingCalls = vi.mocked(authStore.setLoading).mock.calls;
			expect(setLoadingCalls).toContainEqual([true]);
			expect(setLoadingCalls).toContainEqual([false]);
		});

		it('should always reset loading state in register', async () => {
			vi.mocked(api.post).mockResolvedValue(mockLoginResponse);

			await register({
				email: 'test@test.com',
				password: 'pass',
				first_name: 'Test',
				last_name: 'User'
			});

			const setLoadingCalls = vi.mocked(authStore.setLoading).mock.calls;
			expect(setLoadingCalls).toContainEqual([true]);
			expect(setLoadingCalls).toContainEqual([false]);
		});

		it('should reset loading on error', async () => {
			vi.mocked(api.post).mockRejectedValue(new Error('Failed'));

			try {
				await login({ email: 'test@test.com', password: 'pass' });
			} catch {
				// Expected to throw
			}

			expect(authStore.setLoading).toHaveBeenCalledWith(false);
		});
	});
});
