<script lang="ts">
	import SearchBar from '$lib/components/SearchBar.svelte';
	import SearchResults from '$lib/components/SearchResults.svelte';
	import { t } from 'svelte-i18n';
	import { onMount } from 'svelte';
	import type { PageData } from './$types';

	export let data: PageData;

	let query = '';
	let loading = false;
	let results: any[] = [];
	let hasSearched = false;
	let domainFilter = '';
	let levelFilter = '';

	const domains = ['all', 'mathematics', 'physics', 'biology', 'chemistry', 'computer-science'];
	const levels = ['all', 'basic', 'intermediate', 'advanced'];

	async function handleSearch(event: CustomEvent<string>) {
		query = event.detail;
		hasSearched = query.length > 0;

		if (!query.trim()) {
			results = [];
			return;
		}

		loading = true;
		try {
			const params = new URLSearchParams();
			params.set('q', query);
			if (domainFilter && domainFilter !== 'all') {
				params.set('domain', domainFilter);
			}
			if (levelFilter && levelFilter !== 'all') {
				params.set('level', levelFilter);
			}
			params.set('limit', '10');

			const response = await fetch(`/api/terms/search?${params.toString()}`);
			if (response.ok) {
				results = await response.json();
			} else {
				results = [];
			}
		} catch (error) {
			console.error('Search failed:', error);
			results = [];
		} finally {
			loading = false;
		}
	}

	function handleFilterChange() {
		if (query) {
			hasSearched = false;
			handleSearch(new CustomEvent('search', { detail: query }));
		}
	}

	onMount(() => {
		const urlParams = new URLSearchParams(window.location.search);
		query = urlParams.get('q') || '';
		if (query) {
			setTimeout(() => {
				const event = new CustomEvent('search', { detail: query });
				handleSearch(event);
			}, 0);
		}
	});
</script>

<svelte:head>
	<title>{$t('search.title')} - Lexikon</title>
</svelte:head>

<main class="min-h-screen bg-gray-50">
	<div class="max-w-4xl mx-auto px-4 py-8">
		<!-- Header -->
		<div class="mb-8">
			<h1 class="text-3xl font-bold text-gray-900 mb-2">{$t('search.title')}</h1>
			<p class="text-gray-600">{$t('search.subtitle')}</p>
		</div>

		<!-- Search Bar -->
		<div class="mb-8">
			<SearchBar
				placeholder={$t('search.placeholder')}
				on:search={handleSearch}
			/>
		</div>

		<!-- Filters -->
		{#if hasSearched || query}
			<div class="mb-6 p-4 bg-white rounded-lg border border-gray-200 space-y-4">
				<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
					<div>
						<label class="block text-sm font-medium text-gray-700 mb-2">
							{$t('search.filters.domain')}
						</label>
						<select
							bind:value={domainFilter}
							on:change={handleFilterChange}
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-primary-600 focus:border-primary-600"
						>
							{#each domains as domain}
								<option value={domain}>
									{domain === 'all' ? $t('common.all') : domain}
								</option>
							{/each}
						</select>
					</div>

					<div>
						<label class="block text-sm font-medium text-gray-700 mb-2">
							{$t('search.filters.level')}
						</label>
						<select
							bind:value={levelFilter}
							on:change={handleFilterChange}
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-primary-600 focus:border-primary-600"
						>
							{#each levels as level}
								<option value={level}>
									{level === 'all' ? $t('common.all') : level}
								</option>
							{/each}
						</select>
					</div>
				</div>
			</div>
		{/if}

		<!-- Results -->
		<SearchResults {results} {loading} {hasSearched} {query} />
	</div>
</main>
