"""
Markdo - PyQt6
提供更好的HTML/CSS渲染支持
"""
import sys
import markdown
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QTabWidget, QToolBar, QPushButton, QFileDialog,
    QMessageBox, QSplitter, QLabel, QStatusBar, QMenuBar, QMenu,
    QDialog, QGridLayout, QGroupBox, QToolButton, QCheckBox, QComboBox,
    QLineEdit, QSpinBox, QRadioButton, QButtonGroup
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPoint, QSettings, QUrl, QObject
from PyQt6.QtGui import QFont, QColor, QAction, QKeySequence, QTextCursor, QShortcut, QSyntaxHighlighter, QTextCharFormat, QPalette, QIcon
import re
from datetime import datetime


# ==================== 主题系统 ====================
class Theme:
    """主题配置"""
    DARK = {
        'name': 'dark',
        'bg': '#1e1e1e',
        'bg_secondary': '#252526',
        'bg_tertiary': '#2d2d30',
        'text': '#d4d4d4',
        'text_secondary': '#9d9d9d',
        'accent': '#ffffff',  # 白色强调色
        'accent_hover': '#e0e0e0',
        'accent_text': '#1e1e1e',  # 强调色背景上的文字色（黑色）
        'border': '#3c3c3c',
        'editor_bg': '#1e1e1e',
        'editor_text': '#d4d4d4',
        'toolbar_bg': '#2d2d30',
        'status_bg': '#333337',
        'status_text': '#cccccc',
    }
    
    LIGHT = {
        'name': 'light',
        'bg': '#ffffff',
        'bg_secondary': '#f8f9fa',
        'bg_tertiary': '#e9ecef',
        'text': '#333333',
        'text_secondary': '#6c757d',
        'accent': '#333333',  # 黑色强调色
        'accent_hover': '#555555',
        'accent_text': '#ffffff',  # 强调色背景上的文字色（白色）
        'border': '#dee2e6',
        'editor_bg': '#ffffff',
        'editor_text': '#333333',
        'toolbar_bg': '#f8f9fa',
        'status_bg': '#e9ecef',
        'status_text': '#495057',
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
            }}
            QMenuBar {{
                background-color: {theme['bg_secondary']};
                color: {theme['text']};
                border-bottom: 1px solid {theme['border']};
            }}
            QMenuBar::item:selected {{
                background-color: {theme['accent']};
                color: {theme['accent_text']};
            }}
            QMenu {{
                background-color: {theme['bg_secondary']};
                color: {theme['text']};
                border: 1px solid {theme['border']};
            }}
            QMenu::item:selected {{
                background-color: {theme['accent']};
                color: {theme['accent_text']};
            }}
            QToolBar {{
                background-color: {theme['toolbar_bg']};
                border: none;
                spacing: 5px;
                padding: 5px;
            }}
            QToolBar QPushButton {{
                background-color: {theme['bg_tertiary']};
                color: {theme['text']};
                border: 1px solid {theme['border']};
                padding: 5px 12px;
                border-radius: 4px;
            }}
            QToolBar QPushButton:hover {{
                background-color: {theme['accent']};
                color: {theme['accent_text']};
                border-color: {theme['accent']};
            }}
            QTabWidget::pane {{
                border: 1px solid {theme['border']};
                background-color: {theme['bg']};
            }}
            QTabBar::tab {{
                background-color: {theme['bg_secondary']};
                color: {theme['text']};
                padding: 8px 16px;
                border: 1px solid {theme['border']};
                border-bottom: none;
            }}
            QTabBar::tab:selected {{
                background-color: {theme['bg']};
                border-bottom: 2px solid {theme['accent']};
            }}
            QTabBar::tab:hover {{
                background-color: {theme['bg_tertiary']};
            }}
            QTextEdit {{
                background-color: {theme['editor_bg']};
                color: {theme['editor_text']};
                border: none;
                selection-background-color: {theme['accent']};
                selection-color: {theme['accent_text']};
            }}
            QStatusBar {{
                background-color: {theme['status_bg']};
                color: {theme['status_text']};
            }}
            QSplitter::handle {{
                background-color: {theme['border']};
            }}
            QScrollBar:vertical {{
                background-color: {theme['bg_secondary']};
                width: 12px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {theme['border']};
                border-radius: 6px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {theme['text_secondary']};
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
        self.setFixedSize(420, 380)
        
        # 获取当前主题
        theme_name = self.settings.value("theme", "dark", type=str)
        theme = Theme.get_theme(theme_name)
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {theme['bg_secondary']};
            }}
            QGroupBox {{
                font-weight: bold;
                border: 1px solid {theme['border']};
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 10px;
                background-color: {theme['bg']};
                color: {theme['text']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: {theme['accent']};
            }}
            QCheckBox {{
                spacing: 8px;
                color: {theme['text']};
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
            }}
            QLabel {{
                color: {theme['text']};
            }}
            QComboBox {{
                background-color: {theme['bg']};
                color: {theme['text']};
                border: 1px solid {theme['border']};
                padding: 5px 10px;
                border-radius: 4px;
            }}
            QComboBox:hover {{
                border-color: {theme['accent']};
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox QAbstractItemView {{
                background-color: {theme['bg']};
                color: {theme['text']};
                selection-background-color: {theme['accent']};
                selection-color: {theme['accent_text']};
            }}
            QPushButton {{
                background-color: {theme['accent']};
                color: {theme['accent_text']};
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {theme['accent_hover']};
                color: {theme['accent_text']};
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 外观设置组
        appearance_group = QGroupBox("外观")
        appearance_layout = QHBoxLayout()
        
        theme_label = QLabel("主题：")
        self.theme_combo = QComboBox()
        self.theme_combo.addItem("🌙 黑夜模式", "dark")
        self.theme_combo.addItem("☀️ 白天模式", "light")
        self.theme_combo.setMinimumWidth(150)
        
        appearance_layout.addWidget(theme_label)
        appearance_layout.addWidget(self.theme_combo)
        appearance_layout.addStretch()
        appearance_group.setLayout(appearance_layout)
        layout.addWidget(appearance_group)
        
        # 悬浮工具栏设置组
        toolbar_group = QGroupBox("悬浮工具栏")
        toolbar_layout = QVBoxLayout()
        
        # 自动显示/隐藏开关
        self.auto_show_checkbox = QCheckBox("光标在编辑区时自动显示悬浮工具栏")
        self.auto_show_checkbox.setToolTip("开启后，当光标进入编辑区时自动显示工具栏\n离开编辑区时自动隐藏")
        toolbar_layout.addWidget(self.auto_show_checkbox)
        
        # 快捷键自定义
        hotkey_layout = QHBoxLayout()
        hotkey_label = QLabel("显示/隐藏快捷键：")
        self.hotkey_input = QLineEdit()
        self.hotkey_input.setPlaceholderText("按下想要设置的快捷键")
        self.hotkey_input.setReadOnly(True)
        self.hotkey_input.setMinimumWidth(150)
        reset_btn = QPushButton("重置为Ctrl+Space")
        reset_btn.setMaximumWidth(120)
        reset_btn.clicked.connect(self.reset_hotkey)
        hotkey_layout.addWidget(hotkey_label)
        hotkey_layout.addWidget(self.hotkey_input)
        hotkey_layout.addWidget(reset_btn)
        hotkey_layout.addStretch()
        toolbar_layout.addLayout(hotkey_layout)
        
        # 提示信息
        hint_label = QLabel("提示：默认快捷键 Ctrl+Space，Ctrl+M 也可使用")
        hint_label.setStyleSheet(f"color: {theme['text_secondary']}; font-size: 11px;")
        toolbar_layout.addWidget(hint_label)
        
        toolbar_group.setLayout(toolbar_layout)
        layout.addWidget(toolbar_group)
        
        # 弹性空间
        layout.addStretch()
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.save_settings)
        btn_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.setStyleSheet(f"background-color: {theme['text_secondary']};")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def load_settings(self):
        """加载设置"""
        auto_show = self.settings.value("toolbar/auto_show", False, type=bool)
        self.auto_show_checkbox.setChecked(auto_show)
        
        theme_name = self.settings.value("theme", "dark", type=str)
        index = self.theme_combo.findData(theme_name)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
        
        # 加载快捷键设置
        hotkey = self.settings.value("toolbar/hotkey", "Ctrl+Space", type=str)
        self.hotkey_input.setText(hotkey)
    
    def reset_hotkey(self):
        """重置Ctrl+Space快捷键"""
        self.hotkey_input.setText("Ctrl+Space")
        self.settings.setValue("toolbar/hotkey", "Ctrl+Space")
    
    def save_settings(self):
        """保存设置"""
        auto_show = self.auto_show_checkbox.isChecked()
        self.settings.setValue("toolbar/auto_show", auto_show)
        
        theme_name = self.theme_combo.currentData()
        self.settings.setValue("theme", theme_name)
        
        # 保存快捷键设置
        hotkey = self.hotkey_input.text() or "Ctrl+Space"
        self.settings.setValue("toolbar/hotkey", hotkey)
        
        # 通知父窗口更新设置
        if self.parent_editor:
            self.parent_editor.update_toolbar_settings(auto_show)
            self.parent_editor.apply_theme(theme_name)
            self.parent_editor.reload_toolbar_shortcut(hotkey)
        
        self.accept()


class WelcomeDialog(QDialog):
    """开屏教程窗口"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_editor = parent
        self.settings = QSettings("Markdo", "Settings")
        self.init_ui()
    
    def get_theme(self):
        theme_name = self.settings.value("theme", "dark", type=str)
        return Theme.get_theme(theme_name)
    
    def init_ui(self):
        self.setWindowTitle("👋 欢迎使用 Markdo")
        self.setFixedSize(520, 580)
        theme = self.get_theme()
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {theme['bg_secondary']};
            }}
            QLabel {{
                color: {theme['text']};
            }}
            QCheckBox {{
                color: {theme['text_secondary']};
                spacing: 8px;
            }}
            QPushButton {{
                background-color: {theme['accent']};
                color: {theme['accent_text']};
                border: none;
                padding: 12px 40px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {theme['accent_hover']};
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(15)
        
        # 标题
        title = QLabel("📝 Markdo - 现代 Markdown 编辑器")
        title.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {theme['accent']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # 副标题
        subtitle = QLabel("简洁、高效、实时预览")
        subtitle.setStyleSheet(f"font-size: 13px; color: {theme['text_secondary']};")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        
        layout.addSpacing(10)
        
        # 特色介绍
        features_group = QGroupBox("✨ 核心特色")
        features_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 1px solid {theme['border']};
                border-radius: 8px;
                margin-top: 12px;
                padding: 15px;
                background-color: {theme['bg']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                color: {theme['accent']};
            }}
        """)
        features_layout = QVBoxLayout()
        features_layout.setSpacing(8)
        
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
            label.setStyleSheet(f"font-size: 13px; padding: 3px 0; color: {theme['text']};")
            features_layout.addWidget(label)
        
        features_group.setLayout(features_layout)
        layout.addWidget(features_group)
        
        # 快捷键介绍
        shortcuts_group = QGroupBox("⌨️ 常用快捷键")
        shortcuts_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 1px solid {theme['border']};
                border-radius: 8px;
                margin-top: 12px;
                padding: 15px;
                background-color: {theme['bg']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                color: {theme['accent']};
            }}
        """)
        shortcuts_layout = QGridLayout()
        shortcuts_layout.setVerticalSpacing(6)
        shortcuts_layout.setHorizontalSpacing(20)
        
        shortcuts = [
            ("Ctrl+Space", "唤出 Markdown 工具栏"),
            ("Ctrl+B", "加粗"),
            ("Ctrl+I", "斜体"),
            ("Tab", "符号自动补全"),
            ("Ctrl+S", "保存文件"),
            ("Ctrl+N", "新建标签页"),
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
        
        self.setLayout(layout)
    
    def on_start(self):
        """点击开始使用"""
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
        self.highlighting_rules.append((re.compile(r'^#{1,6}\s.*'), header_format))
        
        # 粗体 (**text**) - 深棕色
        bold_format = QTextCharFormat()
        bold_format.setForeground(QColor("#7a5230"))
        bold_format.setFontWeight(QFont.Weight.Bold)
        self.highlighting_rules.append((re.compile(r'\*\*.+?\*\*'), bold_format))
        
        # 斜体 (*text*) - 深紫色
        italic_format = QTextCharFormat()
        italic_format.setForeground(QColor("#6b5b7a"))
        italic_format.setFontItalic(True)
        self.highlighting_rules.append((re.compile(r'\*.+?\*'), italic_format))
        
        # 行内代码 (`code`) - 深绿色
        code_format = QTextCharFormat()
        code_format.setForeground(QColor("#4a7a5a"))
        self.highlighting_rules.append((re.compile(r'`.+?`'), code_format))
        
        # 代码块标记 (```) - 深灰绿色
        codeblock_format = QTextCharFormat()
        codeblock_format.setForeground(QColor("#5a7a6a"))
        self.highlighting_rules.append((re.compile(r'^```.*'), codeblock_format))
        
        # 链接 [text](url) - 深青色
        link_format = QTextCharFormat()
        link_format.setForeground(QColor("#3a6a7a"))
        self.highlighting_rules.append((re.compile(r'\[.+?\]\(.+?\)'), link_format))
        
        # 列表标记 (- * +) - 深橙色
        list_format = QTextCharFormat()
        list_format.setForeground(QColor("#8a6a4a"))
        list_format.setFontWeight(QFont.Weight.Bold)
        self.highlighting_rules.append((re.compile(r'^\s*[-*+]\s'), list_format))
        self.highlighting_rules.append((re.compile(r'^\s*\d+\.\s'), list_format))
        
        # 引用 (>) - 深灰色
        quote_format = QTextCharFormat()
        quote_format.setForeground(QColor("#6a6a6a"))
        self.highlighting_rules.append((re.compile(r'^>+.*'), quote_format))
        
        # 删除线 (~~text~~) - 灰色
        strikethrough_format = QTextCharFormat()
        strikethrough_format.setForeground(QColor("#7a7a7a"))
        self.highlighting_rules.append((re.compile(r'~~.+?~~'), strikethrough_format))
        
        # 高亮 (==text==) - 深黄色
        highlight_format = QTextCharFormat()
        highlight_format.setForeground(QColor("#7a6a3a"))
        self.highlighting_rules.append((re.compile(r'==.+?=='), highlight_format))
        
        # 分割线 (--- 或 ***) - 灰色
        hr_format = QTextCharFormat()
        hr_format.setForeground(QColor("#999999"))
        self.highlighting_rules.append((re.compile(r'^[-*]{3,}$'), hr_format))
        
        # 数学公式 $...$ - 深蓝色
        math_format = QTextCharFormat()
        math_format.setForeground(QColor("#5a6a8a"))
        self.highlighting_rules.append((re.compile(r'\$[^$]+\$'), math_format))
        self.highlighting_rules.append((re.compile(r'\\\([^)]+\\\)'), math_format))
        
        # 公式块标记 $$ - 深蓝色
        mathblock_format = QTextCharFormat()
        mathblock_format.setForeground(QColor("#4a5a7a"))
        mathblock_format.setFontWeight(QFont.Weight.Bold)
        self.highlighting_rules.append((re.compile(r'^\$\$'), mathblock_format))
        self.highlighting_rules.append((re.compile(r'^\\\[$'), mathblock_format))  # \[
        self.highlighting_rules.append((re.compile(r'^\\\]$'), mathblock_format))  # \]
        
        # 脚注 [^1] - 深青色
        footnote_format = QTextCharFormat()
        footnote_format.setForeground(QColor("#4a7a7a"))
        self.highlighting_rules.append((re.compile(r'\[\^\w+\]'), footnote_format))
        
        # 目录标记 [TOC] - 深橙色
        toc_format = QTextCharFormat()
        toc_format.setForeground(QColor("#8a5a4a"))
        toc_format.setFontWeight(QFont.Weight.Bold)
        self.highlighting_rules.append((re.compile(r'^\[TOC\]$', re.IGNORECASE), toc_format))
        
        # 上标 ^text^ - 深紫色
        superscript_format = QTextCharFormat()
        superscript_format.setForeground(QColor("#7a5a8a"))
        self.highlighting_rules.append((re.compile(r'\^[^^]+\^'), superscript_format))
        
        # 下标 ~text~ - 深青色
        subscript_format = QTextCharFormat()
        subscript_format.setForeground(QColor("#5a7a8a"))
        self.highlighting_rules.append((re.compile(r'~[^~]+~'), subscript_format))
        
        # 表格分隔符 | - 深灰色
        table_format = QTextCharFormat()
        table_format.setForeground(QColor("#6a6a6a"))
        self.highlighting_rules.append((re.compile(r'^\|.*\|$'), table_format))
        self.highlighting_rules.append((re.compile(r'^\|[-:| ]+\|$'), table_format))
        
        # 粗斜体 ***text*** - 深棕色加粗斜体
        bolditalic_format = QTextCharFormat()
        bolditalic_format.setForeground(QColor("#6a4a30"))
        bolditalic_format.setFontWeight(QFont.Weight.Bold)
        bolditalic_format.setFontItalic(True)
        self.highlighting_rules.append((re.compile(r'\*\*\*.+?\*\*\*'), bolditalic_format))
    
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
        ordered_match = re.match(r'^(\s*)(\d+)\.\s(.*)$', line_text)
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
        unordered_match = re.match(r'^(\s*)([-*+])\s(.*)$', line_text)
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
        task_match = re.match(r'^(\s*)([-*+])\s\[([ x])\]\s(.*)$', line_text)
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
        quote_match = re.match(r'^(\s*)(>+)\s(.*)$', line_text)
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
            }}
            QLabel {{
                color: {theme['text']};
                font-size: 13px;
            }}
            QLineEdit {{
                background-color: {theme['bg']};
                color: {theme['text']};
                border: 1px solid {theme['border']};
                padding: 8px;
                border-radius: 4px;
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border-color: {theme['accent']};
            }}
            QRadioButton {{
                color: {theme['text']};
                spacing: 8px;
            }}
            QPushButton {{
                background-color: {theme['accent']};
                color: {theme['accent_text']};
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {theme['accent_hover']};
            }}
            QPushButton#browseBtn {{
                background-color: {theme['bg_tertiary']};
                color: {theme['text']};
                border: 1px solid {theme['border']};
            }}
            QPushButton#browseBtn:hover {{
                background-color: {theme['accent']};
                color: {theme['accent_text']};
            }}
            QPushButton#cancelBtn {{
                background-color: {theme['bg_tertiary']};
                color: {theme['text']};
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
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
            }}
            QLabel {{
                color: {theme['text']};
                font-size: 13px;
            }}
            QSpinBox {{
                background-color: {theme['bg']};
                color: {theme['text']};
                border: 1px solid {theme['border']};
                padding: 6px 10px;
                border-radius: 4px;
                min-width: 80px;
            }}
            QSpinBox:focus {{
                border-color: {theme['accent']};
            }}
            QCheckBox {{
                color: {theme['text']};
                spacing: 8px;
            }}
            QPushButton {{
                background-color: {theme['accent']};
                color: {theme['accent_text']};
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {theme['accent_hover']};
            }}
            QPushButton#cancelBtn {{
                background-color: {theme['bg_tertiary']};
                color: {theme['text']};
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 20)
        layout.setSpacing(18)
        
        # 行数
        row_layout = QHBoxLayout()
        row_label = QLabel("行数：")
        row_label.setMinimumWidth(60)
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
        col_label.setMinimumWidth(60)
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
            }}
            QLabel {{
                color: {theme['text']};
                font-size: 13px;
            }}
            QLineEdit {{
                background-color: {theme['bg']};
                color: {theme['text']};
                border: 1px solid {theme['border']};
                padding: 8px;
                border-radius: 4px;
            }}
            QLineEdit:focus {{
                border-color: {theme['accent']};
            }}
            QPushButton {{
                background-color: {theme['accent']};
                color: {theme['accent_text']};
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {theme['accent_hover']};
            }}
            QPushButton#cancelBtn {{
                background-color: {theme['bg_tertiary']};
                color: {theme['text']};
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 链接文本
        text_layout = QHBoxLayout()
        text_label = QLabel("链接文本：")
        text_label.setMinimumWidth(70)
        self.text_input = QLineEdit()
        self.text_input.setText(self.selected_text)
        self.text_input.setPlaceholderText("显示的文本")
        text_layout.addWidget(text_label)
        text_layout.addWidget(self.text_input, 1)
        layout.addLayout(text_layout)
        
        # 链接URL
        url_layout = QHBoxLayout()
        url_label = QLabel("链接地址：")
        url_label.setMinimumWidth(70)
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
        self.setFixedSize(350, 180)
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
            }}
            QLabel {{
                color: {theme['text']};
                font-size: 13px;
            }}
            QComboBox {{
                background-color: {theme['bg']};
                color: {theme['text']};
                border: 1px solid {theme['border']};
                padding: 8px;
                border-radius: 4px;
                min-width: 180px;
            }}
            QComboBox:focus {{
                border-color: {theme['accent']};
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox QAbstractItemView {{
                background-color: {theme['bg']};
                color: {theme['text']};
                selection-background-color: {theme['accent']};
                selection-color: {theme['accent_text']};
            }}
            QPushButton {{
                background-color: {theme['accent']};
                color: {theme['accent_text']};
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {theme['accent_hover']};
            }}
            QPushButton#cancelBtn {{
                background-color: {theme['bg_tertiary']};
                color: {theme['text']};
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 20)
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
    """悬浮Markdown工具栏 - 折叠菜单样式 + 鼠标控制"""
    
    def __init__(self, parent=None):
        super().__init__(parent, 
                         Qt.WindowType.Tool | 
                         Qt.WindowType.FramelessWindowHint |
                         Qt.WindowType.WindowDoesNotAcceptFocus)  # 不接受焦点
        self.parent_editor = parent
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)  # 显示时不激活
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)  # 透明背景
        self.init_ui()
    
    def get_theme(self):
        """获取当前主题"""
        if self.parent_editor and hasattr(self.parent_editor, 'current_theme'):
            return self.parent_editor.current_theme
        return Theme.DARK
        
    def init_ui(self):
        """初始化UI - 折叠菜单布局"""
        theme = self.get_theme()
        is_dark = theme['name'] == 'dark'
        
        if is_dark:
            bg_color = "rgba(40, 40, 44, 0.60)"  # 40%透明度
            btn_bg = "rgba(55, 55, 60, 0.85)"
            btn_hover = "rgba(255, 255, 255, 0.95)"  # 白色
            text_color = "#e0e0e0"
            border_color = "rgba(80, 80, 90, 0.7)"
            menu_bg = "rgba(45, 45, 50, 0.95)"
            menu_hover = "rgba(255, 255, 255, 0.9)"  # 白色
            menu_border = "rgba(70, 70, 80, 0.8)"
            hover_text = "#1e1e1e"  # 悬停时文字变黑
        else:
            bg_color = "rgba(255, 255, 255, 0.60)"  # 40%透明度
            btn_bg = "rgba(245, 245, 248, 0.9)"
            btn_hover = "rgba(51, 51, 51, 0.9)"  # 黑色
            text_color = "#333"
            border_color = "rgba(200, 200, 210, 0.8)"
            menu_bg = "rgba(255, 255, 255, 0.98)"
            menu_hover = "rgba(51, 51, 51, 0.85)"  # 黑色
            menu_border = "rgba(220, 220, 230, 0.9)"
            hover_text = "#ffffff"  # 悬停时文字变白
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 8px;
            }}
            QToolButton {{
                background-color: {btn_bg};
                color: {text_color};
                border: 1px solid {border_color};
                padding: 6px 12px;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 500;
            }}
            QToolButton:hover {{
                background-color: {btn_hover};
                color: {hover_text};
                border-color: {theme['accent']};
            }}
            QToolButton:pressed {{
                background-color: {btn_hover};
                color: {hover_text};
                border-color: {theme['accent']};
            }}
            QToolButton[popupMode="1"]:pressed {{
                background-color: {btn_hover};
                color: {hover_text};
            }}
            QToolButton::menu-indicator {{
                image: none;
                width: 0px;
            }}
            QMenu {{
                background-color: {menu_bg};
                border: 1px solid {menu_border};
                border-radius: 6px;
                padding: 4px;
            }}
            QMenu::item {{
                background-color: transparent;
                color: {text_color};
                padding: 6px 20px 6px 10px;
                border-radius: 4px;
                margin: 2px 4px;
            }}
            QMenu::item:selected {{
                background-color: {menu_hover};
                color: {hover_text};
            }}
            QMenu::separator {{
                height: 1px;
                background-color: {border_color};
                margin: 4px 8px;
            }}
            QPushButton#closeBtn {{
                background-color: rgba(220, 53, 69, 0.9);
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
            }}
            QPushButton#closeBtn:hover {{
                background-color: rgba(200, 35, 51, 1.0);
            }}
        """)
        
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(6, 6, 6, 6)
        main_layout.setSpacing(4)
        
        # === 基础格式菜单 ===
        basic_btn = self._create_menu_button("📝 基础", "标题和文本格式")
        basic_menu = self._create_menu()
        
        # 标题子菜单
        header_menu = basic_menu.addMenu("🅽 标题")
        for i in range(1, 7):
            action = header_menu.addAction(f"H{i} - {'#'*i} 标题{i}")
            action.triggered.connect(lambda c, l=i: self.insert_header(l))
        
        basic_menu.addSeparator()
        
        # 格式按钮
        format_items = [
            ("🅱️ 粗体", "**", "**", "Ctrl+B"),
            ("🅸️ 斜体", "*", "*", "Ctrl+I"),
            ("S̶ 删除线", "~~", "~~", "Ctrl+D"),
            ("🟡 高亮", "==", "==", "Ctrl+H"),
            ("💻 行内代码", "`", "`", "Ctrl+`")
        ]
        for text, prefix, suffix, shortcut in format_items:
            action = basic_menu.addAction(f"{text}  {shortcut}")
            action.triggered.connect(lambda c, p=prefix, s=suffix: self.insert_format(p, s))
        
        basic_btn.setMenu(basic_menu)
        main_layout.addWidget(basic_btn)
        
        # === 列表引用菜单 ===
        list_btn = self._create_menu_button("📝 列表", "列表和引用")
        list_menu = self._create_menu()
        
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
        
        list_btn.setMenu(list_menu)
        main_layout.addWidget(list_btn)
        
        # === 插入元素菜单 ===
        insert_btn = self._create_menu_button("➕ 插入", "插入各种元素")
        insert_menu = self._create_menu()
        
        insert_items = [
            ("🔗 链接", self.insert_link),
            ("🖼️ 图片", self.insert_image),
            ("📊 表格", self.insert_table),
            ("💻 代码块", self.insert_code_block),
            ("── 分割线", self.insert_hr),
            ("⏰ 时间戳", self.insert_timestamp),
            ("📌 脚注", self.insert_footnote),
            ("📑 目录", self.insert_toc)
        ]
        for text, func in insert_items:
            action = insert_menu.addAction(text)
            action.triggered.connect(func)
        
        insert_btn.setMenu(insert_menu)
        main_layout.addWidget(insert_btn)
        
        # === LaTeX公式菜单 ===
        latex_btn = self._create_menu_button("∑ LaTeX", "数学公式")
        latex_menu = self._create_menu()
        
        # 公式类型
        latex_menu.addAction("$ 行内公式").triggered.connect(lambda: self.insert_format("$", "$"))
        latex_menu.addAction("$$ 公式块").triggered.connect(self.insert_math_block)
        latex_menu.addAction("\\[...\\] 公式块").triggered.connect(self.insert_math_block_bracket)
        
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
        
        latex_btn.setMenu(latex_menu)
        main_layout.addWidget(latex_btn)
        
        # 弹性空间
        main_layout.addStretch()
        
        # 关闭按钮
        close_btn = QPushButton("✕")
        close_btn.setObjectName("closeBtn")
        close_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        close_btn.setToolTip("关闭工具栏")
        close_btn.clicked.connect(self.hide)
        main_layout.addWidget(close_btn)
        
        self.setLayout(main_layout)
        self.adjustSize()
    
    def _create_menu_button(self, text, tooltip):
        """创建菜单按钮"""
        btn = QToolButton()
        btn.setText(text)
        btn.setToolTip(tooltip)
        btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)  # 不获取焦点
        return btn
    
    def _create_menu(self):
        """创建菜单"""
        from PyQt6.QtWidgets import QMenu
        menu = QMenu(self)
        menu.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        return menu
    
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
        """在光标位置显示，避开文本"""
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
        
        self.move(x, y)
        self.show()
        self.raise_()
    
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
        cleaned = re.sub(r'^#+\s*', '', line_text)
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
        cleaned = re.sub(r'^([-*+]\s+|\d+\.\s+|[-*+]\s+\[[x ]\]\s+|>\s+)', '', line_text)
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
    
    def insert_math_block_bracket(self):
        """插入数学公式块 \\[...\\]"""
        editor = self.get_editor()
        if not editor:
            return
        
        cursor = editor.textCursor()
        cursor.insertText("\n\\[\n\n\\]\n")
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
    
    def insert_toc(self):
        """插入目录"""
        editor = self.get_editor()
        if not editor:
            return
        
        cursor = editor.textCursor()
        cursor.insertText("[TOC]\n\n")
        editor.setTextCursor(cursor)
        editor.setFocus()


