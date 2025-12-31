"""
Markdo - PyQt6
提供更好的HTML/CSS渲染支持
"""
from sys import executable, argv, exit
import sys  # 保留用于 getattr(sys, 'frozen')
import os

# 禁用Qt调试输出（在导入Qt之前设置）
os.environ['QT_LOGGING_RULES'] = '*.debug=false;qt.qpa.window=false'

from markdown import markdown
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QTabWidget, QToolBar, QPushButton, QFileDialog,
    QMessageBox, QSplitter, QLabel, QStatusBar, QMenuBar, QMenu,
    QDialog, QGridLayout, QGroupBox, QToolButton, QCheckBox, QComboBox,
    QLineEdit, QSpinBox, QRadioButton, QButtonGroup, QScrollArea, QSizePolicy, QTimeEdit,
    QGraphicsOpacityEffect, QFrame
)
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPoint, QSettings, QUrl, QObject, QRect, QTime, QPropertyAnimation, QEasingCurve, QSequentialAnimationGroup, QEvent, QVariantAnimation, QAbstractAnimation, QThread
from PyQt6.QtGui import QFont, QColor, QAction, QKeySequence, QTextCursor, QShortcut, QSyntaxHighlighter, QTextCharFormat, QPalette, QIcon, QMouseEvent, QPainter, QPen, QCursor, QTextDocument, QSurfaceFormat, QRegion, QScreen
from re import compile, match, sub, IGNORECASE
from os.path import dirname, abspath, join, exists
from os import getcwd
from datetime import datetime
import traceback
import logging


# ==================== 日志系统 ====================
def setup_logging():
    """设置日志系统"""
    try:
        # 确定日志文件路径
        if getattr(sys, 'frozen', False):
            # 打包后的环境：日志文件在可执行文件同目录
            log_dir = dirname(executable)
            if not exists(log_dir):
                log_dir = getcwd()
        else:
            # 开发环境：日志文件在脚本同目录
            log_dir = dirname(abspath(__file__))
        
        log_file = join(log_dir, 'markdo_crash.log')
        
        # 配置日志格式
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()  # 同时输出到控制台
            ]
        )
        
        logger = logging.getLogger('Markdo')
        logger.info(f"日志系统初始化完成，日志文件: {log_file}")
        return logger
    except Exception as e:
        # 如果日志初始化失败，至少尝试写入一个简单的错误文件
        try:
            error_file = join(getcwd(), 'markdo_error.txt')
            with open(error_file, 'w', encoding='utf-8') as f:
                f.write(f"日志初始化失败: {e}\n")
                traceback.print_exc(file=f)
        except:
            pass
        return None

# 初始化日志系统
logger = setup_logging()

def log_exception(exc_type, exc_value, exc_traceback, context=""):
    """记录异常信息到日志文件"""
    try:
        if logger:
            logger.error(f"异常发生 {context}:", exc_info=(exc_type, exc_value, exc_traceback))
        else:
            # 如果日志系统未初始化，直接写入文件
            error_file = join(getcwd(), 'markdo_error.txt')
            with open(error_file, 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*60}\n")
                f.write(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                if context:
                    f.write(f"上下文: {context}\n")
                f.write(f"异常类型: {exc_type.__name__}\n")
                f.write(f"异常信息: {exc_value}\n")
                f.write("堆栈跟踪:\n")
                traceback.print_exception(exc_type, exc_value, exc_traceback, file=f)
                f.write(f"{'='*60}\n")
    except Exception as e:
        # 如果连日志写入都失败，至少打印到控制台
        print(f"无法写入日志: {e}")
        traceback.print_exception(exc_type, exc_value, exc_traceback)

def exception_handler(exc_type, exc_value, exc_traceback):
    """全局异常处理器"""
    if issubclass(exc_type, KeyboardInterrupt):
        # 忽略键盘中断
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    # 记录异常
    log_exception(exc_type, exc_value, exc_traceback, "全局异常处理器")
    
    # 调用默认异常处理器
    sys.__excepthook__(exc_type, exc_value, exc_traceback)

# 设置全局异常处理器
sys.excepthook = exception_handler


# ==================== 工具函数 ====================
# 全局帧率设置（在 main() 中初始化）
_ui_fps = 60  # UI 动画帧率，默认 60fps
_data_fps = 30  # 数据动画帧率，默认 30fps
_ui_update_interval = 16  # UI 动画更新间隔（ms），默认 16ms (60fps)
_data_update_interval = 33  # 数据动画更新间隔（ms），默认 33ms (30fps)

# ==================== 常量定义 ====================
# 窗口相关常量
DEFAULT_WINDOW_WIDTH = 1200
DEFAULT_WINDOW_HEIGHT = 750
MIN_WINDOW_WIDTH = 500
MIN_WINDOW_HEIGHT = 650
SMALL_WINDOW_THRESHOLD = 900  # 小窗口模式阈值（像素）

# 动画相关常量
WINDOW_FADE_DURATION = 300  # 窗口淡入淡出动画时长（ms）
DIALOG_FADE_DURATION = 250  # 对话框淡入淡出动画时长（ms）
TOOLBAR_FADE_DURATION = 200  # 工具栏淡入淡出动画时长（ms）
THEME_SWITCH_DURATION = 600  # 主题切换动画时长（ms），华丽的过渡效果
THEME_SWITCH_FADE_DURATION = 400  # 主题切换淡入淡出时长（ms）

# 定时器相关常量
THEME_CHECK_INTERVAL = 60000  # 主题检查间隔（ms），1分钟
PREVIEW_UPDATE_DELAY = 500  # 预览更新延迟（ms），防抖时间

# 工具栏相关常量
TOOLBAR_BUTTON_SIZE = 42  # 工具栏按钮大小（像素）
TOOLBAR_BUTTON_SPACING = 4  # 工具栏按钮间距（像素）
RESIZE_BORDER_WIDTH = 5  # 窗口边缘检测宽度（像素）

# 默认值
DEFAULT_REFRESH_RATE = 60  # 默认刷新率（Hz）
DEFAULT_NIGHT_START = "18:00"  # 默认黑夜模式开始时间
DEFAULT_NIGHT_END = "06:00"  # 默认黑夜模式结束时间
DEFAULT_EDITOR_FONT_SIZE = 15  # 默认编辑器字号
DEFAULT_TOOLBAR_HOTKEY = "Ctrl+;"  # 默认工具栏快捷键

def get_screen_refresh_rate():
    """获取主显示器刷新率（Hz）"""
    try:
        app = QApplication.instance()
        if app:
            primary_screen = app.primaryScreen()
            if primary_screen:
                refresh_rate = primary_screen.refreshRate()
                # 如果刷新率无效（通常为 -1），使用默认值 60Hz
                if refresh_rate > 0:
                    return refresh_rate
    except (AttributeError, RuntimeError, TypeError):
        pass
    return DEFAULT_REFRESH_RATE

def init_animation_frame_rates():
    """初始化动画帧率设置，匹配显示器刷新率"""
    global _ui_fps, _data_fps, _ui_update_interval, _data_update_interval
    
    refresh_rate = get_screen_refresh_rate()
    
    # UI 动画：匹配显示器刷新率（通常为 60Hz、120Hz 等）
    _ui_fps = refresh_rate
    _ui_update_interval = int(1000 / refresh_rate)  # 转换为毫秒
    
    # 数据动画：固定为 30fps（或显示器刷新率的一半，取较小值）
    _data_fps = min(30, refresh_rate // 2) if refresh_rate >= 60 else refresh_rate
    _data_update_interval = int(1000 / _data_fps)
    
    # 确保更新间隔至少为 8ms（最高 125fps）
    _ui_update_interval = max(8, _ui_update_interval)
    _data_update_interval = max(8, _data_update_interval)

def get_icon_path(filename):
    """获取图标文件路径"""
    try:
        if getattr(sys, 'frozen', False):
            # 打包后的可执行文件（Nuitka 或 cx_Freeze）
            # 打包后，数据文件在可执行文件所在目录
            application_path = dirname(executable)
            # 确保路径存在
            if not exists(application_path):
                application_path = dirname(abspath(executable))
            # 如果还是不存在，尝试使用 sys._MEIPASS（PyInstaller）或当前目录
            if not exists(application_path):
                # Nuitka 打包后，资源文件在可执行文件同目录
                # 尝试使用可执行文件的目录
                try:
                    if hasattr(sys, '_MEIPASS'):
                        # PyInstaller 打包
                        application_path = sys._MEIPASS
                    else:
                        # Nuitka 或其他打包方式
                        application_path = getcwd()
                except:
                    application_path = getcwd()
        else:
            # 开发环境
            application_path = dirname(abspath(__file__))
        
        # 构建完整路径
        full_path = join(application_path, filename)
        
        # 如果文件不存在，尝试在当前工作目录查找（开发环境备用）
        if not exists(full_path) and not getattr(sys, 'frozen', False):
            cwd_path = join(getcwd(), filename)
            if exists(cwd_path):
                return cwd_path
        
        return full_path
    except Exception as e:
        # 如果出现任何错误，返回文件名本身，让调用者处理
        import traceback
        print(f"Warning: Error getting icon path for {filename}: {e}")
        traceback.print_exc()
        return filename


def get_app_icon():
    """获取应用图标"""
    try:
        icon_path = get_icon_path('markdo-icon.png')
        if exists(icon_path):
            icon = QIcon(icon_path)
            # 验证图标是否有效
            if not icon.isNull():
                return icon
        
        # 如果找不到，尝试其他可能的文件名
        fallback_path = get_icon_path('Markdo.png')
        if exists(fallback_path):
            icon = QIcon(fallback_path)
            if not icon.isNull():
                return icon
        
        # 尝试查找 .ico 文件
        ico_path = get_icon_path('Markdo.ico')
        if exists(ico_path):
            icon = QIcon(ico_path)
            if not icon.isNull():
                return icon
        
        # 如果都找不到，返回空图标（不会导致崩溃）
        return QIcon()
    except Exception as e:
        # 如果出现任何错误，返回空图标，避免崩溃
        import traceback
        print(f"Warning: Error loading app icon: {e}")
        traceback.print_exc()
        return QIcon()


# ==================== 主题系统 ====================
class Theme:
    """主题配置"""
    # 黑夜主题
    DARK = {
        'name': 'dark',
        'display_name': '橙黑',
        'is_dark': True,
        'bg': '#1a1a1a',  # 主背景：更深的灰色，减少刺眼感
        'bg_secondary': '#252525',  # 次要背景：稍浅但仍柔和的深灰色
        'bg_tertiary': '#2d2d2d',  # 三级背景：柔和的灰色
        'text': '#d0d0d0',  # 文字：柔和的浅灰色，不刺眼
        'text_secondary': '#a0a0a0',  # 次要文字：中等灰色
        'accent': '#e67e22',  # 主色：稍暗的橙色，更柔和
        'accent_hover': '#f39c12',  # 悬停：稍亮的橙色但仍柔和
        'accent_text': '#ffffff',  # 辅助色：白色（用于按钮文字）
        'border': '#3a3a3a',  # 边框：柔和的深灰色，降低对比度
        'editor_bg': '#1a1a1a',  # 编辑器背景：与主背景一致
        'editor_text': '#d0d0d0',  # 编辑器文字：柔和的浅灰色
        'toolbar_bg': '#252525',  # 工具栏背景：次要背景
        'status_bg': '#2d2d2d',  # 状态栏背景：三级背景
        'status_text': '#d0d0d0',  # 状态栏文字：柔和的浅灰色
        'success': '#4ade80',
        'warning': '#fbbf24',
        'error': '#f87171',
        'shadow': 'rgba(0, 0, 0, 0.4)',
    }
    
    # 黑夜主题 - Discord风格
    DISCORD = {
        'name': 'discord',
        'display_name': 'Discord',
        'is_dark': True,
        'bg': '#36393f',  # Discord主背景
        'bg_secondary': '#2f3136',  # 侧边栏背景
        'bg_tertiary': '#202225',  # 更深的背景
        'text': '#dcddde',  # Discord文字颜色
        'text_secondary': '#96989d',  # 次要文字
        'accent': '#5865f2',  # Discord Blurple蓝紫色
        'accent_hover': '#4752c4',  # 悬停时稍深
        'accent_text': '#ffffff',  # 白色文字
        'border': '#42454a',  # 边框颜色
        'editor_bg': '#36393f',  # 编辑器背景
        'editor_text': '#dcddde',  # 编辑器文字
        'toolbar_bg': '#2f3136',  # 工具栏背景
        'status_bg': '#202225',  # 状态栏背景
        'status_text': '#dcddde',  # 状态栏文字
        'success': '#3ba55d',  # Discord绿色
        'warning': '#faa81a',  # Discord黄色
        'error': '#ed4245',  # Discord红色
        'shadow': 'rgba(0, 0, 0, 0.5)',
    }
    
    # 黑夜主题 - VSCode风格
    VSCODE = {
        'name': 'vscode',
        'display_name': 'VSCode',
        'is_dark': True,
        'bg': '#1e1e1e',  # VSCode Dark+主背景
        'bg_secondary': '#252526',  # 侧边栏背景
        'bg_tertiary': '#333333',  # 活动栏背景
        'text': '#d4d4d4',  # VSCode文字颜色
        'text_secondary': '#858585',  # 次要文字
        'accent': '#007acc',  # VSCode蓝色
        'accent_hover': '#0098ff',  # 悬停时稍亮
        'accent_text': '#ffffff',  # 白色文字
        'border': '#3c3c3c',  # 边框颜色
        'editor_bg': '#1e1e1e',  # 编辑器背景
        'editor_text': '#d4d4d4',  # 编辑器文字
        'toolbar_bg': '#252526',  # 工具栏背景
        'status_bg': '#1e1e1e',  # 状态栏背景（与背景相同深灰色）
        'status_text': '#ffffff',  # 状态栏文字
        'success': '#4ec9b0',  # VSCode青色
        'warning': '#dcdcaa',  # VSCode黄色
        'error': '#f14c4c',  # VSCode红色
        'shadow': 'rgba(0, 0, 0, 0.5)',
    }
    
    # 白天主题 - 莫兰迪粉灰
    MORANDI_PINK = {
        'name': 'morandi_pink',
        'display_name': '莫兰迪粉灰',
        'is_dark': False,
        'bg': '#f5f0ed',  # 柔和的粉灰色背景
        'bg_secondary': '#e8e3df',  # 稍深的粉灰色
        'bg_tertiary': '#ddd8d4',  # 再深一点的粉灰
        'text': '#5a5654',  # 深灰褐色文字
        'text_secondary': '#9a918c',  # 中灰色文字
        'accent': '#b8a398',  # 莫兰迪粉褐色
        'accent_hover': '#a89388',  # 略深的粉褐色
        'accent_text': '#ffffff',  # 白色文字
        'border': '#d5ccc7',  # 柔和的边框
        'editor_bg': '#f5f0ed',  # 编辑器背景
        'editor_text': '#5a5654',  # 编辑器文字
        'toolbar_bg': '#e8e3df',  # 工具栏背景
        'status_bg': '#ddd8d4',  # 状态栏背景
        'status_text': '#5a5654',  # 状态栏文字
        'success': '#8ba888',
        'warning': '#d4b896',
        'error': '#c19b9b',
        'shadow': 'rgba(0, 0, 0, 0.08)',
    }
    
    # 白天主题 - 莫兰迪蓝灰
    MORANDI_BLUE = {
        'name': 'morandi_blue',
        'display_name': '莫兰迪蓝灰',
        'is_dark': False,
        'bg': '#e8eff2',  # 柔和的蓝灰色背景
        'bg_secondary': '#dce5e9',  # 稍深的蓝灰色
        'bg_tertiary': '#d0dade',  # 再深一点的蓝灰
        'text': '#4a5559',  # 深灰蓝色文字
        'text_secondary': '#8a9599',  # 中灰蓝色文字
        'accent': '#8fa8b0',  # 莫兰迪蓝灰色
        'accent_hover': '#7f98a0',  # 略深的蓝灰色
        'accent_text': '#ffffff',  # 白色文字
        'border': '#c8d5d9',  # 柔和的边框
        'editor_bg': '#e8eff2',  # 编辑器背景
        'editor_text': '#4a5559',  # 编辑器文字
        'toolbar_bg': '#dce5e9',  # 工具栏背景
        'status_bg': '#d0dade',  # 状态栏背景
        'status_text': '#4a5559',  # 状态栏文字
        'success': '#88a898',
        'warning': '#c4b896',
        'error': '#b89b9b',
        'shadow': 'rgba(0, 0, 0, 0.08)',
    }
    
    # 白天主题 - 莫兰迪绿灰
    MORANDI_GREEN = {
        'name': 'morandi_green',
        'display_name': '莫兰迪绿灰',
        'is_dark': False,
        'bg': '#eff2ed',  # 柔和的绿灰色背景
        'bg_secondary': '#e3e9e0',  # 稍深的绿灰色
        'bg_tertiary': '#d7ded4',  # 再深一点的绿灰
        'text': '#4f5954',  # 深灰绿色文字
        'text_secondary': '#8f9994',  # 中灰绿色文字
        'accent': '#99aa9a',  # 莫兰迪绿灰色
        'accent_hover': '#899a8a',  # 略深的绿灰色
        'accent_text': '#ffffff',  # 白色文字
        'border': '#ccd9cd',  # 柔和的边框
        'editor_bg': '#eff2ed',  # 编辑器背景
        'editor_text': '#4f5954',  # 编辑器文字
        'toolbar_bg': '#e3e9e0',  # 工具栏背景
        'status_bg': '#d7ded4',  # 状态栏背景
        'status_text': '#4f5954',  # 状态栏文字
        'success': '#88a898',
        'warning': '#c4b896',
        'error': '#b89b9b',
        'shadow': 'rgba(0, 0, 0, 0.08)',
    }
    
    # 白天主题 - 莫兰迪米色
    MORANDI_BEIGE = {
        'name': 'morandi_beige',
        'display_name': '莫兰迪米色',
        'is_dark': False,
        'bg': '#f2f0eb',  # 柔和的米色背景
        'bg_secondary': '#e9e5df',  # 稍深的米色
        'bg_tertiary': '#ddd9d3',  # 再深一点的米色
        'text': '#5a5954',  # 深灰褐色文字
        'text_secondary': '#9a9994',  # 中灰色文字
        'accent': '#afa898',  # 莫兰迪米灰色
        'accent_hover': '#9f9888',  # 略深的米灰色
        'accent_text': '#ffffff',  # 白色文字
        'border': '#d9d5cf',  # 柔和的边框
        'editor_bg': '#f2f0eb',  # 编辑器背景
        'editor_text': '#5a5954',  # 编辑器文字
        'toolbar_bg': '#e9e5df',  # 工具栏背景
        'status_bg': '#ddd9d3',  # 状态栏背景
        'status_text': '#5a5954',  # 状态栏文字
        'success': '#98a888',
        'warning': '#d4c896',
        'error': '#c19b9b',
        'shadow': 'rgba(0, 0, 0, 0.08)',
    }
    
    LIGHT = {
        'name': 'light',
        'display_name': '素白',
        'is_dark': False,
        'bg': '#ffffff',  # 白色为主
        'bg_secondary': '#f5f7fa',  # 浅灰白
        'bg_tertiary': '#e8ecf0',  # 更浅的灰白
        'text': '#1e293b',  # 深色文字
        'text_secondary': '#64748b',  # 灰色文字
        'accent': '#6b8fd4',  # 略低饱和度的蓝色为辅
        'accent_hover': '#5a7fc4',  # 稍深的蓝色
        'accent_text': '#ffffff',  # 白色文字
        'border': '#d1d9e3',  # 浅灰边框
        'editor_bg': '#ffffff',  # 纯白编辑器背景
        'editor_text': '#1e293b',  # 深色文字
        'toolbar_bg': '#f5f7fa',  # 工具栏背景
        'status_bg': '#e8ecf0',  # 状态栏背景
        'status_text': '#475569',  # 深灰文字
        'success': '#22c55e',
        'warning': '#f59e0b',
        'error': '#ef4444',
        'shadow': 'rgba(0, 0, 0, 0.1)',
    }
    
    @staticmethod
    def get_theme(name):
        """根据主题名称获取主题配置"""
        themes = {
            'dark': Theme.DARK,
            'discord': Theme.DISCORD,
            'vscode': Theme.VSCODE,
            'light': Theme.LIGHT,
            'morandi_pink': Theme.MORANDI_PINK,
            'morandi_blue': Theme.MORANDI_BLUE,
            'morandi_green': Theme.MORANDI_GREEN,
            'morandi_beige': Theme.MORANDI_BEIGE,
        }
        return themes.get(name, Theme.DARK)
    
    @staticmethod
    def get_all_themes():
        """获取所有主题列表"""
        return [
            Theme.DARK,
            Theme.DISCORD,
            Theme.VSCODE,
            Theme.LIGHT,
            Theme.MORANDI_PINK,
            Theme.MORANDI_BLUE,
            Theme.MORANDI_GREEN,
            Theme.MORANDI_BEIGE,
        ]
    
    @staticmethod
    def get_light_themes():
        """获取所有白天主题"""
        return [theme for theme in Theme.get_all_themes() if not theme.get('is_dark', False)]
    
    @staticmethod
    def get_dark_themes():
        """获取所有黑夜主题"""
        return [theme for theme in Theme.get_all_themes() if theme.get('is_dark', False)]
    
    @staticmethod
    def get_app_stylesheet(theme):
        """生成应用级样式表"""
        return f"""
            QMainWindow {{
                background-color: {theme['bg']};
            }}
            QWidget {{
                background-color: {theme['bg']};
                color: {theme['text']};
                font-family: 'Microsoft YaHei', '微软雅黑', 'Segoe UI', sans-serif;
                font-size: 14px;
            }}
            QMenuBar {{
                background-color: {theme['bg_secondary']};
                color: {theme['text']};
                border: none;
                padding: 2px;
                font-size: 13px;
            }}
            QMenuBar::item:selected {{
                background-color: {theme['accent']};
                color: {theme['accent_text']};
                border-radius: 0;
                padding: 2px 8px;
            }}
            QMenu {{
                background-color: {theme['bg_secondary']};
                color: {theme['text']};
                border: none;
                border-radius: 0;
                padding: 4px;
            }}
            QMenu::item {{
                padding: 6px 20px;
                border-radius: 0;
            }}
            QMenu::item:selected {{
                background-color: {theme['accent']};
                color: {theme['accent_text']};
            }}
            QToolBar {{
                background-color: {theme['toolbar_bg']};
                border: none;
                spacing: 8px;
                padding: 8px 12px;
            }}
            QToolBar QPushButton {{
                background-color: {theme['bg_secondary']};
                color: {theme['text']};
                border: none;
                padding: 4px 10px;
                border-radius: 0;
                font-weight: normal;
                font-size: 12px;
                min-width: 50px;
            }}
            QToolBar QPushButton:hover {{
                background-color: {theme['bg_tertiary']};
                color: {theme['text']};
                border-color: {theme['border']};
                font-weight: normal;
            }}
            QToolBar QPushButton:pressed {{
                background-color: {theme['bg_tertiary']};
                font-weight: normal;
            }}
            QWidget#toolbarWidget QPushButton {{
                font-weight: normal;
            }}
            QTabWidget::pane {{
                border: none;
                border-top: 1px solid {theme['border']};
                border-bottom: none;
                background-color: {theme['bg']};
                border-radius: 0 0 0 0;
            }}
            QTabBar::tab {{
                background-color: {theme['bg_secondary']};
                color: {theme['text']};
                padding: 10px 20px;
                border: none;
                border-bottom: none;
                border-radius: 0 0 0 0;
                margin-right: 2px;
                font-weight: 500;
            }}
            QTabBar::tab:selected {{
                background-color: {theme['bg']};
                color: {theme['text']};
                border-bottom: 2px solid {theme['accent']};
            }}
            QTabBar::tab:hover {{
                background-color: {theme['bg_tertiary']};
                color: {theme['text']};
            }}
            QTextEdit {{
                background-color: {theme['editor_bg']};
                color: {theme['editor_text']};
                border: none;
                border-right: 1px solid {theme['border']};
                border-radius: 0;
                padding: 12px;
                selection-background-color: {theme['accent']};
                selection-color: {theme['accent_text']};
                font-family: 'Consolas', 'Courier New', monospace;
                line-height: 1.6;
            }}
            QTextEdit:focus {{
                border: none;
                border-right: 1px solid {theme['border']};
            }}
            QStatusBar {{
                background-color: {theme['status_bg']};
                color: {theme['status_text']};
                border: none;
                padding: 4px 12px;
                font-size: 12px;
            }}
            QSplitter::handle {{
                background-color: transparent;
                width: 2px;
            }}
            QSplitter::handle:hover {{
                background-color: {theme['accent']};
            }}
            QWebEngineView {{
                border: none;
            }}
            QScrollBar:vertical {{
                background-color: {theme['bg_secondary']};
                width: 14px;
                border-radius: 0;
                margin: 2px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {theme['border']};
                border-radius: 0;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {theme['accent']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar:horizontal {{
                background-color: {theme['bg_secondary']};
                height: 14px;
                border-radius: 0;
                margin: 2px;
            }}
            QScrollBar::handle:horizontal {{
                background-color: {theme['border']};
                border-radius: 0;
                min-width: 30px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background-color: {theme['accent']};
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
            QPushButton {{
                background-color: {theme['bg_secondary']};
                color: {theme['text']};
                border: none;
                padding: 8px 20px;
                border-radius: 0;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {theme['bg_tertiary']};
                border-color: {theme['border']};
            }}
            QPushButton:pressed {{
                background-color: {theme['bg_tertiary']};
            }}
            QPushButton:disabled {{
                background-color: {theme['bg_tertiary']};
                color: {theme['text_secondary']};
            }}
            QLineEdit {{
                background-color: {theme['bg']};
                color: {theme['text']};
                border: none;
                border-radius: 0;
                padding: 8px 12px;
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: none;
            }}
            QLineEdit:disabled {{
                background-color: {theme['bg_secondary']};
                color: {theme['text_secondary']};
            }}
            QComboBox {{
                background-color: {theme['bg']};
                color: {theme['text']};
                border: none;
                border-radius: 0;
                padding: 6px 12px;
                min-width: 120px;
            }}
            QComboBox:hover {{
                border: none;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 24px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {theme['text_secondary']};
            }}
            QComboBox QAbstractItemView {{
                background-color: {theme['bg_secondary']};
                color: {theme['text']};
                border: none;
                border-radius: 0;
                selection-background-color: {theme['accent']};
                selection-color: {theme['accent_text']};
            }}
            QCheckBox {{
                spacing: 8px;
                color: {theme['text']};
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: none;
                border-radius: 0;
                background-color: {theme['bg']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {theme['accent']};
                border-color: {theme['accent']};
            }}
            QCheckBox::indicator:hover {{
                border-color: {theme['accent']};
            }}
            QGroupBox {{
                font-weight: 600;
                border: none;
                border-radius: 0;
                margin-top: 16px;
                padding-top: 12px;
                background-color: {theme['bg']};
                color: {theme['text']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
                color: {theme['accent']};
                font-size: 13px;
            }}
            QLabel {{
                color: {theme['text']};
            }}
            QSpinBox {{
                background-color: {theme['bg']};
                color: {theme['text']};
                border: none;
                border-radius: 0;
                padding: 6px;
            }}
            QSpinBox:focus {{
                border: 2px solid {theme['accent']};
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                width: 20px;
                border: none;
                background-color: {theme['bg_secondary']};
            }}
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
                background-color: {theme['accent']};
            }}
        """


class SettingsDialog(QDialog):
    """设置窗口"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_editor = parent
        # 使用 INI 格式，避免打包后注册表权限问题
        self.settings = QSettings(QSettings.Format.IniFormat, QSettings.Scope.UserScope, "Markdo", "Settings")
        
        # 添加对话框动画支持（使用缓存）
        self.opacity_animation = AnimationCache.get_animation(
            self, b'windowOpacity', DIALOG_FADE_DURATION, QEasingCurve.Type.OutCubic, self
        )
        self._closing = False  # 标记是否正在关闭
        
        # 使用模态对话框，确保在父窗口之上
        self.setModal(True)
        self.init_ui()
        self.load_settings()
    
    def closeEvent(self, event):
        """关闭事件 - 添加淡出动画"""
        if not self._closing:
            self._closing = True
            event.ignore()
            # 淡出动画
            try:
                # 先断开之前的连接（如果存在）
                try:
                    self.opacity_animation.finished.disconnect()
                except (TypeError, RuntimeError):
                    pass
                
                self.opacity_animation.setStartValue(1.0)
                self.opacity_animation.setEndValue(0.0)
                self.opacity_animation.finished.connect(self._on_close_animation_finished)
                self.opacity_animation.start()
            except Exception as e:
                # 如果动画启动失败，直接关闭对话框
                log_exception(type(e), e, e.__traceback__, "启动关闭动画")
                event.accept()
        else:
            event.accept()
    
    def _on_close_animation_finished(self):
        """关闭动画完成"""
        try:
            self.opacity_animation.finished.disconnect(self._on_close_animation_finished)
        except (TypeError, RuntimeError):
            # 信号可能已经断开或对象状态不正确，忽略错误
            pass
        self.accept()
    
    def accept(self):
        """接受对话框 - 添加淡出动画"""
        if not self._closing:
            self._closing = True
            # 淡出动画
            try:
                # 先断开之前的连接（如果存在）
                try:
                    self.opacity_animation.finished.disconnect()
                except (TypeError, RuntimeError):
                    pass
                
                self.opacity_animation.setStartValue(1.0)
                self.opacity_animation.setEndValue(0.0)
                self.opacity_animation.finished.connect(self._on_accept_animation_finished)
                self.opacity_animation.start()
            except Exception as e:
                # 如果动画启动失败，直接接受对话框
                log_exception(type(e), e, e.__traceback__, "启动接受动画")
                super().accept()
        else:
            super().accept()
    
    def _on_accept_animation_finished(self):
        """接受动画完成"""
        try:
            self.opacity_animation.finished.disconnect(self._on_accept_animation_finished)
        except (TypeError, RuntimeError):
            # 信号可能已经断开或对象状态不正确，忽略错误
            # 这在 Nuitka 打包后的环境中可能发生
            pass
        super().accept()
    
    def reject(self):
        """拒绝对话框 - 添加淡出动画"""
        if not self._closing:
            self._closing = True
            # 淡出动画
            try:
                # 先断开之前的连接（如果存在）
                try:
                    self.opacity_animation.finished.disconnect()
                except (TypeError, RuntimeError):
                    pass
                
                self.opacity_animation.setStartValue(1.0)
                self.opacity_animation.setEndValue(0.0)
                self.opacity_animation.finished.connect(self._on_reject_animation_finished)
                self.opacity_animation.start()
            except Exception as e:
                # 如果动画启动失败，直接拒绝对话框
                log_exception(type(e), e, e.__traceback__, "启动拒绝动画")
                super().reject()
        else:
            super().reject()
    
    def _on_reject_animation_finished(self):
        """拒绝动画完成"""
        try:
            self.opacity_animation.finished.disconnect(self._on_reject_animation_finished)
        except (TypeError, RuntimeError):
            # 信号可能已经断开或对象状态不正确，忽略错误
            # 这在 Nuitka 打包后的环境中可能发生
            pass
        super().reject()
        
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("⚙️ 设置")
        self.setFixedSize(550, 650)
        
        # 从父窗口获取当前主题
        if self.parent_editor and hasattr(self.parent_editor, 'current_theme'):
            theme = self.parent_editor.current_theme
        else:
            theme_name = self.settings.value("theme", "dark", type=str)
            theme = Theme.get_theme(theme_name)
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {theme['bg_secondary']};
                border-radius: 0;
            }}
            QGroupBox {{
                font-weight: 600;
                border: none;
                border-radius: 0;
                margin-top: 12px;
                padding-top: 12px;
                background-color: {theme['bg']};
                color: {theme['text']};
                font-size: 14px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 6px;
                color: {theme['accent']};
                font-size: 15px;
            }}
            QCheckBox {{
                spacing: 10px;
                color: {theme['text']};
                font-size: 14px;
                font-weight: 500;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: none;
                border-radius: 0;
                background-color: {theme['bg']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {theme['accent']};
                border-color: {theme['accent']};
            }}
            QLabel {{
                color: {theme['text']};
                font-size: 14px;
                font-weight: 500;
            }}
            QComboBox {{
                background-color: {theme['bg']};
                color: {theme['text']};
                border: 1px solid {theme['border']};
                padding: 8px 14px;
                border-radius: 0;
                font-size: 14px;
                min-height: 20px;
            }}
            QComboBox:hover {{
                border-color: {theme['accent']};
            }}
            QComboBox:focus {{
                border: 2px solid {theme['accent']};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border: 5px solid transparent;
                border-top: 8px solid {theme['text_secondary']};
                margin-right: 10px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {theme['bg']};
                color: {theme['text']};
                selection-background-color: {theme['accent']};
                selection-color: {theme['accent_text']};
                border: 1px solid {theme['border']};
                border-radius: 0;
                padding: 4px;
                outline: none;
            }}
            QComboBox QAbstractItemView::item {{
                padding: 10px 12px;
                min-height: 24px;
                border-radius: 0;
            }}
            QComboBox QAbstractItemView::item:hover {{
                background-color: {theme['bg_tertiary']};
            }}
            QComboBox QAbstractItemView::item:selected {{
                background-color: {theme['accent']};
                color: {theme['accent_text']};
            }}
            QLineEdit {{
                background-color: {theme['bg']};
                color: {theme['text']};
                border: none;
                padding: 10px 14px;
                border-radius: 0;
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border: none;
            }}
            QTimeEdit {{
                background-color: {theme['bg']};
                color: {theme['text']};
                border: 1px solid {theme['border']};
                padding: 8px 12px;
                border-radius: 4px;
                font-size: 14px;
            }}
            QTimeEdit:focus {{
                border: 1px solid {theme['accent']};
            }}
            QTimeEdit:disabled {{
                background-color: {theme['bg_secondary']};
                color: {theme['text_secondary']};
            }}
            QTimeEdit::up-button, QTimeEdit::down-button {{
                background-color: {theme['bg_secondary']};
                border: none;
                width: 20px;
            }}
            QTimeEdit::up-button:hover, QTimeEdit::down-button:hover {{
                background-color: {theme['bg_tertiary']};
            }}
            QTimeEdit::up-button:disabled, QTimeEdit::down-button:disabled {{
                background-color: {theme['bg_secondary']};
            }}
            QPushButton {{
                background-color: {theme['bg_secondary']};
                color: {theme['text']};
                border: none;
                padding: 10px 24px;
                border-radius: 0;
                font-weight: 600;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {theme['bg_tertiary']};
                border-color: {theme['border']};
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)
        
        # 外观设置组
        appearance_group = QGroupBox("外观")
        appearance_grid = QGridLayout()
        appearance_grid.setColumnStretch(0, 1)
        appearance_grid.setColumnStretch(1, 1)
        appearance_grid.setHorizontalSpacing(30)
        
        # 左侧：主题设置
        left_layout = QVBoxLayout()
        
        # 黑夜主题选择
        dark_theme_layout = QHBoxLayout()
        dark_theme_label = QLabel("黑夜主题：")
        self.dark_theme_combo = QComboBox()
        for theme in Theme.get_dark_themes():
            self.dark_theme_combo.addItem(theme['display_name'], theme['name'])
        self.dark_theme_combo.setMinimumWidth(150)
        dark_theme_layout.addWidget(dark_theme_label)
        dark_theme_layout.addWidget(self.dark_theme_combo)
        dark_theme_layout.addStretch()
        left_layout.addLayout(dark_theme_layout)
        
        # 白天主题选择
        light_theme_layout = QHBoxLayout()
        light_theme_label = QLabel("白天主题：")
        self.light_theme_combo = QComboBox()
        for theme in Theme.get_light_themes():
            self.light_theme_combo.addItem(theme['display_name'], theme['name'])
        self.light_theme_combo.setMinimumWidth(150)
        light_theme_layout.addWidget(light_theme_label)
        light_theme_layout.addWidget(self.light_theme_combo)
        light_theme_layout.addStretch()
        left_layout.addLayout(light_theme_layout)
        
        # 主题模式选择
        theme_mode_layout = QHBoxLayout()
        theme_mode_label = QLabel("主题模式：")
        self.theme_mode_combo = QComboBox()
        self.theme_mode_combo.addItem("跟随时间切换", "auto")
        self.theme_mode_combo.addItem("始终使用白天主题", "light")
        self.theme_mode_combo.addItem("始终使用黑夜主题", "dark")
        self.theme_mode_combo.setMinimumWidth(150)
        self.theme_mode_combo.setToolTip("选择主题切换模式")
        self.theme_mode_combo.currentIndexChanged.connect(self.on_theme_mode_changed)
        theme_mode_layout.addWidget(theme_mode_label)
        theme_mode_layout.addWidget(self.theme_mode_combo)
        theme_mode_layout.addStretch()
        left_layout.addLayout(theme_mode_layout)
        
        # 自动切换主题选项（保留但隐藏，用于内部逻辑）
        self.auto_theme_checkbox = QCheckBox("根据时间自动切换主题")
        self.auto_theme_checkbox.setToolTip("开启后，将在指定时间自动切换黑夜/白天模式")
        self.auto_theme_checkbox.toggled.connect(self.on_auto_theme_toggled)
        self.auto_theme_checkbox.setVisible(False)
        
        # 时间设置区域
        time_layout = QHBoxLayout()
        time_layout.setContentsMargins(0, 5, 0, 0)
        
        night_start_label = QLabel("黑夜开始：")
        self.night_start_time = QTimeEdit()
        self.night_start_time.setDisplayFormat("HH:mm")
        self.night_start_time.setTime(QTime(18, 0))
        from PyQt6.QtWidgets import QAbstractSpinBox
        self.night_start_time.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.UpDownArrows)
        self.night_start_time.setKeyboardTracking(False)
        
        night_end_label = QLabel("黑夜结束：")
        self.night_end_time = QTimeEdit()
        self.night_end_time.setDisplayFormat("HH:mm")
        self.night_end_time.setTime(QTime(6, 0))
        self.night_end_time.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.UpDownArrows)
        self.night_end_time.setKeyboardTracking(False)
        
        time_layout.addWidget(night_start_label)
        time_layout.addWidget(self.night_start_time)
        time_layout.addSpacing(10)
        time_layout.addWidget(night_end_label)
        time_layout.addWidget(self.night_end_time)
        time_layout.addStretch()
        left_layout.addLayout(time_layout)
        
        left_layout.addStretch()
        
        # 右侧：编辑器设置
        right_layout = QVBoxLayout()
        
        # 编辑器字号设置
        font_size_layout = QHBoxLayout()
        font_size_label = QLabel("编辑器字号：")
        self.font_size_spinbox = QSpinBox()
        self.font_size_spinbox.setRange(10, 32)
        self.font_size_spinbox.setValue(15)  # 默认值
        self.font_size_spinbox.setSuffix(" px")
        self.font_size_spinbox.setMinimumWidth(80)
        font_size_layout.addWidget(font_size_label)
        font_size_layout.addWidget(self.font_size_spinbox)
        font_size_layout.addStretch()
        right_layout.addLayout(font_size_layout)
        
        right_layout.addStretch()
        
        # 将左右布局添加到grid
        appearance_grid.addLayout(left_layout, 0, 0)
        appearance_grid.addLayout(right_layout, 0, 1)
        
        appearance_group.setLayout(appearance_grid)
        layout.addWidget(appearance_group)
        
        # 常规设置组
        general_group = QGroupBox("常规")
        general_layout = QVBoxLayout()
        
        # 启动时显示使用指南开关（默认开启）
        self.show_welcome_checkbox = QCheckBox("启动时显示使用指南")
        self.show_welcome_checkbox.setToolTip("开启后，每次启动程序时会显示使用指南")
        self.show_welcome_checkbox.setChecked(True)  # 默认选中
        general_layout.addWidget(self.show_welcome_checkbox)
        
        # 同步滚动开关（默认开启）
        self.sync_scroll_checkbox = QCheckBox("启用同步滚动")
        self.sync_scroll_checkbox.setToolTip("开启后，编辑器和预览窗的滚动位置将同步")
        self.sync_scroll_checkbox.setChecked(True)  # 默认选中
        general_layout.addWidget(self.sync_scroll_checkbox)
        
        # 快捷键设置
        hotkey_layout = QHBoxLayout()
        hotkey_label = QLabel("工具栏快捷键：")
        self.hotkey_input = QLineEdit()
        self.hotkey_input.setPlaceholderText("点击此处并按下想要设置的快捷键")
        self.hotkey_input.setReadOnly(True)  # 只读，通过键盘事件设置
        self.hotkey_input.mousePressEvent = self.on_hotkey_input_click
        self.hotkey_input.setToolTip("点击输入框后按下快捷键组合来设置")
        hotkey_layout.addWidget(hotkey_label)
        hotkey_layout.addWidget(self.hotkey_input)
        hotkey_layout.addStretch()
        general_layout.addLayout(hotkey_layout)
        
        general_group.setLayout(general_layout)
        layout.addWidget(general_group)
        
        # 弹性空间
        layout.addStretch()
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.save_settings)
        btn_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.setStyleSheet(f"""
            background-color: {theme['bg_tertiary']};
            color: {theme['text']};
            border: none;
            padding: 10px 24px;
            border-radius: 0;
            font-weight: 600;
            font-size: 14px;
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def load_settings(self):
        """加载设置"""
        # 加载黑夜主题
        dark_theme_name = self.settings.value("theme/dark", "dark", type=str)
        dark_index = self.dark_theme_combo.findData(dark_theme_name)
        if dark_index >= 0:
            self.dark_theme_combo.setCurrentIndex(dark_index)
        
        # 加载白天主题
        light_theme_name = self.settings.value("theme/light", "morandi_pink", type=str)
        light_index = self.light_theme_combo.findData(light_theme_name)
        if light_index >= 0:
            self.light_theme_combo.setCurrentIndex(light_index)
        
        # 加载主题模式
        theme_mode = self.settings.value("theme/mode", "auto", type=str)
        mode_index = self.theme_mode_combo.findData(theme_mode)
        if mode_index >= 0:
            self.theme_mode_combo.setCurrentIndex(mode_index)
        
        # 加载自动切换主题设置（用于向后兼容）
        auto_theme = self.settings.value("theme/auto_switch", False, type=bool)
        # 如果旧版本启用了自动切换，迁移到新的mode设置
        if auto_theme and not self.settings.contains("theme/mode"):
            self.theme_mode_combo.setCurrentIndex(self.theme_mode_combo.findData("auto"))
        self.auto_theme_checkbox.setChecked(auto_theme)
        
        # 加载黑夜模式时间设置
        night_start = self.settings.value("theme/night_start", "18:00", type=str)
        night_end = self.settings.value("theme/night_end", "06:00", type=str)
        try:
            self.night_start_time.setTime(QTime.fromString(night_start, "HH:mm"))
        except (ValueError, AttributeError, TypeError):
            self.night_start_time.setTime(QTime(18, 0))  # 如果解析失败，使用默认值
        try:
            self.night_end_time.setTime(QTime.fromString(night_end, "HH:mm"))
        except (ValueError, AttributeError, TypeError):
            self.night_end_time.setTime(QTime(6, 0))  # 如果解析失败，使用默认值
        
        # 更新控件的启用状态
        self.on_theme_mode_changed(self.theme_mode_combo.currentIndex())
        
        # 加载快捷键设置
        hotkey = self.settings.value("toolbar/hotkey", "Ctrl+;", type=str)
        self.hotkey_input.setText(hotkey)
        
        # 加载启动时显示使用指南设置
        show_welcome = self.settings.value("show_welcome", True, type=bool)
        self.show_welcome_checkbox.setChecked(show_welcome)
        
        # 加载同步滚动设置
        sync_scroll = self.settings.value("sync_scroll", True, type=bool)
        self.sync_scroll_checkbox.setChecked(sync_scroll)
        
        # 加载编辑器字号设置
        font_size = self.settings.value("editor/font_size", 15, type=int)
        self.font_size_spinbox.setValue(font_size)
    
    def on_theme_mode_changed(self, index):
        """主题模式改变事件"""
        theme_mode = self.theme_mode_combo.currentData()
        
        if theme_mode == "auto":
            # 跟随时间切换模式：启用时间设置
            self.night_start_time.setEnabled(True)
            self.night_end_time.setEnabled(True)
            self.auto_theme_checkbox.setChecked(True)
        else:
            # 始终白天/黑夜模式：禁用时间设置
            self.night_start_time.setEnabled(False)
            self.night_end_time.setEnabled(False)
            self.auto_theme_checkbox.setChecked(False)
        
        # 两个主题下拉框始终保持启用
        self.dark_theme_combo.setEnabled(True)
        self.light_theme_combo.setEnabled(True)
    
    def on_auto_theme_toggled(self, checked):
        """自动切换主题复选框切换事件"""
        self.night_start_time.setEnabled(checked)
        self.night_end_time.setEnabled(checked)
        # 两个主题下拉框始终保持启用
        self.dark_theme_combo.setEnabled(True)
        self.light_theme_combo.setEnabled(True)
    
    def on_hotkey_input_click(self, event):
        """点击快捷键输入框时开始捕获键盘"""
        self.hotkey_input.clear()
        self.hotkey_input.setPlaceholderText("请按下快捷键...")
        self.hotkey_input.setFocus()
    
    def keyPressEvent(self, event):
        """捕获键盘事件用于自定义快捷键"""
        if self.hotkey_input.hasFocus():
            # 检查是否是有效的快捷键组合
            modifiers = []
            
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                modifiers.append("Ctrl")
            if event.modifiers() & Qt.KeyboardModifier.AltModifier:
                modifiers.append("Alt")
            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                modifiers.append("Shift")
            if event.modifiers() & Qt.KeyboardModifier.MetaModifier:
                modifiers.append("Meta")
            
            # 获取按键
            key = event.key()
            key_name = ""
            
            # 常用按键映射
            key_map = {
                Qt.Key.Key_Space: "Space",
                Qt.Key.Key_Tab: "Tab",
                Qt.Key.Key_Enter: "Enter",
                Qt.Key.Key_Return: "Return",
                Qt.Key.Key_Escape: "Esc",
                Qt.Key.Key_Backspace: "Backspace",
                Qt.Key.Key_Delete: "Delete",
                Qt.Key.Key_Insert: "Insert",
                Qt.Key.Key_Home: "Home",
                Qt.Key.Key_End: "End",
                Qt.Key.Key_PageUp: "PageUp",
                Qt.Key.Key_PageDown: "PageDown",
                Qt.Key.Key_Up: "Up",
                Qt.Key.Key_Down: "Down",
                Qt.Key.Key_Left: "Left",
                Qt.Key.Key_Right: "Right",
                Qt.Key.Key_F1: "F1", Qt.Key.Key_F2: "F2", Qt.Key.Key_F3: "F3",
                Qt.Key.Key_F4: "F4", Qt.Key.Key_F5: "F5", Qt.Key.Key_F6: "F6",
                Qt.Key.Key_F7: "F7", Qt.Key.Key_F8: "F8", Qt.Key.Key_F9: "F9",
                Qt.Key.Key_F10: "F10", Qt.Key.Key_F11: "F11", Qt.Key.Key_F12: "F12",
                Qt.Key.Key_QuoteLeft: "`",
            }
            
            if key in key_map:
                key_name = key_map[key]
            elif 0x20 <= key <= 0x7e:  # 可打印ASCII字符
                key_name = chr(key)
            elif 0x41 <= key <= 0x5a:  # A-Z
                key_name = chr(key)
            elif 0x30 <= key <= 0x39:  # 0-9
                key_name = chr(key)
            
            # 如果只有修饰键，只显示修饰键
            if not key_name and modifiers:
                hotkey = "+".join(modifiers)
            elif key_name:
                hotkey = "+".join(modifiers + [key_name]) if modifiers else key_name
            else:
                event.ignore()
                return
            
            # 设置快捷键
            self.hotkey_input.setText(hotkey)
            self.hotkey_input.setPlaceholderText("点击此处并按下想要设置的快捷键")
            event.accept()
        else:
            super().keyPressEvent(event)
    
    def reset_hotkey(self):
        """重置快捷键为默认值"""
        self.hotkey_input.setText("Ctrl+;")
        self.settings.setValue("toolbar/hotkey", "Ctrl+;")
    
    def save_settings(self):
        """保存设置"""
        try:
            if logger:
                logger.info("开始保存设置...")
            
            # 保存黑夜主题和白天主题
            try:
                dark_theme_name = self.dark_theme_combo.currentData()
                light_theme_name = self.light_theme_combo.currentData()
                if logger:
                    logger.debug(f"保存主题: dark={dark_theme_name}, light={light_theme_name}")
                self.settings.setValue("theme/dark", dark_theme_name)
                self.settings.setValue("theme/light", light_theme_name)
            except Exception as e:
                log_exception(type(e), e, e.__traceback__, "保存主题设置")
                raise
            
            # 保存主题模式
            try:
                theme_mode = self.theme_mode_combo.currentData()
                if logger:
                    logger.debug(f"保存主题模式: {theme_mode}")
                self.settings.setValue("theme/mode", theme_mode)
            except Exception as e:
                log_exception(type(e), e, e.__traceback__, "保存主题模式")
                raise
            
            # 保存自动切换主题设置（由theme_mode控制）
            try:
                auto_theme = self.auto_theme_checkbox.isChecked()
                if logger:
                    logger.debug(f"保存自动切换主题: {auto_theme}")
                self.settings.setValue("theme/auto_switch", auto_theme)
            except Exception as e:
                log_exception(type(e), e, e.__traceback__, "保存自动切换主题设置")
                raise
            
            # 保存黑夜模式时间设置
            try:
                night_start = self.night_start_time.time().toString("HH:mm")
                night_end = self.night_end_time.time().toString("HH:mm")
                if logger:
                    logger.debug(f"保存时间设置: start={night_start}, end={night_end}")
                self.settings.setValue("theme/night_start", night_start)
                self.settings.setValue("theme/night_end", night_end)
            except Exception as e:
                log_exception(type(e), e, e.__traceback__, "保存时间设置")
                raise
            
            # 保存快捷键设置（验证快捷键有效性 ）
            try:
                hotkey = self.hotkey_input.text().strip()
                if not hotkey:
                    hotkey = "Ctrl+;"  # 默认快捷键
                if logger:
                    logger.debug(f"保存快捷键: {hotkey}")
                self.settings.setValue("toolbar/hotkey", hotkey)
            except Exception as e:
                log_exception(type(e), e, e.__traceback__, "保存快捷键设置")
                raise
            
            # 保存启动时显示使用指南设置
            try:
                show_welcome = self.show_welcome_checkbox.isChecked()
                if logger:
                    logger.debug(f"保存显示欢迎对话框设置: {show_welcome}")
                self.settings.setValue("show_welcome", show_welcome)
            except Exception as e:
                log_exception(type(e), e, e.__traceback__, "保存显示欢迎对话框设置")
                raise
            
            # 保存同步滚动设置
            try:
                sync_scroll = self.sync_scroll_checkbox.isChecked()
                if logger:
                    logger.debug(f"保存同步滚动设置: {sync_scroll}")
                self.settings.setValue("sync_scroll", sync_scroll)
            except Exception as e:
                log_exception(type(e), e, e.__traceback__, "保存同步滚动设置")
                raise
            
            # 保存编辑器字号设置
            try:
                font_size = self.font_size_spinbox.value()
                if logger:
                    logger.debug(f"保存编辑器字号: {font_size}")
                self.settings.setValue("editor/font_size", font_size)
            except Exception as e:
                log_exception(type(e), e, e.__traceback__, "保存编辑器字号设置")
                raise
            
            # 注意：不调用 sync()，让 QSettings 自动同步
            # 在打包后的环境中，sync() 可能会阻塞或导致崩溃
            # QSettings 会在对象销毁时自动同步到磁盘，所以不需要手动调用 sync()
            # 为了确保设置能够保存，我们在关闭对话框前处理一次事件
            try:
                if logger:
                    logger.debug("处理事件队列，确保设置操作完成...")
                QApplication.processEvents()
            except Exception as e:
                log_exception(type(e), e, e.__traceback__, "处理事件队列")
                # 这个错误不应该阻止保存
            
            # 通知父窗口更新设置
            if self.parent_editor:
                try:
                    if logger:
                        logger.debug("通知父窗口更新设置...")
                    self.parent_editor.update_theme_settings(dark_theme_name, light_theme_name, theme_mode, auto_theme, night_start, night_end)
                    self.parent_editor.reload_toolbar_shortcut(hotkey)
                    self.parent_editor.update_editor_font_size(font_size)
                    self.parent_editor.update_sync_scroll_setting(sync_scroll)
                    if logger:
                        logger.info("父窗口设置更新完成")
                except Exception as e:
                    log_exception(type(e), e, e.__traceback__, "更新父窗口设置")
                    # 这个错误不应该阻止保存
            
            if logger:
                logger.info("设置保存完成")
            
            self.accept()
        except Exception as e:
            # 捕获所有异常，记录详细信息
            log_exception(type(e), e, e.__traceback__, "保存设置")
            
            # 显示错误消息给用户
            try:
                error_msg = QMessageBox(self)
                error_msg.setIcon(QMessageBox.Icon.Warning)
                error_msg.setWindowTitle("保存设置失败")
                error_msg.setText(f"保存设置时发生错误:\n{str(e)}\n\n详细信息已记录到日志文件。")
                error_msg.setDetailedText(traceback.format_exc())
                error_msg.exec()
            except Exception as msg_error:
                # 如果连消息框都显示不了，至少记录错误
                log_exception(type(msg_error), msg_error, msg_error.__traceback__, "显示错误消息框")
            
            # 即使保存失败，也关闭对话框，避免用户无法关闭
            try:
                self.accept()
            except Exception as close_error:
                log_exception(type(close_error), close_error, close_error.__traceback__, "关闭对话框")


class TitleButton(QPushButton):
    """标题栏按钮"""
    def __init__(self, parent=None, text=""):
        super().__init__(parent)
        self.setText(text)
        self.setFixedSize(40, 30)
        self.setFlat(True)
        self.setCursor(Qt.CursorShape.ArrowCursor)


class CustomTitleBar(QWidget):
    """自定义标题栏 - 包含Logo、程序名、拖动区域和窗口控制按钮"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.init_ui()
        # 初始化时应用主题（如果父窗口有主题）
        if parent and hasattr(parent, 'current_theme'):
            self.update_theme(parent.current_theme)
    
    def init_ui(self):
        """初始化标题栏UI"""
        self.setFixedHeight(40)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(12, 0, 8, 0)
        layout.setSpacing(8)
        
        # 左侧：应用图标和标题
        icon_label = QLabel()
        app_icon = get_app_icon()
        if not app_icon.isNull():
            icon_label.setPixmap(app_icon.pixmap(24, 24))
        else:
            icon_label.setText("📝")  # 备用emoji
        icon_label.setStyleSheet("font-size: 18px; padding: 0; background-color: transparent;")
        layout.addWidget(icon_label)
        
        self.title_label = QLabel("Markdo")
        self.title_label.setStyleSheet("font-size: 14px; font-weight: 600; padding: 0; background-color: transparent;")
        layout.addWidget(self.title_label)
        
        # 中间弹性空间（拖动区域）
        layout.addStretch()
        
        # 右侧：窗口控制按钮
        # 置顶按钮
        self.pin_btn = QPushButton("📌")
        self.pin_btn.setFixedSize(30, 30)  # 缩小按钮尺寸
        self.pin_btn.setObjectName("titleBarButton")
        self.pin_btn.setCheckable(True)  # 设置为可选中状态
        self.pin_btn.clicked.connect(self.toggle_pin_window)

        
        self.minimize_btn = QPushButton("−")
        self.minimize_btn.setFixedSize(40, 30)
        self.minimize_btn.setObjectName("titleBarButton")
        self.minimize_btn.clicked.connect(self.parent_window.showMinimized)
        
        self.maximize_btn = QPushButton("□")
        self.maximize_btn.setFixedSize(40, 30)
        self.maximize_btn.setObjectName("titleBarButton")
        self.maximize_btn.clicked.connect(self.toggle_maximize)
        
        self.close_btn = QPushButton("×")
        self.close_btn.setFixedSize(40, 30)
        self.close_btn.setObjectName("closeButton")
        self.close_btn.clicked.connect(self.parent_window.close)
        
        layout.addWidget(self.pin_btn)
        layout.addWidget(self.minimize_btn)
        layout.addWidget(self.maximize_btn)
        layout.addWidget(self.close_btn)
        
        self.setLayout(layout)
        
        # 立即应用样式（如果父窗口已有主题）
        if self.parent_window and hasattr(self.parent_window, 'current_theme'):
            self.update_theme(self.parent_window.current_theme)
    
    def toggle_maximize(self):
        """切换最大化/还原"""
        if self.parent_window.isMaximized():
            self.parent_window.showNormal()
            self.maximize_btn.setText("□")
        else:
            self.parent_window.showMaximized()
            self.maximize_btn.setText("❐")
    
    def toggle_pin_window(self):
        """切换窗口置顶状态"""
        # 获取当前窗口的窗口标志
        flags = self.parent_window.windowFlags()
        # 检查是否已经置顶
        is_pinned = flags & Qt.WindowType.WindowStaysOnTopHint
        
        if is_pinned:
            # 如果当前是置顶状态，则取消置顶
            self.parent_window.setWindowFlags(flags & ~Qt.WindowType.WindowStaysOnTopHint)
            self.pin_btn.setChecked(False)  # 更新按钮状态
        else:
            # 如果当前不是置顶状态，则设置为置顶
            self.parent_window.setWindowFlags(flags | Qt.WindowType.WindowStaysOnTopHint)
            self.pin_btn.setChecked(True)  # 更新按钮状态
        
        # 重新显示窗口以应用新的窗口标志
        self.parent_window.show()
        
        # 刷新样式
        self.pin_btn.style().unpolish(self.pin_btn)
        self.pin_btn.style().polish(self.pin_btn)
    
    def mousePressEvent(self, event):
        """鼠标按下事件 - 传递给主窗口处理拖动"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 检查是否在按钮区域
            if (self.pin_btn.geometry().contains(event.pos()) or
                self.minimize_btn.geometry().contains(event.pos()) or
                self.maximize_btn.geometry().contains(event.pos()) or
                self.close_btn.geometry().contains(event.pos())):
                # 在按钮上，不处理拖动
                super().mousePressEvent(event)
                return
            
            # 不在按钮区域，触发主窗口拖动
            # 将事件坐标转换为全局坐标，然后传递给主窗口
            global_pos = self.mapToGlobal(event.pos())
            # 创建新的事件传递给主窗口
            if hasattr(self.parent_window, 'mousePressEvent'):
                # 设置主窗口的拖动标志
                self.parent_window.move_flag = True
                self.parent_window.window_origin_x = self.parent_window.x()
                self.parent_window.window_origin_y = self.parent_window.y()
                self.parent_window.mouse_origin_x = global_pos.x()
                self.parent_window.mouse_origin_y = global_pos.y()
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件 - 传递给主窗口处理拖动"""
        if event.buttons() == Qt.MouseButton.LeftButton:
            if hasattr(self.parent_window, 'move_flag') and self.parent_window.move_flag:
                # 主窗口正在拖动，继续处理
                global_pos = self.mapToGlobal(event.pos())
                # 如果全屏，先退出全屏
                if self.parent_window.isFullScreen():
                    self.parent_window.showNormal()
                    # 更新窗口位置信息
                    self.parent_window.window_origin_x = self.parent_window.x()
                    self.parent_window.window_origin_y = self.parent_window.y()
                    # 重新计算鼠标位置
                    self.parent_window.mouse_origin_x = global_pos.x()
                    self.parent_window.mouse_origin_y = global_pos.y()
                
                if not self.parent_window.isMaximized():
                    mouse_des_x = global_pos.x()
                    mouse_des_y = global_pos.y()
                    window_des_x = self.parent_window.window_origin_x + mouse_des_x - self.parent_window.mouse_origin_x
                    window_des_y = self.parent_window.window_origin_y + mouse_des_y - self.parent_window.mouse_origin_y
                    self.parent_window.move(window_des_x, window_des_y)
                event.accept()
                return
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件 - 结束拖动"""
        if event.button() == Qt.MouseButton.LeftButton:
            if hasattr(self.parent_window, 'move_flag'):
                self.parent_window.move_flag = False
        super().mouseReleaseEvent(event)
    
    def mouseDoubleClickEvent(self, event):
        """双击标题栏 - 切换最大化"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 检查是否在按钮区域
            if not (self.pin_btn.geometry().contains(event.pos()) or
                    self.minimize_btn.geometry().contains(event.pos()) or
                    self.maximize_btn.geometry().contains(event.pos()) or
                    self.close_btn.geometry().contains(event.pos())):
                self.toggle_maximize()
        super().mouseDoubleClickEvent(event)
    
    def update_theme(self, theme):
        """更新主题样式"""
        self.setStyleSheet(f"""
            CustomTitleBar {{
                background-color: {theme['bg_secondary']};
                border-bottom: 1px solid {theme['border']};
            }}
            QLabel {{
                color: {theme['text']};
                background-color: transparent;
            }}
            QPushButton#titleBarButton {{
                background-color: transparent;
                color: {theme['text']};  /* 使用标准文本颜色 */
                border: none;
                border-radius: 0;
                font-size: 16px;  /* 缩小字体大小 */
                font-weight: 600;
                padding: 0px;
                min-width: 30px;
                min-height: 30px;
            }}
            QPushButton#titleBarButton:hover {{
                background-color: {theme['bg_tertiary']};
            }}
            QPushButton#titleBarButton:pressed {{
                background-color: {theme['bg_tertiary']};
            }}
            QPushButton#titleBarButton:checked {{
                background-color: {theme['bg_tertiary']};  /* 使用较柔和的背景高亮 */
                color: {theme['accent']};
            }}
            QPushButton#closeButton {{
                background-color: transparent;
                color: {theme['text']};
                border: none;
                border-radius: 0;
                font-size: 20px;
                font-weight: 600;
                padding: 0px;
                min-width: 40px;
                min-height: 30px;
            }}
            QPushButton#closeButton:hover {{
                background-color: {theme['error']};
                color: {theme['accent_text']};
            }}
            QPushButton#closeButton:pressed {{
                background-color: {theme['error']};
                color: {theme['accent_text']};
            }}
        """)


class WelcomeDialog(QDialog):
    """开屏教程窗口"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_editor = parent
        # 使用 INI 格式，避免打包后注册表权限问题
        self.settings = QSettings(QSettings.Format.IniFormat, QSettings.Scope.UserScope, "Markdo", "Settings")
        
        # 添加对话框动画支持
        # UI 动画：匹配显示器刷新率（通常 60fps 或更高）
        # 添加对话框动画支持（使用缓存）
        self.opacity_animation = AnimationCache.get_animation(
            self, b'windowOpacity', WINDOW_FADE_DURATION, QEasingCurve.Type.OutCubic, self
        )
        self._closing = False  # 标记是否正在关闭
        
        # 设置为模态对话框，确保显示在最前面
        self.setModal(True)
        # 设置窗口标志，确保显示在最前面
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowStaysOnTopHint)
        self.init_ui()
    
    def closeEvent(self, event):
        """关闭事件 - 添加淡出动画"""
        if not self._closing:
            self._closing = True
            event.ignore()
            # 停止任何正在进行的动画
            if self.opacity_animation.state() == QAbstractAnimation.State.Running:
                self.opacity_animation.stop()
            # 断开之前的连接，避免重复连接
            try:
                self.opacity_animation.finished.disconnect(self._on_close_animation_finished)
            except (TypeError, RuntimeError):
                pass
            # 淡出动画
            self.opacity_animation.setStartValue(self.windowOpacity())
            self.opacity_animation.setEndValue(0.0)
            self.opacity_animation.finished.connect(self._on_close_animation_finished)
            self.opacity_animation.start()
        else:
            event.accept()
    
    def _on_close_animation_finished(self):
        """关闭动画完成"""
        try:
            self.opacity_animation.finished.disconnect(self._on_close_animation_finished)
        except (TypeError, RuntimeError):
            pass
        # 直接调用父类的 accept，避免再次触发动画
        self._closing = True
        super().accept()
    
    def accept(self):
        """接受对话框 - 添加淡出动画"""
        if not self._closing:
            self._closing = True
            # 停止任何正在进行的动画
            if self.opacity_animation.state() == QAbstractAnimation.State.Running:
                self.opacity_animation.stop()
            # 断开之前的连接，避免重复连接
            try:
                self.opacity_animation.finished.disconnect(self._on_close_animation_finished)
            except (TypeError, RuntimeError):
                pass
            # 淡出动画
            self.opacity_animation.setStartValue(self.windowOpacity())
            self.opacity_animation.setEndValue(0.0)
            self.opacity_animation.finished.connect(self._on_close_animation_finished)
            self.opacity_animation.start()
        else:
            super().accept()
    
    def reject(self):
        """拒绝对话框 - 添加淡出动画"""
        if not self._closing:
            self._closing = True
            # 停止任何正在进行的动画
            if self.opacity_animation.state() == QAbstractAnimation.State.Running:
                self.opacity_animation.stop()
            # 断开之前的连接，避免重复连接
            try:
                self.opacity_animation.finished.disconnect(self._on_reject_animation_finished)
            except (TypeError, RuntimeError):
                pass
            # 淡出动画
            self.opacity_animation.setStartValue(self.windowOpacity())
            self.opacity_animation.setEndValue(0.0)
            self.opacity_animation.finished.connect(self._on_reject_animation_finished)
            self.opacity_animation.start()
        else:
            super().reject()
    
    def _on_reject_animation_finished(self):
        """拒绝动画完成"""
        try:
            self.opacity_animation.finished.disconnect(self._on_reject_animation_finished)
        except (TypeError, RuntimeError):
            pass
        # 直接调用父类的 reject，避免再次触发动画
        self._closing = True
        super().reject()
    
    def get_theme(self):
        # 从父窗口获取当前主题
        if self.parent_editor and hasattr(self.parent_editor, 'current_theme'):
            return self.parent_editor.current_theme
        # 后备：从设置中读取
        theme_name = self.settings.value("theme", "dark", type=str)
        return Theme.get_theme(theme_name)
    
    def init_ui(self):
        self.setWindowTitle("👋 欢迎使用 Markdo")
        theme = self.get_theme()
        
        # 获取屏幕尺寸，确保窗口不超过屏幕高度
        screen = QApplication.primaryScreen().geometry()
        max_height = min(680, screen.height() - 100)  # 留出一些边距
        
        # 使用最小/最大尺寸而不是固定尺寸，允许窗口调整但限制范围
        self.setMinimumSize(560, 500)
        self.setMaximumSize(600, max_height)
        self.resize(560, min(680, max_height))
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {theme['bg_secondary']};
                border-radius: 0;
            }}
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            QLabel {{
                color: {theme['text']};
            }}
            QCheckBox {{
                color: {theme['text_secondary']};
                spacing: 10px;
            }}
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border: none;
                border-radius: 0;
                background-color: {theme['bg']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {theme['accent']};
                border-color: {theme['accent']};
            }}
            QPushButton {{
                background-color: {theme['bg_secondary']};
                color: {theme['text']};
                border: none;
                padding: 14px 48px;
                border-radius: 0;
                font-weight: 700;
                font-size: 15px;
            }}
            QPushButton:hover {{
                background-color: {theme['bg_tertiary']};
                border-color: {theme['border']};
            }}
        """)
        
        # 创建主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # 创建内容容器
        content_widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 32, 40, 32)
        layout.setSpacing(18)
        
        # 标题
        title = QLabel("📝 Markdo")
        title.setStyleSheet(f"font-size: 28px; font-weight: 800; color: {theme['accent']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # 副标题
        subtitle = QLabel("现代 Markdown 编辑器")
        subtitle.setStyleSheet(f"font-size: 15px; color: {theme['text_secondary']}; font-weight: 500;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        
        layout.addSpacing(12)
        
        # 特色介绍
        features_group = QGroupBox("✨ 核心特色")
        features_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: 700;
                border: none;
                border-radius: 0;
                margin-top: 16px;
                padding: 18px;
                background-color: {theme['bg']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 18px;
                padding: 0 10px;
                color: {theme['accent']};
                font-size: 14px;
            }}
        """)
        features_layout = QVBoxLayout()
        features_layout.setSpacing(10)
        
        features = [
            "🔄 实时预览 - 边写边看，左右分屏，所见即所得",
            "🎨 语法高亮 - 清晰展示 Markdown 结构，提升可读性",
            "✨ 悬浮工具栏 - 快速插入各种格式，智能定位光标",
            "📷 智能插入 - 图片、表格、链接、代码块向导",
            "🌙 主题切换 - 支持黑夜/白天模式，护眼舒适",
            "📑 多标签页 - 同时编辑多个文件，高效切换",
            "⌨️ 快捷键支持 - 27个快捷键，提升编辑效率",
            "🔢 数学公式 - 完整支持 LaTeX/MathJax 数学公式",
            "💻 代码高亮 - 基于 Pygments 的语法高亮",
            "📝 列表自动续接 - 智能识别并自动续接列表项",
            "🔤 Tab自动补全 - 智能补全成对符号和常用格式",
            "📊 同步滚动 - 编辑器与预览窗同步滚动",
            "📈 字数统计 - 实时显示字数、行数、字符数",
            "🔗 文件关联 - 支持 .md 和 .markdown 文件关联",
            "⚙️ 丰富设置 - 自定义字体、主题、工具栏等",
        ]
        for feature in features:
            label = QLabel(feature)
            label.setStyleSheet(f"font-size: 14px; padding: 4px 0; color: {theme['text']};")
            features_layout.addWidget(label)
        
        features_group.setLayout(features_layout)
        layout.addWidget(features_group)
        
        # 快捷键介绍
        shortcuts_group = QGroupBox("⌨️ 常用快捷键")
        shortcuts_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: 700;
                border: none;
                border-radius: 0;
                margin-top: 16px;
                padding: 18px;
                background-color: {theme['bg']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 18px;
                padding: 0 10px;
                color: {theme['accent']};
                font-size: 14px;
            }}
        """)
        shortcuts_layout = QGridLayout()
        shortcuts_layout.setVerticalSpacing(8)
        shortcuts_layout.setHorizontalSpacing(24)
        
        shortcuts = [
            ("Ctrl+N", "新建文件"),
            ("Ctrl+O", "打开文件"),
            ("Ctrl+S", "保存文件"),
            ("Ctrl+Shift+S", "另存为"),
            ("Ctrl+Z", "撤销"),
            ("Ctrl+Y", "重做"),
            ("Ctrl+A", "全选"),
            ("Ctrl+F", "查找"),
            ("Ctrl+Shift+C", "复制全文"),
            ("Ctrl+B", "加粗"),
            ("Ctrl+I", "斜体"),
            ("Ctrl+D", "删除线"),
            ("Ctrl+H", "高亮"),
            ("Ctrl+`", "行内代码"),
            ("Ctrl+1~6", "标题1~6"),
            ("Ctrl+K", "插入链接"),
            ("Ctrl+Shift+K", "插入代码块"),
            ("Ctrl+Q", "插入引用"),
            ("Ctrl+L", "无序列表"),
            ("Ctrl+Shift+L", "有序列表"),
            ("Ctrl+R", "插入分割线"),
            ("Ctrl+T", "插入时间戳"),
            ("Ctrl+;", "显示/隐藏工具栏"),
            ("Ctrl+M", "显示/隐藏工具栏(备选)"),
            ("F1", "快捷键帮助"),
            ("Tab", "符号自动补全"),
        ]
        for i, (key, desc) in enumerate(shortcuts):
            key_label = QLabel(key)
            key_label.setStyleSheet(f"font-weight: bold; color: {theme['accent']}; font-size: 12px;")
            key_label.setMinimumWidth(100)
            shortcuts_layout.addWidget(key_label, i, 0)
            
            desc_label = QLabel(desc)
            desc_label.setStyleSheet(f"color: {theme['text']}; font-size: 12px;")
            shortcuts_layout.addWidget(desc_label, i, 1)
        
        shortcuts_group.setLayout(shortcuts_layout)
        layout.addWidget(shortcuts_group)
        
        # 使用提示
        tips_group = QGroupBox("💡 使用提示")
        tips_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: 700;
                border: none;
                border-radius: 0;
                margin-top: 16px;
                padding: 18px;
                background-color: {theme['bg']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 18px;
                padding: 0 10px;
                color: {theme['accent']};
                font-size: 14px;
            }}
        """)
        tips_layout = QVBoxLayout()
        tips_layout.setSpacing(8)
        
        tips = [
            "• 输入 * 后按 Tab 可自动补全为 **，再按可扩展为 ****",
            "• 支持行内数学公式：$E=mc^2$，块级公式：$$\\int_0^\\infty e^{-x}dx = 1$$",
            "• 列表项后按回车可自动续接，Shift+Tab 可取消缩进",
            "• 右键点击工具栏按钮可查看详细说明",
            "• 在设置中可自定义主题、字体大小、同步滚动等选项",
            "• 支持拖拽文件到窗口直接打开",
        ]
        for tip in tips:
            tip_label = QLabel(tip)
            tip_label.setStyleSheet(f"font-size: 12px; color: {theme['text_secondary']}; padding: 2px 0;")
            tip_label.setWordWrap(True)
            tips_layout.addWidget(tip_label)
        
        tips_group.setLayout(tips_layout)
        layout.addWidget(tips_group)
        
        layout.addStretch()
        
        # 不再显示复选框
        self.dont_show_checkbox = QCheckBox("下次启动时不再显示")
        layout.addWidget(self.dont_show_checkbox)
        
        # 开始使用按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        start_btn = QPushButton("开始使用")
        start_btn.clicked.connect(self.on_start)
        btn_layout.addWidget(start_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # 设置内容容器的布局
        content_widget.setLayout(layout)
        
        # 将内容容器添加到滚动区域
        scroll_area.setWidget(content_widget)
        
        # 将滚动区域添加到主布局
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)
        
        # 居中显示对话框
        self.center_dialog()
    
    def center_dialog(self):
        """居中显示对话框"""
        # 获取屏幕尺寸
        screen = QApplication.primaryScreen().geometry()
        # 获取对话框尺寸
        dialog_size = self.size()
        # 计算居中位置
        x = (screen.width() - dialog_size.width()) // 2
        y = (screen.height() - dialog_size.height()) // 2
        # 移动对话框到居中位置
        self.move(x, y)
    
    def on_start(self):
        """点击开始使用"""
        # 如果勾选了"不再显示"，则关闭启动时显示使用指南的开关
        if self.dont_show_checkbox.isChecked():
            self.settings.setValue("show_welcome", False)
        self.accept()


