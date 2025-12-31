"""
将 markdo-icon.png 转换为 Markdo.ico
需要安装 Pillow: pip install Pillow
"""
try:
    from PIL import Image
    
    # 打开PNG图片
    img = Image.open('markdo-icon.png')
    
    # 转换为ICO格式，包含多个尺寸
    img.save('Markdo.ico', format='ICO', sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    
    print("✅ 图标转换成功！已生成 Markdo.ico")
    
except ImportError:
    print("❌ 需要安装 Pillow 库")
    print("请运行: pip install Pillow")
except FileNotFoundError:
    print("❌ 找不到 markdo-icon.png 文件")
except Exception as e:
    print(f"❌ 转换失败: {e}")
