"""
JSON Browser for Interactive Examples

Provides functionality to browse and load JSON configurations
from the centralized JSON directory.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from .ui_helpers import display_menu, get_menu_choice, pause_for_user


class JSONBrowser:
    """Browse and load JSON configurations"""
    
    def __init__(self, json_dir: Path = None):
        """
        Initialize JSON browser
        
        Args:
            json_dir: Path to JSON directory (auto-detected if None)
        """
        if json_dir is None:
            # Auto-detect JSON directory relative to examples folder
            examples_dir = Path(__file__).parent.parent
            json_dir = examples_dir / "json"
        
        self.json_dir = json_dir
        self.templates_dir = json_dir / "templates"
        self.keyboard_configs_dir = json_dir / "keyboard-configs"
        self.device_commands_dir = json_dir / "device-commands"
    
    def list_templates(self) -> List[Path]:
        """List available JSON templates"""
        if not self.templates_dir.exists():
            return []
        return sorted(self.templates_dir.glob("*.json"))
    
    def list_keyboard_configs(self) -> List[Path]:
        """List available keyboard configuration examples"""
        if not self.keyboard_configs_dir.exists():
            return []
        return sorted(self.keyboard_configs_dir.glob("*.json"))
    
    def list_device_commands(self) -> List[Path]:
        """List available device command examples"""
        if not self.device_commands_dir.exists():
            return []
        return sorted(self.device_commands_dir.glob("*.json"))
    
    def load_json(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Load and parse a JSON file
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            Parsed JSON data or None if error
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading JSON: {e}")
            return None
    
    def display_json_menu(self, category: str = "all") -> Optional[Path]:
        """
        Display menu to select a JSON file
        
        Args:
            category: Type of JSON to show ("templates", "keyboard", "device", "all")
            
        Returns:
            Selected file path or None
        """
        files = []
        
        if category in ["templates", "all"]:
            templates = self.list_templates()
            for f in templates:
                files.append(("📄 Template", f))
        
        if category in ["keyboard", "all"]:
            keyboards = self.list_keyboard_configs()
            for f in keyboards:
                files.append(("⌨️  Keyboard", f))
        
        if category in ["device", "all"]:
            devices = self.list_device_commands()
            for f in devices:
                files.append(("🎮 Device", f))
        
        if not files:
            print("❌ No JSON files found")
            pause_for_user()
            return None
        
        # Build menu items
        menu_items = []
        for file_type, file_path in files:
            name = file_path.stem.replace('_', ' ').title()
            menu_items.append(f"{file_type}: {name}")
        
        display_menu("Available JSON Files", menu_items)
        
        choice = get_menu_choice(len(menu_items))
        if choice and 0 < choice <= len(files):
            return files[choice - 1][1]
        
        return None
    
    def preview_json(self, file_path: Path, max_lines: int = 20) -> None:
        """
        Preview JSON file contents
        
        Args:
            file_path: Path to JSON file
            max_lines: Maximum lines to display
        """
        data = self.load_json(file_path)
        if data:
            print(f"\n📄 Preview of {file_path.name}:")
            print("-" * 50)
            
            # Pretty print with indentation
            json_str = json.dumps(data, indent=2, ensure_ascii=False)
            lines = json_str.split('\n')
            
            if len(lines) > max_lines:
                for line in lines[:max_lines]:
                    print(line)
                print(f"... ({len(lines) - max_lines} more lines)")
            else:
                print(json_str)
            
            print("-" * 50)
    
    def get_json_info(self, file_path: Path) -> Dict[str, Any]:
        """
        Get information about a JSON file
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            Dict with file information
        """
        data = self.load_json(file_path)
        if not data:
            return {}
        
        info = {
            "name": file_path.stem,
            "path": str(file_path),
            "type": data.get("type", "unknown")
        }
        
        # Add metadata if available
        if "metadata" in data:
            info["metadata"] = data["metadata"]
        
        # Add type-specific info
        if data.get("type") == "keyboard_configuration":
            if "keys" in data:
                info["keys_count"] = len(data["keys"])
            elif "matrix_keys" in data:
                info["keys_count"] = len(data["matrix_keys"])
        elif data.get("type") == "device_batch":
            if "commands" in data:
                info["commands_count"] = len(data["commands"])
        
        return info
    
    def save_json(self, data: Dict[str, Any], file_path: Path) -> bool:
        """
        Save data to a JSON file
        
        Args:
            data: Data to save
            file_path: Path where to save
            
        Returns:
            True if successful
        """
        try:
            # Create parent directory if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Saved to {file_path}")
            return True
        except Exception as e:
            print(f"❌ Error saving JSON: {e}")
            return False