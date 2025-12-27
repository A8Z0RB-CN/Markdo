@echo off
chcp 65001 >nul
echo ========================================
echo 测试打包后的程序
echo ========================================
echo.

cd build\exe.win-amd64-3.13

echo 正在启动程序...
start Markdo.exe

echo 等待 5 秒...
timeout /t 5 /nobreak >nul 2>&1

echo.
echo 检查程序是否在运行...
tasklist | findstr /i "Markdo.exe" >nul
if %errorlevel% equ 0 (
    echo ✓ 程序正在运行中！
    echo.
    echo 如果程序窗口正常显示，说明问题已解决。
    echo 如果程序窗口没有显示或出现错误对话框，请告诉我具体的错误信息。
) else (
    echo ✗ 程序未在运行（可能已退出或启动失败）
    echo.
    echo 请手动双击 Markdo.exe 查看是否有错误对话框
)

cd ..\..

pause



