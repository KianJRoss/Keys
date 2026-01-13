"""
Keychron V1 Menu System - State Machine
Based on keychron_commands.ahk AutoHotkey v2 implementation

Architecture:
    - State machine tracks current mode (normal, menu modes)
    - Event processor handles encoder events (CW/CCW/press/release)
    - Command registry for extensible command system
    - Mode handlers for different menu types
"""

import time
import threading
from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional, Callable, List, Dict, Any
from abc import ABC, abstractmethod


# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    """Global configuration constants"""
    DOUBLE_CLICK_MS = 300           # Double-click detection threshold
    MENU_TIMEOUT_MS = 5000          # Auto-exit menu after inactivity
    VOLUME_STEP = 2                 # Volume change percentage
    WINDOW_TITLE_MAX_LEN = 22       # Max chars for window titles
    NOTIFICATION_DURATION = 1500    # Default notification time (ms)
    COMMAND_EXECUTE_DURATION = 2000 # Command execution notification time
    ERROR_DURATION = 3000           # Error notification time


# ============================================================================
# STATE DEFINITIONS
# ============================================================================

class MenuMode(Enum):
    """Available menu modes"""
    NORMAL = auto()                 # Command selection mode

    # Main menus
    VOICEMEETER_MENU = auto()      # Voicemeeter submenu selector
    MEDIA = auto()                 # Media control mode
    VOLUME = auto()                # System volume control
    WINDOW_MENU = auto()           # Window manager submenu selector

    # Theme submenus
    THEME_MENU = auto()            # Theme main menu
    THEME_PRESET = auto()          # Theme presets selector
    THEME_BOX = auto()             # Box color
    THEME_ACCENT = auto()          # Accent color
    THEME_TEXT = auto()            # Text color

    # Voicemeeter submenus
    VM_SYSTEM = auto()             # System volume + mic mute
    VM_MIC = auto()                # Microphone Gain
    VM_MAIN_ROUTING = auto()       # Main audio routing
    VM_MUSIC_GAIN = auto()         # Music gain control
    VM_MUSIC_ROUTING = auto()      # Music routing
    VM_COMM_GAIN = auto()          # Comm gain control
    VM_COMM_ROUTING = auto()       # Comm routing

    # Window submenus
    WINDOW_CYCLE = auto()          # Alt-Tab like window switching
    WINDOW_SNAP = auto()           # Window snapping

    # App launcher menu
    APP_LAUNCHER_MENU = auto()     # App launcher submenu selector

    # Virtual Desktop modes (plugin)
    VIRTUAL_DESKTOP = auto()       # Virtual desktop switcher
    VIRTUAL_DESKTOP_MENU = auto()  # Virtual desktop actions menu

    # Display Control modes (plugin)
    DISPLAY_MENU = auto()          # Display control main menu
    DISPLAY_BRIGHTNESS = auto()    # Brightness adjustment
    DISPLAY_MODE = auto()          # Display mode selector
    DISPLAY_TOGGLE = auto()        # Monitor toggle

    # Context-aware modes (plugin)
    CONTEXT_MENU = auto()          # Context-specific commands


@dataclass
class AppState:
    """Application state container"""
    current_command: int = 0        # Selected command (0-3)
    previous_command: int = 0       # Previous command
    menu_mode: MenuMode = MenuMode.NORMAL
    submenu_index: int = 0          # Current submenu selection
    last_click_time: float = 0      # For double-click detection
    click_count: int = 0            # Click counter
    last_rotation_index: int = 0    # Last command index for direction detection
    routing_selection: int = 0      # For routing modes: 0=A1, 1=A2, 2=A3
    menu_timer: Optional[float] = None  # Timestamp for auto-exit
    window_list: List[Any] = None   # Cached window list

    def __post_init__(self):
        if self.window_list is None:
            self.window_list = []


# ============================================================================
# COMMAND SYSTEM
# ============================================================================

