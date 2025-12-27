"""
cx_Freeze 完整打包配置文件
先完整打包所有模块，然后通过清理脚本删除不必要的文件
"""
import sys
from cx_Freeze import setup, Executable

# 包含的文件和目录
include_files = [
    ("markdo-icon.png", "markdo-icon.png"),  # 图标文件
    ("register_file_association.bat", "register_file_association.bat"),  # 文件关联注册脚本
    ("unregister_file_association.bat", "unregister_file_association.bat"),  # 文件关联卸载脚本
    ("FILE_ASSOCIATION_README.md", "FILE_ASSOCIATION_README.md"),  # 文件关联说明文档
]

# 完整打包：包含所有可能需要的包（不排除）
packages = [
    # PyQt6 核心模块
    "PyQt6",
    "PyQt6.QtCore",
    "PyQt6.QtGui",
    "PyQt6.QtWidgets",
    "PyQt6.QtWebEngineWidgets",
    "PyQt6.QtWebEngineCore",
    "PyQt6.QtWebChannel",
    
    # Markdown 相关
    "markdown",
    "markdown.extensions",
    "markdown.extensions.extra",
    "markdown.extensions.tables",
    "markdown.extensions.fenced_code",
    "markdown.extensions.codehilite",
    "markdown.extensions.toc",
    "markdown.extensions.nl2br",
    "markdown.extensions.sane_lists",
    
    # pymdownx 扩展
    "pymdownx",
    "pymdownx.tilde",
    "pymdownx.caret",
    "pymdownx.mark",
    "pymdownx.arithmatex",
    
    # Pygments
    "pygments",
    
    # ========== 编码支持（解决 filesystem encoding 错误）==========
    "encodings",  # 编码包（必须）
    "encodings.utf_8",  # UTF-8 编码
    "encodings.cp1252",  # Windows 编码
    "encodings.latin_1",  # Latin-1 编码
    "encodings.mbcs",  # Windows 多字节编码
    "encodings.ascii",  # ASCII 编码
    "encodings.utf_16",  # UTF-16 编码
    "encodings.utf_16_be",  # UTF-16 BE
    "encodings.utf_16_le",  # UTF-16 LE
    "encodings.utf_32",  # UTF-32 编码
    
    # ========== 标准库核心模块（必需）==========
    "codecs",  # 编解码器（编码系统核心）
    "locale",  # 区域设置（影响编码）
    "sys",  # 系统模块
    "os",  # 操作系统接口
    "os.path",  # 路径操作
    "pathlib",  # 路径处理
    "io",  # 输入输出（文件操作需要）
    "collections",  # 集合类型
    "collections.abc",  # 集合抽象基类
    "copy",  # 对象复制
    "functools",  # 函数工具
    "itertools",  # 迭代器工具
    "operator",  # 操作符函数
    "types",  # 类型系统
    "weakref",  # 弱引用
    "warnings",  # 警告系统
    "inspect",  # 代码检查
    "importlib",  # 导入系统
    "importlib.util",  # 导入工具
    "importlib.machinery",  # 导入机制
    "pkgutil",  # 包工具
    "traceback",  # 错误追踪
    "html",  # HTML 转义
    "re",  # 正则表达式
    "datetime",  # 日期时间
    "urllib.parse",  # URL 解析
    "urllib.request",  # URL 请求
    "zipfile",  # ZIP 文件处理
    "logging",  # 日志系统
    "hashlib",  # 哈希算法
    "threading",  # 线程支持
    "select",  # 选择器
    "selectors",  # 选择器
]

# 最小排除：只排除明显不需要的
excludes = [
    # 测试和文档（这些肯定不需要）
    "tkinter",
    "unittest",
    "test",
    "tests",
    "pydoc",
    "doctest",
    "pydoc_data",
    
    # 包管理工具（不需要）
    "distutils",
    "setuptools",
    "pip",
    "wheel",
]

# 构建选项 - 完整打包模式
build_exe_options = {
    "packages": packages,
    "excludes": excludes,
    "include_files": include_files,
    "optimize": 2,  # 优化级别
    # 不排除任何 DLL，让 cx_Freeze 自动包含所有需要的
    "bin_excludes": [],
    "bin_includes": [],
    "bin_path_includes": [],
    "bin_path_excludes": [],
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
        shortcut_dir="ProgramMenuFolder",
    )
]

setup(
    name="Markdo",
    version="1.0.3",
    description="PyQt6 Markdown编辑器 - 完整打包版本",
    options={"build_exe": build_exe_options},
    executables=executables
)

