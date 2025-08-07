import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import json
import os
import glob

class AnimationPreview:
    def __init__(self, sprites_path):
        self.sprites_path = sprites_path
        self.session_path = os.path.dirname(sprites_path)  # 用于显示
        
        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("动画预览器")
        self.root.geometry("800x600")
        
        # 动画相关变量
        self.animations = {}
        self.current_animation = None
        self.current_frame = 0
        self.is_playing = True
        self.animation_delay = 100  # 默认延迟（毫秒）
        
        # 加载所有动画
        self.load_animations()
        
        # 创建UI
        self.create_ui()
        
        # 开始动画循环
        if self.animations:
            first_animation = list(self.animations.keys())[0]
            self.switch_animation(first_animation)
            self.animate()
    
    def load_animations(self):
        """加载所有动画资源"""
        # 查找所有sprite配置文件
        config_files = glob.glob(os.path.join(self.sprites_path, '*/*_sprite_config.json'))
        
        for config_file in config_files:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            action_name = config['name']
            sprite_path = config_file.replace('_sprite_config.json', '_sprite_sheet.png')
            
            if os.path.exists(sprite_path):
                # 加载sprite sheet
                sprite_image = Image.open(sprite_path)
                
                # 解析帧
                frames = self.extract_frames(sprite_image, config)
                
                # 计算帧延迟
                fps = config.get('fps', 10)
                delay = int(1000 / fps)  # 转换为毫秒
                
                self.animations[action_name] = {
                    'frames': frames,
                    'config': config,
                    'delay': delay
                }
    
    def extract_frames(self, sprite_sheet, config):
        """从sprite sheet中提取帧"""
        frames = []
        frame_width = config['frame_width']
        frame_height = config['frame_height']
        frames_per_row = config['frames_per_row']
        frame_count = config['frame_count']
        
        for i in range(frame_count):
            row = i // frames_per_row
            col = i % frames_per_row
            
            # 计算帧位置（考虑padding）
            padding = 2  # 从配置中的padding
            x = col * (frame_width + padding)
            y = row * (frame_height + padding)
            
            # 裁剪帧
            frame = sprite_sheet.crop((x, y, x + frame_width, y + frame_height))
            
            # 缩放到合适的显示大小，保持宽高比
            max_display_size = 400  # 最大显示尺寸
            
            # 计算缩放比例
            scale = min(max_display_size / frame_width, max_display_size / frame_height)
            new_width = int(frame_width * scale)
            new_height = int(frame_height * scale)
            
            # 使用高质量重采样
            frame = frame.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # 转换为PhotoImage
            photo = ImageTk.PhotoImage(frame)
            frames.append(photo)
        
        return frames
    
    def create_ui(self):
        """创建用户界面"""
        # 顶部控制区
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # 动作选择按钮
        ttk.Label(control_frame, text="选择动作:").grid(row=0, column=0, padx=5)
        
        button_col = 1
        for action_name in self.animations.keys():
            btn = ttk.Button(
                control_frame, 
                text=action_name.capitalize(),
                command=lambda a=action_name: self.switch_animation(a)
            )
            btn.grid(row=0, column=button_col, padx=5)
            button_col += 1
        
        # 播放控制
        self.play_button = ttk.Button(
            control_frame,
            text="暂停",
            command=self.toggle_play
        )
        self.play_button.grid(row=0, column=button_col, padx=20)
        
        # 帧控制按钮
        ttk.Button(
            control_frame,
            text="◀",
            width=3,
            command=self.prev_frame
        ).grid(row=0, column=button_col+1, padx=2)
        
        ttk.Button(
            control_frame,
            text="▶",
            width=3,
            command=self.next_frame
        ).grid(row=0, column=button_col+2, padx=2)
        
        # 速度控制
        ttk.Label(control_frame, text="速度:").grid(row=0, column=button_col+3, padx=5)
        self.speed_var = tk.DoubleVar(value=1.0)
        speed_scale = ttk.Scale(
            control_frame,
            from_=0.25,
            to=2.0,
            variable=self.speed_var,
            orient=tk.HORIZONTAL,
            length=150
        )
        speed_scale.grid(row=0, column=button_col+4, padx=5)
        
        self.speed_label = ttk.Label(control_frame, text="1.0x")
        self.speed_label.grid(row=0, column=button_col+5, padx=5)
        speed_scale.configure(command=self.update_speed)
        
        # 动画显示区
        display_frame = ttk.Frame(self.root, padding="10")
        display_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 画布容器
        canvas_container = ttk.Frame(display_frame, relief=tk.SUNKEN, borderwidth=2)
        canvas_container.pack(pady=10)
        
        # 画布
        self.canvas = tk.Canvas(
            canvas_container, 
            width=500, 
            height=500,
            bg='#2b2b2b'  # 深色背景
        )
        self.canvas.pack()
        
        # 添加网格背景
        self.draw_grid()
        
        # 信息区
        info_frame = ttk.Frame(self.root, padding="10")
        info_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        self.info_label = ttk.Label(info_frame, text="")
        self.info_label.pack()
        
        # 让主要区域可扩展
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        
        # 绑定键盘快捷键
        self.root.bind('<space>', lambda e: self.toggle_play())
        self.root.bind('<Left>', lambda e: self.prev_frame())
        self.root.bind('<Right>', lambda e: self.next_frame())
        
        # 添加快捷键提示
        shortcut_frame = ttk.Frame(self.root, padding="5")
        shortcut_frame.grid(row=3, column=0, sticky=(tk.W, tk.E))
        ttk.Label(shortcut_frame, text="快捷键: 空格=播放/暂停  ←/→=上/下一帧", 
                 foreground='gray').pack()
    
    def switch_animation(self, action_name):
        """切换动画"""
        if action_name in self.animations:
            self.current_animation = action_name
            self.current_frame = 0
            self.update_info()
    
    def toggle_play(self):
        """切换播放/暂停"""
        self.is_playing = not self.is_playing
        self.play_button.configure(text="播放" if not self.is_playing else "暂停")
    
    def prev_frame(self):
        """上一帧"""
        if self.current_animation:
            anim = self.animations[self.current_animation]
            frame_count = len(anim['frames'])
            self.current_frame = (self.current_frame - 1) % frame_count
            self.show_current_frame()
            self.is_playing = False
            self.play_button.configure(text="播放")
    
    def next_frame(self):
        """下一帧"""
        if self.current_animation:
            anim = self.animations[self.current_animation]
            frame_count = len(anim['frames'])
            self.current_frame = (self.current_frame + 1) % frame_count
            self.show_current_frame()
            self.is_playing = False
            self.play_button.configure(text="播放")
    
    def show_current_frame(self):
        """显示当前帧"""
        if self.current_animation:
            anim = self.animations[self.current_animation]
            frames = anim['frames']
            
            # 清除动画元素（保留网格）
            self.canvas.delete("sprite")
            
            if frames and self.current_frame < len(frames):
                # 居中显示
                canvas_width = self.canvas.winfo_width()
                canvas_height = self.canvas.winfo_height()
                center_x = canvas_width // 2 if canvas_width > 1 else 250
                center_y = canvas_height // 2 if canvas_height > 1 else 250
                
                self.canvas.create_image(
                    center_x, center_y,
                    image=frames[self.current_frame],
                    anchor=tk.CENTER,
                    tags="sprite"
                )
            
            self.update_info()
    
    def update_speed(self, value):
        """更新播放速度"""
        speed = float(value)
        self.speed_label.configure(text=f"{speed:.2f}x")
    
    def update_info(self):
        """更新信息显示"""
        if self.current_animation:
            anim = self.animations[self.current_animation]
            config = anim['config']
            info = f"动作: {self.current_animation} | "
            info += f"帧数: {config['frame_count']} | "
            info += f"FPS: {config['fps']} | "
            info += f"当前帧: {self.current_frame + 1}/{config['frame_count']}"
            self.info_label.configure(text=info)
    
    def draw_grid(self):
        """绘制网格背景"""
        grid_size = 20
        color = '#3a3a3a'
        
        # 绘制垂直线
        for x in range(0, 400, grid_size):
            self.canvas.create_line(x, 0, x, 400, fill=color, tags="grid")
        
        # 绘制水平线
        for y in range(0, 400, grid_size):
            self.canvas.create_line(0, y, 400, y, fill=color, tags="grid")
    
    def animate(self):
        """动画循环"""
        if self.current_animation and self.is_playing:
            anim = self.animations[self.current_animation]
            frames = anim['frames']
            
            # 清除动画元素（保留网格）
            self.canvas.delete("sprite")
            
            if frames:
                # 居中显示
                canvas_width = self.canvas.winfo_width()
                canvas_height = self.canvas.winfo_height()
                center_x = canvas_width // 2 if canvas_width > 1 else 250
                center_y = canvas_height // 2 if canvas_height > 1 else 250
                
                self.canvas.create_image(
                    center_x, center_y,
                    image=frames[self.current_frame],
                    anchor=tk.CENTER,
                    tags="sprite"
                )
            
            # 更新帧索引
            self.current_frame = (self.current_frame + 1) % len(frames)
            self.update_info()
        
        # 计算延迟
        if self.current_animation:
            base_delay = self.animations[self.current_animation]['delay']
            speed = self.speed_var.get()
            delay = int(base_delay / speed)
        else:
            delay = 100
        
        # 继续动画循环
        self.root.after(delay, self.animate)
    
    def run(self):
        """运行预览器"""
        self.root.mainloop()


def launch_preview(session_path):
    """启动预览器"""
    # 确定sprites目录的实际位置
    session_name = os.path.basename(session_path)
    
    # 尝试不同的目录结构
    possible_sprites_paths = [
        os.path.join(session_path, 'sprites'),  # 旧结构: output/session_xxx/sprites
        os.path.join(os.path.dirname(session_path), 'sprites', session_name),  # 新结构: output/sprites/session_xxx
        os.path.join('./output', 'sprites', session_name)  # 绝对路径
    ]
    
    sprites_path = None
    for path in possible_sprites_paths:
        if os.path.exists(path):
            sprites_path = path
            break
    
    if not sprites_path:
        print(f"错误: 找不到精灵图目录")
        print(f"尝试过的路径: {possible_sprites_paths}")
        return
    
    # 检查是否有动画文件
    config_files = glob.glob(os.path.join(sprites_path, '*/*_sprite_config.json'))
    if not config_files:
        print(f"错误: 在 {sprites_path} 中没有找到任何动画文件")
        return
    
    print(f"\n🎮 启动动画预览器...")
    print(f"📁 精灵图目录: {sprites_path}")
    
    # 使用sprites路径作为session路径
    preview = AnimationPreview(sprites_path)
    preview.run()