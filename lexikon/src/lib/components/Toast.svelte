<script lang="ts">
	import type { NotificationType } from '$lib/stores/notifications';
	import { notifications } from '$lib/stores/notifications';

	export let id: string;
	export let type: NotificationType = 'info';
	export let message: string;

	const icons = {
		success: '✓',
		error: '✕',
		warning: '⚠',
		info: 'ⓘ',
	};

	const colors = {
		success: 'bg-green-50 border-green-200 text-green-900',
		error: 'bg-red-50 border-red-200 text-red-900',
		warning: 'bg-yellow-50 border-yellow-200 text-yellow-900',
		info: 'bg-blue-50 border-blue-200 text-blue-900',
	};

	const iconColors = {
		success: 'text-green-600',
		error: 'text-red-600',
		warning: 'text-yellow-600',
		info: 'text-blue-600',
	};

	function handleClose() {
		notifications.remove(id);
	}
</script>

<div
	class="flex items-center gap-3 p-4 rounded-lg border {colors[type]} shadow-md animate-fade-in"
	role="alert"
>
	<span class="text-lg font-bold {iconColors[type]} flex-shrink-0">
		{icons[type]}
	</span>

	<span class="flex-grow text-sm font-medium">{message}</span>

	<button
		on:click={handleClose}
		class="flex-shrink-0 ml-2 text-lg font-bold opacity-70 hover:opacity-100 transition-opacity"
		aria-label="Close"
	>
		×
	</button>
</div>

<style>
	@keyframes fadeIn {
		from {
			opacity: 0;
			transform: translateY(-10px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	.animate-fade-in {
		animation: fadeIn 0.3s ease-out;
	}
</style>
