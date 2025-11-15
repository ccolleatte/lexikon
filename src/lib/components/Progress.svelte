<script lang="ts">
  /**
   * Progress Component - Lexikon Design System
   *
   * @component
   * Progress bar with multiple variants and optional label
   * Animated transitions, accessible, and responsive
   * Based on design tokens and accessibility best practices (WCAG AA)
   */

  import { onMount } from 'svelte';

  // Props
  export let value: number = 0; // 0-100
  export let max: number = 100;
  export let showLabel: boolean = false;
  export let label: string = '';
  export let variant: 'primary' | 'success' | 'warning' | 'error' = 'primary';
  export let size: 'sm' | 'md' | 'lg' = 'md';
  export let animated: boolean = true;
  export let striped: boolean = false;
  export let indeterminate: boolean = false;
  export let className: string = '';

  // State
  let mounted = false;

  // Computed
  $: percentage = Math.min(Math.max((value / max) * 100, 0), 100);
  $: displayValue = mounted && animated ? percentage : 0;
  $: ariaLabel = label || `${Math.round(percentage)}% complété`;

  // Animation on mount
  onMount(() => {
    if (animated) {
      // Slight delay for smooth animation
      setTimeout(() => {
        mounted = true;
      }, 50);
    } else {
      mounted = true;
    }
  });

  // Watch for value changes
  $: if (mounted) {
    displayValue = percentage;
  }
</script>

<div class="progress-wrapper {className}">
  {#if showLabel || label}
    <div class="progress-header">
      <span class="progress-label">{label}</span>
      <span class="progress-percentage">{Math.round(percentage)}%</span>
    </div>
  {/if}

  <div
    class="progress-container size-{size}"
    role="progressbar"
    aria-label={ariaLabel}
    aria-valuenow={Math.round(percentage)}
    aria-valuemin={0}
    aria-valuemax={100}
  >
    <div
      class="progress-bar variant-{variant}"
      class:striped
      class:indeterminate
      style:width="{indeterminate ? 100 : displayValue}%"
    ></div>
  </div>
</div>

<style>
  .progress-wrapper {
    width: 100%;
  }

  .progress-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
  }

  .progress-label {
    font-size: 0.875rem;
    font-weight: 500;
    color: var(--color-gray-700, #374151);
  }

  .progress-percentage {
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--color-gray-900, #111827);
  }

  .progress-container {
    width: 100%;
    background-color: var(--color-gray-200, #e5e7eb);
    border-radius: 9999px;
    overflow: hidden;
    position: relative;
  }

  /* Sizes */
  .progress-container.size-sm {
    height: 6px;
  }

  .progress-container.size-md {
    height: 8px;
  }

  .progress-container.size-lg {
    height: 12px;
  }

  .progress-bar {
    height: 100%;
    border-radius: 9999px;
    transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
  }

  /* Variants */
  .progress-bar.variant-primary {
    background: linear-gradient(90deg, var(--color-primary-500, #3b82f6), var(--color-primary-600, #2563eb));
  }

  .progress-bar.variant-success {
    background: linear-gradient(90deg, #10b981, #059669);
  }

  .progress-bar.variant-warning {
    background: linear-gradient(90deg, #f59e0b, #d97706);
  }

  .progress-bar.variant-error {
    background: linear-gradient(90deg, #ef4444, #dc2626);
  }

  /* Striped pattern */
  .progress-bar.striped::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-image: linear-gradient(
      45deg,
      rgba(255, 255, 255, 0.15) 25%,
      transparent 25%,
      transparent 50%,
      rgba(255, 255, 255, 0.15) 50%,
      rgba(255, 255, 255, 0.15) 75%,
      transparent 75%,
      transparent
    );
    background-size: 1rem 1rem;
    animation: progress-stripes 1s linear infinite;
  }

  @keyframes progress-stripes {
    0% {
      background-position: 0 0;
    }
    100% {
      background-position: 1rem 0;
    }
  }

  /* Indeterminate state */
  .progress-bar.indeterminate {
    width: 100% !important;
    background: var(--color-gray-200, #e5e7eb);
  }

  .progress-bar.indeterminate::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    bottom: 0;
    width: 30%;
    background: linear-gradient(90deg, var(--color-primary-500, #3b82f6), var(--color-primary-600, #2563eb));
    border-radius: 9999px;
    animation: progress-indeterminate 1.5s ease-in-out infinite;
  }

  @keyframes progress-indeterminate {
    0% {
      left: -30%;
    }
    100% {
      left: 100%;
    }
  }

  /* Pulse animation for near-complete */
  .progress-bar:not(.indeterminate) {
    position: relative;
  }

  .progress-bar:not(.indeterminate)::after {
    content: '';
    position: absolute;
    top: 0;
    right: 0;
    bottom: 0;
    width: 20px;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3));
    animation: progress-shimmer 2s ease-in-out infinite;
  }

  @keyframes progress-shimmer {
    0%, 100% {
      opacity: 0;
    }
    50% {
      opacity: 1;
    }
  }
</style>
