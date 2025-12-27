@echo off
chcp 65001 >nul
echo ========================================
echo 使用控制台模式测试程序（可以看到错误信息）
echo ========================================
echo.

cd build\exe.win-amd64-3.13

echo 正在运行程序（控制台模式）...
echo 如果程序有错误，将显示在下方：
echo.
echo ----------------------------------------

:: 尝试直接运行，看看是否有错误输出
python -c "import sys; sys.path.insert(0, 'lib'); import main; main.main()" 2>&1

echo.
echo ----------------------------------------
echo.

cd ..\..

pause



