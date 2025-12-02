<script lang="ts">
	import Button from '$lib/components/Button.svelte';
	import { addToast } from '$lib/stores/notifications';
	import { goto } from '$app/navigation';
	import { t } from 'svelte-i18n';

	let selectedFile: File | null = null;
	let fileInput: HTMLInputElement;
	let loading = false;
	let progress = 0;
	let importResult: { success: number; failed: number; errors?: string[] } | null = null;

	const formats = [
		{ value: 'skos', label: 'SKOS/RDF (Turtle or XML)' },
		{ value: 'json', label: 'JSON' },
		{ value: 'csv', label: 'CSV' },
	];

	let selectedFormat = 'skos';

	function handleFileSelect(e: Event) {
		const files = (e.target as HTMLInputElement).files;
		if (files && files.length > 0) {
			selectedFile = files[0];
		}
	}

	async function handleImport() {
		if (!selectedFile) {
			addToast('error', 'Veuillez sélectionner un fichier');
			return;
		}

		loading = true;
		progress = 0;

		try {
			const formData = new FormData();
			formData.append('file', selectedFile);

			const response = await fetch(`/api/vocabularies/import/${selectedFormat}`, {
				method: 'POST',
				body: formData,
			});

			if (!response.ok) {
				const error = await response.json();
				throw new Error(error.message || 'Erreur lors de l\'import');
			}

			const result = await response.json();
			importResult = result;

			addToast('success', `Import réussi: ${result.success} termes importés`);
			progress = 100;

			setTimeout(() => {
				goto('/terms');
			}, 2000);
		} catch (error) {
			const errorMessage = error instanceof Error ? error.message : 'Erreur lors de l\'import';
			addToast('error', errorMessage);
		} finally {
			loading = false;
		}
	}

	function resetForm() {
		selectedFile = null;
		fileInput.value = '';
		importResult = null;
		progress = 0;
	}
</script>

<svelte:head>
	<title>Importer un vocabulaire - Lexikon</title>
</svelte:head>

<main class="min-h-screen bg-gray-50">
	<div class="max-w-2xl mx-auto px-4 py-12">
		<!-- Breadcrumb -->
		<div class="mb-8">
			<a href="/vocabularies" class="text-primary-600 hover:text-primary-700 text-sm">← Vocabulaires</a>
		</div>

		<!-- Header -->
		<div class="mb-8">
			<h1 class="text-3xl font-bold text-gray-900 mb-2">Importer un vocabulaire</h1>
			<p class="text-gray-600">Sélectionnez un fichier et un format pour commencer l'import</p>
		</div>

		{#if importResult}
			<!-- Result -->
			<div class="bg-white rounded-lg border border-gray-200 p-8">
				<div class="text-center">
					<div class="text-4xl mb-4">{importResult.success > 0 ? '✓' : '⚠'}</div>
					<h2 class="text-2xl font-bold text-gray-900 mb-2">Import terminé</h2>
					<p class="text-gray-600 mb-6">
						<span class="text-lg font-semibold text-green-600">{importResult.success}</span> termes ont été importés avec succès
					</p>

					{#if importResult.failed > 0}
						<p class="text-sm text-orange-600 mb-4">
							{importResult.failed} terme(s) n'ont pas pu être importés
						</p>
					{/if}

					<div class="flex gap-3 justify-center">
						<Button href="/terms" variant="primary">
							Voir mes termes
						</Button>
						<Button on:click={resetForm} variant="outline">
							Importer un autre fichier
						</Button>
					</div>
				</div>
			</div>
		{:else}
			<!-- Form -->
			<div class="bg-white rounded-lg border border-gray-200 p-8 space-y-6">
				<!-- Format Selection -->
				<div>
					<label class="block text-sm font-medium text-gray-700 mb-2">Format du fichier</label>
					<select
						bind:value={selectedFormat}
						disabled={loading}
						class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-600"
					>
						{#each formats as format}
							<option value={format.value}>{format.label}</option>
						{/each}
					</select>
				</div>

				<!-- File Upload -->
				<div>
					<label class="block text-sm font-medium text-gray-700 mb-2">Fichier à importer</label>

					<div
						class="relative border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-primary-400 transition-colors"
						on:dragover|preventDefault={() => {}}
						on:drop|preventDefault={(e) => {
							const files = e.dataTransfer.files;
							if (files.length > 0) {
								selectedFile = files[0];
							}
						}}
					>
						<svg class="w-12 h-12 text-gray-400 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
						</svg>

						{#if selectedFile}
							<p class="text-gray-900 font-medium">{selectedFile.name}</p>
							<p class="text-sm text-gray-500 mt-1">{(selectedFile.size / 1024).toFixed(2)} KB</p>
						{:else}
							<p class="text-gray-700">Glissez votre fichier ici ou cliquez pour sélectionner</p>
							<input
								bind:this={fileInput}
								type="file"
								on:change={handleFileSelect}
								disabled={loading}
								class="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
								accept=".rdf,.ttl,.xml,.json,.csv"
							/>
						{/if}
					</div>

					{#if selectedFile}
						<div class="mt-3">
							<button
								on:click={() => resetForm()}
								class="text-sm text-primary-600 hover:text-primary-700"
								disabled={loading}
							>
								Choisir un autre fichier
							</button>
						</div>
					{/if}
				</div>

				<!-- Progress -->
				{#if loading && progress > 0}
					<div>
						<div class="w-full bg-gray-200 rounded-full h-2">
							<div class="bg-primary-600 h-2 rounded-full transition-all" style="width: {progress}%" />
						</div>
						<p class="text-sm text-gray-600 mt-2 text-center">Import en cours...</p>
					</div>
				{/if}

				<!-- Submit Button -->
				<Button
					on:click={handleImport}
					disabled={!selectedFile || loading}
					variant="primary"
					class="w-full"
				>
					{loading ? 'Import en cours...' : 'Commencer l\'import'}
				</Button>
			</div>

			<!-- Help -->
			<div class="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
				<h3 class="font-semibold text-blue-900 mb-2">Format des fichiers</h3>
				<div class="space-y-3 text-sm text-blue-800">
					<div>
						<p class="font-medium">CSV</p>
						<p>Colonnes attendues: name, definition, domain, level (séparateur: virgule)</p>
					</div>
					<div>
						<p class="font-medium">JSON</p>
						<p>Array d'objets avec propriétés: name, definition, domain, level</p>
					</div>
					<div>
						<p class="font-medium">SKOS/RDF</p>
						<p>Format Turtle (.ttl) ou RDF/XML (.rdf)</p>
					</div>
				</div>
			</div>
		{/if}
	</div>
</main>
