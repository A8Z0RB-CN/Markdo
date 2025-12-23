"""
PyQt6 独立预览窗口，用于在 tkinter 编辑器中显示 Markdown 预览
使用方法：
    preview_window = MarkdownPreviewWindow()
    preview_window.set_html(html_content)
    preview_window.show()
"""
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, Qt, QTimer
from PyQt6.QtGui import QColor

# 全局 QApplication 实例
_qt_app = None

def get_qt_app():
    """获取或创建 QApplication 实例"""
    global _qt_app
    if _qt_app is None:
        if not QApplication.instance():
            _qt_app = QApplication(sys.argv)
        else:
            _qt_app = QApplication.instance()
    return _qt_app


class MarkdownPreviewWindow(QMainWindow):
    """独立的 Markdown 预览窗口"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        """初始化 UI"""
        self.setWindowTitle("📝 Markdown 预览")
        self.setGeometry(100, 100, 900, 700)
        
        # 创建 WebEngineView
        self.web_view = QWebEngineView(self)
        self.setCentralWidget(self.web_view)
        
        # 设置背景颜色
        self.web_view.page().setBackgroundColor(QColor(255, 255, 255))
        
        # 设置初始内容
        self.set_html("<p style='text-align:center; color:#999; padding:50px;'><i>开始编辑以查看预览</i></p>")
        
    def set_html(self, html_content):
        """设置 HTML 内容"""
        # 添加完整的 HTML 文档结构和样式
        full_html = self._wrap_with_style(html_content)
        self.web_view.setHtml(full_html)
    
    def _wrap_with_style(self, html_content):
        """为 HTML 内容添加完整的文档结构和样式"""
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
    }}
    
    h1, h2, h3, h4, h5, h6 {{
        margin-top: 24px;
        margin-bottom: 16px;
        font-weight: 600;
        line-height: 1.25;
    }}
    
    h1 {{ font-size: 2em; border-bottom: 2px solid #eaecef; padding-bottom: 0.3em; }}
    h2 {{ font-size: 1.5em; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }}
    h3 {{ font-size: 1.25em; }}
    h4 {{ font-size: 1em; }}
    h5 {{ font-size: 0.875em; }}
    h6 {{ font-size: 0.85em; color: #6a737d; }}
    
    /* 删除线 */
    del {{
        text-decoration: line-through;
        color: #888;
    }}
    
    /* 高亮 */
    mark {{
        background-color: #fff3cd;
        padding: 2px 4px;
        border-radius: 3px;
    }}
    
    /* 下标 */
    sub {{
        vertical-align: sub;
        font-size: 0.8em;
    }}
    
    /* 上标 */
    sup {{
        vertical-align: super;
        font-size: 0.8em;
    }}
    
    /* 粗体和斜体 */
    strong {{ font-weight: 600; }}
    em {{ font-style: italic; }}
    
    /* 代码 */
    code {{
        background-color: rgba(27, 31, 35, 0.05);
        padding: 0.2em 0.4em;
        margin: 0;
        font-size: 85%;
        border-radius: 3px;
        font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
    }}
    
    /* 代码块 */
    pre {{
        background-color: #f6f8fa;
        border-radius: 6px;
        padding: 16px;
        overflow-x: auto;
        line-height: 1.45;
        margin: 16px 0;
    }}
    
    pre code {{
        background-color: transparent;
        padding: 0;
        margin: 0;
        font-size: 100%;
        border-radius: 0;
    }}
    
    /* 引用 */
    blockquote {{
        margin: 0;
        padding: 0 1em;
        color: #6a737d;
        border-left: 0.25em solid #dfe2e5;
    }}
    
    /* 链接 */
    a {{
        color: #0366d6;
        text-decoration: none;
    }}
    
    a:hover {{
        text-decoration: underline;
    }}
    
    /* 列表 */
    ul, ol {{
        padding-left: 2em;
        margin-top: 0;
        margin-bottom: 16px;
    }}
    
    li {{
        margin-top: 0.25em;
    }}
    
    /* 表格 */
    table {{
        border-spacing: 0;
        border-collapse: collapse;
        margin-top: 0;
        margin-bottom: 16px;
        width: 100%;
    }}
    
    table th {{
        font-weight: 600;
        padding: 6px 13px;
        border: 1px solid #dfe2e5;
        background-color: #f6f8fa;
    }}
    
    table td {{
        padding: 6px 13px;
        border: 1px solid #dfe2e5;
    }}
    
    table tr {{
        background-color: #fff;
        border-top: 1px solid #c6cbd1;
    }}
    
    table tr:nth-child(2n) {{
        background-color: #f6f8fa;
    }}
    
    /* 水平线 */
    hr {{
        height: 0.25em;
        padding: 0;
        margin: 24px 0;
        background-color: #e1e4e8;
        border: 0;
    }}
    
    /* 图片 */
    img {{
        max-width: 100%;
        box-sizing: content-box;
        background-color: #fff;
    }}
</style>
</head>
<body>
{html_content}
</body>
</html>'''


# 用于在独立进程中运行预览窗口
if __name__ == '__main__':
    app = get_qt_app()
    
    window = MarkdownPreviewWindow()
    window.show()
    
    # 测试内容
    test_html = """
    <h1>标题测试</h1>
    <p><strong>粗体</strong> <em>斜体</em> <del>删除线</del> <mark>高亮</mark></p>
    <p>H<sub>2</sub>O x<sup>2</sup></p>
    <pre><code>print("Hello World")</code></pre>
    """
    window.set_html(test_html)
    
    sys.exit(app.exec())
