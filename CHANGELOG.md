# Markdo 更新日志

## 版本 1.0.3 (2024-12-25)

### 🎯 主要改进
- **完善快捷键系统**: 修复了快捷键在编辑框内外不一致的问题，大幅增强了键盘操作支持
- **使用指南优化**: 修复了使用指南对话框的显示问题

### 🔧 技术修复
- **快捷键上下文**: 将 `ApplicationShortcut` 改为 `WindowShortcut`，解决与编辑框按键处理的冲突
- **智能冲突检测**: 避免工具栏快捷键与主快捷键重复设置
- **焦点一致性**: 确保快捷键在编辑框内外都能正常工作

### ✨ 新增功能
- **文件操作快捷键**: Ctrl+N(新建)、Ctrl+O(打开)、Ctrl+S(保存)、Ctrl+Shift+S(另存为)
- **编辑操作快捷键**: Ctrl+Z(撤销)、Ctrl+Y(重做)、Ctrl+A(全选)、Ctrl+F(查找)、Ctrl+Shift+C(复制全文)
- **实用快捷键**: Ctrl+T(插入时间戳)、Ctrl+R(插入分割线)
- **帮助快捷键**: F1(显示快捷键帮助)
- **智能快捷键管理**: 统一管理25个功能快捷键，避免冲突

### 🔧 技术改进
- 统一使用 `Qt.ShortcutContext.ApplicationShortcut` 确保全局有效
- 实现快捷键冲突检测机制
- 添加防重复触发功能
- 增强状态栏反馈机制
- 完善菜单栏快捷键集成

### 📋 完整快捷键列表
文件操作 (4个): Ctrl+N, Ctrl+O, Ctrl+S, Ctrl+Shift+S  
编辑操作 (6个): Ctrl+Z, Ctrl+Y, Ctrl+Shift+Z, Ctrl+A, Ctrl+F, Ctrl+Shift+C  
文本格式 (7个): Ctrl+B, Ctrl+I, Ctrl+D, Ctrl+H, Ctrl+`, Ctrl+1~6  
插入内容 (7个): Ctrl+K, Ctrl+Shift+K, Ctrl+Q, Ctrl+L, Ctrl+Shift+L, Ctrl+R, Ctrl+T  
工具栏 (2个): Ctrl+M, Ctrl+;  
帮助 (1个): F1  

**总计**: 27个功能快捷键

## 版本 1.0.2 (2024-12-20)

### 功能特性
- 实时Markdown预览
- 悬浮工具栏支持
- 多标签页编辑
- 主题切换(暗黑/明亮)
- 数学公式支持(MathJax)
- 语法高亮显示
- 列表自动续接
- Tab键自动补全

### 技术特性
- PyQt6 + WebEngine架构
- Python-Markdown解析
- pymdown-extensions扩展
- cx_Freeze打包
- Inno Setup安装程序

---

**发布日期**: 2024-12-25  
**兼容性**: Windows 10/11, Python 3.8+