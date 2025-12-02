<script lang="ts">
	import { onMount } from 'svelte';
	import { createEventDispatcher } from 'svelte';

	const dispatch = createEventDispatcher();

	export let placeholder = 'Rechercher...';
	export let debounceMs = 300;

	let query = '';
	let debounceTimer: NodeJS.Timeout;
	let isFocused = false;

	function handleInput(e: Event) {
		const value = (e.target as HTMLInputElement).value;
		query = value;

		clearTimeout(debounceTimer);
		debounceTimer = setTimeout(() => {
			dispatch('search', value);
		}, debounceMs);
	}

	function handleFocus() {
		isFocused = true;
	}

	function handleBlur() {
		isFocused = false;
	}

	function handleClear() {
		query = '';
		dispatch('search', '');
	}

	onMount(() => {
		return () => clearTimeout(debounceTimer);
	});
</script>

<div class="relative">
	<div class="flex items-center bg-white border border-gray-300 rounded-lg px-4 py-2 focus-within:border-primary-600 focus-within:ring-1 focus-within:ring-primary-600 transition-all">
		<svg class="w-5 h-5 text-gray-400 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
			<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
		</svg>

		<input
			type="text"
			{placeholder}
			value={query}
			on:input={handleInput}
			on:focus={handleFocus}
			on:blur={handleBlur}
			class="flex-grow bg-transparent outline-none text-gray-900 placeholder-gray-500"
			aria-label={placeholder}
		/>

		{#if query}
			<button
				on:click={handleClear}
				class="ml-2 text-gray-400 hover:text-gray-600 transition-colors flex-shrink-0"
				aria-label="Clear search"
			>
				<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
				</svg>
			</button>
		{/if}
	</div>
</div>

<style>
	:global([role="searchbox"]:focus) {
		outline: none;
	}
</style>
