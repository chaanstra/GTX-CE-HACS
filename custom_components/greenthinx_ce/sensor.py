from typing import Any, Dict, Optional, Tuple
from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import (
    EntityCategory,
    UnitOfTemperature,
    PERCENTAGE,
)
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN, SOIL_PROFILES


def _get_soil_type(entry) -> str:
    """Get current soil type from config or options."""
    return entry.options.get("soil_type", entry.data["soil_type"])


def _get_root_zone(entry) -> Tuple[int, int]:
    """Get current root zone configuration.
    
    Returns:
        Tuple of (start_cm, end_cm).
    """
    start_cm = int(entry.options.get("root_zone_start_cm", 10))
    end_cm = int(entry.options.get("root_zone_end_cm", 30))
    return start_cm, end_cm


def _channel_to_cm(channel) -> Optional[int]:
    """Convert reading['channel'] to depth in centimeters.

    GreenThinx CE convention:
    - channel 1 = 10 cm
    - channel 2 = 20 cm
    - channel 3 = 30 cm
    - etc.
    
    Args:
        channel: The channel number (string or int).
        
    Returns:
        Depth in centimeters or None if invalid.
    """
    try:
        return int(channel) * 10
    except (TypeError, ValueError):
        return None


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up GreenThinx sensors from config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    sensors = []

    # 1) Root-zone aggregated status (one per device)
    sensors.append(
        GreenThinxRootZoneSoilStatusSensor(coordinator, entry)
    )

    # 2) Per-depth sensors
    for reading in coordinator.data.get("readings", []):
        channel = reading["channel"]

        sensors.append(
            GreenThinxSoilSensor(coordinator, entry, channel, "moisture")
        )
        sensors.append(
            GreenThinxSoilSensor(coordinator, entry, channel, "temperature")
        )
        sensors.append(
            GreenThinxSoilStatusSensor(coordinator, entry, channel)
        )

    async_add_entities(sensors)


class _GreenThinxBase(CoordinatorEntity):
    """Base class for GreenThinx sensors."""
    
    def __init__(self, coordinator, entry) -> None:
        """Initialize base sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._sensor_id = entry.data["sensor_id"]
        # Cache soil type to avoid repeated dict lookups
        self._cached_soil_type: Optional[str] = None
        self._cached_profile: Optional[Dict[str, int]] = None

        self._device_info = DeviceInfo(
            identifiers={(DOMAIN, self._sensor_id)},
            name=f"GreenThinx CE Sensor {self._sensor_id}",
            manufacturer="GreenThinx",
            model="CE Soil Sensor",
        )

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return self._device_info

    def _get_soil_type_cached(self) -> str:
        """Get soil type with caching for performance."""
        current_soil_type = _get_soil_type(self._entry)
        # Invalidate cache if soil type changed
        if self._cached_soil_type != current_soil_type:
            self._cached_soil_type = current_soil_type
            self._cached_profile = SOIL_PROFILES.get(current_soil_type)
        return current_soil_type

    def _get_profile_cached(self) -> Optional[Dict[str, int]]:
        """Get soil profile with caching for performance."""
        self._get_soil_type_cached()  # Ensure cache is valid
        return self._cached_profile


class GreenThinxSoilSensor(_GreenThinxBase, SensorEntity):
    """Sensor for soil moisture and temperature at specific depths."""
    
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator, entry, channel: str, sensor_type: str) -> None:
        """Initialize soil sensor.
        
        Args:
            coordinator: Data coordinator.
            entry: Config entry.
            channel: Channel number.
            sensor_type: Either 'moisture' or 'temperature'.
        """
        super().__init__(coordinator, entry)
        self._channel = channel
        self._type = sensor_type

        self._attr_unique_id = f"{self._sensor_id}_{channel}_{sensor_type}"
        self._attr_name = f"GreenThinx Depth {channel} {sensor_type.capitalize()}"

        if sensor_type == "temperature":
            self._attr_device_class = SensorDeviceClass.TEMPERATURE
            self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        elif sensor_type == "moisture":
            self._attr_device_class = SensorDeviceClass.MOISTURE
            self._attr_native_unit_of_measurement = PERCENTAGE

    @property
    def native_value(self) -> Optional[float]:
        """Return the current sensor value using cached coordinator lookup."""
        reading = self.coordinator.get_reading_by_channel(self._channel)
        if reading is None:
            return None

        val = reading.get(self._type)
        if val is None:
            return None
            
        try:
            return float(val) if self._type in ("moisture", "temperature") else val
        except (TypeError, ValueError):
            return None


class GreenThinxSoilStatusSensor(_GreenThinxBase, SensorEntity):
    """Sensor for soil status at specific depth."""
    
    _attr_icon = "mdi:sprout"

    def __init__(self, coordinator, entry, channel: str) -> None:
        """Initialize soil status sensor."""
        super().__init__(coordinator, entry)
        self._channel = channel

        self._attr_unique_id = f"{self._sensor_id}_{channel}_soil_status"
        self._attr_name = f"GreenThinx Depth {channel} Soil Status"

    @property
    def native_value(self) -> Optional[str]:
        """Return soil status based on moisture reading."""
        profile = self._get_profile_cached()
        if not profile:
            return None

        reading = self.coordinator.get_reading_by_channel(self._channel)
        if reading is None:
            return None

        moisture_raw = reading.get("moisture")
        if moisture_raw is None:
            return None
            
        try:
            moisture = float(moisture_raw)
        except (TypeError, ValueError):
            return None

        if moisture < profile["min"]:
            return "Too dry"
        if moisture > profile["max"]:
            return "Too wet"
        return "Optimal"

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return extra state attributes."""
        soil_type = self._get_soil_type_cached()
        profile = self._get_profile_cached()
        
        if not profile:
            return {"soil_type": soil_type, "channel": self._channel}

        return {
            "soil_type": soil_type,
            "min_threshold": profile["min"],
            "max_threshold": profile["max"],
            "capacity": profile["capacity"],
            "channel": self._channel,
        }


