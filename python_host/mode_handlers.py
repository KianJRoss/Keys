"""
Mode Handlers - Implement behavior for each menu mode

Each handler implements:
- on_enter: Setup when mode is activated
- on_exit: Cleanup when mode is exited
- on_rotation: Handle encoder rotation (CW/CCW)
- on_press: Handle encoder press
- get_display_text: Return text for overlay UI
"""

from menu_system import ModeHandler, AppState, MenuMode
from windows_api import SystemAPI
from typing import Dict
import time
import threading


# ============================================================================
# MEDIA CONTROL MODE
# ============================================================================

class MediaModeHandler(ModeHandler):
    """Media control: Play/Pause, Next/Prev track"""

    def __init__(self, api: SystemAPI, state_machine):
        self.api = api
        self.sm = state_machine
        self.last_active = -1
        self.reset_timer: threading.Timer = None

    def on_enter(self, state: AppState):
        self.last_active = -1
        if self.reset_timer:
            self.reset_timer.cancel()

    def on_exit(self, state: AppState):
        if self.reset_timer:
            self.reset_timer.cancel()

    def _trigger_highlight(self, index: int):
        """Highlight an item briefly"""
        self.last_active = index
        
        if self.reset_timer:
            self.reset_timer.cancel()
            
        self.reset_timer = threading.Timer(0.5, self._reset_active)
        self.reset_timer.start()

    def _reset_active(self):
        """Reset highlight to neutral"""
        self.last_active = -1
        self.sm.update_display()

    def on_rotation(self, state: AppState, clockwise: bool):
        """Rotate: Next/Previous track"""
        if clockwise:
            self.api.media.next_track()
            self._trigger_highlight(2)
        else:
            self.api.media.prev_track()
            self._trigger_highlight(0)

    def on_press(self, state: AppState):
        """Press: Play/Pause"""
        self.api.media.play_pause()
        self._trigger_highlight(1)

    def get_display_text(self, state: AppState) -> Dict[str, str]:
        return {
            'left': 'Previous Track',
            'center': 'Play/Pause',
            'right': 'Next Track',
            'title': '',
            'icons': {'left': '⏮', 'center': '⏯', 'right': '⏭'},
            'active_index': self.last_active,
            'pulsing': self.last_active != -1
        }


# ============================================================================
# VOLUME CONTROL MODE
# ============================================================================

class VolumeModeHandler(ModeHandler):
    """System volume control"""

    def __init__(self, api: SystemAPI, volume_step: int = 2):
        self.api = api
        self.volume_step = volume_step

    def on_enter(self, state: AppState):
        pass

    def on_exit(self, state: AppState):
        pass

    def on_rotation(self, state: AppState, clockwise: bool):
        """Rotate: Adjust volume"""
        if clockwise:
            self.api.volume.adjust_volume(self.volume_step)
        else:
            self.api.volume.adjust_volume(-self.volume_step)

    def on_press(self, state: AppState):
        """Press: Toggle mute"""
        self.api.volume.toggle_mute()

    def get_display_text(self, state: AppState) -> Dict[str, str]:
        volume = self.api.volume.get_volume()
        muted = self.api.volume.get_mute()

        return {
            'left': 'Volume Down',
            'center': f'{volume}%',
            'right': 'Volume Up',
            'title': '🔇 MUTED' if muted else '🔊 Volume',
            'progress': volume / 100.0,
            'icons': {'left': '−', 'center': '🔇' if muted else '🔊', 'right': '+'}
        }


# ============================================================================
# WINDOW MENU MODE (Submenu selector)
# ============================================================================

