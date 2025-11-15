<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { api } from '$lib/utils/api';
	import { authStore } from '$lib/stores/auth';
	import type { User } from '$lib/stores/auth';
	import Alert from '$lib/components/Alert.svelte';

	let isLoading = true;
	let error: string | null = null;

	interface OAuthCallbackResponse {
		access_token: string;
		refresh_token: string;
		token_type: string;
		expires_in: number;
		user: User;
	}

	onMount(async () => {
		const code = $page.url.searchParams.get('code');
		const errorParam = $page.url.searchParams.get('error');

		if (errorParam) {
			error = 'OAuth authentication was cancelled or failed';
			isLoading = false;
			return;
		}

		if (!code) {
			error = 'No authorization code received';
			isLoading = false;
			return;
		}

		try {
			// Exchange code for tokens (this would be handled by backend OAuth endpoint)
			const response = await api.post<OAuthCallbackResponse>('/auth/oauth/github/callback', {
				code
			});

			// Store authentication data
			authStore.login(response.user, response.access_token, response.refresh_token);

			// Redirect to terms page
			goto('/terms');
		} catch (e) {
			error = 'Failed to complete GitHub authentication. Please try again.';
			isLoading = false;
		}
	});
</script>

<svelte:head>
	<title>Authenticating with GitHub - Lexikon</title>
</svelte:head>

<div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4">
	<div class="max-w-md w-full text-center space-y-6">
		{#if isLoading}
			<!-- Loading State -->
			<div class="space-y-4">
				<div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
				<h2 class="text-2xl font-bold text-gray-900">Authenticating with GitHub...</h2>
				<p class="text-gray-600">Please wait while we complete your login.</p>
			</div>
		{:else if error}
			<!-- Error State -->
			<div class="space-y-4">
				<Alert type="error">
					{error}
				</Alert>
				<div class="space-y-2">
					<a href="/login" class="block text-primary-600 hover:text-primary-500 font-medium">
						← Back to login
					</a>
					<button
						on:click={() => window.location.reload()}
						class="block w-full text-gray-600 hover:text-gray-900"
					>
						Try again
					</button>
				</div>
			</div>
		{/if}
	</div>
</div>
