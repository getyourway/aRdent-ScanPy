# aRdent ScanPad Python Library

A professional Python library for controlling aRdent ScanPad BLE HID devices. Provides high-level async API for key configuration, LED control, device settings, and OTA updates.

## 🚀 Quick Start

```python
from ardent_scanpad import ScanPad

# Simple usage with context manager
async with ScanPad() as device:
    # Configure a key to type "Hello"
    await device.keys.set_key_text("Hello", key_id=0)
    
    # Set up a hotkey (Ctrl+C)
    await device.keys.set_key_hotkey(
        HIDKeyCodes.C, HIDModifiers.LEFT_CTRL, key_id=1
    )
    
    # Configure media key
    await device.keys.set_key_media(ConsumerCodes.VOLUME_UP, key_id=2)
    
    # Save configuration to device
    await device.keys.save_config()
```

## 📦 Installation

```bash
pip install ardent-scanpad
```

### Development Installation

```bash
git clone https://github.com/ardentsolutions/ardent-scanpad-python
cd ardent-scanpad-python
pip install -e ".[dev]"
```

## 🔧 Requirements

- Python 3.8+
- `bleak` for BLE communication
- aRdent ScanPad device with firmware v1.0+

## 📖 Documentation

### Key Configuration

#### Simple Text Configuration
```python
# Configure key to type UTF-8 text
await device.keys.set_key_text("Hello World!", key_id=0)

# Configure with delay
await device.keys.set_key_text("Slow typing", key_id=1, delay=500)
```

#### Keyboard Shortcuts
```python
from ardent_scanpad import HIDKeyCodes, HIDModifiers

# Ctrl+C
await device.keys.set_key_hotkey(
    HIDKeyCodes.C, HIDModifiers.LEFT_CTRL, key_id=2
)

# Ctrl+Shift+Z
await device.keys.set_key_hotkey(
    HIDKeyCodes.Z, 
    HIDModifiers.LEFT_CTRL | HIDModifiers.LEFT_SHIFT, 
    key_id=3
)
```

#### Media Controls
```python
from ardent_scanpad import ConsumerCodes

# Volume controls
await device.keys.set_key_media(ConsumerCodes.VOLUME_UP, key_id=4)
await device.keys.set_key_media(ConsumerCodes.VOLUME_DOWN, key_id=5)
await device.keys.set_key_media(ConsumerCodes.MUTE, key_id=6)

# Media playback
await device.keys.set_key_media(ConsumerCodes.PLAY_PAUSE, key_id=7)
```

#### Custom Sequences
```python
# Create complex action sequence
actions = [
    device.keys.create_text_action("Dear "),
    device.keys.create_hid_action(HIDKeyCodes.TAB),
    device.keys.create_text_action(","),
    device.keys.create_hid_action(HIDKeyCodes.ENTER, delay=100),
    device.keys.create_text_action("Best regards")
]

await device.keys.set_key_sequence(actions, key_id=8)
```

### Key Management

```python
# Get key configuration
config = await device.keys.get_key_config(key_id=0)
print(f"Key has {config['action_count']} actions")

# Enable/disable keys
await device.keys.set_key_enabled(key_id=0, enabled=False)
await device.keys.set_key_enabled(key_id=0, enabled=True)

# Clear key configuration
await device.keys.clear_key(key_id=0)

# Get all configurations
all_configs = await device.keys.get_all_configs()
print(f"Total configured keys: {len(all_configs)}")

# Factory reset
await device.keys.factory_reset()
```

### Batch Operations

```python
# Configure multiple keys at once
configs = {
    0: [device.keys.create_text_action("A")],
    1: [device.keys.create_text_action("B")],
    2: [device.keys.create_hid_action(HIDKeyCodes.ENTER)],
    3: [device.keys.create_consumer_action(ConsumerCodes.VOLUME_UP)]
}

await device.keys.set_multiple_keys(configs)
```

### Configuration Backup/Restore

```python
# Backup current configuration
backup = await device.backup_config()

# Restore from backup
await device.restore_config(backup)
```

## 🗂️ Key Layout

The aRdent ScanPad has 20 configurable inputs:

