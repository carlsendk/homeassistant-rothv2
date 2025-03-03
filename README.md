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

### HACS Custom Repository

If the integration is not yet available in the default HACS store, you can add it as a custom repository:

1. Make sure you have [HACS](https://hacs.xyz/) installed
2. Go to HACS → Integrations
3. Click on the three dots in the upper right corner
4. Select "Custom repositories"
5. Enter the URL of this repository: `https://github.com/yourusername/homeassistant-rothv2`
6. Select "Integration" as the category
7. Click "ADD"
8. Find "Roth Touchline V2" in the list of integrations
9. Click "DOWNLOAD"
10. Restart Home Assistant

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

## Custom Services

This integration provides the following services:

### refresh_devices

Refreshes all Roth Touchline devices connected to the controller or a specific device.

Parameters:
- `device_id` (optional): The device ID for a specific Roth Touchline device to refresh

Example:
```yaml
service: rothv2.refresh_devices
```

### set_week_program

Sets a specific week program for a Roth Touchline device.

Parameters:
- `device_id` (required): The device ID for the Roth Touchline thermostat
- `program` (required): The program number (0-3)

Example:
```yaml
service: rothv2.set_week_program
data:
  device_id: device.roth_touchline_thermostat
  program: 1
```

## Troubleshooting

- Make sure your Roth Touchline controller is accessible on your network
- Check that you have the correct IP address or hostname
- Check Home Assistant logs for any error messages related to "rothv2"

## Development

### Setup Development Environment

1. Clone this repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment: `source venv/bin/activate` (Linux/macOS) or `venv\Scripts\activate` (Windows)
4. Install requirements: `pip install -r requirements_dev.txt`

### Testing

Run tests with:
```bash
pytest
```

### Linting

Run linting with:
```bash
pre-commit run --all-files
```

### Submitting Changes

1. Fork this repository
2. Create a new branch: `git checkout -b my-feature-branch`
3. Make your changes
4. Run tests and linting
5. Create a pull request

## Dependencies

This integration uses the `pytouchline_extended` Python library to communicate with the Roth Touchline controller.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Based on the original [Touchline integration](https://github.com/home-assistant/core/tree/dev/homeassistant/components/touchline) for Home Assistant
- Uses the `pytouchline_extended` Python library 