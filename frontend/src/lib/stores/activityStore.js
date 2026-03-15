/**
 * Activity store for fetching and managing recent activity data.
 * 
 * Fetches real activity data from backend API instead of using mock data.
 */

import { writable, derived } from 'svelte/store';
import { configStore } from './appStore.js';

/**
 * Activity item type definition
 * @typedef {Object} ActivityItem
 * @property {string} id
 * @property {string} type - 'movie', 'tv', 'music', 'search', 'import', 'download'
 * @property {string} title
 * @property {string} service - 'radarr', 'sonarr', 'lidarr', 'prowlarr'
 * @property {Date} timestamp
 * @property {Object} [details]
 */

/**
 * Activity state store
 * @type {import('svelte/store').Writable<{
 *   activities: Array<ActivityItem>,
 *   isLoading: boolean,
 *   lastUpdated: Date | null,
 *   error: string | null
 * }>}
 */
export const activityStore = writable({
    activities: [],
    isLoading: false,
    lastUpdated: null,
    error: null
});

/**
 * Get backend URL from config store
 * @returns {Promise<string>}
 */
async function getBackendUrl() {
    return new Promise((resolve) => {
        const unsubscribe = configStore.subscribe((config) => {
            resolve(config.backendUrl);
            unsubscribe();
        });
    });
}

/**
 * Fetch recent activity from backend API
 * @param {number} [limit=20] - Maximum number of activities to fetch
 * @param {number} [hours=24] - Time window in hours
 * @returns {Promise<Array<ActivityItem>>}
 */
export async function fetchRecentActivity(limit = 20, hours = 24) {
    try {
        const backendUrl = await getBackendUrl();
        
        const response = await fetch(
            `${backendUrl}/api/v1/activity/recent?limit=${limit}&hours=${hours}`,
            {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            }
        );

        if (!response.ok) {
            throw new Error(`Failed to fetch activity: ${response.status} ${response.statusText}`);
        }

        const data = await response.json();
        
        // Convert timestamp strings to Date objects
        return data.activities.map(activity => ({
            ...activity,
            timestamp: new Date(activity.timestamp)
        }));
        
    } catch (error) {
        console.error('Error fetching recent activity:', error);
        throw error;
    }
}

/**
 * Fetch activity for a specific service
 * @param {string} serviceName - 'radarr', 'sonarr', 'lidarr', or 'prowlarr'
 * @param {number} [limit=10] - Maximum number of activities to fetch
 * @param {number} [hours=24] - Time window in hours
 * @returns {Promise<Array<ActivityItem>>}
 */
export async function fetchServiceActivity(serviceName, limit = 10, hours = 24) {
    try {
        const backendUrl = await getBackendUrl();
        
        const response = await fetch(
            `${backendUrl}/api/v1/activity/service/${serviceName}?limit=${limit}&hours=${hours}`,
            {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            }
        );

        if (!response.ok) {
            throw new Error(`Failed to fetch ${serviceName} activity: ${response.status} ${response.statusText}`);
        }

        const data = await response.json();
        
        // Convert timestamp strings to Date objects
        return data.activities.map(activity => ({
            ...activity,
            timestamp: new Date(activity.timestamp)
        }));
        
    } catch (error) {
        console.error(`Error fetching ${serviceName} activity:`, error);
        throw error;
    }
}

/**
 * Refresh activity data and update store
 * @param {number} [limit=20] - Maximum number of activities to fetch
 * @param {number} [hours=24] - Time window in hours
 * @returns {Promise<void>}
 */
export async function refreshActivity(limit = 20, hours = 24) {
    activityStore.update(store => ({
        ...store,
        isLoading: true,
        error: null
    }));

    try {
        const activities = await fetchRecentActivity(limit, hours);
        
        activityStore.set({
            activities,
            isLoading: false,
            lastUpdated: new Date(),
            error: null
        });
    } catch (error) {
        console.error('Failed to refresh activity:', error);
        
        activityStore.update(store => ({
            ...store,
            isLoading: false,
            error: error.message || 'Failed to fetch activity data'
        }));
    }
}

/**
 * Poll for new activity at regular intervals
 * @param {number} intervalMs - Polling interval in milliseconds
 * @returns {NodeJS.Timeout} Interval ID
 */
export function startActivityPolling(intervalMs = 30000) {
    // Initial refresh
    refreshActivity();
    
    // Start polling interval
    return setInterval(() => {
        refreshActivity();
    }, intervalMs);
}

/**
 * Get the most recent activity items (limited to count)
 * @type {import('svelte/store').Readable<Array<ActivityItem>>}
 */
export const recentActivities = derived(activityStore, ($store) => {
    return $store.activities.slice(0, 5); // Only show last 5 items
});

/**
 * Get activity count by service type
 * @type {import('svelte/store').Readable<Object<string, number>>}
 */
export const activityCountByService = derived(activityStore, ($store) => {
    const counts = {
        radarr: 0,
        sonarr: 0,
        lidarr: 0,
        prowlarr: 0
    };
    
    $store.activities.forEach(activity => {
        if (activity.service && counts[activity.service] !== undefined) {
            counts[activity.service]++;
        }
    });
    
    return counts;
});

/**
 * Get activity count by type
 * @type {import('svelte/store').Readable<Object<string, number>>}
 */
export const activityCountByType = derived(activityStore, ($store) => {
    const counts = {};
    
    $store.activities.forEach(activity => {
        const type = activity.type || 'unknown';
        counts[type] = (counts[type] || 0) + 1;
    });
    
    return counts;
});

/**
 * Clear activity store
 */
export function clearActivity() {
    activityStore.set({
        activities: [],
        isLoading: false,
        lastUpdated: null,
        error: null
    });
}