class MarkdownHighlighter(QSyntaxHighlighter):
    """Markdown语法高亮器 - 柔和配色，简化正则"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = []
        
        # 标题 (# ## ### 等) - 深灰蓝色
        header_format = QTextCharFormat()
        header_format.setForeground(QColor("#4a6785"))
        header_format.setFontWeight(QFont.Weight.Bold)
        self.highlighting_rules.append((compile(r'^#{1,6}\s.*'), header_format))
        
        # 粗体 (**text**) - 深棕色
        bold_format = QTextCharFormat()
        bold_format.setForeground(QColor("#7a5230"))
        bold_format.setFontWeight(QFont.Weight.Bold)
        self.highlighting_rules.append((compile(r'\*\*.+?\*\*'), bold_format))
        
        # 斜体 (*text*) - 深紫色
        italic_format = QTextCharFormat()
        italic_format.setForeground(QColor("#6b5b7a"))
        italic_format.setFontItalic(True)
        self.highlighting_rules.append((compile(r'\*.+?\*'), italic_format))
        
        # 行内代码 (`code`) - 深绿色
        code_format = QTextCharFormat()
        code_format.setForeground(QColor("#4a7a5a"))
        self.highlighting_rules.append((compile(r'`.+?`'), code_format))
        
        # 代码块标记 (```) - 深灰绿色
        codeblock_format = QTextCharFormat()
        codeblock_format.setForeground(QColor("#5a7a6a"))
        self.highlighting_rules.append((compile(r'^```.*'), codeblock_format))
        
        # 链接 [text](url) - 深青色
        link_format = QTextCharFormat()
        link_format.setForeground(QColor("#3a6a7a"))
        self.highlighting_rules.append((compile(r'\[.+?\]\(.+?\)'), link_format))
        
        # 列表标记 (- * +) - 深橙色
        list_format = QTextCharFormat()
        list_format.setForeground(QColor("#8a6a4a"))
        list_format.setFontWeight(QFont.Weight.Bold)
        self.highlighting_rules.append((compile(r'^\s*[-*+]\s'), list_format))
        self.highlighting_rules.append((compile(r'^\s*\d+\.\s'), list_format))
        
        # 引用 (>) - 深灰色
        quote_format = QTextCharFormat()
        quote_format.setForeground(QColor("#6a6a6a"))
        self.highlighting_rules.append((compile(r'^>+.*'), quote_format))
        
        # 删除线 (~~text~~) - 灰色
        strikethrough_format = QTextCharFormat()
        strikethrough_format.setForeground(QColor("#7a7a7a"))
        self.highlighting_rules.append((compile(r'~~.+?~~'), strikethrough_format))
        
        # 高亮 (==text==) - 深黄色
        highlight_format = QTextCharFormat()
        highlight_format.setForeground(QColor("#7a6a3a"))
        self.highlighting_rules.append((compile(r'==.+?=='), highlight_format))
        
        # 分割线 (--- 或 ***) - 灰色
        hr_format = QTextCharFormat()
        hr_format.setForeground(QColor("#999999"))
        self.highlighting_rules.append((compile(r'^[-*]{3,}$'), hr_format))
        
        # 数学公式 $...$ - 深蓝色
        math_format = QTextCharFormat()
        math_format.setForeground(QColor("#5a6a8a"))
        self.highlighting_rules.append((compile(r'\$[^$]+\$'), math_format))
        self.highlighting_rules.append((compile(r'\\\([^)]+\\\)'), math_format))
        
        # 公式块标记 $$ - 深蓝色
        mathblock_format = QTextCharFormat()
        mathblock_format.setForeground(QColor("#4a5a7a"))
        mathblock_format.setFontWeight(QFont.Weight.Bold)
        self.highlighting_rules.append((compile(r'^\$\$'), mathblock_format))
        
        # 脚注 [^1] - 深青色
        footnote_format = QTextCharFormat()
        footnote_format.setForeground(QColor("#4a7a7a"))
        self.highlighting_rules.append((compile(r'\[\^\w+\]'), footnote_format))
        
        # 目录标记 [TOC] - 深橙色
        toc_format = QTextCharFormat()
        toc_format.setForeground(QColor("#8a5a4a"))
        toc_format.setFontWeight(QFont.Weight.Bold)
        self.highlighting_rules.append((compile(r'^\[TOC\]$', IGNORECASE), toc_format))
        
        # 上标 ^text^ - 深紫色
        superscript_format = QTextCharFormat()
        superscript_format.setForeground(QColor("#7a5a8a"))
        self.highlighting_rules.append((compile(r'\^[^^]+\^'), superscript_format))
        
        # 下标 ~text~ - 深青色
        subscript_format = QTextCharFormat()
        subscript_format.setForeground(QColor("#5a7a8a"))
        self.highlighting_rules.append((compile(r'~[^~]+~'), subscript_format))
        
        # 表格分隔符 | - 深灰色
        table_format = QTextCharFormat()
        table_format.setForeground(QColor("#6a6a6a"))
        self.highlighting_rules.append((compile(r'^\|.*\|$'), table_format))
        self.highlighting_rules.append((compile(r'^\|[-:| ]+\|$'), table_format))
        
        # 粗斜体 ***text*** - 深棕色加粗斜体
        bolditalic_format = QTextCharFormat()
        bolditalic_format.setForeground(QColor("#6a4a30"))
        bolditalic_format.setFontWeight(QFont.Weight.Bold)
        bolditalic_format.setFontItalic(True)
        self.highlighting_rules.append((compile(r'\*\*\*.+?\*\*\*'), bolditalic_format))
    
    def highlightBlock(self, text):
        """对每个文本块应用高亮规则"""
        for pattern, fmt in self.highlighting_rules:
            try:
                for match in pattern.finditer(text):
                    start = match.start()
                    length = match.end() - start
                    self.setFormat(start, length, fmt)
            except Exception:
                pass  # 忽略正则匹配错误


class MarkdownTextEdit(QTextEdit):
    """自定义Markdown编辑器 - 支持列表自动接续和Tab自动补全"""
    
    def keyPressEvent(self, event):
        """处理键盘事件"""
        # Tab键仅执行自动补全（不再召起悬浮窗）
        if event.key() == Qt.Key.Key_Tab:
            self.handle_tab_completion()
            event.accept()  # 明确接受事件，防止被其他功能拦截
            return  # 不继续默认行为（不插入缩进）
        
        # Ctrl+F - 查找
        if event.key() == Qt.Key.Key_F and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            # 找到主窗口并调用查找方法
            parent = self.parent()
            while parent:
                if hasattr(parent, 'show_find_dialog'):
                    parent.show_find_dialog()
                    event.accept()
                    return
                parent = parent.parent()
            # 如果找不到主窗口，忽略事件（不触发默认查找）
            event.ignore()
            return
        
        # Ctrl+Shift+C - 复制全文
        if event.key() == Qt.Key.Key_C and event.modifiers() == (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier):
            # 找到主窗口并调用复制全文方法
            parent = self.parent()
            while parent:
                if hasattr(parent, 'copy_all_content'):
                    parent.copy_all_content()
                    event.accept()
                    return
                parent = parent.parent()
            # 如果找不到主窗口，忽略事件（不触发默认复制）
            event.ignore()
            return
        
        # 回车键处理列表自动接续
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            if self.handle_list_continuation():
                return  # 已处理，不继续默认行为
        
        # 调用父类默认处理
        super().keyPressEvent(event)
        
    def handle_tab_completion(self):
        """处理Tab自动补全 - 渐进式补全，有上限"""
        cursor = self.textCursor()
        
        # 获取光标前后的文本
        block = cursor.block()
        line_text = block.text()
        col = cursor.positionInBlock()
        
        before_text = line_text[:col]
        after_text = line_text[col:]
        
        if not before_text:
            return
        
        last_char = before_text[-1]
        
        # 定义成对符号及其最大层级
        pair_symbols = {
            '*': ('*', 2),   # 最多 2 层（****），对应 Markdown 斜体/粗体
            '_': ('_', 2),   # 最多 2 层
            '~': ('~', 1),   # 最多 1 层（~~），删除线
            '=': ('=', 1),   # 最多 1 层（==），高亮
            '`': ('`', 1),   # 最多 1 层
            '[': (']', 1),   # 链接只补全一次
            '(': (')', 1),   # 括号只补全一次
            '{': ('}', 1),   # 花括号只补全一次
        }
        
        if last_char in pair_symbols:
            expected_closing, max_level = pair_symbols[last_char]
            
            # 检查光标后面是否有对应的闭合符号（光标在成对符号中间）
            if after_text and after_text[0] == expected_closing:
                # 计算当前已有的符号层级
                current_level = 1
                # 向前数连续的相同符号
                for i in range(len(before_text) - 2, -1, -1):
                    if before_text[i] == last_char:
                        current_level += 1
                    else:
                        break
                
                # 检查是否达到上限
                if current_level >= max_level:
                    return  # 已达上限，不再补全
                
                # 扩展符号：*|* -> **|**
                cursor.insertText(expected_closing + last_char)
                cursor.movePosition(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.MoveAnchor, 1)
                self.setTextCursor(cursor)
            else:
                # 普通补全：* -> *|*
                if last_char == '[':
                    # 链接特殊处理：[ -> []()  光标在 ] 前面
                    cursor.insertText(']()')
                    cursor.movePosition(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.MoveAnchor, 3)
                else:
                    cursor.insertText(expected_closing)
                    cursor.movePosition(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.MoveAnchor, 1)
                self.setTextCursor(cursor)
    
    def handle_list_continuation(self):
        """处理列表自动接续，返回True表示已处理"""
        cursor = self.textCursor()
        
        # 获取当前行内容
        cursor.movePosition(QTextCursor.MoveOperation.StartOfLine, QTextCursor.MoveMode.KeepAnchor)
        line_text = cursor.selectedText()
        cursor = self.textCursor()  # 恢复原始光标
        
        # 检查是否是有序列表
        ordered_match = match(r'^(\s*)(\d+)\.\s(.*)$', line_text)
        if ordered_match:
            indent = ordered_match.group(1)
            number = int(ordered_match.group(2))
            content = ordered_match.group(3)
            
            # 如果当前行内容为空，结束列表
            if not content.strip():
                # 删除当前行的列表标记
                cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
                cursor.movePosition(QTextCursor.MoveOperation.EndOfLine, QTextCursor.MoveMode.KeepAnchor)
                cursor.removeSelectedText()
                cursor.insertText("\n")
                self.setTextCursor(cursor)
                return True
            
            # 插入下一行并自动编号
            next_number = number + 1
            cursor.insertText(f"\n{indent}{next_number}. ")
            self.setTextCursor(cursor)
            return True
        
        # 检查是否是无序列表
        unordered_match = match(r'^(\s*)([-*+])\s(.*)$', line_text)
        if unordered_match:
            indent = unordered_match.group(1)
            marker = unordered_match.group(2)
            content = unordered_match.group(3)
            
            # 如果当前行内容为空，结束列表
            if not content.strip():
                cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
                cursor.movePosition(QTextCursor.MoveOperation.EndOfLine, QTextCursor.MoveMode.KeepAnchor)
                cursor.removeSelectedText()
                cursor.insertText("\n")
                self.setTextCursor(cursor)
                return True
            
            # 插入下一行
            cursor.insertText(f"\n{indent}{marker} ")
            self.setTextCursor(cursor)
            return True
        
        # 检查是否是任务列表
        task_match = match(r'^(\s*)([-*+])\s\[([ x])\]\s(.*)$', line_text)
        if task_match:
            indent = task_match.group(1)
            marker = task_match.group(2)
            content = task_match.group(4)
            
            # 如果当前行内容为空，结束列表
            if not content.strip():
                cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
                cursor.movePosition(QTextCursor.MoveOperation.EndOfLine, QTextCursor.MoveMode.KeepAnchor)
                cursor.removeSelectedText()
                cursor.insertText("\n")
                self.setTextCursor(cursor)
                return True
            
            # 插入下一行（默认未完成）
            cursor.insertText(f"\n{indent}{marker} [ ] ")
            self.setTextCursor(cursor)
            return True
        
        # 检查是否是引用
        quote_match = match(r'^(\s*)(>+)\s(.*)$', line_text)
        if quote_match:
            indent = quote_match.group(1)
            quotes = quote_match.group(2)
            content = quote_match.group(3)
            
            # 如果当前行内容为空，结束引用
            if not content.strip():
                cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
                cursor.movePosition(QTextCursor.MoveOperation.EndOfLine, QTextCursor.MoveMode.KeepAnchor)
                cursor.removeSelectedText()
                cursor.insertText("\n")
                self.setTextCursor(cursor)
                return True
            
            # 插入下一行引用
            cursor.insertText(f"\n{indent}{quotes} ")
            self.setTextCursor(cursor)
            return True
        
        return False  # 未处理，使用默认行为


class ImageInsertDialog(QDialog):
    """图片插入对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_editor = parent
        self.setWindowTitle("插入图片")
        self.setFixedSize(450, 280)
        self.init_ui()
    
    def get_theme(self):
        """获取当前主题"""
        if self.parent_editor and hasattr(self.parent_editor, 'current_theme'):
            return self.parent_editor.current_theme
        return Theme.DARK
    
    def init_ui(self):
        theme = self.get_theme()
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {theme['bg_secondary']};
                border-radius: 0;
            }}
            QLabel {{
                color: {theme['text']};
                font-size: 14px;
                font-weight: 500;
            }}
            QLineEdit {{
                background-color: {theme['bg']};
                color: {theme['text']};
                border: none;
                padding: 10px 14px;
                border-radius: 0;
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border: none;
            }}
            QLineEdit:disabled {{
                background-color: {theme['bg_tertiary']};
                color: {theme['text_secondary']};
            }}
            QRadioButton {{
                color: {theme['text']};
                spacing: 10px;
                font-size: 14px;
            }}
            QRadioButton::indicator {{
                width: 18px;
                height: 18px;
                border: none;
                border-radius: 0;
                background-color: {theme['bg']};
            }}
            QRadioButton::indicator:checked {{
                background-color: {theme['accent']};
                border-color: {theme['accent']};
            }}
            QPushButton {{
                background-color: {theme['bg_secondary']};
                color: {theme['text']};
                border: none;
                padding: 10px 24px;
                border-radius: 0;
                font-weight: 600;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {theme['bg_tertiary']};
                border-color: {theme['border']};
            }}
            QPushButton#browseBtn {{
                background-color: {theme['bg_secondary']};
                color: {theme['text']};
                border: none;
            }}
            QPushButton#browseBtn:hover {{
                background-color: {theme['bg_tertiary']};
                border-color: {theme['border']};
            }}
            QPushButton#cancelBtn {{
                background-color: {theme['bg_secondary']};
                color: {theme['text']};
                border: none;
            }}
            QPushButton#cancelBtn:hover {{
                background-color: {theme['bg_tertiary']};
                border-color: {theme['border']};
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)
        
        # 图片描述
        desc_layout = QHBoxLayout()
        desc_label = QLabel("图片描述：")
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("输入图片的替代文本")
        desc_layout.addWidget(desc_label)
        desc_layout.addWidget(self.desc_input, 1)
        layout.addLayout(desc_layout)
        
        # 来源选择
        source_layout = QHBoxLayout()
        source_label = QLabel("图片来源：")
        self.source_group = QButtonGroup(self)
        self.local_radio = QRadioButton("本地文件")
        self.url_radio = QRadioButton("网络链接")
        self.url_radio.setChecked(True)
        self.source_group.addButton(self.local_radio, 0)
        self.source_group.addButton(self.url_radio, 1)
        source_layout.addWidget(source_label)
        source_layout.addWidget(self.local_radio)
        source_layout.addWidget(self.url_radio)
        source_layout.addStretch()
        layout.addLayout(source_layout)
        
        # 路径/链接输入
        path_layout = QHBoxLayout()
        self.path_label = QLabel("图片链接：")
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("输入图片URL")
        self.browse_btn = QPushButton("浏览...")
        self.browse_btn.setObjectName("browseBtn")
        self.browse_btn.setVisible(False)
        self.browse_btn.clicked.connect(self.browse_file)
        path_layout.addWidget(self.path_label)
        path_layout.addWidget(self.path_input, 1)
        path_layout.addWidget(self.browse_btn)
        layout.addLayout(path_layout)
        
        # 切换来源时更新UI
        self.local_radio.toggled.connect(self.on_source_changed)
        
        layout.addStretch()
        
        # 按钮区
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        cancel_btn = QPushButton("取消")
        cancel_btn.setObjectName("cancelBtn")
        cancel_btn.clicked.connect(self.reject)
        insert_btn = QPushButton("插入")
        insert_btn.clicked.connect(self.accept)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(insert_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def on_source_changed(self, checked):
        """来源切换"""
        if self.local_radio.isChecked():
            self.path_label.setText("文件路径：")
            self.path_input.setPlaceholderText("选择本地图片文件")
            self.browse_btn.setVisible(True)
        else:
            self.path_label.setText("图片链接：")
            self.path_input.setPlaceholderText("输入图片URL")
            self.browse_btn.setVisible(False)
    
    def browse_file(self):
        """浏览本地文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择图片", "",
            "图片文件 (*.png *.jpg *.jpeg *.gif *.bmp *.webp);;所有文件 (*.*)"
        )
        if file_path:
            self.path_input.setText(file_path)
    
    def get_result(self):
        """获取结果"""
        desc = self.desc_input.text() or "图片描述"
        path = self.path_input.text() or "图片地址"
        return f"![{desc}]({path})"


class TableInsertDialog(QDialog):
    """表格插入对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_editor = parent
        self.setWindowTitle("插入表格")
        self.setFixedSize(350, 220)
        self.init_ui()
    
    def get_theme(self):
        if self.parent_editor and hasattr(self.parent_editor, 'current_theme'):
            return self.parent_editor.current_theme
        return Theme.DARK
    
    def init_ui(self):
        theme = self.get_theme()
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {theme['bg_secondary']};
                border-radius: 0;
            }}
            QLabel {{
                color: {theme['text']};
                font-size: 14px;
                font-weight: 500;
            }}
            QSpinBox {{
                background-color: {theme['bg']};
                color: {theme['text']};
                border: none;
                padding: 8px 12px;
                border-radius: 0;
                min-width: 100px;
                font-size: 14px;
            }}
            QSpinBox:focus {{
                border: 2px solid {theme['accent']};
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                width: 24px;
                border: none;
                background-color: {theme['bg_tertiary']};
                border-radius: 0;
            }}
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
                background-color: {theme['accent']};
            }}
            QCheckBox {{
                color: {theme['text']};
                spacing: 10px;
                font-size: 14px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: none;
                border-radius: 0;
                background-color: {theme['bg']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {theme['accent']};
                border-color: {theme['accent']};
            }}
            QPushButton {{
                background-color: {theme['bg_secondary']};
                color: {theme['text']};
                border: none;
                padding: 10px 24px;
                border-radius: 0;
                font-weight: 600;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {theme['bg_tertiary']};
                border-color: {theme['border']};
            }}
            QPushButton#cancelBtn {{
                background-color: {theme['bg_secondary']};
                color: {theme['text']};
                border: none;
            }}
            QPushButton#cancelBtn:hover {{
                background-color: {theme['bg_tertiary']};
                border-color: {theme['border']};
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(28, 28, 28, 24)
        layout.setSpacing(20)
        
        # 行数
        row_layout = QHBoxLayout()
        row_label = QLabel("行数：")
        row_label.setMinimumWidth(70)
        self.row_spin = QSpinBox()
        self.row_spin.setRange(1, 20)
        self.row_spin.setValue(3)
        row_layout.addWidget(row_label)
        row_layout.addWidget(self.row_spin)
        row_layout.addStretch()
        layout.addLayout(row_layout)
        
        # 列数
        col_layout = QHBoxLayout()
        col_label = QLabel("列数：")
        col_label.setMinimumWidth(70)
        self.col_spin = QSpinBox()
        self.col_spin.setRange(1, 10)
        self.col_spin.setValue(3)
        col_layout.addWidget(col_label)
        col_layout.addWidget(self.col_spin)
        col_layout.addStretch()
        layout.addLayout(col_layout)
        
        # 包含表头
        self.header_check = QCheckBox("包含表头行")
        self.header_check.setChecked(True)
        layout.addWidget(self.header_check)
        
        layout.addStretch()
        
        # 按钮区
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        cancel_btn = QPushButton("取消")
        cancel_btn.setObjectName("cancelBtn")
        cancel_btn.clicked.connect(self.reject)
        insert_btn = QPushButton("插入")
        insert_btn.clicked.connect(self.accept)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(insert_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def get_result(self):
        """生成表格Markdown"""
        rows = self.row_spin.value()
        cols = self.col_spin.value()
        has_header = self.header_check.isChecked()
        
        lines = ["\n"]
        
        if has_header:
            # 表头行
            header = "| " + " | ".join([f"列{i+1}" for i in range(cols)]) + " |"
            lines.append(header)
            # 分隔行
            separator = "| " + " | ".join(["---" for _ in range(cols)]) + " |"
            lines.append(separator)
            # 数据行（减1因为表头占一行）
            for r in range(rows - 1):
                row = "| " + " | ".join([f"内容" for _ in range(cols)]) + " |"
                lines.append(row)
        else:
            # 无表头，直接数据行
            for r in range(rows):
                row = "| " + " | ".join([f"内容" for _ in range(cols)]) + " |"
                lines.append(row)
        
        lines.append("\n")
        return "\n".join(lines)


class LinkInsertDialog(QDialog):
    """链接插入对话框"""
    
    def __init__(self, parent=None, selected_text=""):
        super().__init__(parent)
        self.parent_editor = parent
        self.selected_text = selected_text
        self.setWindowTitle("插入链接")
        self.setFixedSize(420, 200)
        self.init_ui()
    
    def get_theme(self):
        if self.parent_editor and hasattr(self.parent_editor, 'current_theme'):
            return self.parent_editor.current_theme
        return Theme.DARK
    
    def init_ui(self):
        theme = self.get_theme()
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {theme['bg_secondary']};
                border-radius: 0;
            }}
            QLabel {{
                color: {theme['text']};
                font-size: 14px;
                font-weight: 500;
            }}
            QLineEdit {{
                background-color: {theme['bg']};
                color: {theme['text']};
                border: none;
                padding: 10px 14px;
                border-radius: 0;
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border: none;
            }}
            QPushButton {{
                background-color: {theme['bg_secondary']};
                color: {theme['text']};
                border: none;
                padding: 10px 24px;
                border-radius: 0;
                font-weight: 600;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {theme['bg_tertiary']};
                border-color: {theme['border']};
            }}
            QPushButton#cancelBtn {{
                background-color: {theme['bg_secondary']};
                color: {theme['text']};
                border: none;
            }}
            QPushButton#cancelBtn:hover {{
                background-color: {theme['bg_tertiary']};
                border-color: {theme['border']};
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)
        
        # 链接文本
        text_layout = QHBoxLayout()
        text_label = QLabel("链接文本：")
        text_label.setMinimumWidth(80)
        self.text_input = QLineEdit()
        self.text_input.setText(self.selected_text)
        self.text_input.setPlaceholderText("显示的文本")
        text_layout.addWidget(text_label)
        text_layout.addWidget(self.text_input, 1)
        layout.addLayout(text_layout)
        
        # 链接URL
        url_layout = QHBoxLayout()
        url_label = QLabel("链接地址：")
        url_label.setMinimumWidth(80)
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://example.com")
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input, 1)
        layout.addLayout(url_layout)
        
        layout.addStretch()
        
        # 按钮区
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        cancel_btn = QPushButton("取消")
        cancel_btn.setObjectName("cancelBtn")
        cancel_btn.clicked.connect(self.reject)
        insert_btn = QPushButton("插入")
        insert_btn.clicked.connect(self.accept)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(insert_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def get_result(self):
        text = self.text_input.text() or "链接文本"
        url = self.url_input.text() or "链接地址"
        return f"[{text}]({url})"


class CodeBlockInsertDialog(QDialog):
    """代码块插入对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_editor = parent
        self.setWindowTitle("插入代码块")
        self.setFixedSize(420, 220)
        self.init_ui()
    
    def get_theme(self):
        if self.parent_editor and hasattr(self.parent_editor, 'current_theme'):
            return self.parent_editor.current_theme
        return Theme.DARK
    
    def init_ui(self):
        theme = self.get_theme()
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {theme['bg_secondary']};
                border-radius: 0;
            }}
            QLabel {{
                color: {theme['text']};
                font-size: 14px;
                font-weight: 500;
            }}
            QComboBox {{
                background-color: {theme['bg']};
                color: {theme['text']};
                border: none;
                padding: 10px 14px;
                border-radius: 0;
                min-width: 200px;
                font-size: 14px;
            }}
            QComboBox:focus {{
                border: 2px solid {theme['accent']};
            }}
            QComboBox:hover {{
                border-color: {theme['accent']};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border: 5px solid transparent;
                border-top: 8px solid {theme['text_secondary']};
                margin-right: 10px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {theme['bg']};
                color: {theme['text']};
                selection-background-color: {theme['accent']};
                selection-color: {theme['accent_text']};
                border: none;
                border-radius: 0;
                padding: 4px;
            }}
            QComboBox QAbstractItemView::item {{
                padding: 8px 12px;
                border-radius: 0;
            }}
            QPushButton {{
                background-color: {theme['bg_secondary']};
                color: {theme['text']};
                border: none;
                padding: 10px 24px;
                border-radius: 0;
                font-weight: 600;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {theme['bg_tertiary']};
                border-color: {theme['border']};
            }}
            QPushButton#cancelBtn {{
                background-color: {theme['bg_secondary']};
                color: {theme['text']};
                border: none;
            }}
            QPushButton#cancelBtn:hover {{
                background-color: {theme['bg_tertiary']};
                border-color: {theme['border']};
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)
        
        # 语言选择
        lang_layout = QHBoxLayout()
        lang_label = QLabel("编程语言：")
        self.lang_combo = QComboBox()
        languages = [
            "（无）", "python", "javascript", "typescript", "java", "c", "cpp", "csharp",
            "go", "rust", "html", "css", "sql", "bash", "powershell",
            "json", "xml", "yaml", "markdown", "plaintext"
        ]
        self.lang_combo.addItems(languages)
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.lang_combo)
        lang_layout.addStretch()
        layout.addLayout(lang_layout)
        
        layout.addStretch()
        
        # 按钮区
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        cancel_btn = QPushButton("取消")
        cancel_btn.setObjectName("cancelBtn")
        cancel_btn.clicked.connect(self.reject)
        insert_btn = QPushButton("插入")
        insert_btn.clicked.connect(self.accept)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(insert_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def get_result(self):
        lang = self.lang_combo.currentText()
        if lang == "（无）":
            lang = ""
        return f"```{lang}\n\n```\n"


class FloatingMarkdownToolbar(QDialog):
    """悬浮Markdown工具栏 - 菜单栏样式，悬停展开"""
    
    def __init__(self, parent=None):
        super().__init__(parent, 
                         Qt.WindowType.Tool | 
                         Qt.WindowType.FramelessWindowHint |
                         Qt.WindowType.WindowDoesNotAcceptFocus)  # 不接受焦点
        self.parent_editor = parent
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)  # 显示时不激活
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)  # 透明背景
        self.current_menu = None  # 跟踪当前显示的菜单
        
        # 添加动画支持（使用缓存，无时间限制）
        self.opacity_animation = AnimationCache.get_animation(
            self, b'windowOpacity', -1, QEasingCurve.Type.Linear, self
        )
        self.move_animation = AnimationCache.get_animation(
            self, b'pos', -1, QEasingCurve.Type.Linear, self
        )
        
        self.init_ui()
    
    def get_theme(self):
        """获取当前主题"""
        if self.parent_editor and hasattr(self.parent_editor, 'current_theme'):
            return self.parent_editor.current_theme
        return Theme.DARK
        
    def init_ui(self):
        """初始化UI - 菜单栏样式"""
        theme = self.get_theme()
        
        # 使用主题颜色
        bg_color = theme['bg']
        text_color = theme['text']
        menu_bg = theme['bg_secondary']
        menu_hover = theme['bg_tertiary']
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {bg_color};
                border: none;
            }}
            QMenuBar {{
                background-color: {bg_color};
                color: {text_color};
                border: none;
                padding: 0px;
                spacing: 0px;
            }}
            QMenuBar::item {{
                background-color: transparent;
                color: {text_color};
                padding: 6px 12px;
                border-radius: 0;
                font-size: 13px;
            }}
            QMenuBar::item:selected, QMenuBar::item:pressed {{
                background-color: {menu_hover};
                color: {text_color};
            }}
            QMenu {{
                background-color: {menu_bg};
                border: none;
                padding: 4px;
            }}
            QMenu::item {{
                background-color: transparent;
                color: {text_color};
                padding: 8px 24px 8px 12px;
                font-size: 13px;
            }}
            QMenu::item:selected {{
                background-color: {menu_hover};
            }}
            QMenu::separator {{
                height: 1px;
                background-color: {theme['border']};
                margin: 4px 8px;
            }}
            QPushButton#closeBtn {{
                background-color: rgba(220, 53, 69, 0.9);
                color: white;
                border: none;
                padding: 4px 10px;
                font-size: 12px;
                font-weight: 600;
            }}
            QPushButton#closeBtn:hover {{
                background-color: rgba(200, 35, 51, 1.0);
            }}
        """)
        
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(0)
        
        # 创建菜单栏
        self.menubar = QMenuBar()
        self.menubar.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        # === 基础格式菜单 ===
        basic_menu = self.menubar.addMenu("📝 基础")
        basic_menu.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        # 标题选项
        for i in range(1, 6):
            action = basic_menu.addAction(f"H{i} - {'#'*i} 标题{i}")
            action.triggered.connect(lambda c, l=i: self.insert_header(l))
        
        basic_menu.addSeparator()
        
        # 格式选项
        format_items = [
            ("🅱️ 粗体  Ctrl+B", "**", "**"),
            ("🅸️ 斜体  Ctrl+I", "*", "*"),
            ("S̶ 删除线  Ctrl+D", "~~", "~~"),
            ("🟡 高亮  Ctrl+H", "==", "=="),
            ("💻 行内代码  Ctrl+`", "`", "`")
        ]
        for text, prefix, suffix in format_items:
            action = basic_menu.addAction(text)
            action.triggered.connect(lambda c, p=prefix, s=suffix: self.insert_format(p, s))
        
        # === 列表引用菜单 ===
        list_menu = self.menubar.addMenu("📝 列表")
        list_menu.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        list_items = [
            ("• 无序列表", "- "),
            ("1. 有序列表", "1. "),
            ("☐ 任务列表", "- [ ] "),
            ("☑ 已完成", "- [x] ")
        ]
        for text, marker in list_items:
            action = list_menu.addAction(text)
            action.triggered.connect(lambda c, m=marker: self.insert_list_marker(m))
        
        list_menu.addSeparator()
        
        quote_items = [
            ("> 一级引用", "> "),
            (">> 二级引用", ">> "),
            (">>> 三级引用", ">>> ")
        ]
        for text, marker in quote_items:
            action = list_menu.addAction(text)
            action.triggered.connect(lambda c, m=marker: self.insert_list_marker(m))
        
        # === 插入元素菜单 ===
        insert_menu = self.menubar.addMenu("➕ 插入")
        insert_menu.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        insert_menu.addAction("🔗 链接").triggered.connect(self.insert_link)
        insert_menu.addAction("🖼️ 图片").triggered.connect(self.insert_image)
        insert_menu.addSeparator()
        insert_menu.addAction("📊 表格").triggered.connect(self.insert_table)
        insert_menu.addAction("💻 代码块").triggered.connect(self.insert_code_block)
        insert_menu.addAction("── 分割线").triggered.connect(self.insert_hr)
        insert_menu.addAction("📑 目录").triggered.connect(self.insert_toc)
        insert_menu.addSeparator()
        insert_menu.addAction("⏰ 时间戳").triggered.connect(self.insert_timestamp)
        insert_menu.addAction("📌 脚注").triggered.connect(self.insert_footnote)
        
        # === LaTeX公式菜单 ===
        latex_menu = self.menubar.addMenu("∑ LaTeX")
        latex_menu.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        latex_menu.addAction("$ 行内公式").triggered.connect(lambda: self.insert_format("$", "$"))
        latex_menu.addAction("$$ 公式块").triggered.connect(self.insert_math_block)
        latex_menu.addSeparator()
        
        # 常用符号子菜单
        symbols_menu = latex_menu.addMenu("🔣 常用符号")
        symbols = [
            ("∑ 求和", "\\sum_{i=1}^{n}"),
            ("∏ 连乘", "\\prod_{i=1}^{n}"),
            ("∫ 积分", "\\int_{a}^{b}"),
            ("√ 根号", "\\sqrt{}"),
            ("÷ 分数", "\\frac{}{}"),
            ("x² 上标", "^{}"),
            ("x₂ 下标", "_{}")
        ]
        for text, template in symbols:
            action = symbols_menu.addAction(text)
            action.triggered.connect(lambda c, t=template: self.insert_latex_template(t))
        
        # 希腊字母子菜单
        greek_menu = latex_menu.addMenu("αβ 希腊字母")
        greeks = [
            ("α alpha", "\\alpha"), ("β beta", "\\beta"),
            ("γ gamma", "\\gamma"), ("δ delta", "\\delta"),
            ("ε epsilon", "\\epsilon"), ("θ theta", "\\theta"),
            ("λ lambda", "\\lambda"), ("μ mu", "\\mu"),
            ("π pi", "\\pi"), ("σ sigma", "\\sigma"),
            ("φ phi", "\\phi"), ("ω omega", "\\omega")
        ]
        for text, template in greeks:
            action = greek_menu.addAction(text)
            action.triggered.connect(lambda c, t=template: self.insert_latex_template(t))
        
        # 关系符号子菜单
        relation_menu = latex_menu.addMenu("≠ 关系符号")
        relations = [
            ("≠ 不等于", "\\neq"),
            ("≈ 约等于", "\\approx"),
            ("≤ 小于等于", "\\leq"),
            ("≥ 大于等于", "\\geq"),
            ("≪ 远小于", "\\ll"),
            ("≫ 远大于", "\\gg"),
            ("∝ 正比于", "\\propto"),
            ("∞ 无穷大", "\\infty")
        ]
        for text, template in relations:
            action = relation_menu.addAction(text)
            action.triggered.connect(lambda c, t=template: self.insert_latex_template(t))
        
        main_layout.addWidget(self.menubar)
        
        # 关闭按钮
        close_btn = QPushButton("✕")
        close_btn.setObjectName("closeBtn")
        close_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        close_btn.setToolTip("关闭工具栏")
        close_btn.setFixedSize(28, 28)
        close_btn.clicked.connect(self.hide)
        main_layout.addWidget(close_btn)
        
        self.setLayout(main_layout)
        self.adjustSize()
    
    def update_theme(self):
        """更新主题样式"""
        theme = self.get_theme()
        
        # 使用主题颜色
        bg_color = theme['bg']
        text_color = theme['text']
        menu_bg = theme['bg_secondary']
        menu_hover = theme['bg_tertiary']
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {bg_color};
                border: none;
            }}
            QMenuBar {{
                background-color: {bg_color};
                color: {text_color};
                border: none;
                padding: 0px;
                spacing: 0px;
            }}
            QMenuBar::item {{
                background-color: transparent;
                color: {text_color};
                padding: 6px 12px;
                border-radius: 0;
                font-size: 13px;
            }}
            QMenuBar::item:selected, QMenuBar::item:pressed {{
                background-color: {menu_hover};
                color: {text_color};
            }}
            QMenu {{
                background-color: {menu_bg};
                border: none;
                padding: 4px;
            }}
            QMenu::item {{
                background-color: transparent;
                color: {text_color};
                padding: 8px 24px 8px 12px;
                font-size: 13px;
            }}
            QMenu::item:selected {{
                background-color: {menu_hover};
            }}
            QMenu::separator {{
                height: 1px;
                background-color: {theme['border']};
                margin: 4px 8px;
            }}
            QPushButton#closeBtn {{
                background-color: rgba(220, 53, 69, 0.9);
                color: white;
                border: none;
                padding: 4px 10px;
                font-size: 12px;
                font-weight: 600;
            }}
            QPushButton#closeBtn:hover {{
                background-color: rgba(200, 35, 51, 1.0);
            }}
        """)
        
    def insert_latex_template(self, template):
        """插入LaTeX模板"""
        editor = self.get_editor()
        if not editor:
            return
        
        cursor = editor.textCursor()
        cursor.insertText(template)
        editor.setTextCursor(cursor)
        editor.setFocus()
    
    def insert_hr(self):
        """插入分割线（别名）"""
        self.insert_separator()
    
    def _create_btn(self, text, callback, tooltip=None):
        """创建按钮，点击后不失去编辑器焦点"""
        btn = QPushButton(text)
        btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)  # 按钮不获取焦点
        btn.clicked.connect(callback)
        if tooltip:
            btn.setToolTip(tooltip)
        return btn
        
    def get_editor(self):
        """获取当前编辑器"""
        if self.parent_editor:
            return self.parent_editor.get_current_editor()
        return None
    
    def show_at_cursor(self):
        """在光标位置显示，避开文本，带动画效果"""
        editor = self.get_editor()
        if not editor:
            return
        
        # 获取光标在屏幕上的位置
        cursor_rect = editor.cursorRect()
        global_pos = editor.mapToGlobal(cursor_rect.bottomLeft())
        
        # 计算工具栏位置（光标下方，左侧对齐）
        x = global_pos.x()
        y = global_pos.y() + 5  # 光标下方留一点5px间距
        
        # 屏幕边界检查
        screen = QApplication.primaryScreen().geometry()
        toolbar_width = self.width() if self.width() > 0 else 350
        toolbar_height = self.height() if self.height() > 0 else 80
        
        # 如果右侧超出屏幕，左移
        if x + toolbar_width > screen.width():
            x = screen.width() - toolbar_width - 10
        
        # 如果下方超出屏幕，显示在光标上方
        if y + toolbar_height > screen.height():
            y = global_pos.y() - cursor_rect.height() - toolbar_height - 5
        
        # 确保不超出左上角
        x = max(10, x)
        y = max(10, y)
        
        # 如果是首次显示，直接移动到目标位置而不使用动画
        if not self.isVisible():
            self.setWindowOpacity(0.0)
            self.move(x, y)  # 直接移动到目标位置
            self.show()  # 显示
            
            # 设置淡入动画
            self.opacity_animation.setStartValue(0.0)
            self.opacity_animation.setEndValue(1.0)
            self.opacity_animation.finished.connect(lambda: self.opacity_animation.finished.disconnect())  # 清理连接
            self.opacity_animation.start()
        else:
            # 如果已经显示，使用移动动画到新位置
            self.move_animation.setStartValue(self.pos())
            self.move_animation.setEndValue(QPoint(x, y))
            self.move_animation.start()
    
    def update_position(self):
        """更新位置跟随光标"""
        if self.isVisible():
            self.show_at_cursor()
    
    def insert_header(self, level):
        """插入标题"""
        editor = self.get_editor()
        if not editor:
            return
        
        cursor = editor.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
        cursor.movePosition(QTextCursor.MoveOperation.EndOfLine, QTextCursor.MoveMode.KeepAnchor)
        line_text = cursor.selectedText()
        
        # 移除已有的标题标记
        cleaned = sub(r'^#+\s*', '', line_text)
        new_text = '#' * level + ' ' + cleaned
        
        cursor.insertText(new_text)
        cursor.movePosition(QTextCursor.MoveOperation.EndOfLine)
        editor.setTextCursor(cursor)
        editor.setFocus()
    
    def insert_format(self, prefix, suffix):
        """插入格式化文本"""
        editor = self.get_editor()
        if not editor:
            return
        
        cursor = editor.textCursor()
        if cursor.hasSelection():
            selected = cursor.selectedText()
            cursor.insertText(f"{prefix}{selected}{suffix}")
        else:
            cursor.insertText(f"{prefix}{suffix}")
            cursor.movePosition(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.MoveAnchor, len(suffix))
            editor.setTextCursor(cursor)
        editor.setFocus()
    
    def insert_list_marker(self, marker):
        """插入列表标记"""
        editor = self.get_editor()
        if not editor:
            return
        
        cursor = editor.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
        cursor.movePosition(QTextCursor.MoveOperation.EndOfLine, QTextCursor.MoveMode.KeepAnchor)
        line_text = cursor.selectedText()
        
        # 移除已有的列表标记
        cleaned = sub(r'^([-*+]\s+|\d+\.\s+|[-*+]\s+\[[x ]\]\s+|>\s+)', '', line_text)
        new_text = marker + cleaned
        
        cursor.insertText(new_text)
        cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
        cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.MoveAnchor, len(marker))
        editor.setTextCursor(cursor)
        editor.setFocus()
    
    def insert_link(self):
        """插入链接 - 使用对话框"""
        editor = self.get_editor()
        if not editor:
            return
        
        # 获取选中文本作为默认链接文本
        cursor = editor.textCursor()
        selected_text = cursor.selectedText() if cursor.hasSelection() else ""
        
        dialog = LinkInsertDialog(self.parent_editor, selected_text)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            result = dialog.get_result()
            cursor.insertText(result)
            editor.setTextCursor(cursor)
        editor.setFocus()
    
    def insert_image(self):
        """插入图片 - 使用对话框"""
        editor = self.get_editor()
        if not editor:
            return
        
        dialog = ImageInsertDialog(self.parent_editor)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            result = dialog.get_result()
            cursor = editor.textCursor()
            cursor.insertText(result)
            editor.setTextCursor(cursor)
        editor.setFocus()
    
    def insert_table(self):
        """插入表格 - 使用对话框"""
        editor = self.get_editor()
        if not editor:
            return
        
        dialog = TableInsertDialog(self.parent_editor)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            result = dialog.get_result()
            cursor = editor.textCursor()
            cursor.insertText(result)
            editor.setTextCursor(cursor)
        editor.setFocus()
    
    def insert_code_block(self):
        """插入代码块 - 使用对话框"""
        editor = self.get_editor()
        if not editor:
            return
        
        dialog = CodeBlockInsertDialog(self.parent_editor)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            result = dialog.get_result()
            cursor = editor.textCursor()
            cursor.insertText(result)
            # 将光标移动到代码块内部
            cursor.movePosition(QTextCursor.MoveOperation.Up, QTextCursor.MoveMode.MoveAnchor, 2)
            editor.setTextCursor(cursor)
        editor.setFocus()
    
    def insert_timestamp(self):
        """插入时间戳"""
        editor = self.get_editor()
        if not editor:
            return
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor = editor.textCursor()
        cursor.insertText(f"[{timestamp}] ")
        editor.setFocus()
    
    def insert_separator(self):
        """插入分割线"""
        editor = self.get_editor()
        if not editor:
            return
        
        cursor = editor.textCursor()
        cursor.insertText("\n---\n\n")
        editor.setFocus()
    
    def insert_math_block(self):
        """插入数学公式块 $$...$$"""
        editor = self.get_editor()
        if not editor:
            return
        
        cursor = editor.textCursor()
        cursor.insertText("\n$$\n\n$$\n")
        cursor.movePosition(QTextCursor.MoveOperation.Up, QTextCursor.MoveMode.MoveAnchor, 2)
        editor.setTextCursor(cursor)
        editor.setFocus()
    
    def insert_footnote(self):
        """插入脚注"""
        editor = self.get_editor()
        if not editor:
            return
        
        cursor = editor.textCursor()
        # 插入脚注引用和脚注内容
        cursor.insertText("[^1]\n\n[^1]: 脚注内容")
        editor.setTextCursor(cursor)
        editor.setFocus()
    
    def hide_animated(self):
        """带动画的隐藏方法"""
        # 设置淡出动画
        self.opacity_animation.setStartValue(1.0)
        self.opacity_animation.setEndValue(0.0)
        self.opacity_animation.finished.connect(self._on_opacity_animation_finished)
        self.opacity_animation.start()
    
    def _on_opacity_animation_finished(self):
        """淡出动画完成后的回调"""
        # 断开连接以避免重复调用
        try:
            self.opacity_animation.finished.disconnect(self._on_opacity_animation_finished)
        except (TypeError, RuntimeError):
            pass
        self.hide()  # 真正隐藏窗口
    
    def insert_toc(self):
        """插入目录"""
        editor = self.get_editor()
        if not editor:
            return
        
        cursor = editor.textCursor()
        cursor.insertText("[TOC]\n\n")
        editor.setTextCursor(cursor)
        editor.setFocus()
    

class TimeProgressBar(QWidget):
    """时间进度条控件 - 显示一天中时间的流逝"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(3)  # 设置固定高度为3像素
        self.parent_editor = parent
        
        # 创建定时器更新进度
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(60000)  # 每分钟更新一次
        
        # 初始更新
        self.update_progress()
    
    def set_theme(self, theme):
        """设置主题"""
        # 直接更新颜色值以确保主题变化立即生效
        self.cached_bg_color = theme.get('bg_tertiary', '#2d2d2d')
        self.cached_accent_color = theme.get('accent', '#e67e22')
        # 使用区域更新，只更新整个控件区域
        self.update(self.rect())
    
    def update_progress(self):
        """更新进度"""
        # 使用区域更新，只更新整个控件区域
        self.update(self.rect())
    
    def paintEvent(self, event):
        """绘制进度条（优化：减少计算，使用缓存）"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 获取当前时间（优化：缓存秒数，减少重复计算）
        now = datetime.now()
        current_seconds = (now.hour * 3600) + (now.minute * 60) + now.second
        
        # 缓存进度值，避免重复计算
        if not hasattr(self, '_cached_seconds') or self._cached_seconds != current_seconds:
            self._cached_seconds = current_seconds
            total_seconds_in_day = 24 * 60 * 60  # 一天的总秒数
            self._cached_progress = current_seconds / total_seconds_in_day
        
        progress = self._cached_progress
        
        # 绘制背景 - 使用缓存的颜色值
        bg_color = getattr(self, 'cached_bg_color', '#2d2d2d')
        painter.fillRect(self.rect(), QColor(bg_color))
        
        # 计算进度条宽度（优化：缓存宽度，避免重复计算）
        widget_width = self.width()
        if not hasattr(self, '_cached_width') or self._cached_width != widget_width:
            self._cached_width = widget_width
        
        progress_width = int(widget_width * progress)
        
        # 绘制进度
        if progress_width > 0:
            progress_rect = QRect(0, 0, progress_width, self.height())
            accent_color = getattr(self, 'cached_accent_color', '#e67e22')
            painter.fillRect(progress_rect, QColor(accent_color))


class FileWorkerThread(QThread):
    """文件操作工作线程 - 处理文件读写，避免阻塞GUI"""
    file_read = pyqtSignal(str, str)  # 文件路径, 内容
    file_written = pyqtSignal(str)  # 文件路径
    error_occurred = pyqtSignal(str)  # 错误信息
    
    def __init__(self, operation, file_path, content=None):
        super().__init__()
        self.operation = operation  # 'read' 或 'write'
        self.file_path = file_path
        self.content = content
    
    def run(self):
        """在工作线程中执行文件操作"""
        try:
            if self.operation == 'read':
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.file_read.emit(self.file_path, content)
            elif self.operation == 'write':
                with open(self.file_path, 'w', encoding='utf-8') as f:
                    f.write(self.content)
                self.file_written.emit(self.file_path)
        except Exception as e:
            self.error_occurred.emit(str(e))


class MarkdownRenderThread(QThread):
    """Markdown渲染工作线程 - 处理Markdown到HTML的转换，避免阻塞GUI"""
    html_ready = pyqtSignal(str, int)  # HTML内容, tab_id
    error_occurred = pyqtSignal(str)  # 错误信息
    
    def __init__(self, content, tab_id, markdown_to_html_func):
        super().__init__()
        self.content = content
        self.tab_id = tab_id
        self.markdown_to_html_func = markdown_to_html_func  # 完整的转换函数（包含wrap_html_with_style）
    
    def run(self):
        """在工作线程中执行Markdown渲染"""
        try:
            # 执行Markdown转换（markdown_to_html_func已经包含了完整的转换流程）
            html = self.markdown_to_html_func(self.content)
            self.html_ready.emit(html, self.tab_id)
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.error_occurred.emit(str(e))


# ==================== 基于 moveToThread 的工作线程模式 ====================

class WorkerThread(QThread):
    """通用工作线程 - 配合 Worker 对象使用 moveToThread 模式"""
    started_signal = pyqtSignal()  # 启动信号，用于触发工作
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
    
    def set_worker(self, worker):
        """设置工作对象并移动到线程"""
        self.worker = worker
        worker.moveToThread(self)
        # 连接启动信号到工作对象的执行方法
        self.started_signal.connect(worker.execute)
        # 工作完成后退出线程
        worker.finished.connect(self.quit)
    
    def run(self):
        """启动事件循环并触发工作"""
        self.started_signal.emit()
        self.exec()


class BaseWorker(QObject):
    """基础工作对象 - 继承此类创建具体的工作类"""
    finished = pyqtSignal()  # 任务完成信号
    error_occurred = pyqtSignal(str)  # 错误信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._thread = None
    
    def start_work(self, thread=None):
        """
        启动工作线程并执行任务（立即迁出主线程）
        
        Args:
            thread: 可选，如果提供则使用该线程，否则创建新线程
        Returns:
            QThread: 工作线程实例
        """
        if thread is None:
            self._thread = WorkerThread()
        else:
            self._thread = thread
        
        self._thread.set_worker(self)
        self._thread.finished.connect(self._on_thread_finished)
        self._thread.start()  # 立即启动线程，任务立即迁出主线程
        return self._thread
    
    def stop_work(self):
        """停止工作线程"""
        if self._thread and self._thread.isRunning():
            self._thread.quit()
            self._thread.wait()
    
    def _on_thread_finished(self):
        """线程完成回调"""
        if self._thread:
            self._thread.deleteLater()
            self._thread = None
    
    def execute(self):
        """执行任务（在工作线程中调用，子类必须实现）"""
        raise NotImplementedError("子类必须实现 execute 方法")


class TaskWorker(BaseWorker):
    """通用任务工作对象 - 执行任意耗时任务"""
    result_ready = pyqtSignal(object)  # 结果就绪信号
    progress_updated = pyqtSignal(int)  # 进度更新信号（0-100）
    
    def __init__(self, task_func, *args, **kwargs):
        """
        初始化任务工作对象
        
        Args:
            task_func: 要执行的函数
            *args: 传递给任务函数的参数
            **kwargs: 传递给任务函数的关键字参数
        """
        super().__init__()
        self.task_func = task_func
        self.task_args = args
        self.task_kwargs = kwargs
    
    def execute(self):
        """执行任务（在工作线程中调用）"""
        try:
            result = self.task_func(*self.task_args, **self.task_kwargs)
            self.result_ready.emit(result)
            self.finished.emit()
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.error_occurred.emit(str(e))
            self.finished.emit()


class HeavyTaskWorker(BaseWorker):
    """耗时任务工作对象 - 示例：执行耗时计算"""
    result_ready = pyqtSignal(object)  # 结果就绪信号
    progress_updated = pyqtSignal(int)  # 进度更新信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._task_data = None
    
    def set_task_data(self, data):
        """设置任务数据（在主线程中调用）"""
        self._task_data = data
    
    def execute(self):
        """执行耗时任务（在工作线程中调用）"""
        try:
            # 在这里执行耗时操作
            # 示例：模拟耗时计算
            result = self._process_data(self._task_data)
            self.result_ready.emit(result)
            self.finished.emit()
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.error_occurred.emit(str(e))
            self.finished.emit()
    
    def _process_data(self, data):
        """处理数据的实际逻辑（在工作线程中执行）"""
        # 在这里实现具体的耗时任务逻辑
        # 例如：大量数据处理、文件操作、网络请求等
        return data


# ==================== 动画优化工作线程 ====================

class AnimationStyleWorker(BaseWorker):
    """动画样式计算工作对象 - 在工作线程中计算样式表，避免阻塞主线程"""
    style_ready = pyqtSignal(object, str)  # 样式就绪信号 (button, style)
    
    def __init__(self, button, original_style, theme, hover):
        """
        初始化动画样式工作对象
        
        Args:
            button: 按钮对象（仅用于标识，不直接操作）
            original_style: 原始样式表
            theme: 主题字典
            hover: 是否悬停
        """
        super().__init__()
        self.button_id = id(button)  # 使用对象ID作为标识
        self.original_style = original_style
        self.theme = theme
        self.hover = hover
    
    def execute(self):
        """计算样式表（在工作线程中执行）"""
        try:
            style = self._calculate_style()
            self.style_ready.emit(self.button_id, style)
            self.finished.emit()
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.error_occurred.emit(str(e))
            self.finished.emit()
    
    def _calculate_style(self):
        """计算样式表（耗时操作在工作线程中执行）"""
        if self.hover:
            # 悬停：添加视觉反馈
            hover_style = self.original_style + f"""
                border: 2px solid {self.theme.get('accent', self.theme.get('border', '#666'))};
                background-color: {self.theme.get('bg_tertiary', self.theme.get('bg_secondary', '#333'))};
            """
            return hover_style
        else:
            # 离开：返回原始样式
            return self.original_style


class AnimationValueWorker(BaseWorker):
    """动画值计算工作对象 - 在工作线程中预计算动画值"""
    values_ready = pyqtSignal(list)  # 动画值列表就绪信号
    
    def __init__(self, start_value, end_value, duration, easing_curve, steps=60):
        """
        初始化动画值计算工作对象
        
        Args:
            start_value: 起始值
            end_value: 结束值
            duration: 动画时长（毫秒）
            easing_curve: 缓动曲线类型
            steps: 计算步数（默认60，对应60fps）
        """
        super().__init__()
        self.start_value = start_value
        self.end_value = end_value
        self.duration = duration
        self.easing_curve = easing_curve
        self.steps = steps
    
    def execute(self):
        """计算动画值（在工作线程中执行）"""
        try:
            values = self._calculate_animation_values()
            self.values_ready.emit(values)
            self.finished.emit()
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.error_occurred.emit(str(e))
            self.finished.emit()
    
    def _calculate_animation_values(self):
        """计算动画值序列（耗时操作在工作线程中执行）"""
        values = []
        easing = QEasingCurve(self.easing_curve)
        
        for i in range(self.steps + 1):
            progress = i / self.steps
            eased_progress = easing.valueForProgress(progress)
            value = self.start_value + (self.end_value - self.start_value) * eased_progress
            values.append(value)
        
        return values


class AnimationFrameWorker(BaseWorker):
    """动画帧预计算工作对象 - 在工作线程中预计算动画帧，减少主线程卡顿"""
    frame_ready = pyqtSignal(int, float)  # 帧就绪信号 (frame_index, value)
    frames_complete = pyqtSignal(list)  # 所有帧计算完成信号
    
    def __init__(self, start_value, end_value, easing_curve, total_frames=60):
        """
        初始化动画帧预计算工作对象
        
        Args:
            start_value: 起始值
            end_value: 结束值
            easing_curve: 缓动曲线类型
            total_frames: 总帧数（默认60，对应60fps）
        """
        super().__init__()
        self.start_value = start_value
        self.end_value = end_value
        self.easing_curve = easing_curve
        self.total_frames = total_frames
    
    def execute(self):
        """预计算动画帧（在工作线程中执行）"""
        try:
            frames = []
            easing = QEasingCurve(self.easing_curve)
            
            for i in range(self.total_frames + 1):
                progress = i / self.total_frames
                eased_progress = easing.valueForProgress(progress)
                value = self.start_value + (self.end_value - self.start_value) * eased_progress
                frames.append(value)
                # 每计算一帧就发送一次信号（可选，用于实时更新）
                # self.frame_ready.emit(i, value)
            
            # 所有帧计算完成后一次性发送
            self.frames_complete.emit(frames)
            self.finished.emit()
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.error_occurred.emit(str(e))
            self.finished.emit()


class ThrottledAnimationUpdater(QObject):
    """节流动画更新器 - 限制动画更新频率，减少卡顿"""
    update_requested = pyqtSignal(float)  # 更新请求信号
    
    def __init__(self, update_func, min_interval_ms=16, parent=None):
        """
        初始化节流动画更新器
        
        Args:
            update_func: 更新函数
            min_interval_ms: 最小更新间隔（毫秒），默认16ms（60fps）
            parent: 父对象
        """
        super().__init__(parent)
        self.update_func = update_func
        self.min_interval_ms = min_interval_ms
        self.last_update_time = 0
        self.pending_value = None
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self._do_update)
        
        # 连接更新请求信号
        self.update_requested.connect(self._on_update_requested)
    
    def _on_update_requested(self, value):
        """处理更新请求"""
        current_time = QTime.currentTime().msecsSinceStartOfDay()
        elapsed = current_time - self.last_update_time
        
        self.pending_value = value
        
        if elapsed >= self.min_interval_ms:
            # 立即更新
            self._do_update()
        else:
            # 延迟更新
            if not self.timer.isActive():
                self.timer.start(self.min_interval_ms - elapsed)
    
    def _do_update(self):
        """执行更新"""
        if self.pending_value is not None:
            self.update_func(self.pending_value)
            self.pending_value = None
            self.last_update_time = QTime.currentTime().msecsSinceStartOfDay()


class AnimationCache:
    """动画缓存管理器 - 缓存动画对象和预计算的动画值，提高性能"""
    
    _instance = None
    _animation_cache = {}  # 动画对象缓存 {(target, property, duration, easing): animation}
    _value_cache = {}  # 动画值缓存 {(start, end, duration, easing, steps): [values]}
    _max_cache_size = 100  # 最大缓存数量
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def get_animation(cls, target, property_name, duration, easing_curve, parent=None):
        """
        获取或创建动画对象（带缓存）
        
        Args:
            target: 动画目标对象
            property_name: 属性名称（bytes类型，如 b'opacity'）
            duration: 动画时长（毫秒）
            easing_curve: 缓动曲线类型
            parent: 父对象
            
        Returns:
            QPropertyAnimation: 动画对象
        """
        # 创建缓存键
        cache_key = (id(target), property_name, duration, easing_curve)
        
        # 检查缓存
        if cache_key in cls._animation_cache:
            animation = cls._animation_cache[cache_key]
            # 检查动画对象是否仍然有效
            if animation.parent() == parent or (parent is None and animation.parent() is None):
                # 重置动画状态
                if animation.state() == QAbstractAnimation.State.Running:
                    animation.stop()
                return animation
        
        # 创建新动画
        animation = QPropertyAnimation(target, property_name, parent)
        animation.setDuration(duration)
        animation.setEasingCurve(easing_curve)
        
        # 设置更新间隔
        if hasattr(animation, 'setUpdateInterval'):
            animation.setUpdateInterval(_ui_update_interval)
        
        # 添加到缓存
        cls._animation_cache[cache_key] = animation
        
        # 限制缓存大小
        if len(cls._animation_cache) > cls._max_cache_size:
            # 移除最旧的缓存项（简单策略：移除第一个）
            oldest_key = next(iter(cls._animation_cache))
            del cls._animation_cache[oldest_key]
        
        return animation
    
    @classmethod
    def get_animation_values(cls, start_value, end_value, duration, easing_curve, steps=60):
        """
        获取预计算的动画值序列（带缓存）
        
        Args:
            start_value: 起始值
            end_value: 结束值
            duration: 动画时长（毫秒）
            easing_curve: 缓动曲线类型
            steps: 计算步数（默认60，对应60fps）
            
        Returns:
            list: 动画值序列
        """
        # 创建缓存键
        cache_key = (start_value, end_value, duration, easing_curve, steps)
        
        # 检查缓存
        if cache_key in cls._value_cache:
            return cls._value_cache[cache_key]
        
        # 计算动画值
        values = []
        easing = QEasingCurve(easing_curve)
        
        for i in range(steps + 1):
            progress = i / steps
            eased_progress = easing.valueForProgress(progress)
            value = start_value + (end_value - start_value) * eased_progress
            values.append(value)
        
        # 添加到缓存
        cls._value_cache[cache_key] = values
        
        # 限制缓存大小
        if len(cls._value_cache) > cls._max_cache_size:
            # 移除最旧的缓存项
            oldest_key = next(iter(cls._value_cache))
            del cls._value_cache[oldest_key]
        
        return values
    
    @classmethod
    def clear_cache(cls):
        """清空所有缓存"""
        cls._animation_cache.clear()
        cls._value_cache.clear()
    
    @classmethod
    def get_cache_stats(cls):
        """获取缓存统计信息"""
        return {
            'animation_count': len(cls._animation_cache),
            'value_count': len(cls._value_cache),
            'max_size': cls._max_cache_size
        }


# ==================== 使用示例 ====================
"""
使用 moveToThread 模式的示例：

