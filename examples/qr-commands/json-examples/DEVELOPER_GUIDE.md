# 📋 aRdent ScanPad JSON Configuration Guide for Developers

## 🎯 Overview

This guide explains how to structure JSON configurations for the aRdent ScanPad device. These JSON files can be used to:
- Generate QR codes for device configuration without Bluetooth
- Send configurations via Bluetooth using the Python/Flutter libraries
- Save and share device configurations

## 📁 JSON Structure Types

### 1. Keyboard Configuration (`type: "keyboard_configuration"`)

Used to configure the 16 matrix keys (4x4 grid) and external buttons.

#### Basic Structure:
```json
{
  "type": "keyboard_configuration",
  "metadata": {
    "name": "Configuration Name",
    "description": "What this config does",
    "version": "1.0"
  },
  "matrix_keys": {
    "0": [{"type": "text", "value": "1", "delay": 10}],
    "1": [{"type": "text", "value": "2", "delay": 10}],
    // ... keys 2-15
  },
  "external_buttons": {
    "power_button": [{"type": "text", "value": "PWR"}],
    "scan_trigger": [{"type": "hid", "keycode": 40}]
  }
}
```

### 2. Device Batch Commands (`type: "device_batch"`)

Used to send multiple device control commands in sequence.

#### Basic Structure:
```json
{
  "type": "device_batch",
  "metadata": {
    "name": "Setup Sequence",
    "description": "Initial device setup"
  },
  "commands": [
    {"domain": "led_control", "action": "led_on", "parameters": {"led_id": 1}},
    {"domain": "buzzer_control", "action": "play_melody", "parameters": {"melody": "START"}}
  ]
}
```

## 🔑 Key Configuration Details

### Matrix Key Layout
```
[0]  [1]  [2]  [3]
[4]  [5]  [6]  [7]
[8]  [9]  [10] [11]
[12] [13] [14] [15]
```

### External Button Mapping
```json
"external_buttons": {
  "scan_trigger_double": [...],    // ID 16 - GPIO13 double press
  "scan_trigger_long": [...],      // ID 17 - GPIO13 long press (1.5s)
  "power_button": [...],           // ID 18 - GPIO6 single press
  "power_button_double": [...]     // ID 19 - GPIO6 double press (shutdown)
}
```

**Physical buttons:**
- **Scan Trigger** (GPIO13): Used for barcode scanner activation
  - Double press: Configurable actions (ID 16)
  - Long press: Configurable actions (ID 17) 
- **Power Button** (GPIO6): Main power control
  - Single press: Configurable actions (ID 18)
  - Double press: System shutdown (ID 19, usually not user-configurable)

### Action Types

Each key can have up to **10 actions** that execute sequentially.

#### 1. Text Action
```json
{
  "type": "text",
  "value": "Hello World",  // UTF-8, max 8 bytes per action
  "delay": 10              // Milliseconds delay after action
}
```

#### 2. HID Keyboard Action
```json
{
  "type": "hid",
  "keycode": 40,     // HID keycode (40 = ENTER)
  "modifier": 2,     // Modifier keys (2 = SHIFT)
  "delay": 20
}
```

Common keycodes:
- `40` = ENTER
- `43` = TAB
- `44` = SPACE
- `42` = BACKSPACE
- `41` = ESCAPE

Modifiers (can be combined):
- `0` = None
- `1` = CTRL
- `2` = SHIFT
- `4` = ALT
- `8` = GUI/Windows
- `3` = CTRL+SHIFT

#### 3. Consumer Control Action
```json
{
  "type": "consumer",
  "consumer_code": 205,  // Media keys (205 = Play/Pause)
  "delay": 10
}
```

## 🎮 Device Commands Reference

### LED Control
```json
{"domain": "led_control", "action": "led_on", "parameters": {"led_id": 1}}
{"domain": "led_control", "action": "led_off", "parameters": {"led_id": 1}}
{"domain": "led_control", "action": "all_leds_off", "parameters": {}}
```
LED IDs: 1-5 (individual LEDs), 6-9 (RGB modes)

### Buzzer Control
```json
{"domain": "buzzer_control", "action": "play_melody", "parameters": {"melody": "SUCCESS"}}
{"domain": "buzzer_control", "action": "beep", "parameters": {"duration_ms": 200}}
```
Melodies: SUCCESS, ERROR, WARNING, START, STOP, KEY, CONNECTION, NOTIFICATION

### Device Settings
```json
{"domain": "device_settings", "action": "set_orientation", "parameters": {"orientation": 1}}
{"domain": "device_settings", "action": "set_language", "parameters": {"language": "0x040C"}}
```
Orientations: 0=Portrait, 1=Landscape Right, 2=Inverted, 3=Landscape Left
Languages: 0x0409=English US, 0x040C=French, 0x0407=German

## 💻 Integration Examples

### Python - Generate QR Code
```python
from ardent_scanpad.qr_generators import KeyboardConfigGenerator

# From JSON file
generator = KeyboardConfigGenerator()
qr_codes = generator.from_json_file("my_config.json")

# Save QR to file
for qr in qr_codes:
    qr.save_to_file("output.png")
```