@dataclass
class Command:
    """Command definition"""
    name: str
    description: str
    action: Callable[[], None]


class CommandRegistry:
    """Registry for commands (extensible)"""

    def __init__(self):
        self.commands: List[Command] = []

    def register(self, name: str, description: str, action: Callable[[], None]) -> int:
        """Register a command and return its index"""
        cmd = Command(name=name, description=description, action=action)
        self.commands.append(cmd)
        return len(self.commands) - 1

    def get(self, index: int) -> Optional[Command]:
        """Get command by index"""
        if 0 <= index < len(self.commands):
            return self.commands[index]
        return None

    def count(self) -> int:
        """Get total number of commands"""
        return len(self.commands)


# ============================================================================
# MODE HANDLER BASE CLASS
# ============================================================================

class ModeHandler(ABC):
    """Base class for mode-specific behavior"""

    @abstractmethod
    def on_enter(self, state: AppState) -> None:
        """Called when entering this mode"""
        pass

    @abstractmethod
    def on_exit(self, state: AppState) -> None:
        """Called when exiting this mode"""
        pass

    @abstractmethod
    def on_rotation(self, state: AppState, clockwise: bool) -> None:
        """Handle rotation event"""
        pass

    @abstractmethod
    def on_press(self, state: AppState) -> None:
        """Handle press event"""
        pass

    @abstractmethod
    def get_display_text(self, state: AppState) -> Dict[str, str]:
        """Return display text for menu overlay

        Returns:
            Dict with keys: 'left', 'center', 'right' for wheel layout
        """
        pass


# ============================================================================
# STATE MACHINE
# ============================================================================

