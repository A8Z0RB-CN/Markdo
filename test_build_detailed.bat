@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
echo ========================================
echo 详细测试打包后的程序
echo ========================================
echo.

set BUILD_DIR=build\exe.win-amd64-3.13
cd %BUILD_DIR%

echo [1/3] 检查必要文件是否存在...
if not exist "Markdo.exe" (
    echo ✗ 错误: Markdo.exe 不存在！
    exit /b 1
)
echo ✓ Markdo.exe 存在

if not exist "lib\encodings\__init__.pyc" (
    echo ✗ 错误: 编码模块缺失！
    exit /b 1
)
echo ✓ 编码模块存在

if not exist "lib\PyQt6\Qt6\bin\Qt6Core.dll" (
    echo ✗ 警告: Qt6Core.dll 可能缺失
) else (
    echo ✓ Qt6Core.dll 存在
)
echo.

echo [2/3] 运行程序并捕获输出...
echo 注意：GUI 程序的错误可能不会显示在控制台
echo.

:: 删除旧的错误日志
if exist error.log del /q error.log
if exist output.log del /q output.log

:: 运行程序并捕获输出（GUI 程序可能没有控制台输出）
start /wait /b Markdo.exe >output.log 2>error.log

:: 等待程序启动
timeout /t 3 /nobreak >nul 2>&1

echo [3/3] 检查运行结果...
echo.

:: 检查错误日志
if exist error.log (
    set error_size=0
    for %%A in (error.log) do set error_size=%%~zA
    if !error_size! gtr 0 (
        echo ========================================
        echo 发现错误输出：
        echo ========================================
        type error.log
        echo.
    ) else (
        echo ✓ 错误日志为空（无错误）
    )
) else (
    echo ✓ 未生成错误日志
)

:: 检查输出日志
if exist output.log (
    set output_size=0
    for %%A in (output.log) do set output_size=%%~zA
    if !output_size! gtr 0 (
        echo ========================================
        echo 程序输出：
        echo ========================================
        type output.log
        echo.
    )
)

:: 检查程序进程
tasklist | findstr /i "Markdo.exe" >nul
if %errorlevel% equ 0 (
    echo ✓ 程序进程正在运行
    echo.
    echo 提示：请手动检查程序窗口是否正常显示
    echo       如果窗口没有显示，可能是 GUI 初始化错误
    echo.
) else (
    echo ✗ 程序进程未运行（可能已退出或启动失败）
    echo.
    echo 可能的原因：
    echo 1. 缺少必要的 DLL 文件
    echo 2. 缺少必要的 Python 模块
    echo 3. 程序启动时发生错误
    echo.
    echo 建议：尝试双击 Markdo.exe 查看是否有错误对话框
    echo.
)

cd ..\..

pause



