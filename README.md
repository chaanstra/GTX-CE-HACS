# GreenThinx Community Edition (CE)

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

Custom Component for Home Assistant to integrate GreenThinx Soil Sensors.

## Description

The **GreenThinx Community Edition** integration allows you to monitor soil moisture and temperature at various depths using your GreenThinx hardware. It provides real-time data, configurable soil profiles, and intelligent aggregation of sensor data to help you optimize plant health.

### Key Features

*   **Per-Depth Monitoring**: Moisture (%) and Temperature (°C) sensors for each available depth channel (e.g., 10cm, 20cm, 30cm...).
*   **Soil Profiles**: Configure specific soil types (e.g., Sandy Loam, Clay, Potting Soil) to automatically apply correct moisture thresholds.
*   **Root Zone Status**: A smart "Root Zone" sensor that aggregates data from a configurable depth range to tell you if your plants are "Optimal", "Too dry", or "Too wet".
*   **Dynamic Configuration**: Change soil type and root zone depth settings on-the-fly via the Integration Options.
*   **Real-time Updates**: Live sensor readings updated automatically from your GreenThinx device.

## Requirements

- **Home Assistant**: Version 2023.10 or later
- **Python**: 3.11 or later (automatically provided by Home Assistant)
- **GreenThinx Hardware**: A compatible GreenThinx soil sensor device
- **Network Access**: Device must be reachable on your home network

### Supported Hardware

- GreenThinx Soil Sensor (all versions with multi-depth capability)
- 2, 3, or more simultaneous depth measurements supported

## Installation

### Option 1: HACS (Recommended)

1.  Open **HACS** in Home Assistant.
2.  Go to **Integrations** > **Current Repositories** (top right menu).
3.  Add this repository URL: `https://github.com/chaanstra/GTX-CE-HACS`
4.  Search for **GreenThinx Community Edition** and install it.
5.  Restart Home Assistant.

### Option 2: Manual Installation

1.  Download the `greenthinx_ce` folder from this repository.
2.  Copy the `greenthinx_ce` folder into your Home Assistant `custom_components` directory.
3.  Restart Home Assistant.

## Configuration

### Initial Setup

1.  Go to **Settings** > **Devices & Services**.
2.  Click **Add Integration** and search for **GreenThinx Community Edition**.
3.  Enter your **Sensor ID** (found on your device or in your GreenThinx app).
4.  Select your **Soil Type** from the list (e.g., `sandy loam`, `potting soil`).
5.  Click **Submit**.

### Configuration Options

After installation, you can modify settings at any time:

1.  Go to **Settings** > **Devices & Services** > **GreenThinx CE**.
2.  Click **Configure** (gear icon).
3.  Update:
    *   **Soil Type**: Changes moisture thresholds for all sensors.
    *   **Root Zone Start (cm)**: Top depth of your plant's roots (default: 10).
    *   **Root Zone End (cm)**: Bottom depth of your plant's roots (default: 30).
    *   **Polling Interval (seconds)**: How often to fetch data (default: 300s / 5 minutes).

## Usage & Entities

### Available Sensors

Once added, the integration will create the following entities (where `X` is the depth channel, e.g., 1 for 10cm):

| Entity | Type | Description |
|--------|------|-------------|
| `sensor.greenthinx_depth_X_moisture` | Sensor | Moisture percentage at depth X |
| `sensor.greenthinx_depth_X_temperature` | Sensor | Soil temperature (°C) at depth X |
| `sensor.greenthinx_depth_X_soil_status` | Sensor | Status at depth X ("Too dry", "Optimal", "Too wet") |
| `sensor.greenthinx_root_zone_soil_status` | Sensor | Aggregated status for configured root zone |

### Sensor Attributes

Each sensor includes additional attributes for advanced automations:

**Root Zone Sensor (`sensor.greenthinx_root_zone_soil_status`):**
- `soil_type`: Currently configured soil type
- `depths_used_cm`: List of depths included in root zone calculation
- `min_moisture`: Minimum moisture in root zone (%)
- `max_moisture`: Maximum moisture in root zone (%)
- `avg_moisture`: Average moisture in root zone (%)
- `avg_temperature`: Average temperature in root zone (°C)

