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
            print("  9. 🛠️  Complete Keyboard Builder (All 16 keys + multi-actions)")
            print("  20. Numeric keypad preset (legacy)")
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
                    self._complete_keyboard_builder()
                elif choice == "20":
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
        
        # Show matrix keys layout
        print("Matrix keys (4x4 layout):")
        print("  Row 0: [0] [1] [2] [3]")
        print("  Row 1: [4] [5] [6] [7]")
        print("  Row 2: [8] [9] [10] [11]")
        print("  Row 3: [12] [13] [14] [15]")
        
        try:
            key_id = int(input("Enter key ID (0-15): "))
            if not (0 <= key_id <= 15):
                print("❌ Key ID must be 0-15")
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
            key_id = int(input("\nEnter key ID (0-15): "))
            if not (0 <= key_id <= 15):
                print("❌ Key ID must be 0-15")
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
            key_id = int(input("Enter key ID (0-15): "))
            if not (0 <= key_id <= 15):
                print("❌ Key ID must be 0-15")
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
    
    def _complete_keyboard_builder(self):
        """Complete keyboard builder with all 16 keys and multi-actions support"""
        print("\n🛠️  COMPLETE KEYBOARD BUILDER")
        print("="*60)
        print("Configure all 16 matrix keys with multiple actions support")
        print("Supports full keyboard configuration with $FULL: QR format")
        print()
        
        config = {}
        
        while True:
            # Show keyboard matrix status
            self._display_keyboard_matrix(config)
            
            print("\n📋 CONFIGURATION OPTIONS:")
            print("1. 🔧 Configure single key (with multi-actions)")
            print("2. 🎹 Add standard layout (1-9, A-D, arrows)")
            print("3. 🔤 Add alphabetic layout (A-P)")
            print("4. 🔢 Add numeric layout (0-9)")
            print("5. 📋 View current configuration")
            print("6. 🗑️  Clear key configuration")
            print("7. 📦 Generate $FULL: QR Code")
            print("8. 💡 Help & Examples")
            print("0. ❌ Back to main menu")
            
            choice = input("\nSelect option (0-8): ").strip()
            
            if choice == '0':
                return
            elif choice == '1':
                self._configure_single_key_interactive(config)
            elif choice == '2':
                self._add_standard_layout_to_config(config)
            elif choice == '3':
                self._add_alphabetic_layout_to_config(config)
            elif choice == '4':
                self._add_numeric_layout_to_config(config)
            elif choice == '5':
                self._view_current_config(config)
            elif choice == '6':
                self._clear_key_interactive(config)
            elif choice == '7':
                if config:
                    self._generate_full_qr_from_config(config)
                else:
                    print("❌ No keys configured")
            elif choice == '8':
                self._show_complete_help()
            else:
                print("❌ Invalid choice")
    
    def _display_keyboard_matrix(self, config):
        """Display 4x4 keyboard matrix with configuration status"""
        print("\n⌨️  KEYBOARD MATRIX (4x4):")
        print("=" * 40)
        
        for row in range(4):
            print("  ", end="")
            for col in range(4):
                key_id = row * 4 + col
                if key_id in config:
                    action_count = len(config[key_id])
                    if action_count == 1:
                        # Single action - show type
                        action = config[key_id][0]
                        if action['type'] == KeyTypes.UTF8:  # UTF8 = 0
                            symbol = f"'{action.get('text', '?')[:2]}'"
                        elif action['type'] == KeyTypes.HID:  # HID = 1
                            symbol = f"H{action.get('value', 0):02X}"
                        elif action['type'] == KeyTypes.CONSUMER:  # CONSUMER = 2
                            symbol = f"C{action.get('value', 0)}"
                        else:
                            symbol = f"?{action.get('type', 0)}"
                    else:
                        symbol = f"[{action_count}]"
                    status = f"{symbol:>6}"
                else:
                    status = "  ---"
                print(f"{status}", end="  ")
            print()  # New line after each row
        
        print(f"\n📊 Status: {len(config)}/16 keys configured")
        if config:
            total_actions = sum(len(actions) for actions in config.values())
            print(f"   Total actions: {total_actions}")
    
    def _configure_single_key_interactive(self, config):
        """Configure a single key with multiple actions support"""
        print("\n🔧 SINGLE KEY CONFIGURATION")
        print("-" * 40)
        
        # Key selection
        print("Matrix keys: 0-15 (0=top-left, 3=top-right, 12=bottom-left, 15=bottom-right)")
        print("Or enter as 'row,col' (e.g., '0,0' for top-left)")
        
        key_input = input("\nEnter key to configure: ").strip()
        key_id = self._parse_key_input(key_input)
        
        if key_id is None or not (0 <= key_id <= 15):
            print("❌ Invalid key (must be matrix key 0-15)")
            return
        
        row, col = divmod(key_id, 4)
        print(f"\n📝 Configuring Key [{row},{col}] (ID: {key_id})")
        
        # Show current configuration if exists
        if key_id in config:
            print(f"Current: {len(config[key_id])} action(s)")
            for i, action in enumerate(config[key_id]):
                print(f"  {i+1}. {self._action_summary(action)}")
            
            choice = input("\nReplace (r) or add to (a) existing config? [r]: ").lower()
            if choice == 'a':
                actions = config[key_id][:]
            else:
                actions = []
        else:
            actions = []
        
        # Build actions (up to 10 total)
        while len(actions) < 10:
            remaining = 10 - len(actions)
            print(f"\n⚡ Action {len(actions) + 1} (max {remaining} more):")
            print("1. 📝 UTF-8 Text")
            print("2. ⌨️  HID Key (with modifiers)")
            print("3. 🎛️  Consumer Control")
            print("4. ✅ Finish configuration")
            
            choice = input("\nAction type (1-4): ").strip()
            
            if choice == '4' or not choice:
                break
            elif choice == '1':
                action = self._create_utf8_action_interactive()
            elif choice == '2':
                action = self._create_hid_action_interactive()
            elif choice == '3':
                action = self._create_consumer_action_interactive()
            else:
                print("❌ Invalid choice")
                continue
            
            if action:
                actions.append(action)
                print(f"✅ Action {len(actions)} added: {self._action_summary(action)}")
        
        if actions:
            config[key_id] = actions
            print(f"\n✅ Key [{row},{col}] configured with {len(actions)} action(s)")
        else:
            print("❌ No actions configured")
    
    def _parse_key_input(self, key_input: str):
        """Parse key input (matrix notation or direct ID)"""
        key_input = key_input.strip()
        
        # Try direct ID first
        try:
            key_id = int(key_input)
            if 0 <= key_id <= 15:
                return key_id
        except ValueError:
            pass
        
        # Try matrix notation (row,col)
        if ',' in key_input:
            try:
                row, col = map(int, key_input.split(','))
                if 0 <= row <= 3 and 0 <= col <= 3:
                    return row * 4 + col
            except ValueError:
                pass
        
        return None
    
    def _create_utf8_action_interactive(self):
        """Create UTF-8 text action interactively"""
        print("\n📝 UTF-8 TEXT ACTION")
        print("Examples: 'Hello', 'café', 'naïve', '1', 'A'")
        
        text = input("Enter text (max 8 UTF-8 bytes): ").strip()
        if not text:
            return None
        
        if len(text.encode('utf-8')) > 8:
            print(f"❌ Text '{text}' is {len(text.encode('utf-8'))} bytes (max 8)")
            return None
        
        delay = input("Delay after action (ms, default 0): ").strip()
        try:
            delay = int(delay) if delay else 0
        except ValueError:
            delay = 0
        
        return self.qr_generator.create_text_action(text, delay)
    
    def _create_hid_action_interactive(self):
        """Create HID key action interactively"""
        print("\n⌨️  HID KEY ACTION")
        print("Common keys:")
        print("  Letters: A=4, B=5, C=6... Z=29")
        print("  Numbers: 1=30, 2=31... 0=39")
        print("  Special: Enter=40, Esc=41, Backspace=42, Tab=43, Space=44")
        print("  Arrows: Right=79, Left=80, Down=81, Up=82")
        print("  Function: F1=58, F2=59... F12=69")
        
        key_code = input("\nEnter HID key code (0-255): ").strip()
        try:
            key_code = int(key_code)
            if not (0 <= key_code <= 255):
                print("❌ Key code must be 0-255")
                return None
        except ValueError:
            print("❌ Invalid key code")
            return None
        
        # Modifiers with better explanation
        print("\nModifier keys (combine values):")
        print("  1 = Left Ctrl     2 = Left Shift")
        print("  4 = Left Alt      8 = Left Win/Cmd")
        print("  16 = Right Ctrl   32 = Right Shift")
        print("  64 = Right Alt    128 = Right Win/Cmd")
        print("\nCommon combinations:")
        print("  3 = Ctrl+Shift    5 = Ctrl+Alt    6 = Shift+Alt")
        print("  9 = Ctrl+Win      10 = Shift+Win")
        
        modifiers = input("Enter modifier value (default 0): ").strip()
        try:
            modifiers = int(modifiers) if modifiers else 0
            if not (0 <= modifiers <= 255):
                print("❌ Modifier value must be 0-255")
                return None
        except ValueError:
            print("❌ Invalid modifier value")
            return None
        
        delay = input("Delay after action (ms, default 0): ").strip()
        try:
            delay = int(delay) if delay else 0
        except ValueError:
            delay = 0
        
        return self.qr_generator.create_hid_action(key_code, modifiers, delay)
    
    def _create_consumer_action_interactive(self):
        """Create consumer control action interactively"""
        print("\n🎛️  CONSUMER CONTROL ACTION")
        print("Common controls:")
        print("  Volume: Up=233, Down=234, Mute=226")
        print("  Media: Play/Pause=205, Stop=183, Next=181, Previous=182")
        print("  System: Power=48, Sleep=50, Wake=51")
        print("  Browser: Home=35, Back=36, Forward=37")
        
        control = input("\nEnter consumer control code: ").strip()
        try:
            control = int(control)
        except ValueError:
            print("❌ Invalid control code")
            return None
        
        delay = input("Delay after action (ms, default 0): ").strip()
        try:
            delay = int(delay) if delay else 0
        except ValueError:
            delay = 0
        
        return self.qr_generator.create_consumer_action(control, delay)
    
    def _action_summary(self, action):
        """Get summary description of an action"""
        action_type = action.get('type', 0)
        
        if action_type == KeyTypes.UTF8:  # UTF8 = 0
            text = action.get('text', '')
            return f"Text: '{text}'"
        elif action_type == KeyTypes.HID:  # HID = 1
            key = action.get('value', 0)
            mods = action.get('mask', 0)
            desc = f"HID: {key} (0x{key:02X})"
            if mods:
                mod_names = []
                if mods & 1: mod_names.append("Ctrl")
                if mods & 2: mod_names.append("Shift")
                if mods & 4: mod_names.append("Alt")
                if mods & 8: mod_names.append("Win")
                desc = f"{'+'.join(mod_names)}+{desc}"
            return desc
        elif action_type == KeyTypes.CONSUMER:  # CONSUMER = 2
            return f"Consumer: {action.get('value', 0)}"
        else:
            return f"Unknown (type={action_type})"
    
    def _add_standard_layout_to_config(self, config):
        """Add standard keypad layout (1-9, A-D, arrows)"""
        print("\n🎹 STANDARD LAYOUT")
        print("This will add/replace:")
        print("  Row 0: [1] [2] [3] [A]")
        print("  Row 1: [4] [5] [6] [B]")
        print("  Row 2: [7] [8] [9] [C]")
        print("  Row 3: [←] [0] [→] [D]")
        
        if not self._confirm("Add standard layout?"):
            return
        
        # Define the standard layout
        standard_layout = {
            # Row 0: 1, 2, 3, A
            0: [self.qr_generator.create_text_action("1")],
            1: [self.qr_generator.create_text_action("2")],
            2: [self.qr_generator.create_text_action("3")],
            3: [self.qr_generator.create_text_action("A")],
            
            # Row 1: 4, 5, 6, B
            4: [self.qr_generator.create_text_action("4")],
            5: [self.qr_generator.create_text_action("5")],
            6: [self.qr_generator.create_text_action("6")],
            7: [self.qr_generator.create_text_action("B")],
            
            # Row 2: 7, 8, 9, C
            8: [self.qr_generator.create_text_action("7")],
            9: [self.qr_generator.create_text_action("8")],
            10: [self.qr_generator.create_text_action("9")],
            11: [self.qr_generator.create_text_action("C")],
            
            # Row 3: Left Arrow, 0, Right Arrow, D
            12: [self.qr_generator.create_hid_action(HIDKeyCodes.LEFT_ARROW)],
            13: [self.qr_generator.create_text_action("0")],
            14: [self.qr_generator.create_hid_action(HIDKeyCodes.RIGHT_ARROW)],
            15: [self.qr_generator.create_text_action("D")],
        }
        
        # Add to config
        added_count = 0
        for key_id, actions in standard_layout.items():
            config[key_id] = actions
            added_count += 1
        
        print(f"✅ Added {added_count} keys to configuration")
    
    def _add_alphabetic_layout_to_config(self, config):
        """Add alphabetic layout (A-P)"""
        print("\n🔤 ALPHABETIC LAYOUT")
        print("This will add/replace keys 0-15 with letters A-P")
        
        if not self._confirm("Add alphabetic layout?"):
            return
        
        added_count = 0
        for i in range(16):
            letter = chr(ord('A') + i)  # A, B, C... P
            config[i] = [self.qr_generator.create_text_action(letter)]
            added_count += 1
        
        print(f"✅ Added {added_count} alphabetic keys (A-P)")
    
    def _add_numeric_layout_to_config(self, config):
        """Add numeric layout (0-9)"""
        print("\n🔢 NUMERIC LAYOUT")
        print("This will add/replace first 10 keys with numbers 0-9")
        
        if not self._confirm("Add numeric layout?"):
            return
        
        added_count = 0
        for i in range(10):
            number = str(i)
            config[i] = [self.qr_generator.create_text_action(number)]
            added_count += 1
        
        print(f"✅ Added {added_count} numeric keys (0-9)")
    
    def _view_current_config(self, config):
        """View current configuration details"""
        if not config:
            print("\n❌ No keys configured")
            return
        
        print(f"\n📋 CURRENT CONFIGURATION ({len(config)} keys)")
        print("=" * 60)
        
        for key_id in sorted(config.keys()):
            actions = config[key_id]
            row, col = divmod(key_id, 4)
            print(f"\n🔑 Key [{row},{col}] (ID: {key_id}): {len(actions)} action(s)")
            for i, action in enumerate(actions):
                print(f"  {i+1}. {self._action_summary(action)}")
        
        total_actions = sum(len(actions) for actions in config.values())
        print(f"\n📊 Total: {len(config)} keys, {total_actions} actions")
        
        input("\nPress Enter to continue...")
    
    def _clear_key_interactive(self, config):
        """Clear key configuration interactively"""
        if not config:
            print("\n❌ No keys configured to clear")
            return
        
        print("\n🗑️  CLEAR KEY CONFIGURATION")
        print("Options:")
        print("1. Clear specific key")
        print("2. Clear all keys")
        print("0. Cancel")
        
        choice = input("\nSelect option (0-2): ").strip()
        
        if choice == '1':
            key_input = input("Enter key to clear: ").strip()
            key_id = self._parse_key_input(key_input)
            
            if key_id is not None and key_id in config:
                row, col = divmod(key_id, 4)
                del config[key_id]
                print(f"✅ Cleared key [{row},{col}] (ID: {key_id})")
            else:
                print("❌ Key not found in configuration")
        elif choice == '2':
            if self._confirm("Clear ALL keys?"):
                config.clear()
                print("✅ All keys cleared")
            else:
                print("❌ Cancelled")
    
    def _generate_full_qr_from_config(self, config):
        """Generate $FULL: QR code from current configuration"""
        print(f"\n📦 GENERATING $FULL: QR CODE")
        print(f"Configuration: {len(config)} keys configured")
        
        total_actions = sum(len(actions) for actions in config.values())
        print(f"Total actions: {total_actions}")
        
        try:
            qr_command = self.qr_generator.create_full_keyboard_config(config)
            
            # Show compression statistics
            metadata = qr_command.metadata
            print(f"\n📊 Configuration Statistics:")
            print(f"  Keys configured: {metadata['keys_configured']}")
            print(f"  Total actions: {metadata['total_actions']}")
            print(f"  Original size: {metadata['original_size_bytes']} bytes")
            print(f"  Compressed size: {metadata['compressed_size_bytes']} bytes")
            print(f"  Base64 size: {metadata['base64_size_chars']} characters")
            print(f"  Compression ratio: {metadata['compression_ratio_percent']}%")
            print(f"  QR format: ${metadata['qr_format']}:")
            
            self._add_and_preview_command(qr_command)
            print("\n✅ $FULL: QR code generated successfully!")
            print("You can now scan this QR code with your aRdent ScanPad device")
            
        except Exception as e:
            print(f"❌ Error generating QR code: {e}")
    
    def _show_complete_help(self):
        """Show complete help information"""
        print("\n💡 COMPLETE KEYBOARD BUILDER HELP")
        print("=" * 60)
        
        print("\n🗝️  KEY IDENTIFICATION:")
        print("Matrix keys are numbered 0-15 in row-major order:")
        print("  Row 0: [0] [1] [2] [3]")
        print("  Row 1: [4] [5] [6] [7]")
        print("  Row 2: [8] [9] [10] [11]")
        print("  Row 3: [12] [13] [14] [15]")
        print("\nYou can also use 'row,col' notation (e.g., '0,0' = key 0)")
        
        print("\n📝 ACTION TYPES:")
        print("1. UTF-8 Text: Any text up to 8 UTF-8 bytes")
        print("   - Examples: 'Hello', 'café', '1', 'A'")
        print("   - Supports international characters")
        
        print("\n2. HID Keys: Standard keyboard keys with modifiers")
        print("   - Key codes: A=4, B=5... Z=29, 1=30... 0=39")
        print("   - Special: Enter=40, Esc=41, Space=44, Tab=43")
        print("   - Arrows: Up=82, Down=81, Left=80, Right=79")
        print("   - Function: F1=58, F2=59... F12=69")
        print("   - Modifiers: Ctrl=1, Shift=2, Alt=4, Win=8")
        
        print("\n3. Consumer Controls: Media and system controls")
        print("   - Volume: Up=233, Down=234, Mute=226")
        print("   - Media: Play/Pause=205, Stop=183, Next=181")
        print("   - System: Power=48, Sleep=50, Wake=51")
        
        print("\n⚡ MULTI-ACTIONS:")
        print("Each key can have up to 10 actions executed in sequence")
        print("Perfect for complex macros and key combinations")
        
        print("\n🎹 QUICK LAYOUTS:")
        print("- Standard: Numbers 1-9, letters A-D, arrow keys")
        print("- Alphabetic: Letters A-P across all 16 keys")
        print("- Numeric: Numbers 0-9 on first 10 keys")
        
        print("\n📦 $FULL: FORMAT:")
        print("Uses compressed binary format for complete keyboard config")
        print("Single QR code contains all 16 keys with all actions")
        print("Automatic compression reduces QR code size significantly")
        
        input("\nPress Enter to continue...")
    
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
        """Keyboard language command with guided selection"""
        print("\n⚙️  KEYBOARD LANGUAGE CONFIGURATION")
        print("="*40)
        
        # Step 1: Select Operating System
        print("Step 1 - Select Operating System:")
        print("  1. Windows")
        print("  2. macOS") 
        print("  3. Linux")
        
        try:
            os_choice = input("\nSelect OS (1-3): ").strip()
            if os_choice not in ["1", "2", "3"]:
                print("❌ Invalid OS selection")
                return
                
            os_names = {"1": "Windows", "2": "macOS", "3": "Linux"}
            selected_os = os_names[os_choice]
            
            # Step 2: Select Layout Type
            print(f"\nStep 2 - Select Layout Type for {selected_os}:")
            print("  1. QWERTY (English/US)")
            print("  2. AZERTY (French)")
            print("  3. QWERTZ (German)")
            
            layout_choice = input("\nSelect layout (1-3): ").strip()
            if layout_choice not in ["1", "2", "3"]:
                print("❌ Invalid layout selection")
                return
                
            layout_names = {"1": "QWERTY", "2": "AZERTY", "3": "QWERTZ"}
            selected_layout = layout_names[layout_choice]
            
            # Step 3: Select Language/Region
            print(f"\nStep 3 - Select Language/Region for {selected_layout}:")
            
            # Build available languages based on selections
            available_languages = []
            
            # Map OS codes: Windows=1, macOS=2, Linux=3 (hypothetical mapping)
            os_code = int(os_choice)
            
            if layout_choice == "1":  # QWERTY
                if os_choice == "1":  # Windows
                    available_languages = [
                        ("1. US English", KeyboardLayouts.WIN_US_QWERTY),
                        ("2. Spanish", KeyboardLayouts.WIN_ES_QWERTY),
                        ("3. Italian", KeyboardLayouts.WIN_IT_QWERTY),
                        ("4. Portuguese", KeyboardLayouts.WIN_PT_QWERTY),
                        ("5. Dutch", KeyboardLayouts.WIN_NL_QWERTY),
                    ]
                elif os_choice == "2":  # macOS
                    available_languages = [
                        ("1. US English", 0x2110),  # macOS US (hypothetical)
                    ]
                else:  # Linux
                    available_languages = [
                        ("1. US English", 0x5110),  # Linux US (0x5 = Linux)
                    ]
                    
            elif layout_choice == "2":  # AZERTY
                if os_choice == "1":  # Windows
                    available_languages = [
                        ("1. French (France)", KeyboardLayouts.WIN_FR_AZERTY),
                        ("2. French (Belgium)", KeyboardLayouts.WIN_BE_AZERTY),
                    ]
                elif os_choice == "2":  # macOS
                    available_languages = [
                        ("1. French (France)", 0x2220),  # Hypothetical macOS FR
                    ]
                else:  # Linux
                    available_languages = [
                        ("1. French (France)", 0x5220),  # Linux FR (0x5 = Linux)
                    ]
                    
            elif layout_choice == "3":  # QWERTZ
                if os_choice == "1":  # Windows
                    available_languages = [
                        ("1. German", KeyboardLayouts.WIN_DE_QWERTZ),
                    ]
                elif os_choice == "2":  # macOS
                    available_languages = [
                        ("1. German", 0x2340),  # macOS DE (hypothetical)
                    ]
                else:  # Linux
                    available_languages = [
                        ("1. German", 0x5340),  # Linux DE (0x5 = Linux)
                    ]
            
            # Display available languages
            for desc, code in available_languages:
                print(f"  {desc} (0x{code:04X})")
            
            max_choice = len(available_languages)
            lang_choice = input(f"\nSelect language (1-{max_choice}): ").strip()
            
            try:
                lang_idx = int(lang_choice) - 1
                if not (0 <= lang_idx < max_choice):
                    print("❌ Invalid language selection")
                    return
            except ValueError:
                print("❌ Invalid language selection")
                return
                
            # Get selected language info
            selected_desc, layout_id = available_languages[lang_idx]
            language_name = selected_desc.split(". ")[1]  # Extract name after number
            
            print(f"\n✅ Selected Configuration:")
            print(f"   OS: {selected_os}")
            print(f"   Layout: {selected_layout}")
            print(f"   Language: {language_name}")
            print(f"   Code: 0x{layout_id:04X}")
            
            # Create language command
            payload = bytes([layout_id & 0xFF, (layout_id >> 8) & 0xFF])
            command_data = f"$CMD:DEV:42{payload.hex().upper()}CMD$"
            
            command = QRCommand(
                command_data, "Keyboard Language",
                f"Set keyboard to {language_name} (0x{layout_id:04X})",
                {
                    'layout_id': layout_id,
                    'os': selected_os,
                    'layout_type': selected_layout,
                    'language': language_name
                }
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