@echo off
REM Keychron V1 Firmware Build Script
REM Run this in QMK MSYS terminal

echo ========================================
echo Keychron V1 Command Macro - Build Script
echo ========================================
echo.

cd /d C:\CLIPALS\qmk_firmware

echo Copying firmware files...
if not exist "keyboards\keychron\v1\ansi_encoder\keymaps\macro" mkdir keyboards\keychron\v1\ansi_encoder\keymaps\macro
copy /Y C:\CLIPALS\firmware\keymap.c keyboards\keychron\v1\ansi_encoder\keymaps\macro\keymap.c
copy /Y C:\CLIPALS\firmware\rules.mk keyboards\keychron\v1\ansi_encoder\keymaps\macro\rules.mk

echo.
echo Files copied successfully!
echo.
echo Starting compilation...
echo.

qmk compile -kb keychron/v1/ansi_encoder -km macro

echo.
echo ========================================
echo Build Complete!
echo ========================================
echo.
echo Firmware location:
echo C:\CLIPALS\qmk_firmware\.build\keychron_v1_ansi_encoder_macro.bin
echo.
echo Next step: Flash with QMK Toolbox
echo.
pause
