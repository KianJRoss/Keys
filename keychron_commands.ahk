; Keychron V1 Command Macro Handler with Volume Mode (AutoHotkey v2)
; Maps firmware hotkeys to OS commands
;
; USAGE: Double-click this script to run, or add to Windows startup
; Right-click system tray icon → Exit to stop

#Requires AutoHotkey v2.0
#SingleInstance Force

; ============================================================================
; CONFIGURATION
; ============================================================================

; Configuration constants
global CONFIG := {
    DOUBLE_CLICK_MS: 300,           ; Double-click detection threshold
    MENU_TIMEOUT_MS: 5000,          ; Auto-exit menu mode after this duration
    VOLUME_STEP: 2,                 ; Volume increment/decrement percentage
    WINDOW_TITLE_MAX_LEN: 22,       ; Maximum characters for window titles in display
    NOTIFICATION_DURATION: 1500,    ; Default notification display time
    COMMAND_EXECUTE_DURATION: 2000, ; Notification duration for command execution
    ERROR_DURATION: 3000,           ; Error notification duration

    ; GUI display settings
    GUI_BG_COLOR: "0x1E1E1E",       ; Dark background
    GUI_TEXT_COLOR: "Gray",         ; Inactive option text color
    GUI_ACTIVE_COLOR: "Yellow",     ; Active/selected option color
    GUI_HINT_COLOR: "808080",       ; Exit hint text color
    GUI_FONT: "Segoe UI",           ; Font family
    GUI_FONT_SIZE: 10               ; Font size
}

; Application state (consolidated from scattered globals)
global AppState := {
    currentCommand: 0,      ; Currently selected command (0-3)
    previousCommand: 0,     ; Previous command selection
    menuMode: "",          ; Active menu: "" = normal, "volume", "media", "window_menu", "window_cycle", "window_snap"
    menuModeTimer: 0,      ; Timer reference for auto-exit
    lastClickTime: 0,      ; Timestamp of last click for double-click detection
    clickCount: 0,         ; Click counter for double-click detection
    clickTimer: 0,         ; Timer reference for click processing
    isPressed: false,      ; Guard against repeated key events
    submenuIndex: 0,       ; Current submenu selection index
    windowList: [],        ; Cached window list for cycling
    lastRotation: 0,       ; Last rotation value for direction detection in menus
    routingSelection: 0    ; For routing modes: 0=A1, 1=A2, 2=A3
}

; Menu display GUIs (replaces unreliable tooltips)
; Using 4 separate GUIs to maintain spatial "wheel" layout around cursor
global menuGui_left := 0
global menuGui_center := 0
global menuGui_right := 0
global menuGui_hint := 0

; Notification GUI (replaces tooltip notifications)
global notificationGui := 0

; ============================================================================
; VOICEMEETER API INITIALIZATION
; ============================================================================

global VoicemeeterType := 2   ; (0=Standard, 1=Banana, 2=Potato)
global VoicemeeterPath := "C:\Program Files (x86)\VB\Voicemeeter"
global VoicemeeterEnabled := false
global hModule := 0
global VBVMR_Login := 0
global VBVMR_Logout := 0
global VBVMR_RunVoicemeeter := 0
global VBVMR_SetParameterFloat := 0
global VBVMR_GetParameterFloat := 0
global VBVMR_IsParametersDirty := 0

; Try to load Voicemeeter DLL
try {
    hModule := DllCall("LoadLibrary", "Str", VoicemeeterPath . "\VoicemeeterRemote64.dll", "Ptr")
    if (hModule != 0) {
        VBVMR_Login := DllCall("GetProcAddress", "Ptr", hModule, "AStr", "VBVMR_Login", "Ptr")
        VBVMR_Logout := DllCall("GetProcAddress", "Ptr", hModule, "AStr", "VBVMR_Logout", "Ptr")
        VBVMR_RunVoicemeeter := DllCall("GetProcAddress", "Ptr", hModule, "AStr", "VBVMR_RunVoicemeeter", "Ptr")
        VBVMR_SetParameterFloat := DllCall("GetProcAddress", "Ptr", hModule, "AStr", "VBVMR_SetParameterFloat", "Ptr")
        VBVMR_GetParameterFloat := DllCall("GetProcAddress", "Ptr", hModule, "AStr", "VBVMR_GetParameterFloat", "Ptr")
        VBVMR_IsParametersDirty := DllCall("GetProcAddress", "Ptr", hModule, "AStr", "VBVMR_IsParametersDirty", "Ptr")

        result := DllCall(VBVMR_Login, "Int")
        if (result >= 0) {
            DllCall(VBVMR_RunVoicemeeter, "Int", VoicemeeterType)
            Sleep 1000
            VoicemeeterEnabled := true

            ; Configure microphone routing: Mic (Strip 0) → B1 (virtual output for recording)
            Sleep 500  ; Wait for Voicemeeter to be ready
            SetVMParam("Strip(0).B1", 1)  ; Enable mic routing to first virtual output
        }
    }
} catch {
    VoicemeeterEnabled := false
}

; Voicemeeter configuration (Potato)
; Hardware Inputs (Stereo)
global MicrophoneStrip := 0         ; Strip 0: Microphone
global StereoInputs := [1, 2, 3, 4] ; Strips 1-4: Unused hardware inputs

