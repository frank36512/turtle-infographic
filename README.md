# 小乌龟信息图 (Turtle Infographic)

一个基于 Gemini API 的智能信息图生成工具，通过简单的四步流程（选风格→选比例→输内容→生成图片）快速生成高质量信息图。

## 功能特点

- **8 大风格分类**：3D拟真、极简扁平、科技赛博、复古怀旧、艺术有机、电影视觉、材质纹理、抽象概念
- **多种比例预设**：1:1（社交媒体）、4:3（文档）、16:9（视频）、3:4（手机端）等
- **智能提示词生成**：自动生成结构化提示词，无需手动编写复杂指令
- **图形用户界面**：直观的 GUI 操作界面
- **配置管理**：灵活的配置系统，支持 API 密钥、保存路径等参数设置
- **多模型支持**：支持 Gemini 系列模型以及兼容 OpenAI 格式的 API

## 项目结构

```
信息图生成工具/
├── config/                    # 配置模块
│   ├── config.json.example   # 配置文件模板
│   └── config.json           # 配置文件（需手动创建）
├── core/                      # 核心业务模块
│   ├── __init__.py
│   ├── config_manager.py     # 配置读取与更新
│   ├── prompt_generator.py   # 提示词自动生成
│   └── image_generator.py    # API 调用与图片生成
├── interface/                 # 交互模块
│   ├── __init__.py
│   └── gui.py                # 图形用户界面
├── output/                    # 输出目录（自动创建）
│   └── infographics/         # 生成的信息图保存位置
├── main.py                    # 程序入口
├── requirements.txt           # 依赖包列表
└── README.md                  # 本文件
```

## 环境要求

- Python 3.8+
- Windows/Linux/macOS
- 网络连接（调用 Gemini API）

## 安装步骤

### 1. 克隆或下载项目

```bash
git clone <repository-url>
cd Turtle-Infographic
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

主要依赖：
- `requests`：用于 API 调用
- `Pillow`：用于图片处理
- `tkinter`：Python 内置，用于 GUI（无需额外安装）

### 3. 配置 API 密钥

前往 [Google AI Studio](https://aistudio.google.com/app/apikey) 获取 Gemini API 密钥，或者使用兼容 OpenAI 格式的 API 服务。

**步骤：**

1. 在 `config` 目录下，将 `config.json.example` 复制或重命名为 `config.json`。
2. 编辑 `config.json`，填写 `gemini_api_key` 字段。

```json
{
  "gemini_api_key": "YOUR_GEMINI_API_KEY_HERE",
  ...
}
```

或者，您可以直接运行程序，通过程序的"系统设置"界面进行配置。

## 使用方法

### 启动程序

在项目根目录下运行：

```bash
python main.py
```

程序将启动图形界面（GUI）。

### 操作流程

1. **设置 API**：首次运行请点击"系统设置"，输入 API Key 并保存。
2. **选择风格**：从下拉菜单中选择心仪的设计风格。
3. **选择比例**：选择图片输出比例。
4. **输入内容**：在文本框中输入想要生成的信息图主题或内容描述。
5. **生成**：点击"生成信息图"按钮，等待图片生成。
6. **保存**：生成的图片会自动保存到 `output/infographics` 目录，界面上也会显示预览。

## 开源协议

本项目采用 [Apache License 2.0](LICENSE) 协议开源。
