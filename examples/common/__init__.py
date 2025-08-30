"""
Common utilities for aRdent ScanPad interactive examples

Provides shared functionality for all interactive terminal applications
to avoid code duplication and maintain consistency.
"""

from .ui_helpers import (
    print_header,
    confirm,
    get_int_input,
    get_choice_input,
    get_text_input,
    pause_for_user,
    display_error,
    clear_screen,
    display_menu,
    get_menu_choice
)

from .interactive_base import InteractiveBase
from .json_browser import JSONBrowser
from .keyboard_builder import KeyboardConfigBuilder

__all__ = [
    'print_header',
    'confirm',
    'get_int_input',
    'get_choice_input',
    'get_text_input',
    'pause_for_user',
    'display_error',
    'clear_screen',
    'display_menu',
    'get_menu_choice',
    'InteractiveBase',
    'JSONBrowser',
    'KeyboardConfigBuilder'
]