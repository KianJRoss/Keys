"""
Keychron V1 Menu System - Qt Main Application

Properly restructured with Qt on main thread and HID in worker thread.
"""

import sys
import logging
import json
import os
import importlib
import pkgutil
from typing import Optional, List
from pathlib import Path
import subprocess

from PyQt6.QtCore import QObject, pyqtSlot, QTimer
from PyQt6.QtWidgets import QApplication

# Import our modules
from menu_system import MenuStateMachine, MenuMode
from mode_handlers import create_handlers
from windows_api import SystemAPI
from voicemeeter_api import VoicemeeterController
from tray_icon import TrayIcon
from hid_reader_thread import HIDReaderThread
from overlay_qt import EnhancedUIManager

# ============================================================================
# LOGGING SETUP
# ============================================================================

log_handlers = []

# Always log to file
log_dir = Path(__file__).parent / 'logs'
log_dir.mkdir(exist_ok=True)
log_file = log_dir / 'keychron_app.log'

file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
log_handlers.append(file_handler)

# Also log to console if running with python.exe
if sys.executable.endswith('python.exe'):
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    log_handlers.append(console_handler)

logging.basicConfig(
    level=logging.INFO,
    handlers=log_handlers
)

logger = logging.getLogger(__name__)

# ============================================================================
# PLUGIN MANAGER
# ============================================================================

class PluginManager:
    """Discovers and loads plugins from plugins/ directory"""

    def __init__(self):
        self.plugins = []
        self.plugin_handlers = {}

    def load_plugins(self, state_machine):
        """Load all plugins from plugins directory"""
        plugin_dir = Path(__file__).parent / 'plugins'
        if not plugin_dir.exists():
            return

        sys.path.insert(0, str(plugin_dir))

        for finder, name, ispkg in pkgutil.iter_modules([str(plugin_dir)]):
            try:
                logger.info(f"Loading plugin: {name}")
                module = importlib.import_module(name)

                if hasattr(module, 'get_commands'):
                    commands = module.get_commands()
                    for cmd in commands:
                        state_machine.commands.register(
                            cmd['name'],
                            cmd['description'],
                            cmd['callback']
                        )
                        logger.info(f"  + Registered command: {cmd['name']}")

                if hasattr(module, 'get_mode_handlers'):
                    handlers = module.get_mode_handlers(state_machine)
                    self.plugin_handlers.update(handlers)
                    for mode_name in handlers.keys():
                        logger.info(f"  + Registered plugin mode handler: {mode_name}")

                self.plugins.append(module)
            except Exception as e:
                logger.error(f"Failed to load plugin {name}: {e}")


# ============================================================================
# KEYCHRON APPLICATION (QObject for signals/slots)
# ============================================================================

