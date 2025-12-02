<script lang="ts">
	import Button from '$lib/components/Button.svelte';
	import { t } from 'svelte-i18n';
</script>

<svelte:head>
	<title>Vocabulaires - Lexikon</title>
</svelte:head>

<main class="min-h-screen bg-gray-50">
	<div class="max-w-6xl mx-auto px-4 py-12">
		<!-- Header -->
		<div class="mb-12">
			<h1 class="text-4xl font-bold text-gray-900 mb-2">Vocabulaires</h1>
			<p class="text-lg text-gray-600">Importez et exportez vos termes dans différents formats</p>
		</div>

		<!-- Cards Grid -->
		<div class="grid grid-cols-1 md:grid-cols-2 gap-8">
			<!-- Import Card -->
			<div class="bg-white rounded-lg border border-gray-200 p-8 hover:shadow-lg transition-shadow">
				<div class="flex items-center mb-4">
					<div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center text-2xl">
						📥
					</div>
					<h2 class="text-2xl font-bold text-gray-900 ml-4">Importer</h2>
				</div>

				<p class="text-gray-600 mb-6">
					Importez des termes depuis des fichiers SKOS, JSON ou CSV. Prend en charge la gestion des conflits et le mapping de colonnes.
				</p>

				<div class="space-y-2 mb-6">
					<h3 class="text-sm font-semibold text-gray-700">Formats supportés:</h3>
					<ul class="text-sm text-gray-600 space-y-1">
						<li>✓ SKOS/RDF (Turtle, XML)</li>
						<li>✓ JSON (struktur personnalisée)</li>
						<li>✓ CSV (avec mapping de colonnes)</li>
					</ul>
				</div>

				<Button href="/vocabularies/import" variant="primary" class="w-full">
					Démarrer l'import
				</Button>
			</div>

			<!-- Export Card -->
			<div class="bg-white rounded-lg border border-gray-200 p-8 hover:shadow-lg transition-shadow">
				<div class="flex items-center mb-4">
					<div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center text-2xl">
						📤
					</div>
					<h2 class="text-2xl font-bold text-gray-900 ml-4">Exporter</h2>
				</div>

				<p class="text-gray-600 mb-6">
					Exportez votre vocabulaire dans le format de votre choix. Appliquez des filtres pour sélectionner les données.
				</p>

				<div class="space-y-2 mb-6">
					<h3 class="text-sm font-semibold text-gray-700">Formats disponibles:</h3>
					<ul class="text-sm text-gray-600 space-y-1">
						<li>✓ SKOS RDF (Turtle)</li>
						<li>✓ JSON</li>
						<li>✓ CSV</li>
					</ul>
				</div>

				<Button href="/vocabularies/export" variant="primary" class="w-full">
					Exporter
				</Button>
			</div>
		</div>

		<!-- Info Section -->
		<div class="mt-12 bg-blue-50 border border-blue-200 rounded-lg p-6">
			<h3 class="text-lg font-semibold text-blue-900 mb-2">À propos des vocabulaires</h3>
			<p class="text-blue-700">
				Les vocabulaires sont des collections de termes structurés. Vous pouvez les importer pour enrichir rapidement votre base de données, ou les exporter pour partager avec d'autres utilisateurs.
			</p>
		</div>
	</div>
</main>

<style>
	:global(button[href]) {
		text-decoration: none;
	}
</style>
