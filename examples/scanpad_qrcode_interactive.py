#!/usr/bin/env python3
"""
ScanPad QR Code Generator Interactive Terminal

Interactive QR code generation for aRdent ScanPad device configuration
and control commands. Create scannable QR codes for device setup without
requiring BLE connection.

Features:
- LED control QR codes
- Buzzer melody QR codes  
- Key configuration QR codes
- Device settings QR codes
- Batch QR code generation
- Save to PNG files
"""

import asyncio
import sys
import os
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import json

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ardent_scanpad.controllers.qr_generator import QRGeneratorController, QRCommand
from ardent_scanpad.utils.constants import (
    KeyIDs, KeyTypes, HIDKeyCodes, HIDModifiers, ConsumerCodes,
    DeviceOrientations, KeyboardLayouts, LEDs, BuzzerMelodies
)

try:
    import qrcode
    from PIL import Image
    QR_AVAILABLE = True
    QR_WARNING = ""
except ImportError:
    QR_AVAILABLE = False
    QR_WARNING = "\n⚠️  QR code dependencies not available. Install with: pip install qrcode[pil]\n"


class ScanPadQRInteractive:
    """Interactive terminal application for QR code generation"""
    
    def __init__(self):
        self.qr_generator = QRGeneratorController()
        self.generated_commands: List[QRCommand] = []
        self.output_dir = Path.cwd() / "scanpad_qr_codes"
        
    def run(self):
        """Main entry point"""
        self._print_header()
        
        if not QR_AVAILABLE:
            print(QR_WARNING)
            if not self._confirm("Continue anyway? QR codes won't be generated, only command strings"):
                return
        
        # Enter interactive mode
        self._interactive_menu()
        
        print("\n👋 QR Generator session ended!")
    
    def _print_header(self):
        """Print application header"""
        print("\n" + "="*70)
        print("📱 aRdent ScanPad QR Code Generator")
        print("Create scannable QR codes for device configuration")
        print("="*70)
        
        if QR_AVAILABLE:
            print("✅ QR code generation ready")
        else:
            print("❌ QR code generation not available (qrcode library missing)")
        
        print(f"📁 Output directory: {self.output_dir}")
        print()
    
    def _interactive_menu(self):
        """Main interactive menu"""
        while True:
            print("\n📋 QR CODE GENERATOR MENU:")
            print("="*50)
            print("🔵 LED CONTROL:")
            print("  1. LED On/Off commands")
            print("  2. LED blink commands") 
            print("  3. All LEDs off command")
            print()
            print("🔊 BUZZER CONTROL:")
            print("  4. Buzzer melody commands")
            print("  5. Custom beep command")
            print()
            print("⌨️  KEY CONFIGURATION:")
            print("  6. Single text key")
            print("  7. HID key command")
            print("  8. Multi-action key")
            print("  9. Numeric keypad preset")
            print()
            print("⚙️  DEVICE SETTINGS:")
            print("  10. Device orientation")
            print("  11. Keyboard language")
            print()
            print("📦 BATCH OPERATIONS:")
            print("  12. View generated commands")
            print("  13. Save all QR codes to files")
            print("  14. Clear command list")
            print("  15. Load config from JSON")
            print()
            print("❌ EXIT:")
            print("  16. Exit")
            
            choice = input("\nSelect option (1-16): ").strip()
            
            try:
                if choice == "1":
                    self._led_on_off_menu()
                elif choice == "2":
                    self._led_blink_menu()
                elif choice == "3":
                    self._all_leds_off()
                elif choice == "4":
                    self._buzzer_melody_menu()
                elif choice == "5":
                    self._buzzer_beep_menu()
                elif choice == "6":
                    self._text_key_menu()
                elif choice == "7":
                    self._hid_key_menu()
                elif choice == "8":
                    self._multi_action_key_menu()
                elif choice == "9":
                    self._numeric_keypad_preset()
                elif choice == "10":
                    self._orientation_menu()
                elif choice == "11":
                    self._language_menu()
                elif choice == "12":
                    self._view_commands()
                elif choice == "13":
                    self._save_all_qr_codes()
                elif choice == "14":
                    self._clear_commands()
                elif choice == "15":
                    self._load_config_json()
                elif choice == "16":
                    break
                else:
                    print("❌ Invalid choice. Please select 1-16.")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
                input("Press Enter to continue...")
    
    # ========================================
    # LED COMMANDS
    # ========================================
    
    def _led_on_off_menu(self):
        """LED on/off command generation"""
        print("\n💡 LED ON/OFF COMMAND")
        print("="*30)
        
        # Show available LEDs
        print("Available LEDs:")
        for led_id in LEDs.ALL:
            print(f"  {led_id}: {LEDs.NAMES[led_id]}")
        
        try:
            led_id = int(input(f"\nEnter LED ID (1-9): "))
            if led_id not in LEDs.ALL:
                print(f"❌ Invalid LED ID. Must be one of: {LEDs.ALL}")
                return
                
            state = input("Turn LED ON or OFF? (on/off): ").strip().lower()
            if state not in ['on', 'off']:
                print("❌ Invalid state. Enter 'on' or 'off'")
                return
            
            if state == 'on':
                command = self.qr_generator.create_led_on_command(led_id)
            else:
                command = self.qr_generator.create_led_off_command(led_id)
            
            self._add_and_preview_command(command)
            
        except ValueError:
            print("❌ Invalid LED ID. Must be a number.")
    
    def _led_blink_menu(self):
        """LED blink command generation"""
        print("\n💡 LED BLINK COMMAND")
        print("="*30)
        
        print("Available LEDs:")
        for led_id in LEDs.ALL:
            print(f"  {led_id}: {LEDs.NAMES[led_id]}")
        
        try:
            led_id = int(input(f"\nEnter LED ID (1-9): "))
            if led_id not in LEDs.ALL:
                print(f"❌ Invalid LED ID. Must be one of: {LEDs.ALL}")
                return
                
            freq = float(input("Enter blink frequency (0.1-20.0 Hz): "))
            if not (0.1 <= freq <= 20.0):
                print("❌ Frequency must be between 0.1 and 20.0 Hz")
                return
            
            # Create blink command (not implemented in controller yet, simulate)
            payload = bytes([led_id, int(freq) & 0xFF, (int(freq) >> 8) & 0xFF])
            command_data = f"$CMD:DEV:12{payload.hex().upper()}CMD$"
            
            command = QRCommand(
                command_data, "LED Control", 
                f"Blink {LEDs.NAMES[led_id]} at {freq}Hz",
                {'led_id': led_id, 'frequency': freq}
            )
            
            self._add_and_preview_command(command)
            
        except ValueError:
            print("❌ Invalid input. Please enter valid numbers.")
    
    def _all_leds_off(self):
        """All LEDs off command"""
        print("\n💡 ALL LEDS OFF COMMAND")
        print("="*30)
        
        command = self.qr_generator.create_all_leds_off_command()
        self._add_and_preview_command(command)
    
    # ========================================
    # BUZZER COMMANDS
    # ========================================
    
    def _buzzer_melody_menu(self):
        """Buzzer melody command generation"""
        print("\n🔊 BUZZER MELODY COMMAND")
        print("="*30)
        
        print("Available melodies:")
        melody_names = ['KEY', 'START', 'STOP', 'NOTIF_UP', 'NOTIF_DOWN', 
                       'CONFIRM', 'WARNING', 'ERROR', 'SUCCESS']
        
        for i, melody in enumerate(melody_names, 1):
            print(f"  {i}: {melody}")
        
        try:
            choice = int(input(f"\nSelect melody (1-{len(melody_names)}): "))
            if not (1 <= choice <= len(melody_names)):
                print(f"❌ Invalid choice. Must be 1-{len(melody_names)}")
                return
            
            melody_name = melody_names[choice - 1]
            command = self.qr_generator.create_buzzer_melody_command(melody_name)
            self._add_and_preview_command(command)
            
        except ValueError:
            print("❌ Invalid choice. Must be a number.")
    
    def _buzzer_beep_menu(self):
        """Custom buzzer beep command"""
        print("\n🔊 CUSTOM BEEP COMMAND")
        print("="*30)
        
        try:
            duration = int(input("Enter beep duration (50-5000 ms): "))
            if not (50 <= duration <= 5000):
                print("❌ Duration must be between 50 and 5000 ms")
                return
            
            # Create beep command (simulate - not in controller yet)
            duration_low = duration & 0xFF
            duration_high = (duration >> 8) & 0xFF
            payload = bytes([duration_low, duration_high])
            command_data = f"$CMD:DEV:20{payload.hex().upper()}CMD$"
            
            command = QRCommand(
                command_data, "Buzzer Control",
                f"Beep for {duration}ms",
                {'duration_ms': duration}
            )
            
            self._add_and_preview_command(command)
            
        except ValueError:
            print("❌ Invalid duration. Must be a number.")
    
    # ========================================
    # KEY CONFIGURATION
    # ========================================
    
    def _text_key_menu(self):
        """Single text key configuration"""
        print("\n⌨️  TEXT KEY CONFIGURATION")
        print("="*30)
        
        # Show available keys
        print("Available keys (first 8 for simplicity):")
        for i in range(8):
            key_name = KeyIDs.NAMES.get(i, f"Key {i}")
            print(f"  {i}: {key_name}")
        
        try:
            key_id = int(input("Enter key ID (0-7): "))
            if not (0 <= key_id <= 7):
                print("❌ Key ID must be 0-7")
                return
                
            text = input("Enter text to type (max 8 UTF-8 bytes): ")
            if len(text.encode('utf-8')) > 8:
                print("❌ Text too long (max 8 UTF-8 bytes)")
                return
            
            command = self.qr_generator.create_quick_text_key(key_id, text)
            self._add_and_preview_command(command)
            
        except ValueError:
            print("❌ Invalid key ID. Must be a number.")
    
    def _hid_key_menu(self):
        """HID key configuration"""
        print("\n⌨️  HID KEY CONFIGURATION")
        print("="*30)
        
        print("Common HID keys:")
        common_keys = {
            'ENTER': HIDKeyCodes.ENTER,
            'ESCAPE': HIDKeyCodes.ESCAPE,
            'SPACE': HIDKeyCodes.SPACE,
            'TAB': HIDKeyCodes.TAB,
            'F1': HIDKeyCodes.F1,
            'F2': HIDKeyCodes.F2,
            'A': HIDKeyCodes.A,
            'CTRL': HIDKeyCodes.CTRL
        }
        
        for name, code in common_keys.items():
            print(f"  {name}: 0x{code:02X}")
        
        try:
            key_id = int(input("\nEnter key ID (0-7): "))
            if not (0 <= key_id <= 7):
                print("❌ Key ID must be 0-7")
                return
            
            keycode_input = input("Enter HID keycode (hex like 0x28 or decimal): ")
            if keycode_input.startswith('0x'):
                keycode = int(keycode_input, 16)
            else:
                keycode = int(keycode_input)
            
            if not (0 <= keycode <= 255):
                print("❌ Keycode must be 0-255")
                return
            
            modifier = int(input("Enter modifier (0 for none, or hex/decimal): ") or "0")
            if not (0 <= modifier <= 255):
                print("❌ Modifier must be 0-255") 
                return
            
            command = self.qr_generator.create_quick_hid_key(key_id, keycode, modifier)
            self._add_and_preview_command(command)
            
        except ValueError:
            print("❌ Invalid input. Please enter valid numbers.")
    
    def _multi_action_key_menu(self):
        """Multi-action key configuration"""
        print("\n⌨️  MULTI-ACTION KEY CONFIGURATION")
        print("="*30)
        
        try:
            key_id = int(input("Enter key ID (0-7): "))
            if not (0 <= key_id <= 7):
                print("❌ Key ID must be 0-7")
                return
            
            actions = []
            print("\nAdd actions (max 10). Enter empty line to finish:")
            
            for i in range(10):
                print(f"\nAction {i+1}:")
                print("  1. Text action")
                print("  2. HID action") 
                print("  3. Finish")
                
                choice = input("Select action type (1-3): ").strip()
                
                if choice == "3" or not choice:
                    break
                elif choice == "1":
                    text = input("Enter text: ")
                    if len(text.encode('utf-8')) <= 8:
                        action = self.qr_generator.create_text_action(text)
                        actions.append(action)
                        print(f"✅ Added text action: {text}")
                    else:
                        print("❌ Text too long, skipping")
                elif choice == "2":
                    try:
                        keycode = int(input("Enter HID keycode: "))
                        modifier = int(input("Enter modifier (0 for none): ") or "0")
                        action = self.qr_generator.create_hid_action(keycode, modifier)
                        actions.append(action)
                        print(f"✅ Added HID action: 0x{keycode:02X}")
                    except ValueError:
                        print("❌ Invalid keycode/modifier, skipping")
                else:
                    print("❌ Invalid choice")
            
            if actions:
                command = self.qr_generator.create_key_config_command(key_id, actions)
                self._add_and_preview_command(command)
            else:
                print("❌ No actions added")
                
        except ValueError:
            print("❌ Invalid key ID. Must be a number.")
    
    def _numeric_keypad_preset(self):
        """Generate numeric keypad configuration"""
        print("\n⌨️  NUMERIC KEYPAD PRESET")
        print("="*30)
        print("This will generate QR codes for keys 0-15 as numeric keypad")
        
        if not self._confirm("Generate numeric keypad preset?"):
            return
        
        # Generate numeric keypad layout
        keypad_layout = {
            0: "1", 1: "2", 2: "3", 3: "A",
            4: "4", 5: "5", 6: "6", 7: "B", 
            8: "7", 9: "8", 10: "9", 11: "C",
            12: "←", 13: "0", 14: "→", 15: "D"
        }
        
        count = 0
        for key_id, text in keypad_layout.items():
            try:
                if text in ["←", "→"]:
                    # Arrow keys as HID
                    keycode = HIDKeyCodes.LEFT_ARROW if text == "←" else HIDKeyCodes.RIGHT_ARROW
                    command = self.qr_generator.create_quick_hid_key(key_id, keycode)
                else:
                    # Text keys
                    command = self.qr_generator.create_quick_text_key(key_id, text)
                    
                self.generated_commands.append(command)
                count += 1
            except Exception as e:
                print(f"❌ Failed to create command for key {key_id}: {e}")
        
        print(f"✅ Generated {count} numeric keypad commands")
    
    # ========================================
    # DEVICE SETTINGS
    # ========================================
    
    def _orientation_menu(self):
        """Device orientation command"""
        print("\n⚙️  DEVICE ORIENTATION")
        print("="*30)
        
        orientations = {
            0: "Portrait",
            1: "Landscape", 
            2: "Reverse Portrait",
            3: "Reverse Landscape"
        }
        
        print("Available orientations:")
        for id, name in orientations.items():
            print(f"  {id}: {name}")
        
        try:
            orientation = int(input("Select orientation (0-3): "))
            if orientation not in orientations:
                print("❌ Invalid orientation. Must be 0-3")
                return
            
            command = self.qr_generator.create_orientation_command(orientation)
            self._add_and_preview_command(command)
            
        except ValueError:
            print("❌ Invalid orientation. Must be a number.")
    
    def _language_menu(self):
        """Keyboard language command"""
        print("\n⚙️  KEYBOARD LANGUAGE")
        print("="*30)
        
        # Show common layouts
        common_layouts = {
            'US QWERTY': KeyboardLayouts.WIN_US_QWERTY,
            'French AZERTY': KeyboardLayouts.WIN_FR_AZERTY,
            'German QWERTZ': KeyboardLayouts.WIN_DE_QWERTZ,
        }
        
        print("Common layouts:")
        for name, layout_id in common_layouts.items():
            print(f"  {name}: 0x{layout_id:04X}")
        
        try:
            layout_input = input("\nEnter layout ID (hex like 0x1110 or decimal): ")
            if layout_input.startswith('0x'):
                layout_id = int(layout_input, 16)
            else:
                layout_id = int(layout_input)
            
            if not (0 <= layout_id <= 65535):
                print("❌ Layout ID must be 0-65535")
                return
            
            # Create language command (simulate - not fully in controller)
            payload = bytes([layout_id & 0xFF, (layout_id >> 8) & 0xFF])
            command_data = f"$CMD:DEV:42{payload.hex().upper()}CMD$"
            
            command = QRCommand(
                command_data, "Device Settings",
                f"Set keyboard layout: 0x{layout_id:04X}",
                {'layout_id': layout_id}
            )
            
            self._add_and_preview_command(command)
            
        except ValueError:
            print("❌ Invalid layout ID. Please enter a valid number.")
    
    # ========================================
    # UTILITY METHODS
    # ========================================
    
    def _add_and_preview_command(self, command: QRCommand):
        """Add command to list and preview it"""
        self.generated_commands.append(command)
        
        print(f"\n✅ COMMAND GENERATED:")
        print(f"   Type: {command.command_type}")
        print(f"   Description: {command.description}")
        print(f"   Command Data: {command.command_data}")
        
        if QR_AVAILABLE:
            save_now = input("\n💾 Save QR code to file now? (y/n): ").strip().lower()
            if save_now == 'y':
                self._save_single_qr_code(command)
    
    def _save_single_qr_code(self, command: QRCommand):
        """Save a single QR code to file"""
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename
            safe_desc = "".join(c for c in command.description if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_desc = safe_desc.replace(' ', '_')[:30]
            filename = f"qr_{safe_desc}.png"
            filepath = self.output_dir / filename
            
            if command.save(filepath):
                print(f"✅ QR code saved: {filepath}")
            else:
                print("❌ Failed to save QR code")
                
        except Exception as e:
            print(f"❌ Error saving QR code: {e}")
    
    def _view_commands(self):
        """View all generated commands"""
        print(f"\n📋 GENERATED COMMANDS ({len(self.generated_commands)} total):")
        print("="*60)
        
        if not self.generated_commands:
            print("No commands generated yet.")
            return
        
        for i, command in enumerate(self.generated_commands, 1):
            print(f"{i:2d}. {command.command_type}: {command.description}")
            print(f"    Command: {command.command_data}")
            print()
    
    def _save_all_qr_codes(self):
        """Save all generated QR codes to files"""
        if not self.generated_commands:
            print("❌ No commands to save")
            return
        
        if not QR_AVAILABLE:
            print("❌ QR code generation not available")
            return
        
        print(f"\n💾 SAVING {len(self.generated_commands)} QR CODES")
        print("="*50)
        
        try:
            saved_files = self.qr_generator.save_multiple_qr_codes(
                self.generated_commands, self.output_dir
            )
            
            print(f"✅ Saved {len(saved_files)} QR codes to {self.output_dir}")
            
            if saved_files:
                print("\nSaved files:")
                for filepath in saved_files[:10]:  # Show first 10
                    print(f"  {Path(filepath).name}")
                if len(saved_files) > 10:
                    print(f"  ... and {len(saved_files) - 10} more")
                    
        except Exception as e:
            print(f"❌ Error saving QR codes: {e}")
    
    def _clear_commands(self):
        """Clear all generated commands"""
        if not self.generated_commands:
            print("❌ No commands to clear")
            return
            
        if self._confirm(f"Clear all {len(self.generated_commands)} generated commands?"):
            self.generated_commands.clear()
            print("✅ All commands cleared")
    
    def _load_config_json(self):
        """Load configuration from JSON file"""
        print("\n📄 LOAD CONFIG FROM JSON")
        print("="*30)
        
        filename = input("Enter JSON filename: ").strip()
        if not filename:
            return
            
        try:
            with open(filename, 'r') as f:
                config = json.load(f)
            
            # Simple config format expected:
            # {"commands": [{"type": "led_on", "led_id": 1}, ...]}
            
            commands_config = config.get('commands', []) 
            count = 0
            
            for cmd_config in commands_config:
                cmd_type = cmd_config.get('type', '')
                
                try:
                    if cmd_type == 'led_on':
                        led_id = cmd_config['led_id']
                        command = self.qr_generator.create_led_on_command(led_id)
                        self.generated_commands.append(command)
                        count += 1
                    elif cmd_type == 'led_off':
                        led_id = cmd_config['led_id']
                        command = self.qr_generator.create_led_off_command(led_id)
                        self.generated_commands.append(command)
                        count += 1
                    elif cmd_type == 'buzzer_melody':
                        melody = cmd_config['melody']
                        command = self.qr_generator.create_buzzer_melody_command(melody)
                        self.generated_commands.append(command)
                        count += 1
                    elif cmd_type == 'text_key':
                        key_id = cmd_config['key_id']
                        text = cmd_config['text']
                        command = self.qr_generator.create_quick_text_key(key_id, text)
                        self.generated_commands.append(command)
                        count += 1
                    # Add more command types as needed
                        
                except Exception as e:
                    print(f"❌ Failed to create command {cmd_type}: {e}")
            
            print(f"✅ Loaded {count} commands from {filename}")
            
        except FileNotFoundError:
            print(f"❌ File not found: {filename}")
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON in file: {filename}")
        except Exception as e:
            print(f"❌ Error loading config: {e}")
    
    def _confirm(self, message: str) -> bool:
        """Ask for user confirmation"""
        response = input(f"{message} (y/n): ").strip().lower()
        return response in ['y', 'yes']


def main():
    """Main entry point"""
    try:
        app = ScanPadQRInteractive()
        app.run()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()