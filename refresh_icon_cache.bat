@echo off
:: 刷新Windows图标缓存
echo ========================================
echo 清理Windows图标缓存
echo ========================================
echo.

echo 正在停止Windows资源管理器...
taskkill /f /im explorer.exe >nul 2>&1

echo 正在删除图标缓存...
cd /d "%userprofile%\AppData\Local"

:: 删除IconCache.db (Windows 7/8)
if exist IconCache.db (
    attrib -h IconCache.db
    del /f /q IconCache.db
    echo 已删除 IconCache.db
)

:: 删除图标缓存文件夹 (Windows 10/11)
if exist "Microsoft\Windows\Explorer\IconCache*" (
    attrib -h "Microsoft\Windows\Explorer\IconCache*"
    del /f /q "Microsoft\Windows\Explorer\IconCache*"
    echo 已删除 Windows 10/11 图标缓存
)

:: 删除缩略图缓存
if exist "Microsoft\Windows\Explorer\thumbcache*" (
    attrib -h "Microsoft\Windows\Explorer\thumbcache*"
    del /f /q "Microsoft\Windows\Explorer\thumbcache*"
    echo 已删除缩略图缓存
)

echo.
echo 正在重启Windows资源管理器...
start explorer.exe

echo.
echo ========================================
echo ✓ 图标缓存已清理！
echo ========================================
echo.
echo 图标现在应该会更新为最新版本。
echo 如果仍未更新，请尝试：
echo 1. 重启电脑
echo 2. 重新安装应用程序
echo.
pause