; Virtual Inputs
global MainAudioStrip := 5          ; Strip 5: Main desktop audio
global MusicAudioStrip := 6         ; Strip 6: Music
global CommAudioStrip := 7          ; Strip 7: Communications (Discord)
global VirtualInputs := [5, 6, 7]   ; All virtual inputs

; Hardware Outputs
global SpeakersOutput := "A1"       ; A1: Main speakers
global HeadsetOutput := "A2"        ; A2: Main wired headset
global WirelessOutput := "A3"       ; A3: Wireless headset

; Volume settings
global MasterGainStep := 3.0        ; dB step for volume changes

; Legacy aliases for backward compatibility (will be removed after refactoring)
global currentCommand := 0
global previousCommand := 0
global menuMode := ""
global menuModeTimer := 0
global lastClickTime := 0
global clickCount := 0
global clickTimer := 0
global isPressed := false
global submenuIndex := 0
global windowList := []
global lastRotation := 0
global routingSelection := 0

; Command definitions (EDIT THESE to customize your commands)
commands := [
    {
        name: "Voicemeeter Control",
        action: () => EnterVoicemeeterMenuMode()
    },
    {
        name: "Media Controls",
        action: () => EnterMediaMode()
    },
    {
        name: "Window Manager",
        action: () => EnterWindowMenuMode()
    },
    {
        name: "Launch Playnite",
        action: () => LaunchPlaynite()
    }
]

; Window Manager submenus
windowSubmenus := [
    {
        name: "Window Cycle",
        action: () => EnterWindowCycleMode()
    },
    {
        name: "Window Snap",
        action: () => EnterWindowSnapMode()
    },
    {
        name: "Show Desktop",
        action: () => Send("#d")
    }
]

; Voicemeeter submenus
voicemeeterSubmenus := [
    {
        name: "System Volume + Mic",
        action: () => EnterVoicemeeterSystemMode()
    },
    {
        name: "Main Routing",
        action: () => EnterMainRoutingMode()
    },
    {
        name: "Music Gain",
        action: () => EnterMusicGainMode()
    },
    {
        name: "Music Routing",
        action: () => EnterMusicRoutingMode()
    },
    {
        name: "Comm Gain",
        action: () => EnterCommGainMode()
    },
    {
        name: "Comm Routing",
        action: () => EnterCommRoutingMode()
    }
]

; ============================================================================
; HOTKEY HANDLERS
; ============================================================================

; Unified handler for command key selection
HandleCommandKey(index) {
    global currentCommand, previousCommand, menuMode, lastRotation

    if (menuMode != "") {
        ; Menu mode: Use for rotation, track sequence for direction
        HandleMenuRotation(lastRotation, index)
        lastRotation := index
    } else {
        ; Normal mode: Update command selection
        previousCommand := currentCommand
        currentCommand := index
        ShowNotification(commands[index + 1].name)
        TriggerTrayUpdate()  ; Update tray menu
    }
}

; Determine rotation direction based on command sequence
IsRotatingUp(prev, curr) {
    ; Normal increment: 0→1, 1→2, 2→3
    if (curr == prev + 1)
        return true
    ; Wrap around: 3→0
    if (prev == 3 && curr == 0)
        return true
    return false
}

; Ctrl+Alt+F13 → Command 0 selected
^!F13:: HandleCommandKey(0)

; Ctrl+Alt+F14 → Command 1 selected
^!F14:: HandleCommandKey(1)

; Ctrl+Alt+F15 → Command 2 selected
^!F15:: HandleCommandKey(2)

; Ctrl+Alt+F16 → Command 3 selected
^!F16:: HandleCommandKey(3)

; Ctrl+Alt+Enter → Execute current command OR Handle menu mode clicks
^!Enter:: {
    global menuMode, lastClickTime, isPressed, clickCount, clickTimer

    if (menuMode != "") {
        ; Menu mode: Count clicks
        currentTime := A_TickCount
        timeSinceLastClick := currentTime - lastClickTime

        if (timeSinceLastClick < CONFIG.DOUBLE_CLICK_MS) {
            ; Click came within threshold - increment count
            clickCount++

            if (clickCount >= 2) {
                ; Double-click confirmed - exit immediately
                SetTimer(ProcessClick, 0)  ; Cancel any pending timer
                clickCount := 0
                ExitMenuMode()
            }
        } else {
            ; New click sequence - reset count
            clickCount := 1

            ; Set timer to process single click if no second click arrives
            SetTimer(ProcessClick, -CONFIG.DOUBLE_CLICK_MS)
        }

        lastClickTime := currentTime
        ResetMenuTimer()
    } else {
        ; Normal mode: Execute command (with guard)
        if (isPressed)
            return
        isPressed := true
        ExecuteCommand()
    }
}

; Ctrl+Alt+Enter release → Reset guard flag
^!Enter up:: {
    global isPressed
    isPressed := false
}