**Depth Sensors:**
- `unit_of_measurement`: % for moisture, °C for temperature
- `device_class`: For proper Home Assistant UI representation

### Root Zone Logic

The **Root Zone Soil Status** sensor analyzes all probe readings between the configured *Start* and *End* depths:

*   **"Too dry"**: Reported if *any* sensor in the zone is below the dry threshold for the configured soil type.
*   **"Too wet"**: Reported if *any* sensor in the zone is above the wet threshold (and none are dry).
*   **"Optimal"**: Reported when all sensors are within acceptable range.

This ensures you're notified of any issues at any depth within your plant's root zone.

## Supported Soil Types

The integration includes moisture thresholds for the following soil types:

*   Clay
*   Light Clay
*   Silty Clay
*   Silty Loam
*   Sandy Loam
*   Loamy Sand
*   Sand
*   Potting Soil
*   Peat/Coco Mix
*   Custom (manual threshold configuration available)

Each soil type has preset dry/optimal/wet thresholds based on soil science research.

## Example Dashboard

A complete example dashboard configuration is available in [`lovelace_example.yaml`](lovelace_example.yaml).

<details>
<summary>Click to view Dashboard YAML</summary>

```yaml
title: GreenThinx Soil Monitoring
views:
  - title: Soil Overview
    path: soil
    icon: mdi:sprout
    theme: default
    badges: []
    cards:
      - type: markdown
        content: >
          ## 🌱 Soil overview 

          Real-time soil conditions based on root zone analysis. 


          🧱 **Soil type:**    {{
          state_attr('sensor.greenthinx_root_zone_soil_status', 'soil_type') |
          capitalize }}
      - type: entities
        show_header_toggle: false
        entities:
          - entity: sensor.greenthinx_root_zone_soil_status
            name: Root zone soil status
          - entity: sensor.greenthinx_root_zone_soil_status
            name: Root zone (depths used)
            attribute: depths_used_cm
      - type: markdown
        content: |
          ## 🧱 Soil profile  
          **Root zone: 10–30 cm**  
          Measurements are shown from top to bottom.
      - type: vertical-stack
        cards:
          - type: horizontal-stack
            cards:
              - type: entity
                entity: sensor.greenthinx_depth_1_soil_status
                name: 10 cm – Status
              - type: entity
                entity: sensor.greenthinx_depth_1_moisture
                name: Moisture (%)
          - type: horizontal-stack
            cards:
              - type: entity
                entity: sensor.greenthinx_depth_2_soil_status
                name: 20 cm – Status
              - type: entity
                entity: sensor.greenthinx_depth_2_moisture
                name: Moisture (%)
          - type: horizontal-stack
            cards:
              - type: entity
                entity: sensor.greenthinx_depth_3_soil_status
                name: 30 cm – Status
              - type: entity
                entity: sensor.greenthinx_depth_3_moisture
                name: Moisture (%)
      - type: markdown
        content: |
          ## ℹ️ Details
          Additional context used for soil analysis.
      - type: entities
        show_header_toggle: false
        entities:
          - entity: sensor.greenthinx_depth_1_temperature
            name: 10 cm – Temperature
          - entity: sensor.greenthinx_depth_2_temperature
            name: 20 cm – Temperature
          - entity: sensor.greenthinx_depth_3_temperature
            name: 30 cm – Temperature
      - type: markdown
        content: >
          ---

          **How this works**  

          • Each sensor measures soil moisture and temperature at a fixed
          depth  

          • The *root zone* defines which depths matter most for plant health  

          • The overall soil status is based on the *worst condition within the
          root zone*  


          Powered by **GreenThinx**
```

</details>

## Automations & Examples

### Example: Water Plant When Dry

