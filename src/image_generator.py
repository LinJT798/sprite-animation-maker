import json
import base64
import os
from openai import OpenAI

class ImageGenerator:
    def __init__(self, config_path="config.json"):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        self.client = OpenAI()
        
    def generate(self, prompt):
        """生成多张图片并保存"""
        img_config = self.config['image_generation']
        
        # 构建生成参数
        generate_params = {
            'model': img_config['model'],
            'prompt': prompt,
            'n': img_config['count'],
            'size': img_config.get('size', '1024x1024')
        }
        
        # 添加可选参数
        if 'quality' in img_config:
            generate_params['quality'] = img_config['quality']
        
        # 处理输出格式和压缩率
        output_format = img_config.get('output_format', 'png')
        if 'output_format' in img_config:
            generate_params['output_format'] = output_format
            
        # PNG格式不支持压缩率小于100
        if 'output_compression' in img_config:
            compression = img_config['output_compression']
            if output_format == 'png' and compression < 100:
                print(f"  ⚠️  PNG格式不支持压缩，忽略compression参数")
            elif output_format == 'jpeg' or (output_format == 'png' and compression == 100):
                generate_params['output_compression'] = compression
        
        result = self.client.images.generate(**generate_params)
        
        # 确保输出目录存在
        output_dir = self.config['output_paths']['images']
        os.makedirs(output_dir, exist_ok=True)
        
        image_paths = []
        output_format = img_config.get('output_format', 'png')
        
        for i, image_data in enumerate(result.data):
            image_bytes = base64.b64decode(image_data.b64_json)
            file_path = os.path.join(output_dir, f"image_{i+1}.{output_format}")
            
            with open(file_path, "wb") as f:
                f.write(image_bytes)
            
            image_paths.append(file_path)
            
        return image_paths
    
    def get_image_base64(self, image_path):
        """将图片转换为base64格式，供视频生成使用"""
        with open(image_path, "rb") as f:
            image_bytes = f.read()
        base64_str = base64.b64encode(image_bytes).decode('utf-8')
        
        # 根据文件扩展名确定MIME类型
        ext = os.path.splitext(image_path)[1].lower()
        mime_type = 'jpeg' if ext in ['.jpg', '.jpeg'] else 'png'
        
        return f"data:image/{mime_type};base64,{base64_str}"