class MenuStateMachine:
    """Central state machine for menu system"""

    def __init__(self):
        self.state = AppState()
        self.commands = CommandRegistry()
        self.mode_handlers: Dict[MenuMode, ModeHandler] = {}
        self.ui_callback: Optional[Callable[[Dict[str, str]], None]] = None
        self.notification_callback: Optional[Callable[[str, int], None]] = None
        self.single_click_timer: Optional[threading.Timer] = None

    def register_mode_handler(self, mode: MenuMode, handler: ModeHandler):
        """Register a handler for a specific mode"""
        self.mode_handlers[mode] = handler

    def set_ui_callback(self, callback: Callable[[Dict[str, str]], None]):
        """Set callback for UI updates"""
        self.ui_callback = callback

    def set_notification_callback(self, callback: Callable[[str, int], None]):
        """Set callback for notifications"""
        self.notification_callback = callback

    def show_notification(self, message: str, duration: int = None):
        """Show notification via callback"""
        if self.notification_callback:
            self.notification_callback(message, duration or Config.NOTIFICATION_DURATION)

    def update_display(self):
        """Update UI display based on current state"""
        if self.state.menu_mode == MenuMode.NORMAL:
            # Show current command selection
            cmd = self.commands.get(self.state.current_command)
            if cmd and self.notification_callback:
                self.notification_callback(cmd.name, Config.NOTIFICATION_DURATION)
        else:
            # Show menu overlay
            handler = self.mode_handlers.get(self.state.menu_mode)
            if handler and self.ui_callback:
                display = handler.get_display_text(self.state)
                self.ui_callback(display)

    def reset_menu_timer(self):
        """Reset the auto-exit timer"""
        self.state.menu_timer = time.time()

    def check_menu_timeout(self) -> bool:
        """Check if menu should auto-exit"""
        if self.state.menu_mode == MenuMode.NORMAL:
            return False

        if self.state.menu_timer is None:
            return False

        elapsed = (time.time() - self.state.menu_timer) * 1000
        return elapsed > Config.MENU_TIMEOUT_MS

    def enter_mode(self, mode: MenuMode):
        """Transition to a new mode"""
        # Exit current mode
        old_handler = self.mode_handlers.get(self.state.menu_mode)
        if old_handler:
            old_handler.on_exit(self.state)

        # Update state
        self.state.menu_mode = mode
        self.state.click_count = 0
        self.state.last_rotation_index = 0
        self.reset_menu_timer()

        # Enter new mode
        new_handler = self.mode_handlers.get(mode)
        if new_handler:
            new_handler.on_enter(self.state)

        # Trigger LED update if available
        if hasattr(self, 'led') and self.led:
            self.led.set_mode_color(mode.name)

        self.update_display()

    def exit_menu_mode(self):
        """Exit to normal mode"""
        if self.state.menu_mode != MenuMode.NORMAL:
            self.enter_mode(MenuMode.NORMAL)
            self.show_notification("Returned to Normal Mode", Config.NOTIFICATION_DURATION)
    
    def _execute_single_click(self):
        """Execute single click action after delay"""
        self.state.click_count = 0
        handler = self.mode_handlers.get(self.state.menu_mode)
        if handler:
            handler.on_press(self.state)
            self.update_display()
            self.reset_menu_timer()

    # ========================================================================
    # EVENT HANDLERS
    # ========================================================================

    def handle_rotation(self, command_index: int):
        """Handle rotation event

        Args:
            command_index: The command index (0-3) from firmware
                          Sequence determines direction (0→1→2→3→0 = CW)
        """
        if self.state.menu_mode == MenuMode.NORMAL:
            # Normal mode: Update command selection
            self.state.previous_command = self.state.current_command
            self.state.current_command = command_index
            self.update_display()
        else:
            # Menu mode: Determine rotation direction and delegate to handler
            clockwise = self._is_rotating_clockwise(
                self.state.last_rotation_index,
                command_index
            )
            self.state.last_rotation_index = command_index

            handler = self.mode_handlers.get(self.state.menu_mode)
            if handler:
                handler.on_rotation(self.state, clockwise)
                self.update_display()
                self.reset_menu_timer()

    def handle_press(self):
        """Handle press event"""
        if self.state.menu_mode == MenuMode.NORMAL:
            # Normal mode: Execute current command
            cmd = self.commands.get(self.state.current_command)
            if cmd:
                try:
                    cmd.action()
                    self.show_notification(f"Executed: {cmd.name}", Config.COMMAND_EXECUTE_DURATION)
                except Exception as e:
                    self.show_notification(f"Error: {e}", Config.ERROR_DURATION)
        else:
            # Menu mode: Single click - delegate to handler
            current_time = time.time() * 1000  # Convert to ms
            time_since_last = current_time - self.state.last_click_time
            
            # Cancel pending single click if any
            if self.single_click_timer:
                self.single_click_timer.cancel()
                self.single_click_timer = None

            if time_since_last < Config.DOUBLE_CLICK_MS:
                # Click came within threshold
                self.state.click_count += 1

                if self.state.click_count >= 2:
                    # Double-click: Exit menu mode
                    self.state.click_count = 0
                    self.exit_menu_mode()
                    return
            else:
                # New click sequence
                self.state.click_count = 1

            self.state.last_click_time = current_time

            # Schedule single click execution
            if self.state.click_count == 1:
                self.single_click_timer = threading.Timer(
                    Config.DOUBLE_CLICK_MS / 1000.0, 
                    self._execute_single_click
                )
                self.single_click_timer.start()

    def handle_long_press(self):
        """Handle long press event"""
        # Could be used for alternative actions in the future
        pass

    def handle_double_tap(self):
        """Handle double tap event (from firmware)"""
        if self.state.menu_mode != MenuMode.NORMAL:
            self.exit_menu_mode()

    @staticmethod
    def _is_rotating_clockwise(prev_index: int, curr_index: int) -> bool:
        """Determine rotation direction from command sequence

        Normal increment: 0->1, 1->2, 2->3
        Wrap around: 3->0
        """
        if curr_index == prev_index + 1:
            return True
        if prev_index == 3 and curr_index == 0:
            return True
        return False
