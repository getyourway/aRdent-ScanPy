# 📋 JSON Configuration Examples

This directory contains all JSON configuration examples for the aRdent ScanPad device. These JSON files can be used for:
- 📱 **Bluetooth configuration** - Send configurations directly via BLE
- 📷 **QR code generation** - Create scannable QR codes for device setup
- 🎮 **Interactive editing** - Use the interactive JSON creator/editor

## 📁 Directory Structure

```
json/
├── templates/              # Basic templates for each configuration type
│   ├── keyboard_config.json    # KISS keyboard configuration template
│   └── device_batch.json       # KISS device commands template
├── keyboard-configs/       # Example keyboard configurations
│   ├── simple_partial.json     # Simple numpad configuration
│   ├── multilingual_text.json  # International characters support
│   ├── function_keys.json      # Function key mappings
│   └── complete_example.json   # Full keyboard with all features
└── device-commands/        # Example device command batches
    ├── initial_setup.json       # Initial device setup sequence
    ├── simple_setup.json        # Basic configuration
    ├── demo_sequence.json       # Demo with LED and buzzer
    └── warehouse_lighting.json  # Industrial use case
```

## 🎯 KISS Format

All JSON files use the **KISS (Keep It Simple, Stupid)** format for maximum simplicity:

### Keyboard Configuration
```json
{
  "type": "keyboard_configuration",
  "metadata": {
    "name": "My Keyboard",
    "version": "1.0"
  },
  "keys": {
    "0": [{"type": "text", "value": "1"}],
    "1": [{"type": "text", "value": "2"}],
    "15": [{"type": "hid", "keycode": 40}],
    "18": [{"type": "text", "value": "PWR"}]
  }
}
```

**Key IDs:**
- `0-15`: Matrix keys (4x4 grid)
- `16`: Scan trigger double press (GPIO13)
- `17`: Scan trigger long press (GPIO13)
- `18`: Power button single press (GPIO6)
- `19`: Power button double press (GPIO6)

### Device Commands
```json
{
  "type": "device_batch",
  "metadata": {
    "name": "Setup Commands"
  },
  "commands": {
    "led_1_on": {},
    "buzzer_success": {},
    "orientation_landscape_right": {"value": 1}
  }
}
```

## 🚀 Usage Examples

### Using with Bluetooth
```python
from ardent_scanpad import ScanPad
import json

# Load configuration
with open("json/keyboard-configs/simple_partial.json") as f:
    config = json.load(f)

# Send via Bluetooth
scanpad = await ScanPad.connect_to_first_available()
await scanpad.keys.apply_json_configuration(config)
```

### Generating QR Codes
```python
from ardent_scanpad.qr_generators import KeyboardConfigGenerator

generator = KeyboardConfigGenerator()
qr_codes = generator.from_json_file("json/keyboard-configs/simple_partial.json")
for qr in qr_codes:
    qr.save_to_file("output.png")
```

### Interactive Editing
```bash
# Run the interactive JSON creator/editor
python examples/json/interactive_json.py
```

## 📝 Creating New Configurations

1. Start with a template from `templates/`
2. Modify using the interactive editor or any text editor
3. Test with the simulator or real device
4. Save to appropriate subdirectory

## 🔗 See Also

- [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) - Complete JSON format documentation
- [Interactive Examples](../) - Bluetooth, QR code, and Lua examples