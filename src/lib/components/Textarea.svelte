<script lang="ts">
  /**
   * Textarea Component - Lexikon Design System
   *
   * @component
   * Multi-line text input with label, helper text, error states, and char counter
   * Auto-resize option for dynamic content
   * Based on design tokens and accessibility best practices (WCAG AA)
   */

  import { createEventDispatcher, onMount } from 'svelte';

  // Props
  export let value: string = '';
  export let placeholder: string = '';
  export let label: string = '';
  export let helperText: string = '';
  export let errorMessage: string = '';
  export let disabled: boolean = false;
  export let required: boolean = false;
  export let readonly: boolean = false;
  export let maxlength: number | undefined = undefined;
  export let showCharCounter: boolean = false;
  export let id: string = `textarea-${Math.random().toString(36).substr(2, 9)}`;
  export let name: string = '';
  export let className: string = '';

  // Textarea-specific props
  export let rows: number = 5;
  export let cols: number | undefined = undefined;
  export let resize: 'none' | 'vertical' | 'horizontal' | 'both' = 'vertical';
  export let autoResize: boolean = false;

  const dispatch = createEventDispatcher();

  // State
  let focused = false;
  let touched = false;
  let textareaElement: HTMLTextAreaElement;

  // Computed
  $: hasError = !!errorMessage && touched;
  $: charCount = value.length;
  $: isNearLimit = maxlength && charCount > maxlength * 0.9;

  // Auto-resize logic
  function handleAutoResize() {
    if (autoResize && textareaElement) {
      textareaElement.style.height = 'auto';
      textareaElement.style.height = `${textareaElement.scrollHeight}px`;
    }
  }

  onMount(() => {
    if (autoResize && value) {
      handleAutoResize();
    }
  });

  // Handlers
  function handleInput(event: Event) {
    const target = event.target as HTMLTextAreaElement;
    value = target.value;

    if (autoResize) {
      handleAutoResize();
    }

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

  // Watch for external value changes
  $: if (autoResize && value !== undefined) {
    handleAutoResize();
  }
</script>

<div class="textarea-wrapper {className}">
  {#if label}
    <label for={id} class="textarea-label">
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

  <div class="textarea-container">
    <textarea
      bind:this={textareaElement}
      {id}
      {name}
      {placeholder}
      {disabled}
      {required}
      {readonly}
      {maxlength}
      {rows}
      {cols}
      bind:value
      on:input={handleInput}
      on:change={handleChange}
      on:focus={handleFocus}
      on:blur={handleBlur}
      on:keydown={handleKeydown}
      class="textarea-field"
      class:error={hasError}
      class:focused
      class:disabled
      class:auto-resize={autoResize}
      style:resize={autoResize ? 'none' : resize}
      aria-invalid={hasError}
      aria-describedby={helperText || errorMessage ? `${id}-help` : undefined}
    ></textarea>
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
  .textarea-wrapper {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .textarea-label {
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

  .textarea-container {
    position: relative;
  }

  .textarea-field {
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
    resize: vertical;
    min-height: 120px;
  }

  .textarea-field.auto-resize {
    overflow-y: hidden;
  }

  .textarea-field::placeholder {
    color: var(--color-gray-400, #9ca3af);
  }

  /* Focus state */
  .textarea-field:focus {
    border-color: var(--color-primary-500, #3b82f6);
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }

  /* Error state */
  .textarea-field.error {
    border-color: var(--color-error-500, #ef4444);
  }

  .textarea-field.error:focus {
    border-color: var(--color-error-500, #ef4444);
    box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
  }

  /* Disabled state */
  .textarea-field:disabled {
    background-color: var(--color-gray-100, #f3f4f6);
    color: var(--color-gray-500, #6b7280);
    cursor: not-allowed;
    opacity: 0.6;
  }

  /* Readonly state */
  .textarea-field:read-only {
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
  .textarea-field:not(:disabled):hover {
    border-color: var(--color-gray-400, #9ca3af);
  }

  .textarea-field:not(:disabled):hover:focus {
    border-color: var(--color-primary-500, #3b82f6);
  }

  .textarea-field.error:not(:disabled):hover {
    border-color: var(--color-error-500, #ef4444);
  }

  /* Scrollbar styling (optional) */
  .textarea-field::-webkit-scrollbar {
    width: 8px;
  }

  .textarea-field::-webkit-scrollbar-track {
    background: var(--color-gray-100, #f3f4f6);
    border-radius: 4px;
  }

  .textarea-field::-webkit-scrollbar-thumb {
    background: var(--color-gray-300, #d1d5db);
    border-radius: 4px;
  }

  .textarea-field::-webkit-scrollbar-thumb:hover {
    background: var(--color-gray-400, #9ca3af);
  }
</style>
