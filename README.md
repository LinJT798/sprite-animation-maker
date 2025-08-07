# AI Animation Generator 🎬

<div align="center">
  <h3>一键生成游戏角色精灵动画</h3>
  <p>基于AI的全自动工作流：从文字描述到精灵动画表</p>
  
  ![License](https://img.shields.io/badge/license-MIT-blue.svg)
  ![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
  ![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)
</div>

## 📖 项目背景

在游戏开发中，创建角色动画是一个耗时且成本高昂的过程。传统流程需要：
- 🎨 美术设计角色
- 🖌️ 逐帧绘制动画
- ✂️ 手动抠图去背景
- 📐 制作精灵图表

**AI Animation Generator** 将这个复杂的流程简化为一句话描述，利用最新的AI技术自动完成整个工作流。

### 🌟 核心特性

- **文字生成角色** - 使用GPT-4.1优化提示词，gpt-image-1生成高质量角色图
- **智能视频动画** - 豆包AI视频模型生成流畅的角色动画
- **自动背景移除** - 多种AI抠图模型，完美分离角色
- **精灵图生成** - 自动组合帧序列为游戏引擎可用的Sprite Sheet
- **实时预览** - 内置动画播放器，即时查看效果

## 🚀 快速开始

### 环境要求

- Python 3.8+
- macOS / Linux / Windows
- 稳定的网络连接

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/yourusername/animation-generator.git
cd animation-generator
```

2. **运行安装脚本**
```bash
chmod +x install.sh
./install.sh
```

3. **配置API密钥**

复制环境变量模板并创建你自己的配置文件：
```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的API密钥：
```env
OPENAI_API_KEY=your_openai_api_key_here
ARK_API_KEY=your_volcano_engine_api_key_here
```

> ⚠️ **重要**：`.env` 文件包含敏感信息，已被添加到 `.gitignore`，不会被提交到版本控制系统。

> 💡 获取API密钥：
> - OpenAI: https://platform.openai.com/api-keys
> - 火山引擎: https://console.volcengine.com/ark

4. **运行程序**
```bash
./run.sh
```

## 📝 使用方法

### 1. 输入角色描述
```
[1] 请输入角色描述: 一个精灵弓箭手，金发碧眼，森林守护者
```

### 2. 选择生成的角色图
程序会生成4张不同的角色设计供你选择：
```
[2] 请查看生成的4张图片并选择一张:
    1) image_1.png
    2) image_2.png
    3) image_3.png
    4) image_4.png
选择 (1-4): 2
```

### 3. 选择动画动作
可以多选，用逗号分隔：
```
[3] 请选择动画动作 (可多选，用逗号分隔):
    1) jump
    2) run
    3) walk
    4) wave
    5) rotate
    6) idle
选择动作: 1,2,6
```

### 4. 选择抠图模型
根据角色风格选择合适的模型：
```
[5] 请选择抠图模型:
    1) u2net: 通用模型，适合大多数场景
    2) u2netp: 轻量级模型，处理速度快
    3) u2net_human_seg: 人物分割模型，适合真人照片
    4) isnet-anime: 动漫角色专用模型，高精度分割
```

### 5. 自动处理
程序会自动：
- 🎥 生成选定动作的视频
- 🖼️ 提取视频帧
- ✂️ 移除背景
- 📋 生成精灵图表

## 🎮 示例展示

### 生成的角色设计
<div align="center">
  <img src="docs/images/character_samples.png" width="600" alt="角色设计示例">
  <p><em>AI生成的不同风格角色设计</em></p>
</div>

### 动画效果预览
<div align="center">
  <img src="docs/images/animation_preview.gif" width="400" alt="动画预览">
  <p><em>实时动画预览器</em></p>
</div>

### 精灵图表输出
<div align="center">
  <img src="docs/images/sprite_sheet_example.png" width="800" alt="精灵图表">
  <p><em>自动生成的精灵图表，可直接导入游戏引擎</em></p>
</div>

### 完整工作流程
<div align="center">
  <img src="docs/images/workflow.gif" width="800" alt="工作流程">
  <p><em>从文字到动画的完整流程演示</em></p>
</div>

## ⚙️ 配置选项

### 图片生成参数
```json
"image_generation": {
    "size": "1024x1024",    // 256x256, 512x512, 1024x1024
    "quality": "high",      // low, standard, high
    "output_format": "png"  // png, jpeg
}
```

### 视频生成参数
```json
"video_settings": {
    "duration": 5,          // 视频时长(秒)
    "fps": 24,             // 帧率
    "resolution": "720p",   // 480p, 720p, 1080p
    "ratio": "1:1"         // 1:1, 16:9, 9:16
}
```

### 动画预设
支持的动画类型：
- **jump** - 跳跃动作
- **run** - 奔跑动画
- **walk** - 行走动画
- **wave** - 挥手动作
- **rotate** - 旋转动画
- **idle** - 待机动作

## 📁 项目结构

```
animation-generator/
├── config.json        # 配置文件
├── main.py           # 主程序入口
├── src/              # 核心模块
│   ├── prompt_enhancer.py    # 提示词优化
│   ├── image_generator.py    # 图片生成
│   ├── video_generator.py    # 视频生成
│   ├── frame_processor.py    # 帧处理和抠图
│   └── animation_preview.py  # 动画预览器
└── output/           # 输出目录
    └── session_*/    # 按时间戳组织的输出
```

## 🛠️ 技术栈

- **AI模型**
  - OpenAI GPT-4.1 (提示词优化)
  - OpenAI DALL-E (图片生成)
  - 火山引擎豆包 (视频生成)
  - Rembg (背景移除)

- **开发框架**
  - Python 3.8+
  - OpenCV (视频处理)
  - Pillow (图片处理)
  - Tkinter (GUI预览器)

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork 本仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的改动 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- OpenAI 提供的强大AI模型
- 火山引擎的视频生成技术
- Rembg 开源背景移除工具
- 所有贡献者和用户的支持

---

<div align="center">
  <p>如果这个项目对你有帮助，请给一个 ⭐️ Star！</p>
  <p>Made with ❤️ by [Your Name]</p>
</div>