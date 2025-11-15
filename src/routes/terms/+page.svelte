<script lang="ts">
	import Button from '$components/Button.svelte';
	import { onboarding } from '$lib/stores/onboarding';

	// For Sprint 1, just show a placeholder with CTA to create first term
	const hasOnboarded = !!$onboarding.profile?.email;
</script>

<svelte:head>
	<title>Mes Ontologies - Lexikon</title>
</svelte:head>

<!-- App Header -->
<div class="bg-white border-b border-gray-200">
	<div class="max-w-7xl mx-auto px-4 sm:px-6 py-4 flex justify-between items-center">
		<a href="/" class="flex items-center gap-2 text-xl font-bold text-primary-600">
			<div class="w-8 h-8 bg-gradient-to-br from-primary-500 to-primary-700 rounded-md flex items-center justify-center text-white">
				📚
			</div>
			LEXIKON
		</a>

		<div class="flex items-center gap-4">
			{#if hasOnboarded && $onboarding.profile}
				<div class="text-sm text-gray-600">
					{$onboarding.profile.firstName} {$onboarding.profile.lastName}
				</div>
			{/if}
			<Button href="/terms/new" variant="primary" size="sm">
				+ Nouveau terme
			</Button>
		</div>
	</div>
</div>

<div class="min-h-screen bg-gray-50">
	<div class="max-w-7xl mx-auto px-4 sm:px-6 py-12">
		<!-- Empty State -->
		<div class="text-center py-16">
			<div class="inline-flex items-center justify-center w-24 h-24 bg-gray-100 rounded-full mb-6">
				<span class="text-5xl">📝</span>
			</div>

			<h2 class="text-2xl font-bold text-gray-900 mb-3">
				Aucun terme pour l'instant
			</h2>
			<p class="text-gray-600 mb-8 max-w-md mx-auto">
				Commencez à construire votre ontologie en créant votre premier terme.
				Le mode Quick Draft vous permet de créer un terme en moins de 5 minutes.
			</p>

			<div class="flex flex-col sm:flex-row gap-4 justify-center">
				<Button href="/terms/new" variant="primary" size="lg">
					Créer mon premier terme →
				</Button>

				{#if !hasOnboarded}
					<Button href="/onboarding" variant="outline" size="lg">
						Compléter mon profil
					</Button>
				{/if}
			</div>

			<!-- Quick Stats -->
			<div class="grid grid-cols-1 sm:grid-cols-3 gap-6 max-w-2xl mx-auto mt-16">
				<div class="bg-white p-6 rounded-lg border border-gray-200">
					<div class="text-3xl font-bold text-primary-600 mb-1">5 min</div>
					<div class="text-sm text-gray-600">Temps moyen Quick Draft</div>
				</div>
				<div class="bg-white p-6 rounded-lg border border-gray-200">
					<div class="text-3xl font-bold text-primary-600 mb-1">3</div>
					<div class="text-sm text-gray-600">Champs obligatoires</div>
				</div>
				<div class="bg-white p-6 rounded-lg border border-gray-200">
					<div class="text-3xl font-bold text-primary-600 mb-1">∞</div>
					<div class="text-sm text-gray-600">Termes gratuits</div>
				</div>
			</div>
		</div>
	</div>
</div>
