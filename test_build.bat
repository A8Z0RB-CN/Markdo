@echo off
chcp 65001 >nul
echo ========================================
echo 测试打包后的程序
echo ========================================
echo.

cd build\exe.win-amd64-3.13

echo 正在运行 Markdo.exe...
echo 如果程序启动失败，错误信息将显示在下方：
echo.

:: 尝试运行程序，捕获错误输出
Markdo.exe 2>error.log

:: 等待几秒让程序启动
timeout /t 2 /nobreak >nul 2>&1

:: 检查是否有错误日志
if exist error.log (
    echo.
    echo ========================================
    echo 发现错误日志：
    echo ========================================
    type error.log
    echo.
) else (
    echo.
    echo ✓ 程序已启动（未发现错误日志）
    echo.
)

:: 检查程序是否在运行
tasklist | findstr /i "Markdo.exe" >nul
if %errorlevel% equ 0 (
    echo ✓ 程序正在运行中
    echo.
    echo 提示：程序是 GUI 应用，请手动检查窗口是否正常显示
    echo.
) else (
    echo ✗ 程序未在运行（可能已退出或启动失败）
    echo.
)

cd ..\..

pause
