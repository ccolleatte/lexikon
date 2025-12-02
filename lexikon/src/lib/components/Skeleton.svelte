<script lang="ts">
	export let width: string = 'w-full';
	export let height: string = 'h-4';
	export let className: string = '';
	export let count: number = 1;
	export let circle: boolean = false;
</script>

{#each Array(count) as _}
	<div
		class="{width} {height} {circle ? 'rounded-full' : 'rounded'} bg-gradient-to-r from-gray-200 via-gray-100 to-gray-200 dark:from-gray-700 dark:via-gray-600 dark:to-gray-700 animate-pulse {className}"
	/>
{/each}

<style>
	:global(.animate-pulse) {
		animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
	}

	@keyframes pulse {
		0%,
		100% {
			opacity: 1;
		}
		50% {
			opacity: 0.5;
		}
	}
</style>
