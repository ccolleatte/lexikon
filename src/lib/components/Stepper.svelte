<script lang="ts">
	export let steps: { label: string }[] = [];
	export let currentStep: number = 0;
</script>

<div class="stepper">
	<div class="flex items-center justify-center gap-2">
		{#each steps as step, index}
			<!-- Step Indicator -->
			<div class="step" class:completed={index < currentStep} class:active={index === currentStep} class:pending={index > currentStep}>
				<div class="step-indicator">
					{#if index < currentStep}
						<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
							<path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
						</svg>
					{:else}
						<span class="step-number">{index + 1}</span>
					{/if}
				</div>
				<span class="step-label">{step.label}</span>
			</div>

			<!-- Connector -->
			{#if index < steps.length - 1}
				<div class="step-connector" class:completed={index < currentStep}></div>
			{/if}
		{/each}
	</div>
</div>

<style>
	.stepper {
		margin-bottom: 2rem;
	}

	.step {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 0.5rem;
	}

	.step-indicator {
		width: 40px;
		height: 40px;
		border-radius: 9999px;
		display: flex;
		align-items: center;
		justify-content: center;
		font-weight: 600;
		font-size: 0.875rem;
		transition: all 0.3s;
	}

	.step.completed .step-indicator {
		background: var(--color-success-500, #10b981);
		color: white;
	}

	.step.active .step-indicator {
		background: var(--color-primary-600, #2563eb);
		color: white;
		box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.2);
	}

	.step.pending .step-indicator {
		background: var(--color-gray-200, #e5e7eb);
		color: var(--color-gray-500, #6b7280);
	}

	.step-label {
		font-size: 0.75rem;
		color: var(--color-gray-600, #4b5563);
		font-weight: 500;
		white-space: nowrap;
	}

	.step.active .step-label {
		color: var(--color-primary-600, #2563eb);
		font-weight: 600;
	}

	.step-connector {
		width: 60px;
		height: 2px;
		background: var(--color-gray-200, #e5e7eb);
		margin-bottom: 28px;
		transition: background 0.3s;
	}

	.step-connector.completed {
		background: var(--color-success-500, #10b981);
	}

	@media (max-width: 640px) {
		.step-connector {
			width: 40px;
		}

		.step-label {
			font-size: 0.65rem;
		}

		.step-indicator {
			width: 32px;
			height: 32px;
			font-size: 0.75rem;
		}
	}
</style>
