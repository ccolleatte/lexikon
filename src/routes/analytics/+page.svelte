<script lang="ts">
	import { onMount } from 'svelte';
	import { t } from 'svelte-i18n';
	import TermsByDomain from '$lib/components/charts/TermsByDomain.svelte';
	import GrowthChart from '$lib/components/charts/GrowthChart.svelte';
	import StatCard from '$lib/components/charts/StatCard.svelte';

	let loading = true;
	let error: string | null = null;
	let stats = {
		totalTerms: 0,
		totalRelations: 0,
		avgTermsPerDomain: 0,
		monthlyGrowth: 0,
	};
	let domainStats: Array<{ domain: string; count: number }> = [];
	let growthData: Array<{ date: string; count: number }> = [];

	onMount(async () => {
		await loadAnalytics();
	});

	async function loadAnalytics() {
		try {
			loading = true;
			error = null;

			// Load stats
			const [domainRes, growthRes] = await Promise.all([
				fetch('/api/analytics/terms-by-domain'),
				fetch('/api/analytics/terms-growth'),
			]);

			if (!domainRes.ok || !growthRes.ok) {
				throw new Error('Erreur lors du chargement des données');
			}

			const domainData = await domainRes.json();
			const growthDataRes = await growthRes.json();

			domainStats = domainData;
			growthData = growthDataRes;

			// Calculate stats
			const totalTerms = domainData.reduce((sum: number, d: any) => sum + d.count, 0);
			stats.totalTerms = totalTerms;
			stats.avgTermsPerDomain = domainData.length > 0 ? Math.round(totalTerms / domainData.length) : 0;

			// Calculate monthly growth
			if (growthDataRes.length >= 2) {
				const current = growthDataRes[growthDataRes.length - 1].count;
				const previous = growthDataRes[growthDataRes.length - 2].count;
				stats.monthlyGrowth = current - previous;
			}
		} catch (err) {
			error = err instanceof Error ? err.message : 'Erreur lors du chargement des données';
		} finally {
			loading = false;
		}
	}
</script>

<svelte:head>
	<title>Analyse - Lexikon</title>
</svelte:head>

<main class="min-h-screen bg-gray-50">
	<div class="max-w-6xl mx-auto px-4 py-12">
		<!-- Header -->
		<div class="mb-12">
			<h1 class="text-4xl font-bold text-gray-900 mb-2">Analyse</h1>
			<p class="text-lg text-gray-600">Visualisez les statistiques de votre vocabulaire</p>
		</div>

		{#if loading}
			<div class="text-center py-12">
				<div class="inline-block">
					<div class="w-8 h-8 border-4 border-gray-300 border-t-primary-600 rounded-full animate-spin" />
				</div>
				<p class="text-gray-600 mt-4">Chargement des données...</p>
			</div>
		{:else if error}
			<div class="bg-red-50 border border-red-200 rounded-lg p-6">
				<p class="text-red-800 font-medium">{error}</p>
			</div>
		{:else}
			<!-- Stats Grid -->
			<div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
				<StatCard
					title="Nombre de termes"
					value={stats.totalTerms}
					icon="📚"
					color="blue"
				/>
				<StatCard
					title="Moyenne par domaine"
					value={stats.avgTermsPerDomain}
					icon="📊"
					color="green"
				/>
				<StatCard
					title="Croissance (ce mois)"
					value={stats.monthlyGrowth}
					icon="📈"
					color="purple"
					suffix={stats.monthlyGrowth > 0 ? '+' : ''}
				/>
				<StatCard
					title="Domaines"
					value={domainStats.length}
					icon="🏷️"
					color="orange"
				/>
			</div>

			<!-- Charts Grid -->
			<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
				<!-- Growth Chart -->
				<div class="bg-white rounded-lg border border-gray-200 p-6">
					<h2 class="text-lg font-semibold text-gray-900 mb-4">Croissance des termes</h2>
					<GrowthChart data={growthData} />
				</div>

				<!-- Terms by Domain -->
				<div class="bg-white rounded-lg border border-gray-200 p-6">
					<h2 class="text-lg font-semibold text-gray-900 mb-4">Termes par domaine</h2>
					<TermsByDomain data={domainStats} />
				</div>
			</div>

			<!-- Details Section -->
			<div class="mt-12 grid grid-cols-1 md:grid-cols-2 gap-6">
				<!-- Domains Breakdown -->
				<div class="bg-white rounded-lg border border-gray-200 p-6">
					<h3 class="text-lg font-semibold text-gray-900 mb-4">Répartition par domaine</h3>
					<div class="space-y-2">
						{#each domainStats as domain}
							<div class="flex items-center justify-between">
								<span class="text-sm font-medium text-gray-700">{domain.domain}</span>
								<div class="flex items-center gap-2">
									<div class="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
										<div
											class="h-full bg-primary-600 rounded-full"
											style="width: {(domain.count / stats.totalTerms) * 100}%"
										/>
									</div>
									<span class="text-sm font-medium text-gray-900 w-12 text-right">{domain.count}</span>
								</div>
							</div>
						{/each}
					</div>
				</div>

				<!-- Quick Stats -->
				<div class="bg-white rounded-lg border border-gray-200 p-6">
					<h3 class="text-lg font-semibold text-gray-900 mb-4">Informations</h3>
					<div class="space-y-4">
						<div>
							<p class="text-sm text-gray-600">Termes actifs</p>
							<p class="text-2xl font-bold text-gray-900">{stats.totalTerms}</p>
						</div>
						<div>
							<p class="text-sm text-gray-600">Domaines couverts</p>
							<p class="text-2xl font-bold text-gray-900">{domainStats.length}</p>
						</div>
						<div>
							<p class="text-sm text-gray-600">Croissance mensuelle</p>
							<p class="text-2xl font-bold {stats.monthlyGrowth > 0 ? 'text-green-600' : 'text-gray-900'}">
								{stats.monthlyGrowth > 0 ? '+' : ''}{stats.monthlyGrowth}
							</p>
						</div>
					</div>
				</div>
			</div>
		{/if}
	</div>
</main>

<style>
	:global(.animate-spin) {
		animation: spin 1s linear infinite;
	}

	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}
</style>
