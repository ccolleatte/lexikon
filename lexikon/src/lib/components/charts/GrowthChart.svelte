<script lang="ts">
	export let data: Array<{ date: string; count: number }> = [];

	const padding = { top: 20, right: 20, bottom: 40, left: 40 };
	const width = 500;
	const height = 300;
	const chartWidth = width - padding.left - padding.right;
	const chartHeight = height - padding.top - padding.bottom;

	let maxValue = 0;
	let points: Array<{ x: number; y: number; date: string; count: number }> = [];

	$: {
		if (data.length > 0) {
			maxValue = Math.max(...data.map((d) => d.count));
			maxValue = Math.ceil(maxValue / 10) * 10 || 10; // Round up to nearest 10

			points = data.map((d, i) => ({
				x: padding.left + (i / Math.max(data.length - 1, 1)) * chartWidth,
				y: padding.top + chartHeight - (d.count / maxValue) * chartHeight,
				date: d.date,
				count: d.count,
			}));
		}
	}

	function formatDate(dateStr: string): string {
		const date = new Date(dateStr);
		return date.toLocaleDateString('fr-FR', { month: 'short', day: 'numeric' });
	}

	function getPathD(): string {
		if (points.length === 0) return '';
		return points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ');
	}
</script>

<div class="flex justify-center overflow-x-auto">
	{#if data.length > 0}
		<svg {width} {height} viewBox="0 0 {width} {height}" class="drop-shadow">
			<!-- Grid lines -->
			{#each Array(5) as _, i}
				<line
					x1={padding.left}
					y1={padding.top + (i * chartHeight) / 4}
					x2={width - padding.right}
					y2={padding.top + (i * chartHeight) / 4}
					stroke="#e5e7eb"
					stroke-width="1"
				/>
				<text
					x={padding.left - 8}
					y={padding.top + (i * chartHeight) / 4 + 4}
					font-size="12"
					fill="#6b7280"
					text-anchor="end"
				>
					{maxValue - (i * maxValue) / 4}
				</text>
			{/each}

			<!-- Axes -->
			<line
				x1={padding.left}
				y1={padding.top + chartHeight}
				x2={width - padding.right}
				y2={padding.top + chartHeight}
				stroke="#374151"
				stroke-width="2"
			/>
			<line
				x1={padding.left}
				y1={padding.top}
				x2={padding.left}
				y2={padding.top + chartHeight}
				stroke="#374151"
				stroke-width="2"
			/>

			<!-- Line -->
			<path d={getPathD()} fill="none" stroke="#3b82f6" stroke-width="2" stroke-linejoin="round" />

			<!-- Area under line -->
			<path
				d={`${getPathD()} L ${points[points.length - 1].x} ${padding.top + chartHeight} L ${points[0].x} ${
					padding.top + chartHeight
				} Z`}
				fill="#3b82f6"
				fill-opacity="0.1"
			/>

			<!-- Points -->
			{#each points as point}
				<circle cx={point.x} cy={point.y} r="4" fill="#3b82f6" />
			{/each}

			<!-- X-axis labels -->
			{#each points.filter((_, i) => i % Math.ceil(points.length / 5) === 0 || i === points.length - 1) as point}
				<text
					x={point.x}
					y={padding.top + chartHeight + 20}
					font-size="12"
					fill="#6b7280"
					text-anchor="middle"
				>
					{formatDate(point.date)}
				</text>
			{/each}
		</svg>
	{:else}
		<div class="text-center py-8 w-full">
			<p class="text-gray-500">Aucune donnée disponible</p>
		</div>
	{/if}
</div>
