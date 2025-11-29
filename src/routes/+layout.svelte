<script lang="ts">
	import '../app.css';
	import NavBar from '$lib/components/NavBar.svelte';
	import { onMount } from 'svelte';
	import { waitLocale } from 'svelte-i18n';
	import '$lib/i18n';

	onMount(async () => {
		await waitLocale();
	});
</script>

<NavBar />
<slot />
