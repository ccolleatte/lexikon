<script lang="ts">
	import { goto } from '$app/navigation';
	import { onboarding } from '$lib/stores/onboarding';
	import Button from '$components/Button.svelte';
	import Input from '$components/Input.svelte';
	import Select from '$components/Select.svelte';
	import Stepper from '$components/Stepper.svelte';
	import type { SelectOption } from '$components/Select.svelte';
	import { api } from '$lib/utils/api';

	// Redirect if no adoption level selected
	$: if (!$onboarding.adoptionLevel) {
		goto('/onboarding');
	}

	// Form data
	let firstName = $onboarding.profile?.firstName || '';
	let lastName = $onboarding.profile?.lastName || '';
	let email = $onboarding.profile?.email || '';
	let institution = $onboarding.profile?.institution || '';
	let primaryDomain = $onboarding.profile?.primaryDomain || '';
	let language = $onboarding.profile?.language || 'fr';
	let country = $onboarding.profile?.country || '';

	// Validation errors
	let firstNameError = '';
	let lastNameError = '';
	let emailError = '';

	// State
	let touched = {
		firstName: false,
		lastName: false,
		email: false
	};
	let isSubmitting = false;

	// Domain options
	const domainOptions: SelectOption[] = [
		{ value: 'philosophie', label: 'Philosophie' },
		{ value: 'sciences-education', label: 'Sciences de l\'éducation' },
		{ value: 'sociologie', label: 'Sociologie' },
		{ value: 'psychologie', label: 'Psychologie' },
		{ value: 'linguistique', label: 'Linguistique' },
		{ value: 'histoire', label: 'Histoire' },
		{ value: 'informatique', label: 'Informatique' },
		{ value: 'data-science', label: 'Data Science' },
		{ value: 'autre', label: 'Autre' }
	];

	const languageOptions: SelectOption[] = [
		{ value: 'fr', label: 'Français' },
		{ value: 'en', label: 'English' },
		{ value: 'es', label: 'Español' },
		{ value: 'de', label: 'Deutsch' },
		{ value: 'it', label: 'Italiano' }
	];

	const countryOptions: SelectOption[] = [
		{ value: 'FR', label: 'France' },
		{ value: 'BE', label: 'Belgique' },
		{ value: 'CH', label: 'Suisse' },
		{ value: 'CA', label: 'Canada' },
		{ value: 'US', label: 'États-Unis' },
		{ value: 'GB', label: 'Royaume-Uni' },
		{ value: 'DE', label: 'Allemagne' },
		{ value: 'ES', label: 'Espagne' },
		{ value: 'IT', label: 'Italie' }
	];

	// Adoption level badge data
	const adoptionLevelInfo = {
		'quick-project': { icon: '🚀', label: 'Projet Rapide' },
		'research-project': { icon: '🎓', label: 'Projet de Recherche' },
		'production-api': { icon: '⚡', label: 'Production / API' }
	};

	// Validation
	function validateFirstName() {
		if (touched.firstName) {
			if (firstName.length < 2) {
				firstNameError = 'Minimum 2 caractères requis';
			} else {
				firstNameError = '';
			}
		}
	}

	function validateLastName() {
		if (touched.lastName) {
			if (lastName.length < 2) {
				lastNameError = 'Minimum 2 caractères requis';
			} else {
				lastNameError = '';
			}
		}
	}

	function validateEmail() {
		if (touched.email) {
			const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
			if (!emailRegex.test(email)) {
				emailError = 'Veuillez entrer une adresse email valide';
			} else {
				emailError = '';
			}
		}
	}

	$: firstName, validateFirstName();
	$: lastName, validateLastName();
	$: email, validateEmail();

	// Check if form is valid
	$: isValid =
		firstName.length >= 2 &&
		lastName.length >= 2 &&
		/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

	async function handleSubmit() {
		// Mark all as touched
		touched = { firstName: true, lastName: true, email: true };
		validateFirstName();
		validateLastName();
		validateEmail();

		if (!isValid) return;

		isSubmitting = true;

		try {
			// Save to store
			onboarding.setProfile({
				firstName,
				lastName,
				email,
				institution: institution || undefined,
				primaryDomain: primaryDomain || undefined,
				language,
				country: country || undefined
			});

			// Call API (will fail gracefully if backend not running)
			try {
				await api.post('/users/profile', {
					firstName,
					lastName,
					email,
					institution: institution || undefined,
					primaryDomain: primaryDomain || undefined,
					language,
					country: country || undefined,
					sessionId: $onboarding.sessionId
				});
			} catch (error) {
				console.warn('API call failed, continuing with local state:', error);
			}

			// Navigate to terms page (skip preferences for Sprint 1)
			goto('/terms');
		} catch (error) {
			console.error('Error saving profile:', error);
			isSubmitting = false;
		}
	}

	function handleBack() {
		// Save current data to store before going back
		onboarding.setProfile({
			firstName,
			lastName,
			email,
			institution: institution || undefined,
			primaryDomain: primaryDomain || undefined,
			language,
			country: country || undefined
		});

		goto('/onboarding');
	}

	const steps = [
		{ label: 'Adoption' },
		{ label: 'Profil' },
		{ label: 'Préférences' }
	];
