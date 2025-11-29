<script lang="ts">
	import '../app.css';
	import NavBar from '$lib/components/NavBar.svelte';
	import { onMount } from 'svelte';
	import { init, waitLocale } from 'svelte-i18n';
	import i18n from '$lib/i18n';

	onMount(async () => {
		await waitLocale();
	});
</script>

<NavBar />
<slot />
