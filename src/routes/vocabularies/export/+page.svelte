<script lang="ts">
	import Button from '$lib/components/Button.svelte';
	import { addToast } from '$lib/stores/notifications';

	let selectedFormat = 'skos';
	let domainFilter = '';
	let levelFilter = '';
	let dateFromFilter = '';
	let dateToFilter = '';
	let exporting = false;

	const formats = [
		{ value: 'skos', label: 'SKOS/RDF (Turtle)', ext: 'ttl' },
		{ value: 'json', label: 'JSON', ext: 'json' },
		{ value: 'csv', label: 'CSV', ext: 'csv' },
	];

	const domains = ['all', 'mathematics', 'physics', 'biology', 'chemistry', 'computer-science'];
	const levels = ['all', 'basic', 'intermediate', 'advanced'];

	async function handleExport() {
		exporting = true;

		try {
			const params = new URLSearchParams();
			params.set('format', selectedFormat);

			if (domainFilter && domainFilter !== 'all') {
				params.set('domain', domainFilter);
			}
			if (levelFilter && levelFilter !== 'all') {
				params.set('level', levelFilter);
			}
			if (dateFromFilter) {
				params.set('date_from', dateFromFilter);
			}
			if (dateToFilter) {
				params.set('date_to', dateToFilter);
			}

			const response = await fetch(`/api/vocabularies/extract?${params.toString()}`);

			if (!response.ok) {
				const error = await response.json();
				throw new Error(error.message || 'Erreur lors de l\'export');
			}

			// Get filename from Content-Disposition header or generate default
			const contentDisposition = response.headers.get('content-disposition');
			let filename = `vocabulaire_${new Date().toISOString().split('T')[0]}.${
				formats.find((f) => f.value === selectedFormat)?.ext || 'txt'
			}`;

			if (contentDisposition) {
				const matches = contentDisposition.match(/filename="(.+?)"/);
				if (matches && matches[1]) {
					filename = matches[1];
				}
			}

			// Download the file
			const blob = await response.blob();
			const url = window.URL.createObjectURL(blob);
			const link = document.createElement('a');
			link.href = url;
			link.download = filename;
			document.body.appendChild(link);
			link.click();
			document.body.removeChild(link);
			window.URL.revokeObjectURL(url);

			addToast('success', 'Export téléchargé avec succès');
		} catch (error) {
			const errorMessage = error instanceof Error ? error.message : 'Erreur lors de l\'export';
			addToast('error', errorMessage);
		} finally {
			exporting = false;
		}
	}
</script>

<svelte:head>
	<title>Exporter un vocabulaire - Lexikon</title>
</svelte:head>

<main class="min-h-screen bg-gray-50">
	<div class="max-w-2xl mx-auto px-4 py-12">
		<!-- Breadcrumb -->
		<div class="mb-8">
			<a href="/vocabularies" class="text-primary-600 hover:text-primary-700 text-sm">← Vocabulaires</a>
		</div>

		<!-- Header -->
		<div class="mb-8">
			<h1 class="text-3xl font-bold text-gray-900 mb-2">Exporter un vocabulaire</h1>
			<p class="text-gray-600">Configurez les paramètres et téléchargez votre vocabulaire</p>
		</div>

		<!-- Form -->
		<div class="bg-white rounded-lg border border-gray-200 p-8 space-y-6">
			<!-- Format Selection -->
			<div>
				<label class="block text-sm font-medium text-gray-700 mb-2">Format de sortie</label>
				<select
					bind:value={selectedFormat}
					disabled={exporting}
					class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-600"
				>
					{#each formats as format}
						<option value={format.value}>{format.label}</option>
					{/each}
				</select>
			</div>

			<!-- Filters Section -->
			<div class="border-t border-gray-200 pt-6">
				<h3 class="text-lg font-semibold text-gray-900 mb-4">Filtres (optionnels)</h3>

				<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
					<!-- Domain Filter -->
					<div>
						<label class="block text-sm font-medium text-gray-700 mb-2">Domaine</label>
						<select
							bind:value={domainFilter}
							disabled={exporting}
							class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-600"
						>
							{#each domains as domain}
								<option value={domain}>
									{domain === 'all' ? 'Tous les domaines' : domain}
								</option>
							{/each}
						</select>
					</div>

					<!-- Level Filter -->
					<div>
						<label class="block text-sm font-medium text-gray-700 mb-2">Niveau</label>
						<select
							bind:value={levelFilter}
							disabled={exporting}
							class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-600"
						>
							{#each levels as level}
								<option value={level}>
									{level === 'all' ? 'Tous les niveaux' : level}
								</option>
							{/each}
						</select>
					</div>

					<!-- Date From -->
					<div>
						<label class="block text-sm font-medium text-gray-700 mb-2">À partir de</label>
						<input
							type="date"
							bind:value={dateFromFilter}
							disabled={exporting}
							class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-600"
						/>
					</div>

					<!-- Date To -->
					<div>
						<label class="block text-sm font-medium text-gray-700 mb-2">Jusqu'à</label>
						<input
							type="date"
							bind:value={dateToFilter}
							disabled={exporting}
							class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-600"
						/>
					</div>
				</div>
			</div>

			<!-- Summary -->
			<div class="bg-gray-50 rounded-lg p-4">
				<p class="text-sm text-gray-600">
					<span class="font-medium">Aperçu:</span> Export en format
					<span class="font-semibold">{formats.find((f) => f.value === selectedFormat)?.label}</span>
					{#if domainFilter && domainFilter !== 'all'}
						du domaine <span class="font-semibold">{domainFilter}</span>
					{/if}
					{#if levelFilter && levelFilter !== 'all'}
						niveau <span class="font-semibold">{levelFilter}</span>
					{/if}
				</p>
			</div>

			<!-- Export Button -->
			<Button
				on:click={handleExport}
				disabled={exporting}
				variant="primary"
				class="w-full"
			>
				{exporting ? 'Export en cours...' : '📥 Télécharger l\'export'}
			</Button>
		</div>

		<!-- Info -->
		<div class="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
			<h3 class="font-semibold text-blue-900 mb-2">À propos de l'export</h3>
			<ul class="text-sm text-blue-800 space-y-2">
				<li>✓ Les filtres sont optionnels - laissez-les vides pour exporter tous les termes</li>
				<li>✓ L'export inclut tous les termes qui correspondent aux critères</li>
				<li>✓ Les relations sont incluses dans les formats SKOS et JSON</li>
				<li>✓ Le fichier est téléchargé directement dans votre navigateur</li>
			</ul>
		</div>
	</div>
</main>