class MarkdownEditor(QMainWindow):
    """Markdo 主窗口"""
    
    def __init__(self):
        super().__init__()
        self.tabs = {}  # 存储所有标签页
        self.current_tab_id = 0
        self.floating_toolbar = None  # 悬浮工具栏
        self.toolbar_shortcut = None  # 悬浮工具栏快捷键
        
        # 加载设置
        self.settings = QSettings("Markdo", "Settings")
        self.auto_show_toolbar = self.settings.value("toolbar/auto_show", False, type=bool)
        self.current_theme_name = self.settings.value("theme", "dark", type=str)
        self.current_theme = Theme.get_theme(self.current_theme_name)
        self.toolbar_hotkey = self.settings.value("toolbar/hotkey", "Ctrl+Space", type=str)
        
        self.init_ui()
        self.apply_theme(self.current_theme_name)
        self.setup_toolbar_shortcut()  # 设置悬浮工具栏快捷键
        
        # 显示开屏教程（首次启动或未禁用）
        if self.settings.value("show_welcome", True, type=bool):
            QTimer.singleShot(100, self.show_welcome)
        
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("📝 Markdo")
        self.setGeometry(100, 100, 1200, 750)
        self.setMinimumSize(900, 650)
        
        # 设置窗口图标
        import os
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Markdo.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建工具栏
        self.create_toolbar()
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        main_layout.addWidget(self.tab_widget)
        
        # 创建状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")
        
        # 创建第一个标签页
        self.create_new_tab()
        
        # 添加快捷键
        self.setup_shortcuts()
    
    def apply_theme(self, theme_name):
        """应用主题"""
        self.current_theme_name = theme_name
        self.current_theme = Theme.get_theme(theme_name)
        self.setStyleSheet(Theme.get_app_stylesheet(self.current_theme))
        self.status_bar.showMessage(f"主题已切换为: {'黑夜模式' if theme_name == 'dark' else '白天模式'}", 2000)
        
    def setup_shortcuts(self):
        """设置常用快捷键"""
        # Ctrl+B - 加粗
        bold_shortcut = QShortcut(QKeySequence("Ctrl+B"), self)
        bold_shortcut.activated.connect(lambda: self.insert_markdown_wrapper("**", "**"))
        
        # Ctrl+I - 斜体
        italic_shortcut = QShortcut(QKeySequence("Ctrl+I"), self)
        italic_shortcut.activated.connect(lambda: self.insert_markdown_wrapper("*", "*"))
        
        # Ctrl+K - 插入链接
        link_shortcut = QShortcut(QKeySequence("Ctrl+K"), self)
        link_shortcut.activated.connect(self.insert_link)
        
        # Ctrl+Shift+C - 复制全文
        copy_all_shortcut = QShortcut(QKeySequence("Ctrl+Shift+C"), self)
        copy_all_shortcut.activated.connect(lambda: self.copy_all_content())
        
        # Ctrl+` - 行内代码
        code_shortcut = QShortcut(QKeySequence("Ctrl+`"), self)
        code_shortcut.activated.connect(lambda: self.insert_markdown_wrapper("`", "`"))
        
        # Ctrl+Shift+K - 代码块
        codeblock_shortcut = QShortcut(QKeySequence("Ctrl+Shift+K"), self)
        codeblock_shortcut.activated.connect(self.insert_code_block)
        
        # Ctrl+Q - 引用
        quote_shortcut = QShortcut(QKeySequence("Ctrl+Q"), self)
        quote_shortcut.activated.connect(lambda: self.insert_markdown("> "))
        
        # Ctrl+L - 无序列表
        list_shortcut = QShortcut(QKeySequence("Ctrl+L"), self)
        list_shortcut.activated.connect(lambda: self.insert_markdown("- "))
        
        # Ctrl+Shift+L - 有序列表
        ordered_list_shortcut = QShortcut(QKeySequence("Ctrl+Shift+L"), self)
        ordered_list_shortcut.activated.connect(lambda: self.insert_markdown("1. "))
        
        # Ctrl+D - 删除线
        strikethrough_shortcut = QShortcut(QKeySequence("Ctrl+D"), self)
        strikethrough_shortcut.activated.connect(lambda: self.insert_markdown_wrapper("~~", "~~"))
        
        # Ctrl+H - 高亮
        highlight_shortcut = QShortcut(QKeySequence("Ctrl+H"), self)
        highlight_shortcut.activated.connect(lambda: self.insert_markdown_wrapper("==", "=="))
        
        # Ctrl+1~6 - 标题
        for i in range(1, 7):
            shortcut = QShortcut(QKeySequence(f"Ctrl+{i}"), self)
            shortcut.activated.connect(lambda level=i: self.insert_markdown("#" * level + " "))
        
        # Ctrl+M - 显示/隐藏 Markdown工具栏
        toolbar_shortcut = QShortcut(QKeySequence("Ctrl+M"), self)
        toolbar_shortcut.activated.connect(lambda: self.show_floating_toolbar())
            
    def setup_toolbar_shortcut(self):
        """设置悬浮工具栏快捷键"""
        # 删除旧的快捷键
        if self.toolbar_shortcut:
            self.toolbar_shortcut.deleteLater()
            
        # 根据设置添加新快捷键
        hotkey = self.toolbar_hotkey or "Ctrl+Space"
        self.toolbar_shortcut = QShortcut(QKeySequence(hotkey), self)
        self.toolbar_shortcut.activated.connect(lambda: self.show_floating_toolbar())
        
    def reload_toolbar_shortcut(self, hotkey):
        """重新加载悬浮工具栏快捷键"""
        self.toolbar_hotkey = hotkey
        self.setup_toolbar_shortcut()
        
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
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
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助")
        
        guide_action = QAction("使用指南", self)
        guide_action.triggered.connect(self.show_welcome)
        help_menu.addAction(guide_action)
        
        shortcuts_action = QAction("快捷键", self)
        shortcuts_action.triggered.connect(self.show_shortcuts)
        help_menu.addAction(shortcuts_action)
        
        help_menu.addSeparator()
        
        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def create_toolbar(self):
        """创建工具栏"""
        toolbar = QToolBar("主工具栏")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # 新建按钮
        new_btn = QPushButton("📄 新建")
        new_btn.clicked.connect(lambda: self.create_new_tab())
        toolbar.addWidget(new_btn)
        
        # 打开按钮
        open_btn = QPushButton("📂 打开")
        open_btn.clicked.connect(lambda: self.open_file())
        toolbar.addWidget(open_btn)
        
        # 保存按钮
        save_btn = QPushButton("💾 保存")
        save_btn.clicked.connect(lambda: self.save_file())
        toolbar.addWidget(save_btn)
        
        toolbar.addSeparator()
                
        # 悬浮Markdown工具栏按钮
        float_toolbar_btn = QPushButton("✨ Markdown工具")
        float_toolbar_btn.clicked.connect(lambda: self.show_floating_toolbar())
        toolbar.addWidget(float_toolbar_btn)
        
        toolbar.addSeparator()
        
        # 复制全文按钮
        copy_all_btn = QPushButton("📋 复制全文")
        copy_all_btn.clicked.connect(lambda: self.copy_all_content())
        toolbar.addWidget(copy_all_btn)
        
        # 清空按钮
        clear_btn = QPushButton("🗑️ 清空")
        clear_btn.clicked.connect(lambda: self.clear_current_tab())
        toolbar.addWidget(clear_btn)
        
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
            
            # 保护独立公式块 $$...$$ (支持多行)
            content = re.sub(r'\$\$[\s\S]+?\$\$', protect_math, content)
            # 保护 \[...\] 格式
            content = re.sub(r'\\\[[\s\S]+?\\\]', protect_math, content)
            # 保护 \(...\) 格式 (先处理，避免被 $...$ 匹配干扰)
            content = re.sub(r'\\\(.+?\\\)', protect_math, content)
            # 保护行内公式 $...$ (不跨行，至少有一个非空字符)
            content = re.sub(r'\$(?!\$)([^$\n]+?)\$(?!\$)', protect_math, content)
            
            # 使用pymdown扩展
            html_body = markdown.markdown(content, extensions=[
                'extra',
                'codehilite',
                'toc',
                'pymdownx.tilde',      # 支持~~删除线~~
                'pymdownx.caret',      # 支持^^插入^^
                'pymdownx.mark'        # 支持==高亮==
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
                    return math_placeholders[idx]
                return match.group(0)
            
            html_body = re.sub(r'<span class="math-placeholder" data-idx="(\d+)"></span>', restore_math, html_body)
            
            return self.wrap_html_with_style(html_body)
        except Exception as e:
            # Markdown解析出错时返回纯文本
            import traceback
            traceback.print_exc()
            return self.wrap_html_with_style(f"<pre>{content}</pre>")
    
    def wrap_html_with_style(self, html_body):
        """为HTML添加完整样式"""
        return f'''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
    body {{
        font-family: 微软雅黑, -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
        padding: 20px;
        line-height: 1.8;
        color: #333;
        max-width: 100%;
        margin: 0;
        background-color: #fff;
        overflow-x: hidden;
    }}
    p {{ margin: 0 0 16px 0; }}
    h1, h2, h3, h4, h5, h6 {{
        margin-top: 24px;
        margin-bottom: 16px;
        font-weight: 600;
        line-height: 1.25;
        color: #24292e;
    }}
    h1 {{ font-size: 2em; border-bottom: 2px solid #eaecef; padding-bottom: 0.3em; }}
    h2 {{ font-size: 1.5em; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }}
    h3 {{ font-size: 1.25em; }}
    h4 {{ font-size: 1em; }}
    h5 {{ font-size: 0.875em; }}
    h6 {{ font-size: 0.85em; color: #6a737d; }}
    strong, b {{ font-weight: 600; color: #24292e; }}
    em, i {{ font-style: italic; }}
    del {{ text-decoration: line-through; color: #6a737d; opacity: 0.8; }}
    mark {{ background-color: #fff3cd; color: #856404; padding: 2px 4px; border-radius: 3px; }}
    sub {{ vertical-align: sub; font-size: 0.75em; }}
    sup {{ vertical-align: super; font-size: 0.75em; }}
    code {{
        background-color: rgba(27, 31, 35, 0.05);
        padding: 0.2em 0.4em;
        border-radius: 3px;
        font-family: "Consolas", "Monaco", "Courier New", monospace;
        font-size: 0.9em;
        color: #e83e8c;
    }}
    pre {{
        background-color: #f6f8fa;
        border-radius: 6px;
        padding: 16px;
        overflow-x: auto;
        line-height: 1.45;
        white-space: pre-wrap;
        word-wrap: break-word;
    }}
    pre code {{ background-color: transparent; padding: 0; color: #24292e; }}
    blockquote {{
        border-left: 0.25em solid #dfe2e5;
        padding: 0.5em 1em;
        color: #6a737d;
        margin: 0 0 16px 0;
        background-color: #f8f9fa;
    }}
    blockquote blockquote {{ margin: 8px 0; border-left-color: #c0c0c0; }}
    blockquote p {{ margin: 0.5em 0; }}
    table {{ border-collapse: collapse; width: auto; max-width: 100%; margin: 16px 0; display: table; }}
    table th, table td {{ border: 1px solid #dfe2e5; padding: 8px 12px; text-align: left; vertical-align: top; }}
    table th {{ background-color: #f6f8fa; font-weight: 600; }}
    table tr:nth-child(2n) {{ background-color: #f6f8fa; }}
    table td strong, table td b {{ font-weight: 700; color: #24292e; }}
    table td em, table td i {{ font-style: italic; }}
    ul, ol {{ padding-left: 2em; margin: 0 0 16px 0; }}
    li {{ margin: 0.5em 0; }}
    li > p {{ margin: 0.5em 0; }}
    input[type="checkbox"] {{ margin-right: 0.5em; }}
    hr {{ height: 0.25em; padding: 0; margin: 24px 0; background-color: #e1e4e8; border: 0; }}
    a {{ color: #0366d6; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    img {{ max-width: 100%; box-sizing: border-box; }}
    mjx-container {{ display: inline-block; }}
    mjx-container[display="true"] {{ display: block; text-align: center; margin: 1em 0; }}
</style>
</head>
<body>
{html_body}
<script>
window.MathJax = {{
    tex: {{
        inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
        displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']],
        processEscapes: true
    }},
    options: {{
        skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code']
    }},
    startup: {{
        pageReady: function() {{
            return MathJax.startup.defaultPageReady();
        }}
    }}
}};
</script>
<script id="MathJax-script" src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
</body>
</html>'''
    
    def get_initial_html(self):
        """获取初始HTML"""
        return '''<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="text-align:center; color:#999; padding:50px;">
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
                self.status_bar.showMessage(f"已打开: {file_path}", 3000)
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
                
                self.status_bar.showMessage(f"已保存: {file_path}", 3000)
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
            self.floating_toolbar.hide()
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
            self.status_bar.showMessage("已清空内容", 2000)
    
    def copy_all_content(self):
        """复制当前编辑器的全部内容到剪贴板"""
        tab_id = self.get_current_tab_id()
        if tab_id is None:
            return
        
        content = self.tabs[tab_id]['editor'].toPlainText()
        if content:
            QApplication.clipboard().setText(content)
            self.status_bar.showMessage("已复制全文到剪贴板", 2000)
        else:
            self.status_bar.showMessage("当前内容为空", 2000)
    
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
                border: 1px solid {theme['border']};
                border-radius: 8px;
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
            ("Ctrl+Space", "显示/隐藏Markdown工具栏"),
            ("Ctrl+M", "显示/隐藏Markdown工具栏"),
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
        ]
        content_layout.addWidget(create_shortcut_group("插入内容", insert_shortcuts))
        
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
                background-color: {theme['accent']};
                color: {theme['accent_text']};
                border: none;
                padding: 10px 40px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {theme['accent_hover']};
                color: {theme['accent_text']};
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
    
    def update_toolbar_settings(self, auto_show):
        """更新悬浮工具栏设置"""
        self.auto_show_toolbar = auto_show
        
        # 如果关闭自动显示，隐藏当前的悬浮工具栏
        if not auto_show and self.floating_toolbar:
            self.floating_toolbar.hide()
        
        self.status_bar.showMessage(f"设置已保存: 自动显示工具栏 {'\u5df2开启' if auto_show else '\u5df2关闭'}", 2000)
    
    def eventFilter(self, obj, event):
        """事件过滤器 - 处理编辑器焦点事件"""
        from PyQt6.QtCore import QEvent
        
        # 检查是否是编辑器
        is_editor = False
        for tab_info in self.tabs.values():
            if obj == tab_info['editor']:
                is_editor = True
                break
        
        if is_editor and self.auto_show_toolbar:
            if event.type() == QEvent.Type.FocusIn:
                # 编辑器获得焦点，显示悬浮工具栏
                self.show_floating_toolbar()
            elif event.type() == QEvent.Type.FocusOut:
                # 编辑器失去焦点，隐藏悬浮工具栏
                # 延迟一下，避免点击工具栏按钮时意外关闭
                QTimer.singleShot(100, self._check_hide_toolbar)
        
        return super().eventFilter(obj, event)
    
    def _check_hide_toolbar(self):
        """检查是否需要隐藏工具栏"""
        if not self.auto_show_toolbar:
            return
        
        # 检查当前焦点是否在编辑器中
        current_editor = self.get_current_editor()
        if current_editor and current_editor.hasFocus():
            return  # 编辑器仍有焦点，不隐藏
        
        # 检查焦点是否在悬浮工具栏上
        if self.floating_toolbar and self.floating_toolbar.isVisible():
            # 如果焦点不在编辑器，也不在工具栏，则隐藏
            focused_widget = QApplication.focusWidget()
            if focused_widget is None or not self.floating_toolbar.isAncestorOf(focused_widget):
                self.floating_toolbar.hide()
    
    def show_welcome(self):
        """显示开屏教程/使用指南"""
        dialog = WelcomeDialog(self)
        dialog.exec()


def main():
    app = QApplication(sys.argv)
    
    # 设置应用样式
    app.setStyle('Fusion')
    
    # 设置应用图标
    import os
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Markdo.png')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    window = MarkdownEditor()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
