<script lang="ts">
	import { page } from '$app/stores';
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import Button from '$components/Button.svelte';
	import Input from '$components/Input.svelte';
	import Select from '$components/Select.svelte';
	import Textarea from '$components/Textarea.svelte';
	import NavBar from '$lib/components/NavBar.svelte';
	import { apiCall } from '$lib/utils/api';

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

	let term: Term | null = null;
	let loading = true;
	let saving = false;
	let error: string | null = null;

	// Form fields
	let name = '';
	let definition = '';
	let domain = '';
	let level = '';
	let status = '';

	const domains = ['Informatique', 'Médecine', 'Droit', 'Economie', 'Autre'];
	const levels = ['Quick Draft', 'Ready', 'Production'];
	const statuses = ['draft', 'active', 'deprecated'];

	onMount(async () => {
		await loadTerm();
	});

	async function loadTerm() {
		try {
			loading = true;
			error = null;
			const termId = $page.params.id;

			const response = await apiCall(`/api/terms/${termId}`, {
				method: 'GET'
			});

			if (!response.success) {
				throw new Error(response.error?.message || 'Terme non trouvé');
			}

			term = response.data;
			name = term.name;
			definition = term.definition;
			domain = term.domain;
			level = term.level;
			status = term.status;
		} catch (err) {
			error = err instanceof Error ? err.message : 'Erreur lors du chargement du terme';
		} finally {
			loading = false;
		}
	}

	async function handleSubmit() {
		if (!term) return;

		try {
			saving = true;
			error = null;

			if (!name.trim()) {
				throw new Error('Le nom du terme est obligatoire');
			}

			const response = await apiCall(`/api/terms/${term.id}`, {
				method: 'PUT',
				body: JSON.stringify({
					name: name.trim(),
					definition: definition.trim(),
					domain,
					level,
					status
				})
			});

			if (!response.success) {
				throw new Error(response.error?.message || 'Erreur lors de la sauvegarde');
			}

			await goto(`/terms/${term.id}`);
		} catch (err) {
			error = err instanceof Error ? err.message : 'Erreur inconnue';
		} finally {
			saving = false;
		}
	}
</script>

<svelte:head>
	<title>Éditer - {term?.name || 'Terme'} - Lexikon</title>
</svelte:head>

<NavBar />

<div class="min-h-screen bg-gray-50">
	<div class="max-w-2xl mx-auto px-4 sm:px-6 py-12">
		{#if loading}
			<div class="text-center py-12">
				<div class="inline-block">
					<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
				</div>
				<p class="text-gray-600 mt-4">Chargement du terme...</p>
			</div>
		{:else if error && !term}
			<div class="bg-red-50 border border-red-200 rounded-lg p-6 mb-6">
				<p class="text-red-800 font-medium">{error}</p>
				<Button href="/terms" variant="outline" class="mt-4">← Retour aux termes</Button>
			</div>
		{:else if term}
			<!-- Breadcrumb -->
			<div class="mb-6">
				<a href="/terms/{term.id}" class="text-primary-600 hover:text-primary-700 text-sm">← {term.name}</a>
			</div>

			<!-- Header -->
			<div class="mb-8">
				<h1 class="text-3xl font-bold text-gray-900">Éditer le terme</h1>
				<p class="text-gray-600 mt-2">Modifiez les informations de votre terme</p>
			</div>

			<!-- Form -->
			<div class="bg-white rounded-lg border border-gray-200 p-8">
				{#if error}
					<div class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
						<p class="text-red-800">{error}</p>
					</div>
				{/if}

				<form on:submit|preventDefault={handleSubmit} class="space-y-6">
					<!-- Name -->
					<div>
						<label for="name" class="block text-sm font-medium text-gray-700 mb-2">
							Nom du terme <span class="text-red-600">*</span>
						</label>
						<Input
							id="name"
							type="text"
							placeholder="Ex: Ontologie"
							bind:value={name}
							required
						/>
						<p class="text-xs text-gray-600 mt-1">Identifie le terme de manière unique</p>
					</div>

					<!-- Definition -->
					<div>
						<label for="definition" class="block text-sm font-medium text-gray-700 mb-2">
							Définition
						</label>
						<Textarea
							id="definition"
							placeholder="Description détaillée du terme..."
							bind:value={definition}
							rows={6}
						/>
						<p class="text-xs text-gray-600 mt-1">Fournissez une définition claire et concise</p>
					</div>

					<!-- Domain and Level -->
					<div class="grid grid-cols-1 sm:grid-cols-2 gap-6">
						<div>
							<label for="domain" class="block text-sm font-medium text-gray-700 mb-2">
								Domaine <span class="text-red-600">*</span>
							</label>
							<Select
								id="domain"
								bind:value={domain}
								options={domains.map(d => ({ value: d, label: d }))}
								required
							/>
						</div>

						<div>
							<label for="level" class="block text-sm font-medium text-gray-700 mb-2">
								Niveau <span class="text-red-600">*</span>
							</label>
							<Select
								id="level"
								bind:value={level}
								options={levels.map(l => ({ value: l, label: l }))}
								required
							/>
						</div>
					</div>

					<!-- Status -->
					<div>
						<label for="status" class="block text-sm font-medium text-gray-700 mb-2">
							Statut
						</label>
						<Select
							id="status"
							bind:value={status}
							options={statuses.map(s => ({ value: s, label: s }))}
						/>
						<p class="text-xs text-gray-600 mt-1">
							<strong>Draft:</strong> En brouillon | <strong>Active:</strong> En utilisation | <strong>Deprecated:</strong> Obsolète
						</p>
					</div>

					<!-- Actions -->
					<div class="flex gap-4 pt-6 border-t border-gray-200">
						<Button
							type="submit"
							variant="primary"
							disabled={saving}
						>
							{saving ? 'Sauvegarde...' : 'Sauvegarder'}
						</Button>
						<Button
							href="/terms/{term.id}"
							variant="outline"
							disabled={saving}
						>
							Annuler
						</Button>
					</div>
				</form>
			</div>
		{/if}
	</div>
</div>