class WindowMenuHandler(ModeHandler):
    """Window manager submenu selector"""

    def __init__(self, state_machine):
        self.sm = state_machine
        self.submenus = [
            {'name': 'Window Cycle', 'mode': MenuMode.WINDOW_CYCLE},
            {'name': 'Window Snap', 'mode': MenuMode.WINDOW_SNAP},
            {'name': 'Show Desktop', 'action': self._show_desktop}
        ]

    def _show_desktop(self):
        """Action: Show desktop"""
        self.sm.api.windows.show_desktop()
        self.sm.exit_menu_mode()

    def on_enter(self, state: AppState):
        state.submenu_index = 0

    def on_exit(self, state: AppState):
        pass

    def on_rotation(self, state: AppState, clockwise: bool):
        """Rotate: Cycle through submenus"""
        if clockwise:
            state.submenu_index = (state.submenu_index + 1) % len(self.submenus)
        else:
            state.submenu_index = (state.submenu_index - 1) % len(self.submenus)

    def on_press(self, state: AppState):
        """Press: Execute selected submenu"""
        submenu = self.submenus[state.submenu_index]
        if 'mode' in submenu:
            # Enter submenu mode
            self.sm.enter_mode(submenu['mode'])
        elif 'action' in submenu:
            # Execute action
            submenu['action']()

    def get_display_text(self, state: AppState) -> Dict[str, str]:
        total = len(self.submenus)
        prev_idx = (state.submenu_index - 1) % total
        next_idx = (state.submenu_index + 1) % total

        return {
            'left': self.submenus[prev_idx]['name'],
            'center': f"▶ {self.submenus[state.submenu_index]['name']}",
            'right': self.submenus[next_idx]['name']
        }


# ============================================================================
# WINDOW CYCLE MODE (Alt-Tab like)
# ============================================================================

class WindowCycleHandler(ModeHandler):
    """Alt-Tab like window cycling"""

    def __init__(self, api: SystemAPI):
        self.api = api

    def on_enter(self, state: AppState):
        """Build window list"""
        state.window_list = self.api.windows.get_visible_windows()
        state.submenu_index = 0

    def on_exit(self, state: AppState):
        state.window_list = []

    def on_rotation(self, state: AppState, clockwise: bool):
        """Rotate: Cycle through windows"""
        if not state.window_list:
            return

        if clockwise:
            state.submenu_index = (state.submenu_index + 1) % len(state.window_list)
        else:
            state.submenu_index = (state.submenu_index - 1) % len(state.window_list)

    def on_press(self, state: AppState):
        """Press: Switch to selected window"""
        if state.window_list and 0 <= state.submenu_index < len(state.window_list):
            window = state.window_list[state.submenu_index]
            if self.api.windows.activate_window(window.hwnd):
                # Exit after successful switch
                from menu_system import MenuMode
                state.menu_mode = MenuMode.NORMAL

    def get_display_text(self, state: AppState) -> Dict[str, str]:
        if not state.window_list:
            return {
                'left': '',
                'center': '⚠ No windows found',
                'right': ''
            }

        if len(state.window_list) == 1:
            title = state.window_list[0].title[:22]
            return {
                'left': '',
                'center': f'▶ {title}',
                'right': ''
            }

        # Multiple windows
        total = len(state.window_list)
        prev_idx = (state.submenu_index - 1) % total
        next_idx = (state.submenu_index + 1) % total

        prev_title = state.window_list[prev_idx].title[:22]
        curr_title = state.window_list[state.submenu_index].title[:22]
        next_title = state.window_list[next_idx].title[:22]

        return {
            'left': prev_title,
            'center': f'▶ {curr_title}',
            'right': next_title
        }


# ============================================================================
# WINDOW SNAP MODE
# ============================================================================

class WindowSnapHandler(ModeHandler):
    """Window snapping to screen edges"""

    def __init__(self, api: SystemAPI, state_machine):
        self.api = api
        self.sm = state_machine
        self.snap_options = [
            {'name': '◧ Snap Left', 'action': api.windows.snap_window_left},
            {'name': '◨ Snap Right', 'action': api.windows.snap_window_right},
            {'name': '⬜ Maximize', 'action': api.windows.maximize_window}
        ]

    def on_enter(self, state: AppState):
        state.submenu_index = 0

    def on_exit(self, state: AppState):
        pass

    def on_rotation(self, state: AppState, clockwise: bool):
        """Rotate: Cycle through snap options"""
        if clockwise:
            state.submenu_index = (state.submenu_index + 1) % len(self.snap_options)
        else:
            state.submenu_index = (state.submenu_index - 1) % len(self.snap_options)

    def on_press(self, state: AppState):
        """Press: Execute snap action and exit"""
        option = self.snap_options[state.submenu_index]
        option['action']()
        # Exit after snapping
        self.sm.exit_menu_mode()

    def get_display_text(self, state: AppState) -> Dict[str, str]:
        total = len(self.snap_options)
        prev_idx = (state.submenu_index - 1) % total
        next_idx = (state.submenu_index + 1) % total

        return {
            'left': self.snap_options[prev_idx]['name'],
            'center': f"▶ {self.snap_options[state.submenu_index]['name']}",
            'right': self.snap_options[next_idx]['name']
        }


