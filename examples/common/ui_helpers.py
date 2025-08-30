"""
UI Helper Functions for Interactive Examples

Common UI functions used across all interactive terminal applications.
"""

import os
import sys
from typing import Optional, List


def print_header(title: str, subtitle: str = "") -> None:
    """Print a formatted header for the application"""
    print("\n" + "="*70)
    print(title)
    if subtitle:
        print(subtitle)
    print("="*70)


def confirm(message: str) -> bool:
    """Ask for user confirmation"""
    response = input(f"{message} (y/n): ").strip().lower()
    return response in ['y', 'yes']


def get_int_input(prompt: str, min_val: int = None, max_val: int = None) -> Optional[int]:
    """Get integer input with optional validation"""
    try:
        value = int(input(prompt))
        if min_val is not None and value < min_val:
            print(f"❌ Value must be at least {min_val}")
            return None
        if max_val is not None and value > max_val:
            print(f"❌ Value must be at most {max_val}")
            return None
        return value
    except ValueError:
        print("❌ Invalid number")
        return None
    except KeyboardInterrupt:
        return None


def get_choice_input(prompt: str, choices: List[str]) -> Optional[str]:
    """Get user choice from a list of options"""
    for i, choice in enumerate(choices, 1):
        print(f"  {i}. {choice}")
    
    user_input = input(prompt).strip()
    
    # Allow both numeric and string selection
    try:
        idx = int(user_input) - 1
        if 0 <= idx < len(choices):
            return choices[idx]
    except ValueError:
        # Check if input matches a choice directly
        if user_input in choices:
            return user_input
    
    print(f"❌ Invalid choice. Please select 1-{len(choices)}")
    return None


def get_text_input(prompt: str, max_bytes: int = None) -> Optional[str]:
    """Get text input with optional UTF-8 byte limit"""
    try:
        text = input(prompt)
        if max_bytes and len(text.encode('utf-8')) > max_bytes:
            print(f"❌ Text too long (max {max_bytes} UTF-8 bytes)")
            return None
        return text
    except KeyboardInterrupt:
        return None


def pause_for_user() -> None:
    """Pause and wait for user to press Enter"""
    input("\nPress Enter to continue...")


def display_error(error: Exception) -> None:
    """Display an error message in a consistent format"""
    print(f"\n❌ Error: {error}")
    pause_for_user()


def clear_screen() -> None:
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


def display_menu(title: str, items: List[str], include_back: bool = True) -> None:
    """Display a formatted menu"""
    print(f"\n📋 {title}:")
    print("="*50)
    
    for i, item in enumerate(items, 1):
        print(f"  {i}. {item}")
    
    if include_back:
        print(f"  0. ❌ Back")
    
    print("="*50)


def get_menu_choice(max_choice: int, include_zero: bool = True) -> Optional[int]:
    """Get a menu choice from user"""
    min_val = 0 if include_zero else 1
    prompt = f"\nSelect option ({min_val}-{max_choice}): "
    
    try:
        choice = int(input(prompt).strip())
        if min_val <= choice <= max_choice:
            return choice
        print(f"❌ Invalid choice. Please select {min_val}-{max_choice}")
        return None
    except ValueError:
        print("❌ Please enter a number")
        return None
    except KeyboardInterrupt:
        return 0 if include_zero else None