; Process single click after delay
ProcessClick() {
    global menuMode, submenuIndex, windowSubmenus, windowList, clickCount

    ; Reset click count
    clickCount := 0

    ; Only execute if still in menu mode
    if (menuMode == "")
        return

    ; Route to appropriate handler based on menu type
    if (menuMode == "voicemeeter_system") {
        ; Toggle mic mute on microphone strip
        currentState := GetVMParam("Strip(" MicrophoneStrip ").mute")
        SetVMParam("Strip(" MicrophoneStrip ").mute", !currentState)
        ShowMenuDisplay()
        ResetMenuTimer()
    } else if (menuMode == "music_gain") {
        ; Reset Music gain to 0 dB
        SetVMParam("Strip(" MusicAudioStrip ").gain", 0.0)
        ShowMenuDisplay()
        ResetMenuTimer()
    } else if (menuMode == "main_routing") {
        ; Toggle currently selected output for Main
        outputs := ["A1", "A2", "A3"]
        outputParam := "Strip(" MainAudioStrip ")." outputs[routingSelection + 1]
        currentState := GetVMParam(outputParam)
        SetVMParam(outputParam, !currentState)
        Sleep 50  ; Wait for Voicemeeter to update
        ShowMenuDisplay()
        ResetMenuTimer()
    } else if (menuMode == "music_routing") {
        ; Toggle currently selected output for Music
        outputs := ["A1", "A2", "A3"]
        outputParam := "Strip(" MusicAudioStrip ")." outputs[routingSelection + 1]
        currentState := GetVMParam(outputParam)
        SetVMParam(outputParam, !currentState)
        Sleep 50  ; Wait for Voicemeeter to update
        ShowMenuDisplay()
        ResetMenuTimer()
    } else if (menuMode == "comm_gain") {
        ; Reset Comm gain to 0 dB
        SetVMParam("Strip(" CommAudioStrip ").gain", 0.0)
        ShowMenuDisplay()
        ResetMenuTimer()
    } else if (menuMode == "comm_routing") {
        ; Toggle currently selected output for Comm
        outputs := ["A1", "A2", "A3"]
        outputParam := "Strip(" CommAudioStrip ")." outputs[routingSelection + 1]
        currentState := GetVMParam(outputParam)
        SetVMParam(outputParam, !currentState)
        Sleep 50  ; Wait for Voicemeeter to update
        ShowMenuDisplay()
        ResetMenuTimer()
    } else if (menuMode == "voicemeeter_menu") {
        ; Execute selected submenu
        submenu := voicemeeterSubmenus[submenuIndex + 1]
        submenu.action.Call()
    } else if (menuMode == "volume") {
        ; Toggle mute (system fallback)
        SoundSetMute(!SoundGetMute())
        ShowMenuDisplay()
        ResetMenuTimer()
    } else if (menuMode == "media") {
        ; Play/Pause
        Send("{Media_Play_Pause}")
        ShowMenuDisplay()
        ResetMenuTimer()
    } else if (menuMode == "window_menu") {
        ; Execute selected submenu
        submenu := windowSubmenus[submenuIndex + 1]
        submenu.action.Call()
        ; Don't exit - submenu action might enter another mode
    } else if (menuMode == "window_cycle") {
        ; Switch to selected window
        if (windowList.Length > 0) {
            try {
                hwnd := windowList[submenuIndex + 1]
                ; Restore if minimized first
                if (WinGetMinMax("ahk_id " hwnd) == -1) {
                    WinRestore("ahk_id " hwnd)
                }
                ; Activate window
                WinActivate("ahk_id " hwnd)
                ; Wait for activation
                WinWaitActive("ahk_id " hwnd,, 1)
                ExitMenuMode()
            } catch as err {
                ShowNotification("Error: " err.Message, 2000)
                ShowMenuDisplay()
                ResetMenuTimer()
            }
        }
    } else if (menuMode == "window_snap") {
        ; Snap window based on selection
        if (submenuIndex == 0) {
            ; Snap left
            Send("#{Left}")
        } else if (submenuIndex == 1) {
            ; Snap right
            Send("#{Right}")
        } else if (submenuIndex == 2) {
            ; Maximize
            Send("#{Up}")
        }
        ; Exit after snapping
        ExitMenuMode()
    }
}

