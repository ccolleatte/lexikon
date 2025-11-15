import type { ApiResponse } from '$types';

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

export async function apiCall<T>(
	endpoint: string,
	options: RequestInit = {}
): Promise<T> {
	const url = `${API_BASE_URL}${endpoint}`;

	const defaultOptions: RequestInit = {
		headers: {
			'Content-Type': 'application/json',
			...options.headers
		},
		...options
	};

	try {
		const response = await fetch(url, defaultOptions);
		const data: ApiResponse<T> = await response.json();

		if (!response.ok || !data.success) {
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
