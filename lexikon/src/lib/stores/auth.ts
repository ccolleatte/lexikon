/**
 * Authentication store with JWT token management
 */

import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';

export interface User {
	id: string;
	email: string;
	first_name: string;
	last_name: string;
	institution?: string;
	primary_domain?: string;
	language: string;
	country?: string;
	adoption_level: 'quick-project' | 'research-project' | 'production-api';
	is_active: boolean;
	created_at: string;
}

export interface AuthState {
	user: User | null;
	accessToken: string | null;
	refreshToken: string | null;
	isAuthenticated: boolean;
	isLoading: boolean;
}

const STORAGE_KEY = 'lexikon-auth';

// Initialize from localStorage
function getInitialState(): AuthState {
	if (!browser) {
		return {
			user: null,
			accessToken: null,
			refreshToken: null,
			isAuthenticated: false,
			isLoading: false
		};
	}

	try {
		const stored = localStorage.getItem(STORAGE_KEY);
		if (stored) {
			const parsed = JSON.parse(stored);
			return {
				...parsed,
				isLoading: false,
				isAuthenticated: !!parsed.accessToken
			};
		}
	} catch (e) {
		console.error('Failed to load auth state:', e);
	}

	return {
		user: null,
		accessToken: null,
		refreshToken: null,
		isAuthenticated: false,
		isLoading: false
	};
}

// Create the store
function createAuthStore() {
	const { subscribe, set, update } = writable<AuthState>(getInitialState());

	// Save to localStorage whenever state changes
	if (browser) {
		subscribe((state) => {
			try {
				const { isLoading, ...toStore } = state;
				localStorage.setItem(STORAGE_KEY, JSON.stringify(toStore));
			} catch (e) {
				console.error('Failed to save auth state:', e);
			}
		});
	}

	return {
		subscribe,

		/**
		 * Set authentication state after login
		 */
		login(user: User, accessToken: string, refreshToken: string) {
			set({
				user,
				accessToken,
				refreshToken,
				isAuthenticated: true,
				isLoading: false
			});
		},

		/**
		 * Update user information
		 */
		updateUser(user: User) {
			update((state) => ({
				...state,
				user
			}));
		},

		/**
		 * Update access token (after refresh)
		 */
		updateAccessToken(accessToken: string) {
			update((state) => ({
				...state,
				accessToken
			}));
		},

		/**
		 * Logout and clear all auth data
		 */
		logout() {
			set({
				user: null,
				accessToken: null,
				refreshToken: null,
				isAuthenticated: false,
				isLoading: false
			});
			if (browser) {
				localStorage.removeItem(STORAGE_KEY);
			}
		},

		/**
		 * Set loading state
		 */
		setLoading(isLoading: boolean) {
			update((state) => ({
				...state,
				isLoading
			}));
		},

		/**
		 * Reset to initial state
		 */
		reset() {
			set(getInitialState());
		}
	};
}

export const authStore = createAuthStore();

// Derived stores for convenience
export const user = derived(authStore, ($auth) => $auth.user);
export const isAuthenticated = derived(authStore, ($auth) => $auth.isAuthenticated);
export const isLoading = derived(authStore, ($auth) => $auth.isLoading);
export const accessToken = derived(authStore, ($auth) => $auth.accessToken);
export const adoptionLevel = derived(authStore, ($auth) => $auth.user?.adoption_level);

/**
 * Check if user has minimum adoption level
 */
export const hasAdoptionLevel = derived(authStore, ($auth) => {
	return (minimumLevel: 'quick-project' | 'research-project' | 'production-api'): boolean => {
		if (!$auth.user) return false;

		const levels = {
			'quick-project': 1,
			'research-project': 2,
			'production-api': 3
		};

		const userLevel = levels[$auth.user.adoption_level] || 0;
		const requiredLevel = levels[minimumLevel] || 999;

		return userLevel >= requiredLevel;
	};
});
