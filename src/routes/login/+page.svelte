<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { isAuthenticated } from '$lib/stores/auth';
	import { login, loginWithOAuth } from '$lib/utils/auth';
	import { ApiError } from '$lib/utils/api';
	import Button from '$lib/components/Button.svelte';
	import Input from '$lib/components/Input.svelte';
	import Alert from '$lib/components/Alert.svelte';
	import { t } from 'svelte-i18n';

	let email = '';
	let password = '';
	let isLoading = false;
	let error: string | null = null;

	// Get redirect URL from query params, default to /profile
	$: redirectUrl = $page.url.searchParams.get('redirect') || '/profile';

	// Redirect if already authenticated
	$: if ($isAuthenticated) {
		goto(redirectUrl);
	}

	async function handleSubmit() {
		error = null;
		isLoading = true;

		try {
			await login({ email, password });
			// Redirect will happen automatically via the reactive statement above
		} catch (e) {
			if (e instanceof ApiError) {
				error = e.message;
			} else {
				error = 'An unexpected error occurred. Please try again.';
			}
		} finally {
			isLoading = false;
		}
	}

	function handleOAuthLogin(provider: 'google') {
		loginWithOAuth(provider);
	}
</script>

<svelte:head>
	<title>Login - Lexikon</title>
</svelte:head>

<div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
	<div class="max-w-md w-full space-y-8">
		<!-- Header -->
		<div class="text-center">
			<h1 class="text-4xl font-serif font-bold text-primary-600">Lexikon</h1>
			<h2 class="mt-6 text-3xl font-bold text-gray-900">{$t('auth.welcome')}</h2>
			<p class="mt-2 text-sm text-gray-600">
				{$t('auth.noAccount')}
				<a href="/register" class="font-medium text-primary-600 hover:text-primary-500">
					{$t('auth.signUpNow')}
				</a>
			</p>
		</div>

		<!-- Error Alert -->
		{#if error}
			<Alert type="error">
				{error}
			</Alert>
		{/if}

		<!-- Login Form -->
		<form class="mt-8 space-y-6" on:submit|preventDefault={handleSubmit}>
			<div class="space-y-4">
				<Input
					label={$t('auth.emailAddress')}
					type="email"
					bind:value={email}
					placeholder="you@example.com"
					required
					autocomplete="email"
				/>

				<Input
					label={$t('auth.password')}
					type="password"
					bind:value={password}
					placeholder="••••••••"
					required
					autocomplete="current-password"
				/>
			</div>

			<div class="flex items-center justify-between">
				<div class="flex items-center">
					<input
						id="remember-me"
						name="remember-me"
						type="checkbox"
						class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
					/>
					<label for="remember-me" class="ml-2 block text-sm text-gray-900">
						{$t('auth.rememberMe')}
					</label>
				</div>

				<div class="text-sm">
					<a href="/forgot-password" class="font-medium text-primary-600 hover:text-primary-500">
						{$t('auth.forgotPassword')}
					</a>
				</div>
			</div>

			<Button type="submit" variant="primary" fullWidth {isLoading}>
				{isLoading ? $t('auth.signingIn') : $t('auth.signIn')}
			</Button>
		</form>

		<!-- OAuth Options -->
		<div class="mt-6">
			<div class="relative">
				<div class="absolute inset-0 flex items-center">
					<div class="w-full border-t border-gray-300"></div>
				</div>
				<div class="relative flex justify-center text-sm">
					<span class="px-2 bg-gray-50 text-gray-500">{$t('auth.orContinueWith')}</span>
				</div>
			</div>

			<div class="mt-6">
				<Button
					type="button"
					variant="outline"
					fullWidth
					on:click={() => handleOAuthLogin('google')}
					disabled={isLoading}
				>
					<svg class="w-5 h-5 mr-2" viewBox="0 0 24 24">
						<path
							fill="currentColor"
							d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
						/>
						<path
							fill="currentColor"
							d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
						/>
						<path
							fill="currentColor"
							d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
						/>
						<path
							fill="currentColor"
							d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
						/>
					</svg>
					{$t('auth.googleSignIn')}
				</Button>
			</div>
		</div>

		<!-- Legal -->
		<p class="mt-8 text-center text-xs text-gray-500">
			{$t('auth.agreeToTerms')}
			<a href="/legal/terms" class="underline">{$t('auth.termsOfService')}</a>
			{$t('auth.and')}
			<a href="/legal/privacy" class="underline">{$t('auth.privacyPolicy')}</a>
		</p>
	</div>
</div>
