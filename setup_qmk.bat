@echo off
REM QMK Firmware Setup and Compilation Script
REM This script sets up the QMK environment in MSYS2 and compiles the firmware

echo ========================================
echo QMK Firmware Setup and Compilation
echo ========================================
echo.

REM Check if MSYS2 is installed
if not exist "C:\msys64\msys2_shell.cmd" (
    echo [ERROR] MSYS2 not found at C:\msys64
    echo.
    echo Please install MSYS2 first:
    echo 1. Run: powershell -ExecutionPolicy Bypass -File download_msys2.ps1
    echo    OR
    echo 2. Download from: https://www.msys2.org/
    echo.
    pause
    exit /b 1
)

echo [OK] MSYS2 found at C:\msys64
echo.

echo Creating setup script for MSYS2...
echo.

REM Create a bash script that MSYS2 will execute
set SETUP_SCRIPT=%TEMP%\qmk_setup.sh
set COMPILE_SCRIPT=%TEMP%\qmk_compile.sh

REM Write the setup script
(
echo #!/bin/bash
echo echo "=========================================="
echo echo "Installing QMK Build Dependencies"
echo echo "=========================================="
echo echo ""
echo.
echo echo "Step 1: Installing base development tools..."
echo pacman -S --needed --noconfirm base-devel mingw-w64-x86_64-toolchain git mingw-w64-x86_64-python-pip unzip
echo.
echo echo ""
echo echo "Step 2: Installing QMK CLI..."
echo python -m pip install --user qmk
echo.
echo echo ""
echo echo "Step 3: Setting up QMK..."
echo export PATH="$HOME/.local/bin:$PATH"
echo cd /c/CLIPALS/qmk_firmware
echo qmk setup -y
echo.
echo echo ""
echo echo "=========================================="
echo echo "Setup Complete!"
echo echo "=========================================="
echo echo ""
echo echo "You can now compile the firmware."
echo read -p "Press Enter to continue..."
) > "%SETUP_SCRIPT%"

REM Write the compile script
(
echo #!/bin/bash
echo cd /c/CLIPALS/qmk_firmware
echo export PATH="$HOME/.local/bin:$PATH"
echo.
echo echo "=========================================="
echo echo "Compiling Keychron V1 Knob Macros Firmware"
echo echo "=========================================="
echo echo ""
echo echo "Keyboard: keychron/v1/ansi_encoder"
echo echo "Keymap: knob_macros"
echo echo ""
echo.
echo qmk compile -kb keychron/v1/ansi_encoder -km knob_macros
echo.
echo if [ $? -eq 0 ]; then
echo     echo ""
echo     echo "=========================================="
echo     echo "✓ Compilation Successful!"
echo     echo "=========================================="
echo     echo ""
echo     echo "Firmware file created:"
echo     ls -lh keychron_v1_ansi_encoder_knob_macros.bin 2^>/dev/null ^|^| echo "File: keychron_v1_ansi_encoder_knob_macros.bin"
echo     echo ""
echo     echo "Location: /c/CLIPALS/qmk_firmware/"
echo     echo ""
echo     echo "Next: Flash this .bin file to your keyboard using QMK Toolbox"
echo else
echo     echo ""
echo     echo "=========================================="
echo     echo "✗ Compilation Failed"
echo     echo "=========================================="
echo     echo ""
echo     echo "Check the error messages above."
echo     echo "Common fixes:"
echo     echo "  - Run 'qmk doctor' to diagnose issues"
echo     echo "  - Make sure all dependencies are installed"
echo fi
echo.
echo read -p "Press Enter to exit..."
) > "%COMPILE_SCRIPT%"

echo Select an option:
echo.
echo 1. Full Setup (install dependencies + compile)
echo 2. Compile Only (dependencies already installed)
echo 3. Exit
echo.

choice /c 123 /n /m "Enter your choice (1, 2, or 3): "

if errorlevel 3 (
    echo.
    echo Exiting...
    exit /b 0
)

if errorlevel 2 (
    echo.
    echo Opening MSYS2 MinGW 64-bit for compilation...
    echo.
    C:\msys64\msys2_shell.cmd -mingw64 -no-start -defterm -here -shell bash "%COMPILE_SCRIPT%"
    goto :end
)

if errorlevel 1 (
    echo.
    echo Opening MSYS2 MinGW 64-bit for full setup...
    echo.
    echo This will:
    echo - Install build tools (gcc, make, etc.)
    echo - Install QMK CLI
    echo - Setup QMK environment
    echo - Then you can compile
    echo.
    pause

    C:\msys64\msys2_shell.cmd -mingw64 -no-start -defterm -here -shell bash "%SETUP_SCRIPT%"

    echo.
    echo Setup complete! Now compiling firmware...
    timeout /t 3

    C:\msys64\msys2_shell.cmd -mingw64 -no-start -defterm -here -shell bash "%COMPILE_SCRIPT%"
    goto :end
)

:end
echo.
echo Done!
pause
