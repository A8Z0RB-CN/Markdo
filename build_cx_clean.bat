@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
echo ========================================
echo Markdo cx_Freeze 打包脚本（优化版）
echo ========================================
echo.

:: 步骤1: 清理废弃文件
echo [1/4] 清理废弃和多余文件...
call cleanup_before_build.bat
if errorlevel 1 (
    echo 警告: 清理过程中出现错误，继续打包...
)
echo.

:: 步骤2: 检查图标文件
echo [2/4] 检查图标文件...
if not exist "Markdo.ico" (
    echo 未找到 Markdo.ico，正在生成...
    python create_icon.py
    if errorlevel 1 (
        echo 警告: 图标生成失败，将继续打包但可能没有图标
    ) else (
        echo ✓ 图标文件已生成
    )
) else (
    echo ✓ 图标文件已存在
)
echo.

:: 步骤3: cx_Freeze打包
echo [3/4] 使用 cx_Freeze 打包程序...
echo 这可能需要几分钟，请耐心等待...
echo.
python setup_cx.py build
if errorlevel 1 (
    echo.
    echo ========================================
    echo [错误] cx_Freeze 打包失败！
    echo ========================================
    echo.
    echo 请检查：
    echo 1. 是否已安装 cx_Freeze: pip install cx_Freeze
    echo 2. 是否已安装所有依赖: pip install -r requirements.txt
    echo 3. 查看上方的错误信息
    echo.
    pause
    exit /b 1
)
echo ✓ cx_Freeze 打包成功！
echo.

:: 步骤4: 清理打包后的多余文件
echo [4/4] 清理打包后的多余文件...
set cleaned_count=0

:: 查找打包输出目录
set BUILD_DIR=
for /d %%d in ("build\exe.win-amd64-*") do (
    set BUILD_DIR=%%d
)

if defined BUILD_DIR (
    echo 找到构建目录: !BUILD_DIR!
    
    :: 删除测试目录
    if exist "!BUILD_DIR!\lib\test" (
        rd /s /q "!BUILD_DIR!\lib\test" >nul 2>&1
        echo   已删除: lib\test
        set /a cleaned_count+=1
    )
    if exist "!BUILD_DIR!\lib\tests" (
        rd /s /q "!BUILD_DIR!\lib\tests" >nul 2>&1
        echo   已删除: lib\tests
        set /a cleaned_count+=1
    )
    
    :: 删除文档目录
    if exist "!BUILD_DIR!\lib\docs" (
        rd /s /q "!BUILD_DIR!\lib\docs" >nul 2>&1
        echo   已删除: lib\docs
        set /a cleaned_count+=1
    )
    
    :: 删除示例目录
    if exist "!BUILD_DIR!\lib\examples" (
        rd /s /q "!BUILD_DIR!\lib\examples" >nul 2>&1
        echo   已删除: lib\examples
        set /a cleaned_count+=1
    )
    
    :: 删除 .pyc 文件
    for /r "!BUILD_DIR!" %%f in (*.pyc) do (
        del /q "%%f" >nul 2>&1
    )
    
    :: 删除 .pyi 文件
    for /r "!BUILD_DIR!" %%f in (*.pyi) do (
        del /q "%%f" >nul 2>&1
    )
    
    :: 删除 README 和 LICENSE 文件（如果不需要）
    if exist "!BUILD_DIR!\README.md" (
        del /q "!BUILD_DIR!\README.md" >nul 2>&1
        echo   已删除: README.md
        set /a cleaned_count+=1
    )
    if exist "!BUILD_DIR!\LICENSE" (
        del /q "!BUILD_DIR!\LICENSE" >nul 2>&1
        echo   已删除: LICENSE
        set /a cleaned_count+=1
    )
    if exist "!BUILD_DIR!\LICENSE.txt" (
        del /q "!BUILD_DIR!\LICENSE.txt" >nul 2>&1
        echo   已删除: LICENSE.txt
        set /a cleaned_count+=1
    )
    
    echo 清理完成，共删除 !cleaned_count! 项
) else (
    echo 警告: 未找到构建目录
)

echo.

:: 计算打包体积
echo ========================================
echo ✓ 打包完成！
echo ========================================
echo.

if defined BUILD_DIR (
    echo 输出目录: !BUILD_DIR!
    echo 可执行文件: !BUILD_DIR!\Markdo.exe
    echo.
    
    :: 计算目录大小
    powershell -Command "$size = (Get-ChildItem -Path '!BUILD_DIR!' -Recurse -File | Measure-Object -Property Length -Sum).Sum; $mb = [math]::Round($size / 1MB, 2); Write-Host \"打包目录总大小: $mb MB ($size 字节)\""
    echo.
    
    echo 优化说明：
    echo 1. 已排除测试、文档、示例等不必要的模块
    echo 2. 已删除打包后的测试和文档目录
    echo 3. 已删除 .pyc 和 .pyi 文件
    echo 4. 已优化包含的包，只包含必要的模块
    echo.
) else (
    echo 请检查 build 目录中的输出文件
    echo.
)

echo 现在可以：
echo 1. 测试运行: !BUILD_DIR!\Markdo.exe
echo 2. 使用 Inno Setup 创建安装程序（可选）
echo.

pause



