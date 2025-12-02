<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import { apiCall } from '$lib/utils/api';
	import { addToast } from '$lib/stores/notifications';
	import Button from './Button.svelte';

	const dispatch = createEventDispatcher();

	export let termId: string;
	export let termName: string;

	let selectedType = 'related_to';
	let targetTermQuery = '';
	let targetTermId = '';
	let targetTermName = '';
	let suggestedTerms: any[] = [];
	let loading = false;
	let submitting = false;

	const relationTypes = [
		{ value: 'hypernyme', label: 'Hypernyme (concept plus générique)' },
		{ value: 'hyponymeme', label: 'Hyponymeme (concept plus spécifique)' },
		{ value: 'synonyme', label: 'Synonyme' },
		{ value: 'antonyme', label: 'Antonyme' },
		{ value: 'related_to', label: 'Terme lié' },
	];

	async function handleTargetSearch() {
		if (!targetTermQuery.trim()) {
			suggestedTerms = [];
			return;
		}

		loading = true;
		try {
			const response = await fetch(`/api/terms/search?q=${encodeURIComponent(targetTermQuery)}&limit=5`);
			if (response.ok) {
				const results = await response.json();
				suggestedTerms = results.filter((t: any) => t.id !== termId); // Exclude self
			}
		} catch (error) {
			console.error('Search failed:', error);
			suggestedTerms = [];
		} finally {
			loading = false;
		}
	}

	function selectTerm(term: any) {
		targetTermId = term.id;
		targetTermName = term.name;
		suggestedTerms = [];
		targetTermQuery = term.name;
	}

	async function handleSubmit() {
		if (!targetTermId) {
			addToast('error', 'Veuillez sélectionner un terme');
			return;
		}

		submitting = true;
		try {
			const response = await apiCall('/api/ontology/relations', {
				method: 'POST',
				body: JSON.stringify({
					sourceTermId: termId,
					targetTermId: targetTermId,
					type: selectedType,
				}),
			});

			if (response.success) {
				addToast('success', 'Relation créée avec succès');
				dispatch('added');
				resetForm();
			} else {
				addToast('error', response.error?.message || 'Erreur lors de la création de la relation');
			}
		} catch (error) {
			console.error('Error creating relation:', error);
			addToast('error', 'Erreur lors de la création de la relation');
		} finally {
			submitting = false;
		}
	}

	function resetForm() {
		selectedType = 'related_to';
		targetTermQuery = '';
		targetTermId = '';
		targetTermName = '';
		suggestedTerms = [];
	}

	function handleClose() {
		resetForm();
		dispatch('close');
	}
</script>

<!-- Overlay -->
<div
	class="fixed inset-0 bg-black bg-opacity-50 z-40 transition-opacity"
	on:click={handleClose}
	on:keydown={(e) => e.key === 'Escape' && handleClose()}
	role="button"
	tabindex="0"
/>

<!-- Modal -->
<div class="fixed inset-0 z-50 flex items-center justify-center p-4">
	<div class="bg-white rounded-lg shadow-xl max-w-md w-full max-h-screen overflow-y-auto">
		<!-- Header -->
		<div class="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
			<h2 class="text-xl font-bold text-gray-900">Ajouter une relation</h2>
			<button
				on:click={handleClose}
				class="text-gray-400 hover:text-gray-600 transition-colors"
				aria-label="Close"
			>
				<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
				</svg>
			</button>
		</div>

		<!-- Content -->
		<div class="px-6 py-4 space-y-4">
			<!-- Source Term -->
			<div>
				<label class="block text-sm font-medium text-gray-700 mb-2">De</label>
				<div class="p-3 bg-gray-100 rounded-lg border border-gray-200 text-gray-900 font-medium">
					{termName}
				</div>
			</div>

			<!-- Relation Type -->
			<div>
				<label class="block text-sm font-medium text-gray-700 mb-2">Type de relation</label>
				<select
					bind:value={selectedType}
					class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-600 focus:border-transparent"
				>
					{#each relationTypes as type}
						<option value={type.value}>{type.label}</option>
					{/each}
				</select>
			</div>

			<!-- Target Term Search -->
			<div>
				<label class="block text-sm font-medium text-gray-700 mb-2">Vers (terme cible)</label>
				<div class="relative">
					<input
						type="text"
						placeholder="Chercher un terme..."
						bind:value={targetTermQuery}
						on:input={handleTargetSearch}
						class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-600 focus:border-transparent"
					/>

					{#if loading}
						<div class="absolute right-3 top-2">
							<div class="w-5 h-5 border-2 border-gray-300 border-t-primary-600 rounded-full animate-spin" />
						</div>
					{/if}

					{#if suggestedTerms.length > 0}
						<div class="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-300 rounded-lg shadow-lg z-10">
							{#each suggestedTerms as term}
								<button
									on:click={() => selectTerm(term)}
									class="w-full text-left px-3 py-2 hover:bg-gray-100 transition-colors border-b border-gray-200 last:border-0"
								>
									<p class="font-medium text-gray-900">{term.name}</p>
									{#if term.definition}
										<p class="text-xs text-gray-500 line-clamp-1">{term.definition}</p>
									{/if}
								</button>
							{/each}
						</div>
					{/if}
				</div>
			</div>

			{#if targetTermName}
				<div class="p-3 bg-blue-50 rounded-lg border border-blue-200">
					<p class="text-sm font-medium text-blue-900">Sélectionné: <span class="font-bold">{targetTermName}</span></p>
				</div>
			{/if}
		</div>

		<!-- Footer -->
		<div class="sticky bottom-0 bg-gray-50 border-t border-gray-200 px-6 py-4 flex gap-3">
			<Button variant="ghost" on:click={handleClose} class="flex-1">
				Annuler
			</Button>
			<Button
				variant="primary"
				on:click={handleSubmit}
				disabled={!targetTermId || submitting}
				class="flex-1"
			>
				{submitting ? 'Création...' : 'Créer'}
			</Button>
		</div>
	</div>
</div>

<style>
	:global(.line-clamp-1) {
		display: -webkit-box;
		-webkit-line-clamp: 1;
		-webkit-box-orient: vertical;
		overflow: hidden;
	}

	:global(.animate-spin) {
		animation: spin 1s linear infinite;
	}

	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}
</style>