### Matrix Keys (0-15)
4×4 grid layout:
```
[ 0] [ 1] [ 2] [ 3]    [1] [2] [3] [A]
[ 4] [ 5] [ 6] [ 7]    [4] [5] [6] [B]  
[ 8] [ 9] [10] [11]    [7] [8] [9] [C]
[12] [13] [14] [15]    [←] [0] [→] [D]
```

### Button Actions (16-19)
- `16`: Scan Trigger Double-Press (GPIO13)
- `17`: Scan Trigger Long-Press (GPIO13)
- `18`: Power Button Single-Press (GPIO6)
- `19`: Power Button Double-Press (GPIO6, reserved for shutdown)

## 🔗 Constants and Enums

### KeyIDs
```python
from ardent_scanpad import KeyIDs

# Matrix keys
KeyIDs.MATRIX_0_0  # Key [0,0] - typically "1"
KeyIDs.MATRIX_0_1  # Key [0,1] - typically "2"
# ... etc

# Button actions  
KeyIDs.SCAN_TRIGGER_DOUBLE  # 16
KeyIDs.POWER_SINGLE         # 18

# Collections
KeyIDs.ALL_MATRIX   # [0-15]
KeyIDs.ALL_BUTTONS  # [16-19]
KeyIDs.ALL_KEYS     # [0-19]
```

### HID Key Codes
```python
from ardent_scanpad import HIDKeyCodes

HIDKeyCodes.A         # 0x04
HIDKeyCodes.ENTER     # 0x28
HIDKeyCodes.SPACE     # 0x2C
HIDKeyCodes.F1        # 0x3A
# ... full HID keyboard support
```

### Consumer Controls
```python
from ardent_scanpad import ConsumerCodes

ConsumerCodes.VOLUME_UP    # 0x00E9
ConsumerCodes.PLAY_PAUSE   # 0x00CD
ConsumerCodes.NEXT_TRACK   # 0x00B5
# ... media controls
```

## 🛠️ Advanced Usage

### Connection Management
```python
# Manual connection control
device = ScanPad(auto_reconnect=True, timeout=30.0)
await device.connect()

# Work with device
await device.keys.set_key_text("Test", key_id=0)

# Disconnect when done
await device.disconnect()
```

### Error Handling
```python
from ardent_scanpad import (
    ScanPadError, ConnectionError, ConfigurationError, 
    TimeoutError, DeviceNotFoundError
)

try:
    async with ScanPad() as device:
        await device.keys.set_key_text("Hello", key_id=0)
except DeviceNotFoundError:
    print("ScanPad device not found - check if it's powered on")
except ConnectionError as e:
    print(f"Connection failed: {e}")
except ConfigurationError as e:
    print(f"Configuration error: {e}")
```

### Custom Logging
```python
import logging

# Enable debug logging
logging.getLogger('ardent_scanpad').setLevel(logging.DEBUG)

# Or disable logging
logging.getLogger('ardent_scanpad').setLevel(logging.ERROR)
```

## 🧪 Examples

See the `examples/` directory for complete usage examples:

- `basic_usage.py` - Simple key configuration
- `advanced_sequences.py` - Complex action sequences  
- `batch_operations.py` - Multiple key configuration
- `error_handling.py` - Robust error handling
- `backup_restore.py` - Configuration management

## 🔧 Development

### Running Tests
```bash
pytest tests/ -v
pytest tests/ --cov=ardent_scanpad --cov-report=html
```

### Code Formatting
```bash
black ardent_scanpad/
flake8 ardent_scanpad/
mypy ardent_scanpad/
```

## 📋 Changelog

### v1.0.0 (2025-01-24)
- Initial release
- Complete key configuration API
- BLE connection management with auto-reconnection
- Async context manager support
- Comprehensive error handling
- Configuration backup/restore
- Batch operations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📧 Email: support@ardentsolutions.com
- 📖 Documentation: https://docs.ardentsolutions.com/scanpad
- 🐛 Bug Reports: [GitHub Issues](https://github.com/ardentsolutions/ardent-scanpad-python/issues)

## ⚡ Performance Notes

- BLE operations are async and non-blocking
- Batch operations reduce BLE overhead
- Auto-reconnection handles connection drops
- Configuration caching minimizes device queries
- UTF-8 text is optimized for single characters (1 action = 1 character)

---

**Made with ❤️ by aRdent Solutions**