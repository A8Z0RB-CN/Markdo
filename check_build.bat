@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
echo ========================================
echo Markdo 打包文件检查
echo ========================================
echo.

set BUILD_DIR=build\exe.win-amd64-3.13
set ERROR_COUNT=0

:: 检查构建目录
if not exist "%BUILD_DIR%" (
    echo [错误] 构建目录不存在: %BUILD_DIR%
    pause
    exit /b 1
)

:: 1. 检查可执行文件
echo [1/7] 检查可执行文件...
if exist "%BUILD_DIR%\Markdo.exe" (
    echo   [OK] Markdo.exe 存在
) else (
    echo   [错误] Markdo.exe 不存在
    set /a ERROR_COUNT+=1
)

:: 2. 检查资源文件
echo [2/7] 检查资源文件...
for %%f in (
    markdo-icon.png
    register_file_association.bat
    unregister_file_association.bat
    FILE_ASSOCIATION_README.md
) do (
    if exist "%BUILD_DIR%\%%f" (
        echo   [OK] %%f 存在
    ) else (
        echo   [错误] %%f 不存在
        set /a ERROR_COUNT+=1
    )
)

:: 3. 检查核心库
echo [3/7] 检查核心库...
for %%d in (
    lib\PyQt6
    lib\markdown
    lib\pymdownx
    lib\pygments
) do (
    if exist "%BUILD_DIR%\%%d" (
        echo   [OK] %%d 已包含
    ) else (
        echo   [错误] %%d 未包含
        set /a ERROR_COUNT+=1
    )
)

:: 4. 检查 Python DLL
echo [4/7] 检查 Python DLL...
if exist "%BUILD_DIR%\python3.dll" (
    echo   [OK] python3.dll 存在
) else if exist "%BUILD_DIR%\python313.dll" (
    echo   [OK] python313.dll 存在
) else (
    echo   [警告] Python DLL 未找到（可能使用不同版本）
)

:: 5. 计算打包体积
echo [5/7] 计算打包体积...
powershell -Command "$size = (Get-ChildItem -Path '%BUILD_DIR%' -Recurse -File | Measure-Object -Property Length -Sum).Sum; $mb = [math]::Round($size / 1MB, 2); Write-Host \"  打包目录总大小: $mb MB\""

:: 6. 检查排除的模块
echo [6/7] 检查排除的模块...
if exist "%BUILD_DIR%\lib\test" (
    echo   [警告] lib\test 仍然存在（应该被排除）
) else (
    echo   [OK] lib\test 已正确排除
)
if exist "%BUILD_DIR%\lib\tkinter" (
    echo   [警告] lib\tkinter 仍然存在（应该被排除）
) else (
    echo   [OK] lib\tkinter 已正确排除
)

:: 7. 检查配置文件
echo [7/7] 检查配置文件...
if exist "setup_cx.py" (
    echo   [OK] setup_cx.py 存在
    
    findstr /C:"pygments" setup_cx.py >nul 2>&1
    if !errorlevel! equ 0 (
        echo   [OK] pygments 已在配置中
    ) else (
        echo   [警告] pygments 未在配置中
    )
    
    findstr /C:"\"copyreg\"" setup_cx.py >nul 2>&1
    if !errorlevel! equ 0 (
        echo   [错误] copyreg 仍在排除列表中
        set /a ERROR_COUNT+=1
    ) else (
        echo   [OK] copyreg 未在排除列表中
    )
) else (
    echo   [错误] setup_cx.py 不存在
    set /a ERROR_COUNT+=1
)

echo.
echo ========================================
if !ERROR_COUNT! equ 0 (
    echo [OK] 检查完成，未发现错误
) else (
    echo [错误] 发现 !ERROR_COUNT! 个错误
)
echo ========================================
echo.

pause



