@echo off
:: Markdo文件关联卸载脚本
:: 移除Markdo的文件关联（静默模式，用于卸载程序）

:: 删除.md文件关联
reg delete "HKCU\Software\Classes\.md\OpenWithProgids" /v "Markdo.md" /f >nul 2>&1
reg delete "HKCU\Software\Classes\Markdo.md" /f >nul 2>&1
reg delete "HKCU\Software\Classes\.md\OpenWithList\Markdo.exe" /f >nul 2>&1

:: 删除.markdown文件关联
reg delete "HKCU\Software\Classes\.markdown\OpenWithProgids" /v "Markdo.md" /f >nul 2>&1
reg delete "HKCU\Software\Classes\.markdown\OpenWithList\Markdo.exe" /f >nul 2>&1

:: 删除应用程序信息
reg delete "HKCU\Software\Classes\Applications\Markdo.exe" /f >nul 2>&1

:: 删除右键菜单
reg delete "HKCU\Software\Classes\*\shell\Markdo" /f >nul 2>&1