; Handle rotation in menu mode
HandleMenuRotation(prev, curr) {
    global menuMode, submenuIndex, windowSubmenus, windowList, routingSelection

    isUp := IsRotatingUp(prev, curr)

    if (menuMode == "voicemeeter_system") {
        ; Windows system volume control
        if (isUp) {
            SoundSetVolume("+" CONFIG.VOLUME_STEP)
        } else {
            SoundSetVolume("-" CONFIG.VOLUME_STEP)
        }
    } else if (menuMode == "music_gain") {
        ; Music strip gain control
        currentGain := GetVMParam("Strip(" MusicAudioStrip ").gain")
        if (isUp) {
            SetVMParam("Strip(" MusicAudioStrip ").gain", currentGain + MasterGainStep)
        } else {
            SetVMParam("Strip(" MusicAudioStrip ").gain", currentGain - MasterGainStep)
        }
    } else if (menuMode == "main_routing") {
        ; Rotate through outputs: A1 → A2 → A3 → A1
        if (isUp) {
            routingSelection := Mod(routingSelection + 1, 3)
        } else {
            routingSelection := Mod(routingSelection - 1 + 3, 3)
        }
        Sleep 30  ; Brief delay for smooth display update
    } else if (menuMode == "music_routing") {
        ; Rotate through outputs: A1 → A2 → A3 → A1
        if (isUp) {
            routingSelection := Mod(routingSelection + 1, 3)
        } else {
            routingSelection := Mod(routingSelection - 1 + 3, 3)
        }
        Sleep 30  ; Brief delay for smooth display update
    } else if (menuMode == "comm_gain") {
        ; Comm strip gain control
        currentGain := GetVMParam("Strip(" CommAudioStrip ").gain")
        if (isUp) {
            SetVMParam("Strip(" CommAudioStrip ").gain", currentGain + MasterGainStep)
        } else {
            SetVMParam("Strip(" CommAudioStrip ").gain", currentGain - MasterGainStep)
        }
    } else if (menuMode == "comm_routing") {
        ; Rotate through outputs: A1 → A2 → A3 → A1
        if (isUp) {
            routingSelection := Mod(routingSelection + 1, 3)
        } else {
            routingSelection := Mod(routingSelection - 1 + 3, 3)
        }
        Sleep 30  ; Brief delay for smooth display update
    } else if (menuMode == "voicemeeter_menu") {
        ; Voicemeeter submenu selection
        if (isUp) {
            submenuIndex := Mod(submenuIndex + 1, voicemeeterSubmenus.Length)
        } else {
            submenuIndex := Mod(submenuIndex - 1 + voicemeeterSubmenus.Length, voicemeeterSubmenus.Length)
        }
    } else if (menuMode == "volume") {
        ; System volume control (fallback)
        if (isUp) {
            SoundSetVolume("+" CONFIG.VOLUME_STEP)
        } else {
            SoundSetVolume("-" CONFIG.VOLUME_STEP)
        }
    } else if (menuMode == "media") {
        ; Media control
        if (isUp) {
            Send("{Media_Next}")
        } else {
            Send("{Media_Prev}")
        }
    } else if (menuMode == "window_menu") {
        ; Window submenu selection
        if (isUp) {
            submenuIndex := Mod(submenuIndex + 1, windowSubmenus.Length)
        } else {
            submenuIndex := Mod(submenuIndex - 1 + windowSubmenus.Length, windowSubmenus.Length)
        }
    } else if (menuMode == "window_cycle") {
        ; Cycle through window list
        if (windowList.Length > 0) {
            if (isUp) {
                submenuIndex := Mod(submenuIndex + 1, windowList.Length)
            } else {
                submenuIndex := Mod(submenuIndex - 1 + windowList.Length, windowList.Length)
            }
        }
    } else if (menuMode == "window_snap") {
        ; Snap window to different positions
        if (isUp) {
            ; Cycle through: Left, Right, Maximize
            submenuIndex := Mod(submenuIndex + 1, 3)
        } else {
            submenuIndex := Mod(submenuIndex - 1 + 3, 3)
        }
    }

    ShowMenuDisplay()
    ResetMenuTimer()
}

; ============================================================================
; MENU MODE FUNCTIONS
; ============================================================================

; Get list of visible application windows
; Returns array of window handles (HWNDs) for visible windows with titles
GetVisibleWindows() {
    windowList := []

    ; Get all windows except Program Manager
    ids := WinGetList(,, "Program Manager")

    for hwnd in ids {
        try {
            ; Check if window exists and is visible
            if !WinExist("ahk_id " hwnd)
                continue

            ; Get window properties
            title := WinGetTitle("ahk_id " hwnd)
            style := WinGetStyle("ahk_id " hwnd)
            exStyle := WinGetExStyle("ahk_id " hwnd)

            ; Filter criteria:
            ; - Must have a title
            ; - Must have WS_VISIBLE (0x10000000)
            ; - Must not be a tool window (WS_EX_TOOLWINDOW = 0x80)
            ; - Should be a normal window (WS_EX_APPWINDOW = 0x40000 OR not WS_EX_TOOLWINDOW)

            hasTitle := (title != "")
            isVisible := (style & 0x10000000)
            isToolWindow := (exStyle & 0x80)
            isAppWindow := (exStyle & 0x40000)

            ; Include if: has title, visible, and either AppWindow or not a ToolWindow
            if (hasTitle && isVisible && (isAppWindow || !isToolWindow)) {
                windowList.Push(hwnd)
            }
        } catch {
            ; Skip windows that cause errors
            continue
        }
    }

    return windowList
}

; Enter Voicemeeter menu mode (submenu selector)
EnterVoicemeeterMenuMode() {
    global menuMode, submenuIndex, clickCount, lastRotation, VoicemeeterEnabled

    if (!VoicemeeterEnabled) {
        ShowNotification("Voicemeeter not available", 2000)
        return
    }

    clickCount := 0
    lastRotation := 0
    menuMode := "voicemeeter_menu"
    submenuIndex := 0  ; Start at first submenu
    TriggerTrayUpdate()
    ShowMenuDisplay()
    ResetMenuTimer()
}

; Enter Voicemeeter system volume + mic mode
EnterVoicemeeterSystemMode() {
    global menuMode, clickCount, lastRotation
    clickCount := 0
    lastRotation := 0
    menuMode := "voicemeeter_system"
    TriggerTrayUpdate()
    ShowMenuDisplay()
    ResetMenuTimer()
}

; Enter Main routing control mode
EnterMainRoutingMode() {
    global menuMode, clickCount, lastRotation, routingSelection
    clickCount := 0
    lastRotation := 0
    routingSelection := 0  ; Start at A1 (speakers)
    menuMode := "main_routing"
    TriggerTrayUpdate()
    ShowMenuDisplay()
    ResetMenuTimer()
}

; Enter Music gain control mode
EnterMusicGainMode() {
    global menuMode, clickCount, lastRotation
    clickCount := 0
    lastRotation := 0
    menuMode := "music_gain"
    TriggerTrayUpdate()
    ShowMenuDisplay()
    ResetMenuTimer()
}

