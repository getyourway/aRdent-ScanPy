"""
Controller modules for aRdent ScanPad library

Clean unified architecture with three controllers:
- KeyConfigurationController: Key and button configuration (config_commands characteristic)
- PeripheralController: All hardware control (device_commands characteristic)
  - LED control via .led sub-controller
  - Buzzer control via .buzzer sub-controller  
  - Device settings (orientation, language, auto-shutdown)
  - OTA updates via .ota sub-controller
- QRGeneratorController: QR code generation for device commands (no BLE required)
  - Creates scannable QR codes for all device commands
  - Supports LED, buzzer, key config, and device settings
  - Saves to PNG files for GUI applications
"""