"""
Overlay UI - On-screen menu display

Creates a transparent overlay window showing menu options
in a "wheel" layout around the cursor (like AHK implementation)
"""

import tkinter as tk
from typing import Dict, Optional, Callable
import threading


class OverlayUI:
    """Transparent overlay showing menu options"""

    def __init__(self):
        self.root: Optional[tk.Tk] = None
        self.widgets = {
            'left': None,
            'center': None,
            'right': None,
            'hint': None
        }
        self.notification_widget: Optional[tk.Toplevel] = None
        self.visible = False
        self.notification_timer = None

        # Styling
        self.bg_color = "#1E1E1E"
        self.text_color = "gray"
        self.active_color = "yellow"
        self.hint_color = "#808080"
        self.font = ("Segoe UI", 10)
        self.font_bold = ("Segoe UI", 10, "bold")

    def init_ui(self):
        """Initialize UI (must be called from main thread)"""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide main window

    def show_menu(self, display: Dict[str, str], mouse_x: int = None, mouse_y: int = None):
        """Show menu overlay with wheel layout

        Args:
            display: Dict with keys 'left', 'center', 'right'
            mouse_x, mouse_y: Position (if None, uses current mouse position)
        """
        if not self.root:
            return

        # Get mouse position if not provided
        if mouse_x is None or mouse_y is None:
            mouse_x = self.root.winfo_pointerx()
            mouse_y = self.root.winfo_pointery()

        # Destroy existing widgets
        self._destroy_menu()

        # Create LEFT widget (to the left of cursor)
        if display.get('left'):
            self._create_widget('left', display['left'],
                              mouse_x - 180, mouse_y,
                              self.text_color, self.font)

        # Create CENTER widget (above cursor, bold/active)
        if display.get('center'):
            self._create_widget('center', display['center'],
                              mouse_x - 60, mouse_y - 60,
                              self.active_color, self.font_bold)

        # Create RIGHT widget (to the right of cursor)
        if display.get('right'):
            self._create_widget('right', display['right'],
                              mouse_x + 60, mouse_y,
                              self.text_color, self.font)

        # Create HINT widget (below cursor)
        self._create_widget('hint', "Double-tap: Exit",
                          mouse_x - 40, mouse_y + 40,
                          self.hint_color, self.font)

        self.visible = True

    def hide_menu(self):
        """Hide menu overlay"""
        self._destroy_menu()
        self.visible = False

    def show_notification(self, message: str, duration_ms: int = 1500):
        """Show a notification near the cursor

        Args:
            message: Notification text
            duration_ms: How long to display (milliseconds)
        """
        if not self.root:
            return

        # Cancel existing notification timer
        if self.notification_timer:
            self.root.after_cancel(self.notification_timer)

        # Destroy existing notification
        if self.notification_widget:
            try:
                self.notification_widget.destroy()
            except:
                pass

        # Get mouse position
        mouse_x = self.root.winfo_pointerx()
        mouse_y = self.root.winfo_pointery()

        # Create notification window
        notif = tk.Toplevel(self.root)
        notif.overrideredirect(True)  # No window decorations
        notif.attributes('-topmost', True)
        notif.attributes('-alpha', 0.9)
        notif.configure(bg=self.bg_color)

        # Add text
        label = tk.Label(notif, text=message,
                        bg=self.bg_color, fg=self.active_color,
                        font=self.font, padx=10, pady=8)
        label.pack()

        # Position near cursor
        notif.update_idletasks()
        notif.geometry(f"+{mouse_x + 20}+{mouse_y + 20}")

        self.notification_widget = notif

        # Auto-hide after duration
        self.notification_timer = self.root.after(duration_ms, self._hide_notification)

    def _create_widget(self, key: str, text: str, x: int, y: int, color: str, font: tuple):
        """Create a single overlay widget"""
        widget = tk.Toplevel(self.root)
        widget.overrideredirect(True)  # No window decorations
        widget.attributes('-topmost', True)
        widget.attributes('-alpha', 0.9)
        widget.configure(bg=self.bg_color)

        label = tk.Label(widget, text=text,
                        bg=self.bg_color, fg=color,
                        font=font, padx=5, pady=5)
        label.pack()

        # Position widget
        widget.update_idletasks()
        widget.geometry(f"+{x}+{y}")

        self.widgets[key] = widget

    def _destroy_menu(self):
        """Destroy all menu widgets"""
        for key in ['left', 'center', 'right', 'hint']:
            if self.widgets[key]:
                try:
                    self.widgets[key].destroy()
                except:
                    pass
                self.widgets[key] = None

    def _hide_notification(self):
        """Hide notification widget"""
        if self.notification_widget:
            try:
                self.notification_widget.destroy()
            except:
                pass
            self.notification_widget = None

    def run_mainloop(self):
        """Start tkinter event loop (blocks)"""
        if self.root:
            self.root.mainloop()

    def quit(self):
        """Quit UI"""
        if self.root:
            self.root.quit()


# ============================================================================
# UI MANAGER (thread-safe wrapper)
# ============================================================================

class UIManager:
    """Thread-safe UI manager for use with HID event loop"""

    def __init__(self):
        self.ui = OverlayUI()
        self.ui_thread: Optional[threading.Thread] = None

    def start(self):
        """Start UI in separate thread"""
        def ui_thread_func():
            self.ui.init_ui()
            self.ui.run_mainloop()

        self.ui_thread = threading.Thread(target=ui_thread_func, daemon=True)
        self.ui_thread.start()

        # Wait for UI to initialize
        import time
        time.sleep(0.5)

    def show_menu(self, display: Dict[str, str]):
        """Show menu (thread-safe)"""
        if self.ui.root:
            self.ui.root.after(0, lambda: self.ui.show_menu(display))

    def hide_menu(self):
        """Hide menu (thread-safe)"""
        if self.ui.root:
            self.ui.root.after(0, self.ui.hide_menu)

    def show_notification(self, message: str, duration_ms: int = 1500):
        """Show notification (thread-safe)"""
        if self.ui.root:
            self.ui.root.after(0, lambda: self.ui.show_notification(message, duration_ms))

    def quit(self):
        """Quit UI"""
        if self.ui.root:
            self.ui.root.after(0, self.ui.quit)


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    import time

    ui = UIManager()
    ui.start()

    print("Showing notification...")
    ui.show_notification("Test Notification", 2000)
    time.sleep(2.5)

    print("Showing menu...")
    ui.show_menu({
        'left': 'Option A',
        'center': '▶ Option B (Active)',
        'right': 'Option C'
    })
    time.sleep(3)

    print("Hiding menu...")
    ui.hide_menu()
    time.sleep(1)

    print("Done!")
    ui.quit()
