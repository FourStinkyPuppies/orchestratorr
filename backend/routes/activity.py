"""
Activity routes for fetching recent activity from *arr services.

Provides endpoints to get recent grabs, imports, and searches across all services.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.clients.radarr_client import RadarrClient
from backend.clients.sonarr_client import SonarrClient
from backend.clients.lidarr_client import LidarrClient
from backend.clients.prowlarr_client import ProwlarrClient
from backend.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/activity", tags=["activity"])


class ActivityItem(BaseModel):
    """Model for a single activity item."""
    id: str
    type: str  # 'movie', 'tv', 'music', 'search', 'import', 'download'
    title: str
    service: str  # 'radarr', 'sonarr', 'lidarr', 'prowlarr'
    timestamp: datetime
    details: Optional[dict] = None


class ActivityResponse(BaseModel):
    """Response model for activity endpoints."""
    activities: List[ActivityItem]
    total_count: int
    timestamp: datetime


async def get_radarr_activity() -> List[ActivityItem]:
    """Get recent activity from Radarr."""
    try:
        client = RadarrClient()
        # Get recent history (last 24 hours)
        history = await client.get_history(limit=10)
        
        activities = []
        for item in history:
            activities.append(ActivityItem(
                id=f"radarr_{item.get('id')}",
                type='movie',
                title=item.get('sourceTitle', 'Unknown Movie'),
                service='radarr',
                timestamp=item.get('date', datetime.now()),
                details={
                    'eventType': item.get('eventType'),
                    'quality': item.get('quality', {}).get('quality', {}).get('name')
                }
            ))
        return activities
    except Exception as e:
        logger.error(f"Failed to fetch Radarr activity: {e}")
        return []


async def get_sonarr_activity() -> List[ActivityItem]:
    """Get recent activity from Sonarr."""
    try:
        client = SonarrClient()
        # Get recent history (last 24 hours)
        history = await client.get_history(limit=10)
        
        activities = []
        for item in history:
            activities.append(ActivityItem(
                id=f"sonarr_{item.get('id')}",
                type='tv',
                title=item.get('sourceTitle', 'Unknown TV Show'),
                service='sonarr',
                timestamp=item.get('date', datetime.now()),
                details={
                    'eventType': item.get('eventType'),
                    'quality': item.get('quality', {}).get('quality', {}).get('name')
                }
            ))
        return activities
    except Exception as e:
        logger.error(f"Failed to fetch Sonarr activity: {e}")
        return []


async def get_lidarr_activity() -> List[ActivityItem]:
    """Get recent activity from Lidarr."""
    try:
        client = LidarrClient()
        # Get recent history (last 24 hours)
        history = await client.get_history(limit=10)
        
        activities = []
        for item in history:
            activities.append(ActivityItem(
                id=f"lidarr_{item.get('id')}",
                type='music',
                title=item.get('sourceTitle', 'Unknown Album'),
                service='lidarr',
                timestamp=item.get('date', datetime.now()),
                details={
                    'eventType': item.get('eventType'),
                    'quality': item.get('quality', {}).get('quality', {}).get('name')
                }
            ))
        return activities
    except Exception as e:
        logger.error(f"Failed to fetch Lidarr activity: {e}")
        return []


async def get_prowlarr_activity() -> List[ActivityItem]:
    """Get recent activity from Prowlarr."""
    try:
        client = ProwlarrClient()
        # Get recent indexer queries
        queries = await client.get_indexer_stats(hours=24)
        
        activities = []
        for query in queries:
            activities.append(ActivityItem(
                id=f"prowlarr_{query.get('indexerId')}_{query.get('timestamp')}",
                type='search',
                title=f"Searched {query.get('indexerName', 'Unknown Indexer')}",
                service='prowlarr',
                timestamp=query.get('timestamp', datetime.now()),
                details={
                    'queryCount': query.get('queryCount'),
                    'resultCount': query.get('resultCount')
                }
            ))
        return activities
    except Exception as e:
        logger.error(f"Failed to fetch Prowlarr activity: {e}")
        return []


@router.get("/recent", response_model=ActivityResponse)
async def get_recent_activity(limit: int = 20, hours: int = 24):
    """
    Get recent activity across all *arr services.
    
    Args:
        limit: Maximum number of activities to return
        hours: Time window to look back (default: 24 hours)
    
    Returns:
        ActivityResponse: List of recent activities
    """
    try:
        # Fetch activity from all services concurrently
        radarr_activity = get_radarr_activity()
        sonarr_activity = get_sonarr_activity()
        lidarr_activity = get_lidarr_activity()
        prowlarr_activity = get_prowlarr_activity()
        
        # Wait for all requests to complete
        activities = await radarr_activity + await sonarr_activity + await lidarr_activity + await prowlarr_activity
        
        # Sort by timestamp (newest first)
        activities.sort(key=lambda x: x.timestamp, reverse=True)
        
        # Apply limit
        limited_activities = activities[:limit]
        
        return ActivityResponse(
            activities=limited_activities,
            total_count=len(activities),
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Failed to fetch recent activity: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch activity data")


@router.get("/service/{service_name}", response_model=ActivityResponse)
async def get_service_activity(service_name: str, limit: int = 10, hours: int = 24):
    """
    Get recent activity for a specific service.
    
    Args:
        service_name: Name of the service ('radarr', 'sonarr', 'lidarr', 'prowlarr')
        limit: Maximum number of activities to return
        hours: Time window to look back (default: 24 hours)
    
    Returns:
        ActivityResponse: List of recent activities for the service
    """
    service_name = service_name.lower()
    
    if service_name == 'radarr':
        activities = await get_radarr_activity()
    elif service_name == 'sonarr':
        activities = await get_sonarr_activity()
    elif service_name == 'lidarr':
        activities = await get_lidarr_activity()
    elif service_name == 'prowlarr':
        activities = await get_prowlarr_activity()
    else:
        raise HTTPException(status_code=404, detail=f"Service '{service_name}' not found")
    
    # Sort by timestamp (newest first)
    activities.sort(key=lambda x: x.timestamp, reverse=True)
    
    # Apply limit
    limited_activities = activities[:limit]
    
    return ActivityResponse(
        activities=limited_activities,
        total_count=len(activities),
        timestamp=datetime.now()
    )