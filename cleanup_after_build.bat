@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
echo ========================================
echo 清理打包后的不必要文件
echo ========================================
echo.

:: 查找打包输出目录
set BUILD_DIR=
for /d %%d in ("build\exe.win-amd64-*") do (
    set BUILD_DIR=%%d
)

if not defined BUILD_DIR (
    echo [错误] 未找到构建目录！
    echo 请先运行完整打包脚本
    pause
    exit /b 1
)

echo 找到构建目录: !BUILD_DIR!
echo.

set deleted_count=0
set deleted_size=0

:: ========== 删除测试和文档目录 ==========
echo [1/8] 删除测试和文档目录...
for %%d in (
    "!BUILD_DIR!\lib\test"
    "!BUILD_DIR!\lib\tests"
    "!BUILD_DIR!\lib\docs"
    "!BUILD_DIR!\lib\examples"
    "!BUILD_DIR!\lib\unittest"
    "!BUILD_DIR!\test"
    "!BUILD_DIR!\tests"
) do (
    if exist %%d (
        for /f %%s in ('powershell -Command "(Get-ChildItem -Path '%%d' -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum"') do set size=%%s
        rd /s /q %%d >nul 2>&1
        if !errorlevel! equ 0 (
            echo   ✓ 已删除: %%~nxd
            set /a deleted_count+=1
            if defined size set /a deleted_size+=!size!
        )
    )
)

:: ========== 删除 .pyc 和 .pyi 文件（但保留编码文件） ==========
echo [2/8] 删除 .pyc 和 .pyi 文件（保留编码文件）...
for /r "!BUILD_DIR!" %%f in (*.pyc *.pyi) do (
    if exist "%%f" (
        :: 检查是否是编码文件，如果是则跳过
        echo %%f | findstr /i "encodings" >nul
        if !errorlevel! neq 0 (
            for /f %%s in ('powershell -Command "(Get-Item '%%f' -ErrorAction SilentlyContinue).Length"') do set size=%%s
            del /q "%%f" >nul 2>&1
            if !errorlevel! equ 0 (
                set /a deleted_count+=1
                if defined size set /a deleted_size+=!size!
            )
        )
    )
)
echo   ✓ 已删除 .pyc 和 .pyi 文件（编码文件已保留）

:: ========== 删除文档和说明文件 ==========
echo [3/8] 删除文档和说明文件...
for %%f in (
    "!BUILD_DIR!\README.md"
    "!BUILD_DIR!\README.txt"
    "!BUILD_DIR!\LICENSE"
    "!BUILD_DIR!\LICENSE.txt"
    "!BUILD_DIR!\CHANGELOG.md"
    "!BUILD_DIR!\CHANGELOG.txt"
    "!BUILD_DIR!\AUTHORS"
    "!BUILD_DIR!\CONTRIBUTORS"
    "!BUILD_DIR!\*.rst"
    "!BUILD_DIR!\*.md"
) do (
    if exist %%f (
        for /f %%s in ('powershell -Command "(Get-Item '%%f' -ErrorAction SilentlyContinue).Length"') do set size=%%s
        del /q %%f >nul 2>&1
        if !errorlevel! equ 0 (
            echo   ✓ 已删除: %%~nxf
            set /a deleted_count+=1
            if defined size set /a deleted_size+=!size!
        )
    )
)

