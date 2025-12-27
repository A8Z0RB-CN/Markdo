@echo off
:: Markdo文件关联注册脚本
:: 管理员权限运行此脚本以注册.md文件关联

echo 正在注册Markdo文件关联...

:: 获取当前脚本所在目录
set "APP_DIR=%~dp0"
set "EXE_PATH=%APP_DIR%Markdo.exe"

:: 检查exe是否存在
if not exist "%EXE_PATH%" (
    echo 错误: 找不到 Markdo.exe
    echo 请确保此脚本与 Markdo.exe 在同一目录下
    pause
    exit /b 1
)

echo 找到程序: %EXE_PATH%

:: 注册.md文件关联
reg add "HKCU\Software\Classes\.md\OpenWithProgids" /v "Markdo.md" /t REG_SZ /d "" /f >nul 2>&1
reg add "HKCU\Software\Classes\Markdo.md" /ve /t REG_SZ /d "Markdown文件" /f >nul 2>&1
reg add "HKCU\Software\Classes\Markdo.md\DefaultIcon" /ve /t REG_SZ /d "\"%EXE_PATH%\",0" /f >nul 2>&1
reg add "HKCU\Software\Classes\Markdo.md\shell\open\command" /ve /t REG_SZ /d "\"%EXE_PATH%\" \"%%1\"" /f >nul 2>&1

:: 注册.markdown文件关联
reg add "HKCU\Software\Classes\.markdown\OpenWithProgids" /v "Markdo.md" /t REG_SZ /d "" /f >nul 2>&1

:: 添加到"打开方式"列表
reg add "HKCU\Software\Classes\.md\OpenWithList\Markdo.exe" /ve /t REG_SZ /d "" /f >nul 2>&1
reg add "HKCU\Software\Classes\.markdown\OpenWithList\Markdo.exe" /ve /t REG_SZ /d "" /f >nul 2>&1

:: 注册应用程序信息
reg add "HKCU\Software\Classes\Applications\Markdo.exe" /v "FriendlyAppName" /t REG_SZ /d "Markdo" /f >nul 2>&1
reg add "HKCU\Software\Classes\Applications\Markdo.exe\shell\open\command" /ve /t REG_SZ /d "\"%EXE_PATH%\" \"%%1\"" /f >nul 2>&1

:: 添加右键菜单
reg add "HKCU\Software\Classes\*\shell\Markdo" /ve /t REG_SZ /d "用 Markdo 编辑" /f >nul 2>&1
reg add "HKCU\Software\Classes\*\shell\Markdo" /v "Icon" /t REG_SZ /d "\"%EXE_PATH%\"" /f >nul 2>&1
reg add "HKCU\Software\Classes\*\shell\Markdo\command" /ve /t REG_SZ /d "\"%EXE_PATH%\" \"%%1\"" /f >nul 2>&1

echo.
echo ✓ 文件关联注册完成！
echo.
echo 现在你可以：
echo 1. 右键点击.md文件，选择"打开方式" - 可以看到Markdo
echo 2. 右键点击任意文件，可以看到"用 Markdo 编辑"选项
echo 3. 双击.md文件将使用Markdo打开（如果设置为默认）
echo.
echo 提示: 如需设置为默认打开方式，请右键.md文件 - 属性 - 更改，选择Markdo
echo.
pause
