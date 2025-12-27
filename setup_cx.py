"""
cx_Freeze 配置文件用于打包 Markdo 应用程序
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

# 需要包含的包（只包含实际使用的）
packages = [
    # PyQt6 核心模块（只包含实际使用的）
    "PyQt6",
    "PyQt6.QtCore",
    "PyQt6.QtGui",
    "PyQt6.QtWidgets",
    "PyQt6.QtWebEngineWidgets",
    "PyQt6.QtWebEngineCore",
    "PyQt6.QtWebChannel",  # WebEngine 可能需要
    
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
    
    # Pygments（codehilite 需要）
    "pygments",
    
    # 标准库（实际使用的）
    "html",  # HTML 转义（代码中使用）
    "pathlib",  # 路径处理
    "traceback",  # 错误追踪（代码中使用）
    "datetime",  # 日期时间
    "re",  # 正则表达式
    "os",  # 操作系统接口
    "os.path",  # 路径操作
    "sys",  # 系统相关
    
    # 可能被依赖库需要的标准库模块
    "urllib.parse",  # URL 解析（pymdownx 可能需要）
    "urllib.request",  # URL 请求（pymdownx 可能需要）
    "collections",  # 集合类型（PyQt6 可能需要）
    "collections.abc",  # 集合抽象基类
    "copy",  # 对象复制（PyQt6 可能需要）
    "functools",  # 函数工具（PyQt6 可能需要）
    "itertools",  # 迭代器工具（PyQt6 可能需要）
    "operator",  # 操作符函数（PyQt6 可能需要）
    "types",  # 类型系统（PyQt6 可能需要）
    "weakref",  # 弱引用（PyQt6 可能需要）
    "warnings",  # 警告系统
    "inspect",  # 代码检查（PyQt6 可能需要）
    "importlib",  # 导入系统（动态导入需要）
    "importlib.util",  # 导入工具
    "pkgutil",  # 包工具（动态导入需要）
    "encodings",  # 编码支持
    "encodings.utf_8",  # UTF-8 编码
    "encodings.cp1252",  # Windows 编码
    "encodings.latin_1",  # Latin-1 编码
    "zipfile",  # ZIP 文件处理（多个模块需要）
    "logging",  # 日志系统（多个模块需要）
    "hashlib",  # 哈希算法（多个模块需要）
    "threading",  # 线程支持（多个模块需要）
    "select",  # 选择器（subprocess 需要）
    "selectors",  # 选择器（subprocess 需要）
]

# 需要排除的包（减少包大小）
excludes = [
    # 测试和文档
    "tkinter",
    "unittest",
    "test",
    "tests",
    "pydoc",
    "doctest",
    "pydoc_data",
    
    # 包管理工具
    "distutils",
    "setuptools",
    "pip",
    "wheel",
    
    # 网络相关（不需要，但保留 urllib.parse 和 urllib.request）
    "email",
    "http",
    "http.client",
    "http.server",
    "http.cookiejar",
    "http.cookies",
    "xmlrpc",
    "xmlrpc.client",
    "xmlrpc.server",
    "urllib.robotparser",
    "urllib.response",
    "urllib.error",  # 排除错误处理（如果不需要）
    "smtplib",
    "ftplib",
    "poplib",
    "imaplib",
    "nntplib",
    
    # 并发和异步（不需要）
    "multiprocessing",
    "concurrent",
    "concurrent.futures",
    "asyncio",
    
    # 加密和安全（不需要）
    "ssl",
    "hmac",
    "secrets",
    
    # 压缩（不需要）
    "bz2",
    "lzma",
    "tarfile",
    "gzip",
    
    # 数据库（不需要）
    "sqlite3",
    "dbm",
    
    # 命令行工具（不需要）
    "argparse",
    "cmd",
    "curses",
    
    # 调试和性能分析（不需要）
    "pdb",
    "profile",
    "pstats",
    "timeit",
    "trace",
    "cProfile",
    
    # 其他工具（不需要）
    "shelve",
    "queue",
    "copyreg",
    "pickletools",
    
    # 线程相关（如果不需要）
    "_thread",
    
    # XML（如果不需要）
    "xml.parsers",
    "xml.sax",
    "xml.dom",
    
    # JSON 工具（不需要）
    "json.tool",
    
    # Windows 特定（不需要）
    "ctypes.wintypes",
    "winreg",
    "msvcrt",
    "winsound",
    
    # 其他
    "calendar",
    "locale",
    "gettext",
    "readline",
    "rlcompleter",
    
    # PyQt6 不需要的模块
    "PyQt6.QtBluetooth",
    "PyQt6.QtDBus",
    "PyQt6.QtDesigner",
    "PyQt6.QtHelp",
    "PyQt6.QtMultimedia",
    "PyQt6.QtMultimediaWidgets",
    "PyQt6.QtNetwork",
    "PyQt6.QtNfc",
    "PyQt6.QtOpenGL",
    "PyQt6.QtOpenGLWidgets",
    "PyQt6.QtPdf",
    "PyQt6.QtPdfWidgets",
    "PyQt6.QtPositioning",
    "PyQt6.QtPrintSupport",
    "PyQt6.QtQml",
    "PyQt6.QtQuick",
    "PyQt6.QtQuick3D",
    "PyQt6.QtQuickWidgets",
    "PyQt6.QtRemoteObjects",
    "PyQt6.QtSensors",
    "PyQt6.QtSerialPort",
    "PyQt6.QtSpatialAudio",
    "PyQt6.QtSql",
    "PyQt6.QtStateMachine",
    "PyQt6.QtSvg",
    "PyQt6.QtSvgWidgets",
    "PyQt6.QtTest",
    "PyQt6.QtTextToSpeech",
    "PyQt6.QtWebEngineQuick",
    "PyQt6.QtWebSockets",
    "PyQt6.QtXml",
    "PyQt6.lupdate",
    "PyQt6.uic",
]

# 构建选项
build_exe_options = {
    "packages": packages,
    "excludes": excludes,
    "include_files": include_files,
    "optimize": 2,  # 优化级别
    "bin_excludes": [
        # Windows API 集（系统自带，不需要打包）
        "api-ms-win-*.dll",
        # 其他不需要的 DLL
        "LIBPQ.dll",
        "MIMAPI64.dll",
        "OCI.dll",
        "WINSPOOL.DRV",
        "bthprops.cpl",
        "fbclient.dll",
        
        # PyQt6/Qt 不需要的模块 DLL
        "Qt6Bluetooth*.dll",
        "Qt6DBus*.dll",
        "Qt6Designer*.dll",
        "Qt6Help*.dll",
        "Qt6Multimedia*.dll",
        "Qt6Network*.dll",
        "Qt6Nfc*.dll",
        "Qt6OpenGL*.dll",
        "Qt6Pdf*.dll",
        "Qt6Positioning*.dll",
        "Qt6PrintSupport*.dll",
        "Qt6Qml*.dll",
        "Qt6Quick*.dll",
        "Qt63DQuick*.dll",
        "Qt6RemoteObjects*.dll",
        "Qt6Sensors*.dll",
        "Qt6SerialPort*.dll",
        "Qt6SpatialAudio*.dll",
        "Qt6Sql*.dll",
        "Qt6StateMachine*.dll",
        "Qt6Svg*.dll",
        "Qt6Test*.dll",
        "Qt6TextToSpeech*.dll",
        "Qt6WebEngineQuick*.dll",
        "Qt6WebSockets*.dll",
        "Qt6WebView*.dll",
        "Qt6Xml*.dll",
        
        # Qt 插件 DLL（不需要的）
        "qminimal.dll",  # 最小平台（不需要）
        "qoffscreen.dll",  # 离屏平台（不需要）
    ],
    "bin_includes": [],  # 包含额外的二进制文件
    "bin_path_includes": [],  # 包含额外的二进制路径
    "bin_path_excludes": [
        # 排除 PyQt6 不需要的路径
        "PyQt6/Qt6/plugins/audio",
        "PyQt6/Qt6/plugins/bearer",
        "PyQt6/Qt6/plugins/canbus",
        "PyQt6/Qt6/plugins/designer",
        "PyQt6/Qt6/plugins/geoservices",
        "PyQt6/Qt6/plugins/mediaservice",
        "PyQt6/Qt6/plugins/position",
        "PyQt6/Qt6/plugins/qmltooling",
        "PyQt6/Qt6/plugins/sceneparsers",
        "PyQt6/Qt6/plugins/sensorgestures",
        "PyQt6/Qt6/plugins/sensors",
        "PyQt6/Qt6/plugins/sqldrivers",
        "PyQt6/Qt6/plugins/texttospeech",
        "PyQt6/Qt6/plugins/virtualkeyboard",
        "PyQt6/Qt6/plugins/webview",
        "PyQt6/Qt6/qml",  # QML 文件（不需要）
        "PyQt6/Qt6/translations",  # 翻译文件（如果不需要多语言）
    ],
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
        # 添加文件关联信息
        # Windows会在安装时自动处理这些关联
    )
]

setup(
    name="Markdo",
    version="1.0.3",
    description="PyQt6 Markdown编辑器 - 增强快捷键支持",
    options={"build_exe": build_exe_options},
    executables=executables
)