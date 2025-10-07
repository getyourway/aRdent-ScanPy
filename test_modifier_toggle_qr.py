#!/usr/bin/env python3
"""
Test script for MODIFIER_TOGGLE QR code generation (Mecalux feature)

Tests:
1. Create modifier toggle action
2. Generate QR FULL config with modifier toggle
3. Verify binary format
"""

import sys
from pathlib import Path

# Add library to path
lib_path = Path(__file__).parent
sys.path.insert(0, str(lib_path))

# Direct imports to avoid aiohttp dependency
from ardent_scanpad.qr_generators.keyboard_config import KeyboardConfigGenerator
from ardent_scanpad.utils import constants

def main():
    print("=" * 60)
    print("Testing MODIFIER_TOGGLE QR Code Generation (Mecalux Feature)")
    print("=" * 60)

    # Create generator
    generator = KeyboardConfigGenerator()

    # Test 1: Create modifier toggle action
    print("\n[Test 1] Creating modifier toggle action...")
    try:
        shift_toggle = generator.create_modifier_toggle_action(
            modifier_mask=0x02,  # Left Shift
            delay=10
        )
        print(f"✅ Shift toggle action: {shift_toggle}")
        assert shift_toggle['type'] == 4  # MODIFIER_TOGGLE
        assert shift_toggle['mask'] == 0x02
        assert shift_toggle['value'] == 0  # Reserved
        print("✅ Test 1 passed: Modifier toggle action created")
    except Exception as e:
        print(f"❌ Test 1 failed: {e}")
        return 1

    # Test 2: Create keyboard config with modifier toggle
    print("\n[Test 2] Creating keyboard config with modifier toggles...")
    try:
        config = {
            # Key 0: Shift toggle
            0: [generator.create_modifier_toggle_action(0x02)],  # Left Shift

            # Key 1: Ctrl toggle
            1: [generator.create_modifier_toggle_action(0x01)],  # Left Ctrl

            # Key 2: Alt toggle
            2: [generator.create_modifier_toggle_action(0x04)],  # Left Alt

            # Key 3: Multi-action with HID after modifier toggle
            3: [
                generator.create_modifier_toggle_action(0x02),  # Shift ON
                generator.create_hid_action(constants.HIDKeyCodes.A),     # Send 'A' (becomes 'A' uppercase)
                generator.create_modifier_toggle_action(0x02),  # Shift OFF
            ],

            # Key 4-9: Normal text
            4: [generator.create_text_action("4")],
            5: [generator.create_text_action("5")],
            6: [generator.create_text_action("6")],
            7: [generator.create_text_action("7")],
            8: [generator.create_text_action("8")],
            9: [generator.create_text_action("9")],
        }

        print(f"✅ Keyboard config created with {len(config)} keys")
        print("✅ Test 2 passed: Config with modifier toggles created")
    except Exception as e:
        print(f"❌ Test 2 failed: {e}")
        return 1

    # Test 3: Generate QR FULL
    print("\n[Test 3] Generating QR FULL with modifier toggles...")
    try:
        qr_command = generator.create_full_keyboard_config(config, compression_level=6)

        print(f"✅ QR Command: {qr_command}")
        print(f"   Type: {qr_command.command_type}")
        print(f"   Description: {qr_command.description}")
        print(f"   QR Data Length: {len(qr_command.command_data)} chars")
        print(f"   Metadata:")
        for key, value in qr_command.metadata.items():
            if key != 'b64_data':  # Skip huge base64 string
                print(f"      {key}: {value}")

        # Verify metadata
        assert qr_command.metadata['keys_configured'] == len(config)
        assert qr_command.metadata['qr_format'] == 'FULL'
        assert 'b64_data' in qr_command.metadata

        print("✅ Test 3 passed: QR FULL generated successfully")
    except Exception as e:
        print(f"❌ Test 3 failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    # Test 4: Show QR data prefix (first 100 chars)
    print("\n[Test 4] Verifying QR data format...")
    try:
        qr_data = qr_command.command_data
        print(f"QR Data Prefix: {qr_data[:100]}...")

        # Should start with $FULL:
        assert qr_data.startswith("$FULL:"), "QR data should start with $FULL:"
        assert qr_data.endswith("$"), "QR data should end with $"

        print("✅ Test 4 passed: QR data format correct")
    except Exception as e:
        print(f"❌ Test 4 failed: {e}")
        return 1

    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)
    print("\nUsage Example:")
    print("-" * 60)
    print("from ardent_scanpad.qr_generators.keyboard_config import KeyboardConfigGenerator")
    print("")
    print("gen = KeyboardConfigGenerator()")
    print("")
    print("# Create shift toggle action")
    print("shift_toggle = gen.create_modifier_toggle_action(0x02)  # Left Shift")
    print("")
    print("# Use in keyboard config")
    print("config = {")
    print("    0: [shift_toggle],  # Key 0 = Shift toggle")
    print("    1: [gen.create_text_action('A')]")
    print("}")
    print("")
    print("# Generate QR")
    print("qr = gen.create_full_keyboard_config(config)")
    print("qr.save('modifier_toggle_config.png')")
    print("-" * 60)

    return 0

if __name__ == "__main__":
    sys.exit(main())
