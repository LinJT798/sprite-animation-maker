import json
import os
import time
from concurrent.futures import ThreadPoolExecutor
from volcenginesdkarkruntime import Ark
from .utils import download_file, format_time

class VideoGenerator:
    def __init__(self, config_path="config.json"):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        self.client = Ark(api_key=os.environ.get("ARK_API_KEY"))
        
    def generate_single_video(self, image_base64, action_name, output_filename):
        """生成单个视频"""
        action_prompt = self.config['animation_presets'][action_name]
        
        # 从配置获取视频参数
        video_config = self.config['video_settings']
        duration = video_config['duration']
        resolution = video_config.get('resolution', '720p')
        camera_follow = video_config.get('camera_follow', False)
        fps = video_config.get('fps', 24)
        ratio = video_config.get('ratio', '16:9')
        
        # 构建完整的提示词
        cf_param = "true" if camera_follow else "false"
        full_prompt = f"{action_prompt} --rs {resolution} --dur {duration} --cf {cf_param} --fps {fps} --rt {ratio}"
        
        print(f"  开始生成 {action_name} 视频...")
        
        # 创建视频生成任务
        create_result = self.client.content_generation.tasks.create(
            model=self.config['video_settings']['model'],
            content=[
                {"text": full_prompt, "type": "text"},
                {"image_url": {"url": image_base64}, "type": "image_url"}
            ]
        )
        
        # 获取任务ID
        task_id = create_result.id
        print(f"  任务已创建: {task_id}")
        
        # 等待任务完成并获取视频URL
        video_url = self._wait_for_completion(task_id, action_name)
        
        # 下载视频到本地
        output_dir = self.config['output_paths']['videos']
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, output_filename)
        
        # 下载视频
        if download_file(video_url, output_path):
            print(f"  ✓ {action_name}: {output_path}")
            return output_path
        else:
            raise Exception(f"视频下载失败: {action_name}")
    
    def generate_multiple_videos(self, image_base64, action_names):
        """并发生成多个动作的视频"""
        results = {}
        
        with ThreadPoolExecutor(max_workers=min(len(action_names), 3)) as executor:
            futures = {}
            for action in action_names:
                output_filename = f"{action}.mp4"
                future = executor.submit(
                    self.generate_single_video, 
                    image_base64, 
                    action, 
                    output_filename
                )
                futures[action] = future
            
            for action, future in futures.items():
                try:
                    video_path = future.result()
                    results[action] = video_path
                except Exception as e:
                    print(f"  ✗ 生成{action}视频失败: {e}")
                    results[action] = None
                    
        return results
    
    def _wait_for_completion(self, task_id, action_name, timeout=300):
        """等待任务完成并返回视频URL"""
        start_time = time.time()
        check_interval = 3  # 每3秒检查一次
        
        while True:
            elapsed = time.time() - start_time
            if elapsed > timeout:
                raise TimeoutError(f"任务超时: {task_id}")
            
            # 查询任务状态
            try:
                get_result = self.client.content_generation.tasks.get(task_id=task_id)
                status = get_result.status
                
                if status == "succeeded":
                    # 任务成功，返回视频URL
                    video_url = get_result.content.video_url
                    print(f"  {action_name} 生成完成 (用时: {format_time(int(elapsed))})")
                    return video_url
                    
                elif status == "failed":
                    # 任务失败
                    error_msg = getattr(get_result, 'error', '未知错误')
                    raise Exception(f"视频生成失败: {error_msg}")
                    
                elif status == "cancelled":
                    # 任务被取消
                    raise Exception(f"任务被取消: {task_id}")
                    
                elif status in ["queued", "running"]:
                    # 任务还在处理中
                    if elapsed % 10 == 0:  # 每10秒提示一次
                        print(f"  {action_name} 生成中... ({status})")
                    time.sleep(check_interval)
                    
                else:
                    # 未知状态
                    raise Exception(f"未知任务状态: {status}")
                    
            except Exception as e:
                if "TimeoutError" in str(type(e)) or "failed" in str(e).lower():
                    raise
                # API调用错误，稍后重试
                print(f"  查询任务状态失败，重试中: {e}")
                time.sleep(check_interval)