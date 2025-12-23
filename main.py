"""
Markdo - PyQt6版本
完整重写，提供更好的HTML/CSS渲染支持
"""
import sys
import markdown
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QTabWidget, QToolBar, QPushButton, QFileDialog,
    QMessageBox, QSplitter, QLabel, QStatusBar, QMenuBar, QMenu,
    QDialog, QGridLayout, QGroupBox, QToolButton, QCheckBox, QComboBox,
    QStackedWidget
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPoint, QSettings, QUrl
from PyQt6.QtGui import QFont, QColor, QAction, QKeySequence, QTextCursor, QShortcut, QSyntaxHighlighter, QTextCharFormat, QPalette
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
        'accent': '#0078d4',
        'accent_hover': '#1e90ff',
        'border': '#3c3c3c',
        'editor_bg': '#1e1e1e',
        'editor_text': '#d4d4d4',
        'toolbar_bg': '#2d2d30',
        'status_bg': '#333337',  # 深灰色，比背景稍亮
        'status_text': '#cccccc',
    }
    
    LIGHT = {
        'name': 'light',
        'bg': '#ffffff',
        'bg_secondary': '#f8f9fa',
        'bg_tertiary': '#e9ecef',
        'text': '#333333',
        'text_secondary': '#6c757d',
        'accent': '#007bff',
        'accent_hover': '#0056b3',
        'border': '#dee2e6',
        'editor_bg': '#ffffff',
        'editor_text': '#333333',
        'toolbar_bg': '#f8f9fa',
        'status_bg': '#e9ecef',  # 浅灰色，比背景稍暗
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
                color: white;
            }}
            QMenu {{
                background-color: {theme['bg_secondary']};
                color: {theme['text']};
                border: 1px solid {theme['border']};
            }}
            QMenu::item:selected {{
                background-color: {theme['accent']};
                color: white;
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
                color: white;
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
            }}
            QPushButton {{
                background-color: {theme['accent']};
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {theme['accent_hover']};
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
        
        # 提示信息
        hint_label = QLabel("提示：关闭后可使用 Tab 或 Ctrl+M 手动打开")
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
    
    def save_settings(self):
        """保存设置"""
        auto_show = self.auto_show_checkbox.isChecked()
        self.settings.setValue("toolbar/auto_show", auto_show)
        
        theme_name = self.theme_combo.currentData()
        self.settings.setValue("theme", theme_name)
        
        # 通知父窗口更新设置
        if self.parent_editor:
            self.parent_editor.update_toolbar_settings(auto_show)
            self.parent_editor.apply_theme(theme_name)
        
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
    """自定义Markdown编辑器 - 支持列表自动接续和Tab唤出悬浮窗"""
    
    # 定义信号：Tab键触发
    tab_pressed = pyqtSignal()
    
    def keyPressEvent(self, event):
        """处理键盘事件"""
        # Tab键触发悬浮窗，不插入缩进
        if event.key() == Qt.Key.Key_Tab:
            self.tab_pressed.emit()
            return  # 不继续默认行为（不插入缩进）
        
        # 回车键处理列表自动接续
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            if self.handle_list_continuation():
                return  # 已处理，不继续默认行为
        
        # 调用父类默认处理
        super().keyPressEvent(event)
    
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


class FloatingMarkdownToolbar(QDialog):
    """紧凑型悬浮Markdown工具栏 - 跟随光标且不遗挡文本"""
    
    def __init__(self, parent=None):
        super().__init__(parent, 
                         Qt.WindowType.Tool | 
                         Qt.WindowType.FramelessWindowHint |
                         Qt.WindowType.WindowDoesNotAcceptFocus)  # 不获取焦点，不置顶
        self.parent_editor = parent
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)  # 显示时不激活
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)  # 启用透明背景
        self.init_ui()
    
    def get_theme(self):
        """获取当前主题"""
        if self.parent_editor and hasattr(self.parent_editor, 'current_theme'):
            return self.parent_editor.current_theme
        return Theme.DARK  # 默认暗色主题
        
    def init_ui(self):
        """初始化UI - 分页标签布局"""
        theme = self.get_theme()
        is_dark = theme['name'] == 'dark'
        
        if is_dark:
            bg_color = "rgba(45, 45, 48, 0.95)"
            btn_bg = "rgba(60, 60, 64, 0.9)"
            btn_hover = "rgba(0, 120, 212, 0.9)"
            btn_pressed = "rgba(0, 90, 180, 0.9)"
            text_color = "#d4d4d4"
            border_color = "rgba(0, 120, 212, 0.8)"
            btn_border = "rgba(80, 80, 84, 0.8)"
            tab_bg = "rgba(50, 50, 54, 0.9)"
            tab_active = "rgba(0, 120, 212, 0.9)"
        else:
            bg_color = "rgba(255, 255, 255, 0.95)"
            btn_bg = "rgba(248, 249, 250, 0.9)"
            btn_hover = "rgba(0, 123, 255, 0.9)"
            btn_pressed = "rgba(0, 86, 179, 0.9)"
            text_color = "#333"
            border_color = "rgba(0, 123, 255, 0.8)"
            btn_border = "rgba(222, 226, 230, 0.8)"
            tab_bg = "rgba(240, 240, 240, 0.9)"
            tab_active = "rgba(0, 123, 255, 0.9)"
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 6px;
            }}
            QPushButton {{
                background-color: {btn_bg};
                color: {text_color};
                border: 1px solid {btn_border};
                padding: 3px 6px;
                border-radius: 3px;
                font-size: 11px;
                min-width: 28px;
                max-width: 50px;
            }}
            QPushButton:hover {{
                background-color: {btn_hover};
                color: white;
                border-color: {theme['accent']};
            }}
            QPushButton:pressed {{
                background-color: {btn_pressed};
            }}
            QPushButton#tabBtn {{
                min-width: 50px;
                max-width: 60px;
                padding: 4px 8px;
                border-radius: 4px 4px 0 0;
                border-bottom: none;
            }}
            QPushButton#tabBtn:checked {{
                background-color: {tab_active};
                color: white;
            }}
            QLabel {{
                color: {theme['text_secondary']};
            }}
        """)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(2)
        
        # 标签页按钮行
        tab_row = QHBoxLayout()
        tab_row.setSpacing(2)
        
        self.tab_buttons = []
        tab_names = ["基础", "列表", "插入", "LaTeX"]
        for i, name in enumerate(tab_names):
            btn = QPushButton(name)
            btn.setObjectName("tabBtn")
            btn.setCheckable(True)
            btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            btn.clicked.connect(lambda c, idx=i: self.switch_tab(idx))
            if i == 0:
                btn.setChecked(True)
            tab_row.addWidget(btn)
            self.tab_buttons.append(btn)
        
        # 关闭按钮
        close_btn = QPushButton("✕")
        close_btn.setStyleSheet("background-color: #dc3545; color: white; border: none; max-width: 20px;")
        close_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        close_btn.setToolTip("关闭工具栏")
        close_btn.clicked.connect(self.hide)
        tab_row.addWidget(close_btn)
        main_layout.addLayout(tab_row)
        
        # 内容区域堆叠布局
        self.content_stack = QStackedWidget()
        
        # 创建四个分页
        self.content_stack.addWidget(self._create_basic_page())
        self.content_stack.addWidget(self._create_list_page())
        self.content_stack.addWidget(self._create_insert_page())
        self.content_stack.addWidget(self._create_latex_page())
        
        main_layout.addWidget(self.content_stack)
        self.setLayout(main_layout)
        self.adjustSize()
    
    def switch_tab(self, index):
        """切换标签页"""
        self.content_stack.setCurrentIndex(index)
        for i, btn in enumerate(self.tab_buttons):
            btn.setChecked(i == index)
    
    def _create_basic_page(self):
        """创建基础页 - 标题和格式"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 4, 0, 0)
        layout.setSpacing(2)
        
        # 标题行
        row1 = QHBoxLayout()
        row1.setSpacing(2)
        for i in range(1, 7):
            btn = self._create_btn(f"H{i}", lambda c, l=i: self.insert_header(l), f"标题{i}")
            row1.addWidget(btn)
        layout.addLayout(row1)
        
        # 格式行
        row2 = QHBoxLayout()
        row2.setSpacing(2)
        format_btns = [
            ("B", "**", "**", "粗体"), 
            ("I", "*", "*", "斜体"), 
            ("BI", "***", "***", "粗斜体"),
            ("S", "~~", "~~", "删除线"),
            ("H", "==", "==", "高亮"), 
            ("`", "`", "`", "行内代码")
        ]
        for text, p, s, tip in format_btns:
            btn = self._create_btn(text, lambda c, pr=p, su=s: self.insert_format(pr, su), tip)
            if text == "B":
                btn.setStyleSheet(btn.styleSheet() + "font-weight: bold;")
            elif text == "I":
                btn.setStyleSheet(btn.styleSheet() + "font-style: italic;")
            elif text == "S":
                btn.setStyleSheet(btn.styleSheet() + "text-decoration: line-through;")
            row2.addWidget(btn)
        layout.addLayout(row2)
        
        return page
    
    def _create_list_page(self):
        """创建列表页 - 列表和引用"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 4, 0, 0)
        layout.setSpacing(2)
        
        # 列表行
        row1 = QHBoxLayout()
        row1.setSpacing(2)
        list_btns = [
            ("•", "- ", "无序列表"), 
            ("1.", "1. ", "有序列表"), 
            ("☐", "- [ ] ", "任务列表"), 
            ("☑", "- [x] ", "已完成")
        ]
        for text, marker, tip in list_btns:
            btn = self._create_btn(text, lambda c, m=marker: self.insert_list_marker(m), tip)
            row1.addWidget(btn)
        layout.addLayout(row1)
        
        # 引用行
        row2 = QHBoxLayout()
        row2.setSpacing(2)
        quote_btns = [
            (">", "> ", "引用"),
            (">>", ">> ", "二级引用"),
            (">>>", ">>> ", "三级引用")
        ]
        for text, marker, tip in quote_btns:
            btn = self._create_btn(text, lambda c, m=marker: self.insert_list_marker(m), tip)
            row2.addWidget(btn)
        layout.addLayout(row2)
        
        return page
    
    def _create_insert_page(self):
        """创建插入页 - 链接、图片、表格等"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 4, 0, 0)
        layout.setSpacing(2)
        
        # 第一行
        row1 = QHBoxLayout()
        row1.setSpacing(2)
        insert_btns1 = [
            ("🔗", self.insert_link, "插入链接"), 
            ("🖼", self.insert_image, "插入图片"), 
            ("☰", self.insert_table, "插入表格"), 
            ("</>", self.insert_code_block, "代码块")
        ]
        for text, func, tip in insert_btns1:
            btn = self._create_btn(text, lambda c, f=func: f(), tip)
            row1.addWidget(btn)
        layout.addLayout(row1)
        
        # 第二行
        row2 = QHBoxLayout()
        row2.setSpacing(2)
        insert_btns2 = [
            ("─", self.insert_separator, "分割线"),
            ("⏰", self.insert_timestamp, "时间戳"),
            ("📌", self.insert_footnote, "脚注"),
            ("📑", self.insert_toc, "目录")
        ]
        for text, func, tip in insert_btns2:
            btn = self._create_btn(text, lambda c, f=func: f(), tip)
            row2.addWidget(btn)
        layout.addLayout(row2)
        
        return page
    
    def _create_latex_page(self):
        """创建LaTeX页 - 数学公式"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 4, 0, 0)
        layout.setSpacing(2)
        
        # 行内公式
        row1 = QHBoxLayout()
        row1.setSpacing(2)
        inline_btns = [
            ("$x$", "$", "$", "行内公式 $...$"),
            ("\\(...\\)", "\\(", "\\)", "行内公式 \\(...\\)")
        ]
        for text, p, s, tip in inline_btns:
            btn = self._create_btn(text, lambda c, pr=p, su=s: self.insert_format(pr, su), tip)
            row1.addWidget(btn)
        layout.addLayout(row1)
        
        # 公式块
        row2 = QHBoxLayout()
        row2.setSpacing(2)
        block_btns = [
            ("$$", self.insert_math_block, "公式块 $$...$$"),
            ("\\[\\]", self.insert_math_block_bracket, "公式块 \\[...\\]")
        ]
        for text, func, tip in block_btns:
            btn = self._create_btn(text, lambda c, f=func: f(), tip)
            row2.addWidget(btn)
        layout.addLayout(row2)
        
        # 常用公式模板
        row3 = QHBoxLayout()
        row3.setSpacing(2)
        template_btns = [
            ("∑", "\\sum_{i=1}^{n}", "求和"),
            ("∫", "\\int_{a}^{b}", "积分"),
            ("√", "\\sqrt{}", "平方根"),
            ("x²", "^{2}", "上标"),
            ("x₂", "_{}", "下标")
        ]
        for text, template, tip in template_btns:
            btn = self._create_btn(text, lambda c, t=template: self.insert_latex_template(t), tip)
            row3.addWidget(btn)
        layout.addLayout(row3)
        
        # 更多公式模板
        row4 = QHBoxLayout()
        row4.setSpacing(2)
        more_btns = [
            ("÷", "\\frac{}{}", "分数"),
            ("∞", "\\infty", "无穷大"),
            ("≠", "\\neq", "不等于"),
            ("≤", "\\leq", "小于等于"),
            ("≥", "\\geq", "大于等于")
        ]
        for text, template, tip in more_btns:
            btn = self._create_btn(text, lambda c, t=template: self.insert_latex_template(t), tip)
            row4.addWidget(btn)
        layout.addLayout(row4)
        
        # 希腊字母
        row5 = QHBoxLayout()
        row5.setSpacing(2)
        greek_btns = [
            ("α", "\\alpha", "alpha"),
            ("β", "\\beta", "beta"),
            ("γ", "\\gamma", "gamma"),
            ("δ", "\\delta", "delta"),
            ("π", "\\pi", "pi"),
            ("σ", "\\sigma", "sigma")
        ]
        for text, template, tip in greek_btns:
            btn = self._create_btn(text, lambda c, t=template: self.insert_latex_template(t), tip)
            row5.addWidget(btn)
        layout.addLayout(row5)
        
        return page
    
    def insert_latex_template(self, template):
        """插入LaTeX模板"""
        editor = self.get_editor()
        if not editor:
            return
        
        cursor = editor.textCursor()
        cursor.insertText(template)
        editor.setTextCursor(cursor)
        editor.setFocus()
    
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
        """插入链接"""
        editor = self.get_editor()
        if not editor:
            return
        
        cursor = editor.textCursor()
        if cursor.hasSelection():
            selected = cursor.selectedText()
            cursor.insertText(f"[{selected}](链接地址)")
        else:
            cursor.insertText("[链接文本](链接地址)")
        editor.setFocus()
    
    def insert_image(self):
        """插入图片"""
        editor = self.get_editor()
        if not editor:
            return
        
        cursor = editor.textCursor()
        cursor.insertText("![图片描述](图片地址)")
        editor.setFocus()
    
    def insert_table(self):
        """插入表格"""
        editor = self.get_editor()
        if not editor:
            return
        
        cursor = editor.textCursor()
        table = "\n| 列1 | 列2 | 列3 |\n| --- | --- | --- |\n| 内容1 | 内容2 | 内容3 |\n"
        cursor.insertText(table)
        editor.setFocus()
    
    def insert_code_block(self):
        """插入代码块"""
        editor = self.get_editor()
        if not editor:
            return
        
        cursor = editor.textCursor()
        cursor.insertText("```\n\n```\n")
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
        
        # 加载设置
        self.settings = QSettings("Markdo", "Settings")
        self.auto_show_toolbar = self.settings.value("toolbar/auto_show", False, type=bool)
        self.current_theme_name = self.settings.value("theme", "dark", type=str)
        self.current_theme = Theme.get_theme(self.current_theme_name)
        
        self.init_ui()
        self.apply_theme(self.current_theme_name)
        
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("📝 Markdo")
        self.setGeometry(100, 100, 1200, 750)
        self.setMinimumSize(900, 650)
        
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
        
        # Ctrl+M - 显示/隐藏Markdown工具栏
        toolbar_shortcut = QShortcut(QKeySequence("Ctrl+M"), self)
        toolbar_shortcut.activated.connect(lambda: self.show_floating_toolbar())
        
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")
        
        new_action = QAction("新建(&N)", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(lambda: self.create_new_tab())
        file_menu.addAction(new_action)
        
        open_action = QAction("打开(&O)", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(lambda: self.open_file())
        file_menu.addAction(open_action)
        
        save_action = QAction("保存(&S)", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(lambda: self.save_file())
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        settings_action = QAction("设置(&T)", self)
        settings_action.triggered.connect(self.open_settings)
        file_menu.addAction(settings_action)
        
        file_menu.addSeparator()
        
        quit_action = QAction("退出(&Q)", self)
        quit_action.setShortcut(QKeySequence.StandardKey.Quit)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)
        
        # 编辑菜单
        edit_menu = menubar.addMenu("编辑(&E)")
        
        undo_action = QAction("撤销(&U)", self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.triggered.connect(self.undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("重做(&R)", self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.triggered.connect(self.redo)
        edit_menu.addAction(redo_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")
        
        shortcuts_action = QAction("快捷键(&K)", self)
        shortcuts_action.triggered.connect(self.show_shortcuts)
        help_menu.addAction(shortcuts_action)
        
        help_menu.addSeparator()
        
        about_action = QAction("关于(&A)", self)
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
        
        # Tab键触发悬浮工具栏
        editor.tab_pressed.connect(self.show_floating_toolbar)
        
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
            ("Tab", "显示/隐藏Markdown工具栏"),
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
                color: white;
                border: none;
                padding: 10px 40px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {theme['accent_hover']};
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


def main():
    app = QApplication(sys.argv)
    
    # 设置应用样式
    app.setStyle('Fusion')
    
    window = MarkdownEditor()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
