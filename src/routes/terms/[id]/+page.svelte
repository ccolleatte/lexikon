<script lang="ts">
	import { page } from '$app/stores';
	import { onMount } from 'svelte';
	import Button from '$components/Button.svelte';
	import NavBar from '$lib/components/NavBar.svelte';
	import RelationModal from '$lib/components/RelationModal.svelte';
	import { apiCall } from '$lib/utils/api';
	import { addToast } from '$lib/stores/notifications';

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

	interface Relation {
		id: string;
		sourceTermId: string;
		targetTermId: string;
		type: string;
		targetTermName: string;
	}

	let term: Term | null = null;
	let relations: Relation[] = [];
	let loading = true;
	let error: string | null = null;
	let showRelationModal = false;
	let deleting = false;

	onMount(async () => {
		await loadTerm();
	});

	async function loadTerm() {
		try {
			loading = true;
			error = null;
			const termId = $page.params.id;

			// Get term details
			const termResponse = await apiCall(`/api/terms/${termId}`, {
				method: 'GET'
			});

			if (!termResponse.success) {
				throw new Error(termResponse.error?.message || 'Terme non trouvé');
			}

			term = termResponse.data;

			// Try to get relations
			try {
				const relResponse = await apiCall(`/api/ontology/relations/${termId}`, {
					method: 'GET'
				});

				if (relResponse.success) {
					relations = relResponse.data || [];
				}
			} catch {
				// Relations not available
				relations = [];
			}
		} catch (err) {
			error = err instanceof Error ? err.message : 'Erreur lors du chargement du terme';
		} finally {
			loading = false;
		}
	}

	async function deleteTerm() {
		if (!confirm('Êtes-vous sûr de vouloir supprimer ce terme ?')) return;

		try {
			const response = await apiCall(`/api/terms/${term?.id}`, {
				method: 'DELETE'
			});

			if (!response.success) {
				throw new Error(response.error?.message || 'Erreur lors de la suppression');
			}

			window.location.href = '/terms';
		} catch (err) {
			error = err instanceof Error ? err.message : 'Erreur lors de la suppression';
		}
	}

	async function deleteRelation(relationId: string) {
		if (!confirm('Êtes-vous sûr de vouloir supprimer cette relation ?')) return;

		try {
			deleting = true;
			const response = await apiCall(`/api/ontology/relations/${relationId}`, {
				method: 'DELETE'
			});

			if (!response.success) {
				throw new Error(response.error?.message || 'Erreur lors de la suppression');
			}

			addToast('success', 'Relation supprimée avec succès');
			await loadTerm();
		} catch (err) {
			const errorMessage = err instanceof Error ? err.message : 'Erreur lors de la suppression';
			addToast('error', errorMessage);
		} finally {
			deleting = false;
		}
	}

	function handleRelationAdded() {
		showRelationModal = false;
		loadTerm();
	}

	function formatDate(dateStr: string): string {
		const date = new Date(dateStr);
		return date.toLocaleDateString('fr-FR', {
			year: 'numeric',
			month: 'long',
			day: 'numeric',
			hour: '2-digit',
			minute: '2-digit'
		});
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

	function getStatusBadgeColor(status: string): string {
		switch (status) {
			case 'draft':
				return 'bg-gray-100 text-gray-800';
			case 'active':
				return 'bg-green-100 text-green-800';
			case 'deprecated':
				return 'bg-red-100 text-red-800';
			default:
				return 'bg-gray-100 text-gray-800';
		}
	}
</script>

<svelte:head>
	<title>{term?.name || 'Terme'} - Lexikon</title>
</svelte:head>

<NavBar />

<div class="min-h-screen bg-gray-50">
	<div class="max-w-4xl mx-auto px-4 sm:px-6 py-12">
		{#if loading}
			<div class="text-center py-12">
				<div class="inline-block">
					<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
				</div>
				<p class="text-gray-600 mt-4">Chargement du terme...</p>
			</div>
		{:else if error}
			<div class="bg-red-50 border border-red-200 rounded-lg p-6 mb-6">
				<p class="text-red-800 font-medium">{error}</p>
				<Button href="/terms" variant="outline" class="mt-4">← Retour aux termes</Button>
			</div>
		{:else if term}
			<!-- Breadcrumb -->
			<div class="mb-6">
				<a href="/terms" class="text-primary-600 hover:text-primary-700 text-sm">← Mes termes</a>
			</div>

			<!-- Header Card -->
			<div class="bg-white rounded-lg border border-gray-200 p-8 mb-6">
				<div class="flex flex-col sm:flex-row justify-between items-start gap-4">
					<div class="flex-1">
						<h1 class="text-3xl font-bold text-gray-900">{term.name}</h1>
						<div class="flex flex-wrap gap-2 mt-3">
							<span class="inline-block px-3 py-1 rounded-full text-xs font-medium {getLevelBadgeColor(term.level)}">
								{term.level}
							</span>
							<span class="inline-block px-3 py-1 rounded-full text-xs font-medium {getStatusBadgeColor(term.status)}">
								{term.status}
							</span>
						</div>
					</div>
					<div class="flex flex-col gap-2">
						<Button href="/terms/{term.id}/edit" variant="primary">Éditer</Button>
						<Button on:click={deleteTerm} variant="danger">Supprimer</Button>
					</div>
				</div>
			</div>

			<!-- Content -->
			<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
				<!-- Main Content -->
				<div class="lg:col-span-2">
					<!-- Definition Card -->
					<div class="bg-white rounded-lg border border-gray-200 p-6 mb-6">
						<h2 class="text-lg font-semibold text-gray-900 mb-4">Définition</h2>
						<p class="text-gray-700 leading-relaxed">
							{term.definition || 'Aucune définition fournie'}
						</p>
					</div>

					<!-- Relations Card -->
					<div class="bg-white rounded-lg border border-gray-200 p-6">
						<div class="flex items-center justify-between mb-4">
							<h2 class="text-lg font-semibold text-gray-900">Relations ({relations.length})</h2>
							<Button on:click={() => showRelationModal = true} variant="primary" size="sm">
								+ Ajouter
							</Button>
						</div>

						{#if relations.length > 0}
							<div class="space-y-3">
								{#each relations as relation (relation.id)}
									<div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
										<div class="flex-grow">
											<p class="text-sm font-medium text-gray-700">
												<span class="font-semibold">{relation.type}</span>
											</p>
											<p class="text-sm text-gray-600">
												→ {relation.targetTermName}
											</p>
										</div>
										<div class="flex items-center gap-2 ml-4">
											<a href="/terms/{relation.targetTermId}" class="text-primary-600 hover:text-primary-700 text-sm px-2 py-1 rounded hover:bg-primary-50">
												Voir
											</a>
											<button
												on:click={() => deleteRelation(relation.id)}
												disabled={deleting}
												class="text-red-600 hover:text-red-700 text-sm px-2 py-1 rounded hover:bg-red-50 disabled:opacity-50"
												title="Supprimer"
											>
												✕
											</button>
										</div>
									</div>
								{/each}
							</div>
						{:else}
							<p class="text-gray-600 text-center py-4">Aucune relation définie.</p>
						{/if}
					</div>
				</div>

				<!-- Sidebar -->
				<div class="lg:col-span-1">
					<!-- Metadata Card -->
					<div class="bg-white rounded-lg border border-gray-200 p-6">
						<h3 class="text-lg font-semibold text-gray-900 mb-4">Détails</h3>
						<div class="space-y-4">
							<div>
								<p class="text-xs font-semibold text-gray-600 uppercase">Domaine</p>
								<p class="text-sm text-gray-900">{term.domain}</p>
							</div>
							<div>
								<p class="text-xs font-semibold text-gray-600 uppercase">ID</p>
								<p class="text-xs text-gray-600 font-mono break-all">{term.id}</p>
							</div>
							<div>
								<p class="text-xs font-semibold text-gray-600 uppercase">Créé</p>
								<p class="text-sm text-gray-900">{formatDate(term.createdAt)}</p>
							</div>
							<div>
								<p class="text-xs font-semibold text-gray-600 uppercase">Modifié</p>
								<p class="text-sm text-gray-900">{formatDate(term.updatedAt)}</p>
							</div>
						</div>
					</div>

					<!-- Actions Card -->
					<div class="bg-white rounded-lg border border-gray-200 p-6 mt-6">
						<h3 class="text-lg font-semibold text-gray-900 mb-4">Actions</h3>
						<div class="space-y-2">
							<Button href="/terms/{term.id}/edit" variant="outline" class="w-full">
								Éditer le terme
							</Button>
							<Button href="/terms" variant="outline" class="w-full">
								Voir tous les termes
							</Button>
						</div>
					</div>
				</div>
			</div>
		{/if}
	</div>
</div>

<!-- Relation Modal -->
{#if showRelationModal && term}
	<RelationModal
		termId={term.id}
		termName={term.name}
		on:added={handleRelationAdded}
		on:close={() => (showRelationModal = false)}
	/>
{/if}