```yaml
automation:
  - alias: "GreenThinx - Water Plant Alert"
    trigger:
      platform: state
      entity_id: sensor.greenthinx_root_zone_soil_status
      to: "Too dry"
    action:
      - service: notify.mobile_app_phone
        data:
          message: "🌱 Plant is too dry! Time to water."
```

### Example: Temperature Monitoring

```yaml
automation:
  - alias: "GreenThinx - High Temperature Alert"
    trigger:
      platform: numeric_state
      entity_id: sensor.greenthinx_depth_1_temperature
      above: 30
    action:
      - service: notify.persistent_notification
        data:
          message: "⚠️ Soil temperature is abnormally high (>30°C)"
```

## Troubleshooting

### Integration Not Appearing in Home Assistant

- **Verify Installation**: Check that the `greenthinx_ce` folder is correctly placed in `config/custom_components/`.
- **Restart Home Assistant**: Full restart required (not just reload).
- **Check Home Assistant Version**: Requires version 2023.10 or later.
- **Review Logs**: Check **Settings** > **System** > **Logs** for error messages.

### Sensor ID Not Recognized

- **Find Your Sensor ID**: 
  - Check the physical device (usually on a label or in the device settings).
  - Look in the GreenThinx mobile app under device information.
  - Try accessing the device's web interface directly (e.g., `http://greenthinx-device-ip`).
- **Verify Network Connectivity**: Ensure the device is on the same network and reachable.
- **Check Device Status**: Make sure the device is powered on and initialized.

### No Data or "Unavailable" State

- **Network Connectivity**: Verify the GreenThinx device is online and responding.
- **Polling Interval**: Check if data updates are too infrequent. Reduce polling interval in Integration Options.
- **Device Not Initialized**: Ensure the device has been properly set up and is collecting data.
- **Firewall/Network**: Check if any firewalls are blocking communication with the device.

### Incorrect Moisture Readings

- **Calibration**: The device may need recalibration. Refer to GreenThinx device documentation.
- **Soil Type Selection**: Verify the correct soil type is configured—wrong soil type leads to incorrect status calculations.
- **Sensor Placement**: Ensure probes are at the correct depths and fully inserted into soil.

### Connection Timeout Errors

- **Device Address**: Verify the Sensor ID is correct and the device is reachable.
- **Network Latency**: High latency may cause timeouts. Try increasing the polling interval.
- **Firewall Settings**: Ensure your Home Assistant instance can reach the device on the required port.

**Still Having Issues?** Check the Home Assistant logs for detailed error messages or create an issue on [GitHub](https://github.com/chaanstra/GTX-CE-HACS/issues).

## Advanced Configuration

### Custom Soil Type Thresholds

If your soil type is not in the list, you can contact the maintainer to add custom thresholds. Provide:
- Soil type name
- Dry threshold (%)
- Optimal min/max (%)
- Wet threshold (%)

### Integration with MQTT

If you want to expose GreenThinx data to MQTT:

```yaml
mqtt:
  publish:
    - topic: "home/garden/soil/moisture"
      payload: "{{ state_attr('sensor.greenthinx_root_zone_soil_status', 'avg_moisture') }}"
      retain: true
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes (`git commit -am 'Add feature'`)
4. Push to the branch (`git push origin feature/my-feature`)
5. Create a Pull Request

### Development Setup

```bash
# Clone the repo
git clone https://github.com/chaanstra/GTX-CE-HACS.git
cd GTX-CE-HACS

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Support & Contact

- **Issues**: [GitHub Issues](https://github.com/chaanstra/GTX-CE-HACS/issues)
- **Questions**: Please open a GitHub Discussion or issue with your question
- **Author**: [chaanstra](https://github.com/chaanstra)

## Acknowledgments

- [Home Assistant](https://www.home-assistant.io/) for the amazing smart home platform
- [HACS](https://hacs.xyz/) for simplifying custom component distribution
- GreenThinx for the excellent soil sensing hardware

---

**Disclaimer**: This is a community-maintained integration. It is not officially affiliated with GreenThinx. Use at your own risk.
