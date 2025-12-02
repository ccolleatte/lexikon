<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import { isAuthenticated, user } from '$lib/stores/auth';
	import { logout } from '$lib/utils/auth';
	import { t } from 'svelte-i18n';

	const dispatch = createEventDispatcher();

	async function handleLogout() {
		await logout();
		dispatch('close');
	}

	function handleLinkClick() {
		dispatch('close');
	}
</script>

<!-- Overlay -->
<div
	class="fixed inset-0 bg-black bg-opacity-50 z-40 transition-opacity"
	on:click={() => dispatch('close')}
	on:keydown={(e) => e.key === 'Escape' && dispatch('close')}
	role="button"
	tabindex="0"
/>

<!-- Menu -->
<div
	class="fixed left-0 top-16 bottom-0 w-64 bg-white shadow-lg z-50 overflow-y-auto transition-transform transform animate-slide-in"
>
	{#if $isAuthenticated && $user}
		<!-- User info -->
		<div class="border-b border-gray-200 px-4 py-4">
			<div class="flex items-center gap-3 mb-3">
				<div class="w-10 h-10 bg-primary-600 rounded-full flex items-center justify-center text-white font-semibold">
					{$user.first_name[0]}{$user.last_name[0]}
				</div>
				<div>
					<p class="text-sm font-medium text-gray-900">
						{$user.first_name} {$user.last_name}
					</p>
					<p class="text-xs text-gray-500 truncate">{$user.email}</p>
				</div>
			</div>
		</div>

		<!-- Navigation -->
		<nav class="px-2 py-4 space-y-1">
			<a
				href="/terms"
				on:click={handleLinkClick}
				class="block px-4 py-2 text-sm font-medium text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
			>
				<span class="inline-block mr-2">📚</span>
				{$t('nav.myTerms')}
			</a>

			<a
				href="/terms/new"
				on:click={handleLinkClick}
				class="block px-4 py-2 text-sm font-medium text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
			>
				<span class="inline-block mr-2">➕</span>
				{$t('nav.createTerm')}
			</a>

			<a
				href="/projects"
				on:click={handleLinkClick}
				class="block px-4 py-2 text-sm font-medium text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
			>
				<span class="inline-block mr-2">📁</span>
				{$t('nav.projects')}
			</a>
		</nav>

		<!-- User menu -->
		<div class="border-t border-gray-200 px-2 py-4 space-y-1">
			<a
				href="/profile"
				on:click={handleLinkClick}
				class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
			>
				<span class="inline-block mr-2">👤</span>
				{$t('nav.myProfile')}
			</a>

			<button
				on:click={handleLogout}
				class="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-gray-100 rounded-lg transition-colors"
			>
				<span class="inline-block mr-2">🚪</span>
				{$t('nav.signOut')}
			</button>
		</div>
	{/if}
</div>

<style>
	@keyframes slideIn {
		from {
			transform: translateX(-100%);
		}
		to {
			transform: translateX(0);
		}
	}

	.animate-slide-in {
		animation: slideIn 0.3s ease-out;
	}
</style>
