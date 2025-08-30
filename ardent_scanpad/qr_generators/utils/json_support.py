"""
JSON Support for QR Generators

Handles JSON parsing, validation and conversion to internal structures
"""

import json
import logging
from typing import Dict, Any, List, Union
from pathlib import Path

logger = logging.getLogger(__name__)


class JSONValidator:
    """JSON validation and parsing"""
    
    @staticmethod
    def load_json_file(filepath: Union[str, Path]) -> Dict[str, Any]:
        """Load JSON from file with error handling"""
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"JSON file not found: {filepath}")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Loaded JSON from {filepath}")
            return data
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {filepath}: {e}")
        except Exception as e:
            raise ValueError(f"Failed to read {filepath}: {e}")
    
    @staticmethod
    def validate_json_structure(data: Dict[str, Any], required_fields: List[str]) -> None:
        """Validate JSON has required fields"""
        if not isinstance(data, dict):
            raise ValueError("JSON must be an object")
        
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
    
    @staticmethod
    def validate_keyboard_json(data: Dict[str, Any]) -> None:
        """Validate keyboard configuration JSON structure"""
        JSONValidator.validate_json_structure(data, ['type'])
        
        if data.get('type') not in ['keyboard_configuration', 'full_keyboard']:
            raise ValueError(f"Invalid type for keyboard JSON: {data.get('type')}")
        
        # Support both modern KISS format (keys) and legacy format (matrix_keys)
        keys_to_validate = None
        
        if 'keys' in data:
            # Modern KISS format with unified keys 0-19
            keys_to_validate = data['keys']
        elif 'matrix_keys' in data:
            # Legacy format
            keys_to_validate = data['matrix_keys']
        else:
            raise ValueError("JSON must contain 'keys' (modern format) or 'matrix_keys' (legacy format)")
        
        # Validate the keys
        if not isinstance(keys_to_validate, dict):
            raise ValueError("keys/matrix_keys must be an object")
        
        for key_id_str, actions in keys_to_validate.items():
            # Validate key ID
            try:
                key_id = int(key_id_str)
                if not (0 <= key_id <= 19):
                    raise ValueError(f"Key ID must be 0-19, got {key_id}")
            except ValueError:
                raise ValueError(f"Invalid key ID: {key_id_str}")
            
            # Validate actions
            if not isinstance(actions, list) or not actions:
                raise ValueError(f"Key {key_id} must have non-empty actions list")
            
            if len(actions) > 10:
                raise ValueError(f"Key {key_id} has too many actions (max 10): {len(actions)}")
            
            for i, action in enumerate(actions):
                JSONValidator._validate_action(action, f"Key {key_id} action {i}")
        
        # Validate external_buttons if present in legacy format
        if 'external_buttons' in data:
            external_buttons = data['external_buttons']
            if not isinstance(external_buttons, dict):
                raise ValueError("external_buttons must be an object")
            
            valid_buttons = {"scan_trigger_double", "scan_trigger_long", "power_single", "power_double"}
            for button_name, actions in external_buttons.items():
                if button_name not in valid_buttons:
                    raise ValueError(f"Invalid external button name: {button_name}")
                
                if not isinstance(actions, list) or not actions:
                    raise ValueError(f"External button {button_name} must have non-empty actions list")
                
                if len(actions) > 10:
                    raise ValueError(f"External button {button_name} has too many actions (max 10): {len(actions)}")
                
                for i, action in enumerate(actions):
                    JSONValidator._validate_action(action, f"External button {button_name} action {i}")
    
    @staticmethod
    def validate_device_json(data: Dict[str, Any]) -> None:
        """Validate device command JSON structure"""
        JSONValidator.validate_json_structure(data, ['type'])
        
        valid_types = ['device_command', 'device_batch', 'single_command']
        if data.get('type') not in valid_types:
            raise ValueError(f"Invalid type for device JSON: {data.get('type')} (must be one of {valid_types})")
        
        # Validate commands if present
        if 'commands' in data:
            commands = data['commands']
            if not isinstance(commands, list):
                raise ValueError("commands must be a list")
            
            for i, cmd in enumerate(commands):
                JSONValidator._validate_device_command(cmd, f"Command {i}")
    
    @staticmethod
    def _validate_action(action: Dict[str, Any], context: str) -> None:
        """Validate individual action structure"""
        if not isinstance(action, dict):
            raise ValueError(f"{context}: action must be an object")
        
        if 'type' not in action:
            raise ValueError(f"{context}: action must have 'type' field")
        
        action_type = action['type']
        
        if action_type == 'text':
            if 'value' not in action:
                raise ValueError(f"{context}: text action must have 'value' field")
            
            text = action['value']
            if not isinstance(text, str):
                raise ValueError(f"{context}: text action value must be string")
            
            if len(text.encode('utf-8')) > 8:
                raise ValueError(f"{context}: text too long (max 8 UTF-8 bytes): {text}")
        
        elif action_type == 'hid':
            if 'keycode' not in action:
                raise ValueError(f"{context}: HID action must have 'keycode' field")
            
            keycode = action['keycode']
            if not isinstance(keycode, int) or not (0 <= keycode <= 255):
                raise ValueError(f"{context}: HID keycode must be 0-255, got {keycode}")
            
            modifier = action.get('modifier', 0)
            if not isinstance(modifier, int) or not (0 <= modifier <= 255):
                raise ValueError(f"{context}: HID modifier must be 0-255, got {modifier}")
        
        elif action_type == 'consumer':
            if 'control_code' not in action:
                raise ValueError(f"{context}: consumer action must have 'control_code' field")
            
            code = action['control_code']
            if not isinstance(code, int) or not (0 <= code <= 65535):
                raise ValueError(f"{context}: consumer control code must be 0-65535, got {code}")
        
        else:
            raise ValueError(f"{context}: unsupported action type: {action_type}")
    
    @staticmethod  
    def _validate_device_command(cmd: Dict[str, Any], context: str) -> None:
        """Validate device command structure"""
        if not isinstance(cmd, dict):
            raise ValueError(f"{context}: command must be an object")
        
        required = ['domain', 'action']
        for field in required:
            if field not in cmd:
                raise ValueError(f"{context}: missing required field '{field}'")
        
        domain = cmd['domain']
        action = cmd['action']
        
        # Basic validation - specific validation done in generators
        valid_domains = ['device_settings', 'led_control', 'buzzer_control', 'power_management', 'lua_management']
        if domain not in valid_domains:
            raise ValueError(f"{context}: invalid domain '{domain}' (must be one of {valid_domains})")
        
        if not isinstance(action, str):
            raise ValueError(f"{context}: action must be string")
        
        if 'parameters' in cmd and not isinstance(cmd['parameters'], dict):
            raise ValueError(f"{context}: parameters must be an object")


