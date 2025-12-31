# Markdo

一个基于 PyQt6 构建的现代化、轻量级 Markdown 编辑器，具有实时预览、多标签页编辑、智能补全和工具栏等功能，为您提供流畅的编辑体验。

[下载 Windows 版本](https://github.com/A8Z0RB-CN/Markdo/releases)

项目 QQ 群：329474729

## ✨ 核心功能

### 📝 编辑体验
- **实时预览**: 左右分屏布局，500ms 防抖延迟渲染，即时显示 Markdown 渲染效果
- **多标签页**: 支持同时打开多个文件，标签页可拖拽排序，高效切换
- **语法高亮**: 基于正则表达式的 Markdown 语法高亮，支持标题、粗体、斜体、代码、链接、表格等
- **智能补全**: 
  - **Tab 自动补全**: 渐进式补全成对符号（`*`、`_`、`~`、`=`、`` ` ``、`[]`、`()`、`{}`），支持层级扩展
  - **列表自动续接**: 回车时自动延续有序列表、无序列表、任务列表和引用块的格式
- **滚动同步**: 编辑器和预览窗口智能同步滚动位置

### 🎨 界面特性
- **悬浮工具栏**: 光标位置智能显示工具栏，4 个功能分组（基础、列表、插入、LaTeX）
- **主题系统**: 
  - 支持暗黑/明亮主题切换
  - 自动主题切换（根据时间段）
  - 多种内置主题可选
- **无边框窗口**: 现代化无边框设计，支持窗口拖拽和调整大小

### 🔧 实用功能
- **文件关联**: 支持将 `.md` 和 `.markdown` 文件关联到 Markdo
- **查找功能**: 快速查找文本内容
- **时间戳插入**: 一键插入当前时间戳
- **数学公式**: 完整的 LaTeX 数学公式支持（行内和块级），基于 MathJax
- **代码高亮**: 基于 Pygments 的代码块语法高亮
- **扩展语法**: 支持表格、删除线、高亮、脚注、目录、上下标等扩展 Markdown 语法

## 🚀 快速开始

### 环境要求

- Python 3.8 或更高版本
- Windows 10/11

### 安装步骤

1. 克隆仓库：
```bash
git clone https://github.com/A8Z0RB-CN/Markdo.git
cd Markdo
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 运行程序：
```bash
python main.py
```

## 📦 构建可执行文件

### 使用 Nuitka（推荐）

Nuitka 将 Python 代码编译为 C++，性能更好，启动更快。

#### 目录模式（推荐，启动快）
```bash
build_nuitka.bat
```
输出位置：`build_nuitka\main.dist\Markdo.exe`

#### 单文件模式（便携，启动慢）
```bash
build_nuitka_onefile.bat
```
输出位置：`build_nuitka\Markdo.exe`

**注意**: Windows 用户需要安装 Visual Studio Build Tools（包含 C++ 编译器）

### 使用 cx_Freeze（传统方式）

```bash
build_all.bat
```

这将：
1. 生成 `.ico` 图标文件（如需要）
2. 使用 cx_Freeze 打包应用
3. 使用 Inno Setup 创建 Windows 安装程序

安装程序将生成在 `installer_cx/` 目录中。

## 🛠️ 技术栈

- **框架**: PyQt6 + PyQt6-WebEngine
- **Markdown 解析器**: Python-Markdown 配合 pymdown-extensions
- **语法高亮**: Pygments
- **数学公式**: MathJax
- **打包工具**: Nuitka（推荐）/ cx_Freeze
- **安装程序**: Inno Setup

## 📝 Markdown 功能示例

### 基础格式化
- **粗体**: `**文本**`
- *斜体*: `*文本*`
- ~~删除线~~: `~~文本~~`
- ==高亮==: `==文本==`

### 数学公式
- 行内公式: `$E=mc^2$`
- 块级公式: `$$\int_0^\infty e^{-x}dx = 1$$`

### 代码块
````markdown
```python
def hello():
    print("Hello, Markdo!")
```
````

### 表格
| 功能 | 状态 |
|---------|--------|
| 预览 | ✅     |
| 导出  | ✅     |

### 列表自动续接
- 输入列表项后按回车，自动延续列表格式
- 空行结束列表

### Tab 自动补全
- 输入 `*` 后按 Tab → `**`
- 再按 Tab → `****`（最多 2 层）
- 输入 `[` 后按 Tab → `[]()`（光标在括号内）

## ⌨️ 键盘快捷键

### 文件操作
- `Ctrl+N`: 新建文件
- `Ctrl+O`: 打开文件
- `Ctrl+S`: 保存文件
- `Ctrl+Shift+S`: 另存为

### 编辑操作
- `Ctrl+Z`: 撤销
- `Ctrl+Y`: 重做（也可使用 `Ctrl+Shift+Z`）
- `Ctrl+A`: 全选
- `Ctrl+F`: 查找
- `Ctrl+Shift+C`: 复制全部内容

### 文本格式
- `Ctrl+B`: 粗体
- `Ctrl+I`: 斜体
- `Ctrl+D`: 删除线
- `Ctrl+H`: 高亮
- `Ctrl+``: 行内代码
- `Ctrl+1~6`: 标题 1~6

### 插入内容
- `Ctrl+K`: 插入链接
- `Ctrl+Shift+K`: 插入代码块
- `Ctrl+Q`: 插入引用
- `Ctrl+L`: 插入无序列表
- `Ctrl+Shift+L`: 插入有序列表
- `Ctrl+R`: 插入水平分割线
- `Ctrl+T`: 插入时间戳

### 工具栏
- `Ctrl+M`: 切换悬浮工具栏
- `Ctrl+;`: 切换悬浮工具栏（备用快捷键）

### 帮助
- `F1`: 显示快捷键帮助

**总计**: 27 个功能快捷键

## 📂 项目结构

```
Markdo/
├── main.py                      # 主程序入口（包含所有核心功能）
├── pyqt_webview.py              # WebEngine 预览组件（独立预览窗口）
├── requirements.txt             # Python 依赖
├── build_nuitka.bat             # Nuitka 目录模式打包脚本
├── build_nuitka_onefile.bat     # Nuitka 单文件模式打包脚本
├── build_all.bat                # cx_Freeze 打包脚本
├── setup_nuitka.iss             # Inno Setup 安装程序脚本（Nuitka）
├── setup_cx.iss                 # Inno Setup 安装程序脚本（cx_Freeze）
├── create_icon.py               # PNG 转 ICO 转换器
├── register_file_association.bat # 文件关联注册脚本
├── unregister_file_association.bat # 文件关联卸载脚本
├── FILE_ASSOCIATION_README.md   # 文件关联使用说明
├── NUITKA_BUILD_README.md       # Nuitka 打包详细说明
├── CHANGELOG.md                 # 更新日志
├── markdo-icon.png              # 应用图标（PNG）
└── Markdo.ico                   # 应用图标（ICO）
```

## 🔗 文件关联

Markdo 支持将 `.md` 和 `.markdown` 文件关联到应用程序。

### 自动注册（推荐）
运行打包目录中的 `register_file_association.bat` 脚本即可完成注册。

### 手动设置
1. 右键点击任意 `.md` 文件
2. 选择"属性" → "更改"
3. 浏览到 Markdo.exe 所在目录并选择它
4. 勾选"始终使用此应用打开.md文件"

### 卸载关联
运行 `unregister_file_association.bat` 脚本即可移除文件关联。

详细说明请参考 [FILE_ASSOCIATION_README.md](FILE_ASSOCIATION_README.md)

## ⚙️ 设置功能

- **主题切换**: 支持暗黑/明亮主题，可设置自动切换时间段
- **编辑器字体大小**: 可自定义编辑器字体大小
- **滚动同步**: 可启用/禁用编辑器和预览窗口的滚动同步
- **悬浮工具栏**: 可设置自动显示/隐藏和自定义快捷键
- **欢迎对话框**: 首次启动显示使用指南，可在设置中禁用

## 🤝 贡献

欢迎贡献代码！请随时提交 Pull Request。

## 📄 许可证

本项目采用 MIT 许可证开源。

## 🐛 已知问题

- 悬浮工具栏在点击格式化按钮后会自动关闭（开发中）
- 某些复杂 Markdown 语法可能需要优化渲染性能

## 📮 联系方式

如有问题或功能建议，请使用 [GitHub Issues](https://github.com/A8Z0RB-CN/Markdo/issues) 页面。

---

**享受 Markdown 编辑的乐趣！** ✨
