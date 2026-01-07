import os
import requests
from datetime import datetime
from core.logger import get_logger

class ImageGenerator:
    def __init__(self, config_manager, api_preset=None):
        self.config = config_manager
        self.api_preset = api_preset
        self.logger = get_logger()
        self._init_api()

    def _init_api(self):
        """初始化 API 配置"""
        # 如果指定了API预设，使用预设配置
        if self.api_preset:
            self.api_key = self.api_preset.get("api_key")
            self.api_url = self.api_preset.get("api_url", "https://xiaoai.plus")
            self.model = self.api_preset.get("model", "gemini-3-pro-image-preview")
            self.logger.info(f"使用API预设: {self.api_preset.get('name', '未命名')}")
        else:
            # 否则使用配置文件中的配置
            self.api_key = self.config.get("gemini_api_key")
            self.api_url = self.config.get("api_base_url", "https://xiaoai.plus")
            self.model = self.config.get("default_model", "gemini-3-pro-image-preview")
            self.logger.info("使用默认API配置")
        
        if not self.api_key:
            self.logger.error("未配置API密钥")
            raise RuntimeError("未配置 API 密钥，请在 config.json 中填写或通过设置界面配置")
        
        # 确保API URL格式正确（移除尾部斜杠和可能包含的端点路径）
        self.api_url = self.api_url.rstrip('/')
        
        # 移除用户可能错误添加的端点路径
        # 移除常见的端点路径后缀
        endpoints_to_remove = [
            '/v1/images/generations',
            '/v1beta/models',
            '/v1/chat/completions'
        ]
        for endpoint in endpoints_to_remove:
            if self.api_url.endswith(endpoint):
                self.api_url = self.api_url[:-len(endpoint)]
                self.logger.warning(f"已从API地址中移除端点路径 {endpoint}")
                break
        
        self.logger.info(f"API URL: {self.api_url}, Model: {self.model}")

    def generate(self, prompt, save_name=None):
        """
        调用 API 生成图片并保存
        :param prompt: 提示词
        :param save_name: 自定义文件名，默认自动生成
        :return: 图片保存路径
        """
        self.logger.info("开始生成图片")
        self.logger.debug(f"提示词: {prompt[:100]}...")
        
        # 判断是使用OpenAI格式还是Gemini格式
        is_openai_format = "nano-banana" in self.model.lower() or "dall-e" in self.model.lower() or "dalle" in self.model.lower()
        
        if is_openai_format:
            # OpenAI Dall-e 格式（nano-banana使用）
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "prompt": prompt,
                "model": self.model,
                "n": 1,
                "size": "1024x1024"  # 可以根据需要调整
            }
            
            api_endpoint = f"{self.api_url}/v1/images/generations"
            self.logger.info(f"使用OpenAI格式API，端点: {api_endpoint}")
        else:
            # Gemini API格式
            headers = {
                "x-goog-api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            data = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }],
                "generationConfig": {
                    "response_mime_type": "image/png"
                }
            }
            
            api_endpoint = f"{self.api_url}/v1beta/models/{self.model}:generateContent"
            self.logger.info(f"使用Gemini格式API，端点: {api_endpoint}")
        
        try:
            self.logger.info("正在调用API...")
            
            # 增加重试机制
            max_retries = 2
            retry_count = 0
            last_error = None
            
            while retry_count <= max_retries:
                try:
                    if retry_count > 0:
                        self.logger.warning(f"第 {retry_count} 次重试...")
                    
                    response = requests.post(
                        api_endpoint,
                        headers=headers,
                        json=data,
                        timeout=(30, 180)  # 连接超时30秒，读取超时180秒
                    )
                    
                    self.logger.info(f"API响应状态码: {response.status_code}")
                    break  # 成功则跳出重试循环
                    
                except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                    last_error = e
                    retry_count += 1
                    if retry_count <= max_retries:
                        wait_time = retry_count * 2  # 递增等待时间
                        self.logger.warning(f"请求超时/连接失败，{wait_time}秒后重试...")
                        import time
                        time.sleep(wait_time)
                    else:
                        raise
            
            if retry_count > max_retries:
                error_msg = f"请求失败，已重试{max_retries}次: {str(last_error)}"
                self.logger.error(error_msg)
                raise RuntimeError(error_msg)
            
            if response.status_code != 200:
                error_msg = f"API请求失败: {response.status_code} - {response.text[:200]}"
                self.logger.error(error_msg)
                raise RuntimeError(error_msg)
            
            result = response.json()
            self.logger.debug(f"响应JSON键: {list(result.keys())}")
            
            # 根据API格式解析响应
            image_data = None
            
            if is_openai_format:
                # OpenAI格式响应：{"data": [{"url": "...", "b64_json": "..."}]}
                
                if "data" not in result or len(result["data"]) == 0:
                    error_msg = "API返回数据格式错误：缺少data"
                    self.logger.error(error_msg)
                    raise RuntimeError(error_msg)
                
                image_obj = result["data"][0]
                
                # nano-banana可能返回url或b64_json
                if "b64_json" in image_obj:
                    self.logger.info("收到base64图片数据")
                    image_data = image_obj["b64_json"]
                elif "url" in image_obj:
                    self.logger.info(f"收到图片URL: {image_obj['url'][:50]}...")
                    # 从URL下载图片
                    img_response = requests.get(image_obj["url"], timeout=60)
                    if img_response.status_code == 200:
                        image_bytes = img_response.content
                        # 直接保存
                        save_path = self.config.get("save_path", "./output/infographics")
                        os.makedirs(save_path, exist_ok=True)
                        if not save_name:
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            save_name = f"infographic_{timestamp}.png"
                        full_path = os.path.join(save_path, save_name)
                        
                        with open(full_path, "wb") as f:
                            f.write(image_bytes)
                        
                        self.logger.success(f"图片已保存: {full_path}")
                        return full_path
                    else:
                        error_msg = f"下载图片失败: {img_response.status_code}"
                        self.logger.error(error_msg)
                        raise RuntimeError(error_msg)
                else:
                    error_msg = f"未找到图片数据，可用键: {list(image_obj.keys())}"
                    self.logger.error(error_msg)
                    raise RuntimeError(error_msg)
            else:
                # Gemini格式响应
                
                if "candidates" not in result or len(result["candidates"]) == 0:
                    error_msg = "API返回数据格式错误：缺少candidates"
                    self.logger.error(error_msg)
                    raise RuntimeError(error_msg)
                
                candidate = result["candidates"][0]
                
                if "content" not in candidate or "parts" not in candidate["content"]:
                    error_msg = "API返回数据格式错误：缺少content或parts"
                    self.logger.error(error_msg)
                    raise RuntimeError(error_msg)
                
                parts = candidate["content"]["parts"]
                self.logger.debug(f"响应parts数量: {len(parts)}")
                
                if len(parts) == 0:
                    error_msg = "未获取到图片数据：parts为空"
                    self.logger.error(error_msg)
                    raise RuntimeError(error_msg)
                
                # 优先检查 inlineData（驼峰格式）
                if "inlineData" in parts[0]:
                    self.logger.info("收到inlineData格式图片数据")
                    inline_data = parts[0]["inlineData"]
                    image_data = inline_data.get("data")
                elif "inline_data" in parts[0]:
                    self.logger.info("收到inline_data格式图片数据")
                    inline_data = parts[0]["inline_data"]
                    image_data = inline_data.get("data")
                elif "text" in parts[0]:
                    error_msg = f"API返回了文本而不是图片: {parts[0]['text'][:100]}"
                    self.logger.error(error_msg)
                    raise RuntimeError("API返回了文本而不是图片，可能模型不支持图片生成")
                else:
                    error_msg = f"未找到图片数据字段，可用键: {list(parts[0].keys())}"
                    self.logger.error(error_msg)
                    raise RuntimeError(error_msg)
            
            if not image_data:
                error_msg = "图片数据为空"
                self.logger.error(error_msg)
                raise RuntimeError(error_msg)
            
            # 获取base64编码的图片数据
            import base64
            self.logger.info(f"正在解码图片数据（{len(image_data)}字符）")
            image_bytes = base64.b64decode(image_data)
            
            # 处理保存路径
            save_path = self.config.get("save_path", "./output/infographics")
            os.makedirs(save_path, exist_ok=True)
            if not save_name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_name = f"infographic_{timestamp}.png"
            full_path = os.path.join(save_path, save_name)
            
            self.logger.info(f"正在保存图片到: {full_path}")
            
            # 保存图片
            with open(full_path, "wb") as f:
                f.write(image_bytes)
            
            self.logger.success(f"图片生成成功！保存到: {save_name}")
            return full_path
            
        except requests.exceptions.Timeout:
            error_msg = "API请求超时（120秒），请检查网络或稍后重试"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)
        except requests.exceptions.RequestException as e:
            error_msg = f"网络请求失败: {str(e)}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)
        except Exception as e:
            error_msg = f"图片生成失败: {str(e)}"
            self.logger.error(error_msg)
            import traceback
            self.logger.debug(traceback.format_exc())
            raise RuntimeError(error_msg)
    
    def generate_with_reference(self, prompt, reference_images, reference_mode="full", save_name=None):
        """
        使用参考图片进行创作（参考图片+提示词 -> 新图片）
        :param prompt: 创作提示词
        :param reference_images: PIL Image对象或对象列表（参考图片）
        :param reference_mode: 参考方式 - style(风格), composition(构图), elements(元素), full(全面)
        :param save_name: 自定义文件名
        :return: 生成图片的保存路径
        """
        import base64
        import io
        
        # 确保reference_images是列表
        if not isinstance(reference_images, list):
            reference_images = [reference_images]
        
        # 将所有PIL Image转换为base64
        images_base64 = []
        for ref_img in reference_images:
            buffer = io.BytesIO()
            ref_img.save(buffer, format='PNG')
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            images_base64.append(image_base64)
        
        # 判断API格式
        is_openai_format = "nano-banana" in self.model.lower() or "dall-e" in self.model.lower() or "dalle" in self.model.lower()
        
        if is_openai_format:
            # OpenAI格式（nano-banana等）不直接支持参考图片
            # 提示用户或降级为纯文本生成
            print("[警告] 当前模型不支持参考图片功能，将仅使用提示词生成")
            return self.generate(prompt, save_name)
        else:
            # Gemini格式支持图片+文本输入
            headers = {
                "x-goog-api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            # 根据参考方式构建不同的指令
            mode_instructions = {
                "style": "Use the reference image(s) as STYLE inspiration. Analyze the artistic style, color palette, texture, and visual treatment, then create a new image with the same style but following the user's requirements.",
                "composition": "Use the reference image(s) as COMPOSITION reference. Analyze the layout, spatial arrangement, balance, and structure, then create a new image with similar composition but following the user's requirements.",
                "elements": "Use the reference image(s) as ELEMENTS reference. Identify key visual elements, objects, or motifs, then incorporate similar elements into a new image following the user's requirements.",
                "full": "Use the reference image(s) as COMPREHENSIVE reference. Analyze and draw inspiration from style, composition, elements, and overall aesthetic, then create a new image following the user's requirements."
            }
            
            mode_instruction = mode_instructions.get(reference_mode, mode_instructions["full"])
            
            # 多图片时的额外说明
            multi_image_note = ""
            if len(reference_images) > 1:
                multi_image_note = f"\n\nNOTE: You are provided with {len(reference_images)} reference images. Analyze all of them and synthesize their common features or combine their best aspects according to the reference mode."
            
            # 构建明确的创作指令，告诉AI要基于参考图片进行创作
            enhanced_prompt = f"""Please analyze the provided reference image(s) and create a new image based on them.

REFERENCE MODE: {mode_instruction}{multi_image_note}

USER REQUIREMENTS:
{prompt}

Important:
- Generate a NEW creative work (not an edit of the reference)
- Follow the reference mode instructions carefully
- Maintain high quality and artistic coherence
- Output as PNG image"""
            
            # 构建包含所有参考图片和提示词的请求
            parts = [{"text": enhanced_prompt}]
            
            # 添加所有参考图片
            for img_base64 in images_base64:
                parts.append({
                    "inline_data": {
                        "mime_type": "image/png",
                        "data": img_base64
                    }
                })
            
            data = {
                "contents": [{
                    "parts": parts
                }],
                "generationConfig": {
                    "response_mime_type": "image/png"
                }
            }
            
            api_endpoint = f"{self.api_url}/v1beta/models/{self.model}:generateContent"
            
            try:
                self.logger.info(f"使用{len(reference_images)}张参考图片生成，模式: {reference_mode}")
                self.logger.debug(f"增强提示词: {enhanced_prompt[:200]}...")
                
                # 增加重试机制
                max_retries = 2
                retry_count = 0
                last_error = None
                
                while retry_count <= max_retries:
                    try:
                        if retry_count > 0:
                            self.logger.warning(f"第 {retry_count} 次重试...")
                        
                        response = requests.post(
                            api_endpoint,
                            headers=headers,
                            json=data,
                            timeout=(30, 200)  # 连接超时30秒，读取超时200秒（参考图片需要更长时间）
                        )
                        
                        self.logger.info(f"API响应状态码: {response.status_code}")
                        break  # 成功则跳出重试循环
                        
                    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                        last_error = e
                        retry_count += 1
                        if retry_count <= max_retries:
                            wait_time = retry_count * 3  # 递增等待时间
                            self.logger.warning(f"请求超时/连接失败，{wait_time}秒后重试...")
                            import time
                            time.sleep(wait_time)
                        else:
                            raise
                
                if retry_count > max_retries:
                    error_msg = f"请求失败，已重试{max_retries}次: {str(last_error)}"
                    self.logger.error(error_msg)
                    raise RuntimeError(error_msg)
                
                if response.status_code != 200:
                    error_msg = f"API请求失败: {response.status_code} - {response.text[:200]}"
                    self.logger.error(error_msg)
                    raise RuntimeError(error_msg)
                
                result = response.json()
                self.logger.debug(f"响应JSON键: {list(result.keys())}")
                
                # 解析Gemini格式响应
                if "candidates" not in result or len(result["candidates"]) == 0:
                    error_msg = "API返回数据格式错误：缺少candidates"
                    self.logger.error(error_msg)
                    raise RuntimeError(error_msg)
                
                candidate = result["candidates"][0]
                parts = candidate["content"]["parts"]
                
                if len(parts) == 0:
                    error_msg = "未获取到图片数据：parts为空"
                    self.logger.error(error_msg)
                    raise RuntimeError(error_msg)
                
                # 获取图片数据（处理两种可能的字段名）
                image_data = None
                if "inlineData" in parts[0]:
                    self.logger.info("收到inlineData格式图片数据")
                    image_data = parts[0]["inlineData"].get("data")
                elif "inline_data" in parts[0]:
                    self.logger.info("收到inline_data格式图片数据")
                    image_data = parts[0]["inline_data"].get("data")
                
                if not image_data:
                    error_msg = "未获取到生成的图片数据"
                    self.logger.error(error_msg)
                    raise RuntimeError(error_msg)
                
                # 解码并保存
                self.logger.info(f"正在解码图片数据（{len(image_data)}字符）")
                image_bytes = base64.b64decode(image_data)
                
                save_path = self.config.get("save_path", "./output/infographics")
                os.makedirs(save_path, exist_ok=True)
                if not save_name:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    save_name = f"reference_{timestamp}.png"
                full_path = os.path.join(save_path, save_name)
                
                with open(full_path, "wb") as f:
                    f.write(image_bytes)
                
                self.logger.success(f"参考图片生成成功！保存到: {save_name}")
                return full_path
                
            except requests.exceptions.Timeout:
                error_msg = "API请求超时，参考图片生成通常需要更长时间，建议减少参考图片数量或稍后重试"
                self.logger.error(error_msg)
                raise RuntimeError(error_msg)
            except requests.exceptions.RequestException as e:
                error_msg = f"网络请求失败: {str(e)}"
                self.logger.error(error_msg)
                raise RuntimeError(error_msg)
            except Exception as e:
                error_msg = f"参考图片生成失败: {str(e)}"
                self.logger.error(error_msg)
                import traceback
                self.logger.debug(traceback.format_exc())
                raise RuntimeError(error_msg)
    
    def generate_with_image(self, prompt, input_image, save_name=None):
        """
        使用输入图片进行编辑生成（图片到图片编辑）
        :param prompt: 编辑指令
        :param input_image: PIL Image对象
        :param save_name: 自定义文件名
        :return: 编辑后图片的保存路径
        """
        import base64
        import io
        
        # 将PIL Image转换为base64
        buffer = io.BytesIO()
        input_image.save(buffer, format='PNG')
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # 判断API格式
        is_openai_format = "nano-banana" in self.model.lower()
        
        if is_openai_format:
            # OpenAI格式不直接支持图片编辑，使用图片变体API或直接文生图
            # 这里简化处理，仅使用提示词
            return self.generate(prompt, save_name)
        else:
            # Gemini格式支持图片+文本输入
            headers = {
                "x-goog-api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            data = {
                "contents": [{
                    "parts": [
                        {
                            "text": prompt
                        },
                        {
                            "inline_data": {
                                "mime_type": "image/png",
                                "data": image_base64
                            }
                        }
                    ]
                }],
                "generationConfig": {
                    "response_mime_type": "image/png"
                }
            }
            
            api_endpoint = f"{self.api_url}/v1beta/models/{self.model}:generateContent"
            
            try:
                print(f"\n[调试] 图片编辑API调用")
                print(f"[调试] API端点: {api_endpoint}")
                print(f"[调试] 提示词: {prompt}")
                print(f"[调试] 输入图片base64长度: {len(image_base64)} 字符")
                
                response = requests.post(
                    api_endpoint,
                    headers=headers,
                    json=data,
                    timeout=120
                )
                
                print(f"[调试] HTTP状态码: {response.status_code}")
                
                if response.status_code != 200:
                    print(f"[调试] 错误响应: {response.text}")
                    raise RuntimeError(f"API 请求失败: {response.status_code} - {response.text}")
                
                result = response.json()
                print(f"[调试] 响应JSON键: {list(result.keys())}")
                
                # 解析响应（与generate方法类似）
                if "candidates" not in result or len(result["candidates"]) == 0:
                    raise RuntimeError("API 返回数据格式错误：缺少 candidates")
                
                candidate = result["candidates"][0]
                parts = candidate["content"]["parts"]
                
                if len(parts) == 0:
                    raise RuntimeError("未获取到图片数据：parts为空")
                
                # 获取图片数据
                image_data = None
                if "inlineData" in parts[0]:
                    image_data = parts[0]["inlineData"].get("data")
                elif "inline_data" in parts[0]:
                    image_data = parts[0]["inline_data"].get("data")
                
                if not image_data:
                    raise RuntimeError("未获取到编辑后的图片数据")
                
                # 解码并保存
                image_bytes = base64.b64decode(image_data)
                
                save_path = self.config.get("save_path", "./output/infographics")
                os.makedirs(save_path, exist_ok=True)
                if not save_name:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    save_name = f"edited_{timestamp}.png"
                full_path = os.path.join(save_path, save_name)
                
                with open(full_path, "wb") as f:
                    f.write(image_bytes)
                
                print(f"[调试] 编辑后图片保存成功: {full_path}")
                return full_path
                
            except Exception as e:
                print(f"[调试] 图片编辑异常: {type(e).__name__}: {str(e)}")
                import traceback
                traceback.print_exc()
                raise RuntimeError(f"图片编辑失败：{str(e)}")
