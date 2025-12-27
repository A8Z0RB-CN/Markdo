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
    QGraphicsOpacityEffect
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPoint, QSettings, QUrl, QObject, QRect, QTime, QPropertyAnimation, QEasingCurve, QSequentialAnimationGroup
from PyQt6.QtGui import QFont, QColor, QAction, QKeySequence, QTextCursor, QShortcut, QSyntaxHighlighter, QTextCharFormat, QPalette, QIcon, QMouseEvent, QPainter, QPen, QCursor, QTextDocument
from re import compile, match, sub, IGNORECASE
from os.path import dirname, abspath, join, exists
from os import getcwd
from datetime import datetime


# ==================== 工具函数 ====================
def get_icon_path(filename):
    """获取图标文件路径"""
    if getattr(sys, 'frozen', False):
        # 打包后的可执行文件（cx_Freeze）
        # 打包后，数据文件在可执行文件所在目录
        application_path = dirname(executable)
        # 确保路径存在
        if not exists(application_path):
            application_path = dirname(abspath(executable))
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


def get_app_icon():
    """获取应用图标"""
    icon_path = get_icon_path('markdo-icon.png')
    if exists(icon_path):
        return QIcon(icon_path)
    # 如果找不到，尝试其他可能的文件名
    fallback_path = get_icon_path('Markdo.png')
    if exists(fallback_path):
        return QIcon(fallback_path)
    return QIcon()  # 返回空图标


