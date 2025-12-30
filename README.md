# GreenThinx Community Edition (CE)

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

Custom Component for Home Assistant to integrate GreenThinx Soil Sensors.

## Description

The **GreenThinx Community Edition** integration allows you to monitor soil moisture and temperature at various depths using your GreenThinx hardware. It provides real-time data, configurable soil profiles, and aggregated root zone status to help you optimize your irrigation.

### Key Features
*   **Per-Depth Monitoring**: Moisture (%) and Temperature (°C) sensors for each available depth channel (e.g., 10cm, 20cm, 30cm...).
*   **Soil Profiles**: Configure specific soil types (e.g., Sandy Loam, Clay, Potting Soil) to automatically apply correct moisture thresholds.
*   **Root Zone Status**: A smart "Root Zone" sensor that aggregates data from a configurable depth range to tell you if your plants are "Optimal", "Too dry", or "Too wet".
*   **Dynamic Configuration**: Change soil type and root zone depth settings on-the-fly via the Integration Options.

## Installation

### Option 1: HACS (Recommended)
1.  Open **HACS** in Home Assistant.
2.  Go to **Integrations** > **Current Repositories** (top right menu).
3.  Add this repository URL.
4.  Search for **GreenThinx Community Edition** and install it.
5.  Restart Home Assistant.

### Option 2: Manual Installation
1.  Download the `greenthinx_ce` folder from this repository.
2.  Copy the `greenthinx_ce` folder into your Home Assistant `custom_components` directory.
3.  Restart Home Assistant.

## Configuration

1.  Go to **Settings** > **Devices & Services**.
2.  Click **Add Integration** and search for **GreenThinx Community Edition**.
3.  Enter your **Sensor ID** (found on your device).
4.  Select your **Soil Type** from the list (e.g., `sandy loam`, `potting soil`).

## Usage & Options

### Entities
Once added, the integration will create the following entities (where `X` is the depth channel, e.g., 1 for 10cm):

*   `sensor.greenthinx_depth_X_moisture`: Moisture percentage.
*   `sensor.greenthinx_depth_X_temperature`: Soil temperature.
*   `sensor.greenthinx_depth_X_soil_status`: Status for that specific depth ("Too dry", "Optimal", "Too wet").
*   `sensor.greenthinx_root_zone_soil_status`: Aggregated status for the configured root zone.

### Changing Settings
You can adjust the Soil Type and Root Zone definition at any time:
1.  Go to **Settings** > **Devices & Services** > **GreenThinx CE**.
2.  Click **Configure**.
3.  Update:
    *   **Soil Type**: Updates thresholds for all sensors.
    *   **Root Zone Start (cm)**: Top depth of your plant's roots (default: 10).
    *   **Root Zone End (cm)**: Bottom depth of your plant's roots (default: 30).

### Root Zone Logic
The **Root Zone Soil Status** sensor looks at all probe readings between the *Start* and *End* depths committed in the Options.
*   It reports **Too dry** if *any* sensor in the zone is too dry.
*   It reports **Too wet** if *any* sensor in the zone is too wet (and none are dry).
*   Otherwise, it reports **Optimal**.

## Supported Soil Types
*   Clay
*   Light Clay
*   Silty Clay
*   Silty Loam
*   Sandy Loam
*   Loamy Sand
*   Sand
*   Potting Soil
*   ... and more.

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