# 示例1：使用 TaskWorker 执行任意函数
def heavy_computation(data):
    # 耗时操作
    import time
    time.sleep(2)
    return data * 2

worker = TaskWorker(heavy_computation, 100)
worker.result_ready.connect(lambda result: print(f"结果: {result}"))
worker.error_occurred.connect(lambda err: print(f"错误: {err}"))
worker.start_work()  # 立即迁出主线程

# 示例2：使用 HeavyTaskWorker 执行自定义任务
worker = HeavyTaskWorker()
worker.set_task_data({"key": "value"})
worker.result_ready.connect(lambda result: print(f"结果: {result}"))
worker.error_occurred.connect(lambda err: print(f"错误: {err}"))
worker.start_work()  # 立即迁出主线程

# 示例3：自定义 Worker 类
class MyCustomWorker(BaseWorker):
    result_ready = pyqtSignal(str)
    
    def __init__(self, data):
        super().__init__()
        self.data = data
    
    def execute(self):
        # 在工作线程中执行
        result = self.process(self.data)
        self.result_ready.emit(result)
        self.finished.emit()
    
    def process(self, data):
        # 耗时操作
        return f"处理后的数据: {data}"

worker = MyCustomWorker("测试数据")
worker.result_ready.connect(lambda r: print(r))
worker.start_work()  # 立即迁出主线程

