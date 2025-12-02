<script lang="ts">
	import { onMount } from 'svelte';
	import Button from '$components/Button.svelte';
	import NavBar from '$lib/components/NavBar.svelte';
	import { apiCall } from '$lib/utils/api';

	interface Project {
		id: string;
		name: string;
		description: string;
		language: string;
		primary_domain: string;
		is_public: boolean;
		owner_id: string;
		created_at: string;
		updated_at: string;
		term_count: number;
		member_count: number;
		is_owner: boolean;
		role: string;
	}

	let projects: Project[] = [];
	let loading = true;
	let error: string | null = null;
	let showCreateModal = false;
	let newProjectName = '';
	let newProjectDescription = '';
	let creating = false;

	onMount(async () => {
		await loadProjects();
	});

	async function loadProjects() {
		try {
			loading = true;
			error = null;
			const response = await apiCall('/api/projects', {
				method: 'GET'
			});

			if (!response.success) {
				throw new Error(response.error?.message || 'Erreur lors du chargement des projets');
			}

			projects = response.data || [];
		} catch (err) {
			error = err instanceof Error ? err.message : 'Erreur inconnue';
		} finally {
			loading = false;
		}
	}

	async function createProject() {
		if (!newProjectName.trim()) {
			error = 'Le nom du projet est obligatoire';
			return;
		}

		try {
			creating = true;
			error = null;

			const response = await apiCall('/api/projects', {
				method: 'POST',
				body: JSON.stringify({
					name: newProjectName.trim(),
					description: newProjectDescription.trim() || null,
					language: 'fr',
					is_public: false
				})
			});

			if (!response.success) {
				throw new Error(response.error?.message || 'Erreur lors de la création');
			}

			newProjectName = '';
			newProjectDescription = '';
			showCreateModal = false;
			await loadProjects();
		} catch (err) {
			error = err instanceof Error ? err.message : 'Erreur lors de la création';
		} finally {
			creating = false;
		}
	}

	async function deleteProject(id: string) {
		if (!confirm('Êtes-vous sûr de vouloir supprimer ce projet ?')) return;

		try {
			const response = await apiCall(`/api/projects/${id}`, {
				method: 'DELETE'
			});

			if (!response.success) {
				throw new Error(response.error?.message || 'Erreur lors de la suppression');
			}

			await loadProjects();
		} catch (err) {
			error = err instanceof Error ? err.message : 'Erreur lors de la suppression';
		}
	}

	function formatDate(dateStr: string): string {
		const date = new Date(dateStr);
		return date.toLocaleDateString('fr-FR', { year: 'numeric', month: 'short', day: 'numeric' });
	}

	function getRoleBadgeColor(role: string): string {
		return role === 'owner' ? 'bg-purple-100 text-purple-800' : 'bg-blue-100 text-blue-800';
	}
</script>

<svelte:head>
	<title>Mes Projets - Lexikon</title>
</svelte:head>

<NavBar />

