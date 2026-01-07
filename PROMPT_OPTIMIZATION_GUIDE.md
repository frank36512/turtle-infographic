# 提示词生成系统优化指南

## 📋 概述

基于 Google Gemini 官方文档优化了提示词生成系统，增加了**专业模式**，提供更精细的控制选项。

## 🎯 新功能

### 1. 双模式系统

#### 简易模式（原有功能）
- **风格选择**：8种预设风格（3D拟真、极简扁平、科技赛博等）
- **比例选择**：10种宽高比（1:1、16:9、9:16等）
- **快速生成**：适合快速创作

#### 专业模式（新增）
基于 Google 官方最佳实践，提供8种专业用途模板：

##### 📷 逼真场景摄影
- **镜头类型**：特写、广角、微距、肖像、俯瞰、仰视等
- **光照类型**：自然阳光、黄金时刻、柔和漫射、戏剧侧光、霓虹灯等
- **适用**：产品摄影、人物肖像、场景拍摄
- **模板**：`A photorealistic {shot_type} of {subject}, {content}. Illuminated by {lighting}...`

##### 🎨 风格化插画贴纸
- **艺术风格**：可爱日系、现代极简、手绘草图、水彩画、像素艺术等
- **背景选项**：透明背景支持
- **适用**：贴纸、图标、素材资源
- **模板**：`A {art_style} illustration of {subject}, featuring {content}...`

##### ✍ 文字准确渲染
- **字体样式**：现代粗体、优雅手写、复古风格等
- **设计类型**：徽标、海报、图表
- **适用**：需要精确文字的设计（Logo、海报、图表）
- **特点**：Gemini 3 Pro 在文字渲染方面表现出色

##### 📦 产品模型摄影
- **工作室光照**：三点布光、柔光箱等专业设置
- **角度控制**：展示产品特定功能
- **适用**：电子商务、广告、产品展示

##### 🎭 极简负空间设计
- **留白设计**：大量负空间用于叠加文字
- **适用**：网站背景、演示文稿、营销材料

##### 📊 信息图表数据可视化
- **教育性**：科普、教学内容
- **数据展示**：图表、流程图、时间线
- **目标受众**：可指定受众群体
- **示例**：光合作用过程、节假日安排、技术原理图

##### 📽 连续艺术漫画
- **多分格**：故事板、漫画分镜
- **角色一致性**：保持角色跨格连贯
- **适用**：视觉叙事、教程说明

##### 🌐 使用实时数据
- **Google搜索接地**：基于实时信息生成
- **适用**：天气预报、股市图表、新闻事件
- **要求**：需要 Gemini 3 Pro Image 模型

### 2. 技术参数

#### 宽高比（10种）
```
1:1   正方形
2:3   竖屏照片
3:2   横屏照片
3:4   手机竖屏
4:3   标准显示器
4:5   社交媒体竖版
5:4   社交媒体横版
9:16  短视频竖屏
16:9  宽屏视频
21:9  超宽屏
```

#### 分辨率选项
- **1K**：标准分辨率（1024px）- 快速生成
- **2K**：高分辨率（2048px）- 高质量输出
- **4K**：超高分辨率（4096px）- 仅 Gemini 3 Pro，专业级

### 3. 镜头类型（摄影用途）
```
close-up              特写镜头
wide-angle shot       广角镜头
macro shot            微距镜头
portrait              肖像镜头
full-body shot        全身镜头
bird's eye view       俯瞰视角
low-angle perspective 仰视视角
over-the-shoulder     过肩镜头
```

### 4. 光照类型（摄影用途）
```
natural sunlight       自然阳光
golden hour light      黄金时刻光线
soft diffused light    柔和漫射光
dramatic side lighting 戏剧性侧光
studio lighting        工作室灯光
neon lighting          霓虹灯光
candlelight           烛光
backlight             背光
```

### 5. 艺术风格（插画用途）
```
cute kawaii           可爱日系
modern minimalist     现代极简
hand-drawn sketch     手绘草图
watercolor            水彩画
flat design           扁平化设计
3D rendered           3D渲染
pixel art             像素艺术
vintage poster        复古海报
```

## 💡 使用建议

### 官方最佳实践

1. **内容要非常具体**
   - ❌ "奇幻盔甲"
   - ✅ "华丽的精灵板甲，蚀刻着银叶图案，带有高领和猎鹰翅膀形状的肩甲"

2. **提供上下文和意图**
   - ❌ "设计徽标"
   - ✅ "为高端极简护肤品牌设计徽标"

3. **迭代和优化**
   - 利用对话特性进行小幅更改
   - "这很棒，但你能让光线更暖一些吗？"

