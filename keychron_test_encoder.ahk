; Keychron V1 Encoder Diagnostic Tool
; Shows exactly what the firmware sends for each encoder action
;
; USAGE: Run this instead of the main script to test encoder behavior

#Requires AutoHotkey v2.0
#SingleInstance Force

; Tracking variables
global lastCommand := -1
global pressStartTime := 0
global isHolding := false
global clickCount := 0
global lastClickTime := 0
global isPressed := false

; Log output
global logMessages := []
global maxLogLines := 20

; ============================================================================
; HOTKEY HANDLERS - Show what firmware sends
; ============================================================================

^!F13:: {
    LogAction("F13 (Command 0)", DetectDirection(0))
    global lastCommand := 0
}

^!F14:: {
    LogAction("F14 (Command 1)", DetectDirection(1))
    global lastCommand := 1
}

^!F15:: {
    LogAction("F15 (Command 2)", DetectDirection(2))
    global lastCommand := 2
}

^!F16:: {
    LogAction("F16 (Command 3)", DetectDirection(3))
    global lastCommand := 3
}

; Knob press down
^!Enter:: {
    global pressStartTime, isHolding, clickCount, lastClickTime, isPressed

    ; Ignore if already pressed (shouldn't happen, but just in case)
    if (isPressed)
        return

    isPressed := true
    pressStartTime := A_TickCount
    isHolding := false

    ; Check for double-click
    timeSinceLastClick := A_TickCount - lastClickTime
    if (timeSinceLastClick < 300) {
        clickCount := 2
        LogAction("DOUBLE-CLICK", "Detected!")
    } else {
        clickCount := 1
    }

    lastClickTime := A_TickCount

    ; Start monitoring for hold
    SetTimer(CheckHold, 50)

    LogAction("PRESS DOWN", "Click " clickCount)
}

; Knob release
^!Enter up:: {
    global pressStartTime, isHolding, isPressed

    if (!isPressed)
        return

    isPressed := false
    holdDuration := A_TickCount - pressStartTime
    SetTimer(CheckHold, 0)  ; Stop monitoring

    if (isHolding) {
        LogAction("RELEASE (after hold)", holdDuration . "ms")
    } else {
        LogAction("RELEASE (tap)", holdDuration . "ms")
    }

    isHolding := false
}

; Check if key is being held
CheckHold() {
    global pressStartTime, isHolding, isPressed

    if (!isPressed)
        return

    holdDuration := A_TickCount - pressStartTime

    if (holdDuration > 500 && !isHolding) {
        isHolding := true
        LogAction("HOLDING", holdDuration . "ms")
    } else if (isHolding && Mod(holdDuration, 500) < 50) {
        LogAction("STILL HOLDING", holdDuration . "ms")
    }
}

; ============================================================================
; HELPER FUNCTIONS
; ============================================================================

DetectDirection(current) {
    global lastCommand

    if (lastCommand == -1) {
        return "FIRST INPUT"
    }

    ; Clockwise: 0→1, 1→2, 2→3, 3→0
    if (current == lastCommand + 1 || (lastCommand == 3 && current == 0)) {
        return "CLOCKWISE ➡"
    }

    ; Counter-clockwise: 0→3, 1→0, 2→1, 3→2
    if (current == lastCommand - 1 || (lastCommand == 0 && current == 3)) {
        return "COUNTER-CLOCKWISE ⬅"
    }

    return "JUMP (skipped " Abs(current - lastCommand) " steps)"
}

LogAction(action, detail) {
    global logMessages, maxLogLines

    timestamp := FormatTime(, "HH:mm:ss")
    message := timestamp . " | " . action . " | " . detail

    ; Add to log
    logMessages.Push(message)

    ; Keep only last N lines
    if (logMessages.Length > maxLogLines) {
        logMessages.RemoveAt(1)
    }

    ; Display log
    UpdateDisplay()
}

UpdateDisplay() {
    global logMessages

    output := "=== KEYCHRON ENCODER DIAGNOSTIC ===`n"
    output .= "Rotate knob, press/hold/double-click to see behavior`n"
    output .= "Close this tooltip to exit`n"
    output .= "`n--- LAST " logMessages.Length " ACTIONS ---`n"

    for index, msg in logMessages {
        output .= msg . "`n"
    }

    ToolTip(output)
}

; ============================================================================
; SYSTEM TRAY
; ============================================================================

A_IconTip := "Keychron Encoder Diagnostic"

A_TrayMenu.Delete()
A_TrayMenu.Add("Testing Encoder Behavior", (*) => "")
A_TrayMenu.Disable("1&")
A_TrayMenu.Add()
A_TrayMenu.Add("Exit", (*) => ExitApp())

; Show initial message
LogAction("READY", "Start testing!")
