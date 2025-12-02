<script lang="ts">
	import { onMount } from 'svelte';
	import Button from '$components/Button.svelte';
	import NavBar from '$lib/components/NavBar.svelte';
	import { apiCall } from '$lib/utils/api';
	import { onboarding } from '$lib/stores/onboarding';

	interface Term {
		id: string;
		name: string;
		definition: string;
		domain: string;
		level: string;
		status: string;
		createdAt: string;
		updatedAt: string;
	}

	let terms: Term[] = [];
	let loading = true;
	let error: string | null = null;
	let selectedDomain = '';
	let selectedLevel = '';

	// Domain and level options
	const domains = ['Informatique', 'Médecine', 'Droit', 'Economie', 'Autre'];
	const levels = ['Quick Draft', 'Ready', 'Production'];

	const hasOnboarded = !!$onboarding.profile?.email;

	onMount(async () => {
		await loadTerms();
	});

	async function loadTerms() {
		try {
			loading = true;
			error = null;
			const response = await apiCall('/api/terms', {
				method: 'GET'
			});

			if (!response.success) {
				throw new Error(response.error?.message || 'Erreur lors du chargement des termes');
			}

			terms = response.data || [];
		} catch (err) {
			error = err instanceof Error ? err.message : 'Erreur inconnue';
		} finally {
			loading = false;
		}
	}

	function filteredTerms() {
		return terms.filter((term) => {
			const matchDomain = !selectedDomain || term.domain === selectedDomain;
			const matchLevel = !selectedLevel || term.level === selectedLevel;
			return matchDomain && matchLevel;
		});
	}

	async function deleteTerm(id: string) {
		if (!confirm('Êtes-vous sûr de vouloir supprimer ce terme ?')) return;

		try {
			const response = await apiCall(`/api/terms/${id}`, {
				method: 'DELETE'
			});

			if (!response.success) {
				throw new Error(response.error?.message || 'Erreur lors de la suppression');
			}

			await loadTerms();
		} catch (err) {
			error = err instanceof Error ? err.message : 'Erreur lors de la suppression';
		}
	}

	function formatDate(dateStr: string): string {
		const date = new Date(dateStr);
		return date.toLocaleDateString('fr-FR', { year: 'numeric', month: 'short', day: 'numeric' });
	}

	function getLevelBadgeColor(level: string): string {
		switch (level) {
			case 'Quick Draft':
				return 'bg-yellow-100 text-yellow-800';
			case 'Ready':
				return 'bg-blue-100 text-blue-800';
			case 'Production':
				return 'bg-green-100 text-green-800';
			default:
				return 'bg-gray-100 text-gray-800';
		}
	}
</script>

<svelte:head>
	<title>Mes Termes - Lexikon</title>
</svelte:head>

<NavBar />

