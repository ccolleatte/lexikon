<script lang="ts">
	import '../app.css';
	import NavBar from '$lib/components/NavBar.svelte';
	import { onMount } from 'svelte';
	import { waitLocale } from 'svelte-i18n';
	import '$lib/i18n';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { isAuthenticated } from '$lib/stores/auth';
	import { browser } from '$app/environment';

	// Protected routes that require authentication
	const protectedRoutes = ['/terms', '/profile', '/onboarding/profile'];

	// Routes only accessible to guests (unauthenticated users)
	const guestOnlyRoutes = ['/login', '/register'];

	function isProtectedRoute(pathname: string): boolean {
		return protectedRoutes.some(
			(route) => pathname === route || pathname.startsWith(route + '/')
		);
	}

	function isGuestOnlyRoute(pathname: string): boolean {
		return guestOnlyRoutes.some(
			(route) => pathname === route || pathname.startsWith(route + '/')
		);
	}

	// Route protection logic
	$: if (browser) {
		const pathname = $page.url.pathname;

		if (isProtectedRoute(pathname) && !$isAuthenticated) {
			goto(`/login?redirect=${encodeURIComponent(pathname)}`);
		} else if (isGuestOnlyRoute(pathname) && $isAuthenticated) {
			goto('/profile');
		}
	}

	onMount(async () => {
		await waitLocale();
	});
</script>

<NavBar />
<slot />
