import { writable } from 'svelte/store';
import { browser } from '$app/environment';

export type Theme = 'light' | 'dark';

function createThemeStore() {
	// Get initial theme from localStorage or system preference
	let initialTheme: Theme = 'light';

	if (browser) {
		const storedTheme = localStorage.getItem('theme') as Theme | null;

		if (storedTheme) {
			initialTheme = storedTheme;
		} else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
			initialTheme = 'dark';
		}

		// Apply initial theme
		applyTheme(initialTheme);
	}

	const { subscribe, set } = writable<Theme>(initialTheme);

	return {
		subscribe,
		setTheme: (theme: Theme) => {
			if (browser) {
				localStorage.setItem('theme', theme);
				applyTheme(theme);
			}
			set(theme);
		},
		toggleTheme: () => {
			if (browser) {
				const currentTheme = localStorage.getItem('theme') as Theme;
				const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
				localStorage.setItem('theme', newTheme);
				applyTheme(newTheme);
				set(newTheme);
			}
		},
	};
}

function applyTheme(theme: Theme) {
	if (!browser) return;

	const root = document.documentElement;

	if (theme === 'dark') {
		root.classList.add('dark');
		root.setAttribute('data-theme', 'dark');
	} else {
		root.classList.remove('dark');
		root.setAttribute('data-theme', 'light');
	}
}

export const theme = createThemeStore();
