<script lang="ts">
	/**
	 * Lazy Load Component
	 * Suspends component rendering until visible (intersection observer)
	 */

	import { onMount } from 'svelte';

	let element: HTMLDivElement;
	let isVisible = false;
	let isLoaded = false;

	onMount(() => {
		if (!element || typeof window === 'undefined') return;

		// Use intersection observer for lazy loading
		const observer = new IntersectionObserver(
			(entries) => {
				entries.forEach((entry) => {
					if (entry.isIntersecting && !isLoaded) {
						isVisible = true;
						isLoaded = true;
						observer.disconnect();
					}
				});
			},
			{
				rootMargin: '50px' // Start loading 50px before visible
			}
		);

		observer.observe(element);

		return () => observer.disconnect();
	});
</script>

<div bind:this={element}>
	{#if isLoaded}
		<slot />
	{:else}
		<div class="bg-gray-100 animate-pulse rounded-lg h-96 flex items-center justify-center">
			<p class="text-gray-400">Chargement...</p>
		</div>
	{/if}
</div>