4. **使用分步指令**
   - 复杂场景拆分为多个步骤
   - "首先，创建一个薄雾弥漫的森林。然后，添加古老石制祭坛。最后，放置发光的剑。"

5. **控制镜头**
   - 使用摄影和电影语言
   - `wide-angle shot`, `macro shot`, `low-angle perspective`

### 用途选择指南

| 需求 | 推荐用途 | 关键要素 |
|------|----------|----------|
| 产品照片 | 产品模型摄影 | 工作室光照、专业角度 |
| 社交媒体图标 | 风格化插画贴纸 | 透明背景、可爱风格 |
| Logo设计 | 文字准确渲染 | 精确文字、品牌配色 |
| 教育海报 | 信息图表数据可视化 | 清晰标签、视觉层次 |
| 人物摄影 | 逼真场景摄影 | 肖像镜头、黄金时刻光 |
| PPT背景 | 极简负空间设计 | 大量留白、简约配色 |
| 漫画故事 | 连续艺术漫画 | 角色一致性、分镜叙事 |
| 天气图表 | 使用实时数据 | Google搜索、实时信息 |

## 🎨 示例提示词

### 逼真场景摄影
```
A photorealistic portrait of an elderly Japanese potter, focused expression, 
working with clay in a traditional studio. The scene is illuminated by golden 
hour light, creating a warm atmosphere. Captured with professional camera, 
emphasizing texture of clay and wrinkled hands. 3:4 format.
```

### 信息图表
```
Create a vibrant infographic that explains photosynthesis as if it were a 
recipe for a plant's favorite food. Show the "ingredients" (sunlight, water, 
CO2) and the "finished dish" (sugar/energy). The style should be like a page 
from a colorful kids' cookbook, suitable for a 4th grader. 16:9 format.
```

### 文字准确渲染
```
Create a modern minimalist logo with the text "The Daily Grind" in a bold 
sans-serif font. The design should be clean and professional, with a 
coffee-themed color scheme of dark brown and cream. 1:1 format.
```

## 🔧 API 兼容性

### Gemini 3 Pro Image Preview（推荐）
- ✅ 所有功能
- ✅ 4K 分辨率
- ✅ Google 搜索接地
- ✅ 思维模式（自动优化构图）
- ✅ 最多 14 张参考图片

### Gemini 2.5 Flash Image（Nano Banana）
- ✅ 基础功能
- ✅ 最高 1K 分辨率
- ✅ 快速生成
- ⚠️ 不支持 4K
- ⚠️ 不支持 Google 搜索

### OpenAI 格式（nano-banana-2）
- ✅ 基础文生图
- ⚠️ 功能有限
- ⚠️ 不支持高级特性

## 📝 配置文件结构

```json
{
  "purpose_categories": {
    "逼真场景摄影": {
      "desc": "照片级真实感的场景...",
      "template": "A photorealistic {shot_type}..."
    },
    ...
  },
  "shot_types": {
    "wide-angle shot": "广角镜头",
    ...
  },
  "lighting_types": {
    "natural sunlight": "自然阳光",
    ...
  },
  "art_styles": {
    "modern minimalist": "现代极简",
    ...
  },
  "image_sizes": {
    "1K": "标准分辨率（1024px）",
    "2K": "高分辨率（2048px）",
    "4K": "超高分辨率（4096px，仅Gemini 3 Pro）"
  },
  "ratio_presets": {
    "16:9": "宽屏视频",
    ...
  }
}
```

## 🚀 新增功能

1. **保存到提示词库**：生成的提示词可直接保存到提示词库，方便复用
2. **模式切换**：简易/专业模式一键切换
3. **动态选项**：根据用途自动显示相关选项（镜头、光照、风格）
4. **多分辨率支持**：1K/2K/4K 可选
5. **10种宽高比**：覆盖所有常见使用场景

## 📚 参考资料

- [Google Gemini 图片生成官方文档](https://ai.google.dev/gemini-api/docs/image-generation?hl=zh-cn)
- [Gemini 3 功能介绍](https://ai.google.dev/gemini-api/docs/image-generation?hl=zh-cn#gemini-3-capabilities)
- [提示词最佳实践](https://ai.google.dev/gemini-api/docs/image-generation?hl=zh-cn#prompting-strategies)

## 🔄 更新日志

### v2.0 - 2025-12-11
- ✨ 新增专业模式，基于 Google 官方指南
- ✨ 8种用途分类模板
- ✨ 镜头类型、光照类型选项
- ✨ 10种宽高比支持
- ✨ 1K/2K/4K 分辨率选项
- ✨ 保存到提示词库功能
- 🔧 优化提示词生成逻辑
- 📚 更新配置文件结构

---

**提示**：使用专业模式配合 Gemini 3 Pro Image Preview 模型可获得最佳效果！
