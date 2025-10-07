"""
QR Core Integration

Bridge between new QR generators and existing modular QR system
"""

from typing import List, Dict, Any
from ...controllers.qr.commands import (
    CommandData, LEDCommandBuilder, BuzzerCommandBuilder, 
    DeviceCommandBuilder, KeyConfigCommandBuilder, 
    FullConfigCommandBuilder, LuaCommandBuilder
)
from ...controllers.qr.formats import QRFormatter
from ...controllers.qr.images import QRImageSaver


class QRCommand:
    """
    QR Command wrapper - compatible with existing API
    Bridges new modular system with legacy QRCommand interface
    """
    
    def __init__(self, command_data: CommandData, qr_formatter: QRFormatter = None):
        self._command_data = command_data
        self._qr_formatter = qr_formatter or QRFormatter()
        self._qr_image_saver = QRImageSaver()
        
        # Generate formatted QR string
        self.command_data = self._qr_formatter.format_command(command_data)
        self.command_type = command_data.command_type
        self.description = command_data.description
        self.metadata = command_data.metadata.copy()
    
    def generate_qr_image(self, **kwargs):
        """Generate QR image using modular system"""
        return self._qr_image_saver._generator.generate_qr_image(
            self.command_data,
            title=self.command_type,
            description=self.description,
            **kwargs
        )
    
    def save(self, filename, **kwargs) -> bool:
        """Save QR code as PNG"""
        return self._qr_image_saver.save_qr_image(
            self.command_data,
            filename,
            title=self.command_type,
            description=self.description,
            **kwargs
        )
    
    def __str__(self) -> str:
        return f"QRCommand({self.command_type}: {self.description})"


class QRCore:
    """
    Core QR generation engine
    Provides unified interface to all command builders
    """
    
    def __init__(self):
        self._led_builder = LEDCommandBuilder()
        self._buzzer_builder = BuzzerCommandBuilder()
        self._device_builder = DeviceCommandBuilder()
        self._key_builder = KeyConfigCommandBuilder()
        self._full_builder = FullConfigCommandBuilder()
        self._lua_builder = LuaCommandBuilder()
        self._formatter = QRFormatter()
        self._image_saver = QRImageSaver()
    
    # ===== LED Commands =====
    def create_led_on_command(self, led_id: int) -> QRCommand:
        cmd_data = self._led_builder.create_led_on_command(led_id)
        return QRCommand(cmd_data, self._formatter)
    
    def create_led_off_command(self, led_id: int) -> QRCommand:
        cmd_data = self._led_builder.create_led_off_command(led_id)
        return QRCommand(cmd_data, self._formatter)
    
    def create_all_leds_off_command(self) -> QRCommand:
        cmd_data = self._led_builder.create_all_leds_off_command()
        return QRCommand(cmd_data, self._formatter)
    
    # ===== Buzzer Commands =====
    def create_buzzer_melody_command(self, melody_name: str) -> QRCommand:
        cmd_data = self._buzzer_builder.create_buzzer_melody_command(melody_name)
        return QRCommand(cmd_data, self._formatter)
    
    # ===== Device Commands =====
    def create_orientation_command(self, orientation: int) -> QRCommand:
        cmd_data = self._device_builder.create_orientation_command(orientation)
        return QRCommand(cmd_data, self._formatter)
    
    def create_lua_clear_command(self) -> QRCommand:
        cmd_data = self._device_builder.create_lua_clear_command()
        return QRCommand(cmd_data, self._formatter)
    
    def create_lua_info_command(self) -> QRCommand:
        cmd_data = self._device_builder.create_lua_info_command()
        return QRCommand(cmd_data, self._formatter)
    
    # ===== Key Configuration =====
    def create_text_action(self, text: str) -> Dict[str, Any]:
        return self._key_builder.create_text_action(text)
    
    def create_hid_action(self, keycode: int, modifier: int = 0, delay: int = 10) -> Dict[str, Any]:
        return self._key_builder.create_hid_action(keycode, modifier, delay)
    
    def create_consumer_action(self, control_code: int, delay: int = 10) -> Dict[str, Any]:
        return self._key_builder.create_consumer_action(control_code, delay)

    def create_modifier_toggle_action(self, modifier_mask: int, delay: int = 10) -> Dict[str, Any]:
        return self._key_builder.create_modifier_toggle_action(modifier_mask, delay)
    
    def create_key_config_command(self, key_id: int, actions: list) -> QRCommand:
        cmd_data = self._key_builder.create_key_config_command(key_id, actions)
        return QRCommand(cmd_data, self._formatter)
    
    # ===== Full Configuration =====
    def create_full_keyboard_config(self, keyboard_config: Dict[int, List[Dict[str, Any]]], 
                                   compression_level: int = 6) -> QRCommand:
        cmd_data = self._full_builder.create_full_keyboard_config(keyboard_config, compression_level)
        return QRCommand(cmd_data, self._formatter)
    
    # ===== Lua Scripts =====
    def create_lua_script_qr(self, script_content: str, max_qr_size: int = 1000, 
                            compression_level: int = 6) -> List[QRCommand]:
        cmd_data_list = self._lua_builder.create_lua_script_commands(
            script_content, max_qr_size, compression_level
        )
        return [QRCommand(cmd_data, self._formatter) for cmd_data in cmd_data_list]
    
    def create_lua_script_from_file(self, script_path, **kwargs) -> List[QRCommand]:
        cmd_data_list = self._lua_builder.create_lua_script_from_file(script_path, **kwargs)
        return [QRCommand(cmd_data, self._formatter) for cmd_data in cmd_data_list]
    
    # ===== Batch Operations =====
    def save_multiple_qr_codes(self, commands: List[QRCommand], output_dir, 
                              filename_prefix: str = "qr_", **kwargs) -> List[str]:
        """Save multiple QR codes using modular image system"""
        qr_data_list = []
        
        for cmd in commands:
            qr_data_list.append({
                'qr_data': cmd.command_data,
                'title': cmd.command_type,
                'description': cmd.description
            })
        
        return self._image_saver.save_multiple_qr_images(
            qr_data_list, output_dir, filename_prefix, **kwargs
        )
    
    def save_lua_script_qr_sequence(self, script_content: str, output_dir, 
                                   filename_prefix: str = "lua_script_", **kwargs) -> List[str]:
        """Generate and save Lua script QR sequence"""
        # Generate QR commands
        qr_commands = self.create_lua_script_qr(script_content, **kwargs)
        
        # Prepare data for specialized Lua saver
        qr_data_list = []
        for cmd in qr_commands:
            qr_data_list.append({
                'qr_data': cmd.command_data,
                'title': cmd.command_type,
                'description': cmd.description
            })
        
        return self._image_saver.save_lua_script_sequence(
            qr_data_list, output_dir, filename_prefix
        )