:: ========== 删除 PyQt6 不需要的模块 ==========
echo [4/8] 删除 PyQt6 不需要的模块...
for %%d in (
    "!BUILD_DIR!\lib\PyQt6\Qt6\plugins\audio"
    "!BUILD_DIR!\lib\PyQt6\Qt6\plugins\bearer"
    "!BUILD_DIR!\lib\PyQt6\Qt6\plugins\canbus"
    "!BUILD_DIR!\lib\PyQt6\Qt6\plugins\designer"
    "!BUILD_DIR!\lib\PyQt6\Qt6\plugins\geoservices"
    "!BUILD_DIR!\lib\PyQt6\Qt6\plugins\mediaservice"
    "!BUILD_DIR!\lib\PyQt6\Qt6\plugins\position"
    "!BUILD_DIR!\lib\PyQt6\Qt6\plugins\qmltooling"
    "!BUILD_DIR!\lib\PyQt6\Qt6\plugins\sceneparsers"
    "!BUILD_DIR!\lib\PyQt6\Qt6\plugins\sensorgestures"
    "!BUILD_DIR!\lib\PyQt6\Qt6\plugins\sensors"
    "!BUILD_DIR!\lib\PyQt6\Qt6\plugins\sqldrivers"
    "!BUILD_DIR!\lib\PyQt6\Qt6\plugins\texttospeech"
    "!BUILD_DIR!\lib\PyQt6\Qt6\plugins\virtualkeyboard"
    "!BUILD_DIR!\lib\PyQt6\Qt6\plugins\webview"
    "!BUILD_DIR!\lib\PyQt6\Qt6\qml"
    "!BUILD_DIR!\lib\PyQt6\Qt6\translations"
) do (
    if exist %%d (
        for /f %%s in ('powershell -Command "(Get-ChildItem -Path '%%d' -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum"') do set size=%%s
        rd /s /q %%d >nul 2>&1
        if !errorlevel! equ 0 (
            echo   ✓ 已删除: %%~nxd
            set /a deleted_count+=1
            if defined size set /a deleted_size+=!size!
        )
    )
)

:: ========== 删除 PyQt6 不需要的 DLL ==========
echo [5/8] 删除 PyQt6 不需要的 DLL...
echo 注意：保留 Qt6Network.dll 和 Qt6PrintSupport.dll（WebEngine 需要）
for %%f in (
    "!BUILD_DIR!\lib\PyQt6\Qt6\bin\Qt6Bluetooth*.dll"
    "!BUILD_DIR!\lib\PyQt6\Qt6\bin\Qt6DBus*.dll"
    "!BUILD_DIR!\lib\PyQt6\Qt6\bin\Qt6Designer*.dll"
    "!BUILD_DIR!\lib\PyQt6\Qt6\bin\Qt6Help*.dll"
    "!BUILD_DIR!\lib\PyQt6\Qt6\bin\Qt6Multimedia*.dll"
    "!BUILD_DIR!\lib\PyQt6\Qt6\bin\Qt6Nfc*.dll"
    "!BUILD_DIR!\lib\PyQt6\Qt6\bin\Qt6OpenGL*.dll"
    "!BUILD_DIR!\lib\PyQt6\Qt6\bin\Qt6Pdf*.dll"
    "!BUILD_DIR!\lib\PyQt6\Qt6\bin\Qt6Positioning*.dll"
    :: Qt6PrintSupport.dll 和 Qt6Network.dll 被 WebEngine 需要，不删除
    :: "!BUILD_DIR!\lib\PyQt6\Qt6\bin\Qt6PrintSupport*.dll"
    :: "!BUILD_DIR!\lib\PyQt6\Qt6\bin\Qt6Network*.dll"
    "!BUILD_DIR!\lib\PyQt6\Qt6\bin\Qt6Qml*.dll"
    "!BUILD_DIR!\lib\PyQt6\Qt6\bin\Qt6Quick*.dll"
    "!BUILD_DIR!\lib\PyQt6\Qt6\bin\Qt63DQuick*.dll"
    "!BUILD_DIR!\lib\PyQt6\Qt6\bin\Qt6RemoteObjects*.dll"
    "!BUILD_DIR!\lib\PyQt6\Qt6\bin\Qt6Sensors*.dll"
    "!BUILD_DIR!\lib\PyQt6\Qt6\bin\Qt6SerialPort*.dll"
    "!BUILD_DIR!\lib\PyQt6\Qt6\bin\Qt6SpatialAudio*.dll"
    "!BUILD_DIR!\lib\PyQt6\Qt6\bin\Qt6Sql*.dll"
    "!BUILD_DIR!\lib\PyQt6\Qt6\bin\Qt6StateMachine*.dll"
    "!BUILD_DIR!\lib\PyQt6\Qt6\bin\Qt6Svg*.dll"
    "!BUILD_DIR!\lib\PyQt6\Qt6\bin\Qt6Test*.dll"
    "!BUILD_DIR!\lib\PyQt6\Qt6\bin\Qt6TextToSpeech*.dll"
    "!BUILD_DIR!\lib\PyQt6\Qt6\bin\Qt6WebEngineQuick*.dll"
    "!BUILD_DIR!\lib\PyQt6\Qt6\bin\Qt6WebSockets*.dll"
    "!BUILD_DIR!\lib\PyQt6\Qt6\bin\Qt6WebView*.dll"
    "!BUILD_DIR!\lib\PyQt6\Qt6\bin\Qt6Xml*.dll"
) do (
    for %%g in (%%f) do (
        if exist %%g (
            :: 跳过 WebEngine 需要的 DLL
            echo %%g | findstr /i "Qt6Network Qt6PrintSupport" >nul
            if !errorlevel! neq 0 (
                for /f %%s in ('powershell -Command "(Get-Item '%%g' -ErrorAction SilentlyContinue).Length"') do set size=%%s
                del /q %%g >nul 2>&1
                if !errorlevel! equ 0 (
                    echo   ✓ 已删除: %%~nxg
                    set /a deleted_count+=1
                    if defined size set /a deleted_size+=!size!
                )
            )
        )
    )
)
echo   ✓ 已保留 Qt6Network.dll 和 Qt6PrintSupport.dll（WebEngine 需要）

