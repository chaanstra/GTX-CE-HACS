from homeassistant import config_entries
import voluptuous as vol

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


class GreenThinxCEConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    @staticmethod
    def async_get_options_flow(config_entry):
        return GreenThinxCEOptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input=None):
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
                vol.Required("sensor_id"): str,
                vol.Required("soil_type"): vol.In(SOIL_TYPES),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
        )


class GreenThinxCEOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, entry: config_entries.ConfigEntry) -> None:
        self._entry = entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
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

        current_soil_type = self._entry.options.get(
            "soil_type",
            self._entry.data.get("soil_type"),
        )

        root_zone_start_cm = self._entry.options.get("root_zone_start_cm", 10)
        root_zone_end_cm = self._entry.options.get("root_zone_end_cm", 30)

        schema = vol.Schema(
            {
                vol.Required(
                    "soil_type",
                    default=current_soil_type,
                ): vol.In(SOIL_TYPES),
                vol.Required(
                    "root_zone_start_cm",
                    default=root_zone_start_cm,
                ): vol.Coerce(int),
                vol.Required(
                    "root_zone_end_cm",
                    default=root_zone_end_cm,
                ): vol.Coerce(int),
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
        )
