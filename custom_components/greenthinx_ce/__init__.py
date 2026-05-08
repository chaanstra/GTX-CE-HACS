"""GreenThinx Community Edition integration for Home Assistant."""

from typing import Any
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN
from .coordinator import GreenThinxCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up GreenThinx Community Edition from a config entry.
    
    Args:
        hass: Home Assistant instance.
        entry: Config entry.
        
    Returns:
        True if successful.
    """
    coordinator = GreenThinxCoordinator(
        hass,
        entry.data["sensor_id"]
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(
        entry, ["sensor"]
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry and clean up resources.
    
    Args:
        hass: Home Assistant instance.
        entry: Config entry.
        
    Returns:
        True if successful.
    """
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry, ["sensor"]
    )

    if unload_ok:
        coordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.async_shutdown()

    return unload_ok