:: ========== 删除不需要的 Python 标准库模块 ==========
echo [6/8] 删除不需要的 Python 标准库模块...
for %%d in (
    "!BUILD_DIR!\lib\email"
    "!BUILD_DIR!\lib\http"
    "!BUILD_DIR!\lib\xmlrpc"
    "!BUILD_DIR!\lib\multiprocessing"
    "!BUILD_DIR!\lib\concurrent"
    "!BUILD_DIR!\lib\asyncio"
    "!BUILD_DIR!\lib\sqlite3"
    "!BUILD_DIR!\lib\dbm"
    "!BUILD_DIR!\lib\bz2"
    "!BUILD_DIR!\lib\lzma"
    "!BUILD_DIR!\lib\tarfile"
    "!BUILD_DIR!\lib\gzip"
    "!BUILD_DIR!\lib\argparse"
    "!BUILD_DIR!\lib\pdb"
    "!BUILD_DIR!\lib\profile"
    "!BUILD_DIR!\lib\pstats"
    "!BUILD_DIR!\lib\timeit"
    "!BUILD_DIR!\lib\trace"
    "!BUILD_DIR!\lib\cProfile"
    "!BUILD_DIR!\lib\shelve"
    "!BUILD_DIR!\lib\queue"
    "!BUILD_DIR!\lib\copyreg"
    "!BUILD_DIR!\lib\pickletools"
    "!BUILD_DIR!\lib\xml\parsers"
    "!BUILD_DIR!\lib\xml\sax"
    "!BUILD_DIR!\lib\xml\dom"
    "!BUILD_DIR!\lib\json\tool"
    "!BUILD_DIR!\lib\ctypes\wintypes"
    "!BUILD_DIR!\lib\winreg"
    "!BUILD_DIR!\lib\msvcrt"
    "!BUILD_DIR!\lib\winsound"
    "!BUILD_DIR!\lib\calendar"
    "!BUILD_DIR!\lib\locale"
    "!BUILD_DIR!\lib\gettext"
    "!BUILD_DIR!\lib\readline"
    "!BUILD_DIR!\lib\rlcompleter"
) do (
    if exist %%d (
        for /f %%s in ('powershell -Command "(Get-ChildItem -Path '%%d' -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum"') do set size=%%s
        rd /s /q %%d >nul 2>&1
        if !errorlevel! equ 0 (
            echo   ✓ 已删除: %%~nxd
            set /a deleted_count+=1
            if defined size set /a deleted_size+=!size!
        )
    )
)

