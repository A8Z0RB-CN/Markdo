@echo off
:: Python 3.11.9 自动安装脚本
:: 确保勾选 "Add Python to PATH"

echo ========================================
echo Python 3.11.9 安装脚本
echo ========================================
echo.

if not exist "python-3.11.9-amd64.exe" (
    echo [错误] 找不到 Python 安装程序！
    echo 请确保 python-3.11.9-amd64.exe 在当前目录
    pause
    exit /b 1
)

echo [提示] 即将启动 Python 安装程序
echo.
echo [重要] 安装时请务必：
echo 1. 勾选 "Add Python to PATH" （非常重要！）
echo 2. 选择 "Install Now" 或自定义安装路径
echo 3. 等待安装完成
echo.
echo 按任意键开始安装...
pause >nul

echo.
echo 正在启动安装程序...
start /wait "" "python-3.11.9-amd64.exe"

echo.
echo ========================================
echo 安装完成！
echo ========================================
echo.
echo [下一步]
echo 1. 关闭所有命令行窗口
echo 2. 重新打开命令行
echo 3. 运行以下命令验证安装：
echo    python --version
echo.
echo 如果显示 Python 3.11.9，说明安装成功！
echo 然后就可以运行 build_cx_clean.bat 进行打包了
echo.
pause

