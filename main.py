#!/usr/bin/env python3
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 检查环境变量
if not os.environ.get("OPENAI_API_KEY"):
    print("❌ 错误: 请设置 OPENAI_API_KEY 环境变量")
    print("提示: 复制 .env.example 为 .env 并填入你的API密钥")
    sys.exit(1)
    
if not os.environ.get("ARK_API_KEY"):
    print("❌ 错误: 请设置 ARK_API_KEY 环境变量")
    print("提示: 复制 .env.example 为 .env 并填入你的API密钥")
    sys.exit(1)

from src.prompt_enhancer import PromptEnhancer
from src.image_generator import ImageGenerator
from src.video_generator import VideoGenerator
from src.frame_processor import FrameProcessor

def display_images(image_paths):
    """显示生成的图片路径供用户查看"""
    print("\n✓ 图片已保存到: ./output/images/")
    print("\n请查看生成的4张图片并选择一张:")
    for i, path in enumerate(image_paths):
        print(f"  {i+1}) {os.path.basename(path)}")
    
    while True:
        try:
            choice = input("\n选择 (1-4): ")
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(image_paths):
                return image_paths[choice_idx]
            else:
                print("请输入1-4之间的数字")
        except ValueError:
            print("请输入有效的数字")

def select_actions(config):
    """选择动画动作"""
    # 从配置文件读取动作列表
    animation_presets = config.get('animation_presets', {})
    
    # 创建动作映射
    actions = {}
    action_names = list(animation_presets.keys())
    
    print("\n[3] 请选择动画动作 (可多选，用逗号分隔):")
    for i, (action_key, action_desc) in enumerate(animation_presets.items(), 1):
        actions[str(i)] = action_key
        print(f"    {i}) {action_key}")
    
    while True:
        choice = input("\n选择动作: ")
        selections = [s.strip() for s in choice.split(',')]
        
        selected_actions = []
        for sel in selections:
            if sel in actions:
                selected_actions.append(actions[sel])
            else:
                print(f"无效选择: {sel}")
                continue
                
        if selected_actions:
            return selected_actions
        else:
            print("请至少选择一个有效的动作")

def confirm_videos(video_results):
    """确认视频生成结果"""
    print("\n[4] 视频生成完成:")
    for action, path in video_results.items():
        if path:
            print(f"    ✓ {action}: {path}")
        else:
            print(f"    ✗ {action}: 生成失败")
    
    while True:
        choice = input("\n确认所有视频效果 (y/n/r-重新生成): ").lower()
        if choice in ['y', 'n', 'r']:
            return choice
        else:
            print("请输入 y、n 或 r")

def select_rembg_model(config):
    """选择抠图模型"""
    print("\n[5] 请选择抠图模型:")
    models = config.get('rembg_models', {})
    model_list = list(models.keys())
    
    for i, (model, desc) in enumerate(models.items(), 1):
        print(f"    {i}) {model}: {desc}")
    
    # 默认推荐动漫模型
    default_idx = model_list.index('isnet-anime') + 1 if 'isnet-anime' in model_list else 1
    
    while True:
        choice = input(f"\n选择模型 (1-{len(models)}) [默认: {default_idx}]: ").strip()
        if not choice:
            return model_list[default_idx - 1]
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(model_list):
                return model_list[idx]
            else:
                print(f"请输入1-{len(models)}之间的数字")
        except ValueError:
            print("请输入有效的数字")

def create_session_directory(base_config):
    """创建本次运行的时间戳目录"""
    import copy
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_name = f"session_{timestamp}"
    
    # 深拷贝配置
    updated_config = copy.deepcopy(base_config)
    
    # 更新配置中的路径
    for key in ['images', 'videos', 'sprites']:
        base_path = base_config['output_paths'][key]
        updated_config['output_paths'][key] = os.path.join(base_path, session_name, '')
    
    # 创建目录
    for path in updated_config['output_paths'].values():
        os.makedirs(path, exist_ok=True)
    
    print(f"📁 本次运行输出目录: ./output/{session_name}/")
    
    return updated_config, session_name

def main():
    print("🎬 序列帧动画生成器\n")
    
    # 初始化各个模块（先加载配置）
    import json
    with open('config.json', 'r') as f:
        base_config = json.load(f)
    
    # 创建本次运行的目录
    updated_config, session_name = create_session_directory(base_config)
    
    # 使用更新后的配置初始化模块
    enhancer = PromptEnhancer()
    image_gen = ImageGenerator()
    video_gen = VideoGenerator() 
    frame_proc = FrameProcessor()
    
    # 更新各模块的配置
    image_gen.config = updated_config
    video_gen.config = updated_config
    frame_proc.config = updated_config
    
    try:
        # 步骤1: 用户输入
        user_input = input("[1] 请输入角色描述: ")
        print("    ✓ 正在优化提示词...")
        
        # 润色提示词
        enhanced_prompt = enhancer.enhance(user_input)
        
        # 步骤2: 生成图片
        print("\n[2] 正在生成图片... (1:1, 4张)")
        image_paths = image_gen.generate(enhanced_prompt)
        
        # 用户选择图片
        selected_image = display_images(image_paths)
        
        # 步骤3: 选择动作
        selected_actions = select_actions(updated_config)
        
        # 步骤4: 生成视频
        print(f"\n[4] 正在并发生成{len(selected_actions)}个动画视频... (每个5秒)")
        
        # 获取选中图片的base64格式
        image_base64 = image_gen.get_image_base64(selected_image)
        
        # 并发生成视频
        video_results = video_gen.generate_multiple_videos(image_base64, selected_actions)
        
        # 确认视频
        confirm = confirm_videos(video_results)
        
        if confirm == 'r':
            print("重新生成功能待实现...")
            return
        elif confirm == 'n':
            print("已取消")
            return
        
        # 步骤5: 选择抠图模型
        selected_model = select_rembg_model(frame_proc.config)
        frame_proc.set_model(selected_model)
        
        # 步骤6: 处理视频生成精灵表
        print("\n[6] 正在批量处理视频并生成精灵表...")
        
        for action, video_path in video_results.items():
            if video_path and os.path.exists(video_path):
                frame_proc.process_video(video_path, action)
        
        print("\n✅ 所有动画处理完成！")
        print(f"\n📁 所有文件已保存到: ./output/{session_name}/")
        
        # 询问是否预览动画
        preview_choice = input("\n是否预览动画效果？(y/n) [默认: y]: ").strip().lower()
        if preview_choice == '' or preview_choice == 'y':
            session_path = os.path.join('./output', session_name)
            # 使用专用环境运行预览器
            import subprocess
            try:
                subprocess.run(['./run_preview.sh', session_path])
            except Exception as e:
                print(f"无法启动预览器: {e}")
                print("提示: 你可以手动运行 './run_preview.sh' 来预览动画")
        
    except KeyboardInterrupt:
        print("\n\n已取消操作")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()