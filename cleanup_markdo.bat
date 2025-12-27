@echo off
:: Markdo 手动清理脚本
:: 需要管理员权限运行

echo ========================================
echo Markdo 手动清理脚本
echo ========================================
echo.

:: 检查管理员权限
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [错误] 需要管理员权限运行此脚本
    echo 请右键点击此文件，选择"以管理员身份运行"
    pause
    exit /b 1
)

echo [1/5] 正在删除安装目录...
if exist "C:\Program Files\Markdo" (
    rd /s /q "C:\Program Files\Markdo" 2>nul
    if exist "C:\Program Files\Markdo" (
        echo [警告] 安装目录删除失败，可能正在被使用
    ) else (
        echo [成功] 安装目录已删除
    )
) else (
    echo [信息] 安装目录不存在
)
echo.

echo [2/5] 正在删除文件关联注册表项...
reg delete "HKCR\.md" /f >nul 2>&1
reg delete "HKCR\MarkdoMarkdownFile" /f >nul 2>&1
reg delete "HKCR\.markdown" /f >nul 2>&1
echo [成功] 文件关联注册表项已删除
echo.

echo [3/5] 正在删除卸载程序注册表项...
reg delete "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\A8Z0RB-Markdo-1.0.3" /f >nul 2>&1
echo [成功] 卸载程序注册表项已删除
echo.

echo [4/5] 正在删除用户注册表中的文件关联...
reg delete "HKCU\Software\Classes\.md\OpenWithProgids" /v "Markdo.md" /f >nul 2>&1
reg delete "HKCU\Software\Classes\Markdo.md" /f >nul 2>&1
reg delete "HKCU\Software\Classes\.md\OpenWithList\Markdo.exe" /f >nul 2>&1
reg delete "HKCU\Software\Classes\.markdown\OpenWithProgids" /v "Markdo.md" /f >nul 2>&1
reg delete "HKCU\Software\Classes\.markdown\OpenWithList\Markdo.exe" /f >nul 2>&1
reg delete "HKCU\Software\Classes\Applications\Markdo.exe" /f >nul 2>&1
reg delete "HKCU\Software\Classes\*\shell\Markdo" /f >nul 2>&1
echo [成功] 用户注册表中的文件关联已删除
echo.

echo [5/5] 正在删除快捷方式...
if exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Markdo" (
    rd /s /q "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Markdo" 2>nul
)
if exist "%PUBLIC%\Desktop\Markdo.lnk" (
    del /f /q "%PUBLIC%\Desktop\Markdo.lnk" 2>nul
)
if exist "%USERPROFILE%\Desktop\Markdo.lnk" (
    del /f /q "%USERPROFILE%\Desktop\Markdo.lnk" 2>nul
)
echo [成功] 快捷方式已删除
echo.

echo ========================================
echo 清理完成！
echo ========================================
echo.
pause

