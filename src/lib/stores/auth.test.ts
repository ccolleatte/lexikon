/**
 * Unit tests for auth store
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { get } from 'svelte/store';
import { authStore, isAuthenticated, user, accessToken, hasAdoptionLevel } from './auth';
import type { User } from './auth';

describe('authStore', () => {
	const mockUser: User = {
		id: 'user-123',
		email: 'test@example.com',
		first_name: 'John',
		last_name: 'Doe',
		language: 'en',
		adoption_level: 'research-project',
		is_active: true,
		created_at: '2025-01-01T00:00:00Z'
	};

	const mockTokens = {
		accessToken: 'mock-access-token',
		refreshToken: 'mock-refresh-token'
	};

	beforeEach(() => {
		localStorage.clear();
		authStore.reset();
	});

	describe('Initial State', () => {
		it('should initialize with unauthenticated state', () => {
			const state = get(authStore);

			expect(state.user).toBeNull();
			expect(state.accessToken).toBeNull();
			expect(state.refreshToken).toBeNull();
			expect(state.isAuthenticated).toBe(false);
			expect(state.isLoading).toBe(false);
		});

		it('should have isAuthenticated derived store as false initially', () => {
			expect(get(isAuthenticated)).toBe(false);
		});

		it('should have user derived store as null initially', () => {
			expect(get(user)).toBeNull();
		});

		it('should have accessToken derived store as null initially', () => {
			expect(get(accessToken)).toBeNull();
		});
	});

	describe('login()', () => {
		it('should set auth state on login', () => {
			authStore.login(mockUser, mockTokens.accessToken, mockTokens.refreshToken);

			const state = get(authStore);
			expect(state.user).toEqual(mockUser);
			expect(state.accessToken).toBe(mockTokens.accessToken);
			expect(state.refreshToken).toBe(mockTokens.refreshToken);
			expect(state.isAuthenticated).toBe(true);
			expect(state.isLoading).toBe(false);
		});

		it('should update isAuthenticated derived store on login', () => {
			authStore.login(mockUser, mockTokens.accessToken, mockTokens.refreshToken);

			expect(get(isAuthenticated)).toBe(true);
		});

		it('should update user derived store on login', () => {
			authStore.login(mockUser, mockTokens.accessToken, mockTokens.refreshToken);

			expect(get(user)).toEqual(mockUser);
		});

		it('should update accessToken derived store on login', () => {
			authStore.login(mockUser, mockTokens.accessToken, mockTokens.refreshToken);

			expect(get(accessToken)).toBe(mockTokens.accessToken);
		});

		it('should persist auth state to localStorage on login', () => {
			authStore.login(mockUser, mockTokens.accessToken, mockTokens.refreshToken);

			const stored = localStorage.getItem('lexikon-auth');
			expect(stored).not.toBeNull();

			const parsed = JSON.parse(stored!);
			expect(parsed.user).toEqual(mockUser);
			expect(parsed.accessToken).toBe(mockTokens.accessToken);
			expect(parsed.refreshToken).toBe(mockTokens.refreshToken);
			expect(parsed.isAuthenticated).toBe(true);
		});
	});

	describe('logout()', () => {
		beforeEach(() => {
			// Login first
			authStore.login(mockUser, mockTokens.accessToken, mockTokens.refreshToken);
		});

		it('should clear auth state on logout', () => {
			authStore.logout();

			const state = get(authStore);
			expect(state.user).toBeNull();
			expect(state.accessToken).toBeNull();
			expect(state.refreshToken).toBeNull();
			expect(state.isAuthenticated).toBe(false);
			expect(state.isLoading).toBe(false);
		});

		it('should update isAuthenticated to false on logout', () => {
			authStore.logout();

			expect(get(isAuthenticated)).toBe(false);
		});

		it('should clear localStorage on logout', () => {
			authStore.logout();

			const stored = localStorage.getItem('lexikon-auth');
			expect(stored).toBeNull();
		});
	});

	describe('updateUser()', () => {
		beforeEach(() => {
			authStore.login(mockUser, mockTokens.accessToken, mockTokens.refreshToken);
		});

		it('should update user information', () => {
			const updatedUser: User = {
				...mockUser,
				first_name: 'Jane',
				last_name: 'Smith'
			};

			authStore.updateUser(updatedUser);

			const state = get(authStore);
			expect(state.user).toEqual(updatedUser);
			expect(state.user?.first_name).toBe('Jane');
			expect(state.user?.last_name).toBe('Smith');
		});

		it('should preserve tokens when updating user', () => {
			const updatedUser: User = {
				...mockUser,
				email: 'newemail@example.com'
			};

			authStore.updateUser(updatedUser);

			const state = get(authStore);
			expect(state.accessToken).toBe(mockTokens.accessToken);
			expect(state.refreshToken).toBe(mockTokens.refreshToken);
		});

		it('should persist updated user to localStorage', () => {
			const updatedUser: User = {
				...mockUser,
				institution: 'Test University'
			};

			authStore.updateUser(updatedUser);

			const stored = localStorage.getItem('lexikon-auth');
			const parsed = JSON.parse(stored!);
			expect(parsed.user.institution).toBe('Test University');
		});
	});

	describe('updateAccessToken()', () => {
		beforeEach(() => {
			authStore.login(mockUser, mockTokens.accessToken, mockTokens.refreshToken);
		});

		it('should update access token', () => {
			const newToken = 'new-access-token';

			authStore.updateAccessToken(newToken);

			const state = get(authStore);
			expect(state.accessToken).toBe(newToken);
		});

		it('should preserve user and refresh token when updating access token', () => {
			const newToken = 'new-access-token';

			authStore.updateAccessToken(newToken);

			const state = get(authStore);
			expect(state.user).toEqual(mockUser);
			expect(state.refreshToken).toBe(mockTokens.refreshToken);
		});

		it('should persist updated access token to localStorage', () => {
			const newToken = 'new-access-token';

			authStore.updateAccessToken(newToken);

			const stored = localStorage.getItem('lexikon-auth');
			const parsed = JSON.parse(stored!);
			expect(parsed.accessToken).toBe(newToken);
		});
	});

	describe('setLoading()', () => {
		it('should set loading state to true', () => {
			authStore.setLoading(true);

			const state = get(authStore);
			expect(state.isLoading).toBe(true);
		});

		it('should set loading state to false', () => {
			authStore.setLoading(true);
			authStore.setLoading(false);

			const state = get(authStore);
			expect(state.isLoading).toBe(false);
		});

		it('should not persist loading state to localStorage', () => {
			authStore.setLoading(true);

			const stored = localStorage.getItem('lexikon-auth');
			const parsed = JSON.parse(stored!);
			expect(parsed.isLoading).toBeUndefined();
		});
	});

	describe('reset()', () => {
		beforeEach(() => {
			authStore.login(mockUser, mockTokens.accessToken, mockTokens.refreshToken);
		});

		it('should reset to initial state', () => {
			authStore.reset();

			const state = get(authStore);
			expect(state.user).toBeNull();
			expect(state.accessToken).toBeNull();
			expect(state.refreshToken).toBeNull();
			expect(state.isAuthenticated).toBe(false);
			expect(state.isLoading).toBe(false);
		});
	});

	describe('localStorage persistence', () => {
		it('should restore state from localStorage on initialization', () => {
			// Manually set localStorage
			const storedState = {
				user: mockUser,
				accessToken: mockTokens.accessToken,
				refreshToken: mockTokens.refreshToken,
				isAuthenticated: true
			};
			localStorage.setItem('lexikon-auth', JSON.stringify(storedState));

			// Reset and re-initialize
			authStore.reset();

			const state = get(authStore);
			expect(state.user).toEqual(mockUser);
			expect(state.accessToken).toBe(mockTokens.accessToken);
			expect(state.isAuthenticated).toBe(true);
		});

		it('should handle corrupted localStorage data gracefully', () => {
			localStorage.setItem('lexikon-auth', 'invalid json {{{');

			// Should not throw error
			authStore.reset();

			const state = get(authStore);
			expect(state.user).toBeNull();
			expect(state.isAuthenticated).toBe(false);
		});

		it('should handle missing localStorage gracefully', () => {
			// localStorage is clear, no data
			authStore.reset();

			const state = get(authStore);
			expect(state.user).toBeNull();
			expect(state.isAuthenticated).toBe(false);
		});
	});

	describe('hasAdoptionLevel() derived store', () => {
		it('should return false when no user', () => {
			const checker = get(hasAdoptionLevel);
			expect(checker('quick-project')).toBe(false);
		});

		it('should return true for exact match', () => {
			authStore.login(mockUser, mockTokens.accessToken, mockTokens.refreshToken);

			const checker = get(hasAdoptionLevel);
			expect(checker('research-project')).toBe(true);
		});

		it('should return true for level above requirement', () => {
			// User has research-project (level 2)
			authStore.login(mockUser, mockTokens.accessToken, mockTokens.refreshToken);

			const checker = get(hasAdoptionLevel);
			// Should have access to quick-project (level 1) features
			expect(checker('quick-project')).toBe(true);
		});

		it('should return false for level below requirement', () => {
			// User has research-project (level 2)
			authStore.login(mockUser, mockTokens.accessToken, mockTokens.refreshToken);

			const checker = get(hasAdoptionLevel);
			// Should NOT have access to production-api (level 3) features
			expect(checker('production-api')).toBe(false);
		});

		it('should handle all adoption levels correctly', () => {
			const levels: Array<'quick-project' | 'research-project' | 'production-api'> = [
				'quick-project',
				'research-project',
				'production-api'
			];

			levels.forEach((level, index) => {
				const userWithLevel: User = { ...mockUser, adoption_level: level };
				authStore.login(userWithLevel, mockTokens.accessToken, mockTokens.refreshToken);

				const checker = get(hasAdoptionLevel);

				// Should have access to all levels up to and including own level
				for (let i = 0; i <= index; i++) {
					expect(checker(levels[i])).toBe(true);
				}

				// Should NOT have access to levels above
				for (let i = index + 1; i < levels.length; i++) {
					expect(checker(levels[i])).toBe(false);
				}
			});
		});
	});
});
