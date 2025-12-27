@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
echo ========================================
echo Markdo cx_Freeze 完整打包 + 清理脚本
echo ========================================
echo.
echo 此脚本将：
echo 1. 完整打包所有模块（确保不缺少任何依赖）
echo 2. 清理不影响程序运行的文件和模块
echo.

:: 步骤1: 清理废弃文件
echo [1/5] 清理废弃和多余文件...
if exist cleanup_before_build.bat (
    call cleanup_before_build.bat
    if errorlevel 1 (
        echo 警告: 清理过程中出现错误，继续打包...
    )
) else (
    echo 跳过：未找到 cleanup_before_build.bat
)
echo.

:: 步骤2: 检查图标文件
echo [2/5] 检查图标文件...
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

:: 步骤3: 完整打包（使用完整配置）
echo [3/5] 使用 cx_Freeze 完整打包程序...
echo 这可能需要几分钟，请耐心等待...
echo 注意：此步骤会包含所有模块，确保不缺少任何依赖
echo.
python setup_cx_full.py build
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
echo ✓ cx_Freeze 完整打包成功！
echo.

:: 步骤4: 清理打包后的不必要文件
echo [4/5] 清理打包后的不必要文件...
echo 正在删除不影响程序运行的文件和模块...
echo.
call cleanup_after_build.bat
if errorlevel 1 (
    echo 警告: 清理过程中出现错误
)
echo.

:: 步骤5: 显示最终结果
echo [5/5] 打包和清理完成！
echo.
echo ========================================
echo ✓ 打包完成！
echo ========================================
echo.

:: 查找打包输出目录
set BUILD_DIR=
for /d %%d in ("build\exe.win-amd64-*") do (
    set BUILD_DIR=%%d
)

if defined BUILD_DIR (
    echo 输出目录: !BUILD_DIR!
    echo 可执行文件: !BUILD_DIR!\Markdo.exe
    echo.
    
    :: 计算目录大小
    powershell -Command "$size = (Get-ChildItem -Path '!BUILD_DIR!' -Recurse -File | Measure-Object -Property Length -Sum).Sum; $mb = [math]::Round($size / 1MB, 2); Write-Host \"最终打包目录总大小: $mb MB ($size 字节)\""
    echo.
    
    echo 优化说明：
    echo 1. ✓ 完整打包了所有必要的模块（确保不缺少依赖）
    echo 2. ✓ 删除了测试、文档、示例等不必要的目录
    echo 3. ✓ 删除了 .pyc 和 .pyi 文件
    echo 4. ✓ 删除了 PyQt6 不需要的模块和插件
    echo 5. ✓ 删除了不需要的 Python 标准库模块
    echo 6. ✓ 清理了不需要的编码文件
    echo.
    
    echo 建议测试：
    echo 1. 运行程序: !BUILD_DIR!\Markdo.exe
    echo 2. 测试所有功能（打开文件、Markdown 渲染、预览等）
    echo 3. 如果出现模块缺失错误，请告知具体错误信息
    echo.
) else (
    echo 警告: 未找到构建目录
    echo 请检查 build 目录中的输出文件
    echo.
)

pause



