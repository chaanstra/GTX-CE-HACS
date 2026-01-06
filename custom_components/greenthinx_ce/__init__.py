from .const import DOMAIN
from .coordinator import GreenThinxCoordinator

async def async_setup_entry(hass, entry):
    coordinator = GreenThinxCoordinator(
        hass,
        entry.data["sensor_id"]
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    # ✅ NIEUWE HA API
    await hass.config_entries.async_forward_entry_setups(
        entry, ["sensor"]
    )

    return True