class JSONConverter:
    """Convert JSON structures to internal formats"""
    
    @staticmethod
    def json_to_keyboard_config(data: Dict[str, Any]) -> Dict[int, List[Dict[str, Any]]]:
        """Convert JSON keyboard config to internal format"""
        # Support both modern KISS format (keys) and legacy format (matrix_keys)
        keys_data = None
        
        if 'keys' in data:
            # Modern KISS format with unified keys 0-19
            keys_data = data['keys']
        elif 'matrix_keys' in data:
            # Legacy format - combine matrix_keys and external_buttons
            keys_data = data['matrix_keys'].copy()
            
            # Add external buttons if present, mapping to key IDs 16-19
            if 'external_buttons' in data:
                button_map = {
                    "scan_trigger_double": 16,
                    "scan_trigger_long": 17, 
                    "power_single": 18,
                    "power_double": 19
                }
                
                for button_name, actions in data['external_buttons'].items():
                    key_id = button_map.get(button_name)
                    if key_id is not None:
                        keys_data[str(key_id)] = actions
        else:
            raise ValueError("JSON must contain 'keys' (modern format) or 'matrix_keys' (legacy format)")
        
        keyboard_config = {}
        
        for key_id_str, json_actions in keys_data.items():
            key_id = int(key_id_str)
            actions = []
            
            for json_action in json_actions:
                action = JSONConverter._json_to_action(json_action)
                actions.append(action)
            
            keyboard_config[key_id] = actions
        
        return keyboard_config
    
    @staticmethod
    def _json_to_action(json_action: Dict[str, Any]) -> Dict[str, Any]:
        """Convert JSON action to internal action format"""
        action_type = json_action['type']
        delay = json_action.get('delay', 10)
        
        if action_type == 'text':
            from ...utils.constants import KeyTypes
            return {
                'type': KeyTypes.UTF8,
                'text': json_action['value'],
                'delay': delay
            }
        
        elif action_type == 'hid':
            from ...utils.constants import KeyTypes
            return {
                'type': KeyTypes.HID,
                'value': json_action['keycode'],
                'mask': json_action.get('modifier', 0),
                'delay': delay
            }
        
        elif action_type == 'consumer':
            from ...utils.constants import KeyTypes
            return {
                'type': KeyTypes.CONSUMER,
                'value': json_action['control_code'],
                'delay': delay
            }
        
        else:
            raise ValueError(f"Unsupported action type: {action_type}")
    
    @staticmethod
    def keyboard_config_to_json(keyboard_config: Dict[int, List[Dict[str, Any]]], 
                               metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Convert internal keyboard config to JSON format"""
        from ...utils.constants import KeyTypes
        
        json_data = {
            'type': 'keyboard_configuration',
            'metadata': metadata or {},
            'matrix_keys': {}
        }
        
        for key_id, actions in keyboard_config.items():
            json_actions = []
            
            for action in actions:
                json_action = {'delay': action.get('delay', 10)}
                
                if action['type'] == KeyTypes.UTF8:
                    json_action.update({
                        'type': 'text',
                        'value': action.get('text', '')
                    })
                
                elif action['type'] == KeyTypes.HID:
                    json_action.update({
                        'type': 'hid', 
                        'keycode': action.get('value', 0),
                        'modifier': action.get('mask', 0)
                    })
                
                elif action['type'] == KeyTypes.CONSUMER:
                    json_action.update({
                        'type': 'consumer',
                        'control_code': action.get('value', 0)
                    })
                
                json_actions.append(json_action)
            
            json_data['matrix_keys'][str(key_id)] = json_actions
        
        return json_data