; Enter Music routing control mode
EnterMusicRoutingMode() {
    global menuMode, clickCount, lastRotation, routingSelection
    clickCount := 0
    lastRotation := 0
    routingSelection := 0  ; Start at A1 (speakers)
    menuMode := "music_routing"
    TriggerTrayUpdate()
    ShowMenuDisplay()
    ResetMenuTimer()
}

; Enter Comm gain control mode
EnterCommGainMode() {
    global menuMode, clickCount, lastRotation
    clickCount := 0
    lastRotation := 0
    menuMode := "comm_gain"
    TriggerTrayUpdate()
    ShowMenuDisplay()
    ResetMenuTimer()
}

; Enter Comm routing control mode
EnterCommRoutingMode() {
    global menuMode, clickCount, lastRotation, routingSelection
    clickCount := 0
    lastRotation := 0
    routingSelection := 0  ; Start at A1 (speakers)
    menuMode := "comm_routing"
    TriggerTrayUpdate()
    ShowMenuDisplay()
    ResetMenuTimer()
}

; Launch Playnite in fullscreen on second monitor
LaunchPlaynite() {
    try {
        ; Launch Playnite in fullscreen mode
        Run("playnite://playnite/fullscreen")
        ShowNotification("Launching Playnite Fullscreen", 1500)
    } catch as err {
        ShowNotification("Error launching Playnite: " err.Message, 3000)
    }
}

; Enter media control mode
EnterMediaMode() {
    global menuMode, clickCount, lastRotation
    clickCount := 0
    lastRotation := 0
    menuMode := "media"
    TriggerTrayUpdate()
    ShowMenuDisplay()
    ResetMenuTimer()
}

; Enter window menu mode (submenu selector)
EnterWindowMenuMode() {
    global menuMode, submenuIndex, clickCount, lastRotation
    clickCount := 0
    lastRotation := 0
    menuMode := "window_menu"
    submenuIndex := 0  ; Start at first submenu
    TriggerTrayUpdate()
    ShowMenuDisplay()
    ResetMenuTimer()
}

; Enter window cycle mode (alt-tab like)
EnterWindowCycleMode() {
    global menuMode, submenuIndex, windowList, clickCount, lastRotation

    clickCount := 0
    lastRotation := 0
    submenuIndex := 0

    ; Build list of visible windows using helper function
    windowList := GetVisibleWindows()

    menuMode := "window_cycle"

    ; Show count for debugging
    if (windowList.Length == 0) {
        ShowNotification("No windows found", 2000)
    } else {
        ShowNotification("Found " windowList.Length " windows", 1000)
    }

    TriggerTrayUpdate()
    ShowMenuDisplay()
    ResetMenuTimer()
}

; Enter window snap mode
EnterWindowSnapMode() {
    global menuMode, submenuIndex, clickCount, lastRotation
    clickCount := 0
    lastRotation := 0
    menuMode := "window_snap"
    submenuIndex := 0  ; Start with "Snap Left"
    TriggerTrayUpdate()
    ShowMenuDisplay()
    ResetMenuTimer()
}

; Exit menu mode
ExitMenuMode() {
    global menuMode, menuModeTimer, clickCount, lastRotation
    global menuGui_left, menuGui_center, menuGui_right, menuGui_hint

    menuMode := ""
    clickCount := 0
    lastRotation := 0

    ; Clear timer
    if (menuModeTimer) {
        SetTimer(menuModeTimer, 0)
        menuModeTimer := 0
    }

    ; Clear any pending click timer
    SetTimer(ProcessClick, 0)

    ; Destroy all menu GUIs
    if (menuGui_left) {
        try menuGui_left.Destroy()
        menuGui_left := 0
    }
    if (menuGui_center) {
        try menuGui_center.Destroy()
        menuGui_center := 0
    }
    if (menuGui_right) {
        try menuGui_right.Destroy()
        menuGui_right := 0
    }
    if (menuGui_hint) {
        try menuGui_hint.Destroy()
        menuGui_hint := 0
    }

    TriggerTrayUpdate()

    ; Show exit notification
    ShowNotification("Returned to Macro Mode", 1500)
}

; Reset the auto-exit timer
ResetMenuTimer() {
    global menuModeTimer

    ; Clear existing timer
    if (menuModeTimer) {
        SetTimer(menuModeTimer, 0)
    }

    ; Set new timer (from CONFIG)
    menuModeTimer := () => ExitMenuMode()
    SetTimer(menuModeTimer, -CONFIG.MENU_TIMEOUT_MS)
}

; ============================================================================
; VOICEMEETER API HELPER FUNCTIONS
; ============================================================================

; Set a Voicemeeter parameter (e.g. "Strip(0).mute", value)
SetVMParam(param, value) {
    global VBVMR_SetParameterFloat, VoicemeeterEnabled
    if (!VoicemeeterEnabled)
        return -1
    return DllCall(VBVMR_SetParameterFloat, "AStr", param, "Float", value, "Int")
}

; Get a Voicemeeter parameter value
GetVMParam(param) {
    global VBVMR_GetParameterFloat, VBVMR_IsParametersDirty, VoicemeeterEnabled
    if (!VoicemeeterEnabled)
        return 0

    ; Wait for parameters to not be dirty
    Loop {
        pDirty := DllCall(VBVMR_IsParametersDirty, "Int")
        if (pDirty == 0)
            break
        else if (pDirty < 0)
            return 0
        Sleep 20
        if (A_Index > 50)
            return 0
    }

    ; AutoHotkey v2: Use Buffer instead of VarSetCapacity
    fValue := Buffer(4, 0)
    result := DllCall(VBVMR_GetParameterFloat, "AStr", param, "Ptr", fValue.Ptr, "Int")
    value := NumGet(fValue, 0, "Float")
    if (result < 0)
        return 0
    return value
}