<div class="min-h-screen bg-gray-50">
	<div class="max-w-7xl mx-auto px-4 sm:px-6 py-12">
		<!-- Header -->
		<div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
			<div>
				<h1 class="text-3xl font-bold text-gray-900">Mes Termes</h1>
				<p class="text-gray-600 mt-1">
					Vous avez <strong>{terms.length}</strong> terme{terms.length !== 1 ? 's' : ''}
				</p>
			</div>
			<Button href="/terms/new" variant="primary">+ Nouveau terme</Button>
		</div>

		{#if error}
			<div class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
				<p class="text-red-800">{error}</p>
			</div>
		{/if}

		<!-- Filters -->
		{#if terms.length > 0}
			<div class="bg-white rounded-lg border border-gray-200 p-4 mb-6">
				<div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
					<div>
						<label for="domain-filter" class="block text-sm font-medium text-gray-700 mb-2">
							Domaine
						</label>
						<select
							id="domain-filter"
							bind:value={selectedDomain}
							class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
						>
							<option value="">Tous les domaines</option>
							{#each domains as domain}
								<option value={domain}>{domain}</option>
							{/each}
						</select>
					</div>

					<div>
						<label for="level-filter" class="block text-sm font-medium text-gray-700 mb-2">
							Niveau
						</label>
						<select
							id="level-filter"
							bind:value={selectedLevel}
							class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
						>
							<option value="">Tous les niveaux</option>
							{#each levels as level}
								<option value={level}>{level}</option>
							{/each}
						</select>
					</div>
				</div>
			</div>
		{/if}

		<!-- Loading State -->
		{#if loading}
			<div class="text-center py-12">
				<div class="inline-block">
					<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
				</div>
				<p class="text-gray-600 mt-4">Chargement des termes...</p>
			</div>
		{:else if filteredTerms().length === 0}
			<!-- Empty State -->
			<div class="text-center py-16 bg-white rounded-lg border border-gray-200">
				<div class="inline-flex items-center justify-center w-24 h-24 bg-gray-100 rounded-full mb-6">
					<span class="text-5xl">📝</span>
				</div>

				<h2 class="text-2xl font-bold text-gray-900 mb-3">
					{terms.length === 0 ? 'Aucun terme pour l\'instant' : 'Aucun terme correspondant'}
				</h2>
				<p class="text-gray-600 mb-8 max-w-md mx-auto">
					{#if terms.length === 0}
						Commencez à construire votre ontologie en créant votre premier terme.
						Le mode Quick Draft vous permet de créer un terme en moins de 5 minutes.
					{:else}
						Aucun terme ne correspond à vos filtres. Essayez de modifier vos critères.
					{/if}
				</p>

				<div class="flex flex-col sm:flex-row gap-4 justify-center">
					<Button href="/terms/new" variant="primary">Créer un terme →</Button>
					{#if terms.length === 0 && !hasOnboarded}
						<Button href="/onboarding" variant="outline">Compléter mon profil</Button>
					{/if}
				</div>
			</div>
		{:else}
			<!-- Terms Table -->
			<div class="bg-white rounded-lg border border-gray-200 overflow-hidden">
				<div class="overflow-x-auto">
					<table class="w-full">
						<thead class="bg-gray-50 border-b border-gray-200">
							<tr>
								<th class="px-6 py-3 text-left text-sm font-semibold text-gray-700">Nom</th>
								<th class="px-6 py-3 text-left text-sm font-semibold text-gray-700">Domaine</th>
								<th class="px-6 py-3 text-left text-sm font-semibold text-gray-700">Niveau</th>
								<th class="px-6 py-3 text-left text-sm font-semibold text-gray-700">Créé le</th>
								<th class="px-6 py-3 text-right text-sm font-semibold text-gray-700">Actions</th>
							</tr>
						</thead>
						<tbody class="divide-y divide-gray-200">
							{#each filteredTerms() as term (term.id)}
								<tr class="hover:bg-gray-50 transition-colors">
									<td class="px-6 py-4">
										<a href="/terms/{term.id}" class="text-primary-600 hover:text-primary-700 font-medium">
											{term.name}
										</a>
										<p class="text-sm text-gray-600 mt-1 truncate" title={term.definition}>
											{term.definition || 'Pas de définition'}
										</p>
									</td>
									<td class="px-6 py-4 text-sm text-gray-700">{term.domain}</td>
									<td class="px-6 py-4">
										<span class="inline-block px-3 py-1 rounded-full text-xs font-medium {getLevelBadgeColor(term.level)}">
											{term.level}
										</span>
									</td>
									<td class="px-6 py-4 text-sm text-gray-600">{formatDate(term.createdAt)}</td>
									<td class="px-6 py-4 text-right">
										<div class="flex justify-end gap-2">
											<a href="/terms/{term.id}" class="text-primary-600 hover:text-primary-700 text-sm font-medium">
												Voir
											</a>
											<a href="/terms/{term.id}/edit" class="text-primary-600 hover:text-primary-700 text-sm font-medium">
												Éditer
											</a>
											<button
												on:click={() => deleteTerm(term.id)}
												class="text-red-600 hover:text-red-700 text-sm font-medium"
											>
												Supprimer
											</button>
										</div>
									</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
			</div>
		{/if}
	</div>
</div>
