@echo off
echo ========================================
echo Markdo 完整打包流程
echo ========================================
echo.

echo [0/4] 检查图标文件...
if not exist "Markdo.ico" (
    echo 未找到 Markdo.ico，正在生成...
    python create_icon.py
    if %ERRORLEVEL% NEQ 0 (
        echo ⚠️ 图标生成失败，将继续打包但可能没有图标
    )
) else (
    echo ✅ 图标文件已存在
)
echo.

echo [1/4] 清理旧的构建文件...
if exist "build" rmdir /s /q "build"
if exist "installer_cx" rmdir /s /q "installer_cx"
echo 清理完成
echo.

echo [2/4] 使用 cx_Freeze 打包应用程序...
python setup_cx.py build
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ cx_Freeze 打包失败！
    pause
    exit /b 1
)
echo ✅ cx_Freeze 打包成功！
echo.

echo [3/4] 使用 Inno Setup 创建安装程序...
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" "setup_cx.iss"
) else if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    "C:\Program Files\Inno Setup 6\ISCC.exe" "setup_cx.iss"
) else (
    echo ⚠️ 未找到 Inno Setup，请手动编译 setup_cx.iss
    echo 或者直接使用 build\exe.win-amd64-3.13\ 目录中的文件
)
echo.

echo ========================================
echo 打包完成！
echo ========================================
echo 可执行文件: build\exe.win-amd64-3.13\Markdo.exe
echo 安装程序: installer_cx\Markdo_Setup_CX_1.0.1.exe
echo ========================================
pause