### Python - Send via Bluetooth ✅
```python
from ardent_scanpad import ScanPad
import json

async def configure_from_json():
    # Connect to device
    scanpad = await ScanPad.connect_to_first_available()
    
    # Load JSON configuration
    with open("my_config.json") as f:
        config = json.load(f)
    
    # Send configuration via Bluetooth
    success = await scanpad.keys.apply_json_configuration(config)
    if success:
        print("✅ Configuration applied successfully!")
    else:
        print("❌ Configuration failed")
    
    await scanpad.disconnect()

# Example with validation
async def configure_with_validation():
    scanpad = await ScanPad.connect_to_first_available()
    
    config = {
        "type": "keyboard_configuration",
        "metadata": {"name": "My Custom Keypad"},
        "matrix_keys": {
            "0": [{"type": "text", "value": "1", "delay": 10}],
            "1": [{"type": "text", "value": "2", "delay": 10}],
            "15": [{"type": "hid", "keycode": 40, "modifier": 0}]  # ENTER
        },
        "external_buttons": {
            "power_button": [{"type": "text", "value": "PWR"}],
            "scan_trigger_double": [{"type": "hid", "keycode": 43}]  # TAB
        }
    }
    
    success = await scanpad.keys.apply_json_configuration(config)
    print(f"Configuration result: {success}")
    
    await scanpad.disconnect()
```

### JavaScript/TypeScript - Web Application
```typescript
import { ScanPadWeb } from 'ardent-scanpad';

// Load configuration
const config = {
  type: "keyboard_configuration",
  matrix_keys: {
    "0": [{type: "text", value: "1"}],
    // ...
  }
};

// Generate QR code
const qrDataUrl = await ScanPadWeb.generateQRCode(config);

// Or send via Web Bluetooth
const device = await ScanPadWeb.connect();
await device.applyConfiguration(config);
```

## 📝 Validation Rules

### Keyboard Configuration
- **Max actions per key**: 10
- **Max text bytes per action**: 8 (UTF-8)
- **Valid key IDs**: 0-15 for matrix, "power_button", "scan_trigger" for external
- **Delay range**: 0-65535 milliseconds

### Device Batch Commands
- **Max commands per batch**: 50
- **Required fields**: type, commands
- **Each command needs**: domain, action, parameters

## 🔧 Best Practices

1. **Always include metadata** - Helps track configurations
2. **Use descriptive names** - Makes configs self-documenting
3. **Test incrementally** - Start with simple configs, add complexity
4. **Version your configs** - Track changes over time
5. **Validate before deployment** - Use library validation methods

## 📚 Complete Examples

### Simple Numeric Keypad
```json
{
  "type": "keyboard_configuration",
  "metadata": {
    "name": "Simple Numpad",
    "version": "1.0"
  },
  "matrix_keys": {
    "0": [{"type": "text", "value": "1"}],
    "1": [{"type": "text", "value": "2"}],
    "2": [{"type": "text", "value": "3"}],
    "3": [{"type": "text", "value": "4"}],
    "4": [{"type": "text", "value": "5"}],
    "5": [{"type": "text", "value": "6"}],
    "6": [{"type": "text", "value": "7"}],
    "7": [{"type": "text", "value": "8"}],
    "8": [{"type": "text", "value": "9"}],
    "9": [{"type": "text", "value": "0"}],
    "10": [{"type": "text", "value": "."}],
    "11": [{"type": "hid", "keycode": 40}]
  }
}
```

### Initial Device Setup
```json
{
  "type": "device_batch",
  "metadata": {
    "name": "Initial Setup",
    "version": "1.0"
  },
  "commands": [
    {"domain": "device_settings", "action": "set_orientation", "parameters": {"orientation": 1}},
    {"domain": "device_settings", "action": "set_language", "parameters": {"language": "0x040C"}},
    {"domain": "led_control", "action": "all_leds_off", "parameters": {}},
    {"domain": "led_control", "action": "led_on", "parameters": {"led_id": 1}},
    {"domain": "buzzer_control", "action": "play_melody", "parameters": {"melody": "START"}}
  ]
}
```

## 🆘 Need Help?

- Check `TEMPLATE_keyboard_config.json` for all keyboard options
- Check `TEMPLATE_device_batch.json` for all device commands
- Test with the interactive tool: `python scanpad_qrcode_interactive.py`
- Validate JSON with online validators before use

## 📌 Quick Reference Card

| Action Type | Description | Max Size/Range |
|------------|-------------|----------------|
| text | Types UTF-8 text | 8 bytes per action |
| hid | Keyboard key press | Keycode 0-255 |
| consumer | Media/control keys | Code 0-65535 |

| Domain | Actions Available |
|--------|------------------|
| led_control | led_on, led_off, all_leds_off, rgb_color |
| buzzer_control | play_melody, beep, set_volume, stop |
| device_settings | set_orientation, set_language, set_auto_shutdown |
| lua_management | deploy_script, clear_script |
| power_management | get_battery_level, enable_low_power_mode |

---

**Version**: 2.0  
**Last Updated**: January 2025  
**Compatible With**: aRdent ScanPad firmware v1.0+