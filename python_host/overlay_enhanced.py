"""
Enhanced Overlay UI - Modern Radial Menu Design

Creates a beautiful circular/radial menu with:
- Smooth animations
- Modern styling
- Icons and progress bars
- Theme support
- Transparency effects
"""

import tkinter as tk
from tkinter import font as tkfont
import math
import json
import os
from typing import Dict, Optional, List, Tuple
import threading


class Theme:
    """Visual theme configuration"""

    # Default themes (fallback)
    DARK = {
        'bg': '#1a1a1a',
        'bg_alpha': 0.92,
        'segment_inactive': '#2d2d2d',
        'segment_active': '#3d8aff',
        'segment_hover': '#505050',
        'text_inactive': '#888888',
        'text_active': '#ffffff',
        'accent': '#3d8aff',
        'accent_glow': '#5ba3ff',
        'border': '#404040',
        'progress_bg': '#2d2d2d',
        'progress_fill': '#3d8aff',
        'shadow': '#000000',
    }
    
    # ... other defaults are kept but can be overwritten by file ...

def load_themes():
    """Load themes from themes.json"""
    theme_file = os.path.join(os.path.dirname(__file__), 'themes.json')
    if os.path.exists(theme_file):
        try:
            with open(theme_file, 'r') as f:
                themes = json.load(f)
                for name, data in themes.items():
                    setattr(Theme, name, data)
        except Exception as e:
            print(f"Error loading themes: {e}")