; ============================================================================
; COMMAND EXECUTION
; ============================================================================

; Execute the currently selected command
ExecuteCommand() {
    global currentCommand, menuMode

    ; Exit menu mode if still active (fixes persistence bug)
    if (menuMode != "") {
        ExitMenuMode()
        Sleep 50  ; Brief delay to ensure cleanup
    }

    try {
        cmd := commands[currentCommand + 1]
        cmd.action.Call()
        ShowNotification("Executed: " cmd.name, 2000)
    } catch Error as err {
        ShowNotification("Error: " err.Message, 3000)
    }
}

; Show dark GUI notification
ShowNotification(message, duration := 1500) {
    global notificationGui

    ; Destroy existing notification if present
    if (notificationGui) {
        try notificationGui.Destroy()
    }

    ; Create notification GUI
    notificationGui := Gui("+AlwaysOnTop -Caption +ToolWindow")
    notificationGui.BackColor := CONFIG.GUI_BG_COLOR
    notificationGui.SetFont("s" CONFIG.GUI_FONT_SIZE, CONFIG.GUI_FONT)
    notificationGui.Add("Text", "x10 y8 c" CONFIG.GUI_ACTIVE_COLOR, message)

    ; Get mouse position
    CoordMode("Mouse", "Screen")
    MouseGetPos(&mouseX, &mouseY)

    ; Position near cursor (below and to the right)
    notificationGui.Show("x" (mouseX + 20) " y" (mouseY + 20) " AutoSize NoActivate")

    ; Auto-hide after duration
    SetTimer(() => DestroyNotification(), -duration)
}

; Helper to destroy notification GUI
DestroyNotification() {
    global notificationGui
    if (notificationGui) {
        try notificationGui.Destroy()
        notificationGui := 0
    }
}

