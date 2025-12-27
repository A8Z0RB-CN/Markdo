@echo off
chcp 65001 >nul
echo ========================================
echo 测试打包后的程序
echo ========================================
echo.

set BUILD_DIR=build\exe.win-amd64-3.13

if not exist "%BUILD_DIR%\Markdo.exe" (
    echo [错误] 未找到打包后的程序
    pause
    exit /b 1
)

echo 正在运行程序...
echo 如果程序正常启动，窗口会打开
echo 如果出现错误，请查看错误信息
echo.
echo ----------------------------------------
echo.

cd /d "%BUILD_DIR%"

:: 运行程序并重定向错误输出
Markdo.exe 2>&1 | more

echo.
echo ----------------------------------------
echo 程序已退出
echo.
pause

