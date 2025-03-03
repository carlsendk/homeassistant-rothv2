# Roth Touchline V2 Integration for Home Assistant

This is a custom integration for Home Assistant that allows you to control Roth Touchline floor heating controllers. This is an updated version of the [original Touchline integration](https://github.com/home-assistant/core/tree/dev/homeassistant/components/touchline) with improvements for modern Home Assistant.

## Features

- Configure the integration through the UI (Config Flows)
- Modern Home Assistant integration structure
- Supports all features of the original integration
- Improved error handling and connectivity
- Control multiple thermostats
- View current and target temperatures
- Set target temperatures
- Select operation modes (Normal, Night, Holiday, Program 1-3)

## Requirements

- A running Home Assistant installation
- Roth Touchline floor heating controller accessible on your network
- The controller needs to have a fixed IP address or hostname

## Installation

### HACS (Recommended)

1. Make sure you have [HACS](https://hacs.xyz/) installed
2. Go to HACS → Integrations → + Explore & Add Repositories
3. Search for "Roth Touchline"
4. Install the integration
5. Restart Home Assistant

### Manual Installation

1. Download or clone this repository
2. Copy the `custom_components/rothv2` directory to your Home Assistant `custom_components` directory
3. Restart Home Assistant

## Configuration

### Via UI (Recommended)

1. Go to Settings → Devices & Services
2. Click "+ Add Integration"
3. Search for "Roth Touchline V2"
4. Enter the IP address or hostname of your Roth Touchline controller
5. Click Submit

### Via configuration.yaml

```yaml
rothv2:
  host: 192.168.1.100  # Replace with your controller's IP address or hostname
```

## Troubleshooting

- Make sure your Roth Touchline controller is accessible on your network
- Check that you have the correct IP address or hostname
- Check Home Assistant logs for any error messages related to "rothv2"

## Dependencies

This integration uses the `pytouchline_extended` Python library to communicate with the Roth Touchline controller.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Based on the original [Touchline integration](https://github.com/home-assistant/core/tree/dev/homeassistant/components/touchline) for Home Assistant
- Uses the `pytouchline_extended` Python library 