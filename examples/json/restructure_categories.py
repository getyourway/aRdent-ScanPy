#!/usr/bin/env python3
"""
Restructure device_commands_reference.json:
1. Flatten Device Settings structure
2. Reorganize Keyboard Language into subcategories
"""

import json
from pathlib import Path

# Load the JSON file
json_file = Path(__file__).parent / "library" / "device_commands_reference.json"
with open(json_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Get Device Settings content
device_settings = data['categories'].pop('Device Settings', {}).get('parameters', {})

# Create new structure
new_categories = {}

# Keep existing categories
new_categories['LED Control'] = data['categories']['LED Control']
new_categories['Buzzer Control'] = data['categories']['Buzzer Control']

# Flatten Device Settings
new_categories['Screen Orientation'] = device_settings.get('Screen Orientation', {})
new_categories['Auto Shutdown'] = device_settings.get('Auto Shutdown', {})
new_categories['Power Control'] = device_settings.get('Power Control', {})

# Reorganize Keyboard Language into subcategories
keyboard_lang = device_settings.get('Keyboard Language', {}).get('functions', [])

# Group keyboard languages by category
us_english = []
european = []
macos = []

for func in keyboard_lang:
    name = func.get('function', '')
    if 'US English' in name:
        us_english.append(func)
    elif 'macOS' in name:
        macos.append(func)
    else:
        european.append(func)

# Create Keyboard Language structure with subcategories
new_categories['Keyboard Language'] = {
    "parameters": {
        "US/UK English": {
            "functions": us_english,
            "description": "Standard English keyboard layouts"
        },
        "European Languages": {
            "functions": european, 
            "description": "European keyboard layouts (French, German, Spanish, etc.)"
        },
        "macOS Layouts": {
            "functions": macos,
            "description": "macOS-specific keyboard layouts"
        }
    }
}

# Keep Lua Management
new_categories['Lua Management'] = data['categories']['Lua Management']

# Update the data
data['categories'] = new_categories

# Save the updated JSON
with open(json_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("✅ Restructured device_commands_reference.json")
print("📊 New structure:")
for category in data['categories'].keys():
    print(f"   • {category}")
    if category == 'Keyboard Language':
        for subcat in data['categories'][category]['parameters'].keys():
            print(f"     - {subcat}")