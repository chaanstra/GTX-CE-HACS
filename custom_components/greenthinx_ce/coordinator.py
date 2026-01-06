import logging
import aiohttp
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .const import DEFAULT_SCAN_INTERVAL, API_BASE_URL

_LOGGER = logging.getLogger(__name__)

class GreenThinxCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, sensor_id):
        super().__init__(
            hass,
            logger=_LOGGER,
            name="GreenThinx CE",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.sensor_id = sensor_id

    async def _async_update_data(self):
        url = f"{API_BASE_URL}?sensor={self.sensor_id}"

        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                headers={"Accept": "application/json"},
                timeout=10
            ) as resp:
                resp.raise_for_status()
                return await resp.json()
