@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo 复制 Qt DLL 到可执行文件目录
echo ========================================
echo.

set BUILD_DIR=
for /d %%d in ("build\exe.win-amd64-*") do (
    set BUILD_DIR=%%d
)

if not defined BUILD_DIR (
    echo 错误: 未找到构建目录
    pause
    exit /b 1
)

echo 构建目录: !BUILD_DIR!
echo.

:: 复制 QtWebEngine 相关的 DLL 到可执行文件目录
echo [1/2] 复制 QtWebEngine DLL...
set QT_BIN_DIR=!BUILD_DIR!\lib\PyQt6\Qt6\bin
set EXE_DIR=!BUILD_DIR!

if exist "!QT_BIN_DIR!\Qt6WebEngineCore.dll" (
    copy /y "!QT_BIN_DIR!\Qt6WebEngineCore.dll" "!EXE_DIR!\" >nul 2>&1
    if !errorlevel! equ 0 (
        echo   ✓ 已复制: Qt6WebEngineCore.dll
    )
)

if exist "!QT_BIN_DIR!\Qt6WebEngineWidgets.dll" (
    copy /y "!QT_BIN_DIR!\Qt6WebEngineWidgets.dll" "!EXE_DIR!\" >nul 2>&1
    if !errorlevel! equ 0 (
        echo   ✓ 已复制: Qt6WebEngineWidgets.dll
    )
)

if exist "!QT_BIN_DIR!\Qt6Network.dll" (
    copy /y "!QT_BIN_DIR!\Qt6Network.dll" "!EXE_DIR!\" >nul 2>&1
    if !errorlevel! equ 0 (
        echo   ✓ 已复制: Qt6Network.dll
    )
)

if exist "!QT_BIN_DIR!\Qt6PrintSupport.dll" (
    copy /y "!QT_BIN_DIR!\Qt6PrintSupport.dll" "!EXE_DIR!\" >nul 2>&1
    if !errorlevel! equ 0 (
        echo   ✓ 已复制: Qt6PrintSupport.dll
    )
)

if exist "!QT_BIN_DIR!\Qt6WebChannel.dll" (
    copy /y "!QT_BIN_DIR!\Qt6WebChannel.dll" "!EXE_DIR!\" >nul 2>&1
    if !errorlevel! equ 0 (
        echo   ✓ 已复制: Qt6WebChannel.dll
    )
)

if exist "!QT_BIN_DIR!\Qt6Core.dll" (
    copy /y "!QT_BIN_DIR!\Qt6Core.dll" "!EXE_DIR!\" >nul 2>&1
    if !errorlevel! equ 0 (
        echo   ✓ 已复制: Qt6Core.dll
    )
)

if exist "!QT_BIN_DIR!\Qt6Gui.dll" (
    copy /y "!QT_BIN_DIR!\Qt6Gui.dll" "!EXE_DIR!\" >nul 2>&1
    if !errorlevel! equ 0 (
        echo   ✓ 已复制: Qt6Gui.dll
    )
)

if exist "!QT_BIN_DIR!\Qt6Widgets.dll" (
    copy /y "!QT_BIN_DIR!\Qt6Widgets.dll" "!EXE_DIR!\" >nul 2>&1
    if !errorlevel! equ 0 (
        echo   ✓ 已复制: Qt6Widgets.dll
    )
)

echo.
echo [2/2] 复制 QtWebEngine 资源文件...
set QT_RESOURCES_DIR=!BUILD_DIR!\lib\PyQt6\Qt6\resources
set EXE_RESOURCES_DIR=!EXE_DIR!\resources

if not exist "!EXE_RESOURCES_DIR!" mkdir "!EXE_RESOURCES_DIR!"

if exist "!QT_RESOURCES_DIR!" (
    xcopy /y /e /i "!QT_RESOURCES_DIR!\*" "!EXE_RESOURCES_DIR!\" >nul 2>&1
    if !errorlevel! equ 0 (
        echo   ✓ 已复制资源文件到 resources 目录
    )
)

echo.
echo ========================================
echo ✓ DLL 复制完成！
echo ========================================
echo.

pause



