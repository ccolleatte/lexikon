<script lang="ts">
	import Button from '$components/Button.svelte';
	import NavBar from '$lib/components/NavBar.svelte';

	const plans = [
		{
			id: 'quick-project',
			name: 'Quick Project',
			description: 'Parfait pour découvrir',
			price: 'Gratuit',
			features: [
				'Création illimitée de termes',
				'Relations simples',
				'Export basique',
				'Support communauté'
			],
			current: true
		},
		{
			id: 'research-project',
			name: 'Research Project',
			description: 'Pour les projets de recherche',
			price: '9€/mois',
			features: [
				'Tout de Quick Project',
				'Relations avancées (transitive, symmetric)',
				'Export multi-formats (PDF, JSON, XML)',
				'Collaboration avec 5 membres',
				'Historique des versions',
				'Support prioritaire'
			],
			current: false
		},
		{
			id: 'production-api',
			name: 'Production API',
			description: 'Pour les intégrations professionnelles',
			price: '99€/mois',
			features: [
				'Tout de Research Project',
				'Collaboration illimitée',
				'API REST complète',
				'Webhooks',
				'Rate limits élevés (2000 req/min)',
				'SLA 99.9%',
				'Support 24/7'
			],
			current: false
		}
	];

	function getCurrentPlan(adoptionLevel: string): string {
		switch (adoptionLevel) {
			case 'quick-project':
				return 'Quick Project';
			case 'research-project':
				return 'Research Project';
			case 'production-api':
				return 'Production API';
			default:
				return 'Quick Project';
		}
	}

	const currentPlan = getCurrentPlan('quick-project');
</script>

<svelte:head>
	<title>Passer à un plan premium - Lexikon</title>
</svelte:head>

<NavBar />

<div class="min-h-screen bg-gray-50">
	<div class="max-w-7xl mx-auto px-4 sm:px-6 py-12">
		<!-- Header -->
		<div class="text-center mb-16">
			<h1 class="text-4xl font-bold text-gray-900 mb-4">Plans et tarification</h1>
			<p class="text-xl text-gray-600">Choisissez le plan qui correspond à vos besoins</p>
			<p class="text-gray-600 mt-2">Plan actuel: <strong>{currentPlan}</strong></p>
		</div>

		<!-- Plans Grid -->
		<div class="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
			{#each plans as plan (plan.id)}
				<div
					class="bg-white rounded-lg border-2 transition-all {plan.current
						? 'border-primary-500 shadow-lg'
						: 'border-gray-200 hover:border-primary-300'}"
				>
					<!-- Plan Header -->
					<div class="p-8 border-b border-gray-200 bg-gradient-to-r from-gray-50 to-transparent">
						{#if plan.current}
							<div class="inline-block bg-primary-100 text-primary-800 px-3 py-1 rounded-full text-xs font-semibold mb-3">
								Plan actuel
							</div>
						{/if}
						<h2 class="text-2xl font-bold text-gray-900">{plan.name}</h2>
						<p class="text-gray-600 text-sm mt-2">{plan.description}</p>
					</div>

					<!-- Price -->
					<div class="p-8 border-b border-gray-200">
						<p class="text-4xl font-bold text-gray-900">{plan.price}</p>
						{#if plan.price !== 'Gratuit'}
							<p class="text-gray-600 text-sm">par mois</p>
						{/if}
					</div>

					<!-- Features -->
					<div class="p-8 border-b border-gray-200">
						<ul class="space-y-3">
							{#each plan.features as feature}
								<li class="flex items-start gap-3">
									<span class="text-primary-600 font-bold">✓</span>
									<span class="text-gray-700">{feature}</span>
								</li>
							{/each}
						</ul>
					</div>

					<!-- Action Button -->
					<div class="p-8">
						{#if plan.current}
							<button disabled class="w-full px-4 py-2 bg-gray-100 text-gray-600 rounded-lg font-medium">
								Plan actuel
							</button>
						{:else}
							<Button href="#contact" variant="primary" class="w-full">
								Nous contacter
							</Button>
						{/if}
					</div>
				</div>
			{/each}
		</div>

		<!-- FAQ Section -->
		<div class="max-w-3xl mx-auto">
			<h2 class="text-2xl font-bold text-gray-900 mb-8 text-center">Questions fréquentes</h2>

			<div class="space-y-6">
				<div class="bg-white rounded-lg p-6 border border-gray-200">
					<h3 class="font-semibold text-gray-900 mb-2">Comment puis-je changer de plan?</h3>
					<p class="text-gray-600">Rendez-vous dans les paramètres de votre compte et sélectionnez le plan que vous souhaitez. Votre accès aux nouvelles fonctionnalités sera activé immédiatement.</p>
				</div>

				<div class="bg-white rounded-lg p-6 border border-gray-200">
					<h3 class="font-semibold text-gray-900 mb-2">Puis-je annuler mon abonnement?</h3>
					<p class="text-gray-600">Oui, vous pouvez annuler à tout moment. Vous garderez l'accès jusqu'à la fin du mois en cours.</p>
				</div>

				<div class="bg-white rounded-lg p-6 border border-gray-200">
					<h3 class="font-semibold text-gray-900 mb-2">Acceptez-vous les paiements par facture?</h3>
					<p class="text-gray-600">Pour les plans Production API, oui. Contactez notre équipe commerciale pour plus de détails.</p>
				</div>

				<div class="bg-white rounded-lg p-6 border border-gray-200">
					<h3 class="font-semibold text-gray-900 mb-2">Y a-t-il une période d'essai?</h3>
					<p class="text-gray-600">Oui, 14 jours gratuits pour tous les plans payants. Pas de carte bancaire requise.</p>
				</div>
			</div>
		</div>

		<!-- CTA Section -->
		<div class="mt-16 text-center">
			<p class="text-gray-600 mb-6">Des questions? Notre équipe est là pour vous aider</p>
			<Button href="mailto:support@lexikon.chessplorer.com" variant="primary">
				Nous contacter
			</Button>
		</div>
	</div>
</div>
