<script lang="ts">
	import Skeleton from './Skeleton.svelte';

	export let count: number = 6;
</script>

<div class="space-y-4">
	{#each Array(count) as _}
		<div class="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800 p-4">
			<!-- Title skeleton -->
			<Skeleton width="w-3/4" height="h-5" className="mb-3" />

			<!-- Description skeleton -->
			<div class="space-y-2 mb-4">
				<Skeleton width="w-full" height="h-3" />
				<Skeleton width="w-4/5" height="h-3" />
			</div>

			<!-- Tags skeleton -->
			<div class="flex gap-2">
				<Skeleton width="w-24" height="h-6" className="rounded-full" />
				<Skeleton width="w-20" height="h-6" className="rounded-full" />
			</div>
		</div>
	{/each}
</div>
