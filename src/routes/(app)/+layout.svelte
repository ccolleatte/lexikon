<script lang="ts">
	import NavBar from '$lib/components/NavBar.svelte';
</script>

<div class="min-h-screen bg-gray-50">
	<NavBar />
	<main>
		<slot />
	</main>
</div>