# ==================== 主题系统 ====================
class Theme:
    """主题配置"""
    DARK = {
        'name': 'dark',
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
    
    LIGHT = {
        'name': 'light',
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
        return Theme.DARK if name == 'dark' else Theme.LIGHT
    
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
                border-radius: 0;
                padding: 12px;
                selection-background-color: {theme['accent']};
                selection-color: {theme['accent_text']};
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 13px;
                line-height: 1.6;
            }}
            QTextEdit:focus {{
                border: none;
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
        self.settings = QSettings("Markdo", "Settings")
        self.init_ui()
        self.load_settings()
        
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("⚙️ 设置")
        self.setFixedSize(550, 650)
        
        # 获取当前主题
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
                border: none;
                padding: 10px 14px;
                border-radius: 0;
                font-size: 14px;
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
                border: none;
                border-radius: 0;
                padding: 4px;
            }}
            QComboBox QAbstractItemView::item {{
                padding: 8px 12px;
                border-radius: 0;
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
        appearance_layout = QVBoxLayout()
        
        # 主题选择
        theme_layout = QHBoxLayout()
        theme_label = QLabel("主题：")
        self.theme_combo = QComboBox()
        self.theme_combo.addItem("🌙 黑夜模式", "dark")
        self.theme_combo.addItem("☀️ 白天模式", "light")
        self.theme_combo.setMinimumWidth(180)
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        appearance_layout.addLayout(theme_layout)
        
        # 自动切换主题选项
        self.auto_theme_checkbox = QCheckBox("根据时间自动切换主题")
        self.auto_theme_checkbox.setToolTip("开启后，将在指定时间自动切换黑夜/白天模式")
        self.auto_theme_checkbox.toggled.connect(self.on_auto_theme_toggled)
        appearance_layout.addWidget(self.auto_theme_checkbox)
        
        # 时间设置区域
        time_layout = QHBoxLayout()
        time_layout.setContentsMargins(30, 0, 0, 0)
        
        night_start_label = QLabel("黑夜模式开始：")
        self.night_start_time = QTimeEdit()
        self.night_start_time.setDisplayFormat("HH:mm")
        self.night_start_time.setTime(QTime(18, 0))  # 默认18:00
        # 确保时间控件可以正常编辑
        from PyQt6.QtWidgets import QAbstractSpinBox
        self.night_start_time.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.UpDownArrows)  # 显示上下箭头按钮
        self.night_start_time.setKeyboardTracking(False)  # 禁用键盘跟踪，提高响应速度
        
        night_end_label = QLabel("黑夜模式结束：")
        self.night_end_time = QTimeEdit()
        self.night_end_time.setDisplayFormat("HH:mm")
        self.night_end_time.setTime(QTime(6, 0))  # 默认6:00
        self.night_end_time.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.UpDownArrows)  # 显示上下箭头按钮
        self.night_end_time.setKeyboardTracking(False)  # 禁用键盘跟踪，提高响应速度
        
        time_layout.addWidget(night_start_label)
        time_layout.addWidget(self.night_start_time)
        time_layout.addSpacing(20)
        time_layout.addWidget(night_end_label)
        time_layout.addWidget(self.night_end_time)
        time_layout.addStretch()
        
        appearance_layout.addLayout(time_layout)
        
        # 提示信息
        time_hint_label = QLabel("提示：自动切换时，手动主题选择将被忽略")
        time_hint_label.setStyleSheet(f"color: {theme['text_secondary']}; font-size: 12px;")
        time_hint_label.setContentsMargins(30, 0, 0, 0)
        appearance_layout.addWidget(time_hint_label)
        
        appearance_group.setLayout(appearance_layout)
        layout.addWidget(appearance_group)
        
        # 悬浮工具栏设置组
        toolbar_group = QGroupBox("悬浮工具栏")
        toolbar_layout = QVBoxLayout()
        
        # 快捷键自定义
        hotkey_layout = QHBoxLayout()
        hotkey_label = QLabel("显示/隐藏快捷键：")
        self.hotkey_input = QLineEdit()
        self.hotkey_input.setPlaceholderText("点击此处并按下想要设置的快捷键")
        self.hotkey_input.setReadOnly(True)
        self.hotkey_input.setMinimumWidth(160)
        self.hotkey_input.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.hotkey_input.mousePressEvent = self.on_hotkey_input_click
        reset_btn = QPushButton("重置为Ctrl+;")
        reset_btn.setMaximumWidth(140)
        reset_btn.clicked.connect(self.reset_hotkey)
        hotkey_layout.addWidget(hotkey_label)
        hotkey_layout.addWidget(self.hotkey_input)
        hotkey_layout.addWidget(reset_btn)
        hotkey_layout.addStretch()
        toolbar_layout.addLayout(hotkey_layout)
        
        # 提示信息
        hint_label = QLabel("提示：默认快捷键 Ctrl+;")
        hint_label.setStyleSheet(f"color: {theme['text_secondary']}; font-size: 12px;")
        toolbar_layout.addWidget(hint_label)
        
        toolbar_group.setLayout(toolbar_layout)
        layout.addWidget(toolbar_group)
        
        # 常规设置组
        general_group = QGroupBox("常规")
        general_layout = QVBoxLayout()
        
        # 启动时显示使用指南开关（默认开启）
        self.show_welcome_checkbox = QCheckBox("启动时显示使用指南")
        self.show_welcome_checkbox.setToolTip("开启后，每次启动程序时会显示使用指南")
        self.show_welcome_checkbox.setChecked(True)  # 默认选中
        general_layout.addWidget(self.show_welcome_checkbox)
        
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
        theme_name = self.settings.value("theme", "dark", type=str)
        index = self.theme_combo.findData(theme_name)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
        
        # 加载自动切换主题设置
        auto_theme = self.settings.value("theme/auto_switch", False, type=bool)
        self.auto_theme_checkbox.setChecked(auto_theme)
        
        # 加载黑夜模式时间设置
        night_start = self.settings.value("theme/night_start", "18:00", type=str)
        night_end = self.settings.value("theme/night_end", "06:00", type=str)
        try:
            self.night_start_time.setTime(QTime.fromString(night_start, "HH:mm"))
        except:
            self.night_start_time.setTime(QTime(18, 0))  # 如果解析失败，使用默认值
        try:
            self.night_end_time.setTime(QTime.fromString(night_end, "HH:mm"))
        except:
            self.night_end_time.setTime(QTime(6, 0))  # 如果解析失败，使用默认值
        
        # 更新时间控件的启用状态
        self.on_auto_theme_toggled(auto_theme)
        
        # 加载快捷键设置
        hotkey = self.settings.value("toolbar/hotkey", "Ctrl+;", type=str)
        self.hotkey_input.setText(hotkey)
        
        # 加载启动时显示使用指南设置
        show_welcome = self.settings.value("show_welcome", True, type=bool)
        self.show_welcome_checkbox.setChecked(show_welcome)
    
    def on_auto_theme_toggled(self, checked):
        """自动切换主题复选框切换事件"""
        self.night_start_time.setEnabled(checked)
        self.night_end_time.setEnabled(checked)
        self.theme_combo.setEnabled(not checked)
    
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
        theme_name = self.theme_combo.currentData()
        self.settings.setValue("theme", theme_name)
        
        # 保存自动切换主题设置
        auto_theme = self.auto_theme_checkbox.isChecked()
        self.settings.setValue("theme/auto_switch", auto_theme)
        
        # 保存黑夜模式时间设置
        night_start = self.night_start_time.time().toString("HH:mm")
        night_end = self.night_end_time.time().toString("HH:mm")
        self.settings.setValue("theme/night_start", night_start)
        self.settings.setValue("theme/night_end", night_end)
        
        # 保存快捷键设置（验证快捷键有效性 ）
        hotkey = self.hotkey_input.text().strip()
        if not hotkey:
            hotkey = "Ctrl+;"  # 默认快捷键
        self.settings.setValue("toolbar/hotkey", hotkey)
        
        # 保存启动时显示使用指南设置
        show_welcome = self.show_welcome_checkbox.isChecked()
        self.settings.setValue("show_welcome", show_welcome)
        
        # 通知父窗口更新设置
        if self.parent_editor:
            self.parent_editor.update_theme_settings(theme_name, auto_theme, night_start, night_end)
            self.parent_editor.reload_toolbar_shortcut(hotkey)
        
        self.accept()


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
    
    def mousePressEvent(self, event):
        """鼠标按下事件 - 传递给主窗口处理拖动"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 检查是否在按钮区域
            if (self.minimize_btn.geometry().contains(event.pos()) or
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
            if not (self.minimize_btn.geometry().contains(event.pos()) or
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
                color: {theme['text']};
                border: none;
                border-radius: 0;
                font-size: 20px;
                font-weight: 600;
                padding: 0px;
                min-width: 40px;
                min-height: 30px;
            }}
            QPushButton#titleBarButton:hover {{
                background-color: {theme['bg_tertiary']};
            }}
            QPushButton#titleBarButton:pressed {{
                background-color: {theme['bg_tertiary']};
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
        self.settings = QSettings("Markdo", "Settings")
        
        # 添加对话框动画支持
        self.opacity_animation = QPropertyAnimation(self, b'windowOpacity')
        self.opacity_animation.setDuration(300)  # 300ms 动画时间
        self.opacity_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        # 设置为模态对话框，确保显示在最前面
        self.setModal(True)
        # 设置窗口标志，确保显示在最前面
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowStaysOnTopHint)
        self.init_ui()
    
    def get_theme(self):
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
            "🔄 实时预览 - 边写边看，左右分屏",
            "🎨 语法高亮 - 清晰展示 Markdown 结构",
            "✨ 悬浮工具栏 - 快速插入各种格式",
            "📷 智能插入 - 图片、表格、链接向导",
            "🌙 主题切换 - 支持黑夜/白天模式",
            "📑 多标签页 - 同时编辑多个文件",
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
            ("Ctrl+B", "加粗"),
            ("Ctrl+I", "斜体"),
            ("Ctrl+D", "删除线"),
            ("Ctrl+H", "高亮"),
            ("Ctrl+`", "行内代码"),
            ("Ctrl+K", "插入链接"),
            ("Ctrl+Shift+K", "插入代码块"),
            ("Ctrl+Q", "插入引用"),
            ("Ctrl+L", "无序列表"),
            ("Ctrl+Shift+L", "有序列表"),
            ("Ctrl+;", "显示/隐藏工具栏"),
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
        
        # 提示
        tip = QLabel("💡 提示：输入 * 后按 Tab 可自动补全为 **，再按可扩展为 ****")
        tip.setStyleSheet(f"font-size: 12px; color: {theme['text_secondary']}; padding: 5px;")
        tip.setWordWrap(True)
        layout.addWidget(tip)
        
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
            return  # 不继续默认行为（不插入缩进）
        
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
        
        # 添加动画支持
        self.opacity_animation = QPropertyAnimation(self, b'windowOpacity')
        self.opacity_animation.setDuration(200)  # 200ms 动画时间
        self.opacity_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        self.move_animation = QPropertyAnimation(self, b'pos')
        self.move_animation.setDuration(200)  # 200ms 动画时间
        self.move_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        self.init_ui()
    
    def get_theme(self):
        """获取当前主题"""
        if self.parent_editor and hasattr(self.parent_editor, 'current_theme'):
            return self.parent_editor.current_theme
        return Theme.DARK
        
    def init_ui(self):
        """初始化UI - 菜单栏样式"""
        theme = self.get_theme()
        is_dark = theme['name'] == 'dark'
        
        if is_dark:
            bg_color = theme['bg']  # 使用主题背景色
            text_color = theme['text']
            menu_bg = theme['bg_secondary']  # 使用主题次级背景色
            menu_hover = theme['bg_tertiary']  # 使用主题三级背景色
        else:
            bg_color = theme['bg']  # 使用主题背景色
            text_color = theme['text']
            menu_bg = theme['bg_secondary']  # 使用主题次级背景色
            menu_hover = theme['bg_tertiary']  # 使用主题三级背景色
        
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
        is_dark = theme['name'] == 'dark'
        
        if is_dark:
            bg_color = theme['bg']  # 使用主题背景色
            text_color = theme['text']
            menu_bg = theme['bg_secondary']  # 使用主题次级背景色
            menu_hover = theme['bg_tertiary']  # 使用主题三级背景色
        else:
            bg_color = theme['bg']  # 使用主题背景色
            text_color = theme['text']
            menu_bg = theme['bg_secondary']  # 使用主题次级背景色
            menu_hover = theme['bg_tertiary']  # 使用主题三级背景色
        
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
        except:
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
        self.setFixedHeight(2)  # 设置固定高度为2像素
        self.current_theme = None
        
        # 创建定时器更新进度
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(60000)  # 每分钟更新一次
        
        # 初始更新
        self.update_progress()
    
    def set_theme(self, theme):
        """设置主题"""
        self.current_theme = theme
        self.update()
    
    def update_progress(self):
        """更新进度"""
        self.update()  # 触发重绘
    
    def paintEvent(self, event):
        """绘制进度条"""
        if not self.current_theme:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 获取当前时间
        now = datetime.now()
        total_seconds_in_day = 24 * 60 * 60  # 一天的总秒数
        current_seconds = (now.hour * 3600) + (now.minute * 60) + now.second  # 当前秒数
        progress = current_seconds / total_seconds_in_day  # 计算进度比例
        
        # 绘制背景
        painter.fillRect(self.rect(), QColor(self.current_theme['bg_tertiary']))
        
        # 计算进度条宽度
        progress_width = int(self.width() * progress)
        
        # 绘制进度
        if progress_width > 0:
            progress_rect = QRect(0, 0, progress_width, self.height())
            painter.fillRect(progress_rect, QColor(self.current_theme['accent']))


class MarkdownEditor(QMainWindow):
    """Markdo 主窗口"""

    def __init__(self):
        super().__init__()
        self.tabs = {}  # 存储所有标签页
        self.current_tab_id = 0
        self.floating_toolbar = None  # 悬浮工具栏
        self.toolbar_shortcut = None  # 悬浮工具栏快捷键
            
        # 添加动画支持
        self.window_opacity_animation = QPropertyAnimation(self, b'windowOpacity')
        self.window_opacity_animation.setDuration(300)  # 300ms 动画时间
        self.window_opacity_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
            
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
        self.resize_border_width = 5  # 边缘检测宽度（像素）
            
        # 加载设置
        self.settings = QSettings("Markdo", "Settings")
        self.current_theme_name = self.settings.value("theme", "dark", type=str)
        self.current_theme = Theme.get_theme(self.current_theme_name)
        self.toolbar_hotkey = self.settings.value("toolbar/hotkey", "Ctrl+;", type=str)
            
        # 自动切换主题设置
        self.auto_theme_switch = self.settings.value("theme/auto_switch", False, type=bool)
        self.night_start_time = self.settings.value("theme/night_start", "18:00", type=str)
        self.night_end_time = self.settings.value("theme/night_end", "06:00", type=str)
            
        # 创建主题切换定时器
        self.theme_check_timer = QTimer(self)
        self.theme_check_timer.timeout.connect(self.check_and_switch_theme)
        if self.auto_theme_switch:
            self.theme_check_timer.start(60000)  # 每分钟检查一次
            # 立即检查一次，确保启动时就能正确应用主题
            QTimer.singleShot(100, self.check_and_switch_theme)
            
        # 设置无边框窗口
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
            
        # 设置窗口初始透明度为0，准备淡入动画
        self.setWindowOpacity(0.0)
            
        self.init_ui()
            
        # 设置快捷键（在UI初始化之后）
        self.setup_shortcuts()
        self.setup_toolbar_shortcut()  # 设置工具栏快捷键
            
        # 应用主题（在标题栏创建之后）
        if self.auto_theme_switch:
            # 如果启用了自动切换，检查并应用正确的主题
            self.check_and_switch_theme()
        else:
            # 否则应用保存的主题
            self.apply_theme(self.current_theme_name)
            
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
        self.setGeometry(100, 100, 1200, 750)
        self.setMinimumSize(900, 650)
        
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
        
        # 将标签页添加到布局
        main_layout.addWidget(self.tab_widget)
        
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
        self.word_count_label.setStyleSheet(f"color: {self.current_theme['text_secondary']}; font-size: 12px; background-color: transparent;")
        self.status_bar.addWidget(self.word_count_label)
        
        self.show_status_message_temporarily("就绪", 2000)

        # 创建第一个标签页
        self.create_new_tab()
        
        # 初始化字数统计显示
        QTimer.singleShot(100, self.update_word_count_display)


    def apply_theme(self, theme_name):
        """应用主题"""
        self.current_theme_name = theme_name
        self.current_theme = Theme.get_theme(theme_name)
        base_stylesheet = Theme.get_app_stylesheet(self.current_theme)
        # 应用主题样式
        window_style = f"""
            QMainWindow {{
                background-color: {self.current_theme['bg']};
                border: none;
                border-radius: 12px;
            }}
            QWidget#centralWidget {{
                background-color: {self.current_theme['bg']};
                border-radius: 12px;
            }}
            QWidget#menuBarWidget {{
                background-color: {self.current_theme['bg_secondary']};
                border: none;
            }}
            QWidget#toolbarWidget {{
                background-color: {self.current_theme['toolbar_bg']};
                border: none;
            }}
            QWidget#toolbarWidget QPushButton {{
                font-weight: normal;
            }}
        """
        self.setStyleSheet(base_stylesheet + window_style)
        self.show_status_message_temporarily(f"主题已切换为: {'黑夜模式' if theme_name == 'dark' else '白天模式'}", 2000)

        # 更新标题栏主题
        if hasattr(self, 'title_bar'):
            self.title_bar.update_theme(self.current_theme)
        
        # 更新悬浮工具栏主题
        if self.floating_toolbar:
            self.floating_toolbar.update_theme()
        
        # 更新时间进度条主题
        if hasattr(self, 'time_progress_bar'):
            self.time_progress_bar.set_theme(self.current_theme)
        
        # 仅刷新当前标签页的预览窗口，避免性能问题
        tab_id = self.get_current_tab_id()
        if tab_id is not None:
            self.update_preview(tab_id)
    

    def resizeEvent(self, event):
        """窗口大小改变事件"""
        super().resizeEvent(event)
    
    def moveEvent(self, event):
        """窗口移动事件 - 更新悬浮工具栏位置"""
        super().moveEvent(event)
        # 如果悬浮工具栏可见，更新其位置
        if self.floating_toolbar and self.floating_toolbar.isVisible():
            self.floating_toolbar.update_position()

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
        # 注意：Ctrl+N、Ctrl+O、Ctrl+S 已在菜单栏中注册，此处不再重复注册
        
        # Ctrl+Shift+S - 另存为
        save_as_shortcut = QShortcut(QKeySequence("Ctrl+Shift+S"), self)
        save_as_shortcut.setContext(shortcut_context)
        save_as_shortcut.activated.connect(self.save_file_as)
        
        # ===== 编辑操作快捷键 =====
        # 注意：Ctrl+Z、Ctrl+Y 已在菜单栏中注册，此处不再重复注册
        
        redo_alt_shortcut = QShortcut(QKeySequence("Ctrl+Shift+Z"), self)
        redo_alt_shortcut.setContext(shortcut_context)
        redo_alt_shortcut.activated.connect(self.redo)
        
        # 注意：Ctrl+A 已在菜单栏中注册，此处不再重复注册
        
        # Ctrl+Shift+C - 复制全文
        copy_all_shortcut = QShortcut(QKeySequence("Ctrl+Shift+C"), self)
        copy_all_shortcut.setContext(shortcut_context)
        copy_all_shortcut.activated.connect(self.copy_all_content)
        
        # Ctrl+F - 查找 (预留接口)
        find_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        find_shortcut.setContext(shortcut_context)
        find_shortcut.activated.connect(self.show_find_dialog)
        
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
        
        # Ctrl+Q - 引用
        quote_shortcut = QShortcut(QKeySequence("Ctrl+Q"), self)
        quote_shortcut.setContext(shortcut_context)
        quote_shortcut.activated.connect(lambda: self.insert_markdown("> "))
        
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
        
        # ===== 工具栏快捷键 =====
        # Ctrl+; - 显示/隐藏 Markdown工具栏 (默认)
        toolbar_shortcut = QShortcut(QKeySequence("Ctrl+;"), self)
        toolbar_shortcut.setContext(shortcut_context)
        toolbar_shortcut.activated.connect(self.show_floating_toolbar)
        
        # Ctrl+M - 显示/隐藏 Markdown工具栏 (备选)
        toolbar_alt_shortcut = QShortcut(QKeySequence("Ctrl+M"), self)
        toolbar_alt_shortcut.setContext(shortcut_context)
        toolbar_alt_shortcut.activated.connect(self.show_floating_toolbar)
        
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
        # F1 - 显示快捷键帮助
        help_shortcut = QShortcut(QKeySequence("F1"), self)
        help_shortcut.setContext(shortcut_context)
        help_shortcut.activated.connect(self.show_shortcuts_help)
        
        # 存储所有快捷键以便管理
        self.shortcuts = {
            'save_as': save_as_shortcut,
            'redo_alt': redo_alt_shortcut,
            'copy_all': copy_all_shortcut,
            'find': find_shortcut,
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
            'toolbar': toolbar_shortcut,
            'toolbar_alt': toolbar_alt_shortcut,
            'time': time_shortcut,
            'hr': hr_shortcut,
            'help': help_shortcut,
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
            self.toolbar_shortcut.activated.connect(lambda: self.show_floating_toolbar())
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
        quit_action.setShortcut(QKeySequence.StandardKey.Quit)
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
                
        # 悬浮Markdown工具栏按钮
        float_toolbar_btn = QPushButton("✨ Markdown工具")
        float_toolbar_btn.clicked.connect(lambda: self.show_floating_toolbar())
        toolbar_layout.addWidget(float_toolbar_btn)
        
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
        
    def create_new_tab(self, content="", file_path=None):
        """创建新标签页"""
        tab_id = self.current_tab_id
        self.current_tab_id += 1
        
        # 创建分割器（左右布局）
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧：编辑器
        editor = MarkdownTextEdit()  # 使用自定义编辑器支持列表自动接续
        editor.setFont(QFont("Consolas", 11))
        editor.setPlaceholderText("在此输入Markdown内容...")
        
        # 应用语法高亮（保存引用以防止被垃圾回收）
        editor.highlighter = MarkdownHighlighter(editor.document())
        
        editor.setText(content)
        editor.textChanged.connect(lambda: self.on_text_changed(tab_id))
        editor.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        editor.customContextMenuRequested.connect(lambda pos: self.show_context_menu(tab_id, pos))
        # 光标位置变化时更新悬浮工具栏位置
        editor.cursorPositionChanged.connect(self.on_cursor_position_changed)
        
        # 编辑器焦点事件 - 用于自动显示/隐藏悬浮工具栏
        editor.installEventFilter(self)
        
        # 右侧：预览
        preview = QWebEngineView()
        # 启用JavaScript和远程内容加载
        settings = preview.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, True)
        preview.setHtml(self.get_initial_html(), QUrl("https://localhost/"))
        
        # 添加到分割器
        splitter.addWidget(editor)
        splitter.addWidget(preview)
        splitter.setSizes([600, 600])  # 默认各占一半
        
        # 添加标签页
        tab_name = f"新建 {tab_id + 1}" if not file_path else Path(file_path).name
        index = self.tab_widget.addTab(splitter, tab_name)
        self.tab_widget.setCurrentIndex(index)
        
        # 存储标签页信息
        self.tabs[tab_id] = {
            'editor': editor,
            'preview': preview,
            'file_path': file_path,
            'splitter': splitter
        }
        
        # 连接编辑器内容改变信号，更新字数统计
        editor.textChanged.connect(lambda: self.update_word_count_display())
        
        # 初始渲染
        self.update_preview(tab_id)
        
        return tab_id
    
    def get_current_tab_id(self):
        """获取当前标签页ID"""
        current_index = self.tab_widget.currentIndex()
        for tab_id, info in self.tabs.items():
            if self.tab_widget.indexOf(info['splitter']) == current_index:
                return tab_id
        return None
    
    def on_tab_changed(self):
        """标签页切换时更新字数统计"""
        self.update_word_count_display()
    
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
        self._update_timer.start(500)  # 500ms延迟，减少渲染频率
    
    def _do_update_preview(self):
        """实际执行预览更新"""
        if self._pending_tab_id is not None:
            self.update_preview(self._pending_tab_id)
    
    def on_cursor_position_changed(self):
        """光标位置变化时更新悬浮工具栏位置"""
        if self.floating_toolbar and self.floating_toolbar.isVisible():
            self.floating_toolbar.update_position()
    
    def update_preview(self, tab_id):
        """更新预览"""
        if tab_id not in self.tabs:
            return
        
        editor = self.tabs[tab_id]['editor']
        preview = self.tabs[tab_id]['preview']
        content = editor.toPlainText()
        
        html = self.markdown_to_html(content)
        preview.setHtml(html, QUrl("https://localhost/"))
    
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
                'pymdownx.arithmatex'   # 支持LaTeX数学表达式
            ], extension_configs={
                'pymdownx.tilde': {
                    'subscript': False  # 禁用~下标~，避免与公式冲突
                },
                'pymdownx.caret': {
                    'superscript': False,  # 禁用^上标^，避免与公式冲突
                    'insert': True
                },
                'pymdownx.arithmatex': {  # 支持LaTeX数学表达式
                    'generic': True
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
            
            return self.wrap_html_with_style(html_body)
        except Exception as e:
            # Markdown解析出错时返回纯文本
            import traceback
            traceback.print_exc()
            return self.wrap_html_with_style(f"<pre>{content}</pre>")
    
    def wrap_html_with_style(self, html_body):
        """为HTML添加完整样式"""
        # 根据当前主题设置预览窗口样式
        is_dark = self.current_theme_name == 'dark'
        
        if is_dark:
            # 黑夜模式：黑色背景，白色文字
            bg_color = '#1a1a1a'  # 与编辑器背景一致
            text_color = '#d0d0d0'  # 白色文字
            heading_color = '#e0e0e0'
            code_bg = 'rgba(45, 45, 45, 0.5)'
            code_color = '#ff79c6'
            pre_bg = '#252525'
            pre_text = '#d0d0d0'
            blockquote_bg = '#252525'
            blockquote_border = '#3a3a3a'
            blockquote_text = '#a0a0a0'
            table_border = '#3a3a3a'
            table_header_bg = '#252525'
            table_stripe_bg = '#202020'
            link_color = '#8ab4f8'
            h6_color = '#a0a0a0'
            del_color = '#888'
            h_border_color = '#3a3a3a'
            hr_bg = '#3a3a3a'
        else:
            # 白天模式：白色背景，深色文字
            bg_color = '#fff'
            text_color = '#333'
            heading_color = '#24292e'
            code_bg = 'rgba(27, 31, 35, 0.05)'
            code_color = '#e83e8c'
            pre_bg = '#f6f8fa'
            pre_text = '#24292e'
            blockquote_bg = '#f8f9fa'
            blockquote_border = '#dfe2e5'
            blockquote_text = '#6a737d'
            table_border = '#dfe2e5'
            table_header_bg = '#f6f8fa'
            table_stripe_bg = '#f6f8fa'
            link_color = '#0366d6'
            h6_color = '#6a737d'
            del_color = '#6a737d'
            h_border_color = '#eaecef'
            hr_bg = '#e1e4e8'
        
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
    mjx-container {{ display: inline-block; }}
    mjx-container[display="true"] {{ display: block; text-align: center; margin: 1em 0; }}
</style>
<script>
window.MathJax = {{
    tex: {{
        inlineMath: [['$', '$'], ['\\(', '\\)']],
        displayMath: [['$$', '$$']],
        processEscapes: true
    }}
}};
</script>
<script id="MathJax-script" src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
</head>
<body>
{html_body}
</body>
</html>'''
    
    def get_initial_html(self):
        """获取初始HTML"""
        # 根据当前主题设置预览窗口样式
        is_dark = self.current_theme_name == 'dark'
        
        if is_dark:
            bg_color = '#1a1a1a'
            text_color = '#999'
        else:
            bg_color = '#fff'
            text_color = '#999'
        
        return f'''<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
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
        """打开文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "打开Markdown文件",
            "",
            "Markdown文件 (*.md *.markdown);;所有文件 (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.create_new_tab(content, file_path)
                self.show_status_message_temporarily(f"已打开: {file_path}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "错误", f"打开文件失败: {str(e)}")
    
    def save_file(self):
        """保存文件"""
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
            try:
                content = self.tabs[tab_id]['editor'].toPlainText()
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.tabs[tab_id]['file_path'] = file_path
                
                # 更新标签名
                index = self.tab_widget.indexOf(self.tabs[tab_id]['splitter'])
                self.tab_widget.setTabText(index, Path(file_path).name)
                
                self.show_status_message_temporarily(f"已保存: {file_path}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存文件失败: {str(e)}")
    
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
    
    def show_floating_toolbar(self):
        """切换悬浮工具栏显示/隐藏"""
        if self.floating_toolbar is None:
            self.floating_toolbar = FloatingMarkdownToolbar(self)
        
        # 切换显示/隐藏
        if self.floating_toolbar.isVisible():
            self.floating_toolbar.hide_animated()
        else:
            # 在光标位置显示
            self.floating_toolbar.show_at_cursor()
    
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
        
        # Markdown工具
        markdown_action = menu.addAction("✨ Markdown工具")
        markdown_action.triggered.connect(self.show_floating_toolbar)
        
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
        """显示查找对话框"""
        if not hasattr(self, 'find_dialog') or self.find_dialog is None:
            self.find_dialog = FindDialog(self)
        self.find_dialog.show()
        self.find_dialog.raise_()
        self.find_dialog.activateWindow()
    
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
  Ctrl+Q - 插入引用
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
        theme = self.current_theme if hasattr(self, 'current_theme') else Theme.DARK
        
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
    
    def open_settings(self):
        """打开设置窗口"""
        dialog = SettingsDialog(self)
        dialog.exec()
    
    def show_about(self):
        """显示关于对话框"""
        about_text = """
        <div style="text-align: center;">
            <h2>📝 Markdo</h2>
            <p style="color: #666;">PyQt6版本</p>
            <hr>
            <p><b>作者:</b> A8Z0RB</p>
            <p><b>QQ:</b> 486780065</p>
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
            ("Ctrl+Shift+C", "复制全文"),
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
    
    

class FindDialog(QDialog):
    """查找对话框"""
    
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
def _update_theme_settings(self, theme_name, auto_switch, night_start, night_end):
    """更新主题设置"""
    self.auto_theme_switch = auto_switch
    self.night_start_time = night_start
    self.night_end_time = night_end
    
    if auto_switch:
        # 启用自动切换，启动定时器并立即检查
        self.theme_check_timer.start(60000)  # 每分钟检查一次
        self.check_and_switch_theme()  # 立即检查一次
    else:
        # 禁用自动切换，停止定时器并应用手动选择的主题
        self.theme_check_timer.stop()
        self.apply_theme(theme_name)


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
        
    # 根据时间段切换主题
    target_theme = "dark" if is_night_time else "light"
    if target_theme != self.current_theme_name:
        self.apply_theme(target_theme)
        self.settings.setValue("theme", target_theme)


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
    except:
        pass


def _show_welcome(self):
    """显示开屏教程/使用指南"""
    # 确保窗口已经显示并获得焦点
    if not self.isVisible():
        self.show()
    self.raise_()
    self.activateWindow()
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
    dialog.exec()


# 将方法添加到MarkdownEditor类
MarkdownEditor.update_theme_settings = _update_theme_settings
MarkdownEditor.check_and_switch_theme = _check_and_switch_theme
MarkdownEditor.eventFilter = _eventFilter
MarkdownEditor._start_window_fade_in = _start_window_fade_in
MarkdownEditor._on_window_fade_in_finished = _on_window_fade_in_finished
MarkdownEditor.show_welcome = _show_welcome


def main():
    app = QApplication(argv)
    
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
                print(f"无法打开文件: {file_path}, 错误: {str(e)}")
    
    exit(app.exec())


if __name__ == '__main__':
    main()
