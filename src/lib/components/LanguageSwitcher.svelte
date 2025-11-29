<script lang="ts">
	import { locale } from 'svelte-i18n';

	function toggleLanguage() {
		const newLocale = $locale === 'fr' ? 'en' : 'fr';
		locale.set(newLocale);
		localStorage.setItem('app-locale', newLocale);
	}

	onMount(() => {
		// Load saved language preference from localStorage
		const saved = localStorage.getItem('app-locale');
		if (saved && (saved === 'fr' || saved === 'en')) {
			locale.set(saved);
		}
	});

	import { onMount } from 'svelte';
</script>

<button on:click={toggleLanguage} class="language-switcher" title="Toggle language">
	{#if $locale === 'fr'}
		<span class="flag">🇫🇷</span>
		<span class="text">FR</span>
	{:else}
		<span class="flag">🇬🇧</span>
		<span class="text">EN</span>
	{/if}
</button>

<style>
	.language-switcher {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.5rem 1rem;
		border: 1px solid var(--color-border, #ddd);
		border-radius: 0.375rem;
		background: white;
		cursor: pointer;
		font-size: 0.875rem;
		font-weight: 500;
		color: var(--color-text, #333);
		transition: all 0.2s ease;
	}

	.language-switcher:hover {
		background: var(--color-gray-50, #f9fafb);
		border-color: var(--color-primary, #3b82f6);
	}

	.language-switcher:active {
		transform: scale(0.98);
	}

	.flag {
		font-size: 1.25rem;
	}

	.text {
		font-weight: 600;
	}

	@media (max-width: 640px) {
		.language-switcher {
			padding: 0.5rem;
		}

		.text {
			display: none;
		}
	}
</style>