class RadialMenu:
    """Modern circular menu overlay"""

    def __init__(self, theme_name='DARK'):
        self.root: Optional[tk.Tk] = None
        self.canvas: Optional[tk.Canvas] = None
        self.visible = False

        # Load custom themes
        load_themes()

        # Theme
        self.theme = getattr(Theme, theme_name, Theme.DARK)
        if isinstance(self.theme, dict) is False: # Handle if getattr returns something odd or default
             self.theme = Theme.DARK

        # Menu state
        self.options: List[str] = []
        self.active_index = 1  # Center item
        self.title = ""
        self.subtitle = ""
        self.progress_value: Optional[float] = None  # 0.0 to 1.0
        self.icons: Dict[str, str] = {}  # emoji icons for options

        # Dimensions
        self.screen_x = 0
        self.screen_y = 0
        self.center_x = 300
        self.center_y = 300
        self.radius = 60
        self.segment_width = 140
        self.center_radius = 10

        # Animation
        self.animation_progress = 0.0
        self.target_progress = 1.0
        self.animation_speed = 0.08
        self.animation_timer = None
        
        # Blinking state
        self.blink_counter = 0.0
        self.pulsing = False

        # Fonts
        self.font_title = None
        self.font_option = None
        self.font_icon = None

    def set_theme(self, theme_name):
        """Change theme at runtime"""
        new_theme = getattr(Theme, theme_name, None)
        if isinstance(new_theme, dict):
            self.theme = new_theme
            # If visible, force redraw to apply new colors
            if self.visible and self.canvas:
                self.canvas.window.attributes('-alpha', self.theme['bg_alpha'])
                self._draw_menu()

    def update_theme_color(self, settings: Dict[str, str]):
        """Update specific theme colors at runtime"""
        for key, value in settings.items():
            if key in self.theme:
                self.theme[key] = value
        
        if self.visible and self.canvas:
            self._draw_menu()

    def save_current_theme(self, theme_name):
        """Save current theme colors back to themes.json"""
        theme_file = os.path.join(os.path.dirname(__file__), 'themes.json')
        themes = {}
        if os.path.exists(theme_file):
            try:
                with open(theme_file, 'r') as f:
                    themes = json.load(f)
            except:
                pass
        
        themes[theme_name] = self.theme
        
        try:
            with open(theme_file, 'w') as f:
                json.dump(themes, f, indent=4)
        except Exception as e:
            print(f"Error saving theme: {e}")

    def init_ui(self):
        """Initialize UI (must be called from main thread)"""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide main window

        # Setup fonts
        self.font_title = tkfont.Font(family="Segoe UI", size=14, weight="bold")
        self.font_option = tkfont.Font(family="Segoe UI", size=10)
        self.font_icon = tkfont.Font(family="Segoe UI", size=18)

    def cancel_animation(self):
        """Cancel any pending animation"""
        if self.animation_timer:
            try:
                self.root.after_cancel(self.animation_timer)
            except:
                pass
            self.animation_timer = None

    def show_menu(self, display: Dict[str, str], mouse_x: int = None, mouse_y: int = None,
                  progress: float = None, icons: Dict[str, str] = None):
        """Show radial menu"""
        if not self.root:
            return

        # Get mouse position
        if mouse_x is None or mouse_y is None:
            mouse_x = self.root.winfo_pointerx()
            mouse_y = self.root.winfo_pointery()

        self.screen_x = mouse_x
        self.screen_y = mouse_y

        # Update menu data
        self.options = [
            display.get('left', ''),
            display.get('center', ''),
            display.get('right', '')
        ]
        self.title = display.get('title', '')
        self.subtitle = display.get('subtitle', 'Double-tap to exit')
        self.progress_value = progress
        self.icons = icons or {}
        
        # Set active index (default to center/1 if not provided)
        self.active_index = display.get('active_index', 1)
        self.pulsing = display.get('pulsing', False)

        # Create/update canvas
        if not self.canvas or not self.canvas.winfo_exists():
            self._create_canvas()

        # Position window
        self._position_window()

        # Start animation
        self.cancel_animation()
        
        # Only restart animation if not already visible
        if not self.visible:
            self.animation_progress = 0.0
        
        self.target_progress = 1.0
        self._animate()

        self.visible = True

    def hide_menu(self):
        """Hide menu with fade out"""
        if not self.visible:
            return

        self.target_progress = 0.0
        self.cancel_animation()
        self._animate(on_complete=self._destroy_canvas)

    def _create_canvas(self):
        """Create the canvas window"""
        # Create transparent window
        window = tk.Toplevel(self.root)
        window.overrideredirect(True)
        window.attributes('-topmost', True)
        window.attributes('-alpha', self.theme['bg_alpha'])

        # Make window transparent (Windows specific)
        transparent_color = '#000001'
        try:
            window.wm_attributes('-transparentcolor', transparent_color)
        except:
            pass

        # Create canvas
        # Increase canvas size to accommodate dynamic widths
        size = 600
        self.center_x = size // 2
        self.center_y = size // 2
        
        # Use transparent color for background so the box is invisible
        self.canvas = tk.Canvas(window, width=size, height=size,
                               bg=transparent_color, highlightthickness=0)
        self.canvas.pack()

        # Store window reference
        self.canvas.window = window

    def _position_window(self):
        """Position window centered on cursor"""
        if not self.canvas:
            return

        # Fixed large size for canvas to allow dynamic placement
        size = 600
        x = self.screen_x - size // 2
        y = self.screen_y - size // 2

        self.canvas.window.geometry(f"{size}x{size}+{x}+{y}")

    def _animate(self, on_complete=None):
        """Smooth animation loop"""
        if not self.canvas or not self.canvas.winfo_exists():
            return
            
        # Update cursor position (FOLLOW MOUSE)
        self.screen_x = self.root.winfo_pointerx()
        self.screen_y = self.root.winfo_pointery()
        self._position_window()
            
        # Update blink counter (always run this)
        self.blink_counter += 0.5

        # Update progress
        diff = self.target_progress - self.animation_progress
        
        # Use faster speed and larger snap threshold when closing (target_progress is 0)
        current_speed = self.animation_speed
        finish_threshold = 0.001
        if self.target_progress < 0.1:
            current_speed *= 2.0
            finish_threshold = 0.1 # Snap closed earlier to avoid lingering
            
        if abs(diff) > finish_threshold:
            self.animation_progress += diff * current_speed

            # Redraw
            self._draw_menu()

            # Continue animation
            self.animation_timer = self.root.after(16, lambda: self._animate(on_complete))  # ~60 FPS
        else:
            self.animation_progress = self.target_progress
            self._draw_menu()

            # For blinking, we need to keep animating if there is an active selection
            # Only if we are not hiding (target_progress > 0.5)
            if self.target_progress > 0.5 and self.active_index != -1 and self.visible:
                 self.animation_timer = self.root.after(16, lambda: self._animate(on_complete))
            elif on_complete:
                on_complete()

    def _draw_menu(self):
        """Draw the radial menu"""
        if not self.canvas:
            return

        self.canvas.delete('all')

        # Apply animation scale
        scale = self._ease_out_back(self.animation_progress)

        # Draw segments
        self._draw_segments(scale)

        # Draw center circle
        self._draw_center(scale)

        # Draw progress bar if present
        if self.progress_value is not None:
            self._draw_progress_bar(scale)

        # Draw hint text
        if self.subtitle:
            self._draw_hint(scale)

    def _draw_segments(self, scale: float):
        """Draw option segments in a wheel layout"""
        positions = [
            (-self.radius, 0),      # Left
            (0, -self.radius),      # Top (center)
            (self.radius, 0)        # Right
        ]
        
        gap_from_center = 20  # Fixed gap from center dot to inner edge of box

        for i, (dx, dy) in enumerate(positions):
            if i >= len(self.options) or not self.options[i]:
                continue

            # Determine colors
            is_active = (i == self.active_index)
            
            # Blink logic for active item
            if is_active and self.pulsing:
                # Blink between Active color and Accent Glow
                is_bright = math.sin(self.blink_counter) > 0
                bg_color = self.theme['accent_glow'] if is_bright else self.theme['segment_active']
                text_color = self.theme['text_active']
                active_font = self.font_title
            elif is_active:
                bg_color = self.theme['segment_active']
                text_color = self.theme['text_active']
                active_font = self.font_title
            else:
                bg_color = self.theme['segment_inactive']
                text_color = self.theme['text_inactive']
                active_font = self.font_option

            # Measure content dimensions
            padding = 15
            text_width = active_font.measure(self.options[i]) + padding * 2
            text_height = 40 if is_active else 30

            # Add icon if present
            icon = self.icons.get(['left', 'center', 'right'][i], '')
            icon_width = 0
            if icon:
                icon_width = self.font_icon.measure(icon)
                text_width += icon_width + 5

            # Calculate Position
            if i == 0: # Left
                # Right edge should be at (center_x - gap)
                # Center of box = (center_x - gap) - (width / 2)
                target_x = self.center_x - gap_from_center - (text_width / 2)
                target_y = self.center_y
                
                # Apply scale (slide out from center)
                x = self.center_x + (target_x - self.center_x) * scale
                y = target_y

            elif i == 2: # Right
                # Left edge should be at (center_x + gap)
                # Center of box = (center_x + gap) + (width / 2)
                target_x = self.center_x + gap_from_center + (text_width / 2)
                target_y = self.center_y

                # Apply scale
                x = self.center_x + (target_x - self.center_x) * scale
                y = target_y

            else: # Top (Center item)
                x = self.center_x
                y = self.center_y - self.radius * scale # Keep top item using radius

            # Draw rounded rectangle
            self._draw_rounded_rect(
                x - text_width // 2, y - text_height // 2,
                x + text_width // 2, y + text_height // 2,
                radius=8, fill=bg_color, outline=self.theme['border'], width=1 if not is_active else 2
            )

            # Draw icon
            if icon:
                self.canvas.create_text(
                    x - text_width // 2 + icon_width // 2 + padding,
                    y,
                    text=icon,
                    fill=text_color,
                    font=self.font_icon,
                    anchor='center'
                )
                text_x = x + icon_width // 2
            else:
                text_x = x

            # Draw text
            self.canvas.create_text(
                text_x,
                y,
                text=self.options[i],
                fill=text_color,
                font=active_font,
                anchor='center'
            )

    def _draw_center(self, scale: float):
        """Draw center circle with title"""
        # Draw circle
        r = self.center_radius * scale
        self._draw_circle(
            self.center_x, self.center_y, r,
            fill=self.theme['segment_active'],
            outline=self.theme['accent_glow'],
            width=2
        )

        # Draw title
        if self.title:
            self.canvas.create_text(
                self.center_x,
                self.center_y - 110,  # Moved higher up to avoid overlap
                text=self.title,
                fill=self.theme['text_active'],
                font=self.font_title,
                anchor='center'
            )

    def _draw_progress_bar(self, scale: float):
        """Draw progress bar under center"""
        bar_width = 100 * scale
        bar_height = 8 * scale
        x = self.center_x - bar_width // 2
        y = self.center_y + self.center_radius + 15

        # Background
        self._draw_rounded_rect(
            x, y, x + bar_width, y + bar_height,
            radius=4, fill=self.theme['progress_bg'], outline=''
        )

        # Fill
        fill_width = bar_width * self.progress_value
        if fill_width > 0:
            self._draw_rounded_rect(
                x, y, x + fill_width, y + bar_height,
                radius=4, fill=self.theme['progress_fill'], outline=''
            )

    def _draw_hint(self, scale: float):
        """Draw hint text at bottom"""
        # Position hint closer to center/segments
        y = self.center_y + self.radius // 2 + 50

        self.canvas.create_text(
            self.center_x,
            y * scale,
            text=self.subtitle,
            fill=self.theme['text_inactive'],
            font=self.font_option,
            anchor='center'
        )

    def _draw_circle(self, x: float, y: float, radius: float, **kwargs):
        """Draw a circle"""
        self.canvas.create_oval(
            x - radius, y - radius,
            x + radius, y + radius,
            **kwargs
        )

    def _draw_rounded_rect(self, x1: float, y1: float, x2: float, y2: float,
                          radius: float = 10, **kwargs):
        """Draw a rounded rectangle"""
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1
        ]

        return self.canvas.create_polygon(points, smooth=True, **kwargs)

    @staticmethod
    def _ease_out_back(t: float) -> float:
        """Easing function for smooth animation with slight overshoot"""
        c1 = 1.70158
        c3 = c1 + 1
        return 1 + c3 * pow(t - 1, 3) + c1 * pow(t - 1, 2)

    def _destroy_canvas(self):
        """Destroy canvas window"""
        if self.canvas and self.canvas.winfo_exists():
            try:
                self.canvas.window.destroy()
            except:
                pass
        self.canvas = None
        self.visible = False


