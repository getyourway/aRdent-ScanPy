"""
Keyboard Configuration Builder

Common utilities for building keyboard configurations across different examples.
Provides presets, layouts, and interactive configuration tools.
"""

from typing import Dict, List, Optional, Any
from .ui_helpers import confirm, get_int_input, get_text_input, get_choice_input, pause_for_user


class KeyboardConfigBuilder:
    """Unified keyboard configuration builder with presets and layouts"""
    
    def __init__(self):
        """Initialize keyboard builder"""
        self._qr_generator = None
        self._kb_generator = None
    
    def _get_qr_generator(self):
        """Lazy load QR generator"""
        if self._qr_generator is None:
            try:
                from ardent_scanpad.controllers.qr_generator import QRGeneratorController
                from ardent_scanpad.qr_generators import KeyboardConfigGenerator
                self._qr_generator = QRGeneratorController()
                self._kb_generator = KeyboardConfigGenerator()
            except ImportError as e:
                print(f"❌ QR generation not available: {e}")
                return None, None
        return self._qr_generator, self._kb_generator
    
    
    # ========================================
    # KEYBOARD MATRIX DISPLAY
    # ========================================
    
    def display_keyboard_matrix(self, config: Dict[str, List], title: str = "KEYBOARD MATRIX"):
        """Display current keyboard matrix configuration"""
        print(f"\n⌨️  {title} (4x4):")
        print("="*40)
        
        for row in range(4):
            line = f"    Row {row}: "
            for col in range(4):
                key_id = str(row * 4 + col)
                if key_id in config:
                    actions = config[key_id]
                    if len(actions) == 1:
                        # Single action - show the value
                        display_value = self._get_action_display_value(actions[0])
                        line += f"[{display_value}] "
                    else:
                        # Multiple actions - show first action with count
                        display_value = self._get_action_display_value(actions[0])
                        line += f"[{display_value}]({len(actions)}) "
                else:
                    line += f"[---] "
            print(line)
        
        # Show external buttons
        print("\n📱 External Buttons:")
        button_names = {
            "16": "Scan Double",
            "17": "Scan Long",
            "18": "Power Single",
            "19": "Power Double"
        }

        for key_id, name in button_names.items():
            if key_id in config:
                actions = config[key_id]
                if len(actions) == 1:
                    display_value = self._get_action_display_value(actions[0])
                    status = display_value
                else:
                    display_value = self._get_action_display_value(actions[0])
                    status = f"{display_value}({len(actions)})"
            else:
                status = "---"
            print(f"  [{key_id}:{status:^12}] {name}")

        # Show long press keys (compact view - only configured ones)
        long_press_configured = [key_id for key_id in config if key_id.isdigit() and 100 <= int(key_id) <= 115]
        if long_press_configured:
            print("\n⏱️  Long Press Keys:")
            for key_id in sorted(long_press_configured, key=lambda x: int(x)):
                base_id = int(key_id) - 100
                row, col = divmod(base_id, 4)
                actions = config[key_id]
                if len(actions) == 1:
                    display_value = self._get_action_display_value(actions[0])
                    status = display_value
                else:
                    display_value = self._get_action_display_value(actions[0])
                    status = f"{display_value}({len(actions)})"
                print(f"  [{key_id}:{status:^12}] Key ({row},{col}) Long")

        # Summary (updated to 36 total keys)
        total_configured = len(config)
        print(f"\n📊 Status: {total_configured}/36 keys configured (16 short + 4 buttons + 16 long press)")
        
        if config:
            total_actions = sum(len(actions) for actions in config.values())
            print(f"📊 Total actions: {total_actions}")
    
    def _get_action_display_value(self, action: Dict) -> str:
        """Get short display value for an action"""
        if action["type"] == "text":
            value = action["value"]
            # For single characters, show as-is
            if len(value) == 1:
                return value
            # For short text, truncate if needed
            elif len(value) <= 3:
                return value
            else:
                return value[:2] + "…"
        elif action["type"] == "hid":
            keycode = action.get("keycode", 0)
            # Common HID keycodes to readable values
            hid_display = {
                40: "↵",    # Enter
                42: "⌫",    # Backspace  
                43: "⇥",    # Tab
                44: "␣",    # Space
                79: "→",    # Right Arrow
                80: "←",    # Left Arrow
                81: "↓",    # Down Arrow
                82: "↑",    # Up Arrow
                76: "⌦",    # Delete
                41: "⎋",    # Escape
            }
            
            if keycode in hid_display:
                return hid_display[keycode]
            # For A-Z (4-29)
            elif 4 <= keycode <= 29:
                return chr(ord('A') + keycode - 4)
            # For 1-9 (30-38) 
            elif 30 <= keycode <= 38:
                return str(keycode - 29)
            # For 0 (39)
            elif keycode == 39:
                return "0"
            else:
                return f"K{keycode}"
        elif action["type"] == "consumer":
            consumer_code = action.get("consumer_code", 0)
            consumer_display = {
                205: "⏯",   # Play/Pause
                233: "🔊",   # Volume Up
                234: "🔉",   # Volume Down
                226: "🔇",   # Mute
                181: "⏭",   # Next
                182: "⏮",   # Previous
                183: "⏹",   # Stop
            }
            return consumer_display.get(consumer_code, f"C{consumer_code}")
        else:
            return "?"
    
    # ========================================
    # LAYOUT PRESETS
    # ========================================
    
    def apply_standard_layout(self, config: Dict[str, List], silent: bool = False) -> int:
        """Apply standard keypad layout (1-9, A-D, arrows)"""
        print("\n🎹 STANDARD LAYOUT")
        print("This will add/replace:")
        print("  Row 0: [1] [2] [3] [A]")
        print("  Row 1: [4] [5] [6] [B]")
        print("  Row 2: [7] [8] [9] [C]")
        print("  Row 3: [←] [0] [→] [D]")
        
        if not silent and not confirm("Add standard layout?"):
            return 0
        
        layout = {
            # Row 0: Numbers 1-3, Letter A
            "0": [{"type": "text", "value": "1", "delay": 10}],
            "1": [{"type": "text", "value": "2", "delay": 10}],
            "2": [{"type": "text", "value": "3", "delay": 10}],
            "3": [{"type": "text", "value": "A", "delay": 10}],
            
            # Row 1: Numbers 4-6, Letter B
            "4": [{"type": "text", "value": "4", "delay": 10}],
            "5": [{"type": "text", "value": "5", "delay": 10}],
            "6": [{"type": "text", "value": "6", "delay": 10}],
            "7": [{"type": "text", "value": "B", "delay": 10}],
            
            # Row 2: Numbers 7-9, Letter C
            "8": [{"type": "text", "value": "7", "delay": 10}],
            "9": [{"type": "text", "value": "8", "delay": 10}],
            "10": [{"type": "text", "value": "9", "delay": 10}],
            "11": [{"type": "text", "value": "C", "delay": 10}],
            
            # Row 3: Arrows, 0, Letter D
            "12": [{"type": "hid", "keycode": 80, "modifier": 0, "delay": 10}],  # Left Arrow
            "13": [{"type": "text", "value": "0", "delay": 10}],
            "14": [{"type": "hid", "keycode": 79, "modifier": 0, "delay": 10}],  # Right Arrow
            "15": [{"type": "text", "value": "D", "delay": 10}],
        }
        
        config.update(layout)
        print("✅ Standard layout applied (16 keys)")
        return len(layout)
    
    def apply_alphabetic_layout(self, config: Dict[str, List], silent: bool = False) -> int:
        """Apply alphabetic layout (A-P)"""
        print("\n🔤 ALPHABETIC LAYOUT")
        print("This will add/replace keys 0-15 with letters A-P")
        
        if not silent and not confirm("Add alphabetic layout?"):
            return 0
        
        layout = {}
        for i in range(16):
            letter = chr(ord('A') + i)  # A, B, C, ..., P
            layout[str(i)] = [{"type": "text", "value": letter, "delay": 10}]
        
        config.update(layout)
        print("✅ Alphabetic layout applied (A-P)")
        return len(layout)
    
    def apply_numeric_layout(self, config: Dict[str, List], silent: bool = False) -> int:
        """Apply numeric layout (0-9)"""
        print("\n🔢 NUMERIC LAYOUT")
        print("This will add/replace first 10 keys with numbers 0-9")
        
        if not silent and not confirm("Add numeric layout?"):
            return 0
        
        layout = {}
        for i in range(10):
            layout[str(i)] = [{"type": "text", "value": str(i), "delay": 10}]
        
        config.update(layout)
        print("✅ Numeric layout applied (0-9)")
        return len(layout)
    
    def apply_numpad_preset(self, config: Dict[str, List], silent: bool = False) -> int:
        """Apply calculator-style numpad preset"""
        print("\n🧮 CALCULATOR NUMPAD")
        print("This will create a calculator-style layout:")
        print("  [1] [2] [3] [+]")
        print("  [4] [5] [6] [-]")
        print("  [7] [8] [9] [*]")
        print("  [.] [0] [=] [↵]")
        
        if not silent and not confirm("Apply numpad preset?"):
            return 0
        
        layout = {
            "0": [{"type": "text", "value": "1", "delay": 10}],
            "1": [{"type": "text", "value": "2", "delay": 10}],
            "2": [{"type": "text", "value": "3", "delay": 10}],
            "3": [{"type": "text", "value": "+", "delay": 10}],
            "4": [{"type": "text", "value": "4", "delay": 10}],
            "5": [{"type": "text", "value": "5", "delay": 10}],
            "6": [{"type": "text", "value": "6", "delay": 10}],
            "7": [{"type": "text", "value": "-", "delay": 10}],
            "8": [{"type": "text", "value": "7", "delay": 10}],
            "9": [{"type": "text", "value": "8", "delay": 10}],
            "10": [{"type": "text", "value": "9", "delay": 10}],
            "11": [{"type": "text", "value": "*", "delay": 10}],
            "12": [{"type": "text", "value": ".", "delay": 10}],
            "13": [{"type": "text", "value": "0", "delay": 10}],
            "14": [{"type": "text", "value": "=", "delay": 10}],
            "15": [{"type": "hid", "keycode": 40, "modifier": 0, "delay": 10}]  # ENTER
        }
        
        config.update(layout)
        print("✅ Calculator numpad preset applied")
        return len(layout)
    
    def apply_function_keys_preset(self, config: Dict[str, List], silent: bool = False) -> int:
        """Apply function keys preset (F1-F12)"""
        print("\n🔧 FUNCTION KEYS PRESET")
        print("This will assign F1-F12 to keys 0-11 (top 3 rows)")
        print("⚠️  Keys 12-15 will remain unchanged")
        
        if not silent and not confirm("Apply function keys preset?"):
            return 0
        
        layout = {}
        for i in range(12):
            # F1-F12 are HID codes 58-69
            layout[str(i)] = [{
                "type": "hid",
                "keycode": 58 + i,
                "modifier": 0,
                "delay": 10
            }]
        
        config.update(layout)
        print(f"✅ Function keys preset applied (F1-F{len(layout)} on keys 0-11)")
        return len(layout)
    
    # ========================================
    # INTERACTIVE CONFIGURATION
    # ========================================
    
    def configure_key_interactive(self, key_id: int) -> Optional[List[Dict]]:
        """Configure a single key interactively"""
        print(f"\n🔧 CONFIGURE KEY {key_id}")
        print("-" * 30)
        
        # Show key position in matrix
        if 0 <= key_id <= 15:
            row, col = divmod(key_id, 4)
            print(f"Matrix position: Row {row}, Column {col}")
        else:
            button_names = {
                16: "Scan Trigger Double Press",
                17: "Scan Trigger Long Press",
                18: "Power Button Single Press",
                19: "Power Button Double Press"
            }
            if key_id in button_names:
                print(f"External button: {button_names[key_id]}")
        
        actions = []
        
        while len(actions) < 10:
            print(f"\nAction {len(actions) + 1}/10 for key {key_id}:")
            
            action_types = ["Text", "HID Key", "Consumer Key", "Finish"]
            print("\nAction types:")
            for i, action_type_option in enumerate(action_types, 1):
                print(f"  {i}. {action_type_option}")
            
            try:
                choice_num = int(input("Select action type (1-4): ").strip())
                if 1 <= choice_num <= len(action_types):
                    action_type = action_types[choice_num - 1]
                else:
                    action_type = None
            except ValueError:
                action_type = None
                
            if action_type == "Finish" or not action_type:
                break
            elif action_type == "Text":
                text = get_text_input("Enter text (max 8 UTF-8 bytes): ")
                if text and len(text.encode('utf-8')) <= 8:
                    delay = get_int_input("Delay in ms (0-65535) [10]: ", 0, 65535) or 10
                    actions.append({"type": "text", "value": text, "delay": delay})
                elif text:
                    print("❌ Text too long (max 8 UTF-8 bytes)")
                    
            elif action_type == "HID Key":
                print("\nCommon HID keycodes:")
                print("  ENTER=40, TAB=43, SPACE=44, ESC=41")
                print("  A=4, B=5, ..., Z=29")
                print("  1=30, 2=31, ..., 9=38, 0=39")
                
                keycode = get_int_input("HID keycode (0-255): ", 0, 255)
                if keycode is not None:
                    print("\nModifiers (can be combined):")
                    print("  0=None, 1=CTRL, 2=SHIFT, 4=ALT, 8=GUI")
                    modifier = get_int_input("Modifier (0-15) [0]: ", 0, 15) or 0
                    delay = get_int_input("Delay in ms (0-65535) [10]: ", 0, 65535) or 10
                    
                    actions.append({
                        "type": "hid",
                        "keycode": keycode,
                        "modifier": modifier,
                        "delay": delay
                    })
                    
            elif action_type == "Consumer Key":
                print("\nCommon consumer codes:")
                print("  Play/Pause=205, Vol+=233, Vol-=234, Mute=226")
                print("  Next=181, Prev=182, Stop=183")
                
                code = get_int_input("Consumer code (0-65535): ", 0, 65535)
                if code is not None:
                    delay = get_int_input("Delay in ms (0-65535) [10]: ", 0, 65535) or 10
                    actions.append({
                        "type": "consumer",
                        "consumer_code": code,
                        "delay": delay
                    })
        
        if actions:
            print(f"\n✅ Configured {len(actions)} action(s) for key {key_id}")
            for i, action in enumerate(actions, 1):
                print(f"  {i}. {self._action_summary(action)}")
            
            return actions
        else:
            print("❌ No actions configured")
            return None
    
    def _action_summary(self, action: Dict) -> str:
        """Create a summary string for an action"""
        if action["type"] == "text":
            return f"Text: '{action['value']}'"
        elif action["type"] == "hid":
            keycode = action.get("keycode", 0)
            modifier = action.get("modifier", 0)
            mod_text = ""
            if modifier:
                mods = []
                if modifier & 1: mods.append("CTRL")
                if modifier & 2: mods.append("SHIFT")
                if modifier & 4: mods.append("ALT")
                if modifier & 8: mods.append("GUI")
                mod_text = f" ({'+'.join(mods)})"
            return f"HID: keycode {keycode}{mod_text}"
        elif action["type"] == "consumer":
            return f"Consumer: code {action.get('consumer_code', 0)}"
        else:
            return f"Unknown action: {action}"
    
    # ========================================
    # COMPLETE KEYBOARD BUILDER
    # ========================================
    
    def run_complete_builder(self, initial_config: Optional[Dict[str, List]] = None) -> Optional[Dict[str, List]]:
        """Run complete interactive keyboard builder"""
        print("\n🛠️  COMPLETE KEYBOARD BUILDER")
        print("="*60)
        print("Configure all 16 matrix keys with multiple actions support")
        print("Supports presets, layouts, and individual key configuration")
        
        config = initial_config.copy() if initial_config else {}
        
        while True:
            self.display_keyboard_matrix(config, "CURRENT CONFIGURATION")
            
            print("\n📋 CONFIGURATION OPTIONS:")
            print("1. 🔧 Configure single key (with multi-actions)")
            print("2. 🎨 Apply layout presets (Standard, Numeric, etc.)")
            print("3. 📋 View current configuration")
            print("4. 🗑️  Clear key configuration")
            print("5. ✅ Finish and export")
            print("0. ❌ Cancel and return None")
            
            choice = input("\nSelect option (0-5): ").strip()
            
            if choice == "0":
                if not confirm("Discard configuration?"):
                    continue
                return None
            elif choice == "1":
                self._configure_single_key_menu(config)
            elif choice == "2":
                self._layout_presets_menu(config)
            elif choice == "3":
                self._view_configuration_details(config)
            elif choice == "4":
                self._clear_configuration_menu(config)
            elif choice == "5":
                if config:
                    print(f"\n✅ Configuration completed with {len(config)} keys configured")
                    if self._finish_and_export_menu(config):
                        return config
                else:
                    print("❌ No keys configured")
                    if confirm("Return empty configuration?"):
                        return config
    
    def _layout_presets_menu(self, config: Dict[str, List]):
        """Layout presets submenu"""
        while True:
            print("\n🎨 LAYOUT PRESETS MENU")
            print("="*40)
            print("1. 🎹 Standard layout (1-9, A-D, arrows)")
            print("2. 🔤 Alphabetic layout (A-P)")
            print("3. 🔢 Numeric layout (0-9)")
            print("4. 🧮 Calculator numpad")
            print("5. 🔧 Function keys (F1-F12)")
            print("6. 🗑️  Clear ALL keys first")
            print("0. ⬅️  Back to main menu")
            
            choice = input("\nSelect layout preset (0-6): ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                self.apply_standard_layout(config)
                break  # Return to main menu after applying layout
            elif choice == "2":
                self.apply_alphabetic_layout(config)
                break  # Return to main menu after applying layout
            elif choice == "3":
                self.apply_numeric_layout(config)
                break  # Return to main menu after applying layout
            elif choice == "4":
                self.apply_numpad_preset(config)
                break  # Return to main menu after applying layout
            elif choice == "5":
                self.apply_function_keys_preset(config)
                break  # Return to main menu after applying layout
            elif choice == "6":
                if confirm("⚠️  Clear ALL keys before applying preset?"):
                    config.clear()
                    print("✅ All keys cleared")
            else:
                print("❌ Invalid choice")
    
    def _configure_single_key_menu(self, config: Dict[str, List]):
        """Configure a single key with interactive menu"""
        print("\n🔧 CONFIGURE SINGLE KEY")
        print("-" * 30)
        print("Matrix keys (short press): 0-15")
        print("External buttons: 16=Scan Double, 17=Scan Long, 18=Power, 19=Power Double")
        print("Matrix keys (long press): 100-115")

        key_id = get_int_input("Enter key ID (0-19 or 100-115): ", min_val=0, max_val=115)
        if key_id is None:
            return
        
        # Show existing configuration
        if str(key_id) in config:
            print(f"\nCurrent configuration for key {key_id}:")
            for i, action in enumerate(config[str(key_id)], 1):
                print(f"  {i}. {self._action_summary(action)}")
            
            if not confirm("Replace existing configuration?"):
                return
        
        # Configure key
        actions = self.configure_key_interactive(key_id)
        if actions:
            config[str(key_id)] = actions
    
    def _view_configuration_details(self, config: Dict[str, List]):
        """View detailed configuration"""
        if not config:
            print("\n❌ No keys configured")
            pause_for_user()
            return
        
        print("\n📋 DETAILED CONFIGURATION")
        print("="*50)
        
        for key_id in sorted(config.keys(), key=int):
            actions = config[key_id]
            print(f"\nKey {key_id} ({len(actions)} action{'' if len(actions) == 1 else 's'}):")
            for i, action in enumerate(actions, 1):
                print(f"  {i}. {self._action_summary(action)}")
        
        pause_for_user()
    
    def _clear_configuration_menu(self, config: Dict[str, List]):
        """Clear configuration menu"""
        if not config:
            print("\n❌ No keys to clear")
            return
        
        print("\n🗑️  CLEAR CONFIGURATION")
        print("1. Clear specific key")
        print("2. Clear all keys")
        
        choice = input("Select option (1-2): ").strip()
        
        if choice == "1":
            key_id = get_int_input("Enter key ID to clear (0-19 or 100-115): ", min_val=0, max_val=115)
            if key_id is not None and str(key_id) in config:
                del config[str(key_id)]
                print(f"✅ Key {key_id} cleared")
            elif key_id is not None:
                print(f"❌ Key {key_id} not configured")
        elif choice == "2":
            if confirm("Clear ALL keys?"):
                config.clear()
                print("✅ All keys cleared")
    
    def _finish_and_export_menu(self, config: Dict[str, List]) -> bool:
        """Finish and export menu. Returns True to finish, False to go back"""
        while True:
            print("\n📤 EXPORT CONFIGURATION")
            print("="*40)
            print("1. 💾 Export as JSON file")
            print("2. 📱 Export as QR codes (full command)")
            print("3. 📋 Just return configuration (no export)")
            print("0. ⬅️  Back to configuration")
            
            choice = input("\nSelect export option (0-3): ").strip()
            
            if choice == "0":
                return False  # Go back to main configuration menu
            elif choice == "1":
                self._export_json_with_output_dir(config)
                return True  # Export done, finish
            elif choice == "2":
                self._export_qr_with_output_dir(config)
                return True  # Export done, finish
            elif choice == "3":
                print("✅ Configuration ready to return")
                return True  # No export, just finish
            else:
                print("❌ Invalid choice")
    
    def _export_json_with_output_dir(self, config: Dict[str, List]):
        """Export JSON to output directory"""
        from pathlib import Path
        from datetime import datetime
        
        # Determine output directory relative to example file
        try:
            import inspect
            # Walk up the call stack to find the example script (not this common module)
            current_frame = inspect.currentframe()
            calling_file = None
            
            # Go up the call stack to find a file that's not in the 'common' directory
            frame = current_frame
            while frame:
                frame = frame.f_back
                if frame:
                    file_path = frame.f_globals.get('__file__')
                    if file_path and 'common' not in Path(file_path).parts:
                        calling_file = file_path
                        break
            
            if calling_file:
                script_dir = Path(calling_file).parent
                output_dir = script_dir / "output"
            else:
                output_dir = Path("output")
        except:
            output_dir = Path("output")
        
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"keyboard_config_{timestamp}.json"
        filepath = output_dir / filename
        
        success = self.save_json_export(config, str(filepath))
        if success:
            print(f"📁 Export location: {output_dir}")
            print("💡 You can load this file in the JSON interactive tool")
    
    def _export_qr_with_output_dir(self, config: Dict[str, List]):
        """Export QR codes to output directory"""
        from pathlib import Path
        
        # Determine output directory relative to example file
        try:
            import inspect
            # Walk up the call stack to find the example script (not this common module)
            current_frame = inspect.currentframe()
            calling_file = None
            
            # Go up the call stack to find a file that's not in the 'common' directory
            frame = current_frame
            while frame:
                frame = frame.f_back
                if frame:
                    file_path = frame.f_globals.get('__file__')
                    if file_path and 'common' not in Path(file_path).parts:
                        calling_file = file_path
                        break
            
            if calling_file:
                script_dir = Path(calling_file).parent
                output_dir = script_dir / "output"
            else:
                output_dir = Path("output")
        except:
            output_dir = Path("output")
        
        print(f"\n📱 QR Code Export")
        print("="*30)
        qr_commands = self.export_to_qr_commands(config)
        if not qr_commands:
            print("💡 QR generation failed, generating JSON export instead...")
            self._export_json_with_output_dir(config)
        else:
            # Save QR codes to output directory
            output_dir.mkdir(exist_ok=True)
            
            saved_files = []
            for i, qr_cmd in enumerate(qr_commands):
                if len(qr_commands) == 1:
                    filename = "keyboard_config_full.png"
                else:
                    filename = f"keyboard_config_part_{i+1:02d}_of_{len(qr_commands):02d}.png"
                
                filepath = output_dir / filename
                if qr_cmd.save(filepath):
                    saved_files.append(str(filepath))
                    print(f"✅ Saved: {filename}")
                else:
                    print(f"❌ Failed to save: {filename}")
            
            if saved_files:
                print(f"📁 QR codes saved to: {output_dir}")
                if len(qr_commands) > 1:
                    print("\n📖 Deployment Instructions:")
                    print("1. Scan QR codes in order") 
                    print("2. Configuration will be applied automatically")
    
    # ========================================
    # EXPORT METHODS
    # ========================================
    
    def export_to_json(self, config: Dict[str, List]) -> Dict[str, Any]:
        """Export configuration to JSON format"""
        if not config:
            return {
                "type": "keyboard_configuration",
                "metadata": {
                    "name": "Empty Configuration",
                    "description": "No keys configured",
                    "version": "1.0"
                },
                "keys": {}
            }
        
        from datetime import datetime
        
        # Use modern KISS format with unified keys 0-19
        json_config = {
            "type": "keyboard_configuration",
            "metadata": {
                "name": "Keyboard Configuration",
                "description": f"Configuration with {len(config)} keys",
                "version": "1.0",
                "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "use_case": "custom"
            },
            "keys": config
        }
        
        return json_config
    
    def export_to_qr_commands(self, config: Dict[str, List]):
        """Export configuration to QR commands for scanning"""
        if not config:
            print("❌ No configuration to export")
            return []
        
        qr_gen, kb_gen = self._get_qr_generator()
        if not qr_gen or not kb_gen:
            return []
        
        try:
            # Use modern KISS format directly
            json_config = self.export_to_json(config)
            qr_commands = kb_gen.from_json(json_config)
            print(f"✅ Generated {len(qr_commands)} QR command(s)")
            return qr_commands
            
        except Exception as e:
            print(f"❌ Error generating QR codes: {e}")
            print("💡 Use save_json_export() instead for reliable export.")
            return []
    
    def save_json_export(self, config: Dict[str, List], filepath: str = None) -> bool:
        """Save configuration as JSON file"""
        import json
        from pathlib import Path
        
        if not config:
            print("❌ No configuration to save")
            return False
        
        if not filepath:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"keyboard_config_{timestamp}.json"
        
        try:
            json_data = self.export_to_json(config)
            
            # Create parent directory if it doesn't exist
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Configuration saved: {filepath}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving JSON: {e}")
            return False
    
    def save_qr_export(self, config: Dict[str, List], output_dir: str = None) -> bool:
        """Save configuration as QR code images"""
        from pathlib import Path
        
        if not config:
            print("❌ No configuration to export")
            return False
        
        qr_commands = self.export_to_qr_commands(config)
        if not qr_commands:
            print("💡 QR generation failed, offering JSON export instead...")
            try:
                from .ui_helpers import confirm
                if confirm("Save as JSON file instead?"):
                    from datetime import datetime
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    json_filename = f"keyboard_config_export_{timestamp}.json"
                    return self.save_json_export(config, json_filename)
            except ImportError:
                pass
            return False
        
        if not output_dir:
            output_dir = Path("qr_output")
        else:
            output_dir = Path(output_dir)
        
        output_dir.mkdir(exist_ok=True)
        
        try:
            saved_files = []
            for i, qr_cmd in enumerate(qr_commands):
                if len(qr_commands) == 1:
                    filename = "keyboard_config_full.png"
                else:
                    filename = f"keyboard_config_part_{i+1:02d}_of_{len(qr_commands):02d}.png"
                
                filepath = output_dir / filename
                if qr_cmd.save(filepath):
                    saved_files.append(str(filepath))
                    print(f"✅ Saved: {filename}")
                else:
                    print(f"❌ Failed to save: {filename}")
            
            if saved_files:
                print(f"\n✅ Saved {len(saved_files)} QR code(s) to {output_dir}")
                if len(qr_commands) > 1:
                    print("\n📖 Deployment Instructions:")
                    print("1. Scan QR codes in order")
                    print("2. Configuration will be applied automatically")
                return True
            else:
                return False
                
        except Exception as e:
            print(f"❌ Error saving QR codes: {e}")
            return False