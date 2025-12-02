<script lang="ts">
	import { goto } from '$app/navigation';
	import Button from '$components/Button.svelte';
	import { onboarding } from '$lib/stores/onboarding';
	import type { AdoptionLevel } from '$types';
	import { api } from '$lib/utils/api';

	let selectedLevel: AdoptionLevel | null = null;
	let isSubmitting = false;

	interface LevelOption {
		id: AdoptionLevel;
		icon: string;
		title: string;
		subtitle: string;
		quote: string;
		features: string[];
		badge: {
			text: string;
			color: string;
		};
	}

	const levels: LevelOption[] = [
		{
			id: 'quick-project',
			icon: '🚀',
			title: 'Projet Rapide',
			subtitle: 'Étudiant, usage ponctuel · 6 mois',
			quote: "J'ai besoin d'une ontologie pour mon mémoire de M2",
			features: [
				'Setup en 30 minutes',
				'Export quand terminé',
				'Gratuit, pas de validation obligatoire'
			],
			badge: {
				text: 'Gratuit',
				color: 'bg-success-500'
			}
		},
		{
			id: 'research-project',
			icon: '🎓',
			title: 'Projet de Recherche',
			subtitle: 'Chercheur, usage récurrent · 1-2 ans',
			quote: "J'ai besoin d'un vocabulaire contrôlé pour ma thèse",
			features: [
				'Collaboration avec pairs',
				'Validation experte optionnelle',
				'Export multi-formats (RDF, JSON-LD, CSV)'
			],
			badge: {
				text: 'Pro €49/mois',
				color: 'bg-primary-600'
			}
		},
		{
			id: 'production-api',
			icon: '⚡',
			title: 'Production / API',
			subtitle: 'Développeur, intégration continue',
			quote: "J'intègre une ontologie dans mon app d'écriture académique",
			features: [
				'API REST complète',
				'Webhooks & GraphQL',
				'SLA 99.9% uptime'
			],
			badge: {
				text: 'Team €199/mois',
				color: 'bg-secondary-600'
			}
		}
	];

	async function handleContinue() {
		if (!selectedLevel) return;

		isSubmitting = true;

		try {
			// Save to store
			onboarding.setAdoptionLevel(selectedLevel);

			// Call API (will fail if backend not running, but continue anyway)
			try {
				await api.post('/onboarding/adoption-level', {
					adoptionLevel: selectedLevel,
					sessionId: $onboarding.sessionId
				});
			} catch (error) {
				console.warn('API call failed, continuing with local state:', error);
			}

			// Navigate to profile setup
			goto('/onboarding/profile');
		} catch (error) {
			console.error('Error saving adoption level:', error);
			isSubmitting = false;
		}
	}

	// Restore selection from store
	$: if ($onboarding.adoptionLevel) {
		selectedLevel = $onboarding.adoptionLevel;
	}
</script>

<svelte:head>
	<title>Choisissez votre niveau d'adoption - Lexikon</title>
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
	</div>
</div>

<div class="min-h-screen bg-gray-50 py-12 px-4">
	<div class="max-w-5xl mx-auto">
		<!-- Header -->
		<div class="text-center mb-12">
			<h1 class="text-3xl font-bold text-gray-900 mb-3">
				Bienvenue sur Lexikon
			</h1>
			<p class="text-lg text-gray-600">
				Choisissez le niveau d'adoption qui correspond le mieux à votre besoin
			</p>
		</div>

		<!-- Level Cards -->
		<div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
			{#each levels as level}
				<label class="radio-card cursor-pointer transition-all duration-200" class:selected={selectedLevel === level.id}>
					<input
						type="radio"
						name="adoption-level"
						value={level.id}
						bind:group={selectedLevel}
						class="sr-only"
					/>

					<div class="bg-white rounded-xl border-2 p-6 h-full flex flex-col transition-all duration-200
						{selectedLevel === level.id
							? 'border-primary-500 shadow-md ring-2 ring-primary-100'
							: 'border-gray-200 hover:border-primary-300 hover:shadow-sm'}"
					>
						<!-- Icon & Badge -->
						<div class="flex justify-between items-start mb-4">
							<div class="text-4xl">{level.icon}</div>
							<span class="px-3 py-1 rounded-full text-xs font-medium text-white {level.badge.color}">
								{level.badge.text}
							</span>
						</div>

						<!-- Title & Subtitle -->
						<h3 class="text-xl font-semibold text-gray-900 mb-2">
							{level.title}
						</h3>
						<p class="text-sm text-gray-600 mb-4">
							{level.subtitle}
						</p>

						<!-- Quote -->
						<blockquote class="italic text-sm text-gray-700 mb-6 border-l-2 border-primary-200 pl-3">
							"{level.quote}"
						</blockquote>

						<!-- Features -->
						<ul class="space-y-2 flex-1">
							{#each level.features as feature}
								<li class="flex items-start gap-2 text-sm text-gray-700">
									<span class="text-primary-500 mt-0.5">→</span>
									<span>{feature}</span>
								</li>
							{/each}
						</ul>

						<!-- Selection Indicator -->
						{#if selectedLevel === level.id}
							<div class="mt-4 pt-4 border-t border-gray-200">
								<div class="flex items-center gap-2 text-sm font-medium text-primary-600">
									<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
									</svg>
									Sélectionné
								</div>
							</div>
						{/if}
					</div>
				</label>
			{/each}
		</div>

		<!-- Actions -->
		<div class="flex flex-col sm:flex-row gap-4 justify-center items-center">
			<Button
				variant="primary"
				size="lg"
				disabled={!selectedLevel || isSubmitting}
				loading={isSubmitting}
				on:click={handleContinue}
			>
				Continuer →
			</Button>

			<a href="/quiz" class="text-sm text-gray-600 hover:text-gray-900 transition-colors">
				Pas sûr ? → Quiz 2 minutes
			</a>
		</div>
	</div>
</div>

<style>
	.radio-card input[type="radio"]:checked + div {
		transform: translateY(-2px);
	}
</style>
