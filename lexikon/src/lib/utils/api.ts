import type { ApiResponse } from '$types';
import { get } from 'svelte/store';
import { authStore } from '$lib/stores/auth';

const API_BASE_URL = '/api';

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
			// If unauthorized and we have a refresh token, try to refresh
			if (response.status === 401 && data.error?.code === 'INVALID_TOKEN') {
				const auth = get(authStore);
				if (auth.refreshToken) {
					// Token refresh will be handled by auth utils
					// For now, just throw the error
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
