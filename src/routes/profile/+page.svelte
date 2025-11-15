<script lang="ts">
	import { user } from '$lib/stores/auth';
	import { logout, changePassword } from '$lib/utils/auth';
	import { ApiError } from '$lib/utils/api';
	import Button from '$lib/components/Button.svelte';
	import Input from '$lib/components/Input.svelte';
	import Alert from '$lib/components/Alert.svelte';

	let showChangePassword = false;
	let currentPassword = '';
	let newPassword = '';
	let confirmNewPassword = '';
	let isLoading = false;
	let error: string | null = null;
	let success: string | null = null;
	let passwordMismatch = false;

	$: passwordMismatch = newPassword !== confirmNewPassword && confirmNewPassword.length > 0;

	async function handleChangePassword() {
		error = null;
		success = null;

		if (newPassword !== confirmNewPassword) {
			error = 'Passwords do not match';
			return;
		}

		if (newPassword.length < 8) {
			error = 'Password must be at least 8 characters long';
			return;
		}

		isLoading = true;

		try {
			await changePassword(currentPassword, newPassword);
			success = 'Password changed successfully';
			showChangePassword = false;
			currentPassword = '';
			newPassword = '';
			confirmNewPassword = '';
		} catch (e) {
			if (e instanceof ApiError) {
				error = e.message;
			} else {
				error = 'Failed to change password. Please try again.';
			}
		} finally {
			isLoading = false;
		}
	}

	async function handleLogout() {
		await logout();
	}

	function formatDate(dateString: string): string {
		return new Date(dateString).toLocaleDateString('en-US', {
			year: 'numeric',
			month: 'long',
			day: 'numeric'
		});
	}

	function getAdoptionLevelLabel(level: string): string {
		const labels = {
			'quick-project': 'Quick Project',
			'research-project': 'Research Project',
			'production-api': 'Production API'
		};
		return labels[level as keyof typeof labels] || level;
	}
</script>

<svelte:head>
	<title>My Profile - Lexikon</title>
</svelte:head>

<div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
	<div class="space-y-6">
		<!-- Header -->
		<div class="flex items-center justify-between">
			<div>
				<h1 class="text-3xl font-bold text-gray-900">My Profile</h1>
				<p class="mt-1 text-sm text-gray-600">
					Manage your account settings and preferences
				</p>
			</div>
			<Button variant="outline" on:click={handleLogout}>
				Sign out
			</Button>
		</div>

		<!-- Success/Error Messages -->
		{#if success}
			<Alert type="success">
				{success}
			</Alert>
		{/if}

		{#if error && !showChangePassword}
			<Alert type="error">
				{error}
			</Alert>
		{/if}

		<!-- User Information -->
		{#if $user}
			<div class="bg-white shadow rounded-lg divide-y divide-gray-200">
				<!-- Personal Information -->
				<div class="p-6">
					<h2 class="text-lg font-medium text-gray-900 mb-4">Personal Information</h2>
					<dl class="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
						<div>
							<dt class="text-sm font-medium text-gray-500">Full name</dt>
							<dd class="mt-1 text-sm text-gray-900">
								{$user.first_name} {$user.last_name}
							</dd>
						</div>

						<div>
							<dt class="text-sm font-medium text-gray-500">Email</dt>
							<dd class="mt-1 text-sm text-gray-900">{$user.email}</dd>
						</div>

						{#if $user.institution}
							<div>
								<dt class="text-sm font-medium text-gray-500">Institution</dt>
								<dd class="mt-1 text-sm text-gray-900">{$user.institution}</dd>
							</div>
						{/if}

						{#if $user.primary_domain}
							<div>
								<dt class="text-sm font-medium text-gray-500">Primary domain</dt>
								<dd class="mt-1 text-sm text-gray-900">{$user.primary_domain}</dd>
							</div>
						{/if}

						<div>
							<dt class="text-sm font-medium text-gray-500">Language</dt>
							<dd class="mt-1 text-sm text-gray-900">{$user.language.toUpperCase()}</dd>
						</div>

						{#if $user.country}
							<div>
								<dt class="text-sm font-medium text-gray-500">Country</dt>
								<dd class="mt-1 text-sm text-gray-900">{$user.country}</dd>
							</div>
						{/if}

						<div>
							<dt class="text-sm font-medium text-gray-500">Member since</dt>
							<dd class="mt-1 text-sm text-gray-900">{formatDate($user.created_at)}</dd>
						</div>

						<div>
							<dt class="text-sm font-medium text-gray-500">Account status</dt>
							<dd class="mt-1">
								<span class={`inline-flex px-2 text-xs font-semibold rounded-full ${
									$user.is_active
										? 'bg-green-100 text-green-800'
										: 'bg-red-100 text-red-800'
								}`}>
									{$user.is_active ? 'Active' : 'Inactive'}
								</span>
							</dd>
						</div>
					</dl>
				</div>

				<!-- Adoption Level -->
				<div class="p-6">
					<h2 class="text-lg font-medium text-gray-900 mb-4">Subscription</h2>
					<div class="flex items-center justify-between">
						<div>
							<p class="text-sm font-medium text-gray-500">Current plan</p>
							<p class="mt-1 text-lg font-semibold text-gray-900">
								{getAdoptionLevelLabel($user.adoption_level)}
							</p>
						</div>
						<Button variant="outline">
							Upgrade plan
						</Button>
					</div>
				</div>

				<!-- Security -->
				<div class="p-6">
					<h2 class="text-lg font-medium text-gray-900 mb-4">Security</h2>

					{#if !showChangePassword}
						<Button variant="outline" on:click={() => showChangePassword = true}>
							Change password
						</Button>
					{:else}
						<div class="space-y-4">
							{#if error}
								<Alert type="error">
									{error}
								</Alert>
							{/if}

							<Input
								label="Current password"
								type="password"
								bind:value={currentPassword}
								placeholder="••••••••"
								required
							/>

							<Input
								label="New password"
								type="password"
								bind:value={newPassword}
								placeholder="••••••••"
								required
								helperText="At least 8 characters"
							/>

							<Input
								label="Confirm new password"
								type="password"
								bind:value={confirmNewPassword}
								placeholder="••••••••"
								required
								error={passwordMismatch ? 'Passwords do not match' : undefined}
							/>

							<div class="flex gap-3">
								<Button
									variant="primary"
									on:click={handleChangePassword}
									{isLoading}
									disabled={passwordMismatch}
								>
									{isLoading ? 'Saving...' : 'Save new password'}
								</Button>
								<Button
									variant="outline"
									on:click={() => {
										showChangePassword = false;
										error = null;
										currentPassword = '';
										newPassword = '';
										confirmNewPassword = '';
									}}
									disabled={isLoading}
								>
									Cancel
								</Button>
							</div>
						</div>
					{/if}
				</div>
			</div>
		{/if}
	</div>
</div>
