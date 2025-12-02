/**
 * Unit tests for API client
 */

import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { writable } from 'svelte/store';
import type { AuthState } from '$lib/stores/auth';

// Mock modules before importing - must use factory function
vi.mock('$lib/stores/auth', () => {
	const { writable } = require('svelte/store');
	return {
		authStore: writable({
			user: null,
			accessToken: null,
			refreshToken: null,
			isAuthenticated: false,
			isLoading: false
		})
	};
});

// Import after mocks are set up
import { api, ApiError, apiCall } from './api';
import { authStore } from '$lib/stores/auth';

// Get reference to the mocked store for test manipulation
const mockAuthState = authStore as ReturnType<typeof writable<AuthState>>;

describe('API Client', () => {
	let mockFetch: ReturnType<typeof vi.fn>;

	beforeEach(() => {
		mockFetch = vi.fn();
		vi.stubGlobal('fetch', mockFetch);
		vi.clearAllMocks();
		// Reset auth store to unauthenticated state
		mockAuthState.set({
			user: null,
			accessToken: null,
			refreshToken: null,
			isAuthenticated: false,
			isLoading: false
		});
	});

	afterEach(() => {
		vi.unstubAllGlobals();
	});

	describe('ApiError', () => {
		it('should create ApiError with code and message', () => {
			const error = new ApiError('TEST_ERROR', 'Test error message');

			expect(error).toBeInstanceOf(Error);
			expect(error.name).toBe('ApiError');
			expect(error.code).toBe('TEST_ERROR');
			expect(error.message).toBe('Test error message');
			expect(error.details).toBeUndefined();
		});

		it('should create ApiError with details', () => {
			const details = {
				email: ['Invalid email format'],
				password: ['Password too short']
			};
			const error = new ApiError('VALIDATION_ERROR', 'Validation failed', details);

			expect(error.code).toBe('VALIDATION_ERROR');
			expect(error.message).toBe('Validation failed');
			expect(error.details).toEqual(details);
		});
	});

	describe('apiCall()', () => {
		const mockSuccessResponse = {
			success: true,
			data: { id: '123', name: 'Test' },
			error: null
		};

		it('should make successful GET request', async () => {
			mockFetch.mockResolvedValue({
				ok: true,
				json: async () => mockSuccessResponse
			});

			const result = await apiCall('/test');

			expect(mockFetch).toHaveBeenCalledWith(
				'/api/test',
				expect.objectContaining({
					headers: expect.objectContaining({
						'Content-Type': 'application/json'
					})
				})
			);
			expect(result).toEqual({ id: '123', name: 'Test' });
		});

		it('should make successful POST request with data', async () => {
			mockFetch.mockResolvedValue({
				ok: true,
				json: async () => mockSuccessResponse
			});

			const postData = { email: 'test@example.com', password: 'password123' };
			const result = await apiCall('/auth/login', {
				method: 'POST',
				body: JSON.stringify(postData)
			});

			expect(mockFetch).toHaveBeenCalledWith(
				'/api/auth/login',
				expect.objectContaining({
					method: 'POST',
					body: JSON.stringify(postData),
					headers: expect.objectContaining({
						'Content-Type': 'application/json'
					})
				})
			);
			expect(result).toEqual({ id: '123', name: 'Test' });
		});

		it('should include Authorization header when user is authenticated', async () => {
			// Mock authenticated user
			mockAuthState.set({
				user: { id: 'user-123' } as any,
				accessToken: 'mock-token',
				refreshToken: 'refresh-token',
				isAuthenticated: true,
				isLoading: false
			});

			mockFetch.mockResolvedValue({
				ok: true,
				json: async () => mockSuccessResponse
			});

			await apiCall('/protected');

			expect(mockFetch).toHaveBeenCalledWith(
				expect.any(String),
				expect.objectContaining({
					headers: expect.objectContaining({
						Authorization: 'Bearer mock-token'
					})
				})
			);
		});

		it('should not include Authorization header when user is not authenticated', async () => {
			// Mock unauthenticated user (default)
			mockFetch.mockResolvedValue({
				ok: true,
				json: async () => mockSuccessResponse
			});

			await apiCall('/public');

			const callHeaders = mockFetch.mock.calls[0][1].headers;
			expect(callHeaders).not.toHaveProperty('Authorization');
		});

		it('should merge custom headers with default headers', async () => {
			mockFetch.mockResolvedValue({
				ok: true,
				json: async () => mockSuccessResponse
			});

			await apiCall('/test', {
				headers: {
					'Content-Type': 'application/json',
					'X-Custom-Header': 'custom-value'
				}
			});

			expect(mockFetch).toHaveBeenCalledWith(
				'/api/test',
				expect.objectContaining({
					headers: expect.objectContaining({
						'Content-Type': 'application/json',
						'X-Custom-Header': 'custom-value'
					})
				})
			);
		});

		it('should throw ApiError when response is not ok', async () => {
			mockFetch.mockResolvedValue({
				ok: false,
				status: 400,
				json: async () => ({
					success: false,
					data: null,
					error: {
						code: 'VALIDATION_ERROR',
						message: 'Invalid input',
						details: { email: ['Invalid format'] }
					}
				})
			});

			await expect(apiCall('/test')).rejects.toThrow(ApiError);
			await expect(apiCall('/test')).rejects.toThrow('Invalid input');

			try {
				await apiCall('/test');
			} catch (error) {
				expect(error).toBeInstanceOf(ApiError);
				expect((error as ApiError).code).toBe('VALIDATION_ERROR');
				expect((error as ApiError).details).toEqual({ email: ['Invalid format'] });
			}
		});

		it('should throw ApiError when success is false', async () => {
			mockFetch.mockResolvedValue({
				ok: true,
				json: async () => ({
					success: false,
					data: null,
					error: {
						code: 'CUSTOM_ERROR',
						message: 'Something went wrong'
					}
				})
			});

			await expect(apiCall('/test')).rejects.toThrow(ApiError);
			await expect(apiCall('/test')).rejects.toThrow('Something went wrong');
		});

		it('should throw AUTHENTICATION_REQUIRED error on 401 with INVALID_TOKEN', async () => {
			// Mock authenticated user with refresh token
			mockAuthState.set({
				user: { id: 'user-123' } as any,
				accessToken: 'expired-token',
				refreshToken: 'refresh-token',
				isAuthenticated: true,
				isLoading: false
			});

			mockFetch.mockResolvedValue({
				ok: false,
				status: 401,
				json: async () => ({
					success: false,
					data: null,
					error: {
						code: 'INVALID_TOKEN',
						message: 'Token has expired'
					}
				})
			});

			try {
				await apiCall('/protected');
				expect.fail('Should have thrown');
			} catch (error) {
				expect(error).toBeInstanceOf(ApiError);
				expect((error as ApiError).code).toBe('AUTHENTICATION_REQUIRED');
				expect((error as ApiError).message).toBe(
					'Your session has expired. Please login again.'
				);
			}
		});

		it('should throw original error on 401 when no refresh token', async () => {
			// Mock unauthenticated user (already set in beforeEach, but explicit for clarity)
			mockAuthState.set({
				user: null,
				accessToken: null,
				refreshToken: null,
				isAuthenticated: false,
				isLoading: false
			});

			mockFetch.mockResolvedValue({
				ok: false,
				status: 401,
				json: async () => ({
					success: false,
					data: null,
					error: {
						code: 'UNAUTHORIZED',
						message: 'Authentication required'
					}
				})
			});

			try {
				await apiCall('/protected');
				expect.fail('Should have thrown');
			} catch (error) {
				expect(error).toBeInstanceOf(ApiError);
				expect((error as ApiError).code).toBe('UNAUTHORIZED');
			}
		});

		it('should throw NETWORK_ERROR when fetch fails', async () => {
			mockFetch.mockRejectedValue(new Error('Network failure'));

			try {
				await apiCall('/test');
				expect.fail('Should have thrown');
			} catch (error) {
				expect(error).toBeInstanceOf(ApiError);
				expect((error as ApiError).code).toBe('NETWORK_ERROR');
				expect((error as ApiError).message).toBe('Failed to connect to server');
			}
		});

		it('should preserve ApiError when thrown during fetch', async () => {
			const customError = new ApiError('CUSTOM_CODE', 'Custom message');
			mockFetch.mockRejectedValue(customError);

			try {
				await apiCall('/test');
				expect.fail('Should have thrown');
			} catch (error) {
				expect(error).toBe(customError);
				expect((error as ApiError).code).toBe('CUSTOM_CODE');
			}
		});

		it('should throw UNKNOWN_ERROR when error structure is missing', async () => {
			mockFetch.mockResolvedValue({
				ok: false,
				json: async () => ({
					success: false,
					data: null
					// No error field
				})
			});

			try {
				await apiCall('/test');
				expect.fail('Should have thrown');
			} catch (error) {
				expect(error).toBeInstanceOf(ApiError);
				expect((error as ApiError).code).toBe('UNKNOWN_ERROR');
				expect((error as ApiError).message).toBe('An error occurred');
			}
		});
	});

	describe('api.get()', () => {
		it('should call apiCall with GET method', async () => {
			const mockResponse = {
				success: true,
				data: { items: [] },
				error: null
			};

			mockFetch.mockResolvedValue({
				ok: true,
				json: async () => mockResponse
			});

			const result = await api.get('/items');

			expect(mockFetch).toHaveBeenCalledWith(
				expect.stringContaining('/items'),
				expect.objectContaining({
					method: 'GET'
				})
			);
			expect(result).toEqual({ items: [] });
		});
	});

	describe('api.post()', () => {
		it('should call apiCall with POST method and data', async () => {
			const mockResponse = {
				success: true,
				data: { id: '123' },
				error: null
			};

			mockFetch.mockResolvedValue({
				ok: true,
				json: async () => mockResponse
			});

			const postData = { name: 'Test Item' };
			const result = await api.post('/items', postData);

			expect(mockFetch).toHaveBeenCalledWith(
				expect.stringContaining('/items'),
				expect.objectContaining({
					method: 'POST',
					body: JSON.stringify(postData)
				})
			);
			expect(result).toEqual({ id: '123' });
		});

		it('should handle POST without data', async () => {
			const mockResponse = {
				success: true,
				data: { status: 'ok' },
				error: null
			};

			mockFetch.mockResolvedValue({
				ok: true,
				json: async () => mockResponse
			});

			await api.post('/action');

			expect(mockFetch).toHaveBeenCalledWith(
				expect.any(String),
				expect.objectContaining({
					method: 'POST',
					body: undefined
				})
			);
		});
	});

	describe('api.put()', () => {
		it('should call apiCall with PUT method and data', async () => {
			const mockResponse = {
				success: true,
				data: { updated: true },
				error: null
			};

			mockFetch.mockResolvedValue({
				ok: true,
				json: async () => mockResponse
			});

			const updateData = { name: 'Updated Name' };
			const result = await api.put('/items/123', updateData);

			expect(mockFetch).toHaveBeenCalledWith(
				expect.stringContaining('/items/123'),
				expect.objectContaining({
					method: 'PUT',
					body: JSON.stringify(updateData)
				})
			);
			expect(result).toEqual({ updated: true });
		});
	});

	describe('api.patch()', () => {
		it('should call apiCall with PATCH method and data', async () => {
			const mockResponse = {
				success: true,
				data: { patched: true },
				error: null
			};

			mockFetch.mockResolvedValue({
				ok: true,
				json: async () => mockResponse
			});

			const patchData = { status: 'active' };
			const result = await api.patch('/items/123', patchData);

			expect(mockFetch).toHaveBeenCalledWith(
				expect.stringContaining('/items/123'),
				expect.objectContaining({
					method: 'PATCH',
					body: JSON.stringify(patchData)
				})
			);
			expect(result).toEqual({ patched: true });
		});
	});

	describe('api.delete()', () => {
		it('should call apiCall with DELETE method', async () => {
			const mockResponse = {
				success: true,
				data: { deleted: true },
				error: null
			};

			mockFetch.mockResolvedValue({
				ok: true,
				json: async () => mockResponse
			});

			const result = await api.delete('/items/123');

			expect(mockFetch).toHaveBeenCalledWith(
				expect.stringContaining('/items/123'),
				expect.objectContaining({
					method: 'DELETE'
				})
			);
			expect(result).toEqual({ deleted: true });
		});
	});

	describe('Error Handling Edge Cases', () => {
		it('should handle malformed JSON response', async () => {
			mockFetch.mockResolvedValue({
				ok: true,
				json: async () => {
					throw new Error('Invalid JSON');
				}
			});

			try {
				await apiCall('/test');
				expect.fail('Should have thrown');
			} catch (error) {
				expect(error).toBeInstanceOf(ApiError);
				expect((error as ApiError).code).toBe('NETWORK_ERROR');
			}
		});

		it('should handle response with null data', async () => {
			mockFetch.mockResolvedValue({
				ok: true,
				json: async () => ({
					success: true,
					data: null,
					error: null
				})
			});

			const result = await apiCall('/test');
			expect(result).toBeNull();
		});

		it('should handle timeout errors', async () => {
			mockFetch.mockRejectedValue(new Error('Request timeout'));

			try {
				await apiCall('/test');
				expect.fail('Should have thrown');
			} catch (error) {
				expect(error).toBeInstanceOf(ApiError);
				expect((error as ApiError).code).toBe('NETWORK_ERROR');
				expect((error as ApiError).message).toBe('Failed to connect to server');
			}
		});
	});
});
