import { writable } from 'svelte/store';
import type { OnboardingData, AdoptionLevel } from '$types';

const STORAGE_KEY = 'lexikon-onboarding';

// Initialize from localStorage if available
function createOnboardingStore() {
	const initialData: OnboardingData = {
		adoptionLevel: undefined,
		profile: undefined,
		sessionId: crypto.randomUUID()
	};

	// Try to load from localStorage
	if (typeof window !== 'undefined') {
		const stored = localStorage.getItem(STORAGE_KEY);
		if (stored) {
			try {
				const parsed = JSON.parse(stored);
				Object.assign(initialData, parsed);
			} catch (e) {
				console.error('Failed to parse onboarding data:', e);
			}
		}
	}

	const { subscribe, set, update } = writable<OnboardingData>(initialData);

	return {
		subscribe,
		setAdoptionLevel: (level: AdoptionLevel) => {
			update((data) => {
				const updated = { ...data, adoptionLevel: level };
				if (typeof window !== 'undefined') {
					localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
				}
				return updated;
			});
		},
		setProfile: (profile: OnboardingData['profile']) => {
			update((data) => {
				const updated = { ...data, profile };
				if (typeof window !== 'undefined') {
					localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
				}
				return updated;
			});
		},
		clear: () => {
			if (typeof window !== 'undefined') {
				localStorage.removeItem(STORAGE_KEY);
			}
			set({
				adoptionLevel: undefined,
				profile: undefined,
				sessionId: crypto.randomUUID()
			});
		},
		reset: () => set(initialData)
	};
}

export const onboarding = createOnboardingStore();
