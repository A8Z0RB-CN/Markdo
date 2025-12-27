@echo off
echo 正在生成最小化安装包...
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" /Q setup_cx_minimal.iss
if %ERRORLEVEL% EQU 0 (
    echo 安装包已成功生成！
    echo 位置：installer_cx_minimal\Markdo_Setup_v1.0.3_cx_minimal.exe
) else (
    echo 生成安装包时出错！
)
pause