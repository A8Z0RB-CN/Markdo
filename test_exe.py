# -*- coding: utf-8 -*-
import subprocess
import time
import sys
import os

os.chdir(r"build\exe.win-amd64-3.13")

print("=" * 50)
print("测试打包后的程序")
print("=" * 50)
print()

try:
    print("正在启动程序...")
    p = subprocess.Popen(
        ['Markdo.exe'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NO_WINDOW
    )
    
    print("等待 3 秒...")
    time.sleep(3)
    
    # 检查进程状态
    if p.poll() is None:
        print("[OK] 程序正在运行（进程仍在运行）")
        print("[信息] GUI 程序应该已经启动")
        p.terminate()
        time.sleep(1)
        if p.poll() is None:
            p.kill()
        print("[OK] 程序已关闭")
    else:
        return_code = p.returncode
        stdout, stderr = p.communicate()
        
        print(f"[状态] 程序已退出，返回码: {return_code}")
        
        if stderr:
            err_text = stderr.decode('utf-8', errors='ignore')
            if err_text.strip():
                print("\n[错误输出]:")
                print(err_text)
        
        if stdout:
            out_text = stdout.decode('utf-8', errors='ignore')
            if out_text.strip():
                print("\n[标准输出]:")
                print(out_text)
        
        if return_code != 0:
            print("\n[错误] 程序异常退出")
            sys.exit(1)
        else:
            print("\n[OK] 程序正常退出")
            
except Exception as e:
    print(f"[错误] 运行程序时发生异常: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("=" * 50)
print("测试完成")
print("=" * 50)

