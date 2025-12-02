<script lang="ts">
	import { goto } from '$app/navigation';
	import { t } from 'svelte-i18n';

	export let results: Array<{
		id: string;
		name: string;
		definition?: string;
		domain?: string;
		level?: string;
		score?: number;
	}> = [];
	export let loading = false;
	export let hasSearched = false;
	export let query = '';

	const levelColors = {
		basic: 'bg-blue-100 text-blue-900',
		intermediate: 'bg-yellow-100 text-yellow-900',
		advanced: 'bg-red-100 text-red-900',
	};

	function handleResultClick(id: string) {
		goto(`/terms/${id}`);
	}

	function getScorePercentage(score?: number): string {
		if (!score) return '';
		return `${Math.round(score * 100)}%`;
	}
</script>

<div class="space-y-4">
	{#if loading}
		<div class="text-center py-12">
			<div class="inline-block">
				<div class="w-8 h-8 border-4 border-gray-300 border-t-primary-600 rounded-full animate-spin" />
			</div>
			<p class="text-gray-500 mt-4">{$t('common.loading')}</p>
		</div>
	{:else if !hasSearched}
		<div class="text-center py-12">
			<svg class="w-16 h-16 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
			</svg>
			<p class="text-gray-500">{$t('search.startTyping')}</p>
		</div>
	{:else if results.length === 0}
		<div class="text-center py-12">
			<svg class="w-16 h-16 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
			</svg>
			<p class="text-gray-500">{$t('search.noResults')}</p>
		</div>
	{:else}
		<div class="space-y-3">
			{#each results as result (result.id)}
				<button
					on:click={() => handleResultClick(result.id)}
					class="w-full text-left p-4 bg-white border border-gray-200 rounded-lg hover:shadow-md transition-all hover:border-primary-400"
				>
					<div class="flex items-start justify-between gap-4">
						<div class="flex-grow min-w-0">
							<h3 class="text-lg font-semibold text-gray-900 truncate">{result.name}</h3>
							{#if result.definition}
								<p class="text-sm text-gray-600 line-clamp-2 mt-1">{result.definition}</p>
							{/if}
							<div class="flex gap-2 mt-2 flex-wrap">
								{#if result.domain}
									<span class="inline-block px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">
										{result.domain}
									</span>
								{/if}
								{#if result.level}
									<span
										class="inline-block px-2 py-1 text-xs rounded {levelColors[result.level] || 'bg-gray-100 text-gray-700'}"
									>
										{result.level}
									</span>
								{/if}
							</div>
						</div>
						{#if result.score}
							<div class="flex-shrink-0 text-right">
								<div class="text-sm font-medium text-primary-600">{getScorePercentage(result.score)}</div>
								<div class="text-xs text-gray-500">match</div>
							</div>
						{/if}
					</div>
				</button>
			{/each}
		</div>
	{/if}
</div>

<style>
	:global(.line-clamp-2) {
		display: -webkit-box;
		-webkit-line-clamp: 2;
		-webkit-box-orient: vertical;
		overflow: hidden;
	}

	:global(.animate-spin) {
		animation: spin 1s linear infinite;
	}

	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}
</style>
