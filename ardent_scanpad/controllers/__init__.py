"""
Controller modules for aRdent ScanPad library

Clean unified architecture with two domains:
- KeyConfigurationController: Key and button configuration (config_commands characteristic)
- PeripheralController: All hardware control (device_commands characteristic)
  - LED control via .led sub-controller
  - Buzzer control via .buzzer sub-controller  
  - Device settings (orientation, language, auto-shutdown)
  - OTA updates via .ota sub-controller
"""