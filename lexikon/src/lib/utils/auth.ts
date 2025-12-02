/**
 * Authentication utility functions
 */

import { api } from './api';
import { authStore } from '$lib/stores/auth';
import type { User } from '$lib/stores/auth';
import { goto } from '$app/navigation';

export interface LoginCredentials {
	email: string;
	password: string;
}

export interface RegisterData {
	email: string;
	password: string;
	first_name: string;
	last_name: string;
	language?: string;
}

export interface LoginResponse {
	access_token: string;
	refresh_token: string;
	token_type: string;
	expires_in: number;
	user: User;
}

/**
 * Login with email and password
 */
export async function login(credentials: LoginCredentials): Promise<void> {
	authStore.setLoading(true);

	try {
		const response = await api.post<LoginResponse>('/auth/login', credentials);

		authStore.login(response.user, response.access_token, response.refresh_token);
	} finally {
		authStore.setLoading(false);
	}
}

/**
 * Register a new account
 */
export async function register(data: RegisterData): Promise<void> {
	authStore.setLoading(true);

	try {
		const response = await api.post<LoginResponse>('/auth/register', {
			...data,
			language: data.language || 'fr'
		});

		authStore.login(response.user, response.access_token, response.refresh_token);
	} finally {
		authStore.setLoading(false);
	}
}

/**
 * Logout the current user
 */
export async function logout(): Promise<void> {
	try {
		// Call backend logout endpoint (for token blacklist in future)
		await api.post('/auth/logout');
	} catch (error) {
		// Continue with logout even if API call fails
		console.error('Logout API error:', error);
	} finally {
		authStore.logout();
		goto('/login');
	}
}

/**
 * Refresh the access token
 */
export async function refreshAccessToken(refreshToken: string): Promise<string | null> {
	try {
		const response = await api.post<{ access_token: string }>('/auth/refresh', {
			refresh_token: refreshToken
		});

		authStore.updateAccessToken(response.access_token);
		return response.access_token;
	} catch (error) {
		console.error('Token refresh failed:', error);
		// If refresh fails, logout the user
		authStore.logout();
		return null;
	}
}

/**
 * Get current user information from API
 */
export async function getCurrentUser(): Promise<User | null> {
	try {
		const user = await api.get<User>('/auth/me');
		authStore.updateUser(user);
		return user;
	} catch (error) {
		console.error('Failed to get current user:', error);
		return null;
	}
}

/**
 * Change password
 */
export async function changePassword(
	currentPassword: string,
	newPassword: string
): Promise<void> {
	await api.post('/auth/change-password', {
		current_password: currentPassword,
		new_password: newPassword
	});
}

/**
 * OAuth login URLs
 */
export const OAUTH_URLS = {
	google: import.meta.env.VITE_GOOGLE_OAUTH_URL || '/auth/oauth/google'
};

/**
 * Initiate OAuth login
 */
export function loginWithOAuth(provider: 'google'): void {
	const url = OAUTH_URLS[provider];
	window.location.href = url;
}
