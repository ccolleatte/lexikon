/**
 * Adoption level utilities for feature gating
 */

export type AdoptionLevel = 'quick-project' | 'research-project' | 'production-api';

export interface FeatureAccess {
	webhooks: boolean;
	exportMultiFormat: boolean;
	collaboration: boolean;
	apiKeys: boolean;
	advancedRelations: boolean;
	versionHistory: boolean;
	highRateLimit: boolean;
	sla: boolean;
	support24_7: boolean;
}

/**
 * Get feature access based on adoption level
 */
export function getFeatureAccess(adoptionLevel: AdoptionLevel | null | undefined): FeatureAccess {
	const level = adoptionLevel || 'quick-project';

	return {
		webhooks: level === 'production-api',
		exportMultiFormat: level === 'research-project' || level === 'production-api',
		collaboration: level === 'research-project' || level === 'production-api',
		apiKeys: level === 'production-api',
		advancedRelations: level === 'research-project' || level === 'production-api',
		versionHistory: level === 'research-project' || level === 'production-api',
		highRateLimit: level === 'production-api',
		sla: level === 'production-api',
		support24_7: level === 'production-api'
	};
}

/**
 * Check if user has access to a specific feature
 */
export function hasFeatureAccess(adoptionLevel: AdoptionLevel | null | undefined, feature: keyof FeatureAccess): boolean {
	const access = getFeatureAccess(adoptionLevel);
	return access[feature];
}

/**
 * Check if adoption level is at least the specified level
 */
export function hasAdoptionLevel(currentLevel: AdoptionLevel | null | undefined, requiredLevel: AdoptionLevel): boolean {
	const levels: AdoptionLevel[] = ['quick-project', 'research-project', 'production-api'];
	const currentIndex = levels.indexOf(currentLevel as AdoptionLevel) || 0;
	const requiredIndex = levels.indexOf(requiredLevel);
	return currentIndex >= requiredIndex;
}

/**
 * Get level name for display
 */
export function getLevelName(level: AdoptionLevel | null | undefined): string {
	switch (level) {
		case 'quick-project':
			return 'Quick Project';
		case 'research-project':
			return 'Research Project';
		case 'production-api':
			return 'Production API';
		default:
			return 'Quick Project';
	}
}

/**
 * Get level description for display
 */
export function getLevelDescription(level: AdoptionLevel | null | undefined): string {
	switch (level) {
		case 'quick-project':
			return 'Parfait pour découvrir';
		case 'research-project':
			return 'Pour les projets de recherche';
		case 'production-api':
			return 'Pour les intégrations professionnelles';
		default:
			return 'Parfait pour découvrir';
	}
}
