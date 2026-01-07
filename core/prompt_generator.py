class PromptGenerator:
    def __init__(self, config_manager):
        self.config = config_manager
        # 基础模板（兼容旧版）
        self.base_template = (
            "生成一张{style_name}风格的信息图，风格特点：{style_desc}。"
            "比例：{ratio}，分辨率：{resolution}，语言：{language}。"
            "核心内容：{content}。"
            "设计要求：符合所选风格的视觉特征，布局清晰，重点突出，配色协调，适合{usage_scene}使用。"
            "输出格式：高清 PNG 图片，无水印，无多余文字。"
        )

    def generate_advanced(self, purpose, content, ratio="16:9", image_size="1K", 
                         shot_type=None, lighting=None, art_style=None, 
                         additional_params=None):
        """
        基于Google官方文档的高级提示词生成
        :param purpose: 用途类别（如"逼真场景摄影"）
        :param content: 核心内容描述
        :param ratio: 宽高比
        :param image_size: 分辨率（1K/2K/4K）
        :param shot_type: 镜头类型（用于摄影）
        :param lighting: 光照类型（用于摄影）
        :param art_style: 艺术风格（用于插画）
        :param additional_params: 额外参数字典
        :return: 优化的提示词
        """
        purposes = self.config.get('purpose_categories', {})
        if purpose not in purposes:
            raise ValueError(f"无效用途：{purpose}，可选：{list(purposes.keys())}")
        
        purpose_info = purposes[purpose]
        template = purpose_info['template']
        
        # 准备参数
        params = {
            'content': content,
            'aspect_ratio': ratio,
            'image_size': image_size
        }
        
        # 根据用途添加特定参数
        if purpose == "逼真场景摄影":
            params['shot_type'] = shot_type or 'wide-angle shot'
            params['lighting'] = lighting or 'natural sunlight'
            params['mood'] = additional_params.get('mood', 'professional') if additional_params else 'professional'
            params['camera_details'] = additional_params.get('camera_details', 'professional camera') if additional_params else 'professional camera'
            params['key_details'] = additional_params.get('key_details', 'sharp details') if additional_params else 'sharp details'
            params['subject'] = additional_params.get('subject', 'scene') if additional_params else 'scene'
        elif purpose == "风格化插画贴纸":
            params['art_style'] = art_style or 'modern minimalist'
            params['line_style'] = additional_params.get('line_style', 'clean lines') if additional_params else 'clean lines'
            params['color_palette'] = additional_params.get('color_palette', 'vibrant colors') if additional_params else 'vibrant colors'
            params['background_type'] = additional_params.get('background_type', 'transparent') if additional_params else 'transparent'
            params['subject'] = additional_params.get('subject', 'character') if additional_params else 'character'
        elif purpose == "文字准确渲染":
            params['design_type'] = additional_params.get('design_type', 'logo') if additional_params else 'logo'
            params['text_content'] = additional_params.get('text_content', '') if additional_params else ''
            params['font_style'] = additional_params.get('font_style', 'modern bold') if additional_params else 'modern bold'
            params['style_description'] = additional_params.get('style_description', 'professional') if additional_params else 'professional'
            params['color_scheme'] = additional_params.get('color_scheme', 'brand colors') if additional_params else 'brand colors'
        elif purpose == "信息图表数据可视化":
            params['style'] = art_style or 'modern professional'
            params['key_elements'] = additional_params.get('key_elements', 'data points') if additional_params else 'data points'
            params['visual_style'] = additional_params.get('visual_style', 'clear and colorful') if additional_params else 'clear and colorful'
            params['target_audience'] = additional_params.get('target_audience', 'general audience') if additional_params else 'general audience'
        
        # 尝试填充模板
        try:
            prompt = template.format(**params)
        except KeyError as e:
            # 如果缺少参数，使用占位符
            missing_key = str(e).strip("'")
            params[missing_key] = f"[{missing_key}]"
            prompt = template.format(**params)
        
        # 添加分辨率说明
        if image_size in ['2K', '4K']:
            prompt += f" Generate at {image_size} resolution."
        
        return prompt.strip()

    def generate(self, style_key, ratio, content, usage_scene="通用场景"):
        """
        生成标准化提示词（保留旧版兼容）
        :param style_key: 选中的风格键（如"A 3D拟真与维度"）
        :param ratio: 选中的比例（如"16:9"）
        :param content: 核心内容描述
        :param usage_scene: 使用场景
        :return: 结构化提示词
        """
        # 获取风格名称和描述
        style_dict = self.config.get_style_categories()
        if style_key not in style_dict:
            raise ValueError(f"无效风格：{style_key}，可选风格：{list(style_dict.keys())}")
        style_name = style_key.split(" ")[1] if " " in style_key else style_key
        style_desc = style_dict[style_key]

        # 获取分辨率
        resolution = "1024x1024"  # 默认分辨率
        language = self.config.get("language", "zh-CN")

        # 填充模板
        prompt = self.base_template.format(
            style_name=style_name,
            style_desc=style_desc,
            ratio=ratio,
            resolution=resolution,
            language=language,
            content=content,
            usage_scene=usage_scene
        )
        return prompt.strip()

    def custom_prompt(self, custom_text):
        """支持用户自定义提示词"""
        return custom_text.strip()
