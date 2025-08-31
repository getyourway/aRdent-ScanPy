# QR Generators - KISS API for aRdent ScanPad

Generate QR codes for device commands and keyboard configurations with a simple, maintainable API.

## Quick Start

### Simple Device Command (KISS Approach)

```python
from ardent_scanpad.qr_generators import DeviceCommandGenerator

# Create generator
generator = DeviceCommandGenerator()

# Generate QR code with one simple call
qr_commands = generator.from_simple_command(
    domain="led_control",
    action="led_on", 
    parameters={"led_id": 1}
)

# Get the QR image
qr_image = qr_commands[0].generate_qr_image()
qr_image.show()  # Display the QR code
```

### From JSON File

```python
# Load and generate from JSON file
qr_commands = generator.from_json_file("device_commands.json")
```

### Direct JSON (Type Auto-Detection)

```python
# Type field is optional - auto-detected!
json_data = {
    "domain": "buzzer_control",
    "action": "play_melody",
    "parameters": {"melody": "SUCCESS"}
}
qr_commands = generator.from_json(json_data)
```

## Supported Commands

### LED Control
- `led_on` - Turn LED on
- `led_off` - Turn LED off  
- `led_blink` - Blink LED with frequency
- `led_stop_blink` - Stop LED blinking
- `all_leds_off` - Turn all LEDs off

### Buzzer Control
- `play_melody` - Play predefined melody
- `beep` - Custom beep with duration/frequency
- `set_volume` - Set buzzer volume

### Device Settings
- `set_orientation` - Set screen orientation
- `set_language` - Set keyboard language
- `set_auto_shutdown` - Configure auto-shutdown timers

### Power Management
- `shutdown` - Shutdown device
- `restart` - Restart device
- `deep_sleep` - Enter deep sleep mode

### Lua Management
- `clear_script` - Clear Lua script
- `get_script_info` - Get script information

## Adding New Commands

Adding a new command is now KISS simple:

1. **Add the command builder method:**
```python
def _build_my_new_command(self, params: Dict) -> bytes:
    """Build MY_NEW_COMMAND"""
    value = params.get('value', 0)
    return bytes([Commands.MY_NEW_COMMAND, value])
```

2. **Register in the mapping table:**
```python
def _init_command_builders(self):
    return {
        # ... existing commands ...
        ('my_domain', 'my_action'): self._build_my_new_command,
    }
```

That's it! No need to modify `_build_binary_command()` anymore.

## Architecture Benefits

- **KISS**: Simple API - just 3 parameters
- **Maintainable**: Command mapping table instead of if/else blocks
- **Constants**: Uses Commands class constants instead of hardcoded IDs
- **Auto-detection**: Type field is optional
- **Extensible**: Easy to add new commands

## GUI Integration

Perfect for GUI applications:

```python
# From GUI form data
domain = form.get_domain()      # "led_control"
action = form.get_action()      # "led_blink" 
params = form.get_parameters()  # {"led_id": 1, "frequency": 2.0}

# Generate QR with one line
qr = generator.from_simple_command(domain, action, params)
```

## JSON Formats

### Single Command (Auto-detected)
```json
{
  "domain": "led_control",
  "action": "led_on",
  "parameters": {"led_id": 1}
}
```

### Batch Commands (Auto-detected)
```json
{
  "commands": [
    {"domain": "led_control", "action": "all_leds_off"},
    {"domain": "led_control", "action": "led_on", "parameters": {"led_id": 1}},
    {"domain": "buzzer_control", "action": "play_melody", "parameters": {"melody": "START"}}
  ]
}
```

### With Explicit Type (Optional)
```json
{
  "type": "single_command",
  "domain": "led_control",
  "action": "led_on",
  "parameters": {"led_id": 1}
}
```