import type { ApiResponse } from '$types';
import { get } from 'svelte/store';
import { authStore } from '$lib/stores/auth';
import { goto } from '$app/navigation';
import { browser } from '$app/environment';

const API_BASE_URL = '/api';

// Token refresh state to prevent multiple simultaneous refresh attempts
let isRefreshing = false;
let refreshPromise: Promise<string | null> | null = null;

/**
 * Attempt to refresh the access token using the refresh token
 * Uses a lock to prevent multiple simultaneous refresh attempts
 */
async function tryRefreshToken(): Promise<string | null> {
	const auth = get(authStore);

	if (!auth.refreshToken) {
		return null;
	}

	// If already refreshing, wait for the existing refresh to complete
	if (isRefreshing && refreshPromise) {
		return refreshPromise;
	}

	isRefreshing = true;
	refreshPromise = (async () => {
		try {
			const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ refresh_token: auth.refreshToken })
			});

			if (!response.ok) {
				return null;
			}

			const data: ApiResponse<{ access_token: string }> = await response.json();

			if (data.success && data.data?.access_token) {
				authStore.updateAccessToken(data.data.access_token);
				return data.data.access_token;
			}

			return null;
		} catch {
			return null;
		} finally {
			isRefreshing = false;
			refreshPromise = null;
		}
	})();

	return refreshPromise;
}

export class ApiError extends Error {
	constructor(
		public code: string,
		message: string,
		public details?: Record<string, string[]>
	) {
		super(message);
		this.name = 'ApiError';
	}
}

/**
 * Get authorization header with JWT token if authenticated
 */
function getAuthHeaders(): Record<string, string> {
	const auth = get(authStore);
	if (auth.accessToken) {
		return {
			Authorization: `Bearer ${auth.accessToken}`
		};
	}
	return {};
}

export async function apiCall<T>(
	endpoint: string,
	options: RequestInit = {}
): Promise<T> {
	const url = `${API_BASE_URL}${endpoint}`;

	const defaultOptions: RequestInit = {
		headers: {
			'Content-Type': 'application/json',
			...getAuthHeaders(),
			...options.headers
		},
		...options
	};

	try {
		const response = await fetch(url, defaultOptions);
		const data: ApiResponse<T> = await response.json();

		if (!response.ok || !data.success) {
			// If unauthorized, try to refresh the token
			if (response.status === 401) {
				const auth = get(authStore);

				// Only attempt refresh if we have a refresh token and aren't already in a refresh call
				if (auth.refreshToken && !endpoint.includes('/auth/refresh')) {
					const newToken = await tryRefreshToken();

					if (newToken) {
						// Retry the original request with the new token
						const retryOptions: RequestInit = {
							...defaultOptions,
							headers: {
								...defaultOptions.headers,
								Authorization: `Bearer ${newToken}`
							}
						};
						const retryResponse = await fetch(url, retryOptions);
						const retryData: ApiResponse<T> = await retryResponse.json();

						if (retryResponse.ok && retryData.success) {
							return retryData.data as T;
						}
					}

					// Token refresh failed - logout and redirect to login
					authStore.logout();
					if (browser) {
						goto('/login');
					}
					throw new ApiError(
						'AUTHENTICATION_REQUIRED',
						'Your session has expired. Please login again.'
					);
				}
			}

			throw new ApiError(
				data.error?.code || 'UNKNOWN_ERROR',
				data.error?.message || 'An error occurred',
				data.error?.details
			);
		}

		return data.data as T;
	} catch (error) {
		if (error instanceof ApiError) {
			throw error;
		}

		// Network or other errors
		throw new ApiError('NETWORK_ERROR', 'Failed to connect to server');
	}
}

export const api = {
	get: <T>(endpoint: string) => apiCall<T>(endpoint, { method: 'GET' }),

	post: <T>(endpoint: string, data?: unknown) =>
		apiCall<T>(endpoint, {
			method: 'POST',
			body: data ? JSON.stringify(data) : undefined
		}),

	put: <T>(endpoint: string, data?: unknown) =>
		apiCall<T>(endpoint, {
			method: 'PUT',
			body: data ? JSON.stringify(data) : undefined
		}),

	patch: <T>(endpoint: string, data?: unknown) =>
		apiCall<T>(endpoint, {
			method: 'PATCH',
			body: data ? JSON.stringify(data) : undefined
		}),

	delete: <T>(endpoint: string) => apiCall<T>(endpoint, { method: 'DELETE' })
};
