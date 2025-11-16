<script lang="ts">
  /**
   * Input Component - Lexikon Design System
   *
   * @component
   * Versatile input field with label, helper text, error states, and char counter
   * Supports text, email, password, number types
   * Based on design tokens and accessibility best practices (WCAG AA)
   */

  import { createEventDispatcher } from 'svelte';

  // Props
  export let type: 'text' | 'email' | 'password' | 'number' | 'url' = 'text';
  export let value: string | number = '';
  export let placeholder: string = '';
  export let label: string = '';
  export let helperText: string = '';
  export let errorMessage: string = '';
  export let disabled: boolean = false;
  export let required: boolean = false;
  export let readonly: boolean = false;
  export let maxlength: number | undefined = undefined;
  export let showCharCounter: boolean = false;
  export let id: string = `input-${Math.random().toString(36).substr(2, 9)}`;
  export let name: string = '';
  export let className: string = '';

  // Input-specific props
  export let min: number | undefined = undefined;
  export let max: number | undefined = undefined;
  export let step: number | undefined = undefined;
  export let pattern: string | undefined = undefined;
  export let autocomplete: string | undefined = undefined;

  const dispatch = createEventDispatcher();

  // State
  let focused = false;
  let touched = false;

  // Computed
  $: hasError = !!errorMessage && touched;
  $: charCount = typeof value === 'string' ? value.length : 0;
  $: isNearLimit = maxlength && charCount > maxlength * 0.9;

  // Handlers
  function handleInput(event: Event) {
    const target = event.target as HTMLInputElement;
    value = type === 'number' ? Number(target.value) : target.value;
    dispatch('input', { value, event });
  }

  function handleChange(event: Event) {
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

  function handleKeydown(event: KeyboardEvent) {
    dispatch('keydown', event);
  }
</script>

<div class="input-wrapper {className}">
  {#if label}
    <label for={id} class="input-label">
      <span class="label-text">
        {label}
        {#if required}
          <span class="label-required" aria-label="obligatoire">*</span>
        {/if}
      </span>
      {#if showCharCounter && maxlength}
        <span class="char-counter" class:near-limit={isNearLimit}>
          {charCount}/{maxlength}
        </span>
      {/if}
    </label>
  {/if}

  <div class="input-container">
    <input
      {id}
      {type}
      {name}
      {placeholder}
      {disabled}
      {required}
      {readonly}
      {maxlength}
      {min}
      {max}
      {step}
      {pattern}
      {autocomplete}
      {value}
      on:input={handleInput}
      on:change={handleChange}
      on:focus={handleFocus}
      on:blur={handleBlur}
      on:keydown={handleKeydown}
      class="input-field"
      class:error={hasError}
      class:focused
      class:disabled
      aria-invalid={hasError}
      aria-describedby={helperText || errorMessage ? `${id}-help` : undefined}
    />
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
  .input-wrapper {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .input-label {
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

  .char-counter {
    font-size: 0.75rem;
    font-weight: 400;
    color: var(--color-gray-500, #6b7280);
    transition: color 0.2s;
  }

  .char-counter.near-limit {
    color: var(--color-error-500, #ef4444);
    font-weight: 500;
  }

  .input-container {
    position: relative;
  }

  .input-field {
    width: 100%;
    padding: 0.625rem 0.75rem;
    font-family: var(--font-sans, 'Inter', system-ui, sans-serif);
    font-size: 1rem;
    line-height: 1.5;
    color: var(--color-gray-900, #111827);
    background-color: var(--color-white, #ffffff);
    border: 2px solid var(--color-gray-300, #d1d5db);
    border-radius: var(--radius-md, 0.375rem);
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    outline: none;
  }

  .input-field::placeholder {
    color: var(--color-gray-400, #9ca3af);
  }

  /* Focus state */
  .input-field:focus {
    border-color: var(--color-primary-500, #3b82f6);
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }

  /* Error state */
  .input-field.error {
    border-color: var(--color-error-500, #ef4444);
  }

  .input-field.error:focus {
    border-color: var(--color-error-500, #ef4444);
    box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
  }

  /* Disabled state */
  .input-field:disabled {
    background-color: var(--color-gray-100, #f3f4f6);
    color: var(--color-gray-500, #6b7280);
    cursor: not-allowed;
    opacity: 0.6;
  }

  /* Readonly state */
  .input-field:read-only {
    background-color: var(--color-gray-50, #f9fafb);
    cursor: default;
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
  .input-field:not(:disabled):hover {
    border-color: var(--color-gray-400, #9ca3af);
  }

  .input-field:not(:disabled):hover:focus {
    border-color: var(--color-primary-500, #3b82f6);
  }

  .input-field.error:not(:disabled):hover {
    border-color: var(--color-error-500, #ef4444);
  }

  /* Number input - remove spinners for cleaner look (optional) */
  .input-field[type="number"]::-webkit-inner-spin-button,
  .input-field[type="number"]::-webkit-outer-spin-button {
    -webkit-appearance: none;
    margin: 0;
  }

  .input-field[type="number"] {
    -moz-appearance: textfield;
  }
</style>
