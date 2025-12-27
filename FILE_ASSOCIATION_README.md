# Markdo 文件关联设置指南

## 如何将Markdo设置为.md文件的默认打开方式

### 方法1：使用自动注册脚本（推荐）

1. 找到打包后的目录（`build/exe.win-amd64-3.13/`）
2. 双击运行 `register_file_association.bat`
3. 按照提示完成注册

**注册后你将获得：**
- ✅ .md和.markdown文件可以用Markdo打开
- ✅ 右键菜单中添加"用 Markdo 编辑"选项
- ✅ 在"打开方式"列表中看到Markdo

### 方法2：手动设置默认打开方式

1. 右键点击任意.md文件
2. 选择"属性"
3. 点击"更改"按钮
4. 选择"更多应用"
5. 滚动到底部，点击"在这台电脑上查找其他应用"
6. 浏览到Markdo.exe所在目录并选择它
7. 勾选"始终使用此应用打开.md文件"

### 卸载文件关联

如果需要移除文件关联，运行 `unregister_file_association.bat`

## 使用说明

### 双击打开
设置为默认打开方式后，直接双击.md文件即可用Markdo打开

### 右键打开
即使不是默认打开方式，也可以：
1. 右键点击.md文件
2. 选择"打开方式" → "Markdo"

或者：
1. 右键点击任意文件
2. 选择"用 Markdo 编辑"

### 命令行打开
```
Markdo.exe "文件路径.md"
```

## 技术细节

注册脚本会修改以下注册表项（用户级别，HKCU）：
- `Software\Classes\.md\OpenWithProgids`
- `Software\Classes\Markdo.md`
- `Software\Classes\Applications\Markdo.exe`
- `Software\Classes\*\shell\Markdo`

所有修改仅影响当前用户，不需要管理员权限。
