import logging
import aiohttp
from datetime import timedelta
from urllib.parse import quote
from typing import Any, Dict, Optional
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .const import DEFAULT_SCAN_INTERVAL, API_BASE_URL

_LOGGER = logging.getLogger(__name__)

class GreenThinxCoordinator(DataUpdateCoordinator):
    """Coordinator for fetching GreenThinx sensor data."""
    
    def __init__(self, hass, sensor_id: str) -> None:
        super().__init__(
            hass,
            logger=_LOGGER,
            name="GreenThinx CE",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.sensor_id = sensor_id
        self._session: Optional[aiohttp.ClientSession] = None
        self._readings_cache: Dict[str, Dict[str, Any]] = {}

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session for connection reuse."""
        if self._session is None:
            self._session = aiohttp.ClientSession()
        return self._session

    async def _async_update_data(self) -> Dict[str, Any]:
        """Fetch data from GreenThinx API.
        
        Raises:
            UpdateFailed: If the API request fails or returns invalid data.
        """
        # Properly encode sensor_id to prevent URL injection attacks
        encoded_sensor_id = quote(self.sensor_id, safe='')
        url = f"{API_BASE_URL}?sensor={encoded_sensor_id}"

        session = await self._get_session()
        try:
            async with session.get(
                url,
                headers={"Accept": "application/json"},
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                resp.raise_for_status()
                data = await resp.json()
                # Update readings cache for efficient lookup
                self._update_readings_cache(data.get("readings", []))
                return data
        except aiohttp.ClientError as err:
            _LOGGER.error(f"GreenThinx API error: {err}")
            raise
        except ValueError as err:
            _LOGGER.error(f"GreenThinx API returned invalid JSON: {err}")
            raise

    def _update_readings_cache(self, readings: list) -> None:
        """Cache readings by channel for O(1) lookup performance.
        
        Args:
            readings: List of reading dictionaries with 'channel' keys.
        """
        self._readings_cache = {
            str(reading.get("channel")): reading
            for reading in readings
            if reading.get("channel") is not None
        }

    def get_reading_by_channel(self, channel: str) -> Optional[Dict[str, Any]]:
        """Get a reading by channel number (cached for performance).
        
        Args:
            channel: The channel number as string or int.
            
        Returns:
            The reading dictionary or None if not found.
        """
        return self._readings_cache.get(str(channel))

    async def async_shutdown(self) -> None:
        """Clean up resources."""
        if self._session:
            await self._session.close()
