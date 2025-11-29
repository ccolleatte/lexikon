import { register, init, getLocaleFromNavigator } from 'svelte-i18n';

// Register locale loaders
register('fr', () => import('./locales/fr.json'));
register('en', () => import('./locales/en.json'));

// Initialize i18n
export default init({
  fallbackLocale: 'fr',
  initialLocale: getLocaleFromNavigator() || 'fr',
  formats: {
    number: {
      EUR: {
        style: 'currency',
        currency: 'EUR',
      },
    },
  },
});
