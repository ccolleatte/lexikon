/**
 * Vitest setup file
 * Runs before each test file
 */

import '@testing-library/jest-dom';
import { vi } from 'vitest';

// Mock browser environment
global.window = global.window || {};
global.document = global.document || {};

// Mock localStorage
const localStorageMock = (() => {
	let store: Record<string, string> = {};

	return {
		getItem: (key: string) => store[key] || null,
		setItem: (key: string, value: string) => {
			store[key] = value.toString();
		},
		removeItem: (key: string) => {
			delete store[key];
		},
		clear: () => {
			store = {};
		},
		get length() {
			return Object.keys(store).length;
		},
		key: (index: number) => {
			const keys = Object.keys(store);
			return keys[index] || null;
		}
	};
})();

Object.defineProperty(global, 'localStorage', {
	value: localStorageMock
});

// Clear localStorage before each test
beforeEach(() => {
	localStorage.clear();
});

// Mock console methods to reduce noise during tests
global.console = {
	...console,
	error: vi.fn(),
	warn: vi.fn()
};
