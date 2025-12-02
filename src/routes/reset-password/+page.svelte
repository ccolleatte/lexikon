<script lang="ts">
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import Button from '$components/Button.svelte';
	import Input from '$components/Input.svelte';
	import { apiCall } from '$lib/utils/api';

	let password = '';
	let passwordConfirm = '';
	let loading = false;
	let error: string | null = null;
	let success = false;

	$: token = $page.url.searchParams.get('token') || '';
	$: if (!token) error = 'Token manquant ou invalide';

	async function handleSubmit() {
		try {
			loading = true;
			error = null;

			if (password !== passwordConfirm) {
				throw new Error('Les mots de passe ne correspondent pas');
			}

			if (password.length < 8) {
				throw new Error('Le mot de passe doit contenir au moins 8 caractères');
			}

			const response = await apiCall('/api/auth/reset-password', {
				method: 'POST',
				body: JSON.stringify({
					token,
					new_password: password
				})
			});

			if (!response.success) {
				throw new Error(response.error?.message || 'Erreur lors de la réinitialisation');
			}

			success = true;
			setTimeout(() => {
				goto('/login');
			}, 2000);
		} catch (err) {
			error = err instanceof Error ? err.message : 'Erreur inconnue';
		} finally {
			loading = false;
		}
	}
</script>

<svelte:head>
	<title>Réinitialiser le mot de passe - Lexikon</title>
</svelte:head>

<div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center px-4">
	<div class="bg-white rounded-lg shadow-lg max-w-md w-full p-8">
		<!-- Header -->
		<div class="text-center mb-8">
			<h1 class="text-3xl font-bold text-gray-900 mb-2">Réinitialiser le mot de passe</h1>
			<p class="text-gray-600">Créez un nouveau mot de passe sécurisé</p>
		</div>

		{#if success}
			<!-- Success State -->
			<div class="bg-green-50 border border-green-200 rounded-lg p-6 text-center">
				<p class="text-green-800 font-medium">✓ Mot de passe réinitialisé</p>
				<p class="text-green-700 text-sm mt-2">Redirection vers la connexion...</p>
			</div>
		{:else if !token}
			<!-- Invalid Token -->
			<div class="bg-red-50 border border-red-200 rounded-lg p-6 text-center mb-6">
				<p class="text-red-800 font-medium">Token invalide ou expiré</p>
				<p class="text-red-700 text-sm mt-2">Demandez un nouveau lien de réinitialisation</p>
			</div>

			<Button href="/forgot-password" variant="primary" class="w-full">
				Demander un nouveau lien
			</Button>
		{:else}
			<!-- Form -->
			<form on:submit|preventDefault={handleSubmit} class="space-y-6">
				{#if error}
					<div class="bg-red-50 border border-red-200 rounded-lg p-4">
						<p class="text-red-800 text-sm">{error}</p>
					</div>
				{/if}

				<!-- Password Input -->
				<div>
					<label for="password" class="block text-sm font-medium text-gray-700 mb-2">
						Nouveau mot de passe
					</label>
					<Input
						id="password"
						type="password"
						placeholder="Au moins 8 caractères"
						bind:value={password}
						disabled={loading}
					/>
					<p class="text-xs text-gray-500 mt-1">
						Au moins 8 caractères avec majuscules, minuscules, chiffres et caractères spéciaux
					</p>
				</div>

				<!-- Confirm Password Input -->
				<div>
					<label for="password-confirm" class="block text-sm font-medium text-gray-700 mb-2">
						Confirmer le mot de passe
					</label>
					<Input
						id="password-confirm"
						type="password"
						placeholder="Répétez votre mot de passe"
						bind:value={passwordConfirm}
						disabled={loading}
					/>
				</div>

				<!-- Submit Button -->
				<Button type="submit" variant="primary" disabled={loading} class="w-full">
					{loading ? 'Réinitialisation...' : 'Réinitialiser le mot de passe'}
				</Button>

				<!-- Back Link -->
				<div class="text-center">
					<a href="/login" class="text-primary-600 hover:text-primary-700 text-sm font-medium">
						← Retour à la connexion
					</a>
				</div>
			</form>
		{/if}
	</div>
</div>
