<script lang="ts">
  /**
   * Button Component - Lexikon Design System
   *
   * @component
   * Versatile button with multiple variants, sizes, and states
   * Based on design tokens and accessibility best practices (WCAG AA)
   */

  import { createEventDispatcher } from 'svelte';

  // Props
  export let variant: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger' = 'primary';
  export let size: 'sm' | 'md' | 'lg' = 'md';
  export let disabled: boolean = false;
  export let loading: boolean = false;
  export let fullWidth: boolean = false;
  export let type: 'button' | 'submit' | 'reset' = 'button';
  export let href: string | undefined = undefined;
  export let className: string = '';

  const dispatch = createEventDispatcher();

  // Base classes
  const baseClasses = 'inline-flex items-center justify-center gap-2 font-medium rounded-md transition-all focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed';

  // Variant classes
  const variantClasses = {
    primary: 'bg-primary-600 text-white hover:bg-primary-700 active:bg-primary-800 shadow-sm',
    secondary: 'bg-gray-100 text-gray-900 hover:bg-gray-200 active:bg-gray-300 border border-gray-300',
    outline: 'bg-transparent text-primary-600 border border-primary-600 hover:bg-primary-50 active:bg-primary-100',
    ghost: 'bg-transparent text-gray-700 hover:bg-gray-100 active:bg-gray-200',
    danger: 'bg-error-500 text-white hover:bg-error-600 active:bg-error-700 shadow-sm'
  };

  // Size classes
  const sizeClasses = {
    sm: 'px-4 py-2 text-sm h-8',
    md: 'px-5 py-2.5 text-sm h-10',
    lg: 'px-6 py-3 text-base h-12'
  };

  // Compute final classes
  $: computedClasses = `
    ${baseClasses}
    ${variantClasses[variant]}
    ${sizeClasses[size]}
    ${fullWidth ? 'w-full' : ''}
    ${loading ? 'cursor-wait' : ''}
    ${className}
  `.trim().replace(/\s+/g, ' ');

  function handleClick(event: MouseEvent) {
    if (!disabled && !loading) {
      dispatch('click', event);
    }
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Enter') {
      handleClick(e as unknown as MouseEvent);
    }
  }
</script>

{#if href && !disabled}
  <a
    {href}
    class={computedClasses}
    role="button"
    tabindex="0"
    on:click={handleClick}
    on:keydown={handleKeydown}
  >
    {#if loading}
      <svg class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
    {/if}
    <slot />
  </a>
{:else}
  <button
    {type}
    {disabled}
    class={computedClasses}
    on:click={handleClick}
  >
    {#if loading}
      <svg class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <span>Loading...</span>
    {:else}
      <slot />
    {/if}
  </button>
{/if}

<style>
  /* Additional custom styles if needed */
  button, a[role="button"] {
    user-select: none;
  }
</style>