# ============================================================================
# VOICEMEETER HANDLERS
# ============================================================================

class VoicemeeterMenuHandler(ModeHandler):
    """Voicemeeter submenu selector"""

    def __init__(self, state_machine, vm_controller):
        self.sm = state_machine
        self.vm = vm_controller
        self.submenus = [
            {'name': 'Microphone Control', 'mode': MenuMode.VM_MIC},
            {'name': 'Main Routing', 'mode': MenuMode.VM_MAIN_ROUTING},
            {'name': 'Music Gain', 'mode': MenuMode.VM_MUSIC_GAIN},
            {'name': 'Music Routing', 'mode': MenuMode.VM_MUSIC_ROUTING},
            {'name': 'Comm Gain', 'mode': MenuMode.VM_COMM_GAIN},
            {'name': 'Comm Routing', 'mode': MenuMode.VM_COMM_ROUTING},
        ]

    def on_enter(self, state: AppState):
        state.submenu_index = 0

    def on_exit(self, state: AppState):
        pass

    def on_rotation(self, state: AppState, clockwise: bool):
        """Rotate: Cycle through submenus"""
        if clockwise:
            state.submenu_index = (state.submenu_index + 1) % len(self.submenus)
        else:
            state.submenu_index = (state.submenu_index - 1) % len(self.submenus)

    def on_press(self, state: AppState):
        """Press: Enter selected submenu"""
        submenu = self.submenus[state.submenu_index]
        self.sm.enter_mode(submenu['mode'])

    def get_display_text(self, state: AppState) -> Dict[str, str]:
        total = len(self.submenus)
        prev_idx = (state.submenu_index - 1) % total
        next_idx = (state.submenu_index + 1) % total

        return {
            'left': self.submenus[prev_idx]['name'],
            'center': f"▶ {self.submenus[state.submenu_index]['name']}",
            'right': self.submenus[next_idx]['name']
        }


class VMMicHandler(ModeHandler):
    """Microphone Gain + Mute control (Strip 0)"""

    def __init__(self, vm_controller):
        self.vm = vm_controller
        self.strip = 0 # Strip 0 is Mic
        self.gain_step = 3.0

    def on_enter(self, state: AppState):
        pass

    def on_exit(self, state: AppState):
        pass

    def on_rotation(self, state: AppState, clockwise: bool):
        """Rotate: Adjust mic gain"""
        if clockwise:
            self.vm.adjust_strip_gain(self.strip, self.gain_step)
        else:
            self.vm.adjust_strip_gain(self.strip, -self.gain_step)

    def on_press(self, state: AppState):
        """Press: Toggle mic mute"""
        self.vm.toggle_mic_mute()

    def get_display_text(self, state: AppState) -> Dict[str, str]:
        gain = round(self.vm.get_strip_gain(self.strip))
        muted = self.vm.get_mic_mute()
        
        # Normalize gain to 0-1 range (-60 to +12 dB)
        progress = (gain + 60) / 72.0

        return {
            'left': 'Gain Down',
            'center': f'{gain} dB',
            'right': 'Gain Up',
            'title': '🎤 MIC MUTED' if muted else '🎤 Microphone',
            'progress': max(0.0, min(1.0, progress)),
            'icons': {'left': '−', 'center': '🔇' if muted else '🎤', 'right': '+'}
        }


class VMRoutingHandler(ModeHandler):
    """Audio routing control (Main/Music/Comm to A1/A2/A3)"""

    def __init__(self, vm_controller, strip: int, strip_name: str):
        self.vm = vm_controller
        self.strip = strip
        self.strip_name = strip_name
        self.outputs = ['A1', 'A2', 'A3']
        self.output_names = ['Speakers', 'Wired', 'Wireless']
        self.output_icons = ['🔊', '🎧', '📡']

    def on_enter(self, state: AppState):
        state.routing_selection = 0  # Start at A1

    def on_exit(self, state: AppState):
        pass

    def on_rotation(self, state: AppState, clockwise: bool):
        """Rotate: Select output"""
        if clockwise:
            state.routing_selection = (state.routing_selection + 1) % 3
        else:
            state.routing_selection = (state.routing_selection - 1) % 3
        time.sleep(0.03)  # Brief delay for smooth display

    def on_press(self, state: AppState):
        """Press: Toggle selected output"""
        output = self.outputs[state.routing_selection]
        self.vm.toggle_routing(self.strip, output)
        time.sleep(0.05)  # Wait for update

    def get_display_text(self, state: AppState) -> Dict[str, str]:
        # Get current routing states
        states = [self.vm.get_routing(self.strip, out) for out in self.outputs]

        prev_idx = (state.routing_selection - 1) % 3
        next_idx = (state.routing_selection + 1) % 3

        # Show status
        status = "ON" if states[state.routing_selection] else "OFF"

        return {
            'left': self.output_names[prev_idx],
            'center': f"{self.output_names[state.routing_selection]} [{status}]",
            'right': self.output_names[next_idx],
            'title': f'🎚 {self.strip_name} Routing',
            'icons': {
                'left': self.output_icons[prev_idx] if states[prev_idx] else '⊘',
                'center': self.output_icons[state.routing_selection] if states[state.routing_selection] else '⊘',
                'right': self.output_icons[next_idx] if states[next_idx] else '⊘'
            }
        }


