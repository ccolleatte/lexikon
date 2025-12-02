<script lang="ts">
	export let data: Array<{ domain: string; count: number }> = [];

	const colors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899'];

	interface PieSlice {
		domain: string;
		count: number;
		percentage: number;
		color: string;
		startAngle: number;
		endAngle: number;
	}

	let slices: PieSlice[] = [];

	$: {
		const total = data.reduce((sum, d) => sum + d.count, 0);
		let startAngle = 0;

		slices = data.map((d, i) => {
			const percentage = total > 0 ? (d.count / total) * 100 : 0;
			const angle = (percentage / 100) * 360;
			const slice: PieSlice = {
				domain: d.domain,
				count: d.count,
				percentage: Math.round(percentage),
				color: colors[i % colors.length],
				startAngle,
				endAngle: startAngle + angle,
			};
			startAngle += angle;
			return slice;
		});
	}

	function polarToCartesian(
		centerX: number,
		centerY: number,
		radius: number,
		angleInDegrees: number
	): [number, number] {
		const angleInRadians = ((angleInDegrees - 90) * Math.PI) / 180.0;
		return [centerX + radius * Math.cos(angleInRadians), centerY + radius * Math.sin(angleInRadians)];
	}

	function describeArc(
		centerX: number,
		centerY: number,
		radius: number,
		startAngle: number,
		endAngle: number
	): string {
		const [startX, startY] = polarToCartesian(centerX, centerY, radius, endAngle);
		const [endX, endY] = polarToCartesian(centerX, centerY, radius, startAngle);
		const largeArcFlag = endAngle - startAngle <= 180 ? '0' : '1';

		return [
			'M',
			centerX,
			centerY,
			'L',
			startX,
			startY,
			'A',
			radius,
			radius,
			0,
			largeArcFlag,
			0,
			endX,
			endY,
			'Z',
		].join(' ');
	}
</script>

<div class="flex flex-col gap-6">
	{#if data.length > 0}
		<!-- Pie Chart SVG -->
		<div class="flex justify-center">
			<svg width="250" height="250" viewBox="0 0 250 250" class="drop-shadow">
				{#each slices as slice}
					<path
						d={describeArc(125, 125, 100, slice.startAngle, slice.endAngle)}
						fill={slice.color}
						stroke="white"
						stroke-width="2"
					/>
				{/each}
			</svg>
		</div>

		<!-- Legend -->
		<div class="space-y-2">
			{#each slices as slice}
				<div class="flex items-center justify-between">
					<div class="flex items-center gap-2">
						<div class="w-3 h-3 rounded-full" style="background-color: {slice.color}" />
						<span class="text-sm font-medium text-gray-700">{slice.domain}</span>
					</div>
					<div class="text-right">
						<span class="text-sm font-bold text-gray-900">{slice.count}</span>
						<span class="text-xs text-gray-500 ml-1">({slice.percentage}%)</span>
					</div>
				</div>
			{/each}
		</div>
	{:else}
		<div class="text-center py-8">
			<p class="text-gray-500">Aucune donnée disponible</p>
		</div>
	{/if}
</div>
