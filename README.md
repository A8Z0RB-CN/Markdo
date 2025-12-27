# Markdo

A modern, lightweight Markdown editor built with PyQt6, featuring real-time preview and floating toolbar for seamless editing experience.

**Version**: 1.0.3  
**Latest Update**: Enhanced keyboard shortcuts support

[download releases for Windows]
https://github.com/A8Z0RB-CN/Markdo/releases

project QQ group:329474729
## ✨ Features

- **Real-time Preview**: Instant Markdown rendering with split-pane view
- **Floating Toolbar**: Context-aware toolbar at cursor position for quick formatting
- **Math Support**: Full LaTeX math formula support (inline and block)
- **Code Highlighting**: Syntax highlighting powered by Pygments
- **Extended Markdown**: Support for tables, strikethrough, highlight, and more
- **Clean Interface**: Minimalist design with dark/light theme support

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Windows 10/11

### Installation

1. Clone the repository:
```bash
git clone https://github.com/A8Z0RB-CN/Markdo.git
cd Markdo
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

## 📦 Build Executable

To create a standalone executable:

```bash
build_all.bat
```

This will:
1. Generate `.ico` icon (if needed)
2. Package the app using cx_Freeze
3. Create Windows installer using Inno Setup

The installer will be available in `installer_cx/` directory.

## 🛠️ Tech Stack

- **Framework**: PyQt6 + PyQt6-WebEngine
- **Markdown Parser**: Python-Markdown with pymdown-extensions
- **Syntax Highlighting**: Pygments
- **Packaging**: cx_Freeze
- **Installer**: Inno Setup

## 📝 Markdown Features

### Basic Formatting
- **Bold**: `**text**`
- *Italic*: `*text*`
- ~~Strikethrough~~: `~~text~~`
- ==Highlight==: `==text==`

### Math Formulas
- Inline: `$E=mc^2$`
- Block: `$$\int_0^\infty e^{-x}dx = 1$$`

### Code Blocks
```python
def hello():
    print("Hello, Markdo!")
```

### Tables
| Feature | Status |
|---------|--------|
| Preview | ✅     |
| Export  | ✅     |

## ⌨️ Keyboard Shortcuts

> ✅ **v1.0.3 Update**: All shortcuts now work consistently both inside and outside the editor window!

### 文件操作
- `Ctrl+N`: New file
- `Ctrl+O`: Open file
- `Ctrl+S`: Save file
- `Ctrl+Shift+S`: Save as file

### 编辑操作
- `Ctrl+Z`: Undo
- `Ctrl+Y`: Redo (also `Ctrl+Shift+Z`)
- `Ctrl+A`: Select all
- `Ctrl+F`: Find
- `Ctrl+Shift+C`: Copy all content

### 文本格式
- `Ctrl+B`: Bold
- `Ctrl+I`: Italic
- `Ctrl+D`: Strikethrough
- `Ctrl+H`: Highlight
- `Ctrl+``: Inline code
- `Ctrl+1~6`: Heading 1~6

### 插入内容
- `Ctrl+K`: Insert link
- `Ctrl+Shift+K`: Insert code block
- `Ctrl+Q`: Insert quote
- `Ctrl+L`: Insert unordered list
- `Ctrl+Shift+L`: Insert ordered list
- `Ctrl+R`: Insert horizontal rule
- `Ctrl+T`: Insert timestamp

### 工具bar
- `Ctrl+M`: Toggle floating toolbar
- `Ctrl+;`: Toggle floating toolbar (alternative)

### 帮助
- `F1`: Show shortcuts help

## 📂 Project Structure

```
Markdo/
├── main.py              # Main application entry
├── pyqt_webview.py      # WebEngine preview component
├── requirements.txt     # Python dependencies
├── setup_cx.py          # cx_Freeze build configuration
├── setup_cx.iss         # Inno Setup installer script
├── build_all.bat        # Complete build script
├── create_icon.py       # PNG to ICO converter
├── Markdo.png           # Application icon (PNG)
└── Markdo.ico           # Application icon (ICO)
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the MIT License.

## 🐛 Known Issues

- Floating toolbar auto-closes after clicking formatting buttons (WIP)
- Clear function needs improvement

## 📮 Contact

For issues and feature requests, please use the [GitHub Issues](https://github.com/A8Z0RB-CN/Markdo/issues) page.






