#!/usr/bin/env python3
"""
Update device_commands_reference.json to add qr_supported field
"""

import json
from pathlib import Path

# Load the JSON file
json_file = Path(__file__).parent / "library" / "device_commands_reference.json"
with open(json_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# List of supported (domain, action) pairs from our DeviceCommandGenerator
supported_commands = {
    # LED Control
    ('led_control', 'led_on'),
    ('led_control', 'led_off'),
    ('led_control', 'led_blink'),
    ('led_control', 'led_stop_blink'),
    ('led_control', 'all_leds_off'),
    
    # Buzzer Control
    ('buzzer_control', 'play_melody'),
    ('buzzer_control', 'beep'),
    ('buzzer_control', 'set_volume'),
    
    # Device Settings
    ('device_settings', 'set_orientation'),
    ('device_settings', 'set_language'),
    ('device_settings', 'set_auto_shutdown'),
    
    # Power Management
    ('power_management', 'shutdown'),
    ('power_management', 'restart'),
    ('power_management', 'deep_sleep'),
    
    # Lua Management
    ('lua_management', 'clear_script'),
    ('lua_management', 'get_script_info'),
}

# Update each command with qr_supported field
for category in data['categories'].values():
    for param_group in category.get('parameters', {}).values():
        for func in param_group.get('functions', []):
            domain = func.get('domain', '')
            action = func.get('command', '')
            
            # Check if this command is supported for QR generation
            func['qr_supported'] = (domain, action) in supported_commands

# Save the updated JSON
with open(json_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"✅ Updated {json_file.name} with qr_supported field")

# Print statistics
total = 0
supported = 0
for category in data['categories'].values():
    for param_group in category.get('parameters', {}).values():
        for func in param_group.get('functions', []):
            total += 1
            if func.get('qr_supported', False):
                supported += 1

print(f"📊 Statistics: {supported}/{total} commands support QR generation ({supported*100//total}%)")