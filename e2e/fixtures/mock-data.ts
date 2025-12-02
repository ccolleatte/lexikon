/**
 * Mock data for E2E tests
 */

export const mockSearchResults = {
	success: true,
	data: {
		results: [
			{
				id: 'term-1',
				name: 'Neural Network',
				definition: 'A computing system inspired by biological neural networks',
				domain: 'Computer Science',
				level: 'expert'
			},
			{
				id: 'term-2',
				name: 'Machine Learning',
				definition: 'Subset of artificial intelligence',
				domain: 'Computer Science',
				level: 'ready'
			}
		],
		total: 2,
		page: 1
	}
};

export const mockRelations = {
	success: true,
	data: [
		{
			id: 'rel-1',
			type: 'broader',
			target_term: {
				id: 'term-3',
				name: 'Artificial Intelligence'
			}
		},
		{
			id: 'rel-2',
			type: 'narrower',
			target_term: {
				id: 'term-4',
				name: 'Deep Learning'
			}
		}
	]
};

export const mockInferredRelations = {
	success: true,
	data: [
		{
			type: 'broader',
			target_term: {
				id: 'term-5',
				name: 'Technology'
			},
			reasoning: 'Inferred from transitive broader chain'
		}
	]
};

export const mockAnalyticsSummary = {
	success: true,
	data: {
		total_terms: 127,
		total_relations: 243,
		growth_7d: 8.5,
		growth_30d: 23.2
	}
};

export const mockTermsByDomain = {
	success: true,
	data: [
		{ domain: 'Computer Science', count: 45 },
		{ domain: 'Medicine', count: 32 },
		{ domain: 'Engineering', count: 28 },
		{ domain: 'Philosophy', count: 22 }
	]
};

export const mockGrowthData = {
	success: true,
	data: [
		{ date: '2025-11-01', count: 100 },
		{ date: '2025-11-08', count: 108 },
		{ date: '2025-11-15', count: 115 },
		{ date: '2025-11-22', count: 119 },
		{ date: '2025-12-01', count: 127 }
	]
};

export const mockTopTerms = {
	success: true,
	data: [
		{ id: 'term-1', name: 'Neural Network', views: 245, edits: 12 },
		{ id: 'term-2', name: 'Machine Learning', views: 198, edits: 8 },
		{ id: 'term-3', name: 'Artificial Intelligence', views: 187, edits: 15 },
		{ id: 'term-4', name: 'Deep Learning', views: 156, edits: 7 },
		{ id: 'term-5', name: 'Data Science', views: 143, edits: 5 }
	]
};

export const mockEmptyResults = {
	success: true,
	data: {
		results: [],
		total: 0,
		page: 1
	}
};

export const mockApiError = {
	success: false,
	error: {
		message: 'An error occurred',
		code: 'ERROR_500'
	}
};
