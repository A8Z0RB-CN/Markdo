@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
echo ========================================
echo 清理废弃和多余文件
echo ========================================
echo.

set deleted_count=0

:: 删除测试文件
echo [1/5] 删除测试文件...
for %%f in (
    test_*.py
    quick_test.py
    verify_shortcuts.py
) do (
    if exist "%%f" (
        del /q "%%f" >nul 2>&1
        if !errorlevel! equ 0 (
            echo   已删除: %%f
            set /a deleted_count+=1
        )
    )
)

:: 删除临时和测试文件
echo [2/5] 删除临时文件...
for %%f in (
    latex_test.html
    latex_test.md
    test_open.md
    kimi.exe
    python-3.11.9-amd64.exe
) do (
    if exist "%%f" (
        del /q "%%f" >nul 2>&1
        if !errorlevel! equ 0 (
            echo   已删除: %%f
            set /a deleted_count+=1
        )
    )
)

:: 删除旧的构建目录（保留结构）
echo [3/5] 清理旧的构建目录...
if exist "build\exe.win-amd64-3.13" (
    rd /s /q "build\exe.win-amd64-3.13" >nul 2>&1
    if !errorlevel! equ 0 (
        echo   已清理: build\exe.win-amd64-3.13
        set /a deleted_count+=1
    )
)
if exist "build\bdist.win-amd64" (
    rd /s /q "build\bdist.win-amd64" >nul 2>&1
    if !errorlevel! equ 0 (
        echo   已清理: build\bdist.win-amd64
        set /a deleted_count+=1
    )
)

:: 删除旧的安装程序目录（可选，保留最新版本）
echo [4/5] 清理旧的安装程序...
if exist "installer_cx" (
    for %%f in ("installer_cx\*.exe") do (
        echo   保留: %%~nxf
    )
)

:: 删除 __pycache__ 目录
echo [5/5] 清理 Python 缓存...
for /d /r . %%d in (__pycache__) do (
    if exist "%%d" (
        rd /s /q "%%d" >nul 2>&1
        if !errorlevel! equ 0 (
            echo   已清理: %%d
            set /a deleted_count+=1
        )
    )
)

echo.
echo ========================================
echo 清理完成，共处理 %deleted_count% 项
echo ========================================
echo.
pause

