@echo off
:: Markdo 完整打包脚本 (cx_Freeze + Inno Setup)
echo ========================================
echo Markdo 安装包打包脚本
echo ========================================
echo.

:: 步骤1: 清理旧的构建
echo [1/3] 清理旧的构建文件...
if exist build\exe.win-amd64-3.13 (
    rd /s /q build\exe.win-amd64-3.13
    echo 已清理旧文件
)
echo.

:: 步骤2: cx_Freeze打包
echo [2/3] 使用 cx_Freeze 打包程序...
python setup_cx.py build
if errorlevel 1 (
    echo 错误: cx_Freeze 打包失败！
    pause
    exit /b 1
)
echo ✓ cx_Freeze 打包成功！
echo.

:: 步骤3: Inno Setup编译安装包
echo [3/3] 使用 Inno Setup 制作安装包...

:: 尝试查找Inno Setup
set "ISCC="
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set "ISCC=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
)
if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set "ISCC=C:\Program Files\Inno Setup 6\ISCC.exe"
)

if defined ISCC (
    "%ISCC%" setup_cx.iss
    if errorlevel 1 (
        echo 错误: Inno Setup 编译失败！
        pause
        exit /b 1
    )
    echo.
    echo ========================================
    echo ✓ 安装包制作成功！
    echo ========================================
    echo.
    echo 安装包位置: installer_cx\Markdo_Setup_CX_1.0.3.exe
    echo.
    echo 现在可以：
    echo 1. 运行安装包测试安装
    echo 2. 分发给其他用户使用
    echo.
) else (
    echo.
    echo ========================================
    echo ⚠ 未找到 Inno Setup
    echo ========================================
    echo.
    echo 请先安装 Inno Setup:
    echo 1. 访问 https://jrsoftware.org/isdl.php
    echo 2. 下载并安装 Inno Setup 6
    echo 3. 重新运行此脚本
    echo.
    echo 或者手动编译:
    echo 1. 右键点击 setup_cx.iss
    echo 2. 选择 "Compile"
    echo.
    echo cx_Freeze 打包已完成，可执行文件位于:
    echo build\exe.win-amd64-3.13\
    echo.
)

pause
