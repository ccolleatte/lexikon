<script lang="ts">
  /**
   * Alert Component - Lexikon Design System
   *
   * @component
   * Alert/Banner component for displaying important messages
   * Supports multiple variants with icons and optional close button
   * Based on design tokens and accessibility best practices (WCAG AA)
   */

  import { createEventDispatcher } from 'svelte';

  // Props
  export let variant: 'info' | 'success' | 'warning' | 'error' = 'info';
  export let title: string = '';
  export let closable: boolean = false;
  export let icon: boolean = true;
  export let className: string = '';

  const dispatch = createEventDispatcher();

  // State
  let visible = true;

  // Icons for each variant
  const icons = {
    info: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <circle cx="12" cy="12" r="10"/>
      <path d="M12 16v-4M12 8h.01"/>
    </svg>`,
    success: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
      <polyline points="22 4 12 14.01 9 11.01"/>
    </svg>`,
    warning: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
      <line x1="12" y1="9" x2="12" y2="13"/>
      <line x1="12" y1="17" x2="12.01" y2="17"/>
    </svg>`,
    error: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <circle cx="12" cy="12" r="10"/>
      <line x1="15" y1="9" x2="9" y2="15"/>
      <line x1="9" y1="9" x2="15" y2="15"/>
    </svg>`
  };

  function handleClose() {
    visible = false;
    dispatch('close');
  }
</script>

{#if visible}
  <div
    class="alert variant-{variant} {className}"
    role="alert"
    aria-live={variant === 'error' ? 'assertive' : 'polite'}
  >
    {#if icon}
      <div class="alert-icon">
        {@html icons[variant]}
      </div>
    {/if}

    <div class="alert-content">
      {#if title}
        <div class="alert-title">{title}</div>
      {/if}
      <div class="alert-message">
        <slot />
      </div>
    </div>

    {#if closable}
      <button
        type="button"
        class="alert-close"
        on:click={handleClose}
        aria-label="Fermer l'alerte"
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="18" y1="6" x2="6" y2="18"/>
          <line x1="6" y1="6" x2="18" y2="18"/>
        </svg>
      </button>
    {/if}
  </div>
{/if}

<style>
  .alert {
    display: flex;
    gap: 0.75rem;
    padding: 1rem;
    border-radius: var(--radius-lg, 0.5rem);
    border: 1px solid;
    position: relative;
    animation: alert-slide-in 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  }

  @keyframes alert-slide-in {
    from {
      opacity: 0;
      transform: translateY(-8px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  /* Info variant */
  .alert.variant-info {
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(37, 99, 235, 0.05) 100%);
    border-color: rgba(59, 130, 246, 0.2);
    color: var(--color-gray-900, #111827);
  }

  .alert.variant-info .alert-icon {
    color: var(--color-primary-600, #2563eb);
  }

  /* Success variant */
  .alert.variant-success {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.05) 100%);
    border-color: rgba(16, 185, 129, 0.2);
    color: var(--color-gray-900, #111827);
  }

  .alert.variant-success .alert-icon {
    color: #059669;
  }

  /* Warning variant */
  .alert.variant-warning {
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(217, 119, 6, 0.05) 100%);
    border-color: rgba(245, 158, 11, 0.2);
    color: var(--color-gray-900, #111827);
  }

  .alert.variant-warning .alert-icon {
    color: #d97706;
  }

  /* Error variant */
  .alert.variant-error {
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(220, 38, 38, 0.05) 100%);
    border-color: rgba(239, 68, 68, 0.2);
    color: var(--color-gray-900, #111827);
  }

  .alert.variant-error .alert-icon {
    color: #dc2626;
  }

  /* Icon */
  .alert-icon {
    flex-shrink: 0;
    margin-top: 2px;
  }

  /* Content */
  .alert-content {
    flex: 1;
    min-width: 0;
  }

  .alert-title {
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--color-gray-900, #111827);
    margin-bottom: 0.25rem;
  }

  .alert-message {
    font-size: 0.875rem;
    color: var(--color-gray-700, #374151);
    line-height: 1.5;
  }

  /* Close button */
  .alert-close {
    flex-shrink: 0;
    width: 28px;
    height: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: transparent;
    border: none;
    border-radius: var(--radius-md, 0.375rem);
    color: var(--color-gray-500, #6b7280);
    cursor: pointer;
    transition: all 0.2s;
    margin-top: -4px;
    margin-right: -4px;
  }

  .alert-close:hover {
    background: rgba(0, 0, 0, 0.05);
    color: var(--color-gray-700, #374151);
  }

  .alert-close:focus {
    outline: none;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.3);
  }

  .alert-close:active {
    transform: scale(0.95);
  }

  /* Responsive */
  @media (max-width: 640px) {
    .alert {
      padding: 0.875rem;
    }

    .alert-title {
      font-size: 0.8125rem;
    }

    .alert-message {
      font-size: 0.8125rem;
    }
  }
</style>
