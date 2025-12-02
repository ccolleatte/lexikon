<script lang="ts">
	export let title: string;
	export let value: number;
	export let icon: string;
	export let color: 'blue' | 'green' | 'purple' | 'orange' = 'blue';
	export let suffix: string = '';

	const colorClasses = {
		blue: 'bg-blue-50 border-blue-200',
		green: 'bg-green-50 border-green-200',
		purple: 'bg-purple-50 border-purple-200',
		orange: 'bg-orange-50 border-orange-200',
	};

	const textColorClasses = {
		blue: 'text-blue-900',
		green: 'text-green-900',
		purple: 'text-purple-900',
		orange: 'text-orange-900',
	};
</script>

<div class="bg-white rounded-lg border border-gray-200 p-6">
	<div class="flex items-start justify-between mb-4">
		<div class="text-3xl">{icon}</div>
		<div class={`px-3 py-1 rounded-full text-xs font-semibold {colorClasses[color]}`}>
			<span class={textColorClasses[color]}>{color}</span>
		</div>
	</div>

	<p class="text-sm font-medium text-gray-600 mb-1">{title}</p>
	<p class="text-3xl font-bold text-gray-900">{suffix}{value}</p>
</div>