class VMGainHandler(ModeHandler):
    """Strip gain control"""

    def __init__(self, vm_controller, strip: int, strip_name: str, icon: str):
        self.vm = vm_controller
        self.strip = strip
        self.strip_name = strip_name
        self.icon = icon
        self.gain_step = 3.0

    def on_enter(self, state: AppState):
        pass

    def on_exit(self, state: AppState):
        pass

    def on_rotation(self, state: AppState, clockwise: bool):
        """Rotate: Adjust gain"""
        if clockwise:
            self.vm.adjust_strip_gain(self.strip, self.gain_step)
        else:
            self.vm.adjust_strip_gain(self.strip, -self.gain_step)

    def on_press(self, state: AppState):
        """Press: Reset gain to 0 dB"""
        self.vm.set_strip_gain(self.strip, 0.0)

    def get_display_text(self, state: AppState) -> Dict[str, str]:
        gain = round(self.vm.get_strip_gain(self.strip))
        # Normalize gain to 0-1 range (assuming -60 to +12 dB range)
        progress = (gain + 60) / 72.0

        return {
            'left': 'Gain Down',
            'center': f'{gain} dB',
            'right': 'Gain Up',
            'title': f'{self.icon} {self.strip_name} Gain',
            'progress': max(0.0, min(1.0, progress)),
            'icons': {'left': '−', 'center': self.icon, 'right': '+'}
        }


import json
import os

# ============================================================================
# THEME SELECTION MODE
# ============================================================================

class ThemeMenuHandler(ModeHandler):
    """Theme submenu selector"""

    def __init__(self, state_machine):
        self.sm = state_machine
        self.submenus = [
            {'name': 'Box Color', 'mode': MenuMode.THEME_BOX},
            {'name': 'Accent Color', 'mode': MenuMode.THEME_ACCENT},
            {'name': 'Text Color', 'mode': MenuMode.THEME_TEXT},
        ]

    def on_enter(self, state: AppState):
        state.submenu_index = 0

    def on_exit(self, state: AppState):
        pass

    def on_rotation(self, state: AppState, clockwise: bool):
        """Cycle submenus"""
        if clockwise:
            state.submenu_index = (state.submenu_index + 1) % len(self.submenus)
        else:
            state.submenu_index = (state.submenu_index - 1) % len(self.submenus)

    def on_press(self, state: AppState):
        """Enter selected submenu"""
        submenu = self.submenus[state.submenu_index]
        self.sm.enter_mode(submenu['mode'])

    def get_display_text(self, state: AppState) -> Dict[str, str]:
        total = len(self.submenus)
        prev_idx = (state.submenu_index - 1) % total
        next_idx = (state.submenu_index + 1) % total

        return {
            'left': self.submenus[prev_idx]['name'],
            'center': f"▶ {self.submenus[state.submenu_index]['name']}",
            'right': self.submenus[next_idx]['name'],
            'title': '🎨 Theme Settings'
        }


