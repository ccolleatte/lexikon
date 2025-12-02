import { defineConfig } from 'vitest/config';
import { svelte } from '@sveltejs/vite-plugin-svelte';
import path from 'path';

export default defineConfig({
	plugins: [
		svelte({
			hot: !process.env.VITEST,
			compilerOptions: {
				// Disable CSS generation in tests
				css: 'injected'
			}
		})
	],
	test: {
		globals: true,
		environment: 'jsdom',
		setupFiles: ['./src/test/setup.ts'],
		include: ['src/**/*.{test,spec}.{js,ts}'],
		// Exclude component tests and E2E tests
		exclude: [
			'**/node_modules/**',
			'**/dist/**',
			'**/.svelte-kit/**',
			'**/e2e/**',
			'src/routes/**/page.test.ts',
			'src/lib/components/**/*.test.ts'
		],
		coverage: {
			reporter: ['text', 'json', 'html'],
			include: [
				'src/lib/**/*.{js,ts}',
				'!src/lib/components/**',
				'!src/lib/**/*.test.{js,ts}',
				'!src/lib/**/*.spec.{js,ts}'
			],
			exclude: [
				'node_modules/',
				'src/test/',
				'src/routes/**',
				'src/hooks.client.ts',
				'*.config.{js,ts}',
				'**/*.d.ts',
				'**/*.config.{js,ts}',
				'**/mockData/**',
				'**/*.spec.{js,ts}',
				'**/*.test.{js,ts}'
			]
		}
	},
	resolve: {
		alias: {
			$lib: path.resolve('./src/lib'),
			$types: path.resolve('./src/lib/types'),
			$components: path.resolve('./src/lib/components'),
			'$app/environment': path.resolve('./src/test/mocks/app-environment.ts'),
			'$app/navigation': path.resolve('./src/test/mocks/app-navigation.ts')
		}
	}
});
