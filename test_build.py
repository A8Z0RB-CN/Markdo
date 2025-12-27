#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试打包后的程序
"""
import subprocess
import sys
import os
import time

def test_build():
    build_dir = r"build\exe.win-amd64-3.13"
    exe_path = os.path.join(build_dir, "Markdo.exe")
    
    if not os.path.exists(exe_path):
        print(f"[错误] 未找到打包后的程序: {exe_path}")
        print("请先运行打包脚本")
        return False
    
    print("=" * 50)
    print("测试打包后的程序")
    print("=" * 50)
    print()
    print(f"程序路径: {exe_path}")
    print()
    
    # 尝试运行程序
    try:
        print("正在启动程序...")
        print("注意：GUI 程序会在后台运行")
        print()
        
        # 使用 subprocess 运行程序并捕获输出
        process = subprocess.Popen(
            [exe_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=build_dir,
            creationflags=subprocess.CREATE_NO_WINDOW  # 不显示控制台窗口
        )
        
        # 等待几秒钟看是否有错误
        time.sleep(3)
        
        # 检查进程是否还在运行
        if process.poll() is None:
            print("[✓] 程序正在运行（进程仍在运行）")
            print("[信息] GUI 程序已启动，请检查是否有窗口打开")
            process.terminate()
            time.sleep(1)
            if process.poll() is None:
                process.kill()
            return True
        else:
            # 进程已退出，可能有错误
            return_code = process.returncode
            stdout, stderr = process.communicate()
            
            if return_code != 0:
                print(f"[✗] 程序异常退出，返回码: {return_code}")
                if stderr:
                    print("\n[错误输出]:")
                    try:
                        error_text = stderr.decode('utf-8', errors='ignore')
                        print(error_text)
                    except:
                        print(stderr)
                if stdout:
                    print("\n[标准输出]:")
                    try:
                        output_text = stdout.decode('utf-8', errors='ignore')
                        print(output_text)
                    except:
                        print(stdout)
                return False
            else:
                print("[✓] 程序正常退出")
                return True
                
    except Exception as e:
        print(f"[✗] 运行程序时发生异常: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_build()
    print()
    print("=" * 50)
    if success:
        print("测试完成：程序可以启动")
    else:
        print("测试失败：程序无法正常启动")
    print("=" * 50)
    input("\n按 Enter 键退出...")

