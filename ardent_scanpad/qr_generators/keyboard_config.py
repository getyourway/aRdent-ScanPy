"""
Keyboard Configuration QR Generator

Hybrid API for keyboard configuration:
- JSON-driven approach for GUI applications
- Traditional methods for direct programming
- Both use the same modular QR backend
"""

import logging
from typing import Dict, Any, List, Union, Optional
from pathlib import Path

from .utils.json_support import JSONValidator, JSONConverter
from .utils.qr_core import QRCore, QRCommand
from ..utils.constants import HIDKeyCodes


class KeyboardConfigGenerator:
    """
    Hybrid keyboard configuration generator
    
    Supports both JSON-driven and traditional API approaches
    """
    
    def __init__(self):
        self._qr_core = QRCore()
        self._logger = logging.getLogger(self.__class__.__name__)
    
    # ===== JSON API =====
    
    def from_json_file(self, filepath: Union[str, Path]) -> List[QRCommand]:
        """
        Generate QR codes from JSON configuration file
        
        Args:
            filepath: Path to JSON configuration file
            
        Returns:
            List of QRCommand objects
        """
        json_data = JSONValidator.load_json_file(filepath)
        return self.from_json(json_data)
    
    def from_json(self, json_data: Dict[str, Any]) -> List[QRCommand]:
        """
        Generate QR codes from JSON configuration
        
        Args:
            json_data: JSON configuration dict
            
        Returns:
            List of QRCommand objects
        """
        # Validate JSON structure
        JSONValidator.validate_keyboard_json(json_data)
        
        # Convert to internal format
        keyboard_config = JSONConverter.json_to_keyboard_config(json_data)
        
        # Get options
        options = json_data.get('options', {})
        qr_format = options.get('qr_format', 'full')
        compression_level = options.get('compression_level', 6)
        
        # Generate QR codes based on format
        if qr_format == 'individual':
            return self._generate_individual_commands(keyboard_config)
        else:  # 'full' format (default)
            full_qr = self._qr_core.create_full_keyboard_config(keyboard_config, compression_level)
            return [full_qr]
    
    def to_json(self, keyboard_config: Dict[int, List[Dict[str, Any]]], 
               metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Convert keyboard configuration to JSON format
        
        Args:
            keyboard_config: Internal keyboard config format
            metadata: Optional metadata for JSON
            
        Returns:
            JSON-compatible dictionary
        """
        return JSONConverter.keyboard_config_to_json(keyboard_config, metadata)
    
    def save_json(self, keyboard_config: Dict[int, List[Dict[str, Any]]], 
                 filepath: Union[str, Path],
                 metadata: Optional[Dict[str, Any]] = None) -> None:
        """Save keyboard configuration as JSON file"""
        import json
        
        json_data = self.to_json(keyboard_config, metadata)
        filepath = Path(filepath)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        self._logger.info(f"Saved keyboard configuration to {filepath}")
    
    # ===== Traditional API =====
    
    def create_text_action(self, text: str) -> Dict[str, Any]:
        """Create text action (traditional API)"""
        return self._qr_core.create_text_action(text)
    
    def create_hid_action(self, keycode: int, modifier: int = 0, delay: int = 10) -> Dict[str, Any]:
        """Create HID action (traditional API)"""
        return self._qr_core.create_hid_action(keycode, modifier, delay)
    
    def create_consumer_action(self, control_code: int, delay: int = 10) -> Dict[str, Any]:
        """Create consumer control action (traditional API)"""
        return self._qr_core.create_consumer_action(control_code, delay)
    
    def create_key_config_command(self, key_id: int, actions: List[Dict[str, Any]]) -> QRCommand:
        """Create single key configuration QR (traditional API)"""
        return self._qr_core.create_key_config_command(key_id, actions)
    
    def create_full_keyboard_config(self, keyboard_config: Dict[int, List[Dict[str, Any]]],
                                   compression_level: int = 6) -> QRCommand:
        """Create full keyboard configuration QR (traditional API)"""
        return self._qr_core.create_full_keyboard_config(keyboard_config, compression_level)
    
    # ===== Preset Configurations =====
    
    def create_numpad_config(self) -> QRCommand:
        """
        Create standard numeric keypad configuration (keys 0-9)
        
        Returns:
            QRCommand with numeric keypad layout
        """
        config = {}
        
        # Keys 0-9 with corresponding numbers
        for i in range(10):
            config[i] = [self.create_text_action(str(i))]
            
        return self.create_full_keyboard_config(config)
    
    def create_alpha_config(self) -> QRCommand:
        """
        Create standard alphabetic configuration (A-P for keys 0-15)
        
        Returns:
            QRCommand with alphabetic layout
        """
        config = {}
        
        # Keys 0-15 with letters A-P
        for i in range(16):
            letter = chr(ord('A') + i)  # A, B, C, ..., P
            config[i] = [self.create_text_action(letter)]
            
        return self.create_full_keyboard_config(config)
    
    def create_function_keys_config(self) -> QRCommand:
        """
        Create function keys configuration (F1-F12 + Enter/Esc/etc.)
        
        Returns:
            QRCommand with function keys layout
        """
        config = {}
        
        # F1-F12 on keys 0-11
        for i in range(12):
            f_key = HIDKeyCodes.F1 + i  # F1=0x3A, F2=0x3B, etc.
            config[i] = [self.create_hid_action(f_key)]
        
        # Special keys on remaining positions
        config[12] = [self.create_hid_action(HIDKeyCodes.ENTER)]     # Enter
        config[13] = [self.create_hid_action(HIDKeyCodes.ESCAPE)]    # Escape  
        config[14] = [self.create_hid_action(HIDKeyCodes.TAB)]       # Tab
        config[15] = [self.create_hid_action(HIDKeyCodes.BACKSPACE)] # Backspace
        
        return self.create_full_keyboard_config(config)
    
    def create_arrow_numpad_config(self) -> QRCommand:
        """
        Create configuration with arrow keys and numpad
        
        Returns:
            QRCommand with arrow keys + numpad layout
        """
        config = {}
        
        # Numbers 0-9 on keys 0-9
        for i in range(10):
            config[i] = [self.create_text_action(str(i))]
        
        # Arrow keys on keys 12-15
        config[12] = [self.create_hid_action(HIDKeyCodes.UP_ARROW)]    # ↑
        config[13] = [self.create_hid_action(HIDKeyCodes.LEFT_ARROW)]  # ←
        config[14] = [self.create_hid_action(HIDKeyCodes.DOWN_ARROW)]  # ↓
        config[15] = [self.create_hid_action(HIDKeyCodes.RIGHT_ARROW)] # →
        
        # Special keys
        config[10] = [self.create_text_action(".")]                    # Decimal
        config[11] = [self.create_hid_action(HIDKeyCodes.ENTER)]       # Enter
        
        return self.create_full_keyboard_config(config)
    
    def create_warehouse_config(self) -> QRCommand:
        """
        Create warehouse/logistics keyboard configuration
        
        Returns:
            QRCommand optimized for warehouse operations
        """
        config = {}
        
        # Numbers for quantity/item codes
        for i in range(10):
            config[i] = [self.create_text_action(str(i))]
        
        # Common warehouse operations
        config[10] = [self.create_text_action("QTY: ")]               # Quantity prefix
        config[11] = [self.create_text_action("LOC: ")]               # Location prefix
        config[12] = [self.create_text_action("SKU: ")]               # SKU prefix  
        config[13] = [self.create_text_action("\n")]                  # New line
        config[14] = [self.create_hid_action(HIDKeyCodes.TAB)]        # Tab
        config[15] = [self.create_hid_action(HIDKeyCodes.ENTER)]      # Enter
        
        return self.create_full_keyboard_config(config)
    
    def create_pos_config(self) -> QRCommand:
        """
        Create Point of Sale keyboard configuration
        
        Returns:  
            QRCommand optimized for POS operations
        """
        config = {}
        
        # Numbers for prices/quantities
        for i in range(10):
            config[i] = [self.create_text_action(str(i))]
        
        # POS operations
        config[10] = [self.create_text_action(".")]                   # Decimal point
        config[11] = [self.create_text_action("$")]                   # Currency symbol
        config[12] = [self.create_text_action(" x")]                  # Multiply (quantity)
        config[13] = [self.create_text_action("+")]                   # Add item
        config[14] = [self.create_hid_action(HIDKeyCodes.TAB)]        # Next field
        config[15] = [self.create_hid_action(HIDKeyCodes.ENTER)]      # Confirm
        
        return self.create_full_keyboard_config(config)
    
    # ===== Utility Methods =====
    
    def _generate_individual_commands(self, keyboard_config: Dict[int, List[Dict[str, Any]]]) -> List[QRCommand]:
        """Generate individual QR commands for each key"""
        commands = []
        
        for key_id, actions in keyboard_config.items():
            qr_command = self.create_key_config_command(key_id, actions)
            commands.append(qr_command)
        
        return commands
    
    def save_qr_codes(self, qr_commands: List[QRCommand], output_dir: Union[str, Path],
                     filename_prefix: str = "keyboard_", **kwargs) -> List[str]:
        """
        Save QR codes to files
        
        Args:
            qr_commands: List of QRCommand objects
            output_dir: Output directory
            filename_prefix: Filename prefix
            **kwargs: Additional QR generation options
            
        Returns:
            List of saved file paths
        """
        return self._qr_core.save_multiple_qr_codes(
            qr_commands, output_dir, filename_prefix, **kwargs
        )
    
    def create_quick_text_key(self, key_id: int, text: str) -> QRCommand:
        """Quick method to create single-text-action key"""
        action = self.create_text_action(text)
        return self.create_key_config_command(key_id, [action])
    
    def create_quick_hid_key(self, key_id: int, keycode: int, modifier: int = 0) -> QRCommand:
        """Quick method to create single-HID-action key"""
        action = self.create_hid_action(keycode, modifier)
        return self.create_key_config_command(key_id, [action])