;============================================================
; VoiceMeeter Potato Control for Logitech G910
; Uses G HUB to map G-keys to keyboard shortcuts
;
; This script uses the Voicemeeter Remote API.
; Requests are structured like: Strip(0).mute=1; Bus(0).gain +=3.0;
; Here we emulate them by calling our helper functions with parameter names 
; that use the proper parentheses syntax.
;============================================================

#NoEnv
#SingleInstance Force
SetWorkingDir %A_ScriptDir%
SendMode Input

;============================================================
; Initialization - VoiceMeeter Remote API Setup
;============================================================

global VoicemeeterType := 2   ; (0=Standard, 1=Banana, 2=Potato)
global VoicemeeterPath := "C:\Program Files (x86)\VB\Voicemeeter"

global hModule := DllCall("LoadLibrary", "Str", VoicemeeterPath . "\VoicemeeterRemote64.dll", "Ptr")
if (hModule = 0) {
    MsgBox, 16, Error, Could not load VoicemeeterRemote64.dll. Please check your VoiceMeeter installation.
    ExitApp
}

global VBVMR_Login              := DllCall("GetProcAddress", "Ptr", hModule, "AStr", "VBVMR_Login", "Ptr")
global VBVMR_Logout             := DllCall("GetProcAddress", "Ptr", hModule, "AStr", "VBVMR_Logout", "Ptr")
global VBVMR_RunVoicemeeter     := DllCall("GetProcAddress", "Ptr", hModule, "AStr", "VBVMR_RunVoicemeeter", "Ptr")
global VBVMR_SetParameterFloat  := DllCall("GetProcAddress", "Ptr", hModule, "AStr", "VBVMR_SetParameterFloat", "Ptr")
global VBVMR_GetParameterFloat  := DllCall("GetProcAddress", "Ptr", hModule, "AStr", "VBVMR_GetParameterFloat", "Ptr")
global VBVMR_IsParametersDirty  := DllCall("GetProcAddress", "Ptr", hModule, "AStr", "VBVMR_IsParametersDirty", "Ptr")

result := DllCall(VBVMR_Login, "Int")
if (result < 0) {
    MsgBox, 16, Error, Could not connect to VoiceMeeter. Error code: %result%
    ExitApp
}
DllCall(VBVMR_RunVoicemeeter, "Int", VoicemeeterType)
Sleep, 2000

;------------------------------------------------------------
; Global Configuration
;------------------------------------------------------------
global PrimaryMicStrip := 0      ; Adjust to match your mic input strip index
global MasterGainStep := 3.0       ; dB step for volume changes
global G7PreviousState := false

; Define the multichannel virtual inputs as strips 5–7 (for Potato)
global VirtualInputs := [5, 6, 7]

; Hardware stereo inputs (corrected to inputs 2 through 4)
global StereoInputs := [2, 3, 4]

TrayTip, VoiceMeeter Control, Script is now running. Use Ctrl+Shift+F13–F21 (configured in G HUB), 2

;============================================================
; VoiceMeeter API Helper Functions
;============================================================

; Emulate a Voicemeeter Remote request by setting a float parameter.
; For example, this call simulates: Strip(0).mute=1;
SetVMParam(param, value) {
    return DllCall(VBVMR_SetParameterFloat, "AStr", param, "Float", value, "Int")
}

; Reads a parameter value (e.g. “Strip(5).A1”) after ensuring parameters aren’t “dirty.”
GetVMParam(param) {
    Loop {
        pDirty := DllCall(VBVMR_IsParametersDirty, "Int")
        if (pDirty = 0)
            break
        else if (pDirty < 0)
            return 0
        Sleep, 20
        if (A_Index > 50)
            return 0
    }
    VarSetCapacity(fValue, 4, 0)
    NumPut(0.0, fValue, 0, "Float")
    result := DllCall(VBVMR_GetParameterFloat, "AStr", param, "Ptr", &fValue, "Int")
    value := NumGet(fValue, 0, "Float")
    if (result < 0)
        return 0
    return value
}

;============================================================
; Key Bindings for G-Keys (via Ctrl+Shift+F13–F21)
;============================================================

; Mute/Unmute Primary Mic (G1 Key)
^+F13::
currentState := GetVMParam("Strip(" . PrimaryMicStrip . ").mute")
SetVMParam("Strip(" . PrimaryMicStrip . ").mute", !currentState)
return

; Increase Master Volume (G2 Key)
^+F14::
currentGain := GetVMParam("Bus(0).gain")
SetVMParam("Bus(0).gain", currentGain + MasterGainStep)
return

; Decrease Master Volume (G3 Key)
^+F15::
currentGain := GetVMParam("Bus(0).gain")
SetVMParam("Bus(0).gain", currentGain - MasterGainStep)
return

; Toggle A1 Output for Virtual Inputs (G4 Key)
^+F16::
for index, strip in VirtualInputs
{
    currentState := GetVMParam("Strip(" . strip . ").A1")
    SetVMParam("Strip(" . strip . ").A1", !currentState)
}
return

; Toggle A1 Output for Stereo Inputs (G5 Key)
^+F17::
for index, strip in StereoInputs
{
    currentState := GetVMParam("Strip(" . strip . ").A1")
    SetVMParam("Strip(" . strip . ").A1", !currentState)
}
return

; Toggle B1 Output (G6 Key)
^+F18::
currentState := GetVMParam("Bus(0).B1")
SetVMParam("Bus(0).B1", !currentState)
return

;============================================================
; Cleanup and Exit
;============================================================

OnExit("Cleanup")
Cleanup() {
    DllCall(VBVMR_Logout, "Int")
    DllCall("FreeLibrary", "Ptr", hModule)
}
