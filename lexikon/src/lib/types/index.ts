// User types
export type AdoptionLevel = 'quick-project' | 'research-project' | 'production-api';
export type PrimaryDomain =
	| 'philosophie'
	| 'sciences-education'
	| 'sociologie'
	| 'psychologie'
	| 'linguistique'
	| 'histoire'
	| 'informatique'
	| 'data-science'
	| 'autre';

export interface User {
	id: string;
	firstName: string;
	lastName: string;
	email: string;
	avatar?: string;
	institution?: string;
	primaryDomain?: PrimaryDomain;
	language: string;
	country?: string;
	adoptionLevel: AdoptionLevel;
	createdAt: string;
	updatedAt: string;
}

// Term types
export type TermLevel = 'quick-draft' | 'ready' | 'expert';
export type TermStatus = 'draft' | 'ready' | 'validated';

export interface Term {
	id: string;
	name: string;
	definition: string;
	domain?: string;
	level: TermLevel;
	status: TermStatus;
	createdBy: string;
	createdAt: string;
	updatedAt: string;
}

// Onboarding types
export interface OnboardingData {
	adoptionLevel?: AdoptionLevel;
	profile?: Partial<User>;
	sessionId?: string;
}

// API Response types
export interface ApiResponse<T> {
	success: boolean;
	data?: T;
	error?: {
		code: string;
		message: string;
		details?: Record<string, string[]>;
	};
	metadata?: {
		requestId: string;
		timestamp: string;
		version: string;
	};
}

export interface PaginatedResponse<T> {
	data: T[];
	pagination: {
		page: number;
		limit: number;
		total: number;
		totalPages: number;
		hasNext: boolean;
		hasPrev: boolean;
	};
}
