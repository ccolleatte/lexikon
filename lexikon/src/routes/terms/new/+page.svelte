<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import Button from '$components/Button.svelte';
	import Input from '$components/Input.svelte';
	import Textarea from '$components/Textarea.svelte';
	import Progress from '$components/Progress.svelte';
	import Alert from '$components/Alert.svelte';
	import { api } from '$lib/utils/api';

	const DRAFT_KEY = 'lexikon-draft';
	const AUTO_SAVE_DELAY = 1000; // 1 second

	// Form data
	let termName = '';
	let definition = '';
	let domain = '';

	// Validation
	let nameError = '';
	let defError = '';
	let touched = { name: false, definition: false };

	// State
	let autoSaveStatus: 'saved' | 'saving' | 'idle' = 'idle';
	let isSubmitting = false;
	let autoSaveTimeout: ReturnType<typeof setTimeout> | null = null;

	// Progress calculation
	$: progress = calculateProgress(termName, definition, domain);

	function calculateProgress(name: string, def: string, dom: string): number {
		let p = 0;
		if (name.length >= 3) p += 40;
		if (def.length >= 50) p += 50;
		if (dom.length > 0) p += 10;
		return p;
	}

	// Validation
	function validateName() {
		if (touched.name) {
			if (termName.length > 0 && termName.length < 3) {
				nameError = 'Minimum 3 caractères requis';
			} else {
				nameError = '';
			}
		}
	}

	function validateDefinition() {
		if (touched.definition) {
			if (definition.length > 0 && definition.length < 50) {
				defError = `Minimum 50 caractères (actuellement ${definition.length})`;
			} else {
				defError = '';
			}
		}
	}

	$: termName, validateName();
	$: definition, validateDefinition();

	// Form validity
	$: isValid = termName.length >= 3 && definition.length >= 50;

	// Auto-save
	function autoSave() {
		if (autoSaveTimeout) {
			clearTimeout(autoSaveTimeout);
		}

		autoSaveStatus = 'saving';

		autoSaveTimeout = setTimeout(() => {
			const draft = {
				termName,
				definition,
				domain,
				timestamp: new Date().toISOString()
			};

			localStorage.setItem(DRAFT_KEY, JSON.stringify(draft));
			autoSaveStatus = 'saved';

			// Reset to idle after 2 seconds
			setTimeout(() => {
				if (autoSaveStatus === 'saved') {
					autoSaveStatus = 'idle';
				}
			}, 2000);
		}, AUTO_SAVE_DELAY);
	}

	// Trigger auto-save on any change
	$: if (termName || definition || domain) {
		autoSave();
	}

	// Load draft on mount
	onMount(() => {
		const stored = localStorage.getItem(DRAFT_KEY);
		if (stored) {
			try {
				const draft = JSON.parse(stored);
				termName = draft.termName || '';
				definition = draft.definition || '';
				domain = draft.domain || '';
			} catch (e) {
				console.error('Failed to load draft:', e);
			}
		}
	});

	async function handleSubmit() {
		// Mark all as touched
		touched = { name: true, definition: true };
		validateName();
		validateDefinition();

		if (!isValid) return;

		isSubmitting = true;

		try {
			// Call API
			await api.post('/terms', {
				name: termName,
				definition,
				domain: domain || undefined,
				level: 'quick-draft',
				status: 'draft'
			});

			// Clear draft
			localStorage.removeItem(DRAFT_KEY);

			// Navigate to terms list
			goto('/terms?created=true');
		} catch (error) {
			console.error('Error creating term:', error);
			isSubmitting = false;
		}
	}

	async function handleSaveDraft() {
		// Just trigger auto-save immediately
		if (autoSaveTimeout) {
			clearTimeout(autoSaveTimeout);
		}

		const draft = {
			termName,
			definition,
			domain,
			timestamp: new Date().toISOString()
		};

		localStorage.setItem(DRAFT_KEY, JSON.stringify(draft));
		autoSaveStatus = 'saved';

		alert('Brouillon enregistré !');
	}
</script>

