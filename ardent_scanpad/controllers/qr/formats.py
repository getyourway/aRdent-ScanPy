"""
QR Protocol Formatters

Formats command data into QR scannable protocols:
- Device commands: $CMD:DEV:xxxx$
- Config commands: $CMD:KEY:xxxx$  
- Full keyboard: $FULL:xxxx$
- Lua scripts: $LUA1:/$LUA2:/$LUAX: with fragments
"""

from typing import List
from .commands import CommandData


class QRFormatter:
    """Base QR formatter"""
    
    def format_command(self, command_data: CommandData) -> str:
        """Format CommandData into QR scannable string"""
        domain = command_data.domain
        
        if domain == 'device':
            return self._format_device_command(command_data)
        elif domain == 'config':
            return self._format_config_command(command_data)
        elif domain == 'full':
            return self._format_full_command(command_data)
        elif domain == 'lua':
            return self._format_lua_command(command_data)
        else:
            raise ValueError(f"Unknown command domain: {domain}")
    
    def _format_device_command(self, cmd: CommandData) -> str:
        """Format device domain command: $CMD:DEV:xxxx$"""
        hex_data = cmd.payload.hex().upper()
        return f"$CMD:DEV:{cmd.command_id:02X}{hex_data}CMD$"
    
    def _format_config_command(self, cmd: CommandData) -> str:
        """Format config domain command: $CMD:KEY:xxxx$"""
        hex_data = cmd.payload.hex().upper()
        return f"$CMD:KEY:{cmd.command_id:02X}{hex_data}CMD$"
    
    def _format_full_command(self, cmd: CommandData) -> str:
        """Format full keyboard config: $FULL:xxxx$"""
        b64_data = cmd.metadata.get('b64_data', '')
        return f"$FULL:{b64_data}$"
    
    def _format_lua_command(self, cmd: CommandData) -> str:
        """Format Lua script fragment: $LUA1:/$LUA2:/$LUAX:"""
        fragment_num = cmd.metadata.get('fragment_number', 1)
        total_fragments = cmd.metadata.get('total_fragments', 1)
        fragment_data = cmd.metadata.get('fragment_data', '')
        
        if total_fragments == 1:
            # Single QR - use execute format
            return f"$LUAX:{fragment_data}$"
        elif fragment_num == total_fragments:
            # Last fragment - use execute format
            return f"$LUAX:{fragment_data}$"
        else:
            # Intermediate fragment
            return f"$LUA{fragment_num}:{fragment_data}$"


class BatchFormatter:
    """Helper for formatting multiple commands"""
    
    def __init__(self):
        self._formatter = QRFormatter()
    
    def format_commands(self, commands: List[CommandData]) -> List[str]:
        """Format list of commands into QR strings"""
        return [self._formatter.format_command(cmd) for cmd in commands]