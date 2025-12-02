import { writable } from 'svelte/store';

export type NotificationType = 'success' | 'error' | 'warning' | 'info';

export interface Toast {
	id: string;
	type: NotificationType;
	message: string;
	duration?: number;
}

function createNotificationStore() {
	const { subscribe, set, update } = writable<Toast[]>([]);
	let nextId = 0;

	return {
		subscribe,
		add: (toast: Omit<Toast, 'id'>) => {
			const id = `toast-${nextId++}`;
			const newToast: Toast = {
				...toast,
				id,
				duration: toast.duration ?? 5000,
			};

			update((toasts) => [...toasts, newToast]);

			// Auto-dismiss after duration
			if (newToast.duration && newToast.duration > 0) {
				setTimeout(() => {
					notifications.remove(id);
				}, newToast.duration);
			}

			return id;
		},
		remove: (id: string) => {
			update((toasts) => toasts.filter((t) => t.id !== id));
		},
		clear: () => {
			set([]);
		},
	};
}

export const notifications = createNotificationStore();

// Helper function for easier usage
export function addToast(type: NotificationType, message: string, duration?: number) {
	return notifications.add({ type, message, duration });
}
