import { defineConfig } from 'vitest/config';
import { svelte } from '@sveltejs/vite-plugin-svelte';
import path from 'path';

export default defineConfig({
	plugins: [svelte({ hot: !process.env.VITEST })],
	test: {
		globals: true,
		environment: 'jsdom',
		setupFiles: ['./src/test/setup.ts'],
		include: ['src/**/*.{test,spec}.{js,ts}'],
		coverage: {
			reporter: ['text', 'json', 'html'],
			exclude: [
				'node_modules/',
				'src/test/',
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
			$components: path.resolve('./src/lib/components')
		}
	}
});
