# 打包文件检查脚本
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Markdo 打包文件检查" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$buildDir = "build\exe.win-amd64-3.13"
$errors = @()
$warnings = @()

# 检查构建目录
if (-not (Test-Path $buildDir)) {
    Write-Host "✗ 错误: 构建目录不存在: $buildDir" -ForegroundColor Red
    exit 1
}

Write-Host "[1/8] 检查可执行文件..." -ForegroundColor Yellow
if (Test-Path "$buildDir\Markdo.exe") {
    $exeSize = (Get-Item "$buildDir\Markdo.exe").Length / 1MB
    Write-Host "  ✓ Markdo.exe 存在 ($([math]::Round($exeSize, 2)) MB)" -ForegroundColor Green
} else {
    Write-Host "  ✗ Markdo.exe 不存在" -ForegroundColor Red
    $errors += "Markdo.exe 不存在"
}

Write-Host "[2/8] 检查资源文件..." -ForegroundColor Yellow
$resourceFiles = @(
    "markdo-icon.png",
    "register_file_association.bat",
    "unregister_file_association.bat",
    "FILE_ASSOCIATION_README.md"
)
foreach ($file in $resourceFiles) {
    if (Test-Path "$buildDir\$file") {
        Write-Host "  ✓ $file 存在" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $file 不存在" -ForegroundColor Red
        $errors += "$file 不存在"
    }
}

Write-Host "[3/8] 检查核心库..." -ForegroundColor Yellow
$libraries = @(
    "lib\PyQt6",
    "lib\markdown",
    "lib\pymdownx",
    "lib\pygments"
)
foreach ($lib in $libraries) {
    if (Test-Path "$buildDir\$lib") {
        Write-Host "  ✓ $lib 已包含" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $lib 未包含" -ForegroundColor Red
        $errors += "$lib 未包含"
    }
}

Write-Host "[4/8] 检查 Python 标准库..." -ForegroundColor Yellow
$stdlib = @(
    "lib\re",
    "lib\json",
    "lib\xml",
    "lib\pathlib"
)
foreach ($mod in $stdlib) {
    if (Test-Path "$buildDir\$mod") {
        Write-Host "  ✓ $mod 已包含" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ $mod 未包含（可能不需要）" -ForegroundColor Yellow
        $warnings += "$mod 未包含"
    }
}

Write-Host "[5/8] 检查必要的 DLL..." -ForegroundColor Yellow
$dlls = @(
    "python3.dll",
    "python313.dll"
)
foreach ($dll in $dlls) {
    if (Test-Path "$buildDir\$dll") {
        Write-Host "  ✓ $dll 存在" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ $dll 不存在（可能使用不同版本）" -ForegroundColor Yellow
        $warnings += "$dll 不存在"
    }
}

Write-Host "[6/8] 计算打包体积..." -ForegroundColor Yellow
$totalSize = (Get-ChildItem -Path $buildDir -Recurse -File | Measure-Object -Property Length -Sum).Sum
$totalMB = [math]::Round($totalSize / 1MB, 2)
Write-Host "  打包目录总大小: $totalMB MB ($totalSize 字节)" -ForegroundColor Cyan

Write-Host "[7/8] 检查排除的模块..." -ForegroundColor Yellow
$excludedModules = @(
    "lib\test",
    "lib\tests",
    "lib\tkinter"
)
foreach ($mod in $excludedModules) {
    if (Test-Path "$buildDir\$mod") {
        Write-Host "  ⚠ $mod 仍然存在（应该被排除）" -ForegroundColor Yellow
        $warnings += "$mod 应该被排除但存在"
    } else {
        Write-Host "  ✓ $mod 已正确排除" -ForegroundColor Green
    }
}

Write-Host "[8/8] 检查配置文件..." -ForegroundColor Yellow
if (Test-Path "setup_cx.py") {
    Write-Host "  ✓ setup_cx.py 存在" -ForegroundColor Green
    
    # 检查是否包含 pygments
    $content = Get-Content "setup_cx.py" -Raw
    if ($content -match "pygments") {
        Write-Host "  ✓ pygments 已在配置中" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ pygments 未在配置中（但可能自动包含）" -ForegroundColor Yellow
        $warnings += "pygments 未在配置中"
    }
    
    # 检查是否排除了 copyreg
    if ($content -match '"copyreg"') {
        Write-Host "  ✗ copyreg 仍在排除列表中（可能导致错误）" -ForegroundColor Red
        $errors += "copyreg 仍在排除列表中"
    } else {
        Write-Host "  ✓ copyreg 未在排除列表中" -ForegroundColor Green
    }
} else {
    Write-Host "  ✗ setup_cx.py 不存在" -ForegroundColor Red
    $errors += "setup_cx.py 不存在"
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
if ($errors.Count -eq 0) {
    Write-Host "✓ 检查完成，未发现错误" -ForegroundColor Green
    if ($warnings.Count -gt 0) {
        Write-Host "⚠ 发现 $($warnings.Count) 个警告（通常不影响运行）" -ForegroundColor Yellow
    }
} else {
    Write-Host "✗ 发现 $($errors.Count) 个错误" -ForegroundColor Red
    foreach ($error in $errors) {
        Write-Host "  - $error" -ForegroundColor Red
    }
}
Write-Host "========================================" -ForegroundColor Cyan



