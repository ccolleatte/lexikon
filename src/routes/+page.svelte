<script lang="ts">
	import Button from '$components/Button.svelte';
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
				Service Générique d'Ontologies Lexicales
			</p>
			<p class="text-base text-gray-500">
				Créez, validez et gérez vos ontologies avec l'assistance de l'IA
			</p>
		</div>

		<div class="flex flex-col sm:flex-row gap-4 justify-center mb-12">
			<Button href="/onboarding" variant="primary" size="lg">
				Commencer →
			</Button>
			<Button href="/terms" variant="outline" size="lg">
				Mes Ontologies
			</Button>
		</div>

		<div class="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
			<div class="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
				<div class="text-3xl mb-3">🚀</div>
				<h3 class="font-semibold text-gray-900 mb-2">Création Rapide</h3>
				<p class="text-sm text-gray-600">
					Créez un terme en moins de 5 minutes avec le mode Quick Draft
				</p>
			</div>

			<div class="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
				<div class="text-3xl mb-3">🤖</div>
				<h3 class="font-semibold text-gray-900 mb-2">IA Agnostique</h3>
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

		<p class="text-sm text-gray-500 mt-12">
			v0.1.0 - Sprint 1 Implementation
		</p>
	</div>
</div>
