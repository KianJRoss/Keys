"""
System Tray Icon for Keychron Menu System
"""

import sys
import logging
import threading
from pathlib import Path

try:
    from PIL import Image, ImageDraw
    import pystray
    PYSTRAY_AVAILABLE = True
except ImportError:
    PYSTRAY_AVAILABLE = False
    logging.warning("pystray or PIL not installed. Tray icon will not be available.")
    logging.warning("Install with: pip install pystray Pillow")

logger = logging.getLogger("KeychronApp.TrayIcon")


class TrayIcon:
    """System tray icon manager"""

    def __init__(self, app_instance):
        self.app = app_instance
        self.icon = None
        self.running = False

        if not PYSTRAY_AVAILABLE:
            logger.warning("Tray icon unavailable - missing dependencies")
            return

    def create_icon_image(self):
        """Create a simple icon image that's visible on Windows"""
        # Create a 64x64 icon - use bright colors so it's clearly visible
        width = 64
        height = 64

        # Use a bright blue background so it stands out
        image = Image.new('RGB', (width, height), color='#0078D4')
        draw = ImageDraw.Draw(image)

        # Draw a large white "K" for Keychron
        draw.text((16, 12), "K", fill='white', font=None)

        # Draw a simple keyboard shape (rectangle with keys)
        # Outer border - white so it's visible
        draw.rectangle([12, 24, 52, 52], outline='white', fill='#333333', width=2)

        # Draw key dots in white
        for row in range(2):
            for col in range(3):
                x = 18 + col * 10
                y = 30 + row * 10
                draw.ellipse([x, y, x+4, y+4], fill='white')

        return image

    def on_quit(self, icon, item):
        """Handle quit action"""
        logger.info("Quit requested from tray icon")
        self.running = False
        
        # Explicitly hide icon to prevent ghosting
        icon.visible = False
        icon.stop()
        
        # Small sleep to allow Windows to process the icon removal
        import time
        time.sleep(0.2)

        # Stop the application
        if hasattr(self.app, 'quit'):
            self.app.quit()
        elif hasattr(self.app, 'stop'):
            self.app.stop()

        # Force exit if needed - this should ideally not be necessary if app.quit() works
        # sys.exit(0) # Removed to allow graceful shutdown
    def on_show_status(self, icon, item):
        """Show current status"""
        logger.info("Status requested from tray icon")

        # Get status info
        mode = "Idle"
        if hasattr(self.app, 'state_machine'):
            current_mode = getattr(self.app.state_machine, 'current_mode', None)
            if current_mode:
                mode = str(current_mode).split('.')[-1]

        vm_status = "Not connected"
        if hasattr(self.app, 'vm') and self.app.vm.is_available():
            vm_status = "Connected"

        logger.info(f"Status - Mode: {mode}, Voicemeeter: {vm_status}")

    def on_toggle_led(self, icon, item):
        """Toggle LED feedback on/off"""
        if hasattr(self.app, 'led') and self.app.led:
            # Simple toggle - in a real implementation you'd want to track state
            logger.info("LED toggle requested (not yet fully implemented)")
        else:
            logger.info("LED feedback not available")

    def create_menu(self):
        """Create the tray icon menu"""
        return pystray.Menu(
            pystray.MenuItem("Keychron V1 Menu System", lambda: None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Show Status", self.on_show_status),
            pystray.MenuItem("Toggle LED Feedback", self.on_toggle_led),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", self.on_quit)
        )

    def setup(self, icon):
        """Setup callback - makes icon visible"""
        icon.visible = True
        logger.info("Tray icon is now visible")

    def run(self):
        """Run the tray icon (blocking)"""
        if not PYSTRAY_AVAILABLE:
            logger.warning("Cannot start tray icon - dependencies not available")
            return

        try:
            self.running = True

            # Create icon image
            image = self.create_icon_image()

            # Create icon with setup callback
            self.icon = pystray.Icon(
                "keychron_menu",
                image,
                "Keychron V1 Menu",
                menu=self.create_menu()
            )

            logger.info("Starting tray icon with setup callback...")

            # Run with setup callback - this is REQUIRED on Windows
            self.icon.run(setup=self.setup)
            logger.info("Tray icon stopped")
        except Exception as e:
            logger.error(f"Failed to start tray icon: {e}")
            import traceback
            logger.error(traceback.format_exc())

    def start(self):
        """Start the tray icon in a background thread"""
        if not PYSTRAY_AVAILABLE:
            logger.warning("Tray icon not available")
            return

        # Use a non-daemon thread so it stays alive
        thread = threading.Thread(target=self.run, daemon=False)
        thread.start()
        logger.info("Tray icon thread started")

    def stop(self):
        """Stop the tray icon"""
        if self.icon:
            self.icon.visible = False
            self.icon.stop()
            self.running = False
            logger.info("Tray icon stopped")