class ThemeColorHandler(ModeHandler):
    """Color picker for theme elements"""

    COLORS = [
        ("White", "#FFFFFF"), ("Red", "#FF0000"), ("Green", "#00FF00"), 
        ("Blue", "#0088FF"), ("Yellow", "#FFFF00"), ("Cyan", "#00FFFF"), 
        ("Magenta", "#FF00FF"), ("Orange", "#FFA500"), ("Purple", "#800080"), 
        ("Black", "#000000"), ("Gray", "#808080"), ("Dark Gray", "#2d2d2d")
    ]

    def __init__(self, color_type: str):
        self.color_type = color_type
        self.current_idx = 0
        self.should_save = False

    def on_enter(self, state: AppState):
        self.current_idx = 0
        self.should_save = False

    def on_exit(self, state: AppState):
        pass

    def on_rotation(self, state: AppState, clockwise: bool):
        """Cycle colors"""
        if clockwise:
            self.current_idx = (self.current_idx + 1) % len(self.COLORS)
        else:
            self.current_idx = (self.current_idx - 1) % len(self.COLORS)

    def on_press(self, state: AppState):
        """Confirm and Save"""
        self.should_save = True
        from menu_system import MenuMode
        state.menu_mode = MenuMode.THEME_MENU

    def get_display_text(self, state: AppState) -> Dict[str, str]:
        total = len(self.COLORS)
        prev_idx = (self.current_idx - 1) % total
        next_idx = (self.current_idx + 1) % total
        
        prev_name, _ = self.COLORS[prev_idx]
        curr_name, hex_code = self.COLORS[self.current_idx]
        next_name, _ = self.COLORS[next_idx]
        
        # Build theme update dictionary
        settings = {}
        if self.color_type == 'box':
            settings = {'segment_inactive': hex_code, 'progress_bg': hex_code}
        elif self.color_type == 'accent':
            settings = {
                'segment_active': hex_code, 
                'accent': hex_code, 
                'accent_glow': hex_code,
                'progress_fill': hex_code,
                'border': hex_code
            }
        elif self.color_type == 'text':
            settings = {'text_active': hex_code}

        res = {
            'left': prev_name,
            'center': f"▶ {curr_name}",
            'right': next_name,
            'title': f'🎨 {self.color_type.title()} Color',
            'set_theme_color': settings
        }

        if self.should_save:
            # We don't know the exact theme name here easily, 
            # but we can save to 'CUSTOM' or the currently active one.
            # For simplicity, let's assume the user is updating the current active theme.
            # In keychron_app.py we can pass the theme name or just have it save the current.
            res['save_theme'] = 'CUSTOM' 
            self.should_save = False
            
        return res


# ============================================================================
# HANDLER FACTORY
# ============================================================================

def create_handlers(api: SystemAPI, state_machine, vm_controller=None) -> Dict[MenuMode, ModeHandler]:
    """Create all mode handlers

    Args:
        api: SystemAPI instance
        state_machine: MenuStateMachine instance
        vm_controller: VoicemeeterController instance (optional)

    Returns:
        Dict mapping MenuMode to ModeHandler instance
    """
    handlers = {
        MenuMode.MEDIA: MediaModeHandler(api, state_machine),
        MenuMode.VOLUME: VolumeModeHandler(api),
        MenuMode.THEME_MENU: ThemeMenuHandler(state_machine),
        MenuMode.THEME_BOX: ThemeColorHandler('box'),
        MenuMode.THEME_ACCENT: ThemeColorHandler('accent'),
        MenuMode.THEME_TEXT: ThemeColorHandler('text'),
        MenuMode.WINDOW_MENU: WindowMenuHandler(state_machine),
        MenuMode.WINDOW_CYCLE: WindowCycleHandler(api),
        MenuMode.WINDOW_SNAP: WindowSnapHandler(api, state_machine),
    }

    # Add Voicemeeter handlers if available
    if vm_controller and vm_controller.is_available():
        from voicemeeter_api import VoicemeeterConfig
        config = VoicemeeterConfig()

        handlers.update({
            MenuMode.VOICEMEETER_MENU: VoicemeeterMenuHandler(state_machine, vm_controller),
            MenuMode.VM_MIC: VMMicHandler(vm_controller),
            MenuMode.VM_MAIN_ROUTING: VMRoutingHandler(vm_controller, config.MAIN_STRIP, "Main"),
            MenuMode.VM_MUSIC_GAIN: VMGainHandler(vm_controller, config.MUSIC_STRIP, "Music", "🎵"),
            MenuMode.VM_MUSIC_ROUTING: VMRoutingHandler(vm_controller, config.MUSIC_STRIP, "Music"),
            MenuMode.VM_COMM_GAIN: VMGainHandler(vm_controller, config.COMM_STRIP, "Comm", "💬"),
            MenuMode.VM_COMM_ROUTING: VMRoutingHandler(vm_controller, config.COMM_STRIP, "Comm"),
        })

    return handlers
