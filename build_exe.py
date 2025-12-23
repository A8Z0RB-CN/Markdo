"""
Markdo 打包脚本
使用 PyInstaller 打包为 Windows 应用程序目录
然后使用 Inno Setup 创建安装程序
"""
import subprocess
import sys
import os
import shutil

def clean_build():
    """清理旧的构建文件"""
    import stat
    
    def on_rm_error(func, path, exc_info):
        """处理只读文件删除错误"""
        os.chmod(path, stat.S_IWRITE)
        func(path)
    
    dirs_to_clean = ['build', 'dist']
    for d in dirs_to_clean:
        if os.path.exists(d):
            print(f"清理目录: {d}")
            try:
                shutil.rmtree(d, onerror=on_rm_error)
            except Exception as e:
                print(f"  警告: 无法完全清理 {d}: {e}")
                print(f"  继续打包...")

def build_app():
    """使用PyInstaller打包应用"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print("=" * 60)
    print("步骤 1: 使用 PyInstaller 打包应用程序...")
    print("=" * 60)
    
    # 使用spec文件打包
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--noconfirm",
        "Markdo.spec"
    ]
    
    result = subprocess.run(cmd)
    
    if result.returncode != 0:
        print("\n❌ PyInstaller 打包失败!")
        return False
    
    print("\n✅ PyInstaller 打包成功!")
    print(f"📁 应用程序目录: {os.path.join(script_dir, 'dist', 'Markdo')}")
    return True

def build_installer():
    """使用Inno Setup创建安装程序"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 检查Inno Setup是否安装
    iscc_paths = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
        r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
    ]
    
    iscc_path = None
    for path in iscc_paths:
        if os.path.exists(path):
            iscc_path = path
            break
    
    if not iscc_path:
        print("\n" + "=" * 60)
        print("⚠️ 未检测到 Inno Setup")
        print("=" * 60)
        print("请手动安装 Inno Setup 来创建安装程序:")
        print("1. 下载: https://jrsoftware.org/isdl.php")
        print("2. 安装 Inno Setup 6")
        print("3. 右键点击 setup.iss 选择 'Compile'")
        print(f"\n或者直接运行打包后的程序:")
        print(f"   {os.path.join(script_dir, 'dist', 'Markdo', 'Markdo.exe')}")
        return False
    
    print("\n" + "=" * 60)
    print("步骤 2: 使用 Inno Setup 创建安装程序...")
    print("=" * 60)
    
    # 创建installer目录
    installer_dir = os.path.join(script_dir, 'installer')
    os.makedirs(installer_dir, exist_ok=True)
    
    # 编译安装程序
    iss_file = os.path.join(script_dir, 'setup.iss')
    cmd = [iscc_path, iss_file]
    
    result = subprocess.run(cmd)
    
    if result.returncode != 0:
        print("\n❌ Inno Setup 编译失败!")
        return False
    
    print("\n" + "=" * 60)
    print("✅ 安装程序创建成功!")
    print(f"📦 安装程序: {os.path.join(installer_dir, 'Markdo_Setup_1.0.0.exe')}")
    print("=" * 60)
    return True

def main():
    print("\n" + "=" * 60)
    print("🚀 Markdo 打包工具")
    print("=" * 60 + "\n")
    
    # 清理旧文件
    clean_build()
    
    # 打包应用
    if not build_app():
        return 1
    
    # 创建安装程序
    build_installer()
    
    print("\n✅ 打包完成!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