:: ========== 删除不需要的第三方库文件 ==========
echo [7/8] 删除不需要的第三方库文件...
for %%f in (
    "!BUILD_DIR!\lib\markdown\test_tools.py"
    "!BUILD_DIR!\lib\markdown\__main__.py"
    "!BUILD_DIR!\lib\pygments\cmdline.py"
    "!BUILD_DIR!\lib\pygments\sphinxext.py"
    "!BUILD_DIR!\lib\pygments\__main__.py"
) do (
    if exist %%f (
        for /f %%s in ('powershell -Command "(Get-Item '%%f' -ErrorAction SilentlyContinue).Length"') do set size=%%s
        del /q %%f >nul 2>&1
        if !errorlevel! equ 0 (
            echo   ✓ 已删除: %%~nxf
            set /a deleted_count+=1
            if defined size set /a deleted_size+=!size!
        )
    )
)

:: ========== 保留所有编码文件（不删除，避免编码错误） ==========
echo [8/9] 检查编码文件...
echo   ✓ 保留所有编码文件（避免 filesystem encoding 错误）

:: ========== 复制 Qt DLL 到可执行文件目录（解决 DLL 加载问题）==========
echo [9/9] 复制 Qt DLL 到可执行文件目录...
set QT_BIN_DIR=!BUILD_DIR!\lib\PyQt6\Qt6\bin
set EXE_DIR=!BUILD_DIR!

:: 复制 QtWebEngine 相关的 DLL
for %%dll in (
    Qt6WebEngineCore.dll
    Qt6WebEngineWidgets.dll
    Qt6Network.dll
    Qt6PrintSupport.dll
    Qt6WebChannel.dll
    Qt6Core.dll
    Qt6Gui.dll
    Qt6Widgets.dll
    Qt6ShaderTools.dll
) do (
    if exist "!QT_BIN_DIR!\%%dll" (
        copy /y "!QT_BIN_DIR!\%%dll" "!EXE_DIR!\" >nul 2>&1
        if !errorlevel! equ 0 (
            echo   ✓ 已复制: %%dll
        )
    )
)

:: 复制 QtWebEngine 资源文件
set QT_RESOURCES_DIR=!BUILD_DIR!\lib\PyQt6\Qt6\resources
set EXE_RESOURCES_DIR=!EXE_DIR!\resources

if exist "!QT_RESOURCES_DIR!" (
    if not exist "!EXE_RESOURCES_DIR!" mkdir "!EXE_RESOURCES_DIR!"
    xcopy /y /e /i "!QT_RESOURCES_DIR!\*" "!EXE_RESOURCES_DIR!\" >nul 2>&1
    if !errorlevel! equ 0 (
        echo   ✓ 已复制资源文件到 resources 目录
    )
)

echo   ✓ DLL 复制完成

echo.
echo ========================================
echo 清理完成！
echo ========================================
echo.
echo 共删除项目数: !deleted_count!
if !deleted_size! gtr 0 (
    powershell -Command "$mb = [math]::Round(!deleted_size! / 1MB, 2); Write-Host \"释放空间: $mb MB\""
)
echo.

:: 计算最终体积
powershell -Command "$size = (Get-ChildItem -Path '!BUILD_DIR!' -Recurse -File | Measure-Object -Property Length -Sum).Sum; $mb = [math]::Round($size / 1MB, 2); Write-Host \"最终打包目录大小: $mb MB\""
echo.

