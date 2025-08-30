"""
Base Class for Interactive Terminal Applications

Provides common functionality for all interactive examples.
"""

from typing import Dict, List, Callable, Optional, Any
from .ui_helpers import print_header, display_menu, get_menu_choice, display_error, pause_for_user


class InteractiveBase:
    """Base class for interactive terminal applications"""
    
    def __init__(self, app_name: str, description: str):
        """
        Initialize interactive application
        
        Args:
            app_name: Application name displayed in header
            description: Application description
        """
        self.app_name = app_name
        self.description = description
        self.running = False
    
    def print_header(self) -> None:
        """Print application header"""
        print_header(self.app_name, self.description)
    
    def run_menu_loop(self, menu_title: str, menu_items: List[str], 
                     handler_map: Dict[int, Callable], include_back: bool = True) -> None:
        """
        Run a menu loop with automatic handling
        
        Args:
            menu_title: Title for the menu
            menu_items: List of menu item descriptions
            handler_map: Dict mapping choice numbers to handler functions
            include_back: Whether to include a "Back" option (0)
        """
        while True:
            display_menu(menu_title, menu_items, include_back)
            
            max_choice = len(menu_items)
            choice = get_menu_choice(max_choice, include_back)
            
            if choice is None:
                continue
            
            if choice == 0 and include_back:
                break
            
            if choice in handler_map:
                result = self.safe_execute(handler_map[choice])
                if result == 'exit':
                    break
            else:
                print(f"❌ Option {choice} not implemented yet")
                pause_for_user()
    
    def safe_execute(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute a function with error handling
        
        Args:
            func: Function to execute
            *args, **kwargs: Arguments to pass to function
            
        Returns:
            Function result or None if error
        """
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            print("\n\n⚠️  Operation cancelled")
            pause_for_user()
            return None
        except Exception as e:
            display_error(e)
            return None
    
    async def async_safe_execute(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute an async function with error handling
        
        Args:
            func: Async function to execute
            *args, **kwargs: Arguments to pass to function
            
        Returns:
            Function result or None if error
        """
        try:
            return await func(*args, **kwargs)
        except KeyboardInterrupt:
            print("\n\n⚠️  Operation cancelled")
            pause_for_user()
            return None
        except Exception as e:
            display_error(e)
            return None
    
    async def async_run_menu_loop(self, menu_title: str, menu_items: List[str],
                                  handler_map: Dict[int, Callable], include_back: bool = True) -> None:
        """
        Run an async menu loop with automatic handling
        
        Args:
            menu_title: Title for the menu
            menu_items: List of menu item descriptions
            handler_map: Dict mapping choice numbers to async handler functions
            include_back: Whether to include a "Back" option (0)
        """
        while True:
            display_menu(menu_title, menu_items, include_back)
            
            max_choice = len(menu_items)
            choice = get_menu_choice(max_choice, include_back)
            
            if choice is None:
                continue
            
            if choice == 0 and include_back:
                break
            
            if choice in handler_map:
                result = await self.async_safe_execute(handler_map[choice])
                if result == 'exit':
                    break
            else:
                print(f"❌ Option {choice} not implemented yet")
                pause_for_user()
    
    def display_success(self, message: str) -> None:
        """Display a success message"""
        print(f"\n✅ {message}")
    
    def display_warning(self, message: str) -> None:
        """Display a warning message"""
        print(f"\n⚠️  {message}")
    
    def display_info(self, message: str) -> None:
        """Display an info message"""
        print(f"\nℹ️  {message}")