class KeychronApp(QObject):
    """Main application - integrates HID, state machine, and UI using Qt"""

    def __init__(self, config, app: QApplication):
        super().__init__()

        self.config = config
        self.app = app

        # Components
        self.api = SystemAPI()
        self.vm = VoicemeeterController()
        self.state_machine = MenuStateMachine()
        self.plugin_manager = PluginManager()

        # UI - Qt overlay
        self.ui = EnhancedUIManager(theme=config['ui_theme'])

        # HID Reader Thread
        self.hid_reader: Optional[HIDReaderThread] = None

        # Tray icon
        self.tray_icon = TrayIcon(self)

        # State tracking
        self.is_pressed = False
        self.was_rotated_while_pressed = False
        self.ignore_next_release = False
        self.last_command_index = 0
        self.timeout_timer = None # Added for timeout check

    def setup(self) -> bool:
        """Initialize all components"""
        logger.info("Initializing Keychron V1 Menu System (Qt)...")

        # Check API status
        status = self.api.get_status()
        for name, available in status.items():
            level = logging.INFO if available else logging.WARNING
            logger.log(level, f"API {name}: {'Available' if available else 'Unavailable'}")

        if not self.api.is_available():
            logger.error("No Windows APIs available! Install requirements.")
            return False

        # Try to connect to Voicemeeter
        logger.info("Connecting to Voicemeeter...")
        if self.vm.connect():
            logger.info("Voicemeeter Potato connected")
        else:
            logger.warning("Voicemeeter not available - audio routing disabled")

        # Register commands
        self._register_commands()

        # Load Plugins
        self.plugin_manager.load_plugins(self.state_machine)

        # Register mode handlers (built-in)
        handlers = create_handlers(self.api, self.state_machine, self.vm)
        for mode, handler in handlers.items():
            self.state_machine.register_mode_handler(mode, handler)

        # Register plugin mode handlers
        for mode, handler in self.plugin_manager.plugin_handlers.items():
            self.state_machine.register_mode_handler(mode, handler)

        # Link state machine to components
        self.state_machine.api = self.api
        self.state_machine.vm = self.vm
        self.state_machine.set_ui_callback(self._ui_callback)
        self.state_machine.set_notification_callback(lambda msg, duration: self.ui.show_notification(msg, duration))

        # Start UI
        logger.info("Starting UI...")
        self.ui.start()

        # Start tray icon
        self.tray_icon.start()

        # Connect to HID device
        result = self._connect_hid()
        
        # Start timeout timer (1Hz)
        self.timeout_timer = QTimer(self)
        self.timeout_timer.timeout.connect(self._check_timeout)
        self.timeout_timer.start(1000)
        
        return result

    def _check_timeout(self):
        """Check for menu timeout"""
        if self.state_machine.check_menu_timeout():
            if self.state_machine.state.menu_mode == MenuMode.NORMAL:
                self.ui.hide_menu()
            else:
                self.state_machine.exit_menu_mode()

    def _connect_hid(self) -> bool:
        """Connect to HID device"""
        logger.info("Connecting to HID device...")

        config = self.config
        self.hid_reader = HIDReaderThread(
            vendor_id=config['hid']['vendor_id'],
            product_id=config['hid']['product_id'],
            usage_page=config['hid']['usage_page'],
            usage=config['hid']['usage']
        )

        # Connect signals
        self.hid_reader.event_received.connect(self._on_hid_event)
        self.hid_reader.connection_established.connect(self._on_hid_connected)
        self.hid_reader.connection_lost.connect(self._on_hid_disconnected)

        # Start reader thread
        self.hid_reader.start()

        logger.info("HID reader thread started")
        return True

    @pyqtSlot(int, int, int)
    def _on_hid_event(self, event_type: int, encoder_id: int, value: int):
        """Handle HID event (called on main thread via signal)"""
        if event_type == HIDReaderThread.EVENT_CW:
            self._handle_rotation(True)
        elif event_type == HIDReaderThread.EVENT_CCW:
            self._handle_rotation(False)
        elif event_type == HIDReaderThread.EVENT_PRESS:
            self._handle_press()
        elif event_type == HIDReaderThread.EVENT_RELEASE:
            self._handle_release()
        elif event_type == HIDReaderThread.EVENT_DOUBLE_CLICK:
            self._handle_double_tap()

    @pyqtSlot()
    def _on_hid_connected(self):
        """HID device connected"""
        logger.info("HID device connected")
        self.ui.show_notification("Keyboard Connected", 1500)

    @pyqtSlot()
    def _on_hid_disconnected(self):
        """HID device disconnected"""
        logger.warning("HID device disconnected - attempting reconnect")
        self.ui.show_notification("Keyboard Disconnected", 2000)

    def _handle_rotation(self, clockwise: bool):
        """Handle encoder rotation"""
        if self.is_pressed:
            self.was_rotated_while_pressed = True

        # Calculate new simulated index
        # We need to simulate an absolute 0-3 rotation for the state machine
        # which expects absolute values to detect direction or set command
        count = self.state_machine.commands.count()
        if count == 0: count = 4
        
        direction = 1 if clockwise else -1
        new_index = (self.last_command_index + direction) % count
        
        self.state_machine.handle_rotation(new_index)
        
        # Update our local tracking
        self.last_command_index = new_index

    def _handle_press(self):
        """Handle encoder press"""
        self.is_pressed = True
        self.was_rotated_while_pressed = False

    def _handle_release(self):
        """Handle encoder release"""
        if self.ignore_next_release:
            self.ignore_next_release = False
            self.is_pressed = False
            return

        if not self.was_rotated_while_pressed:
            self.state_machine.handle_press()

        self.is_pressed = False
        self.was_rotated_while_pressed = False

    def _handle_double_tap(self):
        """Handle encoder double-tap"""
        self.ignore_next_release = True
        self.state_machine.exit_menu_mode()

    def _register_commands(self):
        """Register main commands"""
        from functools import partial

        commands = [
            ("Media Controls", "Play/Pause, Next/Prev", partial(self.state_machine.enter_mode, MenuMode.MEDIA)),
            ("Volume", "System volume control", partial(self.state_machine.enter_mode, MenuMode.VOLUME)),
            ("Window Management", "Cycle, Snap, Desktop", partial(self.state_machine.enter_mode, MenuMode.WINDOW_MENU)),
            ("Theme Settings", "UI customization", partial(self.state_machine.enter_mode, MenuMode.THEME_MENU)),
        ]

        # Add Voicemeeter if available
        if self.vm.is_available():
            commands.append(("Voicemeeter", "Audio routing", partial(self.state_machine.enter_mode, MenuMode.VOICEMEETER_MENU)))

        for name, desc, callback in commands:
            self.state_machine.commands.register(name, desc, callback)

        logger.info(f"Registered {len(commands)} main commands")

    def _ui_callback(self, data: dict):
        """Handle UI callback from state machine"""
        if 'set_theme' in data:
            theme_name = data['set_theme']
            self.ui.set_theme(theme_name)
            self.config['ui_theme'] = theme_name
            self._save_config()
        elif 'preview_theme' in data:
            self.ui.set_theme(data['preview_theme'])
        elif 'set_theme_color' in data:
            self.ui.update_theme_color(data['set_theme_color'])
        elif 'save_theme' in data:
            self.ui.save_theme(data['save_theme'])
        else:
            # Standard menu display update
            self.ui.show_menu(data)

    def _save_config(self):
        """Save configuration to file"""
        config_file = Path(__file__).parent / 'config.json'
        try:
            with open(config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save config: {e}")

    def quit(self):
        """Cleanup and exit"""
        logger.info("Shutting down...")

        if self.hid_reader:
            self.hid_reader.stop()
            self.hid_reader.wait()

        if self.vm:
            self.vm.disconnect()

        self.ui.quit()
        self.app.quit()


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def load_config():
    """Load configuration from config.json"""
    config_file = Path(__file__).parent / 'config.json'

    default_config = {
        'hid': {
            'vendor_id': 0x3434,
            'product_id': 0x0311,
            'usage_page': 0xFF60,
            'usage': 0x61
        },
        'ui_theme': 'DARK',
        'use_enhanced_ui': True,
        'led_feedback': False,
    }

    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                # Merge with defaults
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
        except Exception as e:
            logger.error(f"Error loading config: {e}")

    return default_config


def main():
    """Main entry point"""
    import argparse

    # Load config
    config = load_config()

    # Parse arguments
    parser = argparse.ArgumentParser(description='Keychron V1 Menu System (Qt)')

    # Load available themes
    available_themes = ['DARK', 'LIGHT', 'CYBER']
    themes_path = Path(__file__).parent / 'themes.json'
    if themes_path.exists():
        try:
            with open(themes_path, 'r') as f:
                available_themes = list(json.load(f).keys())
        except:
            pass

    parser.add_argument('--theme', choices=available_themes, default=None,
                       help=f'UI theme. Available: {", ".join(available_themes)}')

    args = parser.parse_args()

    # Override config with args
    if args.theme is not None:
        config['ui_theme'] = args.theme
    if config.get('ui_theme') not in available_themes:
        config['ui_theme'] = 'DARK'

    # Create Qt application (MUST be on main thread)
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Keep running with tray icon

    # Create and setup our app
    keychron_app = KeychronApp(config, app)

    if not keychron_app.setup():
        logger.error("Failed to initialize application")
        return 1

    logger.info("Application started. Running Qt event loop...")

    # Run Qt event loop (blocking)
    return app.exec()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        sys.exit(1)