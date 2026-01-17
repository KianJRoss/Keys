"""
Enhanced Overlay UI - Modern Radial Wheel Design

Creates a sleek circular menu with:
- True arc segments forming a wheel
- Glow and shadow effects
- Smooth animations
- Modern glassmorphism-inspired styling
- Theme support with persistence
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
    DARK = {
        'bg': '#1a1a1a',
        'bg_alpha': 0.95,
        'segment_inactive': '#2a2a2a',
        'segment_active': '#3d8aff',
        'segment_hover': '#3a3a3a',
        'text_inactive': '#808080',
        'text_active': '#ffffff',
        'accent': '#3d8aff',
        'accent_glow': '#5ba3ff',
        'border': '#404040',
        'progress_bg': '#2a2a2a',
        'progress_fill': '#3d8aff',
        'shadow': '#000000',
        'glow': '#3d8aff',
    }


def load_themes():
    """Load themes from themes.json"""
    theme_file = os.path.join(os.path.dirname(__file__), 'themes.json')
    if os.path.exists(theme_file):
        try:
            with open(theme_file, 'r') as f:
                themes = json.load(f)
                for name, data in themes.items():
                    # Ensure glow color exists (fallback to accent)
                    if 'glow' not in data:
                        data['glow'] = data.get('accent', '#3d8aff')
                    setattr(Theme, name, data)
        except Exception as e:
            print(f"Error loading themes: {e}")


class RadialMenu:
    """Modern circular wheel menu overlay"""

    def __init__(self, theme_name='DARK'):
        self.root: Optional[tk.Tk] = None
        self.canvas: Optional[tk.Canvas] = None
        self.visible = False
        self.current_theme_name = theme_name

        # Load custom themes
        load_themes()

        # Theme
        self.theme = getattr(Theme, theme_name, Theme.DARK)
        if not isinstance(self.theme, dict):
            self.theme = Theme.DARK

        # Menu state
        self.options: List[str] = []
        self.active_index = 1  # Center/top item
        self.title = ""
        self.subtitle = ""
        self.progress_value: Optional[float] = None
        self.icons: Dict[str, str] = {}

        # Wheel geometry
        self.canvas_size = 400
        self.center_x = self.canvas_size // 2
        self.center_y = self.canvas_size // 2
        self.outer_radius = 140
        self.inner_radius = 50
        self.center_dot_radius = 8

        # Segment angles (degrees) - 3 segments
        # Left: 150-210, Top: 60-120 (center), Right: -30 to 30
        self.segments = [
            {'start': 150, 'extent': 60, 'pos': 'left'},    # Left
            {'start': 60, 'extent': 60, 'pos': 'center'},   # Top (center)
            {'start': -30, 'extent': 60, 'pos': 'right'},   # Right
        ]

        # Animation
        self.animation_progress = 0.0
        self.target_progress = 1.0
        self.animation_speed = 0.12
        self.animation_timer = None

        # Pulse animation
        self.pulse_phase = 0.0
        self.pulsing = False

        # Screen position
        self.screen_x = 0
        self.screen_y = 0

        # Fonts
        self.font_title = None
        self.font_option = None
        self.font_icon = None
        self.font_small = None

    def set_theme(self, theme_name: str):
        """Change theme at runtime"""
        new_theme = getattr(Theme, theme_name, None)
        if isinstance(new_theme, dict):
            self.theme = new_theme
            self.current_theme_name = theme_name
            if self.visible and self.canvas:
                self._update_window_alpha()
                self._draw_menu()

    def _update_window_alpha(self):
        """Update window transparency"""
        if self.canvas and hasattr(self.canvas, 'window'):
            try:
                self.canvas.window.attributes('-alpha', self.theme.get('bg_alpha', 0.95))
            except:
                pass

    def update_theme_color(self, settings: Dict[str, str]):
        """Update specific theme colors at runtime"""
        for key, value in settings.items():
            if key in self.theme:
                self.theme[key] = value
        if self.visible and self.canvas:
            self._draw_menu()

    def save_current_theme(self, theme_name: str):
        """Save current theme colors to themes.json"""
        theme_file = os.path.join(os.path.dirname(__file__), 'themes.json')
        themes = {}
        if os.path.exists(theme_file):
            try:
                with open(theme_file, 'r') as f:
                    themes = json.load(f)
            except:
                pass

        themes[theme_name] = dict(self.theme)

        try:
            with open(theme_file, 'w') as f:
                json.dump(themes, f, indent=4)
        except Exception as e:
            print(f"Error saving theme: {e}")

    def init_ui(self):
        """Initialize UI (must be called from main thread)"""
        self.root = tk.Tk()
        self.root.withdraw()

        # Setup fonts
        self.font_title = tkfont.Font(family="Segoe UI Semibold", size=13)
        self.font_option = tkfont.Font(family="Segoe UI", size=11)
        self.font_icon = tkfont.Font(family="Segoe UI Emoji", size=16)
        self.font_small = tkfont.Font(family="Segoe UI", size=9)

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
        self.active_index = display.get('active_index', 1)
        self.pulsing = display.get('pulsing', False)

        # Create/update canvas
        if not self.canvas or not self.canvas.winfo_exists():
            self._create_canvas()

        self._position_window()

        # Start animation
        self.cancel_animation()
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
        window = tk.Toplevel(self.root)
        window.overrideredirect(True)
        window.attributes('-topmost', True)
        window.attributes('-alpha', self.theme.get('bg_alpha', 0.95))

        # Transparent background
        transparent_color = '#010101'
        try:
            window.wm_attributes('-transparentcolor', transparent_color)
        except:
            pass

        self.canvas = tk.Canvas(
            window,
            width=self.canvas_size,
            height=self.canvas_size,
            bg=transparent_color,
            highlightthickness=0
        )
        self.canvas.pack()
        self.canvas.window = window

    def _position_window(self):
        """Position window centered on cursor"""
        if not self.canvas:
            return

        x = self.screen_x - self.canvas_size // 2
        y = self.screen_y - self.canvas_size // 2
        self.canvas.window.geometry(f"{self.canvas_size}x{self.canvas_size}+{x}+{y}")

    def _animate(self, on_complete=None):
        """Smooth animation loop"""
        if not self.canvas or not self.canvas.winfo_exists():
            return

        # Follow mouse
        self.screen_x = self.root.winfo_pointerx()
        self.screen_y = self.root.winfo_pointery()
        self._position_window()

        # Update pulse
        self.pulse_phase += 0.15

        # Update progress
        diff = self.target_progress - self.animation_progress
        speed = self.animation_speed * (2.0 if self.target_progress < 0.1 else 1.0)
        threshold = 0.1 if self.target_progress < 0.1 else 0.005

        if abs(diff) > threshold:
            self.animation_progress += diff * speed
            self._draw_menu()
            self.animation_timer = self.root.after(16, lambda: self._animate(on_complete))
        else:
            self.animation_progress = self.target_progress
            self._draw_menu()

            if self.target_progress > 0.5 and self.visible:
                self.animation_timer = self.root.after(16, lambda: self._animate(on_complete))
            elif on_complete:
                on_complete()

    def _draw_menu(self):
        """Draw the wheel menu"""
        if not self.canvas:
            return

        self.canvas.delete('all')
        scale = self._ease_out_cubic(self.animation_progress)

        # Draw outer glow
        self._draw_glow(scale)

        # Draw wheel segments
        self._draw_wheel_segments(scale)

        # Draw center hub
        self._draw_center_hub(scale)

        # Draw progress bar
        if self.progress_value is not None:
            self._draw_progress_ring(scale)

        # Draw title
        if self.title:
            self._draw_title(scale)

        # Draw subtitle hint
        if self.subtitle and scale > 0.5:
            self._draw_subtitle(scale)

    def _draw_glow(self, scale: float):
        """Draw subtle outer glow"""
        if scale < 0.1:
            return

        glow_color = self.theme.get('glow', self.theme['accent'])
        # Multiple expanding circles for glow effect
        for i in range(3):
            radius = (self.outer_radius + 10 + i * 8) * scale
            alpha_hex = format(int(20 - i * 6), '02x')
            try:
                # Blend glow with transparency
                self.canvas.create_oval(
                    self.center_x - radius, self.center_y - radius,
                    self.center_x + radius, self.center_y + radius,
                    outline=glow_color, width=2, fill=''
                )
            except:
                pass

    def _draw_wheel_segments(self, scale: float):
        """Draw the arc segments of the wheel"""
        outer_r = self.outer_radius * scale
        inner_r = self.inner_radius * scale

        for i, seg in enumerate(self.segments):
            if i >= len(self.options) or not self.options[i]:
                continue

            is_active = (i == self.active_index)

            # Determine colors
            if is_active and self.pulsing:
                pulse = (math.sin(self.pulse_phase) + 1) / 2
                bg_color = self._blend_colors(
                    self.theme['segment_active'],
                    self.theme['accent_glow'],
                    pulse * 0.5
                )
            elif is_active:
                bg_color = self.theme['segment_active']
            else:
                bg_color = self.theme['segment_inactive']

            text_color = self.theme['text_active'] if is_active else self.theme['text_inactive']
            border_color = self.theme['accent'] if is_active else self.theme['border']

            # Draw arc segment
            self._draw_arc_segment(
                seg['start'], seg['extent'],
                inner_r, outer_r,
                bg_color, border_color,
                width=2 if is_active else 1
            )

            # Calculate text position (middle of arc)
            mid_angle = math.radians(seg['start'] + seg['extent'] / 2)
            text_r = (inner_r + outer_r) / 2
            text_x = self.center_x + text_r * math.cos(mid_angle)
            text_y = self.center_y - text_r * math.sin(mid_angle)

            # Draw icon if present
            icon_key = seg['pos']
            icon = self.icons.get(icon_key, '')

            if icon:
                # Icon above text
                icon_offset = -12 if is_active else -10
                self.canvas.create_text(
                    text_x, text_y + icon_offset,
                    text=icon,
                    fill=text_color,
                    font=self.font_icon,
                    anchor='center'
                )
                text_y += 10

            # Draw label
            label = self.options[i]
            # Truncate if too long
            if len(label) > 15:
                label = label[:14] + "..."

            self.canvas.create_text(
                text_x, text_y,
                text=label,
                fill=text_color,
                font=self.font_option if not is_active else self.font_title,
                anchor='center'
            )

    def _draw_arc_segment(self, start_angle: float, extent: float,
                          inner_r: float, outer_r: float,
                          fill_color: str, outline_color: str, width: int = 1):
        """Draw a single arc segment (donut slice)"""
        # Create arc using polygon points
        points = []
        steps = 20

        # Outer arc (forward)
        for i in range(steps + 1):
            angle = math.radians(start_angle + (extent * i / steps))
            x = self.center_x + outer_r * math.cos(angle)
            y = self.center_y - outer_r * math.sin(angle)
            points.extend([x, y])

        # Inner arc (backward)
        for i in range(steps, -1, -1):
            angle = math.radians(start_angle + (extent * i / steps))
            x = self.center_x + inner_r * math.cos(angle)
            y = self.center_y - inner_r * math.sin(angle)
            points.extend([x, y])

        self.canvas.create_polygon(
            points,
            fill=fill_color,
            outline=outline_color,
            width=width,
            smooth=False
        )

    def _draw_center_hub(self, scale: float):
        """Draw the center hub"""
        hub_r = self.inner_radius * scale - 5

        # Hub background
        self.canvas.create_oval(
            self.center_x - hub_r, self.center_y - hub_r,
            self.center_x + hub_r, self.center_y + hub_r,
            fill=self.theme['bg'],
            outline=self.theme['border'],
            width=2
        )

        # Center dot
        dot_r = self.center_dot_radius * scale
        self.canvas.create_oval(
            self.center_x - dot_r, self.center_y - dot_r,
            self.center_x + dot_r, self.center_y + dot_r,
            fill=self.theme['accent'],
            outline=self.theme['accent_glow'],
            width=2
        )

    def _draw_progress_ring(self, scale: float):
        """Draw progress as an arc around center hub"""
        if self.progress_value is None:
            return

        ring_r = self.inner_radius * scale - 15
        ring_width = 6

        # Background ring
        self.canvas.create_oval(
            self.center_x - ring_r, self.center_y - ring_r,
            self.center_x + ring_r, self.center_y + ring_r,
            outline=self.theme['progress_bg'],
            width=ring_width,
            fill=''
        )

        # Progress arc (starts from top, goes clockwise)
        if self.progress_value > 0:
            extent = -360 * self.progress_value  # Negative for clockwise
            self.canvas.create_arc(
                self.center_x - ring_r, self.center_y - ring_r,
                self.center_x + ring_r, self.center_y + ring_r,
                start=90, extent=extent,
                outline=self.theme['progress_fill'],
                width=ring_width,
                style='arc'
            )

    def _draw_title(self, scale: float):
        """Draw title above the wheel"""
        if scale < 0.3:
            return

        y = self.center_y - self.outer_radius * scale - 25
        self.canvas.create_text(
            self.center_x, y,
            text=self.title,
            fill=self.theme['text_active'],
            font=self.font_title,
            anchor='center'
        )

    def _draw_subtitle(self, scale: float):
        """Draw subtitle below the wheel"""
        y = self.center_y + self.outer_radius * scale + 20
        alpha = min(1.0, (scale - 0.5) * 2)

        self.canvas.create_text(
            self.center_x, y,
            text=self.subtitle,
            fill=self.theme['text_inactive'],
            font=self.font_small,
            anchor='center'
        )

    def _blend_colors(self, color1: str, color2: str, factor: float) -> str:
        """Blend two hex colors"""
        try:
            r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
            r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)

            r = int(r1 + (r2 - r1) * factor)
            g = int(g1 + (g2 - g1) * factor)
            b = int(b1 + (b2 - b1) * factor)

            return f'#{r:02x}{g:02x}{b:02x}'
        except:
            return color1

    @staticmethod
    def _ease_out_cubic(t: float) -> float:
        """Smooth easing function"""
        return 1 - pow(1 - t, 3)

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
    """Thread-safe UI manager"""

    def __init__(self, theme='DARK'):
        self.menu = RadialMenu(theme)
        self.ui_thread: Optional[threading.Thread] = None
        self.hide_timer = None

    def set_theme(self, theme_name: str):
        """Set theme (thread-safe)"""
        if self.menu.root:
            self.menu.root.after(0, lambda: self.menu.set_theme(theme_name))

    def update_theme_color(self, settings: Dict[str, str]):
        """Update theme colors (thread-safe)"""
        if self.menu.root:
            self.menu.root.after(0, lambda: self.menu.update_theme_color(settings))

    def save_theme(self, theme_name: str):
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
        """Show notification as simple centered message"""
        if self.menu.root:
            self._cancel_hide()

            display = {
                'center': message,
                'left': '',
                'right': '',
                'subtitle': ''
            }
            self.menu.root.after(0, lambda: self.menu.show_menu(display))
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

    print("Testing Modern Wheel UI...")

    ui = EnhancedUIManager(theme='DARK')
    ui.start()

    # Test notification
    print("  Showing notification...")
    ui.show_notification("Modern Wheel UI", 2000)
    time.sleep(2.5)

    # Test menu with icons
    print("  Showing media menu...")
    ui.show_menu({
        'left': 'Previous',
        'center': 'Play/Pause',
        'right': 'Next',
        'title': 'Media Controls',
        'subtitle': 'Double-tap to exit'
    }, icons={
        'left': '⏮',
        'center': '⏯',
        'right': '⏭'
    })
    time.sleep(3)

    # Test with progress
    print("  Showing volume with progress...")
    for i in range(11):
        ui.show_menu({
            'left': 'Down',
            'center': f'{i*10}%',
            'right': 'Up',
            'title': 'Volume',
            'active_index': 1
        }, progress=i/10, icons={
            'left': '−',
            'center': '🔊',
            'right': '+'
        })
        time.sleep(0.15)

    time.sleep(2)

    # Test active highlight
    print("  Testing segment highlights...")
    for active in [0, 1, 2, 1]:
        ui.show_menu({
            'left': 'Left Option',
            'center': 'Center',
            'right': 'Right Option',
            'title': 'Selection Test',
            'active_index': active
        })
        time.sleep(1)

    print("  Hiding...")
    ui.hide_menu()
    time.sleep(1)

    ui.quit()
    print("Done!")
