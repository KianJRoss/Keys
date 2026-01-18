"""
Voicemeeter API Integration

Wraps VoicemeeterRemote64.dll for controlling Voicemeeter Potato:
- Audio routing (strips to outputs A1/A2/A3)
- Gain control (strip volumes)
- Mute control
- Parameter get/set

Requirements:
    - Voicemeeter Potato installed
    - VoicemeeterRemote64.dll in system or specified path
"""

import ctypes
import os
import time
from typing import Optional
from pathlib import Path


class VoicemeeterAPI:
    """Voicemeeter Remote API wrapper"""

    def __init__(self, dll_path: Optional[str] = None):
        self.dll = None
        self.logged_in = False

        # Function pointers
        self.login = None
        self.logout = None
        self.run_voicemeeter = None
        self.set_parameter_float = None
        self.get_parameter_float = None
        self.is_parameters_dirty = None
        self.set_parameter_string = None
        self.get_parameter_string = None

        # Try to load DLL
        self._load_dll(dll_path)

    def _load_dll(self, dll_path: Optional[str] = None):
        """Load VoicemeeterRemote64.dll"""
        # Default paths to try
        search_paths = []

        if dll_path:
            search_paths.append(dll_path)

        # Common installation paths
        search_paths.extend([
            r"C:\Program Files (x86)\VB\Voicemeeter\VoicemeeterRemote64.dll",
            r"C:\Program Files\VB\Voicemeeter\VoicemeeterRemote64.dll",
            os.path.join(os.getenv('ProgramFiles(x86)', ''), 'VB', 'Voicemeeter', 'VoicemeeterRemote64.dll'),
            os.path.join(os.getenv('ProgramFiles', ''), 'VB', 'Voicemeeter', 'VoicemeeterRemote64.dll'),
        ])

        # Try to load from each path
        for path in search_paths:
            if path and os.path.exists(path):
                try:
                    self.dll = ctypes.CDLL(path)
                    print(f"[OK] Loaded Voicemeeter DLL: {path}")
                    self._init_functions()
                    return
                except Exception as e:
                    print(f"[WARN] Failed to load {path}: {e}")
                    continue

        print("[WARN] Voicemeeter DLL not found - Voicemeeter features disabled")
        print("Install Voicemeeter Potato from: https://vb-audio.com/Voicemeeter/potato.htm")

    def _init_functions(self):
        """Initialize function pointers from DLL"""
        if not self.dll:
            return

        try:
            # Login / Logout
            self.login = self.dll.VBVMR_Login
            self.login.restype = ctypes.c_long

            self.logout = self.dll.VBVMR_Logout
            self.logout.restype = ctypes.c_long

            # Run Voicemeeter
            self.run_voicemeeter = self.dll.VBVMR_RunVoicemeeter
            self.run_voicemeeter.argtypes = [ctypes.c_long]
            self.run_voicemeeter.restype = ctypes.c_long

            # Set/Get parameters (float)
            self.set_parameter_float = self.dll.VBVMR_SetParameterFloat
            self.set_parameter_float.argtypes = [ctypes.c_char_p, ctypes.c_float]
            self.set_parameter_float.restype = ctypes.c_long

            self.get_parameter_float = self.dll.VBVMR_GetParameterFloat
            self.get_parameter_float.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_float)]
            self.get_parameter_float.restype = ctypes.c_long

            # Check if parameters are dirty
            self.is_parameters_dirty = self.dll.VBVMR_IsParametersDirty
            self.is_parameters_dirty.restype = ctypes.c_long

            # Set/Get parameters (string)
            self.set_parameter_string = self.dll.VBVMR_SetParameterStringA
            self.set_parameter_string.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
            self.set_parameter_string.restype = ctypes.c_long

            self.get_parameter_string = self.dll.VBVMR_GetParameterStringA
            self.get_parameter_string.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_char)]
            self.get_parameter_string.restype = ctypes.c_long

        except Exception as e:
            print(f"[ERROR] Failed to initialize Voicemeeter functions: {e}")
            self.dll = None

    def connect(self) -> bool:
        """Connect to Voicemeeter (login)"""
        if not self.dll or not self.login:
            return False

        try:
            result = self.login()
            if result == 0 or result == 1:
                # 0 = OK, 1 = OK but Voicemeeter was already running
                self.logged_in = True

                # Start Voicemeeter if not running (type 2 = Potato)
                if result == 1:
                    self.run_voicemeeter(2)
                    time.sleep(1.0)  # Wait for Voicemeeter to initialize

                # Configure default routing: Mic (Strip 0) -> B1
                time.sleep(0.5)
                self.set_parameter("Strip[0].Mute", 0.0) # Ensure mic is not muted
                self.set_parameter("Strip[0].A1", 1.0) # Route mic to A1

                print("[OK] Connected to Voicemeeter Potato")
                return True
            else:
                print(f"[ERROR] Voicemeeter login failed: {result}")
                return False

        except Exception as e:
            print(f"[ERROR] Voicemeeter connection error: {e}")
            return False

    def disconnect(self):
        """Disconnect from Voicemeeter (logout)"""
        if self.logged_in and self.logout:
            try:
                self.logout()
                self.logged_in = False
                print("[OK] Disconnected from Voicemeeter")
            except:
                pass

    def set_parameter(self, param: str, value: float) -> bool:
        """Set a Voicemeeter parameter

        Args:
            param: Parameter name (e.g., "Strip[0].Mute", "Strip[5].Gain", "Strip[0].A1")
            value: Value (0.0/1.0 for boolean, -60.0 to 12.0 for gain)

        Returns:
            True if successful
        """
        if not self.logged_in or not self.set_parameter_float:
            return False

        try:
            param_bytes = param.encode('ascii')
            result = self.set_parameter_float(param_bytes, ctypes.c_float(value))
            return result == 0
        except Exception as e:
            print(f"[ERROR] Failed to set parameter {param}: {e}")
            return False

    def get_parameter(self, param: str) -> Optional[float]:
        """Get a Voicemeeter parameter

        Args:
            param: Parameter name (e.g., "Strip[0].Mute")

        Returns:
            Parameter value or None if failed
        """
        if not self.logged_in or not self.get_parameter_float:
            return None

        try:
            # Removed the blocking loop on is_parameters_dirty.
            # Direct parameter retrieval is usually sufficient and faster.
            # If sync issues arise, this might be a place to re-evaluate.
            
            param_bytes = param.encode('ascii')
            value = ctypes.c_float()
            result = self.get_parameter_float(param_bytes, ctypes.byref(value))

            if result == 0:
                return value.value
            else:
                return None

        except Exception as e:
            print(f"[ERROR] Failed to get parameter {param}: {e}")
            return None

    def is_available(self) -> bool:
        """Check if Voicemeeter API is available"""
        return self.dll is not None and self.logged_in


