from homeassistant import config_entries
import voluptuous as vol
from typing import Any, Dict, Optional

DOMAIN = "greenthinx_ce"

SOIL_TYPES = [
    "clay",
    "light clay",
    "silty clay",
    "silty loam",
    "sandy loam",
    "loamy sand",
    "sand",
    "silty clay (topsoil)",
    "silty clay (subsoil)",
    "heavy clay",
    "potting soil",
]

# Constants for validation
MIN_SENSOR_ID_LENGTH = 1
MAX_SENSOR_ID_LENGTH = 64
MIN_ROOT_ZONE_CM = 0
MAX_ROOT_ZONE_CM = 1000


class GreenThinxCEConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for GreenThinx Community Edition."""
    
    VERSION = 1

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> "GreenThinxCEOptionsFlowHandler":
        """Return options flow handler."""
        return GreenThinxCEOptionsFlowHandler(config_entry)

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Handle user-initiated config flow."""
        if user_input is not None:
            await self.async_set_unique_id(user_input["sensor_id"])
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=f"GreenThinx CE Sensor {user_input['sensor_id']}",
                data={
                    "sensor_id": user_input["sensor_id"],
                    "soil_type": user_input["soil_type"],
                },
            )

        schema = vol.Schema(
            {
                vol.Required("sensor_id"): vol.All(
                    str,
                    vol.Length(
                        min=MIN_SENSOR_ID_LENGTH,
                        max=MAX_SENSOR_ID_LENGTH,
                        msg="Sensor ID must be between 1 and 64 characters",
                    ),
                ),
                vol.Required("soil_type"): vol.In(SOIL_TYPES),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
        )


class GreenThinxCEOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for GreenThinx Community Edition."""
    
    def __init__(self, entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self._entry = entry

    async def async_step_init(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Handle options step."""
        if user_input is not None:
            # Validate that start_cm < end_cm
            if user_input["root_zone_start_cm"] >= user_input["root_zone_end_cm"]:
                return self.async_show_form(
                    step_id="init",
                    data_schema=self._get_schema(),
                    errors={"base": "invalid_root_zone"},
                    description_placeholders={
                        "error_msg": "Root zone start must be less than end"
                    },
                )

            # Reload the config entry so sensors immediately use new settings
            self.hass.async_create_task(
                self.hass.config_entries.async_reload(self._entry.entry_id)
            )

            return self.async_create_entry(
                title="",
                data={
                    "soil_type": user_input["soil_type"],
                    "root_zone_start_cm": user_input["root_zone_start_cm"],
                    "root_zone_end_cm": user_input["root_zone_end_cm"],
                },
            )

        return self.async_show_form(
            step_id="init",
            data_schema=self._get_schema(),
        )

    def _get_schema(self) -> vol.Schema:
        """Get the options schema with current values."""
        current_soil_type = self._entry.options.get(
            "soil_type",
            self._entry.data.get("soil_type"),
        )

        root_zone_start_cm = self._entry.options.get("root_zone_start_cm", 10)
        root_zone_end_cm = self._entry.options.get("root_zone_end_cm", 30)

        return vol.Schema(
            {
                vol.Required(
                    "soil_type",
                    default=current_soil_type,
                ): vol.In(SOIL_TYPES),
                vol.Required(
                    "root_zone_start_cm",
                    default=root_zone_start_cm,
                ): vol.All(
                    vol.Coerce(int),
                    vol.Range(
                        min=MIN_ROOT_ZONE_CM,
                        max=MAX_ROOT_ZONE_CM,
                        msg="Root zone start must be between 0 and 1000 cm",
                    ),
                ),
                vol.Required(
                    "root_zone_end_cm",
                    default=root_zone_end_cm,
                ): vol.All(
                    vol.Coerce(int),
                    vol.Range(
                        min=MIN_ROOT_ZONE_CM,
                        max=MAX_ROOT_ZONE_CM,
                        msg="Root zone end must be between 0 and 1000 cm",
                    ),
                ),
            }
        )
