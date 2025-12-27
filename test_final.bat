@echo off
chcp 65001 >nul
echo ========================================
echo 最终测试打包后的程序
echo ========================================
echo.

cd build\exe.win-amd64-3.13

echo 检查 DLL 文件...
if exist "Qt6WebEngineCore.dll" (
    echo   ✓ Qt6WebEngineCore.dll 存在
) else (
    echo   ✗ Qt6WebEngineCore.dll 不存在
)

if exist "Qt6WebEngineWidgets.dll" (
    echo   ✓ Qt6WebEngineWidgets.dll 存在
) else (
    echo   ✗ Qt6WebEngineWidgets.dll 不存在
)

if exist "Qt6Network.dll" (
    echo   ✓ Qt6Network.dll 存在
) else (
    echo   ✗ Qt6Network.dll 不存在
)

if exist "Qt6PrintSupport.dll" (
    echo   ✓ Qt6PrintSupport.dll 存在
) else (
    echo   ✗ Qt6PrintSupport.dll 不存在
)

echo.
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
    echo 请测试以下功能：
    echo 1. 打开 Markdown 文件
    echo 2. 编辑和预览功能
    echo 3. 保存文件
) else (
    echo ✗ 程序未在运行（可能已退出或启动失败）
    echo.
    echo 请手动双击 Markdo.exe 查看是否有错误对话框
)

cd ..\..

pause



