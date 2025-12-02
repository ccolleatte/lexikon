<script lang="ts">
	import Toast from './Toast.svelte';
	import { notifications } from '$lib/stores/notifications';
</script>

<div class="fixed top-4 right-4 max-w-md space-y-2 z-50 pointer-events-none">
	{#each $notifications as toast (toast.id)}
		<div class="pointer-events-auto">
			<Toast id={toast.id} type={toast.type} message={toast.message} />
		</div>
	{/each}
</div>
