<script lang="ts">
	import Button from '$components/Button.svelte';
	import Input from '$components/Input.svelte';
	import { apiCall } from '$lib/utils/api';

	let email = '';
	let loading = false;
	let error: string | null = null;
	let success = false;

	async function handleSubmit() {
		try {
			loading = true;
			error = null;

			if (!email.trim()) {
				throw new Error('Veuillez entrer votre adresse email');
			}

			const response = await apiCall('/api/auth/forgot-password', {
				method: 'POST',
				body: JSON.stringify({ email: email.trim() })
			});

			if (!response.success) {
				throw new Error(response.error?.message || 'Erreur lors de la demande');
			}

			success = true;
			email = '';
		} catch (err) {
			error = err instanceof Error ? err.message : 'Erreur inconnue';
		} finally {
			loading = false;
		}
	}
</script>

<svelte:head>
	<title>Mot de passe oublié - Lexikon</title>
</svelte:head>

<div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center px-4">
	<div class="bg-white rounded-lg shadow-lg max-w-md w-full p-8">
		<!-- Header -->
		<div class="text-center mb-8">
			<h1 class="text-3xl font-bold text-gray-900 mb-2">Mot de passe oublié</h1>
			<p class="text-gray-600">Entrez votre adresse email pour réinitialiser votre mot de passe</p>
		</div>

		{#if success}
			<!-- Success State -->
			<div class="bg-green-50 border border-green-200 rounded-lg p-6 text-center mb-6">
				<p class="text-green-800 font-medium">✓ Email envoyé avec succès</p>
				<p class="text-green-700 text-sm mt-2">Consultez votre boîte mail pour le lien de réinitialisation</p>
			</div>

			<Button href="/login" variant="primary" class="w-full">← Retour à la connexion</Button>
		{:else}
			<!-- Form -->
			<form on:submit|preventDefault={handleSubmit} class="space-y-6">
				{#if error}
					<div class="bg-red-50 border border-red-200 rounded-lg p-4">
						<p class="text-red-800 text-sm">{error}</p>
					</div>
				{/if}

				<!-- Email Input -->
				<div>
					<label for="email" class="block text-sm font-medium text-gray-700 mb-2">
						Adresse email
					</label>
					<Input
						id="email"
						type="email"
						placeholder="votre@email.com"
						bind:value={email}
						disabled={loading}
					/>
				</div>

				<!-- Submit Button -->
				<Button type="submit" variant="primary" disabled={loading} class="w-full">
					{loading ? 'Envoi...' : 'Envoyer le lien de réinitialisation'}
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
