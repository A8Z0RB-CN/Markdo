@echo off
chcp 65001 >nul
echo ========================================
echo Build Markdo Installer (Nuitka)
echo ========================================
echo.

:: Check if Inno Setup is installed
set INNO_SETUP_PATH=
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set "INNO_SETUP_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
) else if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set "INNO_SETUP_PATH=C:\Program Files\Inno Setup 6\ISCC.exe"
) else (
    echo Error: Inno Setup not found!
    echo.
    echo Please install Inno Setup from:
    echo https://jrsoftware.org/isdl.php
    echo.
    pause
    exit /b 1
)

echo Found Inno Setup: %INNO_SETUP_PATH%
echo.

:: Check if build directory exists
if not exist "build\main.dist\Markdo.exe" (
    echo Error: Nuitka build not found!
    echo.
    echo Please run build_nuitka.bat first to build the application.
    echo.
    pause
    exit /b 1
)

echo Building installer...
echo.

:: Compile installer
"%INNO_SETUP_PATH%" setup_nuitka.iss

if errorlevel 1 (
    echo.
    echo ========================================
    echo Error: Installer build failed!
    echo ========================================
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Installer built successfully!
echo ========================================
echo.
echo Output: installer_nuitka\Markdo_Setup_Nuitka_1.0.3.exe
echo.

pause