; Show visual menu with options (wheel layout around cursor)
ShowMenuDisplay() {
    global menuMode, submenuIndex, windowSubmenus, windowList
    global menuGui_left, menuGui_center, menuGui_right, menuGui_hint

    if (menuMode == "") {
        ; Destroy all GUIs when exiting menu mode
        if (menuGui_left) {
            try menuGui_left.Destroy()
            menuGui_left := 0
        }
        if (menuGui_center) {
            try menuGui_center.Destroy()
            menuGui_center := 0
        }
        if (menuGui_right) {
            try menuGui_right.Destroy()
            menuGui_right := 0
        }
        if (menuGui_hint) {
            try menuGui_hint.Destroy()
            menuGui_hint := 0
        }
        return
    }

    ; Get menu-specific options
    if (menuMode == "voicemeeter_system") {
        currentVol := Round(SoundGetVolume())
        micMuted := GetVMParam("Strip(" MicrophoneStrip ").mute")
        muteStatus := micMuted ? "🎤🔇 MIC MUTED" : "🎤"
        left := "Volume Down"
        center := muteStatus " " currentVol "%"
        right := "Volume Up"
    } else if (menuMode == "music_gain") {
        currentGain := Round(GetVMParam("Strip(" MusicAudioStrip ").gain"))
        left := "Gain Down"
        center := "🎵 Music " currentGain " dB"
        right := "Gain Up"
    } else if (menuMode == "main_routing") {
        ; Main audio routing wheel
        a1State := GetVMParam("Strip(" MainAudioStrip ").A1")
        a2State := GetVMParam("Strip(" MainAudioStrip ").A2")
        a3State := GetVMParam("Strip(" MainAudioStrip ").A3")

        outputNames := ["Speakers", "Wired", "Wireless"]
        outputStates := [a1State, a2State, a3State]
        outputIcons := ["🔊", "🎧", "📡"]

        prevIdx := Mod(routingSelection - 1 + 3, 3)
        nextIdx := Mod(routingSelection + 1, 3)

        leftIcon := outputStates[prevIdx + 1] ? outputIcons[prevIdx + 1] : "⊘"
        centerIcon := outputStates[routingSelection + 1] ? outputIcons[routingSelection + 1] : "⊘"
        rightIcon := outputStates[nextIdx + 1] ? outputIcons[nextIdx + 1] : "⊘"

        left := outputNames[prevIdx + 1] " " leftIcon
        center := outputNames[routingSelection + 1] " " centerIcon
        right := outputNames[nextIdx + 1] " " rightIcon
    } else if (menuMode == "music_routing") {
        ; Music routing wheel
        a1State := GetVMParam("Strip(" MusicAudioStrip ").A1")
        a2State := GetVMParam("Strip(" MusicAudioStrip ").A2")
        a3State := GetVMParam("Strip(" MusicAudioStrip ").A3")

        outputNames := ["Speakers", "Wired", "Wireless"]
        outputStates := [a1State, a2State, a3State]
        outputIcons := ["🔊", "🎧", "📡"]

        prevIdx := Mod(routingSelection - 1 + 3, 3)
        nextIdx := Mod(routingSelection + 1, 3)

        leftIcon := outputStates[prevIdx + 1] ? outputIcons[prevIdx + 1] : "⊘"
        centerIcon := outputStates[routingSelection + 1] ? outputIcons[routingSelection + 1] : "⊘"
        rightIcon := outputStates[nextIdx + 1] ? outputIcons[nextIdx + 1] : "⊘"

        left := outputNames[prevIdx + 1] " " leftIcon
        center := outputNames[routingSelection + 1] " " centerIcon
        right := outputNames[nextIdx + 1] " " rightIcon
    } else if (menuMode == "comm_gain") {
        currentGain := Round(GetVMParam("Strip(" CommAudioStrip ").gain"))
        left := "Gain Down"
        center := "💬 Comm " currentGain " dB"
        right := "Gain Up"
    } else if (menuMode == "comm_routing") {
        ; Comm routing wheel
        a1State := GetVMParam("Strip(" CommAudioStrip ").A1")
        a2State := GetVMParam("Strip(" CommAudioStrip ").A2")
        a3State := GetVMParam("Strip(" CommAudioStrip ").A3")

        outputNames := ["Speakers", "Wired", "Wireless"]
        outputStates := [a1State, a2State, a3State]
        outputIcons := ["🔊", "🎧", "📡"]

        prevIdx := Mod(routingSelection - 1 + 3, 3)
        nextIdx := Mod(routingSelection + 1, 3)

        leftIcon := outputStates[prevIdx + 1] ? outputIcons[prevIdx + 1] : "⊘"
        centerIcon := outputStates[routingSelection + 1] ? outputIcons[routingSelection + 1] : "⊘"
        rightIcon := outputStates[nextIdx + 1] ? outputIcons[nextIdx + 1] : "⊘"

        left := outputNames[prevIdx + 1] " " leftIcon
        center := outputNames[routingSelection + 1] " " centerIcon
        right := outputNames[nextIdx + 1] " " rightIcon
    } else if (menuMode == "voicemeeter_menu") {
        ; Submenu selection
        totalMenus := voicemeeterSubmenus.Length
        prevIdx := Mod(submenuIndex - 1 + totalMenus, totalMenus)
        nextIdx := Mod(submenuIndex + 1, totalMenus)

        left := voicemeeterSubmenus[prevIdx + 1].name
        center := "▶ " voicemeeterSubmenus[submenuIndex + 1].name
        right := voicemeeterSubmenus[nextIdx + 1].name
    } else if (menuMode == "volume") {
        currentVol := Round(SoundGetVolume())
        muteStatus := SoundGetMute() ? "🔇 MUTED" : "🔊"
        left := "Volume Down"
        center := muteStatus " " currentVol "%"
        right := "Volume Up"
    } else if (menuMode == "media") {
        left := "⏮ Previous"
        center := "⏯ Play/Pause"
        right := "⏭ Next"
    } else if (menuMode == "window_menu") {
        ; Submenu selection
        totalMenus := windowSubmenus.Length
        prevIdx := Mod(submenuIndex - 1 + totalMenus, totalMenus)
        nextIdx := Mod(submenuIndex + 1, totalMenus)

        left := windowSubmenus[prevIdx + 1].name
        center := "▶ " windowSubmenus[submenuIndex + 1].name
        right := windowSubmenus[nextIdx + 1].name
    } else if (menuMode == "window_cycle") {
        ; Window cycling
        if (windowList.Length == 0) {
            left := ""
            center := "⚠ No windows found"
            right := ""
        } else if (windowList.Length == 1) {
            ; Only one window
            try {
                currTitle := WinGetTitle("ahk_id " windowList[1])
                left := ""
                center := "▶ " SubStr(currTitle, 1, 25)
                right := ""
            } catch {
                left := ""
                center := "⚠ Error"
                right := ""
            }
        } else {
            ; Multiple windows
            totalWindows := windowList.Length
            prevIdx := Mod(submenuIndex - 1 + totalWindows, totalWindows)
            nextIdx := Mod(submenuIndex + 1, totalWindows)

            try {
                prevTitle := WinGetTitle("ahk_id " windowList[prevIdx + 1])
                currTitle := WinGetTitle("ahk_id " windowList[submenuIndex + 1])
                nextTitle := WinGetTitle("ahk_id " windowList[nextIdx + 1])

                left := SubStr(prevTitle, 1, 22)
                center := "▶ " SubStr(currTitle, 1, 22)
                right := SubStr(nextTitle, 1, 22)
            } catch as err {
                left := ""
                center := "⚠ " err.Message
                right := ""
            }
        }
    } else if (menuMode == "window_snap") {
        ; Snap positions
        snapOptions := ["◧ Snap Left", "◨ Snap Right", "⬜ Maximize"]
        prevIdx := Mod(submenuIndex - 1 + 3, 3)
        nextIdx := Mod(submenuIndex + 1, 3)

        left := snapOptions[prevIdx + 1]
        center := "▶ " snapOptions[submenuIndex + 1]
        right := snapOptions[nextIdx + 1]
    }

    ; Destroy existing GUIs if present
    if (menuGui_left) {
        try menuGui_left.Destroy()
    }
    if (menuGui_center) {
        try menuGui_center.Destroy()
    }
    if (menuGui_right) {
        try menuGui_right.Destroy()
    }
    if (menuGui_hint) {
        try menuGui_hint.Destroy()
    }

    ; Get mouse position for wheel layout
    CoordMode("Mouse", "Screen")
    MouseGetPos(&mouseX, &mouseY)

    ; Create LEFT option GUI (to the left of cursor)
    if (left != "") {
        menuGui_left := Gui("+AlwaysOnTop -Caption +ToolWindow")
        menuGui_left.BackColor := CONFIG.GUI_BG_COLOR
        menuGui_left.SetFont("s" CONFIG.GUI_FONT_SIZE, CONFIG.GUI_FONT)
        menuGui_left.Add("Text", "x5 y5 c" CONFIG.GUI_TEXT_COLOR, left)
        menuGui_left.Show("x" (mouseX - 180) " y" mouseY " AutoSize NoActivate")
    }

    ; Create CENTER option GUI (above cursor) - BOLD
    menuGui_center := Gui("+AlwaysOnTop -Caption +ToolWindow")
    menuGui_center.BackColor := CONFIG.GUI_BG_COLOR
    menuGui_center.SetFont("s" CONFIG.GUI_FONT_SIZE " Bold", CONFIG.GUI_FONT)
    menuGui_center.Add("Text", "x5 y5 c" CONFIG.GUI_ACTIVE_COLOR, center)
    menuGui_center.Show("x" (mouseX - 60) " y" (mouseY - 60) " AutoSize NoActivate")

    ; Create RIGHT option GUI (to the right of cursor)
    if (right != "") {
        menuGui_right := Gui("+AlwaysOnTop -Caption +ToolWindow")
        menuGui_right.BackColor := CONFIG.GUI_BG_COLOR
        menuGui_right.SetFont("s" CONFIG.GUI_FONT_SIZE, CONFIG.GUI_FONT)
        menuGui_right.Add("Text", "x5 y5 c" CONFIG.GUI_TEXT_COLOR, right)
        menuGui_right.Show("x" (mouseX + 60) " y" mouseY " AutoSize NoActivate")
    }

    ; Create HINT GUI (below cursor)
    menuGui_hint := Gui("+AlwaysOnTop -Caption +ToolWindow")
    menuGui_hint.BackColor := CONFIG.GUI_BG_COLOR
    menuGui_hint.SetFont("s" CONFIG.GUI_FONT_SIZE, CONFIG.GUI_FONT)
    menuGui_hint.Add("Text", "x5 y5 c" CONFIG.GUI_HINT_COLOR, "Double-tap: Exit")
    menuGui_hint.Show("x" (mouseX - 40) " y" (mouseY + 40) " AutoSize NoActivate")
}

