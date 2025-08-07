import os
import requests
from typing import Optional

def download_file(url: str, output_path: str, timeout: int = 300) -> bool:
    """
    下载文件到指定路径
    
    Args:
        url: 文件URL
        output_path: 输出路径
        timeout: 超时时间（秒）
        
    Returns:
        bool: 是否下载成功
    """
    try:
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 下载文件
        response = requests.get(url, stream=True, timeout=timeout)
        response.raise_for_status()
        
        # 写入文件
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    
        return True
    except Exception as e:
        print(f"下载失败: {e}")
        return False

def format_time(seconds: int) -> str:
    """格式化时间显示"""
    if seconds < 60:
        return f"{seconds}秒"
    else:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}分{secs}秒"

def clean_filename(filename: str) -> str:
    """清理文件名，移除非法字符"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename