#!/usr/bin/env python3
"""
独立的预览器启动脚本
可以使用系统Python运行，避免虚拟环境中缺少tkinter的问题
"""

import sys
import os

# 添加项目路径到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.animation_preview import launch_preview

if __name__ == "__main__":
    if len(sys.argv) > 1:
        session_path = sys.argv[1]
    else:
        # 查找最新的session目录
        output_dir = "./output"
        if os.path.exists(output_dir):
            # 从sprites目录查找session（因为session目录结构改变了）
            sprites_dir = os.path.join(output_dir, "sprites")
            if os.path.exists(sprites_dir):
                sessions = [d for d in os.listdir(sprites_dir) if d.startswith("session_")]
                if sessions:
                    sessions.sort()
                    # 构建完整的session路径
                    session_name = sessions[-1]
                    session_path = os.path.join(output_dir, session_name)
                    print(f"使用最新的session: {session_path}")
                else:
                    print("错误: 没有找到任何session目录")
                    print("提示: 请先运行主程序生成动画")
                    sys.exit(1)
            else:
                print("错误: sprites目录不存在")
                print("提示: 请先运行主程序生成动画")
                sys.exit(1)
        else:
            print("错误: output目录不存在")
            sys.exit(1)
    
    launch_preview(session_path)