class VoicemeeterConfig:
    """Voicemeeter Potato strip/output configuration"""

    # Hardware Inputs (Stereo)
    MIC_STRIP = 0           # Strip 0: Microphone
    UNUSED_STRIPS = [1, 2, 3, 4]  # Strips 1-4: Unused hardware inputs

    # Virtual Inputs
    MAIN_STRIP = 5          # Strip 5: Main desktop audio
    MUSIC_STRIP = 6         # Strip 6: Music player
    COMM_STRIP = 7          # Strip 7: Communications (Discord)

    # Hardware Outputs
    OUTPUT_A1 = "A1"        # Speakers
    OUTPUT_A2 = "A2"        # Wired headset
    OUTPUT_A3 = "A3"        # Wireless headset


class VoicemeeterController:
    """High-level Voicemeeter control interface"""

    def __init__(self):
        self.api = VoicemeeterAPI()
        self.config = VoicemeeterConfig()

    def connect(self) -> bool:
        """Connect to Voicemeeter"""
        return self.api.connect()

    def disconnect(self):
        """Disconnect from Voicemeeter"""
        self.api.disconnect()

    def is_available(self) -> bool:
        """Check if Voicemeeter is available"""
        return self.api.is_available()

    # ========================================================================
    # MICROPHONE CONTROL
    # ========================================================================

    def get_mic_mute(self) -> bool:
        """Get microphone mute state"""
        value = self.api.get_parameter(f"Strip[{self.config.MIC_STRIP}].Mute")
        return bool(value) if value is not None else False

    def set_mic_mute(self, muted: bool):
        """Set microphone mute state"""
        self.api.set_parameter(f"Strip[{self.config.MIC_STRIP}].Mute", 1.0 if muted else 0.0)

    def toggle_mic_mute(self):
        """Toggle microphone mute"""
        self.set_mic_mute(not self.get_mic_mute())

    # ========================================================================
    # STRIP GAIN CONTROL
    # ========================================================================

    def get_strip_gain(self, strip: int) -> float:
        """Get strip gain in dB"""
        value = self.api.get_parameter(f"Strip[{strip}].Gain")
        return value if value is not None else 0.0

    def set_strip_gain(self, strip: int, gain_db: float):
        """Set strip gain in dB (clamped to -60 to +12 dB)"""
        # Clamp to valid range
        clamped = max(-60.0, min(12.0, gain_db))
        self.api.set_parameter(f"Strip[{strip}].Gain", clamped)

    def adjust_strip_gain(self, strip: int, delta_db: float):
        """Adjust strip gain by delta (clamped to -60 to +12 dB)"""
        current = self.get_strip_gain(strip)
        new_gain = current + delta_db
        # Clamp to valid range
        clamped = max(-60.0, min(12.0, new_gain))
        self.set_strip_gain(strip, clamped)

    # ========================================================================
    # ROUTING CONTROL
    # ========================================================================

    def get_routing(self, strip: int, output: str) -> bool:
        """Get strip routing to output (A1/A2/A3)"""
        value = self.api.get_parameter(f"Strip[{strip}].{output}")
        if value is None:
            return False
        # Voicemeeter returns 0.0 or 1.0
        return value > 0.5

    def set_routing(self, strip: int, output: str, enabled: bool):
        """Set strip routing to output"""
        self.api.set_parameter(f"Strip[{strip}].{output}", 1.0 if enabled else 0.0)

    def toggle_routing(self, strip: int, output: str):
        """Toggle strip routing to output"""
        current = self.get_routing(strip, output)
        self.set_routing(strip, output, not current)
        time.sleep(0.02)  # Small delay for parameter to propagate


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("Testing Voicemeeter API...")

    vm = VoicemeeterController()

    if vm.connect():
        print("\nVoicemeeter Status:")
        print(f"  Mic Mute: {vm.get_mic_mute()}")
        print(f"  Main Gain: {vm.get_strip_gain(vm.config.MAIN_STRIP):.1f} dB")
        print(f"  Music Gain: {vm.get_strip_gain(vm.config.MUSIC_STRIP):.1f} dB")
        print(f"  Comm Gain: {vm.get_strip_gain(vm.config.COMM_STRIP):.1f} dB")

        print("\nMain Audio Routing:")
        print(f"  A1 (Speakers): {vm.get_routing(vm.config.MAIN_STRIP, 'A1')}")
        print(f"  A2 (Wired): {vm.get_routing(vm.config.MAIN_STRIP, 'A2')}")
        print(f"  A3 (Wireless): {vm.get_routing(vm.config.MAIN_STRIP, 'A3')}")

        vm.disconnect()
    else:
        print("[ERROR] Failed to connect to Voicemeeter")
