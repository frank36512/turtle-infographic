import json
import os
import sys

class ConfigManager:
    def __init__(self, config_path=None):
        if config_path is None:
            # 获取程序运行目录（支持打包后的exe）
            if getattr(sys, 'frozen', False):
                # 打包后的exe运行
                base_path = os.path.dirname(sys.executable)
            else:
                # 开发环境运行
                base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(base_path, "config", "config.json")
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self):
        """加载配置文件，不存在则生成默认配置"""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        if not os.path.exists(self.config_path):
            default_config = self._get_default_config()
            self._save_config(default_config)
            return default_config
        with open(self.config_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _get_default_config(self):
        """默认配置模板，与 config.json 结构一致"""
        return {
            "gemini_api_key": "",
            "api_base_url": "https://generativelanguage.googleapis.com",
            "default_model": "gemini-2.0-flash-exp",
            "save_path": "./output/infographics",
            "language": "zh-CN",
            "api_presets": [
                {
                    "name": "Google官方",
                    "api_key": "",
                    "api_url": "https://generativelanguage.googleapis.com",
                    "model": "gemini-2.0-flash-exp",
                    "is_default": True
                }
            ],

"style_categories": {
        "3D": "立体感强、真实感高的3D风格，突出空间层次和实体质感，适合产品展示、数据可视化",
        "极简": "简洁明了、现代感强的扁平化设计，无多余装饰，色彩纯净，适合流程说明、基础信息图",
        "赛博": "未来感、科技感的数字化风格，含霓虹光效、代码元素、金属质感，适合科技产品、技术原理",
        "复古": "经典复古、怀旧情怀的设计风格，采用复古色调、纹理，适合历史主题、怀旧内容",
        "艺术": "艺术化、自然有机的创意风格，融入自然元素、手绘质感，适合科普、文化主题",
        "电影": "电影质感、戏剧化的视觉效果，高对比度、电影色调，适合重点突出、氛围营造",
        "材质": "强调材质质感和纹理细节，如纸张、木纹、金属纹理，适合产品细节、材质展示",
        "抽象": "抽象化、概念化的艺术表达，用几何图形、色彩块传递核心概念，适合哲学、创意主题"
    },



            "ratio_presets": {
                "1:1": "正方形（适合社交媒体、海报）",
                "4:3": "标准比例（适合文档、演示文稿）",
                "16:9": "宽屏比例（适合视频封面、大屏展示）",
                "3:4": "竖屏比例（适合手机端、短视频封面）"
            },
            "ratio_to_resolution": {
                "1:1": "1024x1024",
                "4:3": "1280x960",
                "16:9": "1920x1080",
                "3:4": "960x1280"
            }
        }

    def _save_config(self, config_dict):
        """保存配置到 JSON 文件"""
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(config_dict, f, ensure_ascii=False, indent=4)

    def get(self, key, default=None):
        """获取配置项"""
        value = self.config.get(key, default)
        # 如果是 save_path，转换为绝对路径
        if key == "save_path" and value:
            if not os.path.isabs(value):
                # 获取程序运行目录
                if getattr(sys, 'frozen', False):
                    base_path = os.path.dirname(sys.executable)
                else:
                    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                value = os.path.join(base_path, value)
        return value

    def update(self, key, value):
        """更新单个配置项（如 API 密钥）"""
        self.config[key] = value
        self._save_config(self.config)

    def get_style_categories(self):
        """获取风格分类字典"""
        return self.get("style_categories", {})

    def get_ratio_presets(self):
        """获取比例预设字典"""
        return self.get("ratio_presets", {})

    def get_resolution_by_ratio(self, ratio):
        """根据比例获取对应分辨率"""
        return self.get("ratio_to_resolution", {}).get(ratio, "1024x768")

    def get_api_presets(self):
        """获取API预设列表"""
        return self.get("api_presets", [])

    def add_api_preset(self, name, api_key, api_url, model):
        """添加API预设"""
        presets = self.get_api_presets()
        new_preset = {
            "name": name,
            "api_key": api_key,
            "api_url": api_url,
            "model": model,
            "is_default": False
        }
        presets.append(new_preset)
        self.update("api_presets", presets)

    def update_api_preset(self, index, name, api_key, api_url, model):
        """更新API预设"""
        presets = self.get_api_presets()
        if 0 <= index < len(presets):
            presets[index]["name"] = name
            presets[index]["api_key"] = api_key
            presets[index]["api_url"] = api_url
            presets[index]["model"] = model
            self.update("api_presets", presets)

    def delete_api_preset(self, index):
        """删除API预设"""
        presets = self.get_api_presets()
        if 0 <= index < len(presets):
            presets.pop(index)
            self.update("api_presets", presets)

    def set_default_api(self, index):
        """设置默认API"""
        presets = self.get_api_presets()
        for i, preset in enumerate(presets):
            preset["is_default"] = (i == index)
        self.update("api_presets", presets)

    def get_default_api_preset(self):
        """获取默认API预设"""
        presets = self.get_api_presets()
        for preset in presets:
            if preset.get("is_default", False):
                return preset
        # 如果没有默认的，返回第一个
        return presets[0] if presets else None
