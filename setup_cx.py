"""
cx_Freeze 配置文件用于打包 Markdo 应用程序
"""
import sys
from cx_Freeze import setup, Executable

# 包含的文件和目录
include_files = [
    ("Markdo.png", "Markdo.png"),  # 图标文件
    ("pyqt_webview.py", "pyqt_webview.py"),  # 附加的模块
]

# 需要包含的包
packages = [
    "PyQt6",
    "PyQt6.QtCore",
    "PyQt6.QtGui",
    "PyQt6.QtWidgets",
    "PyQt6.QtWebEngineWidgets",
    "PyQt6.QtWebEngineCore",
    "PyQt6.QtWebChannel",
    "markdown",
    "markdown.extensions",
    "markdown.extensions.tables",
    "markdown.extensions.fenced_code",
    "markdown.extensions.codehilite",
    "markdown.extensions.toc",
    "markdown.extensions.nl2br",
    "markdown.extensions.sane_lists",
    "pymdownx",
    "pymdownx.tilde",
    "pymdownx.caret",
    "pymdownx.mark",
    "pygments",
    "pygments.lexers",
    "pygments.formatters",
    "pygments.styles",
]

# 需要排除的包（可选，减少包大小）
excludes = [
    "tkinter",
    "unittest",
    "pydoc",
    "doctest",
]

# 构建选项
build_exe_options = {
    "packages": packages,
    "excludes": excludes,
    "include_files": include_files,
    "optimize": 2,  # 优化级别
    "bin_excludes": [],  # 不排除任何二进制文件
    "bin_includes": [],  # 包含额外的二进制文件
    "bin_path_includes": [],  # 包含额外的二进制路径
    "bin_path_excludes": [],  # 排除二进制路径
}

# 可执行文件配置
base = None
if sys.platform == "win32":
    base = "gui"  # 无控制台窗口

executables = [
    Executable(
        "main.py",
        base=base,
        target_name="Markdo.exe",
        icon="Markdo.ico",  # 使用ICO格式图标
        shortcut_name="Markdo",
        shortcut_dir="ProgramMenuFolder"
    )
]

setup(
    name="Markdo",
    version="1.0.2",
    description="PyQt6 Markdown编辑器",
    options={"build_exe": build_exe_options},
    executables=executables
)