; ============================================================================
; SYSTEM TRAY
; ============================================================================

; Set custom tray icon text
A_IconTip := "Keychron Command Macro Handler"

; Add tray menu items
A_TrayMenu.Delete()  ; Remove default items
A_TrayMenu.Add("Current Mode: Normal", (*) => "")
A_TrayMenu.Disable("1&")
A_TrayMenu.Add()
A_TrayMenu.Add("Reload Script", (*) => Reload())
A_TrayMenu.Add("Exit", (*) => ExitApp())

; Update tray menu based on mode
UpdateTrayMenu() {
    global menuMode, currentCommand

    if (menuMode == "voicemeeter_menu") {
        A_TrayMenu.Rename("1&", "Current Mode: 🎛️ Voicemeeter Menu")
    } else if (menuMode == "voicemeeter_system") {
        A_TrayMenu.Rename("1&", "Current Mode: 🔊 System Volume + Mic")
    } else if (menuMode == "main_routing") {
        A_TrayMenu.Rename("1&", "Current Mode: 🔊 Main Routing")
    } else if (menuMode == "music_gain") {
        A_TrayMenu.Rename("1&", "Current Mode: 🎵 Music Gain")
    } else if (menuMode == "music_routing") {
        A_TrayMenu.Rename("1&", "Current Mode: 🎵 Music Routing")
    } else if (menuMode == "comm_gain") {
        A_TrayMenu.Rename("1&", "Current Mode: 💬 Comm Gain")
    } else if (menuMode == "comm_routing") {
        A_TrayMenu.Rename("1&", "Current Mode: 💬 Comm Routing")
    } else if (menuMode == "volume") {
        A_TrayMenu.Rename("1&", "Current Mode: 🔊 Volume Control")
    } else if (menuMode == "media") {
        A_TrayMenu.Rename("1&", "Current Mode: 🎵 Media Control")
    } else if (menuMode == "window_menu") {
        A_TrayMenu.Rename("1&", "Current Mode: 🪟 Window Menu")
    } else if (menuMode == "window_cycle") {
        A_TrayMenu.Rename("1&", "Current Mode: 🔄 Window Cycle")
    } else if (menuMode == "window_snap") {
        A_TrayMenu.Rename("1&", "Current Mode: 📐 Window Snap")
    } else {
        A_TrayMenu.Rename("1&", "Current Mode: " commands[currentCommand + 1].name)
    }
}

; Trigger tray update (event-driven replacement for polling)
TriggerTrayUpdate() {
    UpdateTrayMenu()
}

; ============================================================================
; CLEANUP ON EXIT
; ============================================================================

OnExit(CleanupVoicemeeter)

CleanupVoicemeeter(*) {
    global hModule, VBVMR_Logout, VoicemeeterEnabled
    if (VoicemeeterEnabled && hModule != 0) {
        try {
            DllCall(VBVMR_Logout, "Int")
            DllCall("FreeLibrary", "Ptr", hModule)
        }
    }
}

; Show startup notification
if (VoicemeeterEnabled) {
    ShowNotification("Keychron + Voicemeeter Active", 2000)
} else {
    ShowNotification("Keychron Active (Voicemeeter disabled)", 2000)
}
