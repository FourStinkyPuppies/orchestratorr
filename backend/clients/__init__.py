"""
*arr API clients module.

Provides asynchronous HTTP clients for communicating with various *arr services.
"""

from .base import BaseArrClient
from .radarr import RadarrClient
from .sonarr import SonarrClient
from .lidarr import LidarrClient
from .prowlarr import ProwlarrClient

__all__ = ["BaseArrClient", "RadarrClient", "SonarrClient", "LidarrClient", "ProwlarrClient"]