class EnhancedUIManager:
    """Thread-safe UI manager with enhanced visuals"""

    def __init__(self, theme='DARK'):
        self.menu = RadialMenu(theme)
        self.ui_thread: Optional[threading.Thread] = None
        self.hide_timer = None

    def update_theme_color(self, settings: Dict[str, str]):
        """Update theme colors (thread-safe)"""
        if self.menu.root:
            self.menu.root.after(0, lambda: self.menu.update_theme_color(settings))

    def save_theme(self, theme_name):
        """Save theme to file (thread-safe)"""
        if self.menu.root:
            self.menu.root.after(0, lambda: self.menu.save_current_theme(theme_name))

    def start(self):
        """Start UI in separate thread"""
        def ui_thread_func():
            self.menu.init_ui()
            self.menu.root.mainloop()

        self.ui_thread = threading.Thread(target=ui_thread_func, daemon=True)
        self.ui_thread.start()

        # Wait for UI to initialize
        import time
        time.sleep(0.5)

    def _cancel_hide(self):
        """Cancel pending hide timer"""
        if self.hide_timer and self.menu.root:
            try:
                self.menu.root.after_cancel(self.hide_timer)
            except:
                pass
            self.hide_timer = None

    def show_menu(self, display: Dict[str, str], progress: float = None,
                  icons: Dict[str, str] = None):
        """Show menu (thread-safe)"""
        if self.menu.root:
            self._cancel_hide()
            self.menu.root.after(0, lambda: self.menu.show_menu(display, progress=progress, icons=icons))

    def hide_menu(self):
        """Hide menu (thread-safe)"""
        if self.menu.root:
            self._cancel_hide()
            self.menu.root.after(0, self.menu.hide_menu)

    def show_notification(self, message: str, duration_ms: int = 1500):
        """Show notification (simple for now, can be enhanced)"""
        # For now, show as a simple menu
        if self.menu.root:
            self._cancel_hide()
            
            display = {
                'center': message,
                'left': '',
                'right': '',
                'subtitle': ''
            }
            self.menu.root.after(0, lambda: self.menu.show_menu(display))
            
            # Schedule hide
            self.hide_timer = self.menu.root.after(duration_ms, self.menu.hide_menu)

    def quit(self):
        """Quit UI"""
        if self.menu.root:
            self.menu.root.after(0, self.menu.root.quit)