# 示例4：使用动画样式工作线程
worker = AnimationStyleWorker(button, original_style, theme, True)
worker.style_ready.connect(lambda btn_id, style: apply_style(btn_id, style))
worker.start_work()  # 立即迁出主线程
"""


class MarkdownEditor(QMainWindow):
    """Markdo 主窗口"""

    def __init__(self):
        super().__init__()
        self.tabs = {}  # 存储所有标签页
        self.current_tab_id = 0
        self.markdown_toolbar_widget = None  # 左侧Markdown工具栏
        self._updating_preview = False  # 预览更新标志，避免在更新期间进行滚动同步
        self._syncing_scroll = False  # 滚动同步标志，防止循环触发
        self._last_sync_time = 0  # 最后一次同步的时间戳，用于快速滚动时的优化
        
        # 工作线程引用（用于清理）
        self._file_worker_thread = None
        self._markdown_render_thread = None
            
        # 添加动画支持（使用缓存）
        self.window_opacity_animation = AnimationCache.get_animation(
            self, b'windowOpacity', WINDOW_FADE_DURATION, QEasingCurve.Type.OutCubic, self
        )
        
        # 主题切换动画相关
        self._theme_switch_overlay = None  # 主题切换覆盖层
        self._is_switching_theme = False  # 是否正在切换主题
        self._theme_switch_animation_group = None  # 主题切换动画组
            
        # 窗口移动相关属性
        self.move_flag = False
        self.window_origin_x = 0
        self.window_origin_y = 0
        self.mouse_origin_x = 0
        self.mouse_origin_y = 0
            
        # 窗口调整大小相关属性
        self.resize_flag = False
        self.resize_edge = None  # 'left', 'right', 'top', 'bottom', 'top-left', 'top-right', 'bottom-left', 'bottom-right'
        self.window_origin_width = 0
        self.window_origin_height = 0
        self.resize_border_width = RESIZE_BORDER_WIDTH
        
        # 小窗口模式相关属性
        self.view_mode = 'editor'  # 'editor' 或 'preview'，表示小窗口模式下当前显示的视图
        self.toggle_button = None  # 切换按钮
            
        # 加载设置 - 使用 INI 格式，避免打包后注册表权限问题
        self.settings = QSettings(QSettings.Format.IniFormat, QSettings.Scope.UserScope, "Markdo", "Settings")
        # 加载黑夜和白天主题设置
        self.dark_theme_name = self.settings.value("theme/dark", "dark", type=str)
        self.light_theme_name = self.settings.value("theme/light", "morandi_pink", type=str)
        # 为了兼容旧版本，如果存在旧的theme设置，则使用它
        legacy_theme = self.settings.value("theme", None, type=str)
        if legacy_theme and not self.settings.contains("theme/dark"):
            # 如果存在旧设置但没有新设置，则迁移
            if legacy_theme == "dark":
                self.dark_theme_name = legacy_theme
            else:
                self.light_theme_name = legacy_theme
        
        # 加载主题模式
        self.theme_mode = self.settings.value("theme/mode", "auto", type=str)
        
        # 自动切换主题设置
        self.auto_theme_switch = self.settings.value("theme/auto_switch", False, type=bool)
        self.night_start_time = self.settings.value("theme/night_start", DEFAULT_NIGHT_START, type=str)
        self.night_end_time = self.settings.value("theme/night_end", DEFAULT_NIGHT_END, type=str)
        
        # 根据主题模式确定初始主题名称
        initial_theme_name = self.dark_theme_name  # 默认值
        if self.theme_mode == "light":
            initial_theme_name = self.light_theme_name
        elif self.theme_mode == "dark":
            initial_theme_name = self.dark_theme_name
        elif self.theme_mode == "auto":
            # 如果是自动模式，根据当前时间段判断
            if self.auto_theme_switch:
                # 如果启用了自动切换，稍后会通过定时器检查
                initial_theme_name = self.dark_theme_name  # 临时使用默认值
            else:
                # 如果没有启用自动切换，根据当前时间段判断
                try:
                    current_time = datetime.now().time()
                    night_start_t = datetime.strptime(self.night_start_time, "%H:%M").time()
                    night_end_t = datetime.strptime(self.night_end_time, "%H:%M").time()
                    
                    # 判断是否在黑夜模式时间段内
                    is_night_time = False
                    if night_start_t > night_end_t:
                        is_night_time = current_time >= night_start_t or current_time < night_end_t
                    elif night_start_t < night_end_t:
                        is_night_time = night_start_t <= current_time < night_end_t
                    else:
                        is_night_time = True
                    
                    initial_theme_name = self.dark_theme_name if is_night_time else self.light_theme_name
                except (ValueError, AttributeError):
                    # 如果时间解析失败，默认使用黑夜主题
                    initial_theme_name = self.dark_theme_name
        
        # 设置初始主题
        self.current_theme = Theme.get_theme(initial_theme_name)
        # 确保 current_theme_name 与 current_theme 一致（如果主题名称无效，get_theme 会返回默认主题）
        self.current_theme_name = self.current_theme.get('name', initial_theme_name)
        
        # 初始化颜色实例变量
        self._update_theme_colors()
        
        # 初始化主题模式实例变量
        self.is_dark_theme = self.current_theme.get('is_dark', False)
        
        self.toolbar_hotkey = self.settings.value("toolbar/hotkey", DEFAULT_TOOLBAR_HOTKEY, type=str)
        self.editor_font_size = self.settings.value("editor/font_size", DEFAULT_EDITOR_FONT_SIZE, type=int)
        self.sync_scroll_enabled = self.settings.value("sync_scroll", True, type=bool)
            
        # 创建主题切换定时器
        self.theme_check_timer = QTimer(self)
        self.theme_check_timer.timeout.connect(self.check_and_switch_theme)
        if self.auto_theme_switch:
            self.theme_check_timer.start(THEME_CHECK_INTERVAL)
            # 立即检查一次，确保启动时就能正确应用主题
            QTimer.singleShot(100, self.check_and_switch_theme)
            
        # 设置无边框窗口
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
            
        # 设置窗口初始透明度为0，准备淡入动画
        self.setWindowOpacity(0.0)
        
        # 在创建UI之前先应用基础主题样式表，确保组件创建时使用正确的主题
        base_stylesheet = Theme.get_app_stylesheet(self.current_theme)
        window_style = f"""
            QMainWindow {{
                background-color: {self.bg_color};
                border: none;
                border-radius: 12px;
            }}
            QWidget#centralWidget {{
                background-color: {self.bg_color};
                border-radius: 12px;
            }}
        """
        self.setStyleSheet(base_stylesheet + window_style)
            
        self.init_ui()
            
        # 设置快捷键（在UI初始化之后）
        self.setup_shortcuts()
        self.setup_toolbar_shortcut()  # 设置工具栏快捷键
            
        # 应用主题（在标题栏创建之后）
        if self.theme_mode == "auto":
            # 跟随时间自动切换模式
            if self.auto_theme_switch:
                self.check_and_switch_theme()
            else:
                # 根据当前时间段应用对应的主题
                try:
                    current_time = datetime.now().time()
                    night_start_t = datetime.strptime(self.night_start_time, "%H:%M").time()
                    night_end_t = datetime.strptime(self.night_end_time, "%H:%M").time()
                    
                    # 判断是否在黑夜模式时间段内
                    is_night_time = False
                    if night_start_t > night_end_t:
                        is_night_time = current_time >= night_start_t or current_time < night_end_t
                    elif night_start_t < night_end_t:
                        is_night_time = night_start_t <= current_time < night_end_t
                    else:
                        is_night_time = True
                    
                    # 根据时间段应用对应主题
                    target_theme = self.dark_theme_name if is_night_time else self.light_theme_name
                    self.apply_theme(target_theme, animated=False, force=True)  # 初始化时强制应用
                except (ValueError, AttributeError):
                    # 如果时间解析失败，默认使用黑夜主题
                    self.apply_theme(self.dark_theme_name, animated=False, force=True)  # 初始化时强制应用
        elif self.theme_mode == "light":
            # 始终使用白天主题
            self.apply_theme(self.light_theme_name, animated=False, force=True)  # 初始化时强制应用
        elif self.theme_mode == "dark":
            # 始终使用黑夜主题
            self.apply_theme(self.dark_theme_name, animated=False, force=True)  # 初始化时强制应用
            
        # 显示开屏教程（首次启动或未禁用）
        if self.settings.value("show_welcome", True, type=bool):
            # 延迟显示，确保窗口完全加载后再显示对话框
            QTimer.singleShot(500, self.show_welcome)
            
        # 执行淡入动画
        QTimer.singleShot(50, self._start_window_fade_in)
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("Markdo")
        # 设置窗口图标
        app_icon = get_app_icon()
        if not app_icon.isNull():
            self.setWindowIcon(app_icon)
        self.setGeometry(100, 100, DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)
        self.setMinimumSize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
        
        # 创建中心部件
        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 创建自定义标题栏（在最上方）
        self.title_bar = CustomTitleBar(self)
        main_layout.addWidget(self.title_bar)
        
        # 创建菜单栏（作为普通widget添加到布局中）
        self.create_menu_bar()
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        
        # 连接标签页切换信号，更新字数统计
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
        # 创建工具栏（放在菜单栏下方、编辑窗口上方）
        self.create_toolbar()
        
        # 创建水平布局：左侧Markdown工具栏 + 右侧标签页
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(10)  # 工具栏和编辑窗之间10px间距
        
        # 创建左侧Markdown工具栏
        self.create_markdown_toolbar()
        content_layout.addWidget(self.markdown_toolbar_widget)
        
        # 将标签页添加到右侧
        content_layout.addWidget(self.tab_widget)
        
        # 将内容布局添加到主布局
        main_layout.addLayout(content_layout)
        
        # 创建时间进度条 - 紧贴窗口底部
        self.time_progress_bar = TimeProgressBar()
        self.time_progress_bar.set_theme(self.current_theme)
        
        # 将时间进度条添加到底部
        main_layout.addWidget(self.time_progress_bar)
        
        # 创建状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # 创建字数统计标签
        self.word_count_label = QLabel()
        self.word_count_label.setStyleSheet(f"color: {self.text_secondary_color}; font-size: 12px; background-color: transparent;")
        self.status_bar.addWidget(self.word_count_label)
        
        self.show_status_message_temporarily("就绪", 2000)

        # 创建切换按钮（初始隐藏，只在窗口宽度小于900时显示）
        # 按钮作为主窗口的子控件，这样可以在任何标签页上显示
        self.toggle_button = QPushButton("👁️", self)  # 使用眼睛图标表示预览
        self.toggle_button.setObjectName("toggleButton")
        self.toggle_button.setFixedSize(35, 35)
        self.toggle_button.setToolTip("切换编辑/预览视图")  # 添加工具提示
        self.toggle_button.hide()  # 默认隐藏
        self.toggle_button.clicked.connect(self.toggle_view_mode)
        # 设置按钮样式
        self.update_toggle_button_style()
        
        # 创建第一个标签页
        self.create_new_tab()
        
        # 确保编辑器字体大小正确设置（延迟执行，确保在主题应用后也能正确设置）
        QTimer.singleShot(100, lambda: self._ensure_editor_font_sizes())
        
        # 初始化字数统计显示
        QTimer.singleShot(100, self.update_word_count_display)
        
        # 初始检查窗口大小
        QTimer.singleShot(100, self.update_layout_for_width)
        # 确保在窗口显示后再次检查，以处理可能的布局问题
        QTimer.singleShot(300, self.update_layout_for_width)
        # 初始化工具栏折叠状态（在工具栏创建后）
        QTimer.singleShot(200, self.update_markdown_toolbar_collapse)


    def _update_theme_colors(self):
        """更新主题颜色实例变量（内部辅助方法）"""
        # 确保 current_theme 存在且有效
        if not hasattr(self, 'current_theme') or not self.current_theme:
            # 如果主题未初始化，使用默认主题
            self.current_theme = Theme.DARK
        
        self.bg_color = self.current_theme['bg']
        self.bg_secondary_color = self.current_theme['bg_secondary']
        self.bg_tertiary_color = self.current_theme['bg_tertiary']
        self.text_color = self.current_theme['text']
        self.text_secondary_color = self.current_theme['text_secondary']
        self.accent_color = self.current_theme['accent']
        self.accent_hover_color = self.current_theme['accent_hover']
        self.accent_text_color = self.current_theme['accent_text']
        self.border_color = self.current_theme['border']
        self.editor_bg_color = self.current_theme['editor_bg']
        self.editor_text_color = self.current_theme['editor_text']
        self.toolbar_bg_color = self.current_theme['toolbar_bg']
        self.status_bg_color = self.current_theme['status_bg']
        self.status_text_color = self.current_theme['status_text']
        self.success_color = self.current_theme['success']
        self.warning_color = self.current_theme['warning']
        self.error_color = self.current_theme['error']
        self.shadow_color = self.current_theme['shadow']
    
    def apply_theme(self, theme_name, animated=True, force=False):
        """应用主题（带华丽的切换动画）
        
        Args:
            theme_name: 主题名称
            animated: 是否使用动画
            force: 是否强制应用（即使主题相同也应用，用于初始化）
        """
        # 如果正在切换主题，忽略新的切换请求
        if self._is_switching_theme:
            return
        
        # 如果主题没有变化且不是强制应用，直接返回
        if not force and theme_name == self.current_theme_name:
            return
        
        # 保存旧主题信息用于动画
        old_theme = self.current_theme.copy() if hasattr(self, 'current_theme') and self.current_theme else None
        old_bg_color = self.bg_color if hasattr(self, 'bg_color') else '#1a1a1a'
        
        # 更新主题
        self.current_theme = Theme.get_theme(theme_name)
        # 确保 current_theme_name 与 current_theme 一致（如果主题名称无效，get_theme 会返回默认主题）
        self.current_theme_name = self.current_theme.get('name', theme_name)
        
        # 更新颜色实例变量
        self._update_theme_colors()
        
        # 更新主题模式实例变量
        self.is_dark_theme = self.current_theme.get('is_dark', False)
        
        # 获取新主题信息
        new_bg_color = self.bg_color
        theme_display_name = self.current_theme.get('display_name', theme_name)
        
        if animated and old_theme and hasattr(self, 'init_ui'):
            # 执行华丽的切换动画（仅在UI初始化后）
            self._apply_theme_with_animation(old_bg_color, new_bg_color, theme_display_name)
        else:
            # 直接应用主题（无动画）
            self._apply_theme_directly(theme_display_name)
    
    def _apply_theme_directly(self, theme_display_name):
        """直接应用主题（无动画）"""
        base_stylesheet = Theme.get_app_stylesheet(self.current_theme)
        window_style = f"""
            QMainWindow {{
                background-color: {self.bg_color};
                border: none;
                border-radius: 12px;
            }}
            QWidget#centralWidget {{
                background-color: {self.bg_color};
                border-radius: 12px;
            }}
            QWidget#menuBarWidget {{
                background-color: {self.bg_secondary_color};
                border: none;
            }}
            QWidget#toolbarWidget {{
                background-color: {self.toolbar_bg_color};
                border: none;
            }}
            QWidget#toolbarWidget QPushButton {{
                font-weight: normal;
                background-color: {self.bg_secondary_color};
                color: {self.text_color};
                border: none;
                padding: 8px 20px;
                border-radius: 0;
            }}
            QWidget#toolbarWidget QPushButton:hover {{
                background-color: {self.bg_tertiary_color};
            }}
            QWidget#toolbarWidget QPushButton:pressed {{
                background-color: {self.bg_tertiary_color};
            }}
        """
        # 先应用样式表
        self.setStyleSheet(base_stylesheet + window_style)
        # 处理事件，确保样式表立即生效
        QApplication.processEvents()
        # 更新所有组件
        self._update_all_theme_components(theme_display_name)
        # 强制刷新所有子组件的样式
        self._refresh_all_widgets_style()
        # 再次处理事件，确保所有更新生效
        QApplication.processEvents()
    
    def _apply_theme_with_animation(self, old_bg_color, new_bg_color, theme_display_name):
        """应用主题（带华丽的切换动画）"""
        self._is_switching_theme = True
        
        # 创建覆盖层用于动画效果
        if not self._theme_switch_overlay:
            self._theme_switch_overlay = QWidget(self)
            self._theme_switch_overlay.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
            self._theme_switch_overlay.setStyleSheet("background-color: transparent;")
            self._theme_switch_overlay.hide()
        
        # 设置覆盖层大小和位置
        self._theme_switch_overlay.setGeometry(self.rect())
        self._theme_switch_overlay.raise_()
        self._theme_switch_overlay.show()
        
        # 创建淡出动画（旧主题淡出）
        fade_out_animation = QPropertyAnimation(self, b'windowOpacity', self)
        fade_out_animation.setDuration(THEME_SWITCH_FADE_DURATION // 2)
        fade_out_animation.setStartValue(1.0)
        fade_out_animation.setEndValue(0.3)
        fade_out_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        
        # 创建淡入动画（新主题淡入）
        fade_in_animation = QPropertyAnimation(self, b'windowOpacity', self)
        fade_in_animation.setDuration(THEME_SWITCH_FADE_DURATION // 2)
        fade_in_animation.setStartValue(0.3)
        fade_in_animation.setEndValue(1.0)
        fade_in_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        
        # 创建动画组（顺序执行）
        animation_group = QSequentialAnimationGroup(self)
        
        # 第一阶段：淡出旧主题
        animation_group.addAnimation(fade_out_animation)
        
        # 第二阶段：应用新主题样式（在淡出完成后）
        def apply_new_theme():
            base_stylesheet = Theme.get_app_stylesheet(self.current_theme)
            window_style = f"""
                QMainWindow {{
                    background-color: {self.bg_color};
                    border: none;
                    border-radius: 12px;
                }}
                QWidget#centralWidget {{
                    background-color: {self.bg_color};
                    border-radius: 12px;
                }}
                QWidget#menuBarWidget {{
                    background-color: {self.bg_secondary_color};
                    border: none;
                }}
                QWidget#toolbarWidget {{
                    background-color: {self.toolbar_bg_color};
                    border: none;
                }}
                QWidget#toolbarWidget QPushButton {{
                    font-weight: normal;
                }}
            """
            self.setStyleSheet(base_stylesheet + window_style)
            QApplication.processEvents()
            self._update_all_theme_components(theme_display_name)
            # 强制刷新所有组件的样式
            self._refresh_all_widgets_style()
        
        # 第三阶段：淡入新主题
        animation_group.addAnimation(fade_in_animation)
        
        # 动画完成回调
        def on_animation_finished():
            self._is_switching_theme = False
            if self._theme_switch_overlay:
                self._theme_switch_overlay.hide()
            # 确保窗口完全不透明
            self.setWindowOpacity(1.0)
            self.show_status_message_temporarily(f"✨ 主题已切换为: {theme_display_name}", 2000)
        
        animation_group.finished.connect(on_animation_finished)
        
        # 连接淡出动画完成信号，在中间应用新主题
        fade_out_animation.finished.connect(apply_new_theme)
        
        # 启动动画
        self._theme_switch_animation_group = animation_group
        animation_group.start()
    
    def _update_all_theme_components(self, theme_display_name):
        """更新所有主题相关组件"""
        # 更新标题栏主题
        if hasattr(self, 'title_bar'):
            self.title_bar.update_theme(self.current_theme)
        
        # 更新左侧Markdown工具栏主题
        if self.markdown_toolbar_widget:
            self.update_markdown_toolbar_theme()
        
        # 更新时间进度条主题
        if hasattr(self, 'time_progress_bar'):
            self.time_progress_bar.set_theme(self.current_theme)
        
        # 更新状态栏字数统计标签主题
        if hasattr(self, 'word_count_label'):
            self.word_count_label.setStyleSheet(f"color: {self.text_secondary_color}; font-size: 12px; background-color: transparent;")
        
        # 更新切换按钮样式
        if hasattr(self, 'toggle_button'):
            self.update_toggle_button_style()
        
        # 强制更新所有按钮样式，确保没有原生样式泄露
        # 遍历所有子组件，确保样式表正确应用
        self._ensure_all_buttons_styled()
        
        # 更新所有标签页的查找面板主题和预览窗口边框
        for tab_id, tab_info in self.tabs.items():
            if 'find_panel' in tab_info:
                tab_info['find_panel'].update_theme()
            # 更新预览窗口边框样式（移除边框以避免多余线条）
            if 'preview' in tab_info:
                tab_info['preview'].setStyleSheet("")
            # 更新主分割器样式，在预览窗和查找面板之间显示灰色分界线
            if 'splitter' in tab_info:
                tab_info['splitter'].setStyleSheet(f"""
                    QSplitter#mainSplitter::handle {{
                        background-color: {self.border_color};
                        width: 2px;
                    }}
                    QSplitter#mainSplitter::handle:hover {{
                        background-color: {self.accent_color};
                    }}
                """)
            # 更新编辑器字体大小（确保与设置一致）
            if 'editor' in tab_info:
                editor = tab_info['editor']
                if editor and hasattr(self, 'editor_font_size'):
                    editor_font = QFont("Consolas", self.editor_font_size)
                    editor.setFont(editor_font)
                    editor.document().setDefaultFont(editor_font)
        
        # 更新所有标签页的预览窗口内容，以应用新的主题颜色
        for tab_id, tab_info in self.tabs.items():
            if 'preview' in tab_info:
                self.update_preview(tab_id)
    
    def _ensure_all_buttons_styled(self):
        """确保所有按钮都应用了正确的样式，避免原生样式泄露"""
        # 需要排除的按钮对象名称（这些按钮有自己的特殊样式）
        excluded_names = ['titleBarButton', 'closeButton', 'pinButton', 'minimizeButton', 'maximizeButton']
        
        # 递归查找所有 QPushButton
        def find_buttons(widget):
            buttons = []
            if isinstance(widget, QPushButton):
                buttons.append(widget)
            for child in widget.findChildren(QWidget):
                if isinstance(child, QPushButton):
                    buttons.append(child)
            return buttons
        
        # 查找所有按钮
        all_buttons = find_buttons(self)
        
        # 对于工具栏按钮，确保它们使用正确的样式
        for button in all_buttons:
            # 跳过标题栏按钮（它们有自己的样式）
            if button.objectName() in excluded_names:
                continue
            
            # 检查按钮的父组件
            parent = button.parent()
            if parent:
                parent_name = getattr(parent, 'objectName', '')
                # 工具栏按钮应该继承 toolbarWidget 的样式
                if parent_name == 'toolbarWidget':
                    # 确保工具栏按钮没有独立的样式，让它继承父级样式
                    # 清除任何独立的样式表，确保继承全局样式
                    current_style = button.styleSheet()
                    if current_style and current_style.strip():
                        # 清除独立样式，让按钮继承父级样式
                        button.setStyleSheet("")
    
    def _refresh_all_widgets_style(self):
        """强制刷新所有组件的样式，确保样式表正确应用"""
        # 重新应用样式表到主窗口，这会强制所有子组件重新应用样式
        current_stylesheet = self.styleSheet()
        if current_stylesheet:
            # 临时清除样式表
            self.setStyleSheet("")
            QApplication.processEvents()
            # 重新应用样式表
            self.setStyleSheet(current_stylesheet)
            QApplication.processEvents()
    
    def _ensure_editor_font_sizes(self):
        """确保所有编辑器的字体大小与设置一致"""
        if not hasattr(self, 'editor_font_size'):
            return
        for tab_id, tab_info in self.tabs.items():
            if 'editor' in tab_info:
                editor = tab_info['editor']
                if editor:
                    editor_font = QFont("Consolas", self.editor_font_size)
                    editor.setFont(editor_font)
                    editor.document().setDefaultFont(editor_font)
    

    def resizeEvent(self, event):
        """窗口大小改变事件"""
        super().resizeEvent(event)
        # 更新覆盖层大小
        if self._theme_switch_overlay:
            self._theme_switch_overlay.setGeometry(self.rect())
        # 更新布局以适应窗口宽度
        self.update_layout_for_width()
        # 更新左侧工具栏折叠状态以适应窗口高度
        if hasattr(self, 'markdown_toolbar_widget') and self.markdown_toolbar_widget:
            self.update_markdown_toolbar_collapse()
            # 确保滚动提示在窗口大小变化后也能正确更新
            if (hasattr(self, 'markdown_toolbar_scroll_area') and 
                hasattr(self, 'markdown_toolbar_scroll_hint_top') and 
                hasattr(self, 'markdown_toolbar_scroll_hint_bottom')):
                QTimer.singleShot(50, lambda: self._update_scroll_hint(
                    self.markdown_toolbar_scroll_area,
                    self.markdown_toolbar_scroll_hint_top,
                    self.markdown_toolbar_scroll_hint_bottom
                ))
    
    def update_layout_for_width(self):
        """根据窗口宽度更新布局"""
        window_width = self.width()
        tab_id = self.get_current_tab_id()
        
        if tab_id is None or tab_id not in self.tabs:
            return
        
        tab_info = self.tabs[tab_id]
        content_splitter = tab_info.get('content_splitter')
        editor = tab_info.get('editor')
        preview = tab_info.get('preview')
        
        if not content_splitter or not editor or not preview:
            return
        
        if window_width < SMALL_WINDOW_THRESHOLD:
            # 小窗口模式：只显示一个视图，显示切换按钮
            # 显示左侧Markdown工具栏（根据窗口高度自动折叠）
            if self.markdown_toolbar_widget:
                self.markdown_toolbar_widget.show()
                self.update_markdown_toolbar_collapse()
            
            if self.view_mode == 'editor':
                # 显示编辑窗，隐藏预览窗
                editor.show()
                preview.hide()
                # 设置分割器大小，使编辑器占满可用空间，预览窗隐藏
                content_splitter.setSizes([1000, 0])
                # 更新按钮图标
                if self.toggle_button:
                    self.toggle_button.setText("👁️")
            else:
                # 显示预览窗，隐藏编辑窗
                editor.hide()
                preview.show()
                # 设置分割器大小，使预览窗占满可用空间，编辑器隐藏
                content_splitter.setSizes([0, 1000])
                # 更新按钮图标
                if self.toggle_button:
                    self.toggle_button.setText("📝")
            
            # 显示切换按钮并更新位置
            if self.toggle_button:
                self.toggle_button.show()
                # 立即更新按钮位置
                self.update_toggle_button_position()
                # 使用定时器再更新一次位置，确保布局已完成
                QTimer.singleShot(50, self.update_toggle_button_position)
                QTimer.singleShot(100, self.update_toggle_button_position)  # 再次更新，确保位置正确
        else:
            # 大窗口模式：同时显示编辑窗和预览窗，隐藏切换按钮
            # 显示左侧Markdown工具栏（根据窗口高度自动折叠）
            if self.markdown_toolbar_widget:
                self.markdown_toolbar_widget.show()
                self.update_markdown_toolbar_collapse()
            
            editor.show()
            preview.show()
            # 恢复默认分割器大小
            content_splitter.setSizes([600, 600])
            
            if self.toggle_button:
                self.toggle_button.hide()
    
    def update_toggle_button_position(self):
        """更新切换按钮位置到右上角"""
        if not self.toggle_button:
            return
        
        # 检查窗口宽度，如果是双窗口模式，不更新位置（按钮应该隐藏）
        window_width = self.width()
        if window_width >= SMALL_WINDOW_THRESHOLD:
            # 双窗口模式，确保按钮隐藏
            if self.toggle_button.isVisible():
                self.toggle_button.hide()
            return
        
        # 确保标签页组件已创建
        if not self.tab_widget:
            return
        
        # 获取标签页区域的位置和大小
        tab_widget_rect = self.tab_widget.geometry()
        
        # 如果标签页区域无效，等待布局完成
        if tab_widget_rect.width() <= 0 or tab_widget_rect.height() <= 0:
            return
        
        # 计算按钮位置（相对于标签页的右上角，留出一些边距）
        button_x = tab_widget_rect.right() - self.toggle_button.width() - 15
        button_y = tab_widget_rect.top() + 15  # 从顶部开始，而不是底部
        
        # 将按钮位置转换为相对于主窗口的坐标
        local_pos = self.tab_widget.mapTo(self, QPoint(button_x, button_y))
        
        # 确保坐标值有效，并且按钮不会超出窗口边界
        window_height = self.height()
        final_x = max(0, min(local_pos.x(), window_width - self.toggle_button.width()))
        final_y = max(0, min(local_pos.y(), window_height - self.toggle_button.height()))
        
        self.toggle_button.move(final_x, final_y)
        self.toggle_button.raise_()  # 确保按钮在最上层
        
        # 确保按钮可见（仅在小窗口模式下）
        if not self.toggle_button.isVisible():
            self.toggle_button.show()
    
    def update_toggle_button_style(self):
        """更新切换按钮样式"""
        if not self.toggle_button:
            return
        
        self.toggle_button.setStyleSheet(f"""
            QPushButton#toggleButton {{
                background-color: transparent;
                color: {self.text_color};
                border: none;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
                padding: 5px;
                min-width: 30px;
                min-height: 30px;
                qproperty-iconSize: 16px;
            }}
            QPushButton#toggleButton:hover {{
                background-color: {self.bg_tertiary_color};
            }}
            QPushButton#toggleButton:pressed {{
                background-color: {self.bg_secondary_color};
            }}
        """)
    
    def toggle_view_mode(self):
        """切换编辑窗和预览窗"""
        if self.view_mode == 'editor':
            self.view_mode = 'preview'
            if self.toggle_button:
                self.toggle_button.setText("📝")  # 显示编辑图标
        else:
            self.view_mode = 'editor'
            if self.toggle_button:
                self.toggle_button.setText("👁️")  # 显示预览图标
        
        # 更新布局
        self.update_layout_for_width()
        
        # 确保当前标签页的预览也更新
        tab_id = self.get_current_tab_id()
        if tab_id is not None and tab_id in self.tabs:
            self.update_preview(tab_id)
    
    def moveEvent(self, event):
        """窗口移动事件 - 更新悬浮工具栏位置"""
        super().moveEvent(event)

    def get_resize_edge(self, pos):
        """检测鼠标位置是否在窗口边缘，返回边缘类型"""
        x, y = pos.x(), pos.y()
        width, height = self.width(), self.height()
        border = self.resize_border_width
        
        # 检测四个角
        if x <= border and y <= border:
            return 'top-left'
        elif x >= width - border and y <= border:
            return 'top-right'
        elif x <= border and y >= height - border:
            return 'bottom-left'
        elif x >= width - border and y >= height - border:
            return 'bottom-right'
        # 检测四条边
        elif x <= border:
            return 'left'
        elif x >= width - border:
            return 'right'
        elif y <= border:
            return 'top'
        elif y >= height - border:
            return 'bottom'
        return None
    
    def update_cursor(self, pos):
        """根据鼠标位置更新光标形状"""
        edge = self.get_resize_edge(pos)
        if edge is None:
            # 检查是否在标题栏区域（可拖动区域）
            if hasattr(self, 'title_bar'):
                title_bar_y = self.title_bar.y()
                title_bar_height = self.title_bar.height()
                if title_bar_y <= pos.y() <= title_bar_y + title_bar_height:
                    # 在标题栏区域，检查是否在按钮区域
                    if hasattr(self.title_bar, 'minimize_btn'):
                        if pos.x() < self.title_bar.minimize_btn.x():
                            self.setCursor(Qt.CursorShape.ArrowCursor)
                        else:
                            self.setCursor(Qt.CursorShape.ArrowCursor)
                    else:
                        self.setCursor(Qt.CursorShape.ArrowCursor)
                else:
                    self.setCursor(Qt.CursorShape.ArrowCursor)
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)
        else:
            # 根据边缘类型设置光标
            cursor_map = {
                'left': Qt.CursorShape.SizeHorCursor,
                'right': Qt.CursorShape.SizeHorCursor,
                'top': Qt.CursorShape.SizeVerCursor,
                'bottom': Qt.CursorShape.SizeVerCursor,
                'top-left': Qt.CursorShape.SizeFDiagCursor,
                'top-right': Qt.CursorShape.SizeBDiagCursor,
                'bottom-left': Qt.CursorShape.SizeBDiagCursor,
                'bottom-right': Qt.CursorShape.SizeFDiagCursor,
            }
            self.setCursor(cursor_map.get(edge, Qt.CursorShape.ArrowCursor))
    
    def mousePressEvent(self, event):
        """鼠标按下事件 - 开始拖动窗口或调整大小"""
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position().toPoint()
            
            # 优先检测是否在边缘（调整大小）
            edge = self.get_resize_edge(pos)
            if edge and not self.isMaximized():
                self.resize_flag = True
                self.resize_edge = edge
                self.window_origin_x = self.x()
                self.window_origin_y = self.y()
                self.window_origin_width = self.width()
                self.window_origin_height = self.height()
                self.mouse_origin_x = event.globalPosition().toPoint().x()
                self.mouse_origin_y = event.globalPosition().toPoint().y()
                event.accept()
                return
            
            # 检查是否在标题栏区域（按钮区域左侧）- 拖动窗口
            if hasattr(self, 'title_bar'):
                title_bar_y = self.title_bar.y()
                title_bar_height = self.title_bar.height()
                # 检查是否在标题栏区域内，且不在按钮区域
                if title_bar_y <= pos.y() <= title_bar_y + title_bar_height:
                    if hasattr(self.title_bar, 'minimize_btn'):
                        if pos.x() < self.title_bar.minimize_btn.x():
                            self.move_flag = True
                            self.window_origin_x = self.x()
                            self.window_origin_y = self.y()
                            self.mouse_origin_x = event.globalPosition().toPoint().x()
                            self.mouse_origin_y = event.globalPosition().toPoint().y()
                            event.accept()
                            return
                    else:
                        # 如果没有按钮，整个标题栏都可以拖动
                        self.move_flag = True
                        self.window_origin_x = self.x()
                        self.window_origin_y = self.y()
                        self.mouse_origin_x = event.globalPosition().toPoint().x()
                        self.mouse_origin_y = event.globalPosition().toPoint().y()
                        event.accept()
                        return
            
            # 其他情况传递给父类处理
            super().mousePressEvent(event)
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """鼠标移动事件 - 拖动窗口或调整大小"""
        pos = event.position().toPoint()
        
        # 如果不在拖动或调整大小状态，更新光标形状
        if not self.move_flag and not self.resize_flag:
            self.update_cursor(pos)
        
        # 调整窗口大小
        if self.resize_flag and not self.isMaximized():
            mouse_des_x = event.globalPosition().toPoint().x()
            mouse_des_y = event.globalPosition().toPoint().y()
            delta_x = mouse_des_x - self.mouse_origin_x
            delta_y = mouse_des_y - self.mouse_origin_y
            
            new_x = self.window_origin_x
            new_y = self.window_origin_y
            new_width = self.window_origin_width
            new_height = self.window_origin_height
            
            # 根据边缘类型调整窗口大小和位置
            if 'left' in self.resize_edge:
                new_x = self.window_origin_x + delta_x
                new_width = self.window_origin_width - delta_x
                if new_width < self.minimumWidth():
                    new_width = self.minimumWidth()
                    new_x = self.window_origin_x + self.window_origin_width - self.minimumWidth()
            
            if 'right' in self.resize_edge:
                new_width = self.window_origin_width + delta_x
                if new_width < self.minimumWidth():
                    new_width = self.minimumWidth()
            
            if 'top' in self.resize_edge:
                new_y = self.window_origin_y + delta_y
                new_height = self.window_origin_height - delta_y
                if new_height < self.minimumHeight():
                    new_height = self.minimumHeight()
                    new_y = self.window_origin_y + self.window_origin_height - self.minimumHeight()
            
            if 'bottom' in self.resize_edge:
                new_height = self.window_origin_height + delta_y
                if new_height < self.minimumHeight():
                    new_height = self.minimumHeight()
            
            # 应用新的窗口大小和位置
            self.setGeometry(new_x, new_y, new_width, new_height)
            event.accept()
            return
        
        # 拖动窗口
        if self.move_flag:
            # 如果全屏，先退出全屏
            if self.isFullScreen():
                self.showNormal()
                # 更新窗口位置信息
                self.window_origin_x = self.x()
                self.window_origin_y = self.y()
                # 重新计算鼠标位置
                global_pos = event.globalPosition().toPoint()
                self.mouse_origin_x = global_pos.x()
                self.mouse_origin_y = global_pos.y()
            
            if not self.isMaximized():
                mouse_des_x = event.globalPosition().toPoint().x()
                mouse_des_y = event.globalPosition().toPoint().y()
                window_des_x = self.window_origin_x + mouse_des_x - self.mouse_origin_x
                window_des_y = self.window_origin_y + mouse_des_y - self.mouse_origin_y

                self.move(window_des_x, window_des_y)
            event.accept()
            return
        
        # 其他情况传递给父类处理
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """鼠标释放事件 - 结束拖动或调整大小"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.move_flag = False
            self.resize_flag = False
            self.resize_edge = None
            # 恢复默认光标
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def setup_shortcuts(self):
        """设置常用快捷键 - 修复焦点问题"""
        # 使用 WindowShortcut 而不是 ApplicationShortcut，避免与编辑框冲突
        shortcut_context = Qt.ShortcutContext.WindowShortcut
        
        # ===== 文件操作快捷键 =====
        # 注意：Ctrl+N、Ctrl+O、Ctrl+S、Ctrl+Shift+S 已在菜单栏中注册，此处不再重复注册
        
        # ===== 编辑操作快捷键 =====
        # 注意：Ctrl+Z、Ctrl+Y 已在菜单栏中注册，此处不再重复注册
        
        redo_alt_shortcut = QShortcut(QKeySequence("Ctrl+Shift+Z"), self)
        redo_alt_shortcut.setContext(shortcut_context)
        redo_alt_shortcut.activated.connect(self.redo)
        
        # 注意：Ctrl+A 已在菜单栏中注册，此处不再重复注册
        # 注意：Ctrl+Shift+C、Ctrl+F 已在菜单栏中注册，此处不再重复注册
        
        # ===== Markdown格式快捷键 =====
        # Ctrl+B - 加粗
        bold_shortcut = QShortcut(QKeySequence("Ctrl+B"), self)
        bold_shortcut.setContext(shortcut_context)
        bold_shortcut.activated.connect(lambda: self.insert_markdown_wrapper("**", "**"))
        
        # Ctrl+I - 斜体
        italic_shortcut = QShortcut(QKeySequence("Ctrl+I"), self)
        italic_shortcut.setContext(shortcut_context)
        italic_shortcut.activated.connect(lambda: self.insert_markdown_wrapper("*", "*"))
        
        # Ctrl+D - 删除线
        strikethrough_shortcut = QShortcut(QKeySequence("Ctrl+D"), self)
        strikethrough_shortcut.setContext(shortcut_context)
        strikethrough_shortcut.activated.connect(lambda: self.insert_markdown_wrapper("~~", "~~"))
        
        # Ctrl+H - 高亮
        highlight_shortcut = QShortcut(QKeySequence("Ctrl+H"), self)
        highlight_shortcut.setContext(shortcut_context)
        highlight_shortcut.activated.connect(lambda: self.insert_markdown_wrapper("==", "=="))
        
        # Ctrl+` - 行内代码
        code_shortcut = QShortcut(QKeySequence("Ctrl+`"), self)
        code_shortcut.setContext(shortcut_context)
        code_shortcut.activated.connect(lambda: self.insert_markdown_wrapper("`", "`"))
        
        # ===== 插入内容快捷键 =====
        # Ctrl+K - 插入链接
        link_shortcut = QShortcut(QKeySequence("Ctrl+K"), self)
        link_shortcut.setContext(shortcut_context)
        link_shortcut.activated.connect(self.insert_link)
        
        # Ctrl+Shift+K - 代码块
        codeblock_shortcut = QShortcut(QKeySequence("Ctrl+Shift+K"), self)
        codeblock_shortcut.setContext(shortcut_context)
        codeblock_shortcut.activated.connect(self.insert_code_block)
        
        # Ctrl+Q - 插入引用
        quote_shortcut = QShortcut(QKeySequence("Ctrl+Q"), self)
        quote_shortcut.setContext(shortcut_context)
        quote_shortcut.activated.connect(lambda: self.insert_markdown_list("> "))
        
        # Ctrl+L - 无序列表
        list_shortcut = QShortcut(QKeySequence("Ctrl+L"), self)
        list_shortcut.setContext(shortcut_context)
        list_shortcut.activated.connect(lambda: self.insert_markdown("- "))
        
        # Ctrl+Shift+L - 有序列表
        ordered_list_shortcut = QShortcut(QKeySequence("Ctrl+Shift+L"), self)
        ordered_list_shortcut.setContext(shortcut_context)
        ordered_list_shortcut.activated.connect(lambda: self.insert_markdown("1. "))
        
        # ===== 标题快捷键 =====
        # Ctrl+1~6 - 标题1~6
        for i in range(1, 7):
            shortcut = QShortcut(QKeySequence(f"Ctrl+{i}"), self)
            shortcut.setContext(shortcut_context)
            shortcut.activated.connect(lambda level=i: self.insert_markdown("#" * level + " "))
        
        # ===== 其他实用快捷键 =====
        # Ctrl+T - 插入当前时间
        time_shortcut = QShortcut(QKeySequence("Ctrl+T"), self)
        time_shortcut.setContext(shortcut_context)
        time_shortcut.activated.connect(self.insert_timestamp)
        
        # Ctrl+R - 插入水平分割线
        hr_shortcut = QShortcut(QKeySequence("Ctrl+R"), self)
        hr_shortcut.setContext(shortcut_context)
        hr_shortcut.activated.connect(lambda: self.insert_markdown("\n---\n\n"))
        
        # ===== 调试快捷键 =====
        # 注意：F1 已在菜单栏中注册，此处不再重复注册
        
        # 存储所有快捷键以便管理
        self.shortcuts = {
            'redo_alt': redo_alt_shortcut,
            'bold': bold_shortcut,
            'italic': italic_shortcut,
            'strikethrough': strikethrough_shortcut,
            'highlight': highlight_shortcut,
            'code': code_shortcut,
            'link': link_shortcut,
            'codeblock': codeblock_shortcut,
            'quote': quote_shortcut,
            'list': list_shortcut,
            'ordered_list': ordered_list_shortcut,
            'time': time_shortcut,
            'hr': hr_shortcut,
        }
        
        # 设置快捷键自动重复为False，避免长按时的重复触发
        for shortcut in self.shortcuts.values():
            shortcut.setAutoRepeat(False)
            
    def setup_toolbar_shortcut(self):
        """设置悬浮工具栏快捷键"""
        # 如果已经存在工具栏快捷键，先删除它
        if hasattr(self, 'toolbar_shortcut') and self.toolbar_shortcut:
            self.toolbar_shortcut.deleteLater()
            
        # 根据设置添加新快捷键（默认为Ctrl+;）
        hotkey = self.toolbar_hotkey or "Ctrl+;"
        
        # 处理单独的 "Ctrl" 情况，改为 "Ctrl+;"
        if hotkey == "Ctrl":
            hotkey = "Ctrl+;"
        
        # 只有当快捷键不是已被占用的组合时才创建
        occupied_shortcuts = ["Ctrl+M", "Ctrl+;"]  # 这些已经在setup_shortcuts中设置
        if hotkey not in occupied_shortcuts:
            self.toolbar_shortcut = QShortcut(QKeySequence(hotkey), self)
            # 提高优先级，确保快捷键优先响应
            self.toolbar_shortcut.setAutoRepeat(False)
            # 使用 WindowShortcut 使快捷键在整个窗口上有效
            self.toolbar_shortcut.setContext(Qt.ShortcutContext.WindowShortcut)
        else:
            self.toolbar_shortcut = None  # 标记为未使用，避免重复
        
    def reload_toolbar_shortcut(self, hotkey):
        """重新加载悬浮工具栏快捷键"""
        self.toolbar_hotkey = hotkey
        self.setup_toolbar_shortcut()
        
    def create_menu_bar(self):
        """创建菜单栏"""
        # 隐藏默认的菜单栏
        self.menuBar().hide()
        
        # 创建自定义菜单栏widget
        menubar_widget = QWidget()
        menubar_widget.setObjectName("menuBarWidget")
        menubar_layout = QHBoxLayout(menubar_widget)
        menubar_layout.setContentsMargins(0, 0, 0, 0)
        menubar_layout.setSpacing(0)
        
        # 创建菜单栏（但不显示，只用于创建菜单）
        menubar = QMenuBar(menubar_widget)
        menubar.setNativeMenuBar(False)  # 不使用系统菜单栏
        
        # 文件菜单（移除 Alt 快捷键）
        file_menu = menubar.addMenu("文件")
        
        new_action = QAction("新建", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(lambda: self.create_new_tab())
        file_menu.addAction(new_action)
        
        open_action = QAction("打开", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(lambda: self.open_file())
        file_menu.addAction(open_action)
        
        save_action = QAction("保存", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(lambda: self.save_file())
        file_menu.addAction(save_action)
        
        save_as_action = QAction("另存为", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        settings_action = QAction("设置", self)
        settings_action.triggered.connect(self.open_settings)
        file_menu.addAction(settings_action)
        
        file_menu.addSeparator()
        
        quit_action = QAction("退出", self)
        # 移除 Ctrl+Q 快捷键，改为插入引用
        # quit_action.setShortcut(QKeySequence.StandardKey.Quit)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)
        
        # 编辑菜单
        edit_menu = menubar.addMenu("编辑")
        
        undo_action = QAction("撤销", self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.triggered.connect(self.undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("重做", self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.triggered.connect(self.redo)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        select_all_action = QAction("全选", self)
        select_all_action.setShortcut(QKeySequence.StandardKey.SelectAll)
        select_all_action.triggered.connect(self.select_all)
        edit_menu.addAction(select_all_action)
        
        copy_all_action = QAction("复制全文", self)
        copy_all_action.setShortcut("Ctrl+Shift+C")
        copy_all_action.triggered.connect(self.copy_all_content)
        edit_menu.addAction(copy_all_action)
        
        edit_menu.addSeparator()
        
        find_action = QAction("查找", self)
        find_action.setShortcut(QKeySequence.StandardKey.Find)
        find_action.triggered.connect(self.show_find_dialog)
        edit_menu.addAction(find_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助")
        
        guide_action = QAction("使用指南", self)
        guide_action.triggered.connect(self.show_welcome)
        help_menu.addAction(guide_action)
        
        shortcuts_action = QAction("快捷键", self)
        shortcuts_action.setShortcut("F1")
        shortcuts_action.triggered.connect(self.show_shortcuts)
        help_menu.addAction(shortcuts_action)
        
        help_menu.addSeparator()
        
        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        # 将菜单栏添加到布局
        menubar_layout.addWidget(menubar)
        menubar_layout.addStretch()
        
        # 将菜单栏widget添加到主布局
        central_widget = self.centralWidget()
        main_layout = central_widget.layout()
        main_layout.insertWidget(1, menubar_widget)  # 插入到标题栏之后
        
        # 保存菜单栏引用以便后续使用
        self.menubar_widget = menubar_widget
        self.menubar = menubar
        
    def create_toolbar(self):
        """创建工具栏"""
        # 创建工具栏widget（作为普通widget添加到布局中）
        toolbar_widget = QWidget()
        toolbar_widget.setObjectName("toolbarWidget")
        toolbar_layout = QHBoxLayout(toolbar_widget)
        toolbar_layout.setContentsMargins(6, 6, 6, 6)
        toolbar_layout.setSpacing(6)
        
        # 新建按钮
        new_btn = QPushButton("📄 新建")
        new_btn.clicked.connect(lambda: self.create_new_tab())
        toolbar_layout.addWidget(new_btn)
        
        # 打开按钮
        open_btn = QPushButton("📂 打开")
        open_btn.clicked.connect(lambda: self.open_file())
        toolbar_layout.addWidget(open_btn)
        
        # 保存按钮
        save_btn = QPushButton("💾 保存")
        save_btn.clicked.connect(lambda: self.save_file())
        toolbar_layout.addWidget(save_btn)
        
        # 分隔符（使用弹性空间模拟）
        toolbar_layout.addSpacing(10)
                
        # 分隔符
        toolbar_layout.addSpacing(10)
        
        # 复制全文按钮
        copy_all_btn = QPushButton("📋 复制全文")
        copy_all_btn.clicked.connect(lambda: self.copy_all_content())
        toolbar_layout.addWidget(copy_all_btn)
        
        # 清空按钮
        clear_btn = QPushButton("🗑️ 清空")
        clear_btn.clicked.connect(lambda: self.clear_current_tab())
        toolbar_layout.addWidget(clear_btn)
        
        # 右侧弹性空间
        toolbar_layout.addStretch()
        
        # 将工具栏widget添加到主布局（在菜单栏之后、标签页之前）
        central_widget = self.centralWidget()
        main_layout = central_widget.layout()
        # 找到标签页的索引，在它之前插入工具栏
        tab_index = main_layout.indexOf(self.tab_widget)
        main_layout.insertWidget(tab_index, toolbar_widget)
        
        # 保存工具栏引用以便后续使用
        self.toolbar_widget = toolbar_widget
    
    def create_markdown_toolbar(self):
        """创建左侧Markdown工具栏 - 无滚动条，使用滚动提示"""
        # 创建主容器（包含滚动区域和滚动提示）
        toolbar_container = QWidget()
        toolbar_container.setObjectName("markdownToolbarContainer")
        container_layout = QVBoxLayout(toolbar_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        # 创建滚动区域（不显示滚动条）
        scroll_area = QScrollArea()
        scroll_area.setObjectName("markdownToolbarScrollArea")
        scroll_area.setWidgetResizable(False)  # 不自动调整内容大小
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)  # 禁用水平滚动
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)  # 禁用垂直滚动条
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)  # 无边框
        # 固定滚动区域宽度为59px（为按钮左移7px留出空间）
        scroll_area.setFixedWidth(59)
        scroll_area.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        
        # 创建内部工具栏容器（实际内容）
        toolbar_content = QWidget()
        toolbar_content.setObjectName("markdownToolbar")
        toolbar_content.setFixedWidth(59)  # 内容宽度：59px
        
        # 创建主布局
        # 调整边距：左12px（5+7），右0px（5-7，但不能为负），上下8px
        # 内容宽度59px = 按钮42px + 左边距12px + 右边距0px + 余量5px
        toolbar_layout = QVBoxLayout(toolbar_content)
        toolbar_layout.setContentsMargins(12, 8, 0, 8)
        toolbar_layout.setSpacing(6)
        
        # 应用主题样式
        self._apply_toolbar_theme(toolbar_content, scroll_area)
        
        # 定义工具栏按钮组配置
        button_groups = self._get_toolbar_button_groups()
        
        # 初始化工具栏数据
        self.markdown_toolbar_groups = []
        self.markdown_toolbar_buttons = []
        
        # 创建所有按钮组
        for idx, group_info in enumerate(button_groups):
            group_widget = self._create_toolbar_group(group_info)
            toolbar_layout.addWidget(group_widget)
            
            # 在组之间添加分隔线（除了最后一组）
            if idx < len(button_groups) - 1:
                separator = self._create_toolbar_separator()
                toolbar_layout.addWidget(separator)
        
        # 添加底部弹性空间
        toolbar_layout.addStretch()
        
        # 将内容widget添加到滚动区域
        scroll_area.setWidget(toolbar_content)
        
        # 创建向上滚动提示标签（▲符号，表示可以向上滚动）
        scroll_hint_top = QLabel("▲")
        scroll_hint_top.setObjectName("scrollHintLabelTop")
        scroll_hint_top.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll_hint_top.setFixedSize(59, 16)  # 宽度与滚动区域一致
        scroll_hint_top.setStyleSheet(f"""
            QLabel#scrollHintLabelTop {{
                color: {self.current_theme.get('text_secondary', self.current_theme.get('text', '#888888'))};
                font-size: 10px;
                background-color: transparent;
                padding: 0px;
            }}
        """)
        scroll_hint_top.hide()  # 默认隐藏
        
        # 创建向下滚动提示标签（▼符号，表示可以向下滚动）
        scroll_hint_bottom = QLabel("▼")
        scroll_hint_bottom.setObjectName("scrollHintLabelBottom")
        scroll_hint_bottom.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll_hint_bottom.setFixedSize(59, 16)  # 宽度与滚动区域一致
        scroll_hint_bottom.setStyleSheet(f"""
            QLabel#scrollHintLabelBottom {{
                color: {self.current_theme.get('text_secondary', self.current_theme.get('text', '#888888'))};
                font-size: 10px;
                background-color: transparent;
                padding: 0px;
            }}
        """)
        scroll_hint_bottom.hide()  # 默认隐藏
        
        # 添加到容器布局：顶部提示 -> 滚动区域 -> 底部提示
        container_layout.addWidget(scroll_hint_top)
        container_layout.addWidget(scroll_area)
        container_layout.addWidget(scroll_hint_bottom)
        
        # 更新内容高度（使用QTimer确保布局完成后再计算）
        QTimer.singleShot(0, lambda: self._update_toolbar_content_height())
        
        # 连接滚动事件，更新提示显示
        scroll_area.verticalScrollBar().valueChanged.connect(
            lambda: self._update_scroll_hint(scroll_area, scroll_hint_top, scroll_hint_bottom)
        )
        scroll_area.verticalScrollBar().rangeChanged.connect(
            lambda: self._update_scroll_hint(scroll_area, scroll_hint_top, scroll_hint_bottom)
        )
        
        # 保存工具栏引用
        self.markdown_toolbar_widget = toolbar_container
        self.markdown_toolbar_scroll_area = scroll_area  # 保存滚动区域引用
        self.markdown_toolbar_content = toolbar_content  # 保存内容引用以便更新主题
        self.markdown_toolbar_scroll_hint_top = scroll_hint_top  # 保存顶部滚动提示引用
        self.markdown_toolbar_scroll_hint_bottom = scroll_hint_bottom  # 保存底部滚动提示引用
    
    def _get_toolbar_button_groups(self):
        """获取工具栏按钮组配置"""
        return [
            {
                'name': '基础格式',
                'icon': '📝',
                'tooltip': '基础格式',
                'buttons': [
                    ("#", "标题1", lambda: self.insert_markdown_header(1)),
                    ("##", "标题2", lambda: self.insert_markdown_header(2)),
                    ("###", "标题3", lambda: self.insert_markdown_header(3)),
                    ("**", "粗体", lambda: self.insert_markdown_wrapper("**", "**")),
                    ("*", "斜体", lambda: self.insert_markdown_wrapper("*", "*")),
                    ("~~", "删除线", lambda: self.insert_markdown_wrapper("~~", "~~")),
                    ("==", "高亮", lambda: self.insert_markdown_wrapper("==", "==")),
                    ("`", "行内代码", lambda: self.insert_markdown_wrapper("`", "`")),
                ]
            },
            {
                'name': '列表',
                'icon': '📋',
                'tooltip': '列表和引用',
                'buttons': [
                    ("•", "无序列表", lambda: self.insert_markdown_list("- ")),
                    ("1.", "有序列表", lambda: self.insert_markdown_list("1. ")),
                    ("☐", "任务列表", lambda: self.insert_markdown_list("- [ ] ")),
                    (">", "引用", lambda: self.insert_markdown_list("> ")),
                ]
            },
            {
                'name': '插入',
                'icon': '➕',
                'tooltip': '插入元素',
                'buttons': [
                    ("🔗", "链接", self.insert_markdown_link),
                    ("🖼️", "图片", self.insert_markdown_image),
                    ("📊", "表格", self.insert_markdown_table),
                    ("💻", "代码块", self.insert_markdown_code_block),
                    ("──", "分割线", self.insert_markdown_separator),
                    ("📑", "目录", self.insert_markdown_toc),
                    ("⏰", "时间戳", self.insert_markdown_timestamp),
                    ("📌", "脚注", self.insert_markdown_footnote),
                ]
            },
            {
                'name': 'LaTeX',
                'icon': '∑',
                'tooltip': 'LaTeX公式',
                'buttons': [
                    ("$", "行内公式", lambda: self.insert_markdown_wrapper("$", "$")),
                    ("$$", "公式块", self.insert_markdown_math_block),
                ]
            },
        ]
    
    def _apply_toolbar_theme(self, content_widget, scroll_area=None):
        """应用工具栏主题样式"""
        theme = self.current_theme
        
        # 内容widget样式
        # 计算不同等级按钮的颜色
        # 折叠按钮（组标题）：使用更突出的背景色和边框
        collapse_bg = theme.get('bg_tertiary', theme['bg_secondary'])
        collapse_hover_bg = theme.get('accent', theme['bg_tertiary'])
        # 普通功能按钮：使用透明背景
        normal_bg = 'transparent'
        normal_hover = theme['bg_tertiary']
        
        # 计算边框颜色，使折叠按钮更明显
        collapse_border = theme.get('accent', theme['border'])
        
        content_style = f"""
            QWidget#markdownToolbar {{
                background-color: {theme['bg_secondary']};
            }}
            /* 普通功能按钮样式 - 一级按钮（功能按钮） */
            QPushButton {{
                background-color: {normal_bg};
                border: 1px solid transparent;
                border-radius: 5px;
                padding: 0px;
                font-size: 16px;
                min-width: 42px;
                min-height: 42px;
                max-width: 42px;
                max-height: 42px;
                color: {theme.get('text', '#d0d0d0')};
            }}
            QPushButton:hover {{
                background-color: {normal_hover};
                border: 1px solid {theme['border']};
            }}
            QPushButton:pressed {{
                background-color: {theme['accent']};
                color: {theme.get('accent_text', '#ffffff')};
                border: 1px solid {theme['accent']};
            }}
            QPushButton:checked {{
                background-color: {normal_hover};
                border: 1px solid {theme['border']};
            }}
            /* 折叠按钮（组标题）样式 - 二级按钮（组标题按钮），更突出 */
            /* 折叠状态（未选中） */
            QPushButton#collapseButton {{
                font-size: 13px;
                font-weight: 700;
                background-color: {collapse_bg};
                color: {theme.get('text_secondary', theme.get('text', '#888888'))};
                border: 2px solid {theme['border']};
                border-radius: 6px;
            }}
            /* 展开状态（选中） */
            QPushButton#collapseButton:checked {{
                background-color: {theme.get('accent', collapse_bg)};
                color: {theme.get('accent_text', '#ffffff')};
                border: 2px solid {theme['accent']};
            }}
            QPushButton#collapseButton:hover {{
                background-color: {collapse_hover_bg};
                border: 2px solid {theme['accent']};
                color: {theme.get('accent_text', '#ffffff')};
            }}
            QPushButton#collapseButton:checked:hover {{
                background-color: {theme.get('accent_hover', theme.get('accent', collapse_hover_bg))};
                border: 2px solid {theme['accent']};
                color: {theme.get('accent_text', '#ffffff')};
            }}
            QPushButton#collapseButton:pressed {{
                background-color: {theme['accent']};
                color: {theme.get('accent_text', '#ffffff')};
                border: 2px solid {theme['accent']};
            }}
        """
        content_widget.setStyleSheet(content_style)
        
        # 滚动区域样式
        if scroll_area:
            scroll_style = f"""
                QScrollArea#markdownToolbarScrollArea {{
                    background-color: {theme['bg_secondary']};
                    border: none;
                    padding: 0px;
                    margin: 0px;
                }}
                QScrollArea#markdownToolbarScrollArea > QWidget > QWidget {{
                    background-color: {theme['bg_secondary']};
                }}
                QScrollArea#markdownToolbarScrollArea QScrollBar:vertical {{
                    background-color: transparent;
                    background: transparent;
                    width: 6px;
                    border: none;
                    margin: 0px;
                    padding: 0px;
                }}
                QScrollArea#markdownToolbarScrollArea QScrollBar::groove:vertical {{
                    background: transparent;
                    border: none;
                }}
                QScrollArea#markdownToolbarScrollArea QScrollBar::handle:vertical {{
                    background-color: {theme['border']};
                    border-radius: 3px;
                    min-height: 20px;
                    margin: 0px 1px 0px 0px;
                }}
                QScrollArea#markdownToolbarScrollArea QScrollBar::handle:vertical:hover {{
                    background-color: {theme['bg_tertiary']};
                }}
                QScrollArea#markdownToolbarScrollArea QScrollBar::add-line:vertical,
                QScrollArea#markdownToolbarScrollArea QScrollBar::sub-line:vertical {{
                    height: 0px;
                    background: transparent;
                    border: none;
                }}
                QScrollArea#markdownToolbarScrollArea QScrollBar::left-arrow:vertical,
                QScrollArea#markdownToolbarScrollArea QScrollBar::right-arrow:vertical {{
                    width: 0px;
                    height: 0px;
                    background: transparent;
                }}
                QScrollArea#markdownToolbarScrollArea QScrollBar::add-page:vertical,
                QScrollArea#markdownToolbarScrollArea QScrollBar::sub-page:vertical {{
                    background: transparent;
                }}
            """
            scroll_area.setStyleSheet(scroll_style)
    
    def _create_toolbar_group(self, group_info):
        """创建工具栏按钮组"""
        # 创建组容器
        group_widget = QWidget()
        group_layout = QVBoxLayout(group_widget)
        group_layout.setContentsMargins(0, 0, 0, 0)
        group_layout.setSpacing(4)
        
        # 创建折叠/展开按钮
        # 展开状态显示：图标 + ▼，折叠状态显示：图标 + ▶
        collapse_btn = QPushButton(f"{group_info['icon']} ▼")
        collapse_btn.setObjectName("collapseButton")
        collapse_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        collapse_btn.setToolTip(group_info['tooltip'])
        collapse_btn.setCheckable(True)
        collapse_btn.setChecked(True)  # 默认展开
        collapse_btn.setFixedSize(TOOLBAR_BUTTON_SIZE, TOOLBAR_BUTTON_SIZE)
        
        # 绑定折叠/展开事件
        def make_toggle_handler(group_name):
            return lambda checked: self.toggle_toolbar_group(group_name, checked)
        collapse_btn.clicked.connect(make_toggle_handler(group_info['name']))
        
        # 创建按钮容器（用于折叠/展开）
        buttons_container = QWidget()
        # 启用硬件加速相关属性，提升动画性能
        buttons_container.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, False)  # 允许透明绘制
        buttons_container.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)  # 减少系统背景重绘
        # 优化布局更新策略，减少不必要的重绘
        buttons_container.setAttribute(Qt.WidgetAttribute.WA_StaticContents, False)  # 允许动态内容更新
        buttons_layout = QVBoxLayout(buttons_container)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(4)
        # 设置大小策略，优化布局计算
        buttons_container.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        
        # 创建组内所有按钮
        group_buttons = []
        for icon, name, callback in group_info['buttons']:
            btn = self._create_toolbar_button(icon, name, callback)
            buttons_layout.addWidget(btn)
            group_buttons.append(btn)
            self.markdown_toolbar_buttons.append(btn)
        
        # 组装组布局
        group_layout.addWidget(collapse_btn)
        group_layout.addWidget(buttons_container)
        
        # 保存组信息
        self.markdown_toolbar_groups.append({
            'name': group_info['name'],
            'icon': group_info['icon'],  # 保存图标信息
            'widget': group_widget,
            'collapse_button': collapse_btn,
            'buttons_container': buttons_container,
            'buttons': group_buttons,
            'expanded': True
        })
        
        # 预渲染：在创建时立即预计算并缓存高度，避免展开时的卡顿
        # 使用快速估算方法，避免调用sizeHint()导致卡顿（特别是按钮多的组）
        def precompute_height():
            # 使用快速估算，不调用sizeHint()，避免卡顿
            layout = buttons_container.layout()
            if layout:
                button_count = layout.count()
                # 快速估算：每个按钮高度 + 间距
                target_height = button_count * TOOLBAR_BUTTON_SIZE + max(0, (button_count - 1) * TOOLBAR_BUTTON_SPACING)
            else:
                target_height = 100  # 默认值
            
            # 立即缓存高度值（使用快速估算的结果）
            buttons_container._cached_height = target_height
        
        # 立即执行预计算（同步），确保缓存高度在创建时就准备好
        # 使用快速估算方法，不会阻塞UI
        precompute_height()
        
        return group_widget
    
    def _create_toolbar_button(self, icon, name, callback):
        """创建工具栏按钮"""
        btn = QPushButton(icon)
        btn.setFixedSize(TOOLBAR_BUTTON_SIZE, TOOLBAR_BUTTON_SIZE)  # 固定大小，防止被挤压
        btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        btn.setToolTip(name)
        
        if callback:
            btn.clicked.connect(callback)
            # 悬停时在状态栏显示名称
            btn.installEventFilter(self)
            btn.setProperty("toolbar_name", name)
        
        return btn
    
    def _create_toolbar_separator(self):
        """创建工具栏分隔线"""
        separator = QWidget()
        separator.setFixedHeight(1)
        separator.setStyleSheet(f"background-color: {self.current_theme['border']};")
        return separator
    
    def toggle_toolbar_group(self, group_name, expanded):
        """切换工具栏组的折叠状态"""
        if not hasattr(self, 'markdown_toolbar_groups'):
            return
        
        for group in self.markdown_toolbar_groups:
            if group['name'] == group_name:
                group['expanded'] = expanded
                collapse_btn = group['collapse_button']
                buttons_container = group['buttons_container']
                group_icon = group.get('icon', '')
                
                if expanded:
                    # 直接展开：显示容器
                    # 解除固定高度限制，让内容自适应
                    buttons_container.setMaximumHeight(16777215)
                    buttons_container.setMinimumHeight(0)
                    # 使用 setSizePolicy 来让控件根据内容自动调整大小
                    buttons_container.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
                    
                    # 显示容器
                    buttons_container.show()
                    
                    # 强制更新布局，确保容器根据内容自动调整高度
                    buttons_container.updateGeometry()
                    if buttons_container.parent():
                        buttons_container.parent().updateGeometry()
                    
                    collapse_btn.setText(f"{group_icon} ▼")
                    collapse_btn.setChecked(True)
                else:
                    # 直接折叠：隐藏容器
                    if hasattr(buttons_container, '_cached_height'):
                        buttons_container._cached_height = buttons_container.height()
                    buttons_container.hide()
                    collapse_btn.setText(f"{group_icon} ▶")
                    collapse_btn.setChecked(False)
                    # 折叠时也重置高度设置
                    buttons_container.setMaximumHeight(16777215)
                    buttons_container.setMinimumHeight(0)
                
                # 更新工具栏内容高度
                QTimer.singleShot(10, lambda: self._update_toolbar_content_height())
                break
    
    
    def _update_toolbar_content_height(self):
        """更新工具栏内容高度"""
        if not hasattr(self, 'markdown_toolbar_content') or not self.markdown_toolbar_content:
            return
        
        # 禁用更新，避免在计算过程中触发多次重绘
        self.markdown_toolbar_content.setUpdatesEnabled(False)
        
        try:
            toolbar_layout = self.markdown_toolbar_content.layout()
            if toolbar_layout:
                # 使用sizeHint()获取建议高度，确保所有内容都能显示
                min_height = toolbar_layout.sizeHint().height()
                if min_height > 0:
                    self.markdown_toolbar_content.setMinimumHeight(min_height)
                    # 同时设置最大高度，确保内容不会被压缩
                    self.markdown_toolbar_content.setMaximumHeight(min_height)
        finally:
            # 恢复更新
            self.markdown_toolbar_content.setUpdatesEnabled(True)
        
        # 更新滚动提示显示状态（延迟执行，避免阻塞）
        if (hasattr(self, 'markdown_toolbar_scroll_area') and 
            hasattr(self, 'markdown_toolbar_scroll_hint_top') and 
            hasattr(self, 'markdown_toolbar_scroll_hint_bottom')):
            QTimer.singleShot(10, lambda: self._update_scroll_hint(
                self.markdown_toolbar_scroll_area, 
                self.markdown_toolbar_scroll_hint_top,
                self.markdown_toolbar_scroll_hint_bottom
            ))
    
    def _update_scroll_hint(self, scroll_area, hint_top, hint_bottom):
        """更新滚动提示显示状态"""
        if not scroll_area or not hint_top or not hint_bottom:
            return
        
        scroll_bar = scroll_area.verticalScrollBar()
        if not scroll_bar:
            hint_top.hide()
            hint_bottom.hide()
            return
        
        # 检查是否可以滚动（内容高度是否超过可视区域）
        content_widget = scroll_area.widget()
        if not content_widget:
            hint_top.hide()
            hint_bottom.hide()
            return
        
        content_height = content_widget.height()
        viewport_height = scroll_area.viewport().height()
        
        # 检查是否可以滚动
        can_scroll = content_height > viewport_height
        
        if can_scroll:
            scroll_value = scroll_bar.value()
            scroll_max = scroll_bar.maximum()
            
            # 可以向上滚动：当前不在顶部
            can_scroll_up = scroll_value > 0
            # 可以向下滚动：当前不在底部
            can_scroll_down = scroll_value < scroll_max
            
            # 显示/隐藏顶部提示（向上三角）
            if can_scroll_up:
                hint_top.show()
            else:
                hint_top.hide()
            
            # 显示/隐藏底部提示（向下三角）
            if can_scroll_down:
                hint_bottom.show()
            else:
                hint_bottom.hide()
        else:
            # 不需要滚动，隐藏所有提示
            hint_top.hide()
            hint_bottom.hide()
    
    def update_markdown_toolbar_collapse(self):
        """更新工具栏内容高度（现在使用滚动提示，不再自动折叠）"""
        self._update_toolbar_content_height()
    
    def update_markdown_toolbar_size(self):
        """更新工具栏（现在只用于更新折叠状态）"""
        # 根据窗口高度自动折叠工具栏组
        self.update_markdown_toolbar_collapse()
    
    def update_markdown_toolbar_theme(self):
        """更新左侧Markdown工具栏主题"""
        if not self.markdown_toolbar_widget:
            return
        
        # 获取内容widget和滚动区域
        if hasattr(self, 'markdown_toolbar_content') and hasattr(self, 'markdown_toolbar_scroll_area'):
            content_widget = self.markdown_toolbar_content
            scroll_area = self.markdown_toolbar_scroll_area
        elif hasattr(self, 'markdown_toolbar_content'):
            content_widget = self.markdown_toolbar_content
            scroll_area = self.markdown_toolbar_widget if isinstance(self.markdown_toolbar_widget, QScrollArea) else None
        else:
            # 兼容旧版本
            content_widget = self.markdown_toolbar_widget
            scroll_area = None
        
        # 应用主题样式
        self._apply_toolbar_theme(content_widget, scroll_area)
        
        # 更新滚动提示样式
        if hasattr(self, 'markdown_toolbar_scroll_hint_top'):
            self.markdown_toolbar_scroll_hint_top.setStyleSheet(f"""
                QLabel#scrollHintLabelTop {{
                    color: {self.current_theme.get('text_secondary', self.current_theme.get('text', '#888888'))};
                    font-size: 10px;
                    background-color: transparent;
                    padding: 0px;
                }}
            """)
        if hasattr(self, 'markdown_toolbar_scroll_hint_bottom'):
            self.markdown_toolbar_scroll_hint_bottom.setStyleSheet(f"""
                QLabel#scrollHintLabelBottom {{
                    color: {self.current_theme.get('text_secondary', self.current_theme.get('text', '#888888'))};
                    font-size: 10px;
                    background-color: transparent;
                    padding: 0px;
                }}
            """)
        
        # 更新分隔线样式（遍历工具栏布局中的所有子项）
        toolbar_layout = content_widget.layout()
        if toolbar_layout:
            for i in range(toolbar_layout.count()):
                item = toolbar_layout.itemAt(i)
                if item and item.widget():
                    widget = item.widget()
                    # 检查是否是分隔线（高度为1的widget）
                    if widget.height() == 1:
                        widget.setStyleSheet(f"background-color: {self.current_theme['border']};")
    
    def eventFilter(self, obj, event):
        """事件过滤器，处理工具栏按钮悬停"""
        if isinstance(obj, QPushButton) and obj.property("toolbar_name"):
            if event.type() == QEvent.Type.Enter:
                name = obj.property("toolbar_name")
                self.status_bar.showMessage(name, 0)
                return False
            elif event.type() == QEvent.Type.Leave:
                self.status_bar.clearMessage()
                return False
        return super().eventFilter(obj, event)
        
    def create_new_tab(self, content="", file_path=None):
        """创建新标签页"""
        tab_id = self.current_tab_id
        self.current_tab_id += 1
        
        # 创建主分割器（左右布局：编辑器+预览 | 查找面板）
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 创建内容分割器（编辑器 | 预览）
        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧：编辑器
        editor = MarkdownTextEdit()  # 使用自定义编辑器支持列表自动接续
        editor_font = QFont("Consolas", self.editor_font_size)
        editor.setFont(editor_font)
        editor.document().setDefaultFont(editor_font)
        editor.setPlaceholderText("在此输入Markdown内容...")
        # 设置编辑器最小宽度，限制分隔器移动范围
        editor.setMinimumWidth(300)
        
        # 应用语法高亮（保存引用以防止被垃圾回收）
        editor.highlighter = MarkdownHighlighter(editor.document())
        
        editor.setText(content)
        editor.textChanged.connect(lambda: self.on_text_changed(tab_id))
        editor.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        editor.customContextMenuRequested.connect(lambda pos: self.show_context_menu(tab_id, pos))
        # 编辑器焦点事件
        editor.installEventFilter(self)
        
        # 中间：预览
        preview = QWebEngineView()
        # 设置预览窗最小宽度，限制分隔器移动范围
        preview.setMinimumWidth(300)
        # 启用JavaScript和远程内容加载
        settings = preview.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        # 启用硬件加速
        settings.setAttribute(QWebEngineSettings.WebAttribute.Accelerated2dCanvasEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, True)
        # QWebEngineView 默认使用硬件加速（如果系统支持），通过上面的设置已启用
        # 非实时区域优化：预览窗口不需要实时更新，减少渲染开销
        # 注意：QWebEngineView 没有直接的 layer.live 属性，但可以通过其他方式优化
        preview.setHtml(self.get_initial_html(), QUrl("https://cdnjs.cloudflare.com/"))
        
        # 添加到内容分割器
        content_splitter.addWidget(editor)
        content_splitter.addWidget(preview)
        content_splitter.setSizes([600, 600])  # 默认各占一半
        # 移除内容分割器的边框
        content_splitter.setStyleSheet("QSplitter { border: none; }")
        
        # 右侧：查找面板
        find_panel = FindPanel(self)
        find_panel.setMinimumWidth(280)  # 设置最小宽度
        find_panel.setMaximumWidth(400)  # 设置最大宽度
        find_panel.hide()  # 默认隐藏
        
        # 添加到主分割器
        main_splitter.addWidget(content_splitter)
        main_splitter.addWidget(find_panel)
        main_splitter.setSizes([1200, 0])  # 默认查找面板宽度为0（隐藏）
        
        # 设置主分割器样式，在预览窗和查找面板之间显示灰色分界线
        main_splitter.setObjectName("mainSplitter")
        main_splitter.setStyleSheet(f"""
            QSplitter#mainSplitter::handle {{
                background-color: {self.border_color};
                width: 2px;
            }}
            QSplitter#mainSplitter::handle:hover {{
                background-color: {self.accent_color};
            }}
        """)
        
        # 添加标签页
        tab_name = f"新建 {tab_id + 1}" if not file_path else Path(file_path).name
        index = self.tab_widget.addTab(main_splitter, tab_name)
        self.tab_widget.setCurrentIndex(index)
        
        # 存储标签页信息
        self.tabs[tab_id] = {
            'editor': editor,
            'preview': preview,
            'file_path': file_path,
            'splitter': main_splitter,
            'content_splitter': content_splitter,
            'find_panel': find_panel,
            'saved_content': content  # 保存当前内容，用于检测是否有未保存的修改
        }
        
        # 连接编辑器内容改变信号，更新字数统计
        editor.textChanged.connect(lambda: self.update_word_count_display())
        
        # 初始渲染
        self.update_preview(tab_id)
        
        # 设置滚动同步
        self.setup_scroll_sync(tab_id)
        
        return tab_id
    
    def get_current_tab_id(self):
        """获取当前标签页ID"""
        current_index = self.tab_widget.currentIndex()
        for tab_id, info in self.tabs.items():
            if self.tab_widget.indexOf(info['splitter']) == current_index:
                return tab_id
        return None
    
    def on_tab_changed(self):
        """标签页切换时更新字数统计和布局 - 添加淡入动画"""
        tab_id = self.get_current_tab_id()
        if tab_id is not None and tab_id in self.tabs:
            # 为新切换到的标签页添加淡入动画
            splitter = self.tabs[tab_id]['splitter']
            
            # 创建或获取动画对象
            # UI 动画：匹配显示器刷新率（通常 60fps 或更高）
            if not hasattr(splitter, '_fade_animation'):
                splitter._fade_animation = QPropertyAnimation(splitter, b'windowOpacity')
                splitter._fade_animation.setDuration(TOOLBAR_FADE_DURATION)
                splitter._fade_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
                # 设置更新间隔，匹配显示器刷新率
                if hasattr(splitter._fade_animation, 'setUpdateInterval'):
                    splitter._fade_animation.setUpdateInterval(_ui_update_interval)  # UI 动画帧率
            
            # 设置淡入动画
            splitter.setWindowOpacity(0.7)  # 初始透明度
            splitter._fade_animation.setStartValue(0.7)
            splitter._fade_animation.setEndValue(1.0)
            splitter._fade_animation.start()
        
        self.update_word_count_display()
        # 更新布局以适应窗口宽度
        self.update_layout_for_width()
    
    def on_text_changed(self, tab_id):
        """文本改变时更新预览"""
        # 使用定时器延迟更新，避免频繁渲染
        if not hasattr(self, '_update_timer'):
            self._update_timer = QTimer()
            self._update_timer.setSingleShot(True)
            self._update_timer.timeout.connect(self._do_update_preview)
            self._pending_tab_id = None
        
        # 重置定时器
        self._update_timer.stop()
        self._pending_tab_id = tab_id
        self._update_timer.start(PREVIEW_UPDATE_DELAY)  # 防抖延迟，减少渲染频率
    
    def _safe_stop_thread(self, thread_ref_name):
        """安全地停止并清理线程（避免访问已删除的对象）"""
        thread = getattr(self, thread_ref_name, None)
        if thread is None:
            return
        
        try:
            # 检查对象是否仍然有效
            if hasattr(thread, 'isRunning'):
                if thread.isRunning():
                    thread.terminate()
                    thread.wait(1000)  # 等待最多1秒
        except (RuntimeError, AttributeError):
            # 对象已被删除或属性不存在，忽略错误
            pass
        finally:
            # 重置引用，允许垃圾回收
            setattr(self, thread_ref_name, None)
    
    def _do_update_preview(self):
        """实际执行预览更新"""
        if self._pending_tab_id is not None:
            self.update_preview(self._pending_tab_id)
    
    
    def setup_scroll_sync(self, tab_id):
        """设置编辑器和预览窗的滚动同步"""
        if tab_id not in self.tabs:
            return
        
        editor = self.tabs[tab_id]['editor']
        preview = self.tabs[tab_id]['preview']
        
        # 连接编辑器的垂直滚动条变化信号
        editor.verticalScrollBar().valueChanged.connect(
            lambda value: self.sync_preview_scroll(tab_id, value)
        )
        
        # 监听预览窗的滚动事件，通过JavaScript实现
        # 在预览窗加载完成后添加滚动监听器
        preview.loadFinished.connect(lambda: self.add_scroll_listener_to_preview(tab_id))
    
    def add_scroll_listener_to_preview(self, tab_id):
        """为预览窗添加滚动监听器"""
        if tab_id not in self.tabs:
            return
        
        preview = self.tabs[tab_id]['preview']
        
        # 添加JavaScript代码来监听滚动事件
        scroll_script = """
        // 为了同步，需要一个方法来从Python设置滚动位置
        window.setPreviewScroll = function(scrollTop) {
            window.scrollTo(0, scrollTop);
        };
        
        // 存储上一次滚动位置，用于检测变化（初始化为当前滚动位置）
        window.lastScrollTop = window.pageYOffset || document.documentElement.scrollTop || 0;
        """
        preview.page().runJavaScript(scroll_script)
        
        # 设置一个定时器来定期检查预览窗的滚动位置
        # 创建一个定时器用于检查滚动位置（避免使用控制台消息）
        if not hasattr(self, '_scroll_check_timers'):
            self._scroll_check_timers = {}
        
        if tab_id in self._scroll_check_timers:
            self._scroll_check_timers[tab_id].stop()
        
        timer = QTimer(self)
        timer.timeout.connect(lambda: self.check_preview_scroll(tab_id))
        timer.start(16)  # 每16ms检查一次（约60fps），提高快速滚动时的响应性
        self._scroll_check_timers[tab_id] = timer
    
    def check_preview_scroll(self, tab_id):
        """定期检查预览窗滚动位置并同步到编辑器"""
        if tab_id not in self.tabs:
            return
        
        # 检查同步滚动是否启用
        if not hasattr(self, 'sync_scroll_enabled') or not self.sync_scroll_enabled:
            return
        
        # 避免在内容更新期间进行滚动同步
        if hasattr(self, '_updating_preview') and self._updating_preview:
            return
        
        # 如果正在同步滚动，避免循环触发
        if hasattr(self, '_syncing_scroll') and self._syncing_scroll:
            return
        
        preview = self.tabs[tab_id]['preview']
        
        # 获取当前滚动信息，并比较是否发生变化
        # 注意：如果 _syncing_scroll 为 True，说明是程序设置的滚动，lastScrollTop 应该已经更新
        # 所以这里只检查滚动位置是否真的发生了变化
        # PyQt6中runJavaScript不支持回调，需要通过window对象存储结果
        get_scroll_info_script = """
        (function() {
            const currentScrollTop = window.pageYOffset || document.documentElement.scrollTop;
            const lastScrollTop = window.lastScrollTop || 0;
            // 降低阈值到0.5像素，提高快速滚动时的检测灵敏度
            if (Math.abs(currentScrollTop - lastScrollTop) > 0.5) {
                // 更新 lastScrollTop
                window.lastScrollTop = currentScrollTop;
                window.scrollInfo = JSON.stringify({
                    scrollTop: currentScrollTop,
                    scrollHeight: document.documentElement.scrollHeight,
                    clientHeight: document.documentElement.clientHeight
                });
            } else {
                window.scrollInfo = null;
            }
        })();
        """
        
        preview.page().runJavaScript(get_scroll_info_script)
        
        # 立即读取滚动信息并同步到编辑器（减少延迟，提高快速滚动时的响应性）
        def read_scroll_info():
            # 读取 window.scrollInfo，如果存在则返回 JSON 字符串，否则返回 null
            read_script = "(function() { return window.scrollInfo || null; })()"
            preview.page().runJavaScript(read_script, lambda result: self._process_preview_scroll_info(tab_id, result))
        
        QTimer.singleShot(10, read_scroll_info)  # 减少延迟到10ms
    
    def _process_preview_scroll_info(self, tab_id, scroll_info_json):
        """处理预览窗滚动信息并同步到编辑器"""
        if not scroll_info_json or tab_id not in self.tabs:
            return
        
        try:
            import json
            # 如果返回的是字符串，需要解析；如果已经是字典，直接使用
            if isinstance(scroll_info_json, str):
                scroll_data = json.loads(scroll_info_json)
            else:
                scroll_data = scroll_info_json
            self.sync_editor_scroll(tab_id, scroll_data)
        except Exception as e:
            # 忽略解析错误，避免影响其他功能
            pass
    
    def sync_preview_scroll(self, tab_id, editor_scroll_value):
        """同步预览窗的滚动位置"""
        if tab_id not in self.tabs:
            return
        
        # 检查同步滚动是否启用
        if not hasattr(self, 'sync_scroll_enabled') or not self.sync_scroll_enabled:
            return
        
        # 如果正在更新预览，避免滚动同步
        if hasattr(self, '_updating_preview') and self._updating_preview:
            return
        
        # 如果正在同步滚动，避免循环触发
        # 但在快速滚动时，如果距离上次同步超过30ms，允许新的同步
        import time
        current_time = time.time() * 1000  # 转换为毫秒
        if hasattr(self, '_syncing_scroll') and self._syncing_scroll:
            if hasattr(self, '_last_sync_time') and (current_time - self._last_sync_time) < 30:
                return
        
        editor = self.tabs[tab_id]['editor']
        preview = self.tabs[tab_id]['preview']
        
        # 设置同步标志，防止预览窗滚动触发反向同步
        self._syncing_scroll = True
        self._last_sync_time = current_time
        
        # 获取编辑器文档信息
        editor_doc = editor.document()
        editor_max_scroll = max(0, editor_doc.size().height() - editor.viewport().height())
        
        # 获取滚动条的实际最大值，用于更准确的边界检测
        scroll_bar = editor.verticalScrollBar()
        scroll_bar_max = scroll_bar.maximum() if scroll_bar else editor_max_scroll
        
        if editor_max_scroll > 0:
            # 检查是否到达顶部或底部（考虑2像素的容差，提高边界检测准确性）
            # 使用滚动条的实际最大值进行边界检测，确保准确性
            is_at_top = editor_scroll_value <= 2
            is_at_bottom = editor_scroll_value >= (scroll_bar_max - 2) if scroll_bar_max > 0 else False
            
            # 获取预览窗的实际滚动信息
            get_scroll_info_script = """
            window.previewScrollInfo = JSON.stringify({
                scrollHeight: document.documentElement.scrollHeight,
                clientHeight: document.documentElement.clientHeight
            });
            """
            preview.page().runJavaScript(get_scroll_info_script)
            
            # 延迟读取并处理（PyQt6方式），减少延迟提高快速滚动时的响应性
            def process_scroll():
                # 读取实际的预览窗滚动信息
                read_script = "(function() { return window.previewScrollInfo || null; })()"
                preview.page().runJavaScript(read_script, lambda result: self._apply_preview_scroll(tab_id, result, editor_scroll_value, editor_max_scroll, is_at_top, is_at_bottom))
            
            QTimer.singleShot(10, process_scroll)  # 减少延迟到10ms
        else:
            # 如果没有可滚动内容，直接重置标志
            self._syncing_scroll = False
    
    def _apply_preview_scroll(self, tab_id, preview_info_json, editor_scroll_value, editor_max_scroll, is_at_top, is_at_bottom):
        """应用预览窗滚动位置"""
        if tab_id not in self.tabs:
            self._syncing_scroll = False
            return
        
        preview = self.tabs[tab_id]['preview']
        
        try:
            import json
            if preview_info_json:
                # 如果返回的是字符串，需要解析；如果已经是字典，直接使用
                if isinstance(preview_info_json, str):
                    preview_info = json.loads(preview_info_json)
                else:
                    preview_info = preview_info_json
                preview_scroll_height = preview_info.get('scrollHeight', 0)
                preview_client_height = preview_info.get('clientHeight', 600)
            else:
                # 如果无法获取信息，使用预览窗的实际高度
                preview_client_height = preview.height()
                preview_scroll_height = preview_client_height * 2
            
            preview_max_scroll = max(0, preview_scroll_height - preview_client_height)
            
            # 处理边界情况：如果编辑器到达顶部或底部，预览窗也应该到达顶部或底部
            if is_at_top:
                target_preview_scroll = 0
            elif is_at_bottom:
                # 使用一个很大的值确保能够滚动到真正的底部
                # JavaScript 的 scrollTo 会自动限制在有效范围内
                target_preview_scroll = preview_scroll_height  # 使用总高度，确保滚动到底部
            else:
                # 正常情况：按比例计算
                scroll_ratio = editor_scroll_value / editor_max_scroll if editor_max_scroll > 0 else 0
                target_preview_scroll = int(scroll_ratio * preview_max_scroll)
            
            # 先更新 lastScrollTop，再设置滚动位置，以避免触发反向同步
            combined_script = f"""
            window.lastScrollTop = {target_preview_scroll};
            window.scrollTo(0, {target_preview_scroll});
            """
            preview.page().runJavaScript(combined_script)
            
            # 快速重置同步标志，允许快速滚动时的连续同步（减少延迟到30ms）
            QTimer.singleShot(30, lambda: setattr(self, '_syncing_scroll', False))
        except Exception as e:
            # 如果出错，重置标志
            self._syncing_scroll = False
    
    
    
    def sync_editor_scroll(self, tab_id, preview_scroll_data):
        """同步编辑器的滚动位置"""
        if tab_id not in self.tabs:
            return
        
        # 检查同步滚动是否启用
        if not hasattr(self, 'sync_scroll_enabled') or not self.sync_scroll_enabled:
            return
        
        # 如果正在同步滚动，避免循环触发
        # 但在快速滚动时，如果距离上次同步超过30ms，允许新的同步
        import time
        current_time = time.time() * 1000  # 转换为毫秒
        if hasattr(self, '_syncing_scroll') and self._syncing_scroll:
            if hasattr(self, '_last_sync_time') and (current_time - self._last_sync_time) < 30:
                return
        
        # 如果正在更新预览，避免滚动同步
        if hasattr(self, '_updating_preview') and self._updating_preview:
            return
        
        editor = self.tabs[tab_id]['editor']
        preview = self.tabs[tab_id]['preview']
        
        try:
            preview_scroll_top = preview_scroll_data.get('scrollTop', 0)
            preview_scroll_height = preview_scroll_data.get('scrollHeight', 1000)
            preview_client_height = preview_scroll_data.get('clientHeight', 600)
            
            # 计算预览窗滚动比例
            preview_max_scroll = max(0, preview_scroll_height - preview_client_height)
            
            # 检查预览窗是否到达顶部或底部（考虑2像素的容差，提高边界检测准确性）
            is_at_top = preview_scroll_top <= 2
            # 边界检测：如果接近底部（距离底部2像素以内），或者滚动值大于等于最大滚动值
            is_at_bottom = (preview_max_scroll > 0 and 
                          (preview_scroll_top >= (preview_max_scroll - 2) or 
                           preview_scroll_top >= preview_scroll_height - preview_client_height - 2))
            
            # 获取编辑器信息
            editor_doc = editor.document()
            editor_max_scroll = max(0, editor_doc.size().height() - editor.viewport().height())
            
            # 设置同步标志，防止循环触发（在blockSignals之前设置）
            self._syncing_scroll = True
            self._last_sync_time = current_time
            
            # 临时断开信号连接，避免触发循环
            scroll_bar = editor.verticalScrollBar()
            scroll_bar.blockSignals(True)
            
            try:
                # 处理边界情况：如果预览窗到达顶部或底部，编辑器也应该到达顶部或底部
                if is_at_top:
                    target_editor_scroll = 0
                elif is_at_bottom:
                    # 使用滚动条的实际最大值，确保能够滚动到真正的底部
                    target_editor_scroll = scroll_bar.maximum()
                else:
                    # 正常情况：按比例计算
                    scroll_ratio = preview_scroll_top / preview_max_scroll if preview_max_scroll > 0 else 0
                    target_editor_scroll = int(scroll_ratio * editor_max_scroll)
                
                scroll_bar.setValue(target_editor_scroll)
                
                # 强制刷新编辑器视图，确保滚动位置立即生效
                # 只更新视口，避免重复更新
                editor.viewport().update()
                # 处理事件队列，确保更新立即生效
                QApplication.processEvents()
            finally:
                # 确保无论是否发生异常，都恢复信号连接
                scroll_bar.blockSignals(False)
                # 快速重置同步标志，允许快速滚动时的连续同步
                # 使用QTimer延迟重置，但时间很短（20ms），确保快速滚动时不会被阻塞
                QTimer.singleShot(20, lambda: setattr(self, '_syncing_scroll', False))
        except (AttributeError, RuntimeError, TypeError) as e:
            # 确保在异常时也重置标志
            self._syncing_scroll = False
            # 记录错误但不中断程序执行
            if hasattr(self, 'settings') and self.settings.value("debug", False, type=bool):
                print(f"滚动同步错误: {e}")
    
    def update_preview(self, tab_id):
        """更新预览（使用工作线程，避免阻塞GUI）"""
        if tab_id not in self.tabs:
            return
        
        # 设置更新标志，避免在内容更新期间进行滚动同步
        self._updating_preview = True
        
        editor = self.tabs[tab_id]['editor']
        preview = self.tabs[tab_id]['preview']
        content = editor.toPlainText()
        
        # 清理之前的渲染线程（安全检查，避免访问已删除的对象）
        self._safe_stop_thread('_markdown_render_thread')
        
        # 创建工作线程进行Markdown渲染
        # markdown_to_html方法已经包含了完整的转换流程（包括wrap_html_with_style）
        # 注意：该方法会访问self的主题属性，但这些属性是只读的，线程安全
        self._markdown_render_thread = MarkdownRenderThread(
            content, 
            tab_id,
            lambda c: self.markdown_to_html(c)  # markdown转换函数（包含完整流程）
        )
        self._markdown_render_thread.html_ready.connect(self._on_html_ready)
        self._markdown_render_thread.error_occurred.connect(self._on_render_error)
        self._markdown_render_thread.finished.connect(self._markdown_render_thread.deleteLater)
        self._markdown_render_thread.start()
    
    def _on_html_ready(self, html, tab_id):
        """Markdown渲染完成回调"""
        if tab_id not in self.tabs:
            return
        
        preview = self.tabs[tab_id]['preview']
        preview.setHtml(html, QUrl("https://cdnjs.cloudflare.com/"))
        
        # 预览更新后，设置滚动同步（如果尚未设置）
        # 在预览加载完成后会自动设置滚动监听器
        def on_load_finished():
            # 先添加滚动监听器，确保JavaScript函数被定义
            self.add_scroll_listener_to_preview(tab_id)
            # 触发MathJax重新渲染公式
            mathjax_script = """
            if (window.MathJax && window.MathJax.typesetPromise) {
                MathJax.typesetPromise().catch(function(err) {
                    console.log('MathJax渲染错误:', err);
                });
            }
            """
            preview.page().runJavaScript(mathjax_script)
            # 重置更新标志
            self._updating_preview = False
        
        preview.loadFinished.connect(on_load_finished, Qt.ConnectionType.UniqueConnection)
    
    def _on_render_error(self, error_msg):
        """Markdown渲染错误回调"""
        # 渲染错误时，重置更新标志
        self._updating_preview = False
        # 可以选择显示错误消息或静默处理
        # QMessageBox.warning(self, "渲染错误", f"预览渲染失败: {error_msg}")
    
    def markdown_to_html(self, content):
        """将Markdown转换为HTML"""
        if not content.strip():
            return self.get_initial_html()
        
        try:
            # 保护数学公式，避免Markdown解析器干扰
            math_placeholders = []
            
            def protect_math(match):
                """保护公式内容，转换为HTML实体避免干扰"""
                formula = match.group(0)
                # 将公式内容进行HTML转义保护
                import html
                escaped = html.escape(formula)
                idx = len(math_placeholders)
                math_placeholders.append(formula)  # 保存原始公式
                # 使用不会被Markdown处理的占位符
                return f'<span class="math-placeholder" data-idx="{idx}"></span>'
            
            # 保护独立公式块 $$...$$ (支持多行，包括空公式块)
            # 注意：必须在 Markdown 解析之前保护，避免被误解析
            content = sub(r'\$\$[\s\S]*?\$\$', protect_math, content)
            # 保护 \(...\) 格式 (先处理，避免被 $...$ 匹配干扰)
            content = sub(r'\\\([^\)]*?\\\)', protect_math, content)
            # 保护行内公式 $...$ (不跨行，至少有一个非空字符)
            content = sub(r'\$(?!\$)([^\$\n]+?)\$(?!\$)', protect_math, content)
            
            # 使用pymdown扩展
            html_body = markdown(content, extensions=[
                'extra',
                'codehilite',
                'toc',
                'pymdownx.tilde',      # 支持~~删除线~~
                'pymdownx.caret',      # 支持^^插入^^
                'pymdownx.mark',       # 支持==高亮==
            ], extension_configs={
                'pymdownx.tilde': {
                    'subscript': False  # 禁用~下标~，避免与公式冲突
                },
                'pymdownx.caret': {
                    'superscript': False,  # 禁用^上标^，避免与公式冲突
                    'insert': True
                }
            })
            
            # 恢复数学公式
            def restore_math(match):
                idx = int(match.group(1))
                if idx < len(math_placeholders):
                    formula = math_placeholders[idx]
                    # 直接返回原始公式，让 MathJax 处理
                    return formula
                return match.group(0)
            
            # 恢复数学公式
            html_body = sub(r'<span class="math-placeholder" data-idx="(\d+)"></span>', restore_math, html_body)
            
            # 修复公式块的行距问题：确保公式块（$$...$$）成为独立的块级元素
            # 方法：将段落中的公式块提取出来，使其成为独立的块级元素（不在p标签内）
            def fix_math_block_in_paragraph(match):
                para_content = match.group(1)
                # 检查是否包含公式块（$$...$$）
                if '$$' in para_content:
                    # 使用正则表达式分割段落内容，将公式块分离出来
                    # 匹配公式块或非公式块内容
                    parts = []
                    last_pos = 0
                    # 查找所有公式块
                    for math_match in compile(r'\$\$[\s\S]*?\$\$').finditer(para_content):
                        # 添加公式块之前的内容（如果有）
                        if math_match.start() > last_pos:
                            before = para_content[last_pos:math_match.start()].strip()
                            if before:
                                parts.append(('text', before))
                        # 添加公式块（作为独立块，不在p标签内）
                        parts.append(('math', math_match.group(0)))
                        last_pos = math_match.end()
                    # 添加剩余内容
                    if last_pos < len(para_content):
                        after = para_content[last_pos:].strip()
                        if after:
                            parts.append(('text', after))
                    
                    # 构建结果：文本内容放在p标签中，公式块独立
                    result_parts = []
                    current_text = []
                    for part_type, content in parts:
                        if part_type == 'text':
                            current_text.append(content)
                        else:  # math
                            # 如果有累积的文本，先输出为段落
                            if current_text:
                                result_parts.append(f'<p>{" ".join(current_text)}</p>')
                                current_text = []
                            # 公式块独立输出（前后加换行，使其成为独立块）
                            result_parts.append(f'\n\n{content}\n\n')
                    # 处理剩余的文本
                    if current_text:
                        result_parts.append(f'<p>{" ".join(current_text)}</p>')
                    
                    return '\n'.join(result_parts)
                return match.group(0)
            
            # 处理段落中的公式块
            html_body = sub(r'<p>((?:[^<]|<(?!\/p>))*?)</p>', fix_math_block_in_paragraph, html_body)
            
            # 清理多余的空白行（保留最多两个连续换行）
            html_body = sub(r'\n{3,}', '\n\n', html_body)
            
            return self.wrap_html_with_style(html_body)
        except Exception as e:
            # Markdown解析出错时返回纯文本
            import traceback
            traceback.print_exc()
            return self.wrap_html_with_style(f"<pre>{content}</pre>")
    
    def wrap_html_with_style(self, html_body):
        """为HTML添加完整样式"""
        # 根据当前主题设置预览窗口样式
        is_dark = self.is_dark_theme
        
        # 使用当前主题的颜色
        bg_color = self.bg_color
        text_color = self.text_color
        accent_color = self.accent_color
        
        if is_dark:
            # 黑夜模式：使用主题颜色
            heading_color = '#e0e0e0'
            code_bg = f"rgba(45, 45, 45, 0.5)"
            code_color = accent_color
            pre_bg = self.bg_secondary_color
            pre_text = self.text_color
            blockquote_bg = self.bg_secondary_color
            blockquote_border = self.border_color
            blockquote_text = self.text_secondary_color
            table_border = self.border_color
            table_header_bg = self.bg_secondary_color
            table_stripe_bg = self.bg_tertiary_color
            link_color = accent_color
            h6_color = self.text_secondary_color
            del_color = self.text_secondary_color
            h_border_color = self.border_color
            hr_bg = self.border_color
        else:
            # 白天模式：使用主题颜色
            heading_color = self.text_color
            code_bg = f"rgba(0, 0, 0, 0.05)"
            code_color = accent_color
            pre_bg = self.bg_secondary_color
            pre_text = self.text_color
            blockquote_bg = self.bg_secondary_color
            blockquote_border = self.border_color
            blockquote_text = self.text_secondary_color
            table_border = self.border_color
            table_header_bg = self.bg_secondary_color
            table_stripe_bg = self.bg_tertiary_color
            link_color = accent_color
            h6_color = self.text_secondary_color
            del_color = self.text_secondary_color
            h_border_color = self.border_color
            hr_bg = self.border_color
        
        return f'''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
    body {{
        font-family: 微软雅黑, -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
        padding: 20px;
        line-height: 1.8;
        color: {text_color};
        max-width: 100%;
        margin: 0;
        background-color: {bg_color};
        overflow-x: hidden;
        word-wrap: break-word;
        word-break: break-word;
    }}
    p {{ 
        margin: 0 0 16px 0;
        word-wrap: break-word;
        word-break: break-word;
        white-space: pre-wrap;
    }}
    h1, h2, h3, h4, h5, h6 {{
        margin-top: 24px;
        margin-bottom: 16px;
        font-weight: 600;
        line-height: 1.25;
        color: {heading_color};
        word-wrap: break-word;
        word-break: break-word;
    }}
    h1 {{ font-size: 2em; border-bottom: 2px solid {h_border_color}; padding-bottom: 0.3em; }}
    h2 {{ font-size: 1.5em; border-bottom: 1px solid {h_border_color}; padding-bottom: 0.3em; }}
    h3 {{ font-size: 1.25em; }}
    h4 {{ font-size: 1em; }}
    h5 {{ font-size: 0.875em; }}
    h6 {{ font-size: 0.85em; color: {h6_color}; }}
    strong, b {{ font-weight: 600; color: {heading_color}; }}
    em, i {{ font-style: italic; }}
    del {{ text-decoration: line-through; color: {del_color}; opacity: 0.8; }}
    mark {{ background-color: #fff3cd; color: #856404; padding: 2px 4px; border-radius: 0; }}
    sub {{ vertical-align: sub; font-size: 0.75em; }}
    sup {{ vertical-align: super; font-size: 0.75em; }}
    code {{
        background-color: {code_bg};
        padding: 0.2em 0.4em;
        border-radius: 0;
        font-family: "Consolas", "Monaco", "Courier New", monospace;
        font-size: 0.9em;
        color: {code_color};
    }}
    pre {{
        background-color: {pre_bg};
        border-radius: 0;
        padding: 16px;
        overflow-x: auto;
        line-height: 1.45;
        white-space: pre-wrap;
        word-wrap: break-word;
    }}
    pre code {{ background-color: transparent; padding: 0; color: {pre_text}; }}
    blockquote {{
        border-left: 0.25em solid {blockquote_border};
        padding: 0.5em 1em;
        color: {blockquote_text};
        margin: 0 0 16px 0;
        background-color: {blockquote_bg};
        word-wrap: break-word;
        word-break: break-word;
    }}
    blockquote blockquote {{ margin: 8px 0; border-left-color: {blockquote_border}; }}
    blockquote p {{ margin: 0.5em 0; }}
    table {{ 
        border-collapse: collapse; 
        width: auto; 
        max-width: 100%; 
        margin: 16px 0; 
        display: table;
        table-layout: auto;
    }}
    table th, table td {{ 
        border: 1px solid {table_border}; 
        padding: 8px 12px; 
        text-align: left; 
        vertical-align: top;
        word-wrap: break-word;
        word-break: break-word;
    }}
    table th {{ background-color: {table_header_bg}; font-weight: 600; }}
    table tr:nth-child(2n) {{ background-color: {table_stripe_bg}; }}
    table td strong, table td b {{ font-weight: 700; color: {heading_color}; }}
    table td em, table td i {{ font-style: italic; }}
    ul, ol {{ padding-left: 2em; margin: 0 0 16px 0; }}
    li {{ 
        margin: 0.5em 0;
        word-wrap: break-word;
        word-break: break-word;
    }}
    li > p {{ margin: 0.5em 0; }}
    input[type="checkbox"] {{ margin-right: 0.5em; }}
    hr {{ height: 0.25em; padding: 0; margin: 24px 0; background-color: {hr_bg}; border: 0; }}
    a {{ color: {link_color}; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    img {{ max-width: 100%; box-sizing: border-box; }}
    mjx-container {{ 
        display: inline-block; 
        line-height: 1.2;
        vertical-align: middle;
    }}
    mjx-container[display="true"] {{ 
        display: block; 
        text-align: center; 
        margin: 1em 0;
        line-height: 1.2;
    }}
    /* 当公式块紧挨着时（没有空行），保持合适的间距 */
    mjx-container[display="true"] + mjx-container[display="true"] {{
        margin-top: 0.8em;
    }}
    /* 段落内的公式块，确保有正确的上下边距 */
    p > mjx-container[display="true"] {{
        margin-top: 1em !important;
        margin-bottom: 1em !important;
        display: block;
    }}
    /* 段落内相邻的公式块，保持合适的间距 */
    p > mjx-container[display="true"] + mjx-container[display="true"] {{
        margin-top: 0.8em !important;
    }}
    /* 确保包含公式块的段落有正确的行距 */
    p {{
        margin: 0 0 16px 0;
    }}
    /* 如果段落只包含公式块，减少段落本身的margin影响 */
    p:only-child > mjx-container[display="true"]:only-child {{
        margin-top: 0;
        margin-bottom: 0;
    }}
    .MathJax {{ line-height: 1.2 !important; }}
    .MathJax_Display {{ line-height: 1.2 !important; margin: 1em 0 !important; }}
</style>
<script>
window.MathJax = {{
    tex: {{
        inlineMath: [['$', '$'], ['\\(', '\\)']],
        displayMath: [['$$', '$$']],
        processEscapes: true
    }},
    startup: {{
        ready: function() {{
            MathJax.startup.defaultReady();
            MathJax.startup.promise.then(function() {{
                MathJax.typesetPromise();
            }});
        }}
    }}
}};
</script>
<script id="MathJax-script" async src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/3.2.2/es5/tex-mml-chtml.min.js"></script>
</head>
<body>
{html_body}
</body>
</html>'''
    
    def get_initial_html(self):
        """获取初始HTML"""
        # 根据当前主题设置预览窗口样式
        bg_color = self.bg_color
        text_color = self.text_secondary_color
        
        # 包含JavaScript函数定义以支持滚动同步
        return f'''<!DOCTYPE html>
<html>
<head><meta charset="UTF-8">
<script>
// 为了同步，需要一个方法来从Python设置滚动位置
window.setPreviewScroll = function(scrollTop) {{
    window.scrollTo(0, scrollTop);
}};

// 存储上一次滚动位置，用于检测变化（初始化为当前滚动位置）
window.lastScrollTop = window.pageYOffset || document.documentElement.scrollTop || 0;
</script>
</head>
<body style="text-align:center; color:{text_color}; padding:50px; background-color:{bg_color};">
    <p><i>开始编辑以查看预览</i></p>
</body>
</html>'''
    
    def insert_markdown(self, text):
        """插入Markdown文本"""
        tab_id = self.get_current_tab_id()
        if tab_id is not None:
            editor = self.tabs[tab_id]['editor']
            cursor = editor.textCursor()
            cursor.insertText(text)
            editor.setFocus()
    
    def insert_markdown_wrapper(self, prefix, suffix):
        """插入包装类Markdown"""
        tab_id = self.get_current_tab_id()
        if tab_id is not None:
            editor = self.tabs[tab_id]['editor']
            cursor = editor.textCursor()
            if cursor.hasSelection():
                selected = cursor.selectedText()
                cursor.insertText(f"{prefix}{selected}{suffix}")
            else:
                cursor.insertText(f"{prefix}{suffix}")
                # 移动光标到中间位置
                cursor.movePosition(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.MoveAnchor, len(suffix))
            # 先设置光标位置，再设置焦点
            editor.setTextCursor(cursor)
            editor.setFocus()
    
    def open_file(self):
        """打开文件（使用工作线程，避免阻塞GUI）"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "打开Markdown文件",
            "",
            "Markdown文件 (*.md *.markdown);;所有文件 (*.*)"
        )
        
        if file_path:
            # 显示加载状态
            self.show_status_message_temporarily("正在打开文件...", 1000)
            
            # 清理之前的线程（安全检查，避免访问已删除的对象）
            self._safe_stop_thread('_file_worker_thread')
            
            # 创建工作线程读取文件
            self._file_worker_thread = FileWorkerThread('read', file_path)
            self._file_worker_thread.file_read.connect(self._on_file_read)
            self._file_worker_thread.error_occurred.connect(self._on_file_error)
            self._file_worker_thread.finished.connect(self._file_worker_thread.deleteLater)
            self._file_worker_thread.start()
    
    def _on_file_read(self, file_path, content):
        """文件读取完成回调"""
        self.create_new_tab(content, file_path)
        self.show_status_message_temporarily(f"已打开: {file_path}", 3000)
    
    def _on_file_error(self, error_msg):
        """文件操作错误回调"""
        QMessageBox.critical(self, "错误", f"文件操作失败: {error_msg}")
    
    def save_file(self):
        """保存文件（使用工作线程，避免阻塞GUI）"""
        tab_id = self.get_current_tab_id()
        if tab_id is None:
            return
        
        file_path = self.tabs[tab_id].get('file_path')
        
        if not file_path:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "保存Markdown文件",
                "",
                "Markdown文件 (*.md);;所有文件 (*.*)"
            )
        
        if file_path:
            content = self.tabs[tab_id]['editor'].toPlainText()
            
            # 显示保存状态
            self.show_status_message_temporarily("正在保存文件...", 1000)
            
            # 清理之前的线程（安全检查，避免访问已删除的对象）
            self._safe_stop_thread('_file_worker_thread')
            
            # 创建工作线程写入文件
            self._file_worker_thread = FileWorkerThread('write', file_path, content)
            self._file_worker_thread.file_written.connect(lambda path: self._on_file_written(path, tab_id, content))
            self._file_worker_thread.error_occurred.connect(self._on_file_error)
            self._file_worker_thread.finished.connect(self._file_worker_thread.deleteLater)
            self._file_worker_thread.start()
    
    def _on_file_written(self, file_path, tab_id, content):
        """文件写入完成回调"""
        self.tabs[tab_id]['file_path'] = file_path
        # 更新保存的内容，标记为已保存
        self.tabs[tab_id]['saved_content'] = content
        
        # 更新标签名
        index = self.tab_widget.indexOf(self.tabs[tab_id]['splitter'])
        self.tab_widget.setTabText(index, Path(file_path).name)
        
        self.show_status_message_temporarily(f"已保存: {file_path}", 3000)
    
    def close_tab(self, index):
        """关闭标签页"""
        # 找到对应的tab_id
        tab_id_to_remove = None
        for tab_id, info in self.tabs.items():
            if self.tab_widget.indexOf(info['splitter']) == index:
                tab_id_to_remove = tab_id
                break
        
        if tab_id_to_remove is not None:
            self.tab_widget.removeTab(index)
            del self.tabs[tab_id_to_remove]
        
        # 如果没有标签页了，创建一个新的
        if self.tab_widget.count() == 0:
            self.create_new_tab()
    
    def undo(self):
        """撤销"""
        tab_id = self.get_current_tab_id()
        if tab_id is not None:
            self.tabs[tab_id]['editor'].undo()
    
    def redo(self):
        """重做"""
        tab_id = self.get_current_tab_id()
        if tab_id is not None:
            self.tabs[tab_id]['editor'].redo()
    
    def get_current_editor(self):
        """获取当前编辑器"""
        tab_id = self.get_current_tab_id()
        if tab_id is not None:
            return self.tabs[tab_id]['editor']
        return None
    
    def get_word_count(self):
        """获取当前编辑器的字数统计"""
        editor = self.get_current_editor()
        if editor:
            content = editor.toPlainText()
            # 计算字数：包括中英文字符、数字等
            word_count = len(content)
            # 计算行数
            line_count = content.count('\n') + 1 if content else 0
            # 计算字符数（不包括换行符）
            char_count = len(content.replace('\n', ''))
            return word_count, line_count, char_count
        return 0, 0, 0
    
    def update_word_count_display(self):
        """更新字数统计显示"""
        word_count, line_count, char_count = self.get_word_count()
        self.word_count_label.setText(f"字数: {word_count} | 行数: {line_count} | 字符: {char_count}")
    
    def show_status_message(self, message, timeout=0):
        """显示状态栏消息，临时隐藏字数统计"""
        # 隐藏字数统计标签
        self.word_count_label.setVisible(False)
        # 显示消息
        self.status_bar.showMessage(message, timeout)
        
        # 如果设置了超时时间，则在超时后恢复字数统计显示
        if timeout > 0:
            QTimer.singleShot(timeout, self.restore_word_count_display)
        
    def restore_word_count_display(self):
        """恢复字数统计显示"""
        # 显示字数统计标签
        self.word_count_label.setVisible(True)
        # 更新字数统计
        self.update_word_count_display()
    
    def show_status_message_temporarily(self, message, timeout=2000):
        """临时显示状态栏消息，然后恢复字数统计"""
        self.show_status_message(message, timeout)
    
    def insert_markdown(self, prefix):
        """在光标位置插入Markdown前缀"""
        editor = self.get_current_editor()
        if not editor:
            return
        cursor = editor.textCursor()
        cursor.insertText(prefix)
        editor.setTextCursor(cursor)
        editor.setFocus()
    
    def insert_markdown_wrapper(self, prefix, suffix):
        """用Markdown语法包裹选中的文本"""
        editor = self.get_current_editor()
        if not editor:
            return
        cursor = editor.textCursor()
        if cursor.hasSelection():
            selected = cursor.selectedText()
            cursor.insertText(f"{prefix}{selected}{suffix}")
        else:
            cursor.insertText(f"{prefix}{suffix}")
            # 将光标移动到中间
            cursor.movePosition(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.MoveAnchor, len(suffix))
        editor.setTextCursor(cursor)
        editor.setFocus()
    
    def insert_link(self):
        """插入链接"""
        editor = self.get_current_editor()
        if not editor:
            return
        cursor = editor.textCursor()
        if cursor.hasSelection():
            selected = cursor.selectedText()
            cursor.insertText(f"[{selected}](链接地址)")
        else:
            cursor.insertText("[链接文本](链接地址)")
        editor.setTextCursor(cursor)
        editor.setFocus()
    
    def insert_code_block(self):
        """插入代码块"""
        editor = self.get_current_editor()
        if not editor:
            return
        cursor = editor.textCursor()
        cursor.insertText("```\n\n```\n")
        cursor.movePosition(QTextCursor.MoveOperation.Up, QTextCursor.MoveMode.MoveAnchor, 2)
        editor.setTextCursor(cursor)
        editor.setFocus()
    
    # Markdown工具栏插入方法
    def insert_markdown_header(self, level):
        """插入标题"""
        editor = self.get_current_editor()
        if not editor:
            return
        cursor = editor.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
        cursor.movePosition(QTextCursor.MoveOperation.EndOfLine, QTextCursor.MoveMode.KeepAnchor)
        line_text = cursor.selectedText()
        # 移除已有的标题标记
        from re import sub
        cleaned = sub(r'^#+\s*', '', line_text)
        new_text = '#' * level + ' ' + cleaned
        cursor.insertText(new_text)
        cursor.movePosition(QTextCursor.MoveOperation.EndOfLine)
        editor.setTextCursor(cursor)
        editor.setFocus()
    
    def insert_markdown_list(self, marker):
        """插入列表标记"""
        editor = self.get_current_editor()
        if not editor:
            return
        cursor = editor.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
        cursor.movePosition(QTextCursor.MoveOperation.EndOfLine, QTextCursor.MoveMode.KeepAnchor)
        line_text = cursor.selectedText()
        # 移除已有的列表标记
        from re import sub
        cleaned = sub(r'^([-*+]\s+|\d+\.\s+|[-*+]\s+\[[x ]\]\s+|>\s+)', '', line_text)
        new_text = marker + cleaned
        cursor.insertText(new_text)
        cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
        cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.MoveAnchor, len(marker))
        editor.setTextCursor(cursor)
        editor.setFocus()
    
    def insert_markdown_link(self):
        """插入链接"""
        editor = self.get_current_editor()
        if not editor:
            return
        cursor = editor.textCursor()
        selected_text = cursor.selectedText() if cursor.hasSelection() else ""
        dialog = LinkInsertDialog(self, selected_text)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            result = dialog.get_result()
            cursor.insertText(result)
            editor.setTextCursor(cursor)
        editor.setFocus()
    
    def insert_markdown_image(self):
        """插入图片"""
        editor = self.get_current_editor()
        if not editor:
            return
        dialog = ImageInsertDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            result = dialog.get_result()
            cursor = editor.textCursor()
            cursor.insertText(result)
            editor.setTextCursor(cursor)
        editor.setFocus()
    
    def insert_markdown_table(self):
        """插入表格"""
        editor = self.get_current_editor()
        if not editor:
            return
        dialog = TableInsertDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            result = dialog.get_result()
            cursor = editor.textCursor()
            cursor.insertText(result)
            editor.setTextCursor(cursor)
        editor.setFocus()
    
    def insert_markdown_code_block(self):
        """插入代码块"""
        editor = self.get_current_editor()
        if not editor:
            return
        dialog = CodeBlockInsertDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            result = dialog.get_result()
            cursor = editor.textCursor()
            cursor.insertText(result)
            cursor.movePosition(QTextCursor.MoveOperation.Up, QTextCursor.MoveMode.MoveAnchor, 2)
            editor.setTextCursor(cursor)
        editor.setFocus()
    
    def insert_markdown_separator(self):
        """插入分割线"""
        editor = self.get_current_editor()
        if not editor:
            return
        cursor = editor.textCursor()
        cursor.insertText("\n---\n\n")
        editor.setFocus()
    
    def insert_markdown_toc(self):
        """插入目录"""
        editor = self.get_current_editor()
        if not editor:
            return
        cursor = editor.textCursor()
        cursor.insertText("[TOC]\n\n")
        editor.setTextCursor(cursor)
        editor.setFocus()
    
    def insert_markdown_timestamp(self):
        """插入时间戳"""
        editor = self.get_current_editor()
        if not editor:
            return
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor = editor.textCursor()
        cursor.insertText(f"[{timestamp}] ")
        editor.setFocus()
    
    def insert_markdown_footnote(self):
        """插入脚注"""
        editor = self.get_current_editor()
        if not editor:
            return
        cursor = editor.textCursor()
        cursor.insertText("[^1]\n\n[^1]: 脚注内容")
        editor.setTextCursor(cursor)
        editor.setFocus()
    
    def insert_markdown_math_block(self):
        """插入数学公式块"""
        editor = self.get_current_editor()
        if not editor:
            return
        cursor = editor.textCursor()
        cursor.insertText("\n$$\n\n$$\n")
        cursor.movePosition(QTextCursor.MoveOperation.Up, QTextCursor.MoveMode.MoveAnchor, 2)
        editor.setTextCursor(cursor)
        editor.setFocus()
    
    
    def show_context_menu(self, tab_id, pos):
        """显示右键菜单"""
        editor = self.tabs[tab_id]['editor']
        menu = QMenu(self)
        
        # 基本编辑
        undo_action = menu.addAction("撤销")
        undo_action.triggered.connect(editor.undo)
        
        redo_action = menu.addAction("重做")
        redo_action.triggered.connect(editor.redo)
        
        menu.addSeparator()
        
        cut_action = menu.addAction("剪切")
        cut_action.triggered.connect(editor.cut)
        
        copy_action = menu.addAction("复制")
        copy_action.triggered.connect(editor.copy)
        
        paste_action = menu.addAction("粘贴")
        paste_action.triggered.connect(editor.paste)
        
        menu.addSeparator()
        
        
        clear_action = menu.addAction("🗑️ 清空内容")
        clear_action.triggered.connect(self.clear_current_tab)
        
        # 显示菜单
        menu.exec(editor.mapToGlobal(pos))
    
    def clear_current_tab(self):
        """清空当前标签页"""
        tab_id = self.get_current_tab_id()
        if tab_id is None:
            return
        
        reply = QMessageBox.question(
            self,
            "确认清空",
            "确定要清空当前标签页的所有内容吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.tabs[tab_id]['editor'].clear()
            self.show_status_message_temporarily("已清空内容", 2000)
    
    def copy_all_content(self):
        """复制当前编辑器的全部内容到剪贴板"""
        tab_id = self.get_current_tab_id()
        if tab_id is None:
            return
        
        content = self.tabs[tab_id]['editor'].toPlainText()
        if content:
            QApplication.clipboard().setText(content)
            self.show_status_message_temporarily("✅ 全文已复制到剪贴板", 2000)
        else:
            self.show_status_message_temporarily("⚠️ 当前内容为空", 2000)
    
    def select_all(self):
        """全选当前编辑器内容"""
        editor = self.get_current_editor()
        if editor:
            editor.selectAll()
    
    def show_find_dialog(self):
        """显示/隐藏查找面板"""
        tab_id = self.get_current_tab_id()
        if tab_id is None or tab_id not in self.tabs:
            return
        
        find_panel = self.tabs[tab_id]['find_panel']
        main_splitter = self.tabs[tab_id]['splitter']
        
        # 停止之前的动画（如果存在）
        if hasattr(main_splitter, '_find_panel_animation_timer'):
            timer = main_splitter._find_panel_animation_timer
            if timer.isActive():
                timer.stop()
            timer.deleteLater()
            del main_splitter._find_panel_animation_timer
        
        # 切换显示/隐藏（无动画）
        if find_panel.isVisible():
            # 隐藏查找面板
            current_sizes = main_splitter.sizes()
            if len(current_sizes) >= 2:
                # 将查找面板的宽度加到第一个部件上
                total_width = sum(current_sizes)
                find_panel.hide()
                main_splitter.setSizes([total_width, 0])
            else:
                find_panel.hide()
                main_splitter.setSizes([main_splitter.width(), 0])
        else:
            # 显示查找面板
            current_sizes = main_splitter.sizes()
            find_panel_width = 300
            
            if len(current_sizes) >= 2:
                # 从第一个部件中分出空间给查找面板
                current_width_0 = current_sizes[0]
                target_width_0 = max(400, current_width_0 - find_panel_width)  # 确保最小宽度
                find_panel.show()
                main_splitter.setSizes([target_width_0, find_panel_width])
            else:
                # 如果获取不到大小，使用总宽度计算
                total_width = main_splitter.width()
                target_width = max(400, total_width - find_panel_width)
                find_panel.show()
                main_splitter.setSizes([target_width, find_panel_width])
            
            find_panel.find_input.setFocus()
    
    def _on_find_panel_animation_value_changed(self, value):
        """处理查找面板动画值变化（将 QVariant 转换为 float）"""
        if hasattr(self, '_find_panel_updater'):
            try:
                # 将 QVariant 转换为 float
                float_value = float(value) if value is not None else 0.0
                self._find_panel_updater.update_requested(float_value)
            except (ValueError, TypeError):
                pass
    
    def _animate_find_panel_show(self, splitter, find_panel):
        """显示查找面板（带动画效果）"""
        # 停止之前的动画（如果存在）
        if hasattr(splitter, '_find_panel_animation_timer'):
            timer = splitter._find_panel_animation_timer
            if timer.isActive():
                timer.stop()
            timer.deleteLater()
        
        current_width = splitter.width()
        find_panel_width = 300
        target_width = current_width - find_panel_width
        
        # 获取当前大小
        current_sizes = splitter.sizes()
        if len(current_sizes) < 2:
            current_sizes = [current_width, 0]
        
        start_width_0 = current_sizes[0]
        start_width_1 = current_sizes[1]
        end_width_0 = target_width
        end_width_1 = find_panel_width
        
        # 显示面板
        find_panel.show()
        
        # 使用 QTimer 和缓动曲线来实现动画
        animation_duration = 300  # 300ms
        frame_count = int(animation_duration / 16)  # 约60fps
        current_frame = [0]  # 使用列表以便在闭包中修改
        
        easing = QEasingCurve(QEasingCurve.Type.OutCubic)
        
        # 创建定时器来更新动画
        timer = QTimer(splitter)
        timer.setInterval(16)  # 约60fps
        
        def update_animation():
            current_frame[0] += 1
            progress = min(current_frame[0] / frame_count, 1.0)
            eased_progress = easing.valueForProgress(progress)
            
            # 插值计算当前大小
            width_0 = int(start_width_0 + (end_width_0 - start_width_0) * eased_progress)
            width_1 = int(start_width_1 + (end_width_1 - start_width_1) * eased_progress)
            
            splitter.setSizes([width_0, width_1])
            
            if progress >= 1.0:
                timer.stop()
                splitter.setSizes([end_width_0, end_width_1])
                find_panel.find_input.setFocus()
                # 清理定时器引用
                if hasattr(splitter, '_find_panel_animation_timer'):
                    del splitter._find_panel_animation_timer
        
        timer.timeout.connect(update_animation)
        splitter._find_panel_animation_timer = timer
        timer.start()
    
    def _animate_find_panel_hide(self, splitter, find_panel):
        """隐藏查找面板（带动画效果）"""
        # 停止之前的动画（如果存在）
        if hasattr(splitter, '_find_panel_animation_timer'):
            timer = splitter._find_panel_animation_timer
            if timer.isActive():
                timer.stop()
            timer.deleteLater()
        
        current_width = splitter.width()
        
        # 获取当前大小
        current_sizes = splitter.sizes()
        if len(current_sizes) < 2:
            current_sizes = [current_width, 0]
        
        start_width_0 = current_sizes[0]
        start_width_1 = current_sizes[1]
        end_width_0 = current_width
        end_width_1 = 0
        
        # 使用 QTimer 和缓动曲线来实现动画
        animation_duration = 300  # 300ms
        frame_count = int(animation_duration / 16)  # 约60fps
        current_frame = [0]  # 使用列表以便在闭包中修改
        
        easing = QEasingCurve(QEasingCurve.Type.InCubic)
        
        # 创建定时器来更新动画
        timer = QTimer(splitter)
        timer.setInterval(16)  # 约60fps
        
        def update_animation():
            current_frame[0] += 1
            progress = min(current_frame[0] / frame_count, 1.0)
            eased_progress = easing.valueForProgress(progress)
            
            # 插值计算当前大小
            width_0 = int(start_width_0 + (end_width_0 - start_width_0) * eased_progress)
            width_1 = int(start_width_1 + (end_width_1 - start_width_1) * eased_progress)
            
            splitter.setSizes([width_0, width_1])
            
            if progress >= 1.0:
                timer.stop()
                find_panel.hide()
                splitter.setSizes([end_width_0, end_width_1])
                # 清理定时器引用
                if hasattr(splitter, '_find_panel_animation_timer'):
                    del splitter._find_panel_animation_timer
        
        timer.timeout.connect(update_animation)
        splitter._find_panel_animation_timer = timer
        timer.start()
    
    def insert_timestamp(self):
        """插入当前时间戳"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.insert_markdown(f"{timestamp}")
    
    def show_shortcuts_help(self):
        """显示快捷键帮助"""
        help_text = """
📝 Markdo 快捷键帮助

文件操作:
  Ctrl+N - 新建文件
  Ctrl+O - 打开文件  
  Ctrl+S - 保存文件
  Ctrl+Shift+S - 另存为

编辑操作:
  Ctrl+Z - 撤销
  Ctrl+Y - 重做
  Ctrl+A - 全选
  Ctrl+F - 查找
  Ctrl+Shift+C - 复制全文

文本格式:
  Ctrl+B - 加粗
  Ctrl+I - 斜体
  Ctrl+D - 删除线
  Ctrl+H - 高亮
  Ctrl+` - 行内代码
  Ctrl+1~6 - 标题1~6

插入内容:
  Ctrl+K - 插入链接
  Ctrl+Shift+K - 插入代码块
  Ctrl+L - 无序列表
  Ctrl+Shift+L - 有序列表
  Ctrl+R - 插入分割线
  Ctrl+T - 插入时间戳

工具栏:
  Ctrl+; - 显示/隐藏工具栏 (默认)
  Ctrl+M - 显示/隐藏工具栏 (备选)

帮助:
  F1 - 显示此帮助
"""
        
        # 创建帮助对话框
        help_dialog = QDialog(self)
        help_dialog.setWindowTitle("快捷键帮助")
        help_dialog.setFixedSize(500, 600)
        
        # 获取当前主题
        theme = self.current_theme  # 使用实例变量时应改为：theme_display_name = self.current_theme.get('display_name', theme_name) if hasattr(self, 'current_theme') else Theme.DARK
        
        help_dialog.setStyleSheet(f"""
            QDialog {{
                background-color: {theme['bg_secondary']};
                border-radius: 0;
            }}
            QTextEdit {{
                background-color: {theme['bg']};
                color: {theme['text']};
                border: none;
                border-radius: 0;
                padding: 12px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
                line-height: 1.4;
            }}
            QPushButton {{
                background-color: {theme['bg_secondary']};
                color: {theme['text']};
                border: none;
                padding: 8px 20px;
                border-radius: 0;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {theme['bg_tertiary']};
                border-color: {theme['border']};
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 标题
        title_label = QLabel("⌨️ 快捷键帮助")
        title_label.setStyleSheet(f"""
            font-size: 18px;
            font-weight: bold;
            color: {theme['accent']};
            padding: 10px;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # 帮助文本
        help_text_edit = QTextEdit()
        help_text_edit.setPlainText(help_text.strip())
        help_text_edit.setReadOnly(True)
        layout.addWidget(help_text_edit)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(help_dialog.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        help_dialog.setLayout(layout)
        
        # 显示对话框
        help_dialog.exec()
    
    def save_file_as(self):
        """另存为文件"""
        tab_id = self.get_current_tab_id()
        if tab_id is None:
            return
        
        # 获取当前文件路径作为默认路径
        current_file = self.tabs[tab_id].get('file_path', '')
        if current_file:
            from pathlib import Path
            default_name = Path(current_file).name
            default_dir = str(Path(current_file).parent)
        else:
            default_name = ""
            default_dir = ""
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "另存为Markdown文件",
            default_dir + "/" + default_name if default_name else default_dir,
            "Markdown文件 (*.md *.mdown *.markdown);;文本文件 (*.txt);;所有文件 (*)"
        )
        
        if file_path:
            # 保存文件
            content = self.tabs[tab_id]['editor'].toPlainText()
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                # 更新标签页的文件路径
                self.tabs[tab_id]['file_path'] = file_path
                # 更新保存的内容，标记为已保存
                self.tabs[tab_id]['saved_content'] = content
                
                # 更新标签页标题
                file_name = file_path.split('/')[-1] if '/' in file_path else file_path.split('\\\\')[-1]
                tab_index = self.tab_widget.indexOf(self.tabs[tab_id]['splitter'])
                self.tab_widget.setTabText(tab_index, file_name)
                
                # 更新状态栏
                self.show_status_message_temporarily(f"✅ 文件已另存为: {file_path}", 3000)
                
                # 更新窗口标题
                self.update_window_title()
                
            except Exception as e:
                QMessageBox.critical(self, "保存失败", f"无法保存文件:\n{str(e)}")
    
    def has_unsaved_changes(self, tab_id):
        """检查指定标签页是否有未保存的修改"""
        if tab_id not in self.tabs:
            return False
        
        current_content = self.tabs[tab_id]['editor'].toPlainText()
        saved_content = self.tabs[tab_id].get('saved_content', '')
        
        # 如果当前内容与保存的内容不同，说明有未保存的修改
        return current_content != saved_content
    
    def has_any_unsaved_changes(self):
        """检查是否有任何标签页存在未保存的修改"""
        for tab_id in self.tabs.keys():
            current_content = self.tabs[tab_id]['editor'].toPlainText()
            saved_content = self.tabs[tab_id].get('saved_content', '')
            
            # 如果文档有内容且与保存的内容不同，说明有未保存的修改
            if current_content.strip() and current_content != saved_content:
                return True
        return False
    
    def closeEvent(self, event):
        """窗口关闭事件 - 检查未保存的修改"""
        if self.has_any_unsaved_changes():
            # 查找有未保存修改的标签页
            unsaved_tabs = []
            for tab_id, tab_info in self.tabs.items():
                current_content = tab_info['editor'].toPlainText()
                saved_content = tab_info.get('saved_content', '')
                if current_content.strip() and current_content != saved_content:
                    file_path = tab_info.get('file_path')
                    tab_name = Path(file_path).name if file_path else f"新建 {tab_id + 1}"
                    unsaved_tabs.append((tab_id, tab_name))
            
            if unsaved_tabs:
                # 构建提示信息
                if len(unsaved_tabs) == 1:
                    message = f"文档 '{unsaved_tabs[0][1]}' 有未保存的修改。\n\n是否要保存？"
                else:
                    tab_names = '\n'.join([f"  • {name}" for _, name in unsaved_tabs])
                    message = f"以下 {len(unsaved_tabs)} 个文档有未保存的修改：\n\n{tab_names}\n\n是否要保存？"
                
                # 创建自定义对话框
                theme = self.current_theme
                save_dialog = QDialog(self)
                save_dialog.setWindowTitle("未保存的修改")
                save_dialog.setModal(True)
                save_dialog.setFixedSize(400, 180)
                save_dialog.setStyleSheet(f"""
                    QDialog {{
                        background-color: {theme['bg_secondary']};
                        border-radius: 0;
                    }}
                    QLabel {{
                        color: {theme['text']};
                        font-size: 14px;
                        font-weight: normal;
                        background-color: transparent;
                    }}
                    QPushButton {{
                        background-color: {theme['bg']};
                        color: {theme['text']};
                        border: 1px solid {theme['border']};
                        padding: 8px 24px;
                        border-radius: 0;
                        font-size: 13px;
                        font-weight: normal;
                        min-width: 80px;
                    }}
                    QPushButton:hover {{
                        background-color: {theme['bg_tertiary']};
                        border-color: {theme['accent']};
                    }}
                    QPushButton:pressed {{
                        background-color: {theme['accent']};
                        color: {theme['accent_text']};
                    }}
                """)
                
                layout = QVBoxLayout(save_dialog)
                layout.setContentsMargins(20, 20, 20, 15)
                layout.setSpacing(15)
                
                # 消息标签
                message_label = QLabel(message)
                message_label.setWordWrap(True)
                message_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
                layout.addWidget(message_label)
                
                # 按钮布局
                button_layout = QHBoxLayout()
                button_layout.addStretch()
                
                save_btn = QPushButton("保存")
                save_btn.setDefault(True)
                save_btn.clicked.connect(lambda: save_dialog.done(1))
                button_layout.addWidget(save_btn)
                
                discard_btn = QPushButton("不保存")
                discard_btn.clicked.connect(lambda: save_dialog.done(2))
                button_layout.addWidget(discard_btn)
                
                cancel_btn = QPushButton("取消")
                cancel_btn.clicked.connect(lambda: save_dialog.done(0))
                button_layout.addWidget(cancel_btn)
                
                layout.addLayout(button_layout)
                
                reply = save_dialog.exec()
                
                if reply == 1:  # 保存
                    # 保存所有未保存的标签页
                    for tab_id, tab_name in unsaved_tabs:
                        self.tab_widget.setCurrentIndex(
                            self.tab_widget.indexOf(self.tabs[tab_id]['splitter'])
                        )
                        self.save_file()
                    
                    # 再次检查是否还有未保存的修改
                    # 如果用户取消了某个保存对话框，仍然会有未保存的修改
                    if self.has_any_unsaved_changes():
                        # 还有未保存的修改，取消关闭
                        event.ignore()
                        return
                    else:
                        # 所有修改都已保存，允许关闭
                        event.accept()
                elif reply == 2:  # 不保存
                    # 放弃修改，直接退出
                    event.accept()
                else:  # 取消
                    # 取消关闭
                    event.ignore()
                    return
        
        # 清理所有动画工作线程
        self._cleanup_all_animation_workers()
        
        event.accept()
    
    def _cleanup_all_animation_workers(self):
        """清理所有动画工作线程"""
        # 清理其他工作线程
        self._safe_stop_thread('_file_worker_thread')
        self._safe_stop_thread('_markdown_render_thread')
    
    def open_settings(self):
        """打开设置窗口"""
        # 临时取消主窗口置顶（如果有）
        was_on_top = self.windowFlags() & Qt.WindowType.WindowStaysOnTopHint
        if was_on_top:
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, False)
            self.show()
        
        dialog = SettingsDialog(self)
        dialog.exec()
        
        # 恢复置顶状态
        if was_on_top:
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
            self.show()
    
    def show_about(self):
        """显示关于对话框"""
        about_text = """
        <div style="text-align: center;">
            <h2>📝 Markdo</h2>
            <p style="color: #666;">版本 1.0.4</p>
            <p style="color: #666;">PyQt6版本</p>
            <hr>
            <p><b>作者:</b> A8Z0RB</p>
            <p><b>官方QQ群:</b> 329474729</p>
            <p><b>GitHub:</b> <a href="https://github.com/A8Z0RB-CN/Markdo/">https://github.com/A8Z0RB-CN/Markdo/</a></p>
            <hr>
            <p style="color: #888; font-size: 11px;">
                一款简洁高效的Markdown编辑器<br>
                支持实时预览、悬浮工具栏、列表自动接续等功能
            </p>
        </div>
        """
        QMessageBox.about(self, "关于", about_text)
    
    def show_shortcuts(self):
        """显示快捷键帮助窗口"""
        theme = self.current_theme
        
        shortcuts_dialog = QDialog(self)
        shortcuts_dialog.setWindowTitle("⌨️ 快捷键列表")
        shortcuts_dialog.setMinimumSize(480, 650)
        shortcuts_dialog.setStyleSheet(f"""
            QDialog {{
                background-color: {theme['bg']};
            }}
            QScrollArea {{
                border: none;
                background-color: {theme['bg']};
            }}
            QWidget#scrollContent {{
                background-color: {theme['bg']};
            }}
            QGroupBox {{
                font-weight: bold;
                font-size: 13px;
                border: none;
                border-radius: 0;
                margin-top: 16px;
                padding: 20px 15px 15px 15px;
                background-color: {theme['bg_secondary']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 12px;
                padding: 0 8px;
                color: {theme['accent']};
                background-color: {theme['bg_secondary']};
            }}
        """)
        
        # 使用滚动区域
        from PyQt6.QtWidgets import QScrollArea
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        scroll_content = QWidget()
        scroll_content.setObjectName("scrollContent")
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setContentsMargins(20, 15, 20, 15)
        content_layout.setSpacing(15)
        
        # 标题
        title = QLabel("📝 Markdo 快捷键参考")
        title.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {theme['text']}; padding: 5px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(title)
        
        def create_shortcut_group(title_text, shortcuts):
            """ 创建快捷键分组"""
            group = QGroupBox(title_text)
            grid = QGridLayout()
            grid.setVerticalSpacing(12)
            grid.setHorizontalSpacing(25)
            grid.setContentsMargins(10, 15, 10, 10)
            
            for i, (key, desc) in enumerate(shortcuts):
                key_label = QLabel(key)
                key_label.setStyleSheet(f"""
                    font-weight: bold; 
                    color: {theme['accent']}; 
                    font-size: 13px;
                    padding: 3px 0px;
                    background-color: transparent;
                """)
                key_label.setMinimumWidth(120)
                grid.addWidget(key_label, i, 0)
                
                desc_label = QLabel(desc)
                desc_label.setStyleSheet(f"""
                    color: {theme['text']}; 
                    font-size: 13px;
                    padding: 3px 0px;
                    background-color: transparent;
                """)
                grid.addWidget(desc_label, i, 1)
            
            group.setLayout(grid)
            return group
        
        # 文件操作
        file_shortcuts = [
            ("Ctrl+N", "新建文件"),
            ("Ctrl+O", "打开文件"),
            ("Ctrl+S", "保存文件"),
            ("Ctrl+Shift+S", "另存为"),
        ]
        content_layout.addWidget(create_shortcut_group("文件操作", file_shortcuts))
        
        # 编辑操作
        edit_shortcuts = [
            ("Ctrl+Z", "撤销"),
            ("Ctrl+Y", "重做"),
            ("Ctrl+A", "全选"),
            ("Ctrl+F", "查找"),
            ("Ctrl+Shift+C", "复制全文"),
        ]
        content_layout.addWidget(create_shortcut_group("编辑操作", edit_shortcuts))
        
        # 文本格式
        format_shortcuts = [
            ("Ctrl+B", "加粗"),
            ("Ctrl+I", "斜体"),
            ("Ctrl+D", "删除线"),
            ("Ctrl+H", "高亮"),
            ("Ctrl+`", "行内代码"),
            ("Ctrl+1 ~ 6", "标题1 ~ 标题6"),
        ]
        content_layout.addWidget(create_shortcut_group("文本格式", format_shortcuts))
        
        # 插入内容
        insert_shortcuts = [
            ("Ctrl+K", "插入链接"),
            ("Ctrl+Shift+K", "插入代码块"),
            ("Ctrl+Q", "插入引用"),
            ("Ctrl+L", "插入无序列表"),
            ("Ctrl+Shift+L", "插入有序列表"),
            ("Ctrl+R", "插入分割线"),
            ("Ctrl+T", "插入时间戳"),
        ]
        content_layout.addWidget(create_shortcut_group("插入内容", insert_shortcuts))
        
        # 工具栏和帮助
        toolbar_shortcuts = [
            ("Ctrl+;", "显示/隐藏工具栏 (默认)"),
            ("Ctrl+M", "显示/隐藏工具栏 (备选)"),
            ("F1", "快捷键帮助"),
        ]
        content_layout.addWidget(create_shortcut_group("工具栏和帮助", toolbar_shortcuts))
        
        content_layout.addStretch()
        
        scroll.setWidget(scroll_content)
        
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 15)
        main_layout.addWidget(scroll)
        
        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme['bg_secondary']};
                color: {theme['text']};
                border: none;
                padding: 10px 40px;
                border-radius: 0;
                font-weight: bold;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {theme['bg_tertiary']};
                border-color: {theme['border']};
            }}
        """)
        close_btn.clicked.connect(shortcuts_dialog.accept)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)
        
        shortcuts_dialog.setLayout(main_layout)
        shortcuts_dialog.exec()
    
    

class FindPanel(QWidget):
    """查找面板 - 右侧面板，使用Grid布局"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_editor = parent
        self.current_match_index = -1
        self.matches = []
        self.search_text = ""
        
        self.init_ui()
        
        # 连接回车键到查找下一个
        self.find_input.returnPressed.connect(self.find_next)
    
    def get_theme(self):
        """获取当前主题"""
        if self.parent_editor and hasattr(self.parent_editor, 'current_theme'):
            return self.parent_editor.current_theme
        return Theme.DARK
    
    def init_ui(self):
        theme = self.get_theme()
        
        # 设置面板背景色并启用自动填充
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(theme['bg_secondary']))
        self.setPalette(palette)
        
        self.setStyleSheet(f"""
            FindPanel {{
                background-color: {theme['bg_secondary']};
                border: none;
            }}
            QWidget {{
                background-color: {theme['bg_secondary']};
            }}
            QLineEdit {{
                background-color: {theme['bg']};
                color: {theme['text']};
                border: 1px solid {theme['border']};
                padding: 8px 12px;
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: 2px solid {theme['accent']};
            }}
            QPushButton {{
                background-color: {theme['bg']};
                color: {theme['text']};
                border: 1px solid {theme['border']};
                padding: 8px 16px;
                font-size: 13px;
                min-height: 32px;
            }}
            QPushButton:hover {{
                background-color: {theme['bg_tertiary']};
            }}
            QPushButton:pressed {{
                background-color: {theme['accent']};
                color: {theme['accent_text']};
            }}
            QLabel {{
                background-color: {theme['bg_secondary']};
                color: {theme['text']};
                font-size: 13px;
            }}
            QCheckBox {{
                background-color: {theme['bg_secondary']};
                color: {theme['text']};
                font-size: 13px;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border: 1px solid {theme['border']};
                background-color: {theme['bg']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {theme['accent']};
            }}
        """)
        
        # 使用Grid布局
        grid_layout = QGridLayout()
        grid_layout.setContentsMargins(16, 16, 16, 16)
        grid_layout.setSpacing(0)
        grid_layout.setVerticalSpacing(0)
        
        # 标题行（包含标题和关闭按钮）
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(8)
        
        self.title_label = QLabel("🔍 查找")
        self.title_label.setStyleSheet(f"background-color: {theme['bg_secondary']}; font-size: 16px; font-weight: 600; color: {theme['accent']};")
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()
        
        # 关闭按钮
        self.close_btn = QPushButton("×")
        self.close_btn.setObjectName("closeBtn")
        self.close_btn.setFixedSize(24, 24)
        self.close_btn.setStyleSheet(f"""
            QPushButton#closeBtn {{
                background-color: transparent;
                color: {theme['text_secondary']};
                border: none;
                font-size: 20px;
                font-weight: 300;
                padding: 0;
            }}
            QPushButton#closeBtn:hover {{
                background-color: {theme['bg_tertiary']};
                color: {theme['text']};
            }}
            QPushButton#closeBtn:pressed {{
                background-color: {theme['accent']};
                color: {theme['accent_text']};
            }}
        """)
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.clicked.connect(self.close_panel)
        title_layout.addWidget(self.close_btn)
        
        # 将标题行添加到Grid布局
        self.title_widget = QWidget()
        self.title_widget.setLayout(title_layout)
        self.title_widget.setStyleSheet(f"background-color: {theme['bg_secondary']};")
        grid_layout.addWidget(self.title_widget, 0, 0, 1, 2)
        
        # 查找输入框（第1行，占2列）
        self.find_row_widget = QWidget()
        self.find_row_widget.setStyleSheet(f"background-color: {theme['bg_secondary']};")
        find_row_layout = QHBoxLayout()
        find_row_layout.setContentsMargins(0, 0, 0, 0)
        find_row_layout.setSpacing(8)
        self.find_label = QLabel("查找:")
        self.find_label.setStyleSheet(f"background-color: {theme['bg_secondary']}; color: {theme['text']}; font-size: 13px;")
        self.find_input = QLineEdit()
        self.find_input.setPlaceholderText("输入要查找的内容")
        find_row_layout.addWidget(self.find_label)
        find_row_layout.addWidget(self.find_input, 1)
        self.find_row_widget.setLayout(find_row_layout)
        grid_layout.addWidget(self.find_row_widget, 1, 0, 1, 2)
        
        # 选项复选框（第2行）
        self.case_sensitive_check = QCheckBox("区分大小写")
        self.whole_word_check = QCheckBox("全字匹配")
        grid_layout.addWidget(self.case_sensitive_check, 2, 0, 1, 2)
        grid_layout.addWidget(self.whole_word_check, 3, 0, 1, 2)
        
        # 按钮（第4行）
        self.button_row_widget = QWidget()
        self.button_row_widget.setStyleSheet(f"background-color: {theme['bg_secondary']};")
        button_row_layout = QHBoxLayout()
        button_row_layout.setContentsMargins(0, 0, 0, 0)
        button_row_layout.setSpacing(8)
        self.find_next_btn = QPushButton("查找下一个")
        self.find_prev_btn = QPushButton("查找上一个")
        button_row_layout.addWidget(self.find_next_btn)
        button_row_layout.addWidget(self.find_prev_btn)
        self.button_row_widget.setLayout(button_row_layout)
        grid_layout.addWidget(self.button_row_widget, 4, 0, 1, 2)
        
        # 结果标签（第5行）
        self.result_row_widget = QWidget()
        self.result_row_widget.setStyleSheet(f"background-color: {theme['bg_secondary']};")
        result_row_layout = QHBoxLayout()
        result_row_layout.setContentsMargins(0, 0, 0, 0)
        result_row_layout.setSpacing(0)
        self.result_label = QLabel("")
        self.result_label.setStyleSheet(f"background-color: {theme['bg_secondary']}; color: {theme['text_secondary']}; font-size: 12px;")
        self.result_label.setWordWrap(True)
        result_row_layout.addWidget(self.result_label)
        self.result_row_widget.setLayout(result_row_layout)
        grid_layout.addWidget(self.result_row_widget, 5, 0, 1, 2)
        
        # 添加弹性空间
        grid_layout.setRowStretch(6, 1)
        
        self.setLayout(grid_layout)
        
        # 连接信号
        self.find_input.textChanged.connect(self.on_text_changed)
        self.find_next_btn.clicked.connect(self.find_next)
        self.find_prev_btn.clicked.connect(self.find_prev)
    
    def close_panel(self):
        """关闭查找面板"""
        if self.parent_editor:
            tab_id = self.parent_editor.get_current_tab_id()
            if tab_id is not None and tab_id in self.parent_editor.tabs:
                main_splitter = self.parent_editor.tabs[tab_id]['splitter']
                
                # 停止之前的动画（如果存在）
                if hasattr(main_splitter, '_find_panel_animation_timer'):
                    timer = main_splitter._find_panel_animation_timer
                    if timer.isActive():
                        timer.stop()
                    timer.deleteLater()
                    del main_splitter._find_panel_animation_timer
                
                self.hide()
                # 调整分割器大小，将查找面板的宽度设为0
                current_sizes = main_splitter.sizes()
                if len(current_sizes) >= 2:
                    # 将查找面板的宽度加到第一个部件上
                    total_width = sum(current_sizes)
                    main_splitter.setSizes([total_width, 0])
                else:
                    main_splitter.setSizes([main_splitter.width(), 0])
    
    def update_theme(self):
        """更新主题"""
        theme = self.get_theme()
        
        # 更新面板背景色
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(theme['bg_secondary']))
        self.setPalette(palette)
        
        self.setStyleSheet(f"""
            FindPanel {{
                background-color: {theme['bg_secondary']};
                border: none;
            }}
            QWidget {{
                background-color: {theme['bg_secondary']};
            }}
            QLineEdit {{
                background-color: {theme['bg']};
                color: {theme['text']};
                border: 1px solid {theme['border']};
                padding: 8px 12px;
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: 2px solid {theme['accent']};
            }}
            QPushButton {{
                background-color: {theme['bg']};
                color: {theme['text']};
                border: 1px solid {theme['border']};
                padding: 8px 16px;
                font-size: 13px;
                min-height: 32px;
            }}
            QPushButton:hover {{
                background-color: {theme['bg_tertiary']};
            }}
            QPushButton:pressed {{
                background-color: {theme['accent']};
                color: {theme['accent_text']};
            }}
            QLabel {{
                background-color: {theme['bg_secondary']};
                color: {theme['text']};
                font-size: 13px;
            }}
            QCheckBox {{
                background-color: {theme['bg_secondary']};
                color: {theme['text']};
                font-size: 13px;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border: 1px solid {theme['border']};
                background-color: {theme['bg']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {theme['accent']};
            }}
        """)
        # 更新所有行容器widget的背景色
        if hasattr(self, 'title_widget'):
            self.title_widget.setStyleSheet(f"background-color: {theme['bg_secondary']};")
        if hasattr(self, 'find_row_widget'):
            self.find_row_widget.setStyleSheet(f"background-color: {theme['bg_secondary']};")
        if hasattr(self, 'button_row_widget'):
            self.button_row_widget.setStyleSheet(f"background-color: {theme['bg_secondary']};")
        if hasattr(self, 'result_row_widget'):
            self.result_row_widget.setStyleSheet(f"background-color: {theme['bg_secondary']};")
        # 更新标题标签样式
        if hasattr(self, 'title_label'):
            self.title_label.setStyleSheet(f"background-color: {theme['bg_secondary']}; font-size: 16px; font-weight: 600; color: {theme['accent']};")
        # 更新关闭按钮样式
        if hasattr(self, 'close_btn'):
            self.close_btn.setStyleSheet(f"""
                QPushButton#closeBtn {{
                    background-color: transparent;
                    color: {theme['text_secondary']};
                    border: none;
                    font-size: 20px;
                    font-weight: 300;
                    padding: 0;
                }}
                QPushButton#closeBtn:hover {{
                    background-color: {theme['bg_tertiary']};
                    color: {theme['text']};
                }}
                QPushButton#closeBtn:pressed {{
                    background-color: {theme['accent']};
                    color: {theme['accent_text']};
                }}
            """)
        # 更新查找标签样式
        if hasattr(self, 'find_label'):
            self.find_label.setStyleSheet(f"background-color: {theme['bg_secondary']}; color: {theme['text']}; font-size: 13px;")
        self.result_label.setStyleSheet(f"background-color: {theme['bg_secondary']}; color: {theme['text_secondary']}; font-size: 12px;")
    
    def on_text_changed(self, text):
        """文本变化时清除之前的匹配结果"""
        self.current_match_index = -1
        self.matches = []
        self.search_text = text
        if not text:
            self.result_label.setText("")
    
    def get_current_editor(self):
        """获取当前编辑器"""
        if self.parent_editor:
            return self.parent_editor.get_current_editor()
        return None
    
    def find_next(self):
        """查找下一个"""
        search_text = self.find_input.text()
        if not search_text:
            self.result_label.setText("请输入要查找的内容")
            return
        
        editor = self.get_current_editor()
        if not editor:
            return
        
        # 获取编辑器文本
        text = editor.toPlainText()
        if not text:
            self.result_label.setText("文档为空")
            return
        
        # 根据选项设置进行查找
        flags = QTextDocument.FindFlag(0)
        if self.case_sensitive_check.isChecked():
            flags = flags | QTextDocument.FindFlag.FindCaseSensitively
        
        if self.whole_word_check.isChecked():
            flags = flags | QTextDocument.FindFlag.FindWholeWords
        
        # 使用编辑器的查找功能
        # 如果是首次查找或搜索文本已更改，从当前光标位置开始
        if self.search_text != search_text:
            self.search_text = search_text
            # 从当前光标位置开始查找
            found = editor.find(search_text, flags)
        else:
            # 从当前匹配位置之后开始查找
            cursor = editor.textCursor()
            if cursor.hasSelection():
                # 如果有选中内容，从选中内容之后开始查找
                cursor.movePosition(QTextCursor.MoveOperation.Right)
                editor.setTextCursor(cursor)
            found = editor.find(search_text, flags)
        
        if found:
            # 更新当前匹配位置
            cursor = editor.textCursor()
            self.result_label.setText(f"找到匹配项: '{search_text}'")
        else:
            # 从头开始循环查找
            cursor = editor.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            editor.setTextCursor(cursor)
            found = editor.find(search_text, flags)
            if found:
                cursor = editor.textCursor()
                self.result_label.setText(f"已循环查找: '{search_text}'")
            else:
                self.result_label.setText(f"未找到: '{search_text}'")
    
    def find_prev(self):
        """查找上一个"""
        search_text = self.find_input.text()
        if not search_text:
            self.result_label.setText("请输入要查找的内容")
            return
        
        editor = self.get_current_editor()
        if not editor:
            return
        
        # 获取编辑器文本
        text = editor.toPlainText()
        if not text:
            self.result_label.setText("文档为空")
            return
        
        # 根据选项设置进行查找
        flags = QTextDocument.FindFlag.FindBackward
        if self.case_sensitive_check.isChecked():
            flags = flags | QTextDocument.FindFlag.FindCaseSensitively
        
        if self.whole_word_check.isChecked():
            flags = flags | QTextDocument.FindFlag.FindWholeWords
        
        # 使用编辑器的查找功能
        # 如果是首次查找或搜索文本已更改，从当前光标位置开始
        if self.search_text != search_text:
            self.search_text = search_text
            # 从当前光标位置开始查找
            found = editor.find(search_text, flags)
        else:
            # 从当前匹配位置之前开始查找
            cursor = editor.textCursor()
            if cursor.hasSelection():
                # 如果有选中内容，移动到选中内容之前开始查找
                cursor.movePosition(QTextCursor.MoveOperation.Left)
                editor.setTextCursor(cursor)
            found = editor.find(search_text, flags)
        
        if found:
            # 更新当前匹配位置
            cursor = editor.textCursor()
            self.result_label.setText(f"找到匹配项: '{search_text}'")
        else:
            # 从末尾开始循环查找
            cursor = editor.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            editor.setTextCursor(cursor)
            found = editor.find(search_text, flags)
            if found:
                cursor = editor.textCursor()
                self.result_label.setText(f"已循环查找: '{search_text}'")
            else:
                self.result_label.setText(f"未找到: '{search_text}'")
    
    def keyPressEvent(self, event):
        """处理键盘事件"""
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                self.find_prev()
            else:
                self.find_next()
        else:
            super().keyPressEvent(event)