<div class="min-h-screen bg-gray-50">
	<div class="max-w-7xl mx-auto px-4 sm:px-6 py-12">
		<!-- Header -->
		<div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
			<div>
				<h1 class="text-3xl font-bold text-gray-900">Mes Projets</h1>
				<p class="text-gray-600 mt-1">
					Vous avez <strong>{projects.length}</strong> projet{projects.length !== 1 ? 's' : ''}
				</p>
			</div>
			<Button on:click={() => (showCreateModal = true)} variant="primary">+ Nouveau projet</Button>
		</div>

		{#if error}
			<div class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
				<p class="text-red-800">{error}</p>
			</div>
		{/if}

		<!-- Loading State -->
		{#if loading}
			<div class="text-center py-12">
				<div class="inline-block">
					<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
				</div>
				<p class="text-gray-600 mt-4">Chargement des projets...</p>
			</div>
		{:else if projects.length === 0}
			<!-- Empty State -->
			<div class="text-center py-16 bg-white rounded-lg border border-gray-200">
				<div class="inline-flex items-center justify-center w-24 h-24 bg-gray-100 rounded-full mb-6">
					<span class="text-5xl">📁</span>
				</div>

				<h2 class="text-2xl font-bold text-gray-900 mb-3">Aucun projet pour l'instant</h2>
				<p class="text-gray-600 mb-8 max-w-md mx-auto">
					Créez votre premier projet pour commencer à organiser vos termes et ontologies.
				</p>

				<Button on:click={() => (showCreateModal = true)} variant="primary">
					Créer mon premier projet →
				</Button>
			</div>
		{:else}
			<!-- Projects Grid -->
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
				{#each projects as project (project.id)}
					<div class="bg-white rounded-lg border border-gray-200 hover:border-primary-300 transition-colors overflow-hidden">
						<!-- Header -->
						<div class="p-6 border-b border-gray-200 bg-gradient-to-r from-primary-50 to-transparent">
							<a href="/projects/{project.id}" class="text-lg font-semibold text-gray-900 hover:text-primary-600">
								{project.name}
							</a>
							<div class="flex gap-2 mt-2">
								<span class="inline-block px-2 py-1 rounded text-xs font-medium {getRoleBadgeColor(project.role)}">
									{project.role === 'owner' ? 'Propriétaire' : 'Membre'}
								</span>
								{#if project.is_public}
									<span class="inline-block px-2 py-1 rounded text-xs font-medium bg-green-100 text-green-800">
										Public
									</span>
								{:else}
									<span class="inline-block px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-800">
										Privé
									</span>
								{/if}
							</div>
						</div>

						<!-- Content -->
						<div class="p-6">
							<p class="text-sm text-gray-600 line-clamp-2 mb-4">
								{project.description || 'Pas de description'}
							</p>

							<!-- Stats -->
							<div class="grid grid-cols-2 gap-4 mb-4 py-4 border-t border-b border-gray-200">
								<div class="text-center">
									<p class="text-2xl font-bold text-primary-600">{project.term_count}</p>
									<p class="text-xs text-gray-600">terme{project.term_count !== 1 ? 's' : ''}</p>
								</div>
								<div class="text-center">
									<p class="text-2xl font-bold text-primary-600">{project.member_count}</p>
									<p class="text-xs text-gray-600">membre{project.member_count !== 1 ? 's' : ''}</p>
								</div>
							</div>

							<!-- Metadata -->
							<p class="text-xs text-gray-500 mb-4">
								Créé le {formatDate(project.created_at)}
							</p>

							<!-- Actions -->
							<div class="flex gap-2">
								<a href="/projects/{project.id}" class="flex-1 px-3 py-2 bg-primary-50 text-primary-600 rounded text-sm font-medium hover:bg-primary-100 text-center">
									Ouvrir
								</a>
								{#if project.is_owner}
									<button
										on:click={() => deleteProject(project.id)}
										class="px-3 py-2 bg-red-50 text-red-600 rounded text-sm font-medium hover:bg-red-100"
									>
										×
									</button>
								{/if}
							</div>
						</div>
					</div>
				{/each}
			</div>
		{/if}

		<!-- Create Project Modal -->
		{#if showCreateModal}
			<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
				<div class="bg-white rounded-lg max-w-md w-full p-8">
					<h2 class="text-2xl font-bold text-gray-900 mb-6">Créer un nouveau projet</h2>

					<div class="space-y-6">
						<!-- Name -->
						<div>
							<label for="project-name" class="block text-sm font-medium text-gray-700 mb-2">
								Nom du projet
							</label>
							<input
								id="project-name"
								type="text"
								placeholder="Ex: Ontologie Médicale"
								bind:value={newProjectName}
								class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
							/>
						</div>

						<!-- Description -->
						<div>
							<label for="project-desc" class="block text-sm font-medium text-gray-700 mb-2">
								Description (optionnel)
							</label>
							<textarea
								id="project-desc"
								placeholder="Décrivez votre projet..."
								bind:value={newProjectDescription}
								rows={4}
								class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
							/>
						</div>

						{#if error}
							<div class="bg-red-50 border border-red-200 rounded-lg p-4">
								<p class="text-red-800 text-sm">{error}</p>
							</div>
						{/if}

						<!-- Actions -->
						<div class="flex gap-4">
							<button
								on:click={() => (showCreateModal = false)}
								disabled={creating}
								class="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 disabled:opacity-50"
							>
								Annuler
							</button>
							<button
								on:click={createProject}
								disabled={creating}
								class="flex-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
							>
								{creating ? 'Création...' : 'Créer'}
							</button>
						</div>
					</div>
				</div>
			</div>
		{/if}
	</div>
</div>