# ============================================================================ 
# TESTING
# ============================================================================ 

if __name__ == "__main__":
    import time

    print("Testing Enhanced Overlay UI...")

    # Test with different themes
    for theme_name in ['DARK', 'CYBER']:
        print(f"\nTesting {theme_name} theme...")

        ui = EnhancedUIManager(theme=theme_name)
        ui.start()

        # Test notification
        print("  Showing notification...")
        ui.show_notification(f"Testing {theme_name} Theme", 2000)
        time.sleep(2.5)

        # Test menu with icons
        print("  Showing menu...")
        ui.show_menu({
            'left': 'Previous Track',
            'center': 'Play/Pause',
            'right': 'Next Track',
            'title': '♪ Media',
            'subtitle': 'Double-tap to exit'
        }, icons={
            'left': '⏮',
            'center': '⏯',
            'right': '⏭'
        })
        time.sleep(2)

        # Test with progress bar
        print("  Showing menu with progress...")
        for i in range(11):
            ui.show_menu({
                'left': 'Volume Down',
                'center': f'{i*10}%',
                'right': 'Volume Up',
                'title': '🔊 Volume',
                'subtitle': 'Double-tap to exit'
            }, progress=i/10)
            time.sleep(0.2)

        time.sleep(1)

        print("  Hiding menu...")
        ui.hide_menu()
        time.sleep(1)

        ui.quit()
        time.sleep(0.5)

    print("\nDone!")