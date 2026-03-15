<!--
Recent Activity Feed Component

Displays real activity data from the backend API (last 5 items across all services).
Shows appropriate icons based on activity type and service.
-->

<script>
	import { onMount } from 'svelte';
	import {
		activityStore,
		recentActivities,
		refreshActivity
	} from '$lib/stores/activityStore.js';

	/**
	 * Get icon for activity type
	 */
	function getActivityIcon(type) {
		const icons = {
			movie: '🎬',
			tv: '📺',
			music: '🎵',
			search: '🔍',
			import: '📥',
			download: '📥',
		};
		return icons[type] || '📦';
	}

	/**
	 * Format timestamp
	 */
	function formatTime(date) {
		if (!date) return '';
		const now = new Date();
		const seconds = Math.floor((now - new Date(date)) / 1000);

		if (seconds < 60) return `${seconds}s`;
		if (seconds < 3600) return `${Math.floor(seconds / 60)}m`;
		if (seconds < 86400) return `${Math.floor(seconds / 3600)}h`;
		return new Date(date).toLocaleDateString();
	}

	/**
	 * Get service label
	 */
	function getServiceLabel(service) {
		return (service || 'Unknown').charAt(0).toUpperCase() + service.slice(1);
	}

	/**
	 * Handle manual refresh
	 */
	async function handleRefresh() {
		await refreshActivity();
	}

	onMount(() => {
		// Initial refresh on component mount
		refreshActivity();
	});
</script>

<div class="bg-gray-800 border border-gray-700 rounded-lg p-6 shadow-md">
	<div class="flex items-center justify-between mb-4">
		<h2 class="text-lg font-semibold text-white">Recent Activity</h2>
		<div class="flex items-center gap-2">
			<span class="text-xs text-gray-400">Last 5</span>
			<button
				on:click={handleRefresh}
				class="text-xs text-gray-500 hover:text-white transition-colors"
				title="Refresh activity"
			>
				🔄
			</button>
		</div>
	</div>

	<!-- Error state -->
	{#if $activityStore.error}
		<div class="text-center py-8">
			<p class="text-red-500 text-sm">Failed to load activity: {$activityStore.error}</p>
			<button
				on:click={handleRefresh}
				class="mt-2 text-xs text-gray-500 hover:text-white"
			>
				Retry
			</button>
		</div>

	<!-- Loading state -->
	{:else if $activityStore.isLoading}
		<div class="text-center py-8">
			<div class="inline-block animate-spin text-xl mb-2">🔄</div>
			<p class="text-gray-500">Loading activity...</p>
		</div>

	<!-- Empty state -->
	{:else if $recentActivities.length === 0}
		<div class="text-center py-8">
			<p class="text-gray-500">No recent activity found</p>
			<p class="text-xs text-gray-600 mt-1">
				Activity from the last 24 hours will appear here
			</p>
		</div>

	<!-- Activity list -->
	{:else}
		<div class="space-y-3">
			{#each $recentActivities as activity (activity.id)}
				<div class="flex items-start gap-3 pb-3 border-b border-gray-700 last:border-b-0">
					<span class="text-xl flex-shrink-0">{getActivityIcon(activity.type)}</span>
					<div class="flex-1 min-w-0">
						<p class="text-sm text-gray-200 truncate">{activity.title}</p>
						<div class="flex items-center gap-2 mt-1">
							<span class="text-xs text-gray-500">
								{getServiceLabel(activity.service)}
							</span>
							<span class="text-xs text-gray-600">
								{formatTime(activity.timestamp)}
							</span>
						</div>
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>

<style>
	/* All styling via Tailwind */
</style>
