<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { isAuthenticated } from '$lib/stores/auth';
	import { browser } from '$app/environment';

	/**
	 * If true, only authenticated users can see the content
	 */
	export let requireAuth = false;

	/**
	 * If true, only non-authenticated users can see the content
	 */
	export let guestOnly = false;

	/**
	 * Custom redirect path when auth requirement not met
	 */
	export let redirectTo: string | null = null;

	let ready = false;

	onMount(() => {
		ready = true;
	});

	$: if (ready && browser) {
		const currentPath = $page.url.pathname;

		if (requireAuth && !$isAuthenticated) {
			// User needs to be authenticated but isn't
			const redirect = redirectTo || `/login?redirect=${encodeURIComponent(currentPath)}`;
			goto(redirect);
		} else if (guestOnly && $isAuthenticated) {
			// User is authenticated but this is a guest-only route
			const redirect = redirectTo || '/profile';
			goto(redirect);
		}
	}

	// Determine if content should be shown
	$: showContent =
		ready &&
		((requireAuth && $isAuthenticated) ||
			(guestOnly && !$isAuthenticated) ||
			(!requireAuth && !guestOnly));
</script>

{#if showContent}
	<slot />
{:else if ready}
	<!-- Loading state while redirecting -->
	<div class="flex items-center justify-center min-h-screen">
		<div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
	</div>
{:else}
	<!-- Initial loading state -->
	<div class="flex items-center justify-center min-h-screen">
		<div class="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-400"></div>
	</div>
{/if}