class GreenThinxRootZoneSoilStatusSensor(_GreenThinxBase, SensorEntity):
    """Sensor for aggregated soil status across root zone."""
    
    _attr_icon = "mdi:layers-triple"

    def __init__(self, coordinator, entry) -> None:
        """Initialize root zone soil status sensor."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{self._sensor_id}_root_zone_soil_status"
        self._attr_name = "GreenThinx Root Zone Soil Status"

    @property
    def native_value(self) -> Optional[str]:
        """Return aggregated root zone status (worst-case wins)."""
        profile = self._get_profile_cached()
        if not profile:
            return None

        start_cm, end_cm = _get_root_zone(self._entry)
        if start_cm >= end_cm:
            return None

        statuses = []

        for reading in self.coordinator.data.get("readings", []):
            depth_cm = _channel_to_cm(reading.get("channel"))
            if depth_cm is None:
                continue

            if depth_cm < start_cm or depth_cm > end_cm:
                continue

            moisture_raw = reading.get("moisture")
            if moisture_raw is None:
                continue
                
            try:
                moisture = float(moisture_raw)
            except (TypeError, ValueError):
                continue

            if moisture < profile["min"]:
                statuses.append("Too dry")
            elif moisture > profile["max"]:
                statuses.append("Too wet")
            else:
                statuses.append("Optimal")

        if not statuses:
            return None

        # Worst-case wins inside root zone
        if "Too dry" in statuses:
            return "Too dry"
        if "Too wet" in statuses:
            return "Too wet"
        return "Optimal"

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return extra state attributes with root zone analysis."""
        soil_type = self._get_soil_type_cached()
        profile = self._get_profile_cached() or {}
        start_cm, end_cm = _get_root_zone(self._entry)

        used_depths = []
        for reading in self.coordinator.data.get("readings", []):
            depth_cm = _channel_to_cm(reading.get("channel"))
            if depth_cm is None:
                continue
            if start_cm <= depth_cm <= end_cm:
                used_depths.append(depth_cm)

        used_depths_sorted = sorted(set(used_depths))

        attrs = {
            "soil_type": soil_type,
            "root_zone_start_cm": start_cm,
            "root_zone_end_cm": end_cm,
            "depths_used_cm": used_depths_sorted,
        }

        if profile:
            attrs.update(
                {
                    "min_threshold": profile.get("min"),
                    "max_threshold": profile.get("max"),
                    "capacity": profile.get("capacity"),
                }
            )

        return attrs