</script>

<svelte:head>
	<title>Complétez votre profil - Lexikon</title>
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
	<div class="max-w-2xl mx-auto">
		<!-- Progress Stepper -->
		<Stepper {steps} currentStep={1} />

		<!-- Selected Level Badge -->
		{#if $onboarding.adoptionLevel}
			<div class="text-center mb-8">
				<div class="inline-flex items-center gap-2 px-4 py-2 bg-primary-50 border border-primary-200 rounded-full text-sm text-primary-700">
					<span>{adoptionLevelInfo[$onboarding.adoptionLevel].icon}</span>
					<span>Niveau sélectionné : <strong>{adoptionLevelInfo[$onboarding.adoptionLevel].label}</strong></span>
				</div>
			</div>
		{/if}

		<!-- Main Card -->
		<form on:submit|preventDefault={handleSubmit}>
			<div class="bg-white rounded-xl shadow-sm p-8">
				<div class="text-center mb-8">
					<h1 class="text-2xl font-semibold text-gray-900 mb-2">
						Complétez votre profil
					</h1>
					<p class="text-base text-gray-600">
						Aidez-nous à personnaliser votre expérience Lexikon
					</p>
				</div>

				<!-- Name Fields -->
				<div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
					<Input
						label="Prénom"
						bind:value={firstName}
						placeholder="Marie"
						required
						errorMessage={firstNameError}
						on:blur={() => (touched.firstName = true)}
					/>

					<Input
						label="Nom"
						bind:value={lastName}
						placeholder="Dupont"
						required
						errorMessage={lastNameError}
						on:blur={() => (touched.lastName = true)}
					/>
				</div>

				<!-- Email -->
				<div class="mb-6">
					<Input
						type="email"
						label="Email"
						bind:value={email}
						placeholder="marie.dupont@universite.fr"
						required
						errorMessage={emailError}
						helperText="Nous utiliserons cette adresse pour les notifications importantes"
						on:blur={() => (touched.email = true)}
					/>
				</div>

				<!-- Institution & Domain -->
				<div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
					<Input
						label="Institution"
						bind:value={institution}
						placeholder="Université Paris-Sorbonne"
						helperText="Université, entreprise, ou organisme"
					/>

					<Select
						label="Domaine principal"
						options={domainOptions}
						bind:value={primaryDomain}
						placeholder="Sélectionnez un domaine"
						helperText="Pour de meilleures suggestions AI"
					/>
				</div>

				<!-- Language & Country -->
				<div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
					<Select
						label="Langue préférée"
						options={languageOptions}
						bind:value={language}
					/>

					<Select
						label="Pays"
						options={countryOptions}
						bind:value={country}
						placeholder="Sélectionnez un pays"
					/>
				</div>

				<!-- Actions -->
				<div class="flex flex-col sm:flex-row gap-3 pt-6 border-t border-gray-200">
					<Button
						type="button"
						variant="ghost"
						size="md"
						on:click={handleBack}
						class="flex-1"
					>
						← Précédent
					</Button>
					<Button
						type="submit"
						variant="primary"
						size="md"
						disabled={!isValid || isSubmitting}
						loading={isSubmitting}
						class="flex-1"
					>
						Continuer →
					</Button>
				</div>
			</div>
		</form>
	</div>
</div>
