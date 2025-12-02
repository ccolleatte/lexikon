<script lang="ts">
	import { isAuthenticated, user } from '$lib/stores/auth';
	import { logout } from '$lib/utils/auth';
	import Button from './Button.svelte';

	let showUserMenu = false;

	function toggleUserMenu() {
		showUserMenu = !showUserMenu;
	}

	function closeUserMenu() {
		showUserMenu = false;
	}

	async function handleLogout() {
		await logout();
		closeUserMenu();
	}

	// Close menu when clicking outside
	function handleClickOutside(event: MouseEvent) {
		const target = event.target as HTMLElement;
		if (!target.closest('.user-menu-container')) {
			closeUserMenu();
		}
	}
</script>

<svelte:window on:click={handleClickOutside} />

<nav class="bg-white shadow-sm border-b border-gray-200">
	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
		<div class="flex justify-between h-16">
			<!-- Logo and main nav -->
			<div class="flex">
				<a href="/" class="flex items-center">
					<span class="text-2xl font-serif font-bold text-primary-600">Lexikon</span>
				</a>

				{#if $isAuthenticated}
					<div class="hidden sm:ml-8 sm:flex sm:space-x-4">
						<a
							href="/terms"
							class="inline-flex items-center px-3 py-2 text-sm font-medium text-gray-900 hover:text-primary-600"
						>
							My Terms
						</a>
						<a
							href="/terms/new"
							class="inline-flex items-center px-3 py-2 text-sm font-medium text-gray-900 hover:text-primary-600"
						>
							Create Term
						</a>
					</div>
				{/if}
			</div>

			<!-- Right side -->
			<div class="flex items-center">
				{#if $isAuthenticated && $user}
					<!-- User menu -->
					<div class="relative user-menu-container">
						<button
							on:click|stopPropagation={toggleUserMenu}
							class="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-gray-100 transition-colors"
						>
							<div class="w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center text-white font-semibold">
								{$user.first_name[0]}{$user.last_name[0]}
							</div>
							<span class="hidden md:block text-sm font-medium text-gray-900">
								{$user.first_name}
							</span>
							<svg
								class="w-4 h-4 text-gray-500 transition-transform"
								class:rotate-180={showUserMenu}
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
							</svg>
						</button>

						{#if showUserMenu}
							<div
								class="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50"
							>
								<div class="px-4 py-3 border-b border-gray-200">
									<p class="text-sm font-medium text-gray-900">
										{$user.first_name} {$user.last_name}
									</p>
									<p class="text-xs text-gray-500 truncate">{$user.email}</p>
								</div>

								<a
									href="/profile"
									on:click={closeUserMenu}
									class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
								>
									<span class="inline-block w-5">👤</span>
									My Profile
								</a>

								<a
									href="/terms"
									on:click={closeUserMenu}
									class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
								>
									<span class="inline-block w-5">📚</span>
									My Terms
								</a>

								<div class="border-t border-gray-200 my-1"></div>

								<button
									on:click={handleLogout}
									class="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-gray-100"
								>
									<span class="inline-block w-5">🚪</span>
									Sign out
								</button>
							</div>
						{/if}
					</div>
				{:else}
					<!-- Guest buttons -->
					<div class="flex items-center gap-2">
						<Button href="/login" variant="ghost" size="sm">
							Sign in
						</Button>
						<Button href="/register" variant="primary" size="sm">
							Get started
						</Button>
					</div>
				{/if}
			</div>
		</div>
	</div>
</nav>

<style>
	.rotate-180 {
		transform: rotate(180deg);
	}
</style>
