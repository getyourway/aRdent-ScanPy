#!/usr/bin/env python3
"""
Interactive JSON Configuration Creator/Editor

Create and edit JSON configurations for aRdent ScanPad device.
Supports both keyboard configurations and device command batches.
"""

import sys
import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common import (
    InteractiveBase, JSONBrowser, KeyboardConfigBuilder,
    confirm, get_int_input, get_text_input, get_choice_input,
    pause_for_user, display_menu, get_menu_choice
)

# Import constants from main library
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from ardent_scanpad.utils.constants import (
    HIDKeyCodes, HIDModifiers, ConsumerCodes,
    DeviceOrientations, KeyboardLayouts, LEDs, BuzzerMelodies
)


class InteractiveJSONCreator(InteractiveBase):
    """Interactive JSON configuration creator and editor"""
    
    def __init__(self):
        super().__init__(
            "🛠️ aRdent ScanPad - JSON Configuration Creator",
            "Create and edit keyboard configurations and device commands"
        )
        self.json_browser = JSONBrowser()
        self.keyboard_builder = KeyboardConfigBuilder()
        self.current_config = {}
    
    def run(self):
        """Main entry point"""
        self.print_header()
        
        menu_items = [
            "📝 Create new keyboard configuration",
            "🎮 Create new device command batch",
            "✏️  Edit existing JSON file",
            "👁️  View existing JSON file",
            "📋 View all available JSON files"
        ]
        
        handler_map = {
            1: self.create_keyboard_config,
            2: self.create_device_batch,
            3: self.edit_existing,
            4: self.view_existing,
            5: self.view_all_files
        }
        
        self.run_menu_loop("MAIN MENU", menu_items, handler_map)
        print("\n👋 Goodbye!")
    
    def create_keyboard_config(self):
        """Create a new keyboard configuration"""
        print("\n📝 CREATE KEYBOARD CONFIGURATION")
        print("="*50)
        
        # Get metadata
        name = get_text_input("Configuration name: ") or "My Keyboard"
        description = get_text_input("Description (optional): ") or ""
        version = get_text_input("Version (optional): ") or "1.0"
        
        config = {
            "type": "keyboard_configuration",
            "metadata": {
                "name": name,
                "version": version
            },
            "keys": {}
        }
        
        if description:
            config["metadata"]["description"] = description
        
        # Configure keys
        while True:
            self.keyboard_builder.display_keyboard_matrix(config["keys"], "KEYBOARD CONFIGURATION")
            
            menu_items = [
                "🛠️  Complete keyboard builder (Advanced)",
                "🔧 Configure single key",
                "🧮 Quick setup: Calculator numpad",
                "🔧 Quick setup: Function keys",
                "🎹 Quick setup: Standard layout",
                "🔤 Quick setup: Alphabetic layout",
                "📋 View configuration",
                "🗑️  Clear configuration",
                "💾 Save configuration"
            ]
            
            display_menu("KEYBOARD CONFIGURATION", menu_items)
            choice = get_menu_choice(9)
            
            if choice == 0:
                if confirm("Discard configuration?"):
                    break
            elif choice == 1:
                # Use advanced keyboard builder
                result = self.keyboard_builder.run_complete_builder(config["keys"])
                if result is not None:
                    config["keys"] = result
            elif choice == 2:
                self._configure_single_key(config["keys"])
            elif choice == 3:
                self.keyboard_builder.apply_numpad_preset(config["keys"])
            elif choice == 4:
                self.keyboard_builder.apply_function_keys_preset(config["keys"])
            elif choice == 5:
                self.keyboard_builder.apply_standard_layout(config["keys"])
            elif choice == 6:
                self.keyboard_builder.apply_alphabetic_layout(config["keys"])
            elif choice == 7:
                self.keyboard_builder.display_keyboard_matrix(config["keys"], "CURRENT CONFIGURATION")
                pause_for_user()
            elif choice == 8:
                if confirm("Clear all keys?"):
                    config["keys"] = {}
            elif choice == 9:
                self._save_keyboard_config(config)
                break
    
    def create_device_batch(self):
        """Create a new device command batch"""
        print("\n🎮 CREATE DEVICE COMMAND BATCH")
        print("="*50)
        
        # Get metadata
        name = get_text_input("Batch name: ") or "My Commands"
        description = get_text_input("Description (optional): ") or ""
        
        config = {
            "type": "device_batch",
            "metadata": {
                "name": name
            },
            "commands": {}
        }
        
        if description:
            config["metadata"]["description"] = description
        
        # Add commands
        while True:
            self._display_commands_status(config["commands"])
            
            menu_items = [
                "Add LED command",
                "Add buzzer command",
                "Add orientation command",
                "Add language command",
                "Quick setup: Initial setup",
                "Quick setup: Demo sequence",
                "Remove a command",
                "Clear all commands",
                "Save configuration"
            ]
            
            display_menu("DEVICE COMMANDS", menu_items)
            choice = get_menu_choice(9)
            
            if choice == 0:
                if confirm("Discard configuration?"):
                    break
            elif choice == 1:
                self._add_led_command(config["commands"])
            elif choice == 2:
                self._add_buzzer_command(config["commands"])
            elif choice == 3:
                self._add_orientation_command(config["commands"])
            elif choice == 4:
                self._add_language_command(config["commands"])
            elif choice == 5:
                self._apply_initial_setup_preset(config["commands"])
            elif choice == 6:
                self._apply_demo_preset(config["commands"])
            elif choice == 7:
                self._remove_command(config["commands"])
            elif choice == 8:
                if confirm("Clear all commands?"):
                    config["commands"] = {}
            elif choice == 9:
                self._save_device_batch(config)
                break
    
    def edit_existing(self):
        """Edit an existing JSON file"""
        file_path = self.json_browser.display_json_menu()
        if not file_path:
            return
        
        data = self.json_browser.load_json(file_path)
        if not data:
            return
        
        print(f"\n✏️  Editing: {file_path.name}")
        
        if data.get("type") == "keyboard_configuration":
            self._edit_keyboard_config(data, file_path)
        elif data.get("type") == "device_batch":
            self._edit_device_batch(data, file_path)
        else:
            print("❌ Unknown configuration type")
            pause_for_user()
    
    def view_existing(self):
        """View an existing JSON file"""
        file_path = self.json_browser.display_json_menu()
        if file_path:
            self.json_browser.preview_json(file_path, max_lines=50)
            pause_for_user()
    
    def view_all_files(self):
        """View all available JSON files with info"""
        print("\n📋 ALL AVAILABLE JSON FILES")
        print("="*70)
        
        categories = [
            ("Templates", self.json_browser.list_templates()),
            ("Keyboard Configs", self.json_browser.list_keyboard_configs()),
            ("Device Commands", self.json_browser.list_device_commands())
        ]
        
        for category_name, files in categories:
            if files:
                print(f"\n{category_name}:")
                print("-"*40)
                for file_path in files:
                    info = self.json_browser.get_json_info(file_path)
                    print(f"  • {file_path.name}")
                    if info.get("metadata"):
                        meta = info["metadata"]
                        if meta.get("name"):
                            print(f"    Name: {meta['name']}")
                        if meta.get("description"):
                            print(f"    Desc: {meta['description']}")
        
        pause_for_user()
    
    # Helper methods for keyboard configuration
    
    
    def _configure_single_key(self, keys: Dict):
        """Configure a single key using the common builder"""
        key_id = get_int_input("Enter key ID (0-19): ", 0, 19)
        if key_id is None:
            return
        
        actions = self.keyboard_builder.configure_key_interactive(key_id)
        if actions:
            keys[str(key_id)] = actions
    
    
    def _create_actions_interactive(self) -> List[Dict]:
        """Create actions interactively"""
        actions = []
        
        while len(actions) < 10:
            print(f"\nAction {len(actions) + 1}/10:")
            action_type = get_choice_input(
                "Select action type: ",
                ["Text", "HID Key", "Consumer Key", "Finish"]
            )
            
            if action_type == "Finish" or not action_type:
                break
            elif action_type == "Text":
                text = get_text_input("Enter text (max 8 bytes): ", max_bytes=8)
                if text:
                    delay = get_int_input("Delay in ms (0-65535) [10]: ", 0, 65535) or 10
                    actions.append({"type": "text", "value": text, "delay": delay})
            elif action_type == "HID Key":
                print("\nCommon keys: ENTER=40, TAB=43, SPACE=44, ESC=41")
                keycode = get_int_input("HID keycode (0-255): ", 0, 255)
                if keycode is not None:
                    print("Modifiers: 0=None, 1=CTRL, 2=SHIFT, 4=ALT, 8=GUI")
                    modifier = get_int_input("Modifier (0-15) [0]: ", 0, 15) or 0
                    delay = get_int_input("Delay in ms (0-65535) [10]: ", 0, 65535) or 10
                    actions.append({
                        "type": "hid",
                        "keycode": keycode,
                        "modifier": modifier,
                        "delay": delay
                    })
            elif action_type == "Consumer Key":
                print("\nCommon: Play/Pause=205, Vol+=233, Vol-=234, Mute=226")
                code = get_int_input("Consumer code (0-65535): ", 0, 65535)
                if code is not None:
                    delay = get_int_input("Delay in ms (0-65535) [10]: ", 0, 65535) or 10
                    actions.append({
                        "type": "consumer",
                        "consumer_code": code,
                        "delay": delay
                    })
        
        return actions
    
    def _apply_numpad_preset(self, keys: Dict):
        """Apply simple numpad preset"""
        preset = {
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
        keys.update(preset)
        print("✅ Numpad preset applied")
    
    def _apply_function_preset(self, keys: Dict):
        """Apply function keys preset"""
        preset = {}
        for i in range(12):
            # F1-F12 are HID codes 58-69
            preset[str(i)] = [{
                "type": "hid",
                "keycode": 58 + i,
                "modifier": 0,
                "delay": 10
            }]
        keys.update(preset)
        print("✅ Function keys preset applied (F1-F12)")
    
    def _clear_key(self, keys: Dict):
        """Clear a specific key"""
        key_id = get_text_input("Enter key ID to clear: ")
        if key_id in keys:
            del keys[key_id]
            print(f"✅ Key {key_id} cleared")
        else:
            print(f"❌ Key {key_id} not configured")
    
    # Helper methods for device commands
    
    def _display_commands_status(self, commands: Dict):
        """Display current commands"""
        print(f"\n🎮 Current Commands: {len(commands)}")
        if commands:
            for i, (cmd_name, params) in enumerate(commands.items(), 1):
                print(f"  {i}. {cmd_name}: {params}")
        print()
    
    def _add_led_command(self, commands: Dict):
        """Add LED command"""
        led_type = get_choice_input(
            "LED command type: ",
            ["LED On", "LED Off", "LED Blink", "All LEDs Off"]
        )
        
        if led_type == "LED On":
            led_id = get_int_input("LED ID (1-9): ", 1, 9)
            if led_id:
                commands[f"led_{led_id}_on"] = {}
        elif led_type == "LED Off":
            led_id = get_int_input("LED ID (1-9): ", 1, 9)
            if led_id:
                commands[f"led_{led_id}_off"] = {}
        elif led_type == "LED Blink":
            led_id = get_int_input("LED ID (1-9): ", 1, 9)
            freq = get_int_input("Frequency (1-20 Hz): ", 1, 20)
            if led_id and freq:
                commands[f"led_{led_id}_blink_{freq}hz"] = {"frequency": freq}
        elif led_type == "All LEDs Off":
            commands["all_leds_off"] = {}
    
    def _add_buzzer_command(self, commands: Dict):
        """Add buzzer command"""
        buzzer_type = get_choice_input(
            "Buzzer command type: ",
            ["Play Melody", "Beep", "Stop"]
        )
        
        if buzzer_type == "Play Melody":
            melodies = ["SUCCESS", "ERROR", "WARNING", "START", "STOP", "KEY", "CONNECTION", "NOTIFICATION"]
            melody = get_choice_input("Select melody: ", melodies)
            if melody:
                commands[f"buzzer_{melody.lower()}"] = {}
        elif buzzer_type == "Beep":
            duration = get_int_input("Duration (50-5000 ms): ", 50, 5000)
            if duration:
                commands[f"buzzer_beep_{duration}ms"] = {"duration": duration}
        elif buzzer_type == "Stop":
            commands["buzzer_stop"] = {}
    
    def _add_orientation_command(self, commands: Dict):
        """Add orientation command"""
        orientations = ["Portrait", "Landscape Right", "Inverted", "Landscape Left"]
        orientation = get_choice_input("Select orientation: ", orientations)
        if orientation:
            value = orientations.index(orientation)
            name = orientation.lower().replace(" ", "_")
            commands[f"orientation_{name}"] = {"value": value}
    
    def _add_language_command(self, commands: Dict):
        """Add language command"""
        languages = {
            "English US": "0x0409",
            "French": "0x040C",
            "German": "0x0407",
            "Spanish": "0x040A"
        }
        
        lang_names = list(languages.keys())
        language = get_choice_input("Select language: ", lang_names)
        if language:
            commands[f"language_{language.lower().replace(' ', '_')}"] = {
                "value": languages[language]
            }
    
    def _apply_initial_setup_preset(self, commands: Dict):
        """Apply initial setup preset"""
        preset = {
            "orientation_landscape_right": {"value": 1},
            "language_english_us": {"value": "0x0409"},
            "all_leds_off": {},
            "led_1_on": {},
            "buzzer_start": {}
        }
        commands.update(preset)
        print("✅ Initial setup preset applied")
    
    def _apply_demo_preset(self, commands: Dict):
        """Apply demo sequence preset"""
        preset = {
            "led_1_on": {},
            "buzzer_key": {},
            "led_1_off": {},
            "led_2_on": {},
            "buzzer_key": {},
            "led_2_off": {},
            "led_3_on": {},
            "buzzer_key": {},
            "all_leds_off": {},
            "buzzer_success": {}
        }
        commands.update(preset)
        print("✅ Demo sequence preset applied")
    
    def _remove_command(self, commands: Dict):
        """Remove a command"""
        if not commands:
            print("❌ No commands to remove")
            return
        
        cmd_list = list(commands.keys())
        cmd = get_choice_input("Select command to remove: ", cmd_list)
        if cmd and cmd in commands:
            del commands[cmd]
            print(f"✅ Command '{cmd}' removed")
    
    # Save methods
    
    def _save_keyboard_config(self, config: Dict):
        """Save keyboard configuration"""
        filename = get_text_input("Filename (without .json): ")
        if not filename:
            filename = config["metadata"]["name"].lower().replace(" ", "_")
        
        file_path = self.json_browser.keyboard_configs_dir / f"{filename}.json"
        if self.json_browser.save_json(config, file_path):
            print(f"✅ Saved to {file_path}")
            pause_for_user()
    
    def _save_device_batch(self, config: Dict):
        """Save device command batch"""
        filename = get_text_input("Filename (without .json): ")
        if not filename:
            filename = config["metadata"]["name"].lower().replace(" ", "_")
        
        file_path = self.json_browser.device_commands_dir / f"{filename}.json"
        if self.json_browser.save_json(config, file_path):
            print(f"✅ Saved to {file_path}")
            pause_for_user()
    
    def _edit_keyboard_config(self, data: Dict, file_path: Path):
        """Edit keyboard configuration (simplified)"""
        print("✏️  Editing keyboard configuration...")
        print("(Full editing not implemented yet - use create new instead)")
        pause_for_user()
    
    def _edit_device_batch(self, data: Dict, file_path: Path):
        """Edit device batch (simplified)"""
        print("✏️  Editing device batch...")
        print("(Full editing not implemented yet - use create new instead)")
        pause_for_user()


def main():
    """Main entry point"""
    app = InteractiveJSONCreator()
    app.run()


if __name__ == "__main__":
    main()