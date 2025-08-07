import os
import cv2
import numpy as np
from PIL import Image
from rembg import remove, new_session
import json
import math

class FrameProcessor:
    def __init__(self, config_path="config.json"):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        # 初始化时不创建会话，等用户选择模型后再创建
        self.rembg_session = None
        self.current_model = None
        
    def set_model(self, model_name):
        """设置并初始化指定的抠图模型"""
        if self.current_model != model_name:
            print(f"  加载抠图模型: {model_name}...")
            self.rembg_session = new_session(model_name)
            self.current_model = model_name
            print(f"  ✓ 模型加载完成")
            
    def extract_frames(self, video_path, action_name):
        """从视频中提取帧"""
        cap = cv2.VideoCapture(video_path)
        fps = self.config['video_settings']['fps']
        video_fps = cap.get(cv2.CAP_PROP_FPS)
        
        # 计算帧采样间隔
        frame_interval = int(video_fps / fps)
        
        frames = []
        frame_count = 0
        saved_count = 0
        
        # 创建临时目录存储原始帧
        temp_dir = f"./temp_frames/{action_name}"
        os.makedirs(temp_dir, exist_ok=True)
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            if frame_count % frame_interval == 0:
                frame_path = os.path.join(temp_dir, f"frame_{saved_count:03d}.png")
                cv2.imwrite(frame_path, frame)
                frames.append(frame_path)
                saved_count += 1
                
            frame_count += 1
            
        cap.release()
        return frames
    
    def remove_background(self, frame_paths):
        """批量移除背景"""
        processed_frames = []
        
        for frame_path in frame_paths:
            # 读取图片
            with open(frame_path, 'rb') as f:
                input_img = f.read()
            
            # 移除背景，使用alpha matting提高质量
            output_img = remove(
                input_img,
                session=self.rembg_session,
                alpha_matting=True,
                alpha_matting_foreground_threshold=270,
                alpha_matting_background_threshold=10,
                alpha_matting_erode_size=10
            )
            
            # 保存处理后的图片（覆盖原图）
            processed_path = frame_path.replace('.png', '_nobg.png')
            with open(processed_path, 'wb') as f:
                f.write(output_img)
                
            processed_frames.append(processed_path)
            
        return processed_frames
    
    def create_sprite_sequence(self, frame_paths, action_name):
        """将处理后的帧生成精灵表"""
        output_dir = os.path.join(self.config['output_paths']['sprites'], action_name)
        os.makedirs(output_dir, exist_ok=True)
        
        images = []
        
        for frame_path in frame_paths:
            # 读取图片
            img = Image.open(frame_path)
            
            # 确保是RGBA格式（带透明通道）
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            images.append(img)
        
        # 生成精灵图
        sprite_path = self._create_sprite_sheet(images, action_name)
        print(f"  ✓ Sprite Sheet: {sprite_path}")
            
        # 清理临时文件
        self._cleanup_temp_files(action_name)
        
        return sprite_path
    
    def _create_sprite_sheet(self, images, action_name):
        """创建sprite sheet（精灵图）"""
        if not images:
            return None
            
        # 获取配置
        config = self.config.get('sprite_sheet', {})
        max_width = config.get('max_width', 2048)
        padding = config.get('padding', 2)
        bg_color = tuple(config.get('background_color', [0, 0, 0, 0]))
        
        # 获取单帧尺寸（假设所有帧大小相同）
        frame_width, frame_height = images[0].size
        
        # 计算布局
        frames_per_row = min(len(images), max_width // (frame_width + padding))
        rows_needed = math.ceil(len(images) / frames_per_row)
        
        # 计算sprite sheet尺寸
        sheet_width = frames_per_row * (frame_width + padding) - padding
        sheet_height = rows_needed * (frame_height + padding) - padding
        
        # 创建sprite sheet
        sprite_sheet = Image.new('RGBA', (sheet_width, sheet_height), bg_color)
        
        # 将每一帧粘贴到sprite sheet上
        for idx, img in enumerate(images):
            row = idx // frames_per_row
            col = idx % frames_per_row
            x = col * (frame_width + padding)
            y = row * (frame_height + padding)
            sprite_sheet.paste(img, (x, y))
        
        # 保存sprite sheet
        output_dir = os.path.join(self.config['output_paths']['sprites'], action_name)
        sprite_path = os.path.join(output_dir, f"{action_name}_sprite_sheet.png")
        sprite_sheet.save(sprite_path, 'PNG', optimize=True)
        
        # 生成配置文件
        self._create_sprite_config(action_name, len(images), frame_width, 
                                  frame_height, frames_per_row, rows_needed)
        
        # 显示sprite sheet信息
        self._show_sprite_info(action_name, images, sprite_path)
        
        return sprite_path
    
    def _create_sprite_config(self, action_name, frame_count, frame_width, 
                             frame_height, frames_per_row, rows):
        """创建sprite sheet的配置文件（方便游戏引擎使用）"""
        config = {
            "name": action_name,
            "frame_count": frame_count,
            "frame_width": frame_width,
            "frame_height": frame_height,
            "frames_per_row": frames_per_row,
            "rows": rows,
            "fps": self.config['video_settings']['fps']
        }
        
        output_dir = os.path.join(self.config['output_paths']['sprites'], action_name)
        config_path = os.path.join(output_dir, f"{action_name}_sprite_config.json")
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
    
    def _show_sprite_info(self, action_name, images, sprite_sheet_path):
        """显示sprite sheet信息"""
        # sprite sheet大小
        sprite_sheet_size = os.path.getsize(sprite_sheet_path)
        
        # 获取sprite sheet图片信息
        sprite_img = Image.open(sprite_sheet_path)
        width, height = sprite_img.size
        
        print(f"\n  📊 Sprite Sheet 信息 ({action_name}):")
        print(f"     文件大小: {self._format_size(sprite_sheet_size)}")
        print(f"     尺寸: {width} x {height} px")
        print(f"     总帧数: {len(images)}")
        print(f"     单帧尺寸: {images[0].size[0]} x {images[0].size[1]} px")
    
    def _format_size(self, size_bytes):
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def process_video(self, video_path, action_name):
        """完整的视频处理流程"""
        print(f"正在处理 {action_name} 视频...")
        
        # 1. 提取帧
        print(f"  提取帧...")
        frame_paths = self.extract_frames(video_path, action_name)
        print(f"  ✓ 提取了 {len(frame_paths)} 帧")
        
        # 2. 移除背景
        print(f"  移除背景...")
        processed_frames = self.remove_background(frame_paths)
        print(f"  ✓ 背景移除完成")
        
        # 3. 创建精灵表
        print(f"  生成精灵表...")
        sprite_path = self.create_sprite_sequence(processed_frames, action_name)
        
        return sprite_path
    
    def _cleanup_temp_files(self, action_name):
        """清理临时文件"""
        import shutil
        temp_dir = f"./temp_frames/{action_name}"
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)