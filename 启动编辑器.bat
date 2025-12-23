@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo   Markdown 编辑器 (PyQt6)
echo ========================================
echo.

if exist .venv\Scripts\python.exe (
    echo 使用虚拟环境启动...
    .venv\Scripts\python.exe run.py
) else (
    echo 使用系统Python启动...
    python run.py
)

if errorlevel 1 (
    echo.
    echo 启动失败！
    pause
)