<svelte:head>
	<title>Nouveau terme - Quick Draft - Lexikon</title>
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

		<!-- Auto-save status -->
		<div class="flex items-center gap-2 px-3 py-1.5 rounded-md text-sm
			{autoSaveStatus === 'saved' ? 'bg-success-50 text-success-600' :
			 autoSaveStatus === 'saving' ? 'bg-gray-100 text-gray-600' :
			 'bg-gray-50 text-gray-400'}"
		>
			{#if autoSaveStatus === 'saved'}
				<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
					<path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
				</svg>
				Sauvegardé
			{:else if autoSaveStatus === 'saving'}
				<svg class="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
					<path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
				</svg>
				Sauvegarde...
			{:else}
				<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
					<circle cx="12" cy="12" r="10" opacity="0.5"/>
				</svg>
				Auto-save
			{/if}
		</div>
	</div>
</div>

<div class="min-h-screen bg-gray-50 py-8 px-4">
	<div class="max-w-3xl mx-auto">
		<!-- Progress Section -->
		<div class="mb-8">
			<div class="flex justify-between items-center mb-4">
				<h2 class="text-lg font-semibold text-gray-900">Création de terme</h2>
				<span class="inline-flex items-center gap-1.5 px-3 py-1 bg-primary-500 text-white rounded-full text-sm font-medium">
					<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
						<path stroke-linecap="round" stroke-linejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z"/>
					</svg>
					Mode Rapide
				</span>
			</div>
			<Progress value={progress} variant="primary" size="md" />
		</div>

		<!-- Info Banner -->
		<div class="mb-6">
			<Alert variant="info" title="Mode création rapide (5 minutes)">
				Seuls les champs essentiels sont requis. Vous pourrez enrichir le terme plus tard avec des relations, exemples, et validation experte.
			</Alert>
		</div>

		<!-- Main Form Card -->
		<form on:submit|preventDefault={handleSubmit}>
			<div class="bg-white rounded-xl shadow-sm p-8">
				<div class="mb-8">
					<h1 class="text-2xl font-semibold text-gray-900 mb-2">
						Nouveau terme
					</h1>
					<p class="text-base text-gray-600">
						Créez rapidement votre terme avec les informations essentielles
					</p>
				</div>

				<!-- Term Name -->
				<div class="mb-6">
					<Input
						label="Nom du terme"
						bind:value={termName}
						placeholder="Ex: Épistémologie"
						required
						maxlength={100}
						showCharCounter
						errorMessage={nameError}
						helperText="Le nom principal de votre concept (évitez les abréviations)"
						on:blur={() => (touched.name = true)}
					/>
				</div>

				<!-- Definition -->
				<div class="mb-6">
					<Textarea
						label="Définition"
						bind:value={definition}
						placeholder="Définissez le terme de manière claire et concise..."
						required
						maxlength={500}
						showCharCounter
						rows={6}
						errorMessage={defError}
						helperText="Une définition simple et précise (200-300 caractères recommandés)"
						on:blur={() => (touched.definition = true)}
					/>
				</div>

				<!-- Domain (Optional) -->
				<div class="mb-6">
					<Input
						label="Domaine"
						bind:value={domain}
						placeholder="Ex: Philosophie, Sciences de l'éducation..."
						maxlength={100}
						helperText="Le champ disciplinaire principal (vous pourrez en ajouter d'autres plus tard)"
					/>
				</div>

				<!-- Actions -->
				<div class="flex flex-col sm:flex-row gap-3 pt-6 border-t border-gray-200">
					<Button
						type="submit"
						variant="primary"
						size="md"
						disabled={!isValid || isSubmitting}
						loading={isSubmitting}
						class="flex-1 sm:flex-initial"
					>
						Créer le terme →
					</Button>
					<Button
						type="button"
						variant="ghost"
						size="md"
						on:click={handleSaveDraft}
						class="flex-1 sm:flex-initial"
					>
						Enregistrer comme brouillon
					</Button>
				</div>
			</div>
		</form>

		<!-- Link to Advanced Mode -->
		<div class="text-center mt-6">
			<a href="/terms/new?mode=advanced" class="text-sm text-gray-600 hover:text-gray-900 transition-colors inline-flex items-center gap-1.5">
				Besoin de plus de champs ? → Passer en mode Avancé
			</a>
		</div>
	</div>
</div>
