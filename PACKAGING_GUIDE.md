# Markdo 打包与文件关联指南

## 📦 打包步骤

### 1. 打包程序
```bash
python setup_cx.py build
```

打包完成后，可执行文件在：`build/exe.win-amd64-3.13/`

### 2. 测试程序
```bash
cd build/exe.win-amd64-3.13
Markdo.exe
```

## 🔗 设置文件关联

使用cx_Freeze打包后，需要手动注册文件关联。已为你准备好自动化脚本。

### 快速设置（推荐）

1. 进入打包目录：`build/exe.win-amd64-3.13/`
2. 双击运行：`register_file_association.bat`
3. 完成！

### 功能说明

注册后你将获得：
- ✅ 双击.md文件可选择用Markdo打开
- ✅ 在"打开方式"列表中看到Markdo
- ✅ 右键菜单"用 Markdo 编辑"选项
- ✅ 支持.md和.markdown文件

### 卸载关联

运行：`unregister_file_association.bat`

## 📖 更多信息

详细说明请查看打包目录中的：`FILE_ASSOCIATION_README.md`

## 🚀 命令行使用

```bash
# 直接打开文件
Markdo.exe "你的文件.md"

# 从任意位置打开
"C:\完整路径\Markdo.exe" "文档.md"
```

## 📝 注意事项

1. 注册脚本使用HKCU注册表项（用户级别），**不需要管理员权限**
2. 只影响当前用户，其他用户不受影响
3. 卸载软件前建议运行卸载脚本清理注册表
4. main.py已支持命令行参数，可直接接受文件路径

## 🔧 技术细节

**已实现的功能：**
- [x] main.py支持命令行参数打开文件
- [x] 自动注册.md和.markdown文件关联
- [x] Windows右键菜单集成
- [x] "打开方式"列表集成
- [x] 友好应用名称显示
- [x] 自动化注册/卸载脚本

**涉及的文件：**
- `main.py` - 添加了命令行参数处理
- `setup_cx.py` - 包含注册脚本到打包
- `register_file_association.bat` - 注册文件关联
- `unregister_file_association.bat` - 卸载文件关联
- `FILE_ASSOCIATION_README.md` - 用户使用说明
