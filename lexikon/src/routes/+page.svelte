<script lang="ts">
	import Button from '$components/Button.svelte';
	import { isAuthenticated, user } from '$lib/stores/auth';

	const apiDocsUrl = `${typeof window !== 'undefined' ? window.location.origin : ''}/docs`;
</script>

<svelte:head>
	<title>Lexikon - Generic Ontology Service</title>
</svelte:head>

<div class="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-primary-50 via-white to-secondary-50 px-4">
	<div class="max-w-3xl text-center">
		<div class="mb-8">
			<div class="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-primary-500 to-primary-700 rounded-2xl mb-6">
				<span class="text-4xl">📚</span>
			</div>
			<h1 class="text-5xl font-bold text-gray-900 mb-4">
				LEXIKON
			</h1>
			<p class="text-xl text-gray-600 mb-2">
				Service générique d'ontologies lexicales
			</p>
			<p class="text-base text-gray-500">
				Créez, validez et gérez vos ontologies avec l'assistance de l'IA
			</p>
		</div>

		<div class="flex flex-col sm:flex-row gap-4 justify-center mb-12">
			{#if $isAuthenticated}
				<Button href="/terms" variant="primary" size="lg">
					Mes ontologies →
				</Button>
				<Button href="/profile" variant="outline" size="lg">
					Mon profil
				</Button>
			{:else}
				<Button href="/register" variant="primary" size="lg">
					Commencer gratuitement →
				</Button>
				<Button href="/login" variant="outline" size="lg">
					Se connecter
				</Button>
			{/if}
		</div>

		{#if $isAuthenticated && $user}
			<p class="text-sm text-gray-600 mb-8">
				Bienvenue, <span class="font-semibold">{$user.first_name}</span>! 👋
			</p>
		{/if}

		<div class="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
			<div class="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
				<div class="text-3xl mb-3">🚀</div>
				<h3 class="font-semibold text-gray-900 mb-2">Création rapide</h3>
				<p class="text-sm text-gray-600">
					Créez un terme en moins de 5 minutes avec le mode Quick Draft
				</p>
			</div>

			<div class="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
				<div class="text-3xl mb-3">🤖</div>
				<h3 class="font-semibold text-gray-900 mb-2">IA agnostique</h3>
				<p class="text-sm text-gray-600">
					Utilisez votre propre clé API ou nos modèles gratuits
				</p>
			</div>

			<div class="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
				<div class="text-3xl mb-3">✅</div>
				<h3 class="font-semibold text-gray-900 mb-2">Human-in-the-Loop</h3>
				<p class="text-sm text-gray-600">
					Validation humaine obligatoire pour toutes les suggestions IA
				</p>
			</div>
		</div>

		<div class="mt-12 pt-8 border-t border-gray-200">
			<p class="text-sm text-gray-600 mb-4">
				<a href={apiDocsUrl} target="_blank" rel="noopener noreferrer" class="text-primary-600 hover:text-primary-700 font-medium">
					Documentation API →
				</a>
			</p>
			<p class="text-sm text-gray-500">
				v0.1.0 - Sprint 1 Implementation
			</p>
		</div>
	</div>
</div>
