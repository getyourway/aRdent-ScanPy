#!/usr/bin/env python3
"""
Test script for Configurator Support API
Demonstrates all the new methods for building configurator applications
"""

import json
import sys
import os

# Add library to path
sys.path.insert(0, '.')

def test_configurator_api():
    """Test all configurator support methods without BLE connection"""
    
    print("🔧 Testing aRdent ScanPad Configurator API")
    print("=" * 50)
    
    # Test without actual device connection - just capability discovery
    from ardent_scanpad.controllers.keys import KeyController
    from ardent_scanpad.controllers.device import UnifiedDeviceController
    
    # Create controllers with mock connection (None)
    keys = KeyController(None)
    device = UnifiedDeviceController(None)
    
    print("\n📋 1. SUPPORTED LANGUAGES/LAYOUTS")
    print("-" * 35)
    
    languages = keys.get_supported_languages()
    print(f"Total layouts: {languages['total_count']}")
    print(f"Categories: {', '.join(languages['categories'])}")
    print(f"Default: 0x{languages['default']:04X}")
    
    print("\nAvailable layouts:")
    for category in languages['categories']:
        layouts_in_category = [
            layout for layout in languages['layouts'].values() 
            if layout['category'] == category
        ]
        print(f"\n  {category}:")
        for layout in layouts_in_category[:3]:  # Show first 3
            print(f"    • {layout['name']} ({layout['hex_id']})")
        if len(layouts_in_category) > 3:
            print(f"    ... and {len(layouts_in_category) - 3} more")
    
    print("\n🎯 2. SUPPORTED ACTION TYPES")
    print("-" * 30)
    
    actions = keys.get_supported_action_types()
    print(f"Action types: {len(actions['action_types'])}")
    
    for type_id, info in actions['action_types'].items():
        print(f"\n  {info['name']} (ID: {type_id}):")
        print(f"    • {info['description']}")
        if info.get('examples'):
            if isinstance(info['examples'][0], dict):
                print(f"    • Example: {info['examples'][0]}")
            else:
                print(f"    • Examples: {', '.join(info['examples'][:3])}")
        
        capabilities = []
        if info.get('supports_delay'): capabilities.append("delay")
        if info.get('supports_modifiers'): capabilities.append("modifiers")
        if capabilities:
            print(f"    • Supports: {', '.join(capabilities)}")
    
    print(f"\nConstraints:")
    for key, value in actions['constraints'].items():
        print(f"  • {key}: {value}")
    
    print("\n💡 3. SUPPORTED LED COLORS")
    print("-" * 27)
    
    leds = device.get_supported_led_colors()
    print(f"Total LEDs: {leds['total_count']}")
    print(f"Individual LEDs: {len(leds['individual_leds'])}")
    print(f"RGB color modes: {len(leds['rgb_colors'])}")
    
    print("\nIndividual LEDs:")
    for led_id, info in leds['individual_leds'].items():
        print(f"  • ID {led_id}: {info['name']}")
    
    print("\nRGB Color Modes:")
    for led_id, info in leds['rgb_colors'].items():
        color_name = info['name'].replace('RGB ', '').replace(' Mode', '')
        print(f"  • ID {led_id}: {color_name}")
    
    print(f"\nCapabilities:")
    caps = leds['capabilities']
    print(f"  • Blink frequency: {caps['min_blink_frequency']}-{caps['max_blink_frequency']} Hz")
    print(f"  • All off command: {caps['supports_all_off']}")
    
    print("\n📱 4. SUPPORTED ORIENTATIONS")
    print("-" * 29)
    
    orientations = device.get_supported_orientations()
    print(f"Total orientations: {orientations['total_count']}")
    print(f"Default: {orientations['default']}")
    
    for orient_id, info in orientations['orientations'].items():
        print(f"  • {info['icon']} {info['name']} ({orient_id}): {info['rotation_degrees']}°")
    
    print("\n🔊 5. SUPPORTED BUZZER MELODIES")
    print("-" * 33)
    
    buzzer = device.get_supported_buzzer_melodies()
    print(f"Total melodies: {buzzer['total_count']}")
    
    categories = buzzer['categories']
    for category, melody_ids in categories.items():
        print(f"\n  {category.title()}:")
        for melody_id in melody_ids:
            melody_info = buzzer['melodies'][melody_id]
            print(f"    • {melody_info['name']} (ID: {melody_id})")
    
    caps = buzzer['capabilities']
    print(f"\nCapabilities:")
    print(f"  • Custom beep: {caps['supports_custom_beep']}")
    print(f"  • Duration range: {caps['min_duration_ms']}-{caps['max_duration_ms']} ms")
    print(f"  • Volume range: {caps['volume_range'][0]}-{caps['volume_range'][1]}%")
    
    print("\n🏗️ 6. COMPLETE DEVICE CAPABILITIES")
    print("-" * 36)
    
    capabilities = device.get_device_capabilities()
    device_info = capabilities['device_info']
    
    print(f"Device: {device_info['name']} by {device_info['manufacturer']}")
    print(f"Type: {device_info['type']}")
    print(f"Matrix: {device_info['matrix_size']} ({device_info['total_keys']} total keys)")
    print(f"Connectivity: {', '.join(device_info['connectivity'])}")
    
    key_config = capabilities['key_configuration']
    print(f"\nKey Configuration:")
    print(f"  • Matrix keys: {key_config['matrix_keys']}")
    print(f"  • Button actions: {key_config['button_actions']}")
    print(f"  • Max actions per key: {key_config['max_actions_per_key']}")
    print(f"  • Action types: {', '.join(key_config['supported_action_types'])}")
    
    power = capabilities['power_management']['auto_shutdown']
    print(f"\nPower Management:")
    print(f"  • Auto shutdown: {power['configurable']}")
    print(f"  • Timeout range: {power['min_timeout_minutes']}-{power['max_timeout_minutes']} minutes")
    
    print("\n✅ CONFIGURATOR API TEST COMPLETED")
    print("\nThis API enables configurator applications to:")
    print("  • Populate language/layout dropdowns")
    print("  • Show available LED colors and capabilities")
    print("  • Display device orientation options") 
    print("  • List buzzer melodies for selection")
    print("  • Understand action types and constraints")
    print("  • Build comprehensive device configuration UIs")
    
    return True


def export_capabilities_json():
    """Export all capabilities to JSON for external configurator apps"""
    
    from ardent_scanpad.controllers.keys import KeyController
    from ardent_scanpad.controllers.device import UnifiedDeviceController
    
    # Create controllers with mock connection
    keys = KeyController(None)
    device = UnifiedDeviceController(None)
    
    # Gather all capabilities
    capabilities = {
        "api_version": "1.0",
        "generated_by": "aRdent ScanPad Python Library",
        "device_capabilities": device.get_device_capabilities(),
        "supported_languages": keys.get_supported_languages(),
        "supported_action_types": keys.get_supported_action_types(),
        "supported_orientations": device.get_supported_orientations(),
        "supported_led_colors": device.get_supported_led_colors(),
        "supported_buzzer_melodies": device.get_supported_buzzer_melodies()
    }
    
    # Export to JSON
    output_file = "scanpad_capabilities.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(capabilities, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Capabilities exported to: {output_file}")
    print(f"File size: {os.path.getsize(output_file)} bytes")
    print("This JSON can be used by external configurator applications")
    

if __name__ == "__main__":
    print(__doc__)
    
    try:
        # Test all configurator methods
        success = test_configurator_api()
        
        if success:
            # Export capabilities for external apps
            export_capabilities_json()
            
        print(f"\n🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)