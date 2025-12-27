# Nuitka 打包指南

## 📦 使用 Nuitka 打包 Markdo

Nuitka 是一个 Python 编译器，可以将 Python 代码编译成可执行文件，性能通常比 cx_Freeze 更好。

## 🚀 快速开始

### 1. 安装 Nuitka

```bash
pip install nuitka
```

**Windows 用户还需要：**
- Visual Studio Build Tools（包含 C++ 编译器）
- 或安装 Visual Studio Community（包含 C++ 编译器）

### 2. 选择打包模式

#### 模式一：目录模式（推荐，启动快）

```bash
build_nuitka.bat
```

**特点：**
- ✅ 启动速度快
- ✅ 文件结构清晰
- ✅ 便于调试
- ❌ 需要分发整个目录

**输出位置：** `build\Markdo.dist\Markdo.exe`

#### 模式二：单文件模式（便携，启动慢）

```bash
build_nuitka_onefile.bat
```

**特点：**
- ✅ 单个可执行文件，便于分发
- ✅ 无需安装，直接运行
- ❌ 首次启动较慢（需要解压临时文件）
- ❌ 文件体积较大

**输出位置：** `build\Markdo.exe`

## 📋 打包前检查清单

- [ ] 已安装 Nuitka: `pip install nuitka`
- [ ] 已安装所有依赖: `pip install -r requirements.txt`
- [ ] Windows 用户已安装 Visual C++ 编译器
- [ ] `Markdo.ico` 或 `markdo-icon.ico` 图标文件存在
- [ ] 所有资源文件存在：
  - `markdo-icon.png`
  - `register_file_association.bat`（可选）
  - `unregister_file_association.bat`（可选）
  - `FILE_ASSOCIATION_README.md`（可选）

## 🔧 手动打包命令

如果脚本不满足需求，可以手动执行 Nuitka 命令：

### 目录模式

```bash
python -m nuitka ^
    --standalone ^
    --enable-plugin=pyqt6 ^
    --windows-disable-console ^
    --assume-yes-for-downloads ^
    --output-dir=build ^
    --output-filename=Markdo.exe ^
    --windows-icon-from-ico=Markdo.ico ^
    --include-data-file=markdo-icon.png=markdo-icon.png ^
    --include-module=markdown ^
    --include-module=markdown.extensions ^
    --include-module=pymdownx ^
    --include-module=pygments ^
    main.py
```

### 单文件模式

```bash
python -m nuitka ^
    --standalone ^
    --onefile ^
    --enable-plugin=pyqt6 ^
    --windows-disable-console ^
    --assume-yes-for-downloads ^
    --output-dir=build ^
    --output-filename=Markdo.exe ^
    --windows-icon-from-ico=Markdo.ico ^
    --include-data-file=markdo-icon.png=markdo-icon.png ^
    --include-module=markdown ^
    --include-module=markdown.extensions ^
    --include-module=pymdownx ^
    --include-module=pygments ^
    main.py
```

## 📊 对比：Nuitka vs cx_Freeze

| 特性 | Nuitka | cx_Freeze |
|------|--------|-----------|
| 性能 | ⭐⭐⭐⭐⭐ 编译为 C++，性能更好 | ⭐⭐⭐ 解释执行 |
| 启动速度 | ⭐⭐⭐⭐ 较快 | ⭐⭐⭐ 中等 |
| 文件大小 | ⭐⭐⭐ 中等 | ⭐⭐⭐⭐ 较小 |
| 打包速度 | ⭐⭐⭐ 较慢 | ⭐⭐⭐⭐ 较快 |
| 兼容性 | ⭐⭐⭐⭐ 良好 | ⭐⭐⭐⭐⭐ 优秀 |
| 调试难度 | ⭐⭐⭐ 中等 | ⭐⭐⭐⭐ 容易 |

## ⚠️ 注意事项

1. **PyQt6 WebEngine 支持**
   - Nuitka 需要 `--enable-plugin=pyqt6` 来正确支持 PyQt6
   - WebEngine 的资源文件会自动包含

2. **数据文件路径**
   - 打包后的数据文件位于可执行文件同目录
   - 代码已自动处理路径，无需修改

3. **首次运行**
   - Nuitka 首次运行可能需要下载依赖（使用 `--assume-yes-for-downloads` 自动确认）
   - 单文件模式首次启动会解压临时文件，可能较慢

4. **防病毒软件**
   - 某些防病毒软件可能误报 Nuitka 编译的程序
   - 这是误报，可以添加到白名单

## 🐛 常见问题

### Q: 打包失败，提示缺少编译器？

**A:** Windows 用户需要安装 Visual Studio Build Tools：
- 下载：https://visualstudio.microsoft.com/downloads/
- 选择 "Build Tools for Visual Studio"
- 安装时勾选 "C++ build tools"

### Q: 打包后的程序无法运行？

**A:** 检查以下几点：
1. 确保所有依赖已安装
2. 检查数据文件是否正确包含
3. 查看错误日志（如果有控制台窗口）

### Q: 单文件模式启动很慢？

**A:** 这是正常现象。单文件模式会在首次运行时解压临时文件到系统临时目录。如果希望启动更快，使用目录模式。

### Q: 如何减小文件大小？

**A:** 可以尝试：
1. 使用 `--remove-output` 清理临时文件
2. 排除不需要的模块（在脚本中添加 `--nofollow-import-to`）
3. 使用 UPX 压缩（需要额外安装）

## 📚 更多信息

- Nuitka 官方文档: https://nuitka.net/doc/
- PyQt6 插件文档: https://nuitka.net/doc/user-manual.html#pyqt6-plugin