class FindDialog(QDialog):
    """查找对话框（保留用于兼容）"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_editor = parent
        self.current_match_index = -1
        self.matches = []
        self.search_text = ""
        
        self.setWindowTitle("查找")
        self.setFixedSize(400, 180)
        self.init_ui()
        
        # 连接回车键到查找下一个
        self.find_input.returnPressed.connect(self.find_next)
    
    def get_theme(self):
        """获取当前主题"""
        if self.parent_editor and hasattr(self.parent_editor, 'current_theme'):
            return self.parent_editor.current_theme
        return Theme.DARK
    
    def init_ui(self):
        theme = self.get_theme()
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {theme['bg_secondary']};
                border-radius: 0;
            }}
            QLineEdit {{
                background-color: {theme['bg']};
                color: {theme['text']};
                border: 1px solid {theme['border']};
                padding: 6px 10px;
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: 2px solid {theme['accent']};
            }}
            QPushButton {{
                background-color: {theme['bg_secondary']};
                color: {theme['text']};
                border: 1px solid {theme['border']};
                padding: 6px 12px;
                font-size: 13px;
                min-width: 70px;
            }}
            QPushButton:hover {{
                background-color: {theme['bg_tertiary']};
            }}
            QPushButton:pressed {{
                background-color: {theme['accent']};
                color: {theme['accent_text']};
            }}
            QLabel {{
                color: {theme['text']};
                font-size: 13px;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 15)
        layout.setSpacing(12)
        
        # 查找输入框
        input_layout = QHBoxLayout()
        find_label = QLabel("查找:")
        self.find_input = QLineEdit()
        self.find_input.setPlaceholderText("输入要查找的内容")
        input_layout.addWidget(find_label)
        input_layout.addWidget(self.find_input)
        layout.addLayout(input_layout)
        
        # 选项复选框
        options_layout = QHBoxLayout()
        self.case_sensitive_check = QCheckBox("区分大小写")
        self.whole_word_check = QCheckBox("全字匹配")
        options_layout.addWidget(self.case_sensitive_check)
        options_layout.addWidget(self.whole_word_check)
        layout.addLayout(options_layout)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        self.find_next_btn = QPushButton("查找下一个")
        self.find_prev_btn = QPushButton("查找上一个")
        self.close_btn = QPushButton("关闭")
        
        self.find_next_btn.clicked.connect(self.find_next)
        self.find_prev_btn.clicked.connect(self.find_prev)
        self.close_btn.clicked.connect(self.close)
        
        button_layout.addWidget(self.find_next_btn)
        button_layout.addWidget(self.find_prev_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
        
        # 结果标签
        self.result_label = QLabel("")
        self.result_label.setStyleSheet(f"color: {theme['text_secondary']}; font-size: 12px;")
        layout.addWidget(self.result_label)
        
        self.setLayout(layout)
        
        # 连接输入框文本变化信号
        self.find_input.textChanged.connect(self.on_text_changed)
    
    def on_text_changed(self, text):
        """文本变化时清除之前的匹配结果"""
        self.current_match_index = -1
        self.matches = []
        self.search_text = text
        if not text:
            self.result_label.setText("")
    
    def get_current_editor(self):
        """获取当前编辑器"""
        if self.parent_editor:
            return self.parent_editor.get_current_editor()
        return None
    
    def find_next(self):
        """查找下一个"""
        search_text = self.find_input.text()
        if not search_text:
            self.result_label.setText("请输入要查找的内容")
            return
        
        editor = self.get_current_editor()
        if not editor:
            return
        
        # 获取编辑器文本
        text = editor.toPlainText()
        if not text:
            self.result_label.setText("文档为空")
            return
        
        # 根据选项设置进行查找
        flags = QTextDocument.FindFlag(0)
        if self.case_sensitive_check.isChecked():
            flags = flags | QTextDocument.FindFlag.FindCaseSensitively
        
        if self.whole_word_check.isChecked():
            flags = flags | QTextDocument.FindFlag.FindWholeWords
        
        # 使用编辑器的查找功能
        # 如果是首次查找或搜索文本已更改，从当前光标位置开始
        if self.search_text != search_text:
            self.search_text = search_text
            # 从当前光标位置开始查找
            found = editor.find(search_text, flags)
        else:
            # 从当前匹配位置之后开始查找
            cursor = editor.textCursor()
            if cursor.hasSelection():
                # 如果有选中内容，从选中内容之后开始查找
                cursor.movePosition(QTextCursor.MoveOperation.Right)
                editor.setTextCursor(cursor)
            found = editor.find(search_text, flags)
        
        if found:
            # 更新当前匹配位置
            cursor = editor.textCursor()
            self.result_label.setText(f"找到匹配项: '{search_text}'")
        else:
            # 从头开始循环查找
            cursor = editor.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            editor.setTextCursor(cursor)
            found = editor.find(search_text, flags)
            if found:
                cursor = editor.textCursor()
                self.result_label.setText(f"已循环查找: '{search_text}'")
            else:
                self.result_label.setText(f"未找到: '{search_text}'")
    
    def find_prev(self):
        """查找上一个"""
        search_text = self.find_input.text()
        if not search_text:
            self.result_label.setText("请输入要查找的内容")
            return
        
        editor = self.get_current_editor()
        if not editor:
            return
        
        # 获取编辑器文本
        text = editor.toPlainText()
        if not text:
            self.result_label.setText("文档为空")
            return
        
        # 根据选项设置进行查找
        flags = QTextDocument.FindFlag.FindBackward
        if self.case_sensitive_check.isChecked():
            flags = flags | QTextDocument.FindFlag.FindCaseSensitively
        
        if self.whole_word_check.isChecked():
            flags = flags | QTextDocument.FindFlag.FindWholeWords
        
        # 使用编辑器的查找功能
        # 如果是首次查找或搜索文本已更改，从当前光标位置开始
        if self.search_text != search_text:
            self.search_text = search_text
            # 从当前光标位置开始查找
            found = editor.find(search_text, flags)
        else:
            # 从当前匹配位置之前开始查找
            cursor = editor.textCursor()
            if cursor.hasSelection():
                # 如果有选中内容，移动到选中内容之前开始查找
                cursor.movePosition(QTextCursor.MoveOperation.Left)
                editor.setTextCursor(cursor)
            found = editor.find(search_text, flags)
        
        if found:
            # 更新当前匹配位置
            cursor = editor.textCursor()
            self.result_label.setText(f"找到匹配项: '{search_text}'")
        else:
            # 从末尾开始循环查找
            cursor = editor.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            editor.setTextCursor(cursor)
            found = editor.find(search_text, flags)
            if found:
                cursor = editor.textCursor()
                self.result_label.setText(f"已循环查找: '{search_text}'")
            else:
                self.result_label.setText(f"未找到: '{search_text}'")
    
    def keyPressEvent(self, event):
        """处理键盘事件"""
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        elif event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                self.find_prev()
            else:
                self.find_next()
        else:
            super().keyPressEvent(event)


class MarkdownEditorMethods:
    """MarkdownEditor 类的附加方法 - 用于修复类结构"""
    pass


# 以下方法属于 MarkdownEditor 类，通过猴子补丁添加
def _update_theme_settings(self, dark_theme_name, light_theme_name, theme_mode, auto_switch, night_start, night_end):
    """更新主题设置"""
    self.dark_theme_name = dark_theme_name
    self.light_theme_name = light_theme_name
    self.theme_mode = theme_mode
    self.auto_theme_switch = auto_switch
    self.night_start_time = night_start
    self.night_end_time = night_end
    
    if theme_mode == "auto":
        # 跟随时间自动切换模式
        if auto_switch:
            # 启用自动切换，启动定时器并立即检查
            self.theme_check_timer.start(THEME_CHECK_INTERVAL)
            self.check_and_switch_theme()  # 立即检查一次
        else:
            # 禁用自动切换，停止定时器
            # 应用当前时间段应对的主题（根据当前时间判断是白天还是黑夜）
            self.theme_check_timer.stop()
            try:
                current_time = datetime.now().time()
                night_start_t = datetime.strptime(night_start, "%H:%M").time()
                night_end_t = datetime.strptime(night_end, "%H:%M").time()
                
                # 判断是否在黑夜模式时间段内
                is_night_time = False
                if night_start_t > night_end_t:
                    is_night_time = current_time >= night_start_t or current_time < night_end_t
                elif night_start_t < night_end_t:
                    is_night_time = night_start_t <= current_time < night_end_t
                else:
                    is_night_time = True
                
                # 根据时间段应用对应主题
                target_theme = dark_theme_name if is_night_time else light_theme_name
                self.apply_theme(target_theme)
            except (ValueError, AttributeError):
                # 如果时间解析失败，默认使用黑夜主题
                self.apply_theme(dark_theme_name)
    elif theme_mode == "light":
        # 始终使用白天主题
        self.theme_check_timer.stop()
        self.apply_theme(light_theme_name)
    elif theme_mode == "dark":
        # 始终使用黑夜主题
        self.theme_check_timer.stop()
        self.apply_theme(dark_theme_name)


def _check_and_switch_theme(self):
    """检查当前时间并自动切换主题"""
    if not self.auto_theme_switch:
        return
        
    try:
        current_time = datetime.now().time()
        night_start = datetime.strptime(self.night_start_time, "%H:%M").time()
        night_end = datetime.strptime(self.night_end_time, "%H:%M").time()
    except (ValueError, AttributeError) as e:
        # 如果时间格式错误，使用默认值
        print(f"时间解析错误: {e}")
        return
        
    # 判断是否在黑夜模式时间段内
    is_night_time = False
    if night_start > night_end:
        # 跨越午夜（例如 18:00 - 06:00）
        # 从 night_start 到午夜，或从午夜到 night_end
        is_night_time = current_time >= night_start or current_time < night_end
    elif night_start < night_end:
        # 不跨越午夜（例如 06:00 - 18:00）
        # 从 night_start 到 night_end
        is_night_time = night_start <= current_time < night_end
    else:
        # night_start == night_end，全天都是黑夜模式
        is_night_time = True
        
    # 根据时间段选择对应的主题
    target_theme = self.dark_theme_name if is_night_time else self.light_theme_name
    if target_theme != self.current_theme_name:
        self.apply_theme(target_theme)


def _eventFilter(self, obj, event):
    """事件过滤器 - 处理编辑器焦点事件"""
    from PyQt6.QtCore import QEvent
    
    # 检查是否是编辑器
    is_editor = False
    for tab_info in self.tabs.values():
        if obj == tab_info['editor']:
            is_editor = True
            break
    
    # 现在不自动显示悬浮工具栏，只处理其他事件
    return super(MarkdownEditor, self).eventFilter(obj, event)


def _start_window_fade_in(self):
    """启动窗口淡入动画"""
    self.window_opacity_animation.setStartValue(0.0)
    self.window_opacity_animation.setEndValue(1.0)
    self.window_opacity_animation.finished.connect(self._on_window_fade_in_finished)
    self.window_opacity_animation.start()


def _on_window_fade_in_finished(self):
    """窗口淡入动画完成后的回调"""
    try:
        self.window_opacity_animation.finished.disconnect(self._on_window_fade_in_finished)
    except (TypeError, RuntimeError):
        pass


def _show_welcome(self):
    """显示开屏教程/使用指南"""
    try:
        # 确保窗口已经显示并获得焦点
        if not self.isVisible():
            self.show()
        self.raise_()
        self.activateWindow()
        
        # 确保窗口已经完全初始化
        QApplication.processEvents()
        
        # 创建并显示对话框
        dialog = WelcomeDialog(self)
        dialog.raise_()
        dialog.activateWindow()
        
        # 设置对话框初始透明度为0，准备淡入
        dialog.setWindowOpacity(0.0)
        
        # 显示对话框（但先隐藏）
        dialog.show()
        
        # 启动淡入动画
        dialog.opacity_animation.setStartValue(0.0)
        dialog.opacity_animation.setEndValue(1.0)
        dialog.opacity_animation.start()
        
        # 执行对话框
        result = dialog.exec()
        
        # 对话框关闭后，确保主窗口正确显示并获得焦点
        if result == QDialog.DialogCode.Accepted:
            # 确保主窗口可见
            if not self.isVisible():
                self.show()
            # 确保主窗口在最前面
            self.raise_()
            self.activateWindow()
            # 处理事件，确保窗口状态更新
            QApplication.processEvents()
    except Exception as e:
        # 如果出现异常，至少确保主窗口能正常显示
        try:
            if not self.isVisible():
                self.show()
            self.raise_()
            self.activateWindow()
            QApplication.processEvents()
        except:
            pass
        # 记录错误但不抛出，避免程序崩溃
        import traceback
        print(f"Error showing welcome dialog: {e}")
        traceback.print_exc()


# 将方法添加到MarkdownEditor类
MarkdownEditor.update_theme_settings = _update_theme_settings
MarkdownEditor.check_and_switch_theme = _check_and_switch_theme
MarkdownEditor.eventFilter = _eventFilter
MarkdownEditor._start_window_fade_in = _start_window_fade_in
MarkdownEditor._on_window_fade_in_finished = _on_window_fade_in_finished
MarkdownEditor.show_welcome = _show_welcome


def _update_editor_font_size(self, font_size):
    """更新编辑器字号"""
    self.editor_font_size = font_size
    # 更新所有标签页中的编辑器字号
    for tab_id, tab_info in self.tabs.items():
        editor = tab_info.get('editor')
        if editor:
            # 创建新字体对象并设置
            new_font = QFont("Consolas", font_size)
            editor.setFont(new_font)
            editor.document().setDefaultFont(new_font)


MarkdownEditor.update_editor_font_size = _update_editor_font_size


def _update_sync_scroll_setting(self, enabled):
    """更新同步滚动设置"""
    self.sync_scroll_enabled = enabled
    
    # 如果关闭同步滚动，确保所有编辑器的滚动条信号都被恢复
    # 防止之前可能被阻塞的信号导致编辑器无法滚动
    if not enabled:
        if hasattr(self, 'tabs'):
            for tab_id, tab_data in self.tabs.items():
                if 'editor' in tab_data:
                    editor = tab_data['editor']
                    scroll_bar = editor.verticalScrollBar()
                    if scroll_bar:
                        # 确保信号没有被阻塞
                        scroll_bar.blockSignals(False)
        
        # 重置同步标志
        self._syncing_scroll = False


MarkdownEditor.update_sync_scroll_setting = _update_sync_scroll_setting


def main():
    # 启用OpenGL硬件加速，提升渲染和动画性能
    # 设置 OpenGL 表面格式，启用硬件加速
    format = QSurfaceFormat()
    format.setVersion(3, 3)  # 使用 OpenGL 3.3
    format.setProfile(QSurfaceFormat.OpenGLContextProfile.CoreProfile)
    format.setRenderableType(QSurfaceFormat.RenderableType.OpenGL)
    format.setSwapBehavior(QSurfaceFormat.SwapBehavior.DoubleBuffer)
    format.setSwapInterval(1)  # 启用垂直同步
    QSurfaceFormat.setDefaultFormat(format)
    
    # 设置应用程序属性，优先使用桌面 OpenGL
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseDesktopOpenGL, True)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts, True)
    
    app = QApplication(argv)
    
    # 初始化动画帧率设置，匹配显示器刷新率
    init_animation_frame_rates()
    
    # 设置全局字体为微软雅黑
    font = QFont("Microsoft YaHei", 9)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    app.setFont(font)
    
    # 设置应用样式
    app.setStyle('Fusion')
    
    # 设置应用图标
    app_icon = get_app_icon()
    if not app_icon.isNull():
        app.setWindowIcon(app_icon)
    
    try:
        window = MarkdownEditor()
        window.show()
        
        # 检查命令行参数，如果有文件路径则打开该文件
        if len(argv) > 1:
            file_path = argv[1]
            # 检查文件是否存在且是.md或.markdown文件
            if exists(file_path) and file_path.lower().endswith(('.md', '.markdown')):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    window.create_new_tab(content, file_path)
                except Exception as e:
                    # 记录错误但不阻止程序启动
                    import traceback
                    print(f"Warning: 无法打开文件: {file_path}, 错误: {str(e)}")
                    traceback.print_exc()
        
        exit(app.exec())
    except Exception as e:
        # 捕获所有未处理的异常，记录详细信息
        log_exception(type(e), e, e.__traceback__, "程序主循环")
        
        # 尝试显示错误对话框
        try:
            error_msg = QMessageBox()
            error_msg.setIcon(QMessageBox.Icon.Critical)
            error_msg.setWindowTitle("错误")
            error_msg.setText(f"程序启动失败:\n{str(e)}\n\n详细信息已记录到日志文件。")
            error_msg.setDetailedText(traceback.format_exc())
            error_msg.exec()
        except Exception as msg_error:
            log_exception(type(msg_error), msg_error, msg_error.__traceback__, "显示错误对话框")
        
        exit(1)


if __name__ == '__main__':
    main()
