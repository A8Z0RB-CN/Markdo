@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
echo ========================================
echo Markdo Nuitka 单文件打包脚本
echo ========================================
echo.
echo 注意: 单文件模式启动较慢，但分发更方便
echo.

:: 检查 Nuitka 是否已安装
echo [1/5] 检查 Nuitka 是否已安装...
:: 优先使用 Python 3.11，如果没有则使用默认 Python
py -3.11 --version >nul 2>&1
if errorlevel 1 (
    set PYTHON_CMD=python
) else (
    set PYTHON_CMD=py -3.11
)

%PYTHON_CMD% -m nuitka --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未检测到 Nuitka！
    echo.
    echo 请先安装 Nuitka:
    echo   %PYTHON_CMD% -m pip install nuitka
    echo.
    pause
    exit /b 1
)
echo ✓ Nuitka 已安装
echo.

:: 检查图标文件
echo [2/5] 检查图标文件...
if not exist "Markdo.ico" (
    if exist "markdo-icon.ico" (
        echo 使用 markdo-icon.ico 作为图标...
        set ICON_FILE=markdo-icon.ico
    ) else (
        echo 警告: 未找到图标文件，将使用默认图标
        set ICON_FILE=
    )
) else (
    echo ✓ 找到图标文件: Markdo.ico
    set ICON_FILE=Markdo.ico
)
echo.

:: 清理之前的构建
echo [3/5] 清理之前的构建文件...
if exist "build" (
    rd /s /q "build" >nul 2>&1
    echo   已删除 build 目录
)
if exist "Markdo.dist" (
    rd /s /q "Markdo.dist" >nul 2>&1
    echo   已删除 Markdo.dist 目录
)
if exist "Markdo.build" (
    rd /s /q "Markdo.build" >nul 2>&1
    echo   已删除 Markdo.build 目录
)
if exist "Markdo.onefile-build" (
    rd /s /q "Markdo.onefile-build" >nul 2>&1
    echo   已删除 Markdo.onefile-build 目录
)
if exist "Markdo.exe" (
    del /q "Markdo.exe" >nul 2>&1
    echo   已删除 Markdo.exe
)
echo ✓ 清理完成
echo.

:: 开始打包
echo [4/5] 使用 Nuitka 打包程序（单文件模式）...
echo 这可能需要几分钟，请耐心等待...
echo.

:: 构建 Nuitka 命令（单文件模式）
set NUITKA_CMD=!PYTHON_CMD! -m nuitka ^
    --standalone ^
    --onefile ^
    --enable-plugin=pyqt6 ^
    --windows-disable-console ^
    --assume-yes-for-downloads ^
    --output-dir=build ^
    --output-filename=Markdo.exe

:: 添加图标
if defined ICON_FILE (
    set NUITKA_CMD=!NUITKA_CMD! ^
    --windows-icon-from-ico=!ICON_FILE!
)

:: 包含数据文件
set NUITKA_CMD=!NUITKA_CMD! ^
    --include-data-file=markdo-icon.png=markdo-icon.png

:: 包含 bat 文件（如果存在）
if exist "register_file_association.bat" (
    set NUITKA_CMD=!NUITKA_CMD! ^
    --include-data-file=register_file_association.bat=register_file_association.bat
)
if exist "unregister_file_association.bat" (
    set NUITKA_CMD=!NUITKA_CMD! ^
    --include-data-file=unregister_file_association.bat=unregister_file_association.bat
)
if exist "FILE_ASSOCIATION_README.md" (
    set NUITKA_CMD=!NUITKA_CMD! ^
    --include-data-file=FILE_ASSOCIATION_README.md=FILE_ASSOCIATION_README.md
)

:: 包含必要的模块
set NUITKA_CMD=!NUITKA_CMD! ^
    --include-module=markdown ^
    --include-module=markdown.extensions ^
    --include-module=markdown.extensions.extra ^
    --include-module=markdown.extensions.codehilite ^
    --include-module=markdown.extensions.toc ^
    --include-module=pymdownx ^
    --include-module=pymdownx.tilde ^
    --include-module=pymdownx.caret ^
    --include-module=pymdownx.mark ^
    --include-module=pymdownx.arithmatex ^
    --include-module=pygments

:: 优化选项
set NUITKA_CMD=!NUITKA_CMD! ^
    --remove-output ^
    --show-progress

:: 执行打包命令
echo 执行命令:
echo !NUITKA_CMD!
echo.
!NUITKA_CMD!

if errorlevel 1 (
    echo.
    echo ========================================
    echo [错误] Nuitka 打包失败！
    echo ========================================
    echo.
    echo 请检查：
    echo 1. 是否已安装 Nuitka: pip install nuitka
    echo 2. 是否已安装所有依赖: pip install -r requirements.txt
    echo 3. 是否已安装 Visual C++ 编译器（Windows）
    echo 4. 查看上方的错误信息
    echo.
    pause
    exit /b 1
)
echo ✓ Nuitka 打包成功！
echo.

:: 后处理
echo [5/5] 后处理...
set BUILD_DIR=build
if exist "!BUILD_DIR!\Markdo.exe" (
    echo ✓ 找到可执行文件: !BUILD_DIR!\Markdo.exe
    
    :: 复制额外的文件到输出目录（单文件模式下，这些文件需要放在 exe 同目录）
    if exist "markdo-icon.png" (
        copy /y "markdo-icon.png" "!BUILD_DIR!\" >nul 2>&1
        echo   已复制: markdo-icon.png
    )
    if exist "register_file_association.bat" (
        copy /y "register_file_association.bat" "!BUILD_DIR!\" >nul 2>&1
        echo   已复制: register_file_association.bat
    )
    if exist "unregister_file_association.bat" (
        copy /y "unregister_file_association.bat" "!BUILD_DIR!\" >nul 2>&1
        echo   已复制: unregister_file_association.bat
    )
    if exist "FILE_ASSOCIATION_README.md" (
        copy /y "FILE_ASSOCIATION_README.md" "!BUILD_DIR!\" >nul 2>&1
        echo   已复制: FILE_ASSOCIATION_README.md
    )
) else (
    echo 警告: 未找到可执行文件
)

echo.
echo ========================================
echo ✓ 打包完成！
echo ========================================
echo.

if exist "!BUILD_DIR!\Markdo.exe" (
    echo 输出目录: !BUILD_DIR!
    echo 可执行文件: !BUILD_DIR!\Markdo.exe
    echo.
    
    :: 计算文件大小
    powershell -Command "$size = (Get-Item '!BUILD_DIR!\Markdo.exe').Length; $mb = [math]::Round($size / 1MB, 2); Write-Host \"可执行文件大小: $mb MB ($size 字节)\""
    echo.
    
    echo 注意: 单文件模式启动时会解压临时文件，首次启动可能较慢
    echo.
    echo 现在可以：
    echo 1. 测试运行: !BUILD_DIR!\Markdo.exe
    echo 2. 分发整个 build 目录（包含 exe 和数据文件）
    echo 3. 使用 Inno Setup 创建安装程序（可选）
    echo.
) else (
    echo 请检查 build 目录中的输出文件
    echo.
)

pause

