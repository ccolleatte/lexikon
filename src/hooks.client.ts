/**
 * Client-side hooks for route protection and authentication
 */

import { get } from 'svelte/store';
import { authStore } from '$lib/stores/auth';
import { goto } from '$app/navigation';

// Routes that require authentication
const protectedRoutes = [
	'/terms',
	'/terms/new',
	'/onboarding/profile',
	'/profile'
];

// Routes that should redirect to /terms if already authenticated
const guestOnlyRoutes = [
	'/login',
	'/register'
];

/**
 * Check if a path requires authentication
 */
function isProtectedRoute(pathname: string): boolean {
	return protectedRoutes.some(route => pathname.startsWith(route));
}

/**
 * Check if a path is guest-only
 */
function isGuestOnlyRoute(pathname: string): boolean {
	return guestOnlyRoutes.some(route => pathname.startsWith(route));
}

/**
 * Handle navigation hook to check authentication
 */
export async function handleNavigation({ url }: { url: URL }) {
	const auth = get(authStore);
	const pathname = url.pathname;

	// Check protected routes
	if (isProtectedRoute(pathname) && !auth.isAuthenticated) {
		// Redirect to login with return URL
		goto(`/login?redirect=${encodeURIComponent(pathname)}`);
		return;
	}

	// Check guest-only routes
	if (isGuestOnlyRoute(pathname) && auth.isAuthenticated) {
		// Redirect to terms page if already logged in
		goto('/terms');
		return;
	}
}
