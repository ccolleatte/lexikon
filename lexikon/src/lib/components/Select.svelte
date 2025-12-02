<script lang="ts">
  /**
   * Select Component - Lexikon Design System
   *
   * @component
   * Dropdown select input with label, helper text, error states
   * Supports native select and custom options
   * Based on design tokens and accessibility best practices (WCAG AA)
   */

  import { createEventDispatcher } from 'svelte';

  // Types
  export interface SelectOption {
    value: string | number;
    label: string;
    disabled?: boolean;
  }

  // Props
  export let value: string | number = '';
  export let options: SelectOption[] = [];
  export let placeholder: string = 'Sélectionnez une option';
  export let label: string = '';
  export let helperText: string = '';
  export let errorMessage: string = '';
  export let disabled: boolean = false;
  export let required: boolean = false;
  export let id: string = `select-${Math.random().toString(36).substr(2, 9)}`;
  export let name: string = '';
  export let className: string = '';

  const dispatch = createEventDispatcher();

  // State
  let focused = false;
  let touched = false;

  // Computed
  $: hasError = !!errorMessage && touched;

  // Handlers
  function handleChange(event: Event) {
    const target = event.target as HTMLSelectElement;
    value = target.value;
    dispatch('change', { value, event });
  }

  function handleFocus(event: FocusEvent) {
    focused = true;
    dispatch('focus', event);
  }

  function handleBlur(event: FocusEvent) {
    focused = false;
    touched = true;
    dispatch('blur', event);
  }
</script>

<div class="select-wrapper {className}">
  {#if label}
    <label for={id} class="select-label">
      <span class="label-text">
        {label}
        {#if required}
          <span class="label-required" aria-label="obligatoire">*</span>
        {/if}
      </span>
    </label>
  {/if}

  <div class="select-container">
    <select
      {id}
      {name}
      {disabled}
      {required}
      bind:value
      on:change={handleChange}
      on:focus={handleFocus}
      on:blur={handleBlur}
      class="select-field"
      class:error={hasError}
      class:focused
      class:disabled
      class:has-value={value !== ''}
      aria-invalid={hasError}
      aria-describedby={helperText || errorMessage ? `${id}-help` : undefined}
    >
      {#if placeholder}
        <option value="" disabled selected={value === ''}>
          {placeholder}
        </option>
      {/if}

      {#each options as option}
        <option
          value={option.value}
          disabled={option.disabled}
        >
          {option.label}
        </option>
      {/each}
    </select>

    <svg class="select-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M6 9l6 6 6-6"/>
    </svg>
  </div>

  {#if helperText && !hasError}
    <p id="{id}-help" class="helper-text">
      {helperText}
    </p>
  {/if}

  {#if hasError}
    <p id="{id}-help" class="error-text" role="alert">
      <svg class="error-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10"/>
        <line x1="12" y1="8" x2="12" y2="12"/>
        <line x1="12" y1="16" x2="12.01" y2="16"/>
      </svg>
      {errorMessage}
    </p>
  {/if}
</div>

<style>
  .select-wrapper {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .select-label {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.875rem;
    font-weight: 500;
    color: var(--color-gray-700, #374151);
    cursor: pointer;
  }

  .label-text {
    display: flex;
    align-items: center;
    gap: 0.125rem;
  }

  .label-required {
    color: var(--color-error-500, #ef4444);
    font-weight: 600;
  }

  .select-container {
    position: relative;
  }

  .select-field {
    width: 100%;
    padding: 0.625rem 2.5rem 0.625rem 0.75rem;
    font-family: var(--font-sans, 'Inter', system-ui, sans-serif);
    font-size: 1rem;
    line-height: 1.5;
    color: var(--color-gray-900, #111827);
    background-color: var(--color-white, #ffffff);
    border: 2px solid var(--color-gray-300, #d1d5db);
    border-radius: var(--radius-md, 0.375rem);
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    outline: none;
    appearance: none;
    cursor: pointer;
  }

  /* Placeholder style (when no value selected) */
  .select-field:not(.has-value) {
    color: var(--color-gray-400, #9ca3af);
  }

  /* Focus state */
  .select-field:focus {
    border-color: var(--color-primary-500, #3b82f6);
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }

  /* Error state */
  .select-field.error {
    border-color: var(--color-error-500, #ef4444);
  }

  .select-field.error:focus {
    border-color: var(--color-error-500, #ef4444);
    box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
  }

  /* Disabled state */
  .select-field:disabled {
    background-color: var(--color-gray-100, #f3f4f6);
    color: var(--color-gray-500, #6b7280);
    cursor: not-allowed;
    opacity: 0.6;
  }

  /* Chevron icon */
  .select-icon {
    position: absolute;
    right: 0.75rem;
    top: 50%;
    transform: translateY(-50%);
    pointer-events: none;
    color: var(--color-gray-500, #6b7280);
    transition: transform 0.2s, color 0.2s;
  }

  .select-field:focus ~ .select-icon {
    color: var(--color-primary-500, #3b82f6);
    transform: translateY(-50%) rotate(180deg);
  }

  .select-field.error ~ .select-icon {
    color: var(--color-error-500, #ef4444);
  }

  .select-field:disabled ~ .select-icon {
    color: var(--color-gray-400, #9ca3af);
  }

  /* Helper text */
  .helper-text {
    font-size: 0.875rem;
    color: var(--color-gray-600, #4b5563);
    margin: 0;
  }

  /* Error text */
  .error-text {
    display: flex;
    align-items: center;
    gap: 0.375rem;
    font-size: 0.875rem;
    color: var(--color-error-500, #ef4444);
    margin: 0;
  }

  .error-icon {
    flex-shrink: 0;
  }

  /* Hover states (only when not disabled) */
  .select-field:not(:disabled):hover {
    border-color: var(--color-gray-400, #9ca3af);
  }

  .select-field:not(:disabled):hover:focus {
    border-color: var(--color-primary-500, #3b82f6);
  }

  .select-field.error:not(:disabled):hover {
    border-color: var(--color-error-500, #ef4444);
  }
</style>
