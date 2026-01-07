import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from PIL import Image, ImageTk
from core.config_manager import ConfigManager
from core.prompt_generator import PromptGenerator
from core.image_generator import ImageGenerator
from core.history_manager import HistoryManager
from core.prompt_library import PromptLibrary
from core.logger import get_logger

class InfographicGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("小乌龟信息图 (Turtle Infographic)")
        self.root.geometry("1100x750")
        self.root.minsize(900, 650)
        
        # 设置图标
        try:
            icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'turtle.ico')
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception as e:
            print(f"Warning: Could not load icon: {e}")
        
        # 窗口居中
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 1100
        window_height = 750
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 设置主题颜色
        self.colors = {
            'primary': '#4A90E2',
            'secondary': '#50C878',
            'bg': '#F8F9FA',
            'card': '#FFFFFF',
            'text': '#2C3E50',
            'text_light': '#7F8C8D',
            'log_debug': '#95A5A6',
            'log_info': '#3498DB',
            'log_success': '#2ECC71',
            'log_warning': '#F39C12',
            'log_error': '#E74C3C',
        }
        
        self.root.configure(bg=self.colors['bg'])
        
        # 初始化日志
        self.logger = get_logger()
        
        # 初始化模块
        self.config = ConfigManager()
        self.prompt_gen = PromptGenerator(self.config)
        self.history = HistoryManager()
        self.prompt_library = PromptLibrary()
        self.image_gen = None
        
        # 配置样式
        self._setup_styles()
        
        # 界面组件
        self._init_widgets()
        
        # 注册日志GUI回调
        self.logger.add_gui_callback(self._on_log_message)
        
        # 记录启动日志
        self.logger.info("应用程序启动")

        # 尝试初始化图片生成器
        try:
            default_preset = self.config.get_default_api_preset()
            if default_preset and default_preset.get('api_key'):
                self.image_gen = ImageGenerator(self.config, default_preset)
                self.logger.info(f"已加载API配置: {default_preset.get('name')}")
        except Exception as e:
            self.logger.error(f"初始化图片生成器失败: {str(e)}")
        
        # 注册窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # 检查API
        default_preset = self.config.get_default_api_preset()
        if not default_preset or not default_preset.get('api_key'):
            messagebox.showwarning("提示", "未配置 API！\n请先在【API设置】中添加API配置。")
            self.logger.warning("未配置API密钥")

    def _on_tab_changed(self, event):
        """标签页切换时的回调"""
        current_tab = event.widget.select()
        tab_text = event.widget.tab(current_tab, "text")
        self.logger.debug(f"切换到标签页: {tab_text}")
        
        # 如果切换到图片编辑页面，刷新模型状态
        if "图片编辑" in tab_text:
            if hasattr(self, '_update_edit_model_status'):
                self.root.after(100, self._update_edit_model_status)
    
    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('TNotebook', background=self.colors['bg'], borderwidth=0, tabmargins=[2, 5, 2, 0])
        style.configure('TNotebook.Tab', 
                       background=self.colors['card'],
                       foreground=self.colors['text'],
                       padding=[10, 6],
                       font=('微软雅黑', 10, 'bold'),
                       borderwidth=0)
        style.map('TNotebook.Tab',
                 background=[('selected', self.colors['primary']), ('active', '#5BA3EC')],
                 foreground=[('selected', 'white'), ('active', self.colors['text'])],
                 expand=[('selected', [0, 0, 0, 0])],
                 padding=[('selected', [10, 6])])
        
        style.configure('TFrame', background=self.colors['bg'])
        style.configure('TLabel', background=self.colors['bg'], 
                       foreground=self.colors['text'], font=('微软雅黑', 10))
        style.configure('Hint.TLabel', font=('微软雅黑', 9), 
                       foreground=self.colors['text_light'])
        
        style.configure('Primary.TButton',
                       font=('微软雅黑', 10, 'bold'),
                       padding=[20, 10])
        
        style.configure('Card.TLabelframe', 
                       background=self.colors['card'],
                       borderwidth=1,
                       relief='solid')
        style.configure('Card.TLabelframe.Label',
                       background=self.colors['card'],
                       foreground=self.colors['primary'],
                       font=('微软雅黑', 11, 'bold'))

    def _init_widgets(self):
        # 顶部标题栏
        header = tk.Frame(self.root, bg=self.colors['primary'], height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # Logo和标题
        try:
            logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'turtle.png')
            if os.path.exists(logo_path):
                pil_image = Image.open(logo_path)
                # Resize to fit header height (60px) while preserving aspect ratio
                height = 60
                aspect_ratio = pil_image.width / pil_image.height
                width = int(height * aspect_ratio)
                pil_image = pil_image.resize((width, height), Image.Resampling.LANCZOS)
                self.header_logo = ImageTk.PhotoImage(pil_image)
                
                tk.Label(header, text=" 小乌龟信息图 (Turtle Infographic)",
                        image=self.header_logo, compound=tk.LEFT,
                        font=("微软雅黑", 22, "bold"),
                        bg=self.colors['primary'], fg='white', padx=10).pack(pady=5)
            else:
                tk.Label(header, text="小乌龟信息图 (Turtle Infographic)",
                        font=("微软雅黑", 22, "bold"),
                        bg=self.colors['primary'], fg='white').pack(pady=15)
        except Exception as e:
            print(f"Error loading header logo: {e}")
            tk.Label(header, text="小乌龟信息图 (Turtle Infographic)",
                    font=("微软雅黑", 22, "bold"),
                    bg=self.colors['primary'], fg='white').pack(pady=15)

        # Notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=(15, 0))
        
        # 绑定标签页切换事件
        self.notebook.bind('<<NotebookTabChanged>>', self._on_tab_changed)

        self.prompt_frame = ttk.Frame(self.notebook)
        self.image_frame = ttk.Frame(self.notebook)
        self.edit_frame = ttk.Frame(self.notebook)
        self.library_frame = ttk.Frame(self.notebook)
        self.history_frame = ttk.Frame(self.notebook)
        self.settings_frame = ttk.Frame(self.notebook)
        self.log_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.prompt_frame, text="提示词生成")
        self.notebook.add(self.image_frame, text="信息图生成")
        self.notebook.add(self.edit_frame, text="图片编辑")
        self.notebook.add(self.library_frame, text="提示词库")
        self.notebook.add(self.history_frame, text="生成记录")
        self.notebook.add(self.settings_frame, text="API设置")
        self.notebook.add(self.log_frame, text="运行日志")

        self._init_prompt_page()
        self._init_image_page()
        self._init_edit_page()
        self._init_library_page()
        self._init_history_page()
        self._init_settings_page()
        self._init_log_page()
    
    def _init_log_page(self):
        """初始化运行日志页面"""
        # 顶部工具栏
        toolbar = tk.Frame(self.log_frame, bg=self.colors['bg'], height=50)
        toolbar.pack(fill=tk.X, padx=15, pady=10)
        
        tk.Label(toolbar, text="📋 运行日志", font=("微软雅黑", 14, "bold"),
                bg=self.colors['bg'], fg=self.colors['primary']).pack(side=tk.LEFT, padx=5)
        
        # 清空日志按钮 - 简约样式
        clear_btn = tk.Button(toolbar, text="🗑 清空日志", font=("微软雅黑", 9),
                             bg=self.colors['bg'], fg=self.colors['text'],
                             command=self._clear_log, cursor="hand2",
                             relief=tk.FLAT, padx=10, pady=5,
                             activebackground=self.colors['card'],
                             activeforeground=self.colors['primary'])
        clear_btn.pack(side=tk.RIGHT, padx=5)
        
        # 日志文本框
        log_container = tk.Frame(self.log_frame, bg=self.colors['card'], bd=1, relief=tk.SOLID)
        log_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        self.log_text = scrolledtext.ScrolledText(
            log_container,
            bg='#F5F7FA',
            fg='#2C3E50',
            font=("Consolas", 10),
            wrap=tk.WORD,
            state=tk.DISABLED,
            padx=10,
            pady=10
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # 配置日志文本标签颜色
        self.log_text.tag_config("DEBUG", foreground=self.colors['log_debug'])
        self.log_text.tag_config("INFO", foreground=self.colors['log_info'])
        self.log_text.tag_config("SUCCESS", foreground=self.colors['log_success'])
        self.log_text.tag_config("WARNING", foreground=self.colors['log_warning'])
        self.log_text.tag_config("ERROR", foreground=self.colors['log_error'])
    
    def _init_log_panel(self):
        """初始化底部日志面板（已废弃，改用标签页）"""
        pass
    
    def _clear_log(self):
        """清空日志"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.logger.info("日志已清空")
    
    def _on_log_message(self, timestamp, level, message):
        """接收日志消息并显示"""
        try:
            self.log_text.config(state=tk.NORMAL)
            log_line = f"[{timestamp}] [{level}] {message}\n"
            self.log_text.insert(tk.END, log_line, level)
            self.log_text.see(tk.END)  # 自动滚动到最新
            self.log_text.config(state=tk.DISABLED)
        except:
            pass  # 避免GUI错误导致程序崩溃

    def _init_prompt_page(self):
        # 创建左右布局容器
        container = tk.PanedWindow(self.prompt_frame, orient=tk.HORIZONTAL, 
                                  bg=self.colors['bg'], sashwidth=10, sashrelief=tk.RAISED,
                                  sashpad=2, bd=0)
        container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # 左侧主容器
        left_main_container = tk.Frame(container, bg=self.colors['bg'])
        container.add(left_main_container, minsize=400, stretch='always')
        
        # 底部按钮框架（固定在最底部）
        left_bottom_frame = tk.Frame(left_main_container, bg=self.colors['bg'])
        left_bottom_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=10)
        
        tk.Button(left_bottom_frame, text="🔄 生成提示词", command=self._generate_prompt_only,
                 font=("微软雅黑", 11, "bold"), bg=self.colors['primary'],
                 fg='white', relief='flat', padx=30, pady=12, cursor='hand2').pack(fill=tk.X)
        
        # 可滚动内容区域
        left_scroll_container = tk.Frame(left_main_container, bg=self.colors['bg'])
        left_scroll_container.pack(fill=tk.BOTH, expand=True)
        
        left_canvas = tk.Canvas(left_scroll_container, bg=self.colors['bg'], highlightthickness=0)
        left_scrollbar = ttk.Scrollbar(left_scroll_container, orient=tk.VERTICAL, command=left_canvas.yview)
        left_panel = tk.Frame(left_canvas, bg=self.colors['bg'])
        
        left_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        left_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        left_canvas.create_window((0, 0), window=left_panel, anchor='nw', width=left_canvas.winfo_reqwidth())
        left_canvas.configure(yscrollcommand=left_scrollbar.set)
        
        def on_frame_configure(event):
            left_canvas.configure(scrollregion=left_canvas.bbox('all'))
        
        def on_canvas_configure(event):
            # 当canvas大小改变时，更新内部窗口宽度
            canvas_width = event.width
            left_canvas.itemconfig(left_canvas.find_withtag('all')[0], width=canvas_width)
        
        left_panel.bind('<Configure>', on_frame_configure)
        left_canvas.bind('<Configure>', on_canvas_configure)
        
        # 鼠标滚轮支持
        def on_mousewheel(event):
            left_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        left_canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # 模式选择（新增）
        mode_frame = ttk.LabelFrame(left_panel, text="🎯 提示词生成模式", 
                                   padding=15, style='Card.TLabelframe')
        mode_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.prompt_mode = tk.StringVar(value="simple")
        tk.Radiobutton(mode_frame, text="简易模式（快速生成）", variable=self.prompt_mode, 
                      value="simple", bg=self.colors['card'], font=("微软雅黑", 10),
                      command=self._toggle_prompt_mode).pack(anchor=tk.W, pady=2)
        tk.Radiobutton(mode_frame, text="专业模式（基于Google官方指南）", variable=self.prompt_mode, 
                      value="advanced", bg=self.colors['card'], font=("微软雅黑", 10),
                      command=self._toggle_prompt_mode).pack(anchor=tk.W, pady=2)
        
        # 简易模式容器
        self.simple_mode_container = tk.Frame(left_panel, bg=self.colors['bg'])
        self.simple_mode_container.pack(fill=tk.BOTH, expand=True)
        
        # 风格选择
        frame1 = ttk.LabelFrame(self.simple_mode_container, text="📌 第一步：选择风格", 
                              padding=15, style='Card.TLabelframe')
        frame1.pack(fill=tk.X, padx=10, pady=10)

        self.style_var = tk.StringVar()
        styles = list(self.config.get_style_categories().keys())
        self.style_combobox = ttk.Combobox(frame1, textvariable=self.style_var, 
                                          values=styles, state="readonly",
                                          font=("微软雅黑", 10))
        self.style_combobox.pack(pady=5, fill=tk.X)
        
        self.style_desc_label = tk.Label(frame1, text="", wraplength=400, 
                                         bg=self.colors['card'],
                                         fg=self.colors['text_light'],
                                         font=("微软雅黑", 9), justify=tk.LEFT)
        self.style_desc_label.pack(pady=5)
        
        if styles:
            self.style_combobox.current(0)
            self._update_style_desc()
        self.style_combobox.bind("<<ComboboxSelected>>", lambda e: self._update_style_desc())

        # 比例选择
        frame2 = ttk.LabelFrame(self.simple_mode_container, text="📐 第二步：选择比例", 
                              padding=15, style='Card.TLabelframe')
        frame2.pack(fill=tk.X, padx=10, pady=10)

        self.ratio_var = tk.StringVar()
        ratios = list(self.config.get_ratio_presets().keys())
        
        self.ratio_combobox = ttk.Combobox(frame2, textvariable=self.ratio_var, 
                                          values=ratios, state="readonly",
                                          font=("微软雅黑", 10))
        self.ratio_combobox.pack(pady=5, fill=tk.X)
        
        self.ratio_desc_label = tk.Label(frame2, text="",
                                        bg=self.colors['card'],
                                        fg=self.colors['text_light'],
                                        font=("微软雅黑", 9))
        self.ratio_desc_label.pack(pady=5)
        
        if ratios:
            # 安全地设置默认值为 16:9，如果不存在则使用第一个
            try:
                default_index = ratios.index("16:9") if "16:9" in ratios else 0
                self.ratio_combobox.current(default_index)
            except (ValueError, IndexError):
                if len(ratios) > 0:
                    self.ratio_combobox.current(0)
            self._update_ratio_desc()
        self.ratio_combobox.bind("<<ComboboxSelected>>", lambda e: self._update_ratio_desc())

        # 内容输入
        frame3 = ttk.LabelFrame(self.simple_mode_container, text="✍ 第三步：输入内容", 
                              padding=15, style='Card.TLabelframe')
        frame3.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(frame3, text="核心内容：", bg=self.colors['card'],
                fg=self.colors['text'], font=("微软雅黑", 10, "bold")).pack(anchor=tk.W)
        self.content_text = scrolledtext.ScrolledText(frame3, height=8, wrap=tk.WORD,
                                                     font=("微软雅黑", 10),
                                                     relief='solid', bd=1)
        self.content_text.pack(fill=tk.BOTH, expand=True, pady=5)
        self.content_text.insert(tk.END, "示例：2026年法定节假日安排、T细胞激活机制科普")

        tk.Label(frame3, text="使用场景（可选）：", bg=self.colors['card'],
                fg=self.colors['text'], font=("微软雅黑", 10, "bold")).pack(anchor=tk.W, pady=(10, 0))
        self.scene_entry = ttk.Entry(frame3, font=("微软雅黑", 10))
        self.scene_entry.pack(fill=tk.X, pady=5)
        self.scene_entry.insert(tk.END, "公众号文章、论文插图、PPT演示")
        
        # 专业模式容器
        self.advanced_mode_container = tk.Frame(left_panel, bg=self.colors['bg'])
        
        # 用途分类
        adv_frame1 = ttk.LabelFrame(self.advanced_mode_container, text="🎨 用途分类", 
                                   padding=15, style='Card.TLabelframe')
        adv_frame1.pack(fill=tk.X, padx=10, pady=10)
        
        self.purpose_var = tk.StringVar()
        purposes = list(self.config.get('purpose_categories', {}).keys())
        self.purpose_combobox = ttk.Combobox(adv_frame1, textvariable=self.purpose_var,
                                            values=purposes, state="readonly",
                                            font=("微软雅黑", 10))
        self.purpose_combobox.pack(pady=5, fill=tk.X)
        if purposes:
            # 安全地设置默认值为信息图，如果不存在则使用第一个
            try:
                default_index = purposes.index("信息图表数据可视化") if "信息图表数据可视化" in purposes else min(5, len(purposes) - 1)
                self.purpose_combobox.current(default_index)
            except (ValueError, IndexError):
                if len(purposes) > 0:
                    self.purpose_combobox.current(0)
        
        self.purpose_desc_label = tk.Label(adv_frame1, text="", wraplength=400,
                                          bg=self.colors['card'],
                                          fg=self.colors['text_light'],
                                          font=("微软雅黑", 9), justify=tk.LEFT)
        self.purpose_desc_label.pack(pady=5)
        self.purpose_combobox.bind("<<ComboboxSelected>>", lambda e: self._update_purpose_desc())
        self._update_purpose_desc()
        
        # 比例和分辨率
        adv_frame2 = ttk.LabelFrame(self.advanced_mode_container, text="📐 比例与分辨率", 
                                   padding=15, style='Card.TLabelframe')
        adv_frame2.pack(fill=tk.X, padx=10, pady=10)
        
        ratio_grid = tk.Frame(adv_frame2, bg=self.colors['card'])
        ratio_grid.pack(fill=tk.X)
        
        tk.Label(ratio_grid, text="宽高比：", bg=self.colors['card'],
                font=("微软雅黑", 10)).grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.adv_ratio_var = tk.StringVar()
        adv_ratios = list(self.config.get('ratio_presets', {}).keys())
        self.adv_ratio_combobox = ttk.Combobox(ratio_grid, textvariable=self.adv_ratio_var,
                                              values=adv_ratios, state="readonly",
                                              font=("微软雅黑", 10), width=15)
        self.adv_ratio_combobox.grid(row=0, column=1, padx=5)
        if adv_ratios:
            # 安全地设置默认值为 16:9，如果不存在则使用第一个
            try:
                default_index = adv_ratios.index("16:9") if "16:9" in adv_ratios else 0
                self.adv_ratio_combobox.current(default_index)
            except (ValueError, IndexError):
                if len(adv_ratios) > 0:
                    self.adv_ratio_combobox.current(0)
        
        tk.Label(ratio_grid, text="分辨率：", bg=self.colors['card'],
                font=("微软雅黑", 10)).grid(row=0, column=2, sticky=tk.W, padx=(20, 10))
        self.image_size_var = tk.StringVar()
        image_sizes = list(self.config.get('image_sizes', {}).keys())
        self.image_size_combobox = ttk.Combobox(ratio_grid, textvariable=self.image_size_var,
                                               values=image_sizes, state="readonly",
                                               font=("微软雅黑", 10), width=10)
        self.image_size_combobox.grid(row=0, column=3, padx=5)
        if image_sizes:
            self.image_size_combobox.current(0)  # 1K
        
        # 镜头与光照（条件显示）
        self.shot_lighting_frame = ttk.LabelFrame(self.advanced_mode_container, text="📷 镜头与光照", 
                                                 padding=15, style='Card.TLabelframe')
        
        sl_grid = tk.Frame(self.shot_lighting_frame, bg=self.colors['card'])
        sl_grid.pack(fill=tk.X)
        
        tk.Label(sl_grid, text="镜头类型：", bg=self.colors['card'],
                font=("微软雅黑", 10)).grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        self.shot_type_var = tk.StringVar()
        shot_types = list(self.config.get('shot_types', {}).keys())
        self.shot_type_combobox = ttk.Combobox(sl_grid, textvariable=self.shot_type_var,
                                              values=shot_types, state="readonly",
                                              font=("微软雅黑", 10), width=20)
        self.shot_type_combobox.grid(row=0, column=1, padx=5, pady=5)
        if shot_types:
            # 安全地设置默认值
            default_index = min(1, len(shot_types) - 1) if len(shot_types) > 1 else 0
            self.shot_type_combobox.current(default_index)
        
        tk.Label(sl_grid, text="光照类型：", bg=self.colors['card'],
                font=("微软雅黑", 10)).grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        self.lighting_var = tk.StringVar()
        lightings = list(self.config.get('lighting_types', {}).keys())
        self.lighting_combobox = ttk.Combobox(sl_grid, textvariable=self.lighting_var,
                                             values=lightings, state="readonly",
                                             font=("微软雅黑", 10), width=20)
        self.lighting_combobox.grid(row=1, column=1, padx=5, pady=5)
        if lightings:
            self.lighting_combobox.current(0)  # natural sunlight
        
        # 艺术风格（条件显示）
        self.art_style_frame = ttk.LabelFrame(self.advanced_mode_container, text="🎭 艺术风格", 
                                             padding=15, style='Card.TLabelframe')
        
        self.art_style_var = tk.StringVar()
        art_styles = list(self.config.get('art_styles', {}).keys())
        self.art_style_combobox = ttk.Combobox(self.art_style_frame, textvariable=self.art_style_var,
                                              values=art_styles, state="readonly",
                                              font=("微软雅黑", 10))
        self.art_style_combobox.pack(pady=5, fill=tk.X)
        if art_styles:
            # 安全地设置默认值
            default_index = min(1, len(art_styles) - 1) if len(art_styles) > 1 else 0
            self.art_style_combobox.current(default_index)
        
        # 核心内容输入（专业模式）
        adv_frame3 = ttk.LabelFrame(self.advanced_mode_container, text="✍ 核心内容描述", 
                                   padding=15, style='Card.TLabelframe')
        adv_frame3.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(adv_frame3, text="详细描述您想要生成的内容（越具体越好）：",
                bg=self.colors['card'], fg=self.colors['text_light'],
                font=("微软雅黑", 9)).pack(anchor=tk.W, pady=(0, 5))
        
        self.adv_content_text = scrolledtext.ScrolledText(adv_frame3, height=10, wrap=tk.WORD,
                                                         font=("微软雅黑", 10),
                                                         relief='solid', bd=1)
        self.adv_content_text.pack(fill=tk.BOTH, expand=True)
        self.adv_content_text.insert(tk.END, "示例：展示光合作用的信息图，包含阳光、水、CO2作为\"原料\"，糖分/能量作为\"产物\"")

        # 右侧面板：提示词显示
        right_panel = tk.Frame(container, bg=self.colors['bg'])
        container.add(right_panel, minsize=400, stretch='always')
        
        # 提示词显示
        frame4 = ttk.LabelFrame(right_panel, text="✨ 生成的提示词", 
                              padding=15, style='Card.TLabelframe')
        frame4.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 先打包底部按钮
        right_bottom_frame = tk.Frame(frame4, bg=self.colors['card'])
        right_bottom_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        btn_row = tk.Frame(right_bottom_frame, bg=self.colors['card'])
        btn_row.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(btn_row, text="📋 复制提示词", command=self._copy_prompt,
                 font=("微软雅黑", 11, "bold"), bg=self.colors['secondary'],
                 fg='white', relief='flat', padx=30, pady=12, cursor='hand2').pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        tk.Button(btn_row, text="💾 保存到提示词库", command=self._save_to_library,
                 font=("微软雅黑", 11, "bold"), bg='#E67E22',
                 fg='white', relief='flat', padx=30, pady=12, cursor='hand2').pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # 再打包内容区域
        self.prompt_display = scrolledtext.ScrolledText(frame4, wrap=tk.WORD,
                                                       font=("微软雅黑", 10), relief='solid', bd=1)
        self.prompt_display.pack(fill=tk.BOTH, expand=True)
        
        # 初始化模式显示
        self._toggle_prompt_mode()

    def _toggle_prompt_mode(self):
        """切换简易/专业模式"""
        mode = self.prompt_mode.get()
        if mode == "simple":
            self.simple_mode_container.pack(fill=tk.BOTH, expand=True)
            self.advanced_mode_container.pack_forget()
        else:
            self.simple_mode_container.pack_forget()
            self.advanced_mode_container.pack(fill=tk.BOTH, expand=True)
            # 根据用途显示/隐藏特定选项
            self._update_advanced_options()
    
    def _update_advanced_options(self):
        """根据用途更新专业模式选项显示"""
        purpose = self.purpose_var.get()
        
        # 隐藏所有可选frame
        if hasattr(self, 'shot_lighting_frame'):
            self.shot_lighting_frame.pack_forget()
        if hasattr(self, 'art_style_frame'):
            self.art_style_frame.pack_forget()
        
        # 根据用途显示对应选项
        if purpose == "逼真场景摄影" and hasattr(self, 'shot_lighting_frame'):
            self.shot_lighting_frame.pack(fill=tk.X, padx=10, pady=10)
        elif purpose in ["风格化插画贴纸", "信息图表数据可视化"] and hasattr(self, 'art_style_frame'):
            self.art_style_frame.pack(fill=tk.X, padx=10, pady=10)
    
    def _update_purpose_desc(self):
        """更新用途描述"""
        purpose = self.purpose_var.get()
        purposes = self.config.get('purpose_categories', {})
        if purpose in purposes:
            desc = purposes[purpose].get('desc', '')
            self.purpose_desc_label.config(text=f"说明：{desc}")
        self._update_advanced_options()

    def _init_image_page(self):
        # 创建左右布局容器
        container = tk.PanedWindow(self.image_frame, orient=tk.HORIZONTAL, 
                                  bg=self.colors['bg'], sashwidth=10, sashrelief=tk.RAISED,
                                  sashpad=2, bd=0)
        container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # 左侧面板：提示词输入
        left_panel = tk.Frame(container, bg=self.colors['bg'])
        container.add(left_panel, minsize=400, stretch='always')
        
        # 提示词输入
        input_frame = ttk.LabelFrame(left_panel, text="💬 输入提示词", 
                                     padding=15, style='Card.TLabelframe')
        input_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 先打包底部按钮和状态标签
        self.progress_label = tk.Label(input_frame, text="",
                                      font=("微软雅黑", 10),
                                      bg=self.colors['card'],
                                      fg=self.colors['text_light'])
        self.progress_label.pack(side=tk.BOTTOM, pady=5)
        
        bottom_frame = tk.Frame(input_frame, bg=self.colors['card'])
        bottom_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.generate_image_btn = tk.Button(bottom_frame, text="🎨 开始生成",
                                           command=self._generate_image,
                                           font=("微软雅黑", 11, "bold"),
                                           bg=self.colors['primary'], fg='white',
                                           relief='flat', padx=30, pady=12, cursor='hand2')
        self.generate_image_btn.pack(fill=tk.X, padx=10, pady=10)
        
        # 参考图片上传区域（可选）
        reference_frame = tk.Frame(input_frame, bg=self.colors['card'])
        reference_frame.pack(fill=tk.X, pady=(0, 10))
        
        ref_label_frame = tk.Frame(reference_frame, bg=self.colors['card'])
        ref_label_frame.pack(fill=tk.X)
        
        tk.Label(ref_label_frame, text="📷 参考图片（可选）：",
                bg=self.colors['card'], fg=self.colors['text'],
                font=("微软雅黑", 9, "bold")).pack(side=tk.LEFT)
        
        tk.Label(ref_label_frame, text="上传图片作为创作参考",
                bg=self.colors['card'], fg=self.colors['text_light'],
                font=("微软雅黑", 8)).pack(side=tk.LEFT, padx=(5, 15))
        
        # 修改为支持多图片
        self.reference_images = []  # 存储多个图片对象列表 [{path, obj}, ...]
        
        upload_ref_btn = tk.Button(ref_label_frame, text="📁 添加参考图片",
                                   command=self._select_reference_image,
                                   font=("微软雅黑", 9),
                                   bg='#E8E8E8', fg=self.colors['text'],
                                   relief='flat', padx=12, pady=4, cursor='hand2')
        upload_ref_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        clear_ref_btn = tk.Button(ref_label_frame, text="❌ 清除全部",
                                  command=self._clear_reference_image,
                                  font=("微软雅黑", 9),
                                  bg='#FFE5E5', fg='#D32F2F',
                                  relief='flat', padx=12, pady=4, cursor='hand2')
        clear_ref_btn.pack(side=tk.LEFT)
        
        self.ref_image_label = tk.Label(reference_frame, text="未选择参考图片（支持多张）",
                                       bg=self.colors['card'], fg=self.colors['text_light'],
                                       font=("微软雅黑", 8), anchor=tk.W)
        self.ref_image_label.pack(fill=tk.X, pady=(5, 0))
        
        # 参考方式选择
        ref_mode_frame = tk.Frame(reference_frame, bg=self.colors['card'])
        ref_mode_frame.pack(fill=tk.X, pady=(5, 0))
        ref_mode_frame.pack_forget()  # 初始隐藏，选择图片后显示
        
        tk.Label(ref_mode_frame, text="参考方式：",
                bg=self.colors['card'], fg=self.colors['text'],
                font=("微软雅黑", 8)).pack(side=tk.LEFT)
        
        self.ref_mode_var = tk.StringVar(value="style")
        self.ref_mode_frame_widget = ref_mode_frame  # 保存引用
        
        ref_modes = [
            ("style", "🎨 风格参考"),
            ("composition", "📐 构图参考"),
            ("elements", "🧩 元素参考"),
            ("full", "🔄 全面参考")
        ]
        
        for value, text in ref_modes:
            rb = tk.Radiobutton(ref_mode_frame, text=text, value=value,
                               variable=self.ref_mode_var,
                               bg=self.colors['card'], fg=self.colors['text'],
                               font=("微软雅黑", 8), selectcolor=self.colors['card'])
            rb.pack(side=tk.LEFT, padx=5)
        
        # 参考图片预览区域（支持多图片横向滚动）
        self.ref_preview_frame = tk.Frame(reference_frame, bg='#F5F5F5', height=120)
        self.ref_preview_frame.pack(fill=tk.X, pady=(5, 0))
        self.ref_preview_frame.pack_forget()  # 初始隐藏
        
        # 创建画布用于横向滚动
        preview_canvas = tk.Canvas(self.ref_preview_frame, bg='#F5F5F5', 
                                  height=110, highlightthickness=0)
        preview_scrollbar = ttk.Scrollbar(self.ref_preview_frame, orient=tk.HORIZONTAL,
                                         command=preview_canvas.xview)
        preview_canvas.configure(xscrollcommand=preview_scrollbar.set)
        
        preview_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        preview_canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # 内部容器
        self.ref_thumbnails_container = tk.Frame(preview_canvas, bg='#F5F5F5')
        preview_canvas.create_window((0, 0), window=self.ref_thumbnails_container, anchor='nw')
        
        self.ref_thumbnails_container.bind('<Configure>',
            lambda e: preview_canvas.configure(scrollregion=preview_canvas.bbox('all')))
        
        self.ref_preview_canvas = preview_canvas  # 保存引用
        
        # 再打包提示词输入区域
        tk.Label(input_frame, text="可以从【提示词生成】页面生成，也可以直接输入：",
                bg=self.colors['card'], fg=self.colors['text_light'],
                font=("微软雅黑", 9)).pack(anchor=tk.W, pady=(0, 10))
        
        self.image_prompt_text = scrolledtext.ScrolledText(input_frame, wrap=tk.WORD,
                                                          font=("微软雅黑", 10), relief='solid', bd=1)
        self.image_prompt_text.pack(fill=tk.BOTH, expand=True)

        # 右侧面板：预览
        right_panel = tk.Frame(container, bg=self.colors['bg'])
        container.add(right_panel, minsize=400, stretch='always')
        
        preview_frame = ttk.LabelFrame(right_panel, text="🖼 图片预览", 
                                      padding=15, style='Card.TLabelframe')
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        canvas_frame = ttk.Frame(preview_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.image_canvas = tk.Canvas(canvas_frame, bg='#F5F5F5', highlightthickness=0)
        scrollbar_y = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.image_canvas.yview)
        scrollbar_x = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.image_canvas.xview)
        
        self.image_canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.image_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 底部固定的操作按钮
        save_btn_frame = tk.Frame(preview_frame, bg=self.colors['card'])
        save_btn_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        # 按钮容器 - 使用grid布局
        button_container = tk.Frame(save_btn_frame, bg=self.colors['card'])
        button_container.pack(fill=tk.X, padx=10, pady=5)
        
        # 配置列权重使按钮均分空间
        button_container.grid_columnconfigure(0, weight=1)
        button_container.grid_columnconfigure(1, weight=1)
        button_container.grid_columnconfigure(2, weight=1)
        
        self.open_image_btn = tk.Button(button_container, text="📂 打开",
                                       command=self._open_image,
                                       font=("微软雅黑", 10, "bold"),
                                       bg=self.colors['primary'], fg='white',
                                       relief='flat', pady=10,
                                       state=tk.DISABLED, cursor='hand2')
        self.open_image_btn.grid(row=0, column=0, sticky='ew', padx=(0, 5))
        
        self.show_in_folder_btn = tk.Button(button_container, text="📁 在文件夹中显示",
                                           command=self._show_in_folder,
                                           font=("微软雅黑", 10, "bold"),
                                           bg=self.colors['primary'], fg='white',
                                           relief='flat', pady=10,
                                           state=tk.DISABLED, cursor='hand2')
        self.show_in_folder_btn.grid(row=0, column=1, sticky='ew', padx=5)
        
        self.save_image_btn = tk.Button(button_container, text="💾 另存为",
                                       command=self._save_image,
                                       font=("微软雅黑", 10, "bold"),
                                       bg=self.colors['secondary'], fg='white',
                                       relief='flat', pady=10,
                                       state=tk.DISABLED, cursor='hand2')
        self.save_image_btn.grid(row=0, column=2, sticky='ew', padx=(5, 0))
        
        self.current_image_path = None
        self.current_photo = None
        
        # 绑定画布大小改变事件，自动调整图片大小
        self.image_canvas.bind('<Configure>', self._on_canvas_resize)

    def _init_edit_page(self):
        """初始化图片编辑页面（多轮对话迭代）"""
        # 创建上中下三部分布局
        main_container = tk.Frame(self.edit_frame, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # === 顶部：模型状态提示 ===
        model_status_frame = tk.Frame(main_container, bg=self.colors['bg'])
        model_status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.edit_model_status_label = tk.Label(model_status_frame,
                                               text="",
                                               bg=self.colors['bg'],
                                               font=("微软雅黑", 9),
                                               wraplength=1000,
                                               justify=tk.LEFT)
        self.edit_model_status_label.pack(fill=tk.X, padx=10)
        self._update_edit_model_status()
        
        # === 上传图片区域 ===
        upload_frame = ttk.LabelFrame(main_container, text="📤 上传要编辑的图片", 
                                     padding=15, style='Card.TLabelframe')
        upload_frame.pack(fill=tk.X, pady=(0, 10))
        
        upload_container = tk.Frame(upload_frame, bg=self.colors['card'])
        upload_container.pack(fill=tk.X)
        
        self.edit_image_path_var = tk.StringVar()
        self.edit_image_path_entry = ttk.Entry(upload_container, textvariable=self.edit_image_path_var,
                                              font=("微软雅黑", 10), state='readonly')
        self.edit_image_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        tk.Button(upload_container, text="选择图片", command=self._select_edit_image,
                 font=("微软雅黑", 10), bg=self.colors['primary'], fg='white',
                 relief='flat', padx=20, pady=8, cursor='hand2').pack(side=tk.LEFT, padx=5)
        
        tk.Button(upload_container, text="🔄 开始新会话", command=self._start_new_edit_session,
                 font=("微软雅黑", 10), bg='#E67E22', fg='white',
                 relief='flat', padx=20, pady=8, cursor='hand2').pack(side=tk.LEFT)
        
        # === 中间：左右分栏（编辑对话历史 + 输入编辑指令）===
        content_container = tk.PanedWindow(main_container, orient=tk.HORIZONTAL,
                                          bg=self.colors['bg'], sashwidth=10, 
                                          sashrelief=tk.RAISED, sashpad=2, bd=0)
        content_container.pack(fill=tk.BOTH, expand=True)
        
        # 左侧：对话历史
        left_panel = tk.Frame(content_container, bg=self.colors['bg'])
        content_container.add(left_panel, minsize=500, stretch='always')
        
        history_frame = ttk.LabelFrame(left_panel, text="💬 编辑对话历史", 
                                      padding=15, style='Card.TLabelframe')
        history_frame.pack(fill=tk.BOTH, expand=True, padx=(0, 5), pady=0)
        
        # 对话历史显示区域（带滚动条）
        history_scroll_frame = tk.Frame(history_frame, bg=self.colors['card'])
        history_scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        self.edit_history_canvas = tk.Canvas(history_scroll_frame, bg=self.colors['card'], 
                                            highlightthickness=0)
        history_scrollbar = ttk.Scrollbar(history_scroll_frame, orient=tk.VERTICAL, 
                                         command=self.edit_history_canvas.yview)
        self.edit_history_container = tk.Frame(self.edit_history_canvas, bg=self.colors['card'])
        
        history_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.edit_history_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.edit_history_canvas.create_window((0, 0), window=self.edit_history_container, 
                                              anchor='nw')
        self.edit_history_canvas.configure(yscrollcommand=history_scrollbar.set)
        
        self.edit_history_container.bind('<Configure>', 
            lambda e: self.edit_history_canvas.configure(scrollregion=self.edit_history_canvas.bbox('all')))
        
        # 右侧：编辑指令输入区域
        right_panel = tk.Frame(content_container, bg=self.colors['bg'])
        content_container.add(right_panel, minsize=500, stretch='always')
        
        input_frame = ttk.LabelFrame(right_panel, text="✍ 输入编辑指令", 
                                    padding=15, style='Card.TLabelframe')
        input_frame.pack(fill=tk.BOTH, expand=True, padx=(5, 0), pady=0)
        
        # 编辑类型选择
        edit_type_frame = tk.Frame(input_frame, bg=self.colors['card'])
        edit_type_frame.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(edit_type_frame, text="编辑类型：", bg=self.colors['card'],
                fg=self.colors['text'], font=("微软雅黑", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        
        self.edit_type_var = tk.StringVar(value="modify")
        
        type_options = [
            ("modify", "🎨 修改现有元素（改颜色、调整样式等）"),
            ("add", "➕ 添加新元素（加物体、加文字等）"),
            ("remove", "➖ 移除元素（删除物体、清除背景等）"),
            ("style", "🎭 风格转换（改为某种艺术风格）"),
            ("language", "🌍 语言/文字修改（翻译文字）"),
            ("custom", "✏️ 自定义指令")
        ]
        
        type_combo = ttk.Combobox(edit_type_frame, textvariable=self.edit_type_var,
                                 values=[opt[0] for opt in type_options],
                                 state="readonly", font=("微软雅黑", 9))
        type_combo.pack(fill=tk.X)
        
        # 创建类型到描述的映射
        self.edit_type_labels = {opt[0]: opt[1] for opt in type_options}
        
        def update_type_display(event=None):
            current = self.edit_type_var.get()
            type_combo.set(self.edit_type_labels.get(current, current))
            self._update_edit_instruction_template()
        
        type_combo.bind('<<ComboboxSelected>>', update_type_display)
        type_combo.set(self.edit_type_labels['modify'])
        
        # 严格模式选项
        strict_frame = tk.Frame(input_frame, bg=self.colors['card'])
        strict_frame.pack(fill=tk.X, pady=(5, 10))
        
        self.strict_mode_var = tk.BooleanVar(value=True)
        strict_check = tk.Checkbutton(strict_frame, 
                                     text="🔒 严格模式（禁止AI自动添加/美化元素）",
                                     variable=self.strict_mode_var,
                                     bg=self.colors['card'],
                                     font=("微软雅黑", 9, "bold"),
                                     fg='#E74C3C',
                                     selectcolor=self.colors['card'])
        strict_check.pack(anchor=tk.W)
        
        # 提示文本（不再显示，节省空间）
        # self.edit_tip_label = tk.Label(input_frame, 
        #                    text='',
        #                    bg=self.colors['card'], fg=self.colors['text_light'],
        #                    font=("微软雅黑", 9), wraplength=450, justify=tk.LEFT)
        # self.edit_tip_label.pack(anchor=tk.W, pady=(0, 10))
        
        # self._update_edit_instruction_template()
        
        # 输入框标签
        input_label = tk.Label(input_frame, text="输入编辑提示词：",
                              bg=self.colors['card'], fg=self.colors['text'],
                              font=("微软雅黑", 10, "bold"))
        input_label.pack(anchor=tk.W, pady=(0, 5))
        
        # 输入框（在上方，可以扩展）
        self.edit_instruction_text = scrolledtext.ScrolledText(input_frame, 
                                                              height=6,
                                                              wrap=tk.WORD, font=("微软雅黑", 10),
                                                              relief='solid', bd=1)
        self.edit_instruction_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 应用按钮容器（固定在底部）
        btn_container = tk.Frame(input_frame, bg=self.colors['card'])
        btn_container.pack(fill=tk.X, side=tk.BOTTOM)
        
        # 应用按钮（进度直接显示在按钮上）
        self.edit_apply_btn = tk.Button(btn_container, text="应用编辑",
                                       command=self._apply_edit_instruction,
                                       font=("微软雅黑", 11, "bold"),
                                       bg=self.colors['primary'], fg='white',
                                       relief='flat', pady=12, 
                                       cursor='hand2', state=tk.DISABLED)
        self.edit_apply_btn.pack(fill=tk.X)
        
        # 进度标签（隐藏，不再使用）
        # self.edit_progress_label = tk.Label(btn_container, text="",
        #                                   font=("微软雅黑", 9, "bold"),
        #                                   bg=self.colors['card'],
        #                                   fg=self.colors['text_light'],
        #                                   height=2)
        # self.edit_progress_label.pack(fill=tk.X, side=tk.BOTTOM)
        
        # 初始化编辑会话数据
        self.edit_session = {
            'chat_history': [],  # 对话历史
            'current_image_path': None,  # 当前图片路径
            'original_image_path': None,  # 原始图片路径
            'images': []  # 生成的图片列表
        }
        
        # 加载上次的编辑会话
        self._load_last_edit_session()

    def _init_library_page(self):
        """初始化提示词库页面"""
        # 创建左右布局
        container = tk.PanedWindow(self.library_frame, orient=tk.HORIZONTAL,
                                  bg=self.colors['bg'], sashwidth=10, sashrelief=tk.RAISED,
                                  sashpad=2, bd=0)
        container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # 左侧：分类列表
        left_panel = tk.Frame(container, bg=self.colors['bg'])
        container.add(left_panel, minsize=250, stretch='never')
        
        # 分类标题和按钮
        category_header = tk.Frame(left_panel, bg=self.colors['bg'])
        category_header.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(category_header, text="📁 分类管理", font=("微软雅黑", 12, "bold"),
                bg=self.colors['bg'], fg=self.colors['text']).pack(side=tk.LEFT)
        
        tk.Button(category_header, text="➕", command=self._add_category,
                 font=("微软雅黑", 10), bg=self.colors['primary'], fg='white',
                 relief='flat', padx=8, pady=4, cursor='hand2').pack(side=tk.RIGHT, padx=2)
        
        tk.Button(category_header, text="✏", command=self._edit_category,
                 font=("微软雅黑", 10), bg=self.colors['card'],
                 relief='solid', bd=1, padx=8, pady=4, cursor='hand2').pack(side=tk.RIGHT, padx=2)
        
        tk.Button(category_header, text="🗑", command=self._delete_category,
                 font=("微软雅黑", 10), bg=self.colors['card'],
                 relief='solid', bd=1, padx=8, pady=4, cursor='hand2').pack(side=tk.RIGHT, padx=2)
        
        # 分类列表
        category_frame = ttk.LabelFrame(left_panel, text="分类列表", padding=10, style='Card.TLabelframe')
        category_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.category_listbox = tk.Listbox(category_frame, font=("微软雅黑", 10),
                                          bg=self.colors['card'], relief='solid', bd=1)
        category_scrollbar = ttk.Scrollbar(category_frame, orient=tk.VERTICAL,
                                          command=self.category_listbox.yview)
        self.category_listbox.configure(yscrollcommand=category_scrollbar.set)
        
        self.category_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        category_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.category_listbox.bind('<<ListboxSelect>>', self._on_category_select)
        
        # 右侧：提示词列表
        right_panel = tk.Frame(container, bg=self.colors['bg'])
        container.add(right_panel, minsize=600, stretch='always')
        
        # 提示词标题和按钮
        prompt_header = tk.Frame(right_panel, bg=self.colors['bg'])
        prompt_header.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(prompt_header, text="📝 提示词列表", font=("微软雅黑", 12, "bold"),
                bg=self.colors['bg'], fg=self.colors['text']).pack(side=tk.LEFT)
        
        # 搜索框
        self.library_search_var = tk.StringVar()
        search_entry = ttk.Entry(prompt_header, textvariable=self.library_search_var,
                                font=("微软雅黑", 9), width=20)
        search_entry.pack(side=tk.RIGHT, padx=5)
        tk.Button(prompt_header, text="🔍", command=self._search_prompts,
                 font=("微软雅黑", 9), bg=self.colors['card'],
                 relief='solid', bd=1, padx=8, pady=4, cursor='hand2').pack(side=tk.RIGHT)
        
        tk.Button(prompt_header, text="➕ 添加", command=self._add_prompt_to_library,
                 font=("微软雅黑", 9), bg=self.colors['primary'], fg='white',
                 relief='flat', padx=10, pady=5, cursor='hand2').pack(side=tk.RIGHT, padx=2)
        
        tk.Button(prompt_header, text="✏ 编辑", command=self._edit_prompt_in_library,
                 font=("微软雅黑", 9), bg=self.colors['card'],
                 relief='solid', bd=1, padx=10, pady=5, cursor='hand2').pack(side=tk.RIGHT, padx=2)
        
        tk.Button(prompt_header, text="🗑 删除", command=self._delete_prompt_from_library,
                 font=("微软雅黑", 9), bg=self.colors['card'],
                 relief='solid', bd=1, padx=10, pady=5, cursor='hand2').pack(side=tk.RIGHT, padx=2)
        
        # 提示词列表
        list_frame = ttk.LabelFrame(right_panel, text="提示词", padding=10, style='Card.TLabelframe')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        columns = ("分类", "标题", "标签", "风格", "比例", "更新时间")
        self.library_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        self.library_tree.heading("分类", text="分类")
        self.library_tree.heading("标题", text="标题")
        self.library_tree.heading("标签", text="标签")
        self.library_tree.heading("风格", text="风格")
        self.library_tree.heading("比例", text="比例")
        self.library_tree.heading("更新时间", text="更新时间")
        
        self.library_tree.column("分类", width=100)
        self.library_tree.column("标题", width=200)
        self.library_tree.column("标签", width=120)
        self.library_tree.column("风格", width=80)
        self.library_tree.column("比例", width=70)
        self.library_tree.column("更新时间", width=150)
        
        tree_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL,
                                      command=self.library_tree.yview)
        self.library_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        self.library_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.library_tree.bind("<Double-1>", self._view_prompt_detail)
        
        # 右键菜单
        self.library_menu = tk.Menu(self.library_tree, tearoff=0)
        self.library_menu.add_command(label="查看详情", command=self._view_prompt_detail)
        self.library_menu.add_command(label="使用此提示词", command=self._use_library_prompt)
        self.library_menu.add_separator()
        self.library_menu.add_command(label="编辑", command=self._edit_prompt_in_library)
        self.library_menu.add_command(label="删除", command=self._delete_prompt_from_library)
        
        self.library_tree.bind("<Button-3>", self._show_library_menu)
        
        # 加载数据
        self._load_categories()

    def _init_history_page(self):
        toolbar = ttk.Frame(self.history_frame)
        toolbar.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(toolbar, text="历史记录", font=("微软雅黑", 14, "bold"),
                bg=self.colors['bg'], fg=self.colors['text']).pack(side=tk.LEFT)
        
        tk.Button(toolbar, text="🔄 刷新", command=self._refresh_history,
                 font=("微软雅黑", 9), bg=self.colors['card'],
                 relief='solid', bd=1, padx=10, pady=5, cursor='hand2').pack(side=tk.RIGHT, padx=2)
        
        tk.Button(toolbar, text="🗑 清空", command=self._clear_history,
                 font=("微软雅黑", 9), bg=self.colors['card'],
                 relief='solid', bd=1, padx=10, pady=5, cursor='hand2').pack(side=tk.RIGHT, padx=2)

        history_notebook = ttk.Notebook(self.history_frame)
        history_notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        prompt_history_frame = ttk.Frame(history_notebook)
        image_history_frame = ttk.Frame(history_notebook)
        
        history_notebook.add(prompt_history_frame, text="提示词历史")
        history_notebook.add(image_history_frame, text="图片历史")
        
        self._create_prompt_history_list(prompt_history_frame)
        self._create_image_history_list(image_history_frame)

    def _create_prompt_history_list(self, parent):
        columns = ("时间", "风格", "比例", "内容摘要")
        self.prompt_tree = ttk.Treeview(parent, columns=columns, show="headings", height=15)
        
        self.prompt_tree.heading("时间", text="生成时间")
        self.prompt_tree.heading("风格", text="风格")
        self.prompt_tree.heading("比例", text="比例")
        self.prompt_tree.heading("内容摘要", text="内容摘要")
        
        self.prompt_tree.column("时间", width=150)
        self.prompt_tree.column("风格", width=150)
        self.prompt_tree.column("比例", width=80)
        self.prompt_tree.column("内容摘要", width=300)
        
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.prompt_tree.yview)
        self.prompt_tree.configure(yscrollcommand=scrollbar.set)
        
        self.prompt_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.prompt_tree.bind("<Double-1>", self._show_prompt_detail)
        
        self.prompt_menu = tk.Menu(self.prompt_tree, tearoff=0)
        self.prompt_menu.add_command(label="查看详情", command=lambda: self._show_prompt_detail(None))
        self.prompt_menu.add_command(label="复制到生成页面", command=self._copy_prompt_to_page)
        self.prompt_menu.add_separator()
        self.prompt_menu.add_command(label="删除记录", command=self._delete_prompt_record)
        
        self.prompt_tree.bind("<Button-3>", self._show_prompt_menu)
        self._load_prompt_history()

    def _create_image_history_list(self, parent):
        columns = ("时间", "风格", "比例", "路径", "状态")
        self.image_tree = ttk.Treeview(parent, columns=columns, show="headings", height=15)
        
        self.image_tree.heading("时间", text="生成时间")
        self.image_tree.heading("风格", text="风格")
        self.image_tree.heading("比例", text="比例")
        self.image_tree.heading("路径", text="文件路径")
        self.image_tree.heading("状态", text="状态")
        
        self.image_tree.column("时间", width=150)
        self.image_tree.column("风格", width=120)
        self.image_tree.column("比例", width=70)
        self.image_tree.column("路径", width=250)
        self.image_tree.column("状态", width=80)
        
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.image_tree.yview)
        self.image_tree.configure(yscrollcommand=scrollbar.set)
        
        self.image_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.image_tree.bind("<Double-1>", self._open_image_from_history)
        
        self.image_menu = tk.Menu(self.image_tree, tearoff=0)
        self.image_menu.add_command(label="打开图片", command=lambda: self._open_image_from_history(None))
        self.image_menu.add_command(label="查看提示词", command=self._show_image_prompt)
        self.image_menu.add_command(label="在文件夹中显示", command=self._show_in_folder)
        self.image_menu.add_separator()
        self.image_menu.add_command(label="删除记录", command=self._delete_image_record)
        
        self.image_tree.bind("<Button-3>", self._show_image_menu)
        self._load_image_history()

    def _init_settings_page(self):
        tk.Label(self.settings_frame, text="⚙ API 配置管理",
                font=("微软雅黑", 14, "bold"),
                bg=self.colors['bg'], fg=self.colors['text']).pack(padx=20, pady=(15, 10), anchor=tk.W)
        
        # API列表
        presets_frame = ttk.LabelFrame(self.settings_frame, text="API 预设管理", 
                                      padding=15, style='Card.TLabelframe')
        presets_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        toolbar = ttk.Frame(presets_frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(toolbar, text="管理多个API配置，可快速切换", bg=self.colors['card'],
                fg=self.colors['text_light'], font=("微软雅黑", 9)).pack(side=tk.LEFT)
        
        tk.Button(toolbar, text="➕ 添加", command=self._add_api_preset,
                 font=("微软雅黑", 9), bg=self.colors['primary'], fg='white',
                 relief='flat', padx=10, pady=5, cursor='hand2').pack(side=tk.RIGHT, padx=2)
        
        tk.Button(toolbar, text="✏ 编辑", command=self._edit_api_preset,
                 font=("微软雅黑", 9), bg=self.colors['card'],
                 relief='solid', bd=1, padx=10, pady=5, cursor='hand2').pack(side=tk.RIGHT, padx=2)
        
        tk.Button(toolbar, text="🗑 删除", command=self._delete_api_preset,
                 font=("微软雅黑", 9), bg=self.colors['card'],
                 relief='solid', bd=1, padx=10, pady=5, cursor='hand2').pack(side=tk.RIGHT, padx=2)

        list_frame = ttk.Frame(presets_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("名称", "API地址", "模型", "默认")
        self.api_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=8)
        
        self.api_tree.heading("名称", text="配置名称")
        self.api_tree.heading("API地址", text="API地址")
        self.api_tree.heading("模型", text="模型")
        self.api_tree.heading("默认", text="默认")
        
        self.api_tree.column("名称", width=120)
        self.api_tree.column("API地址", width=300)
        self.api_tree.column("模型", width=150)
        self.api_tree.column("默认", width=60)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.api_tree.yview)
        self.api_tree.configure(yscrollcommand=scrollbar.set)
        
        self.api_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.api_tree.bind("<Double-1>", self._set_default_api)

        # 保存路径
        path_frame = ttk.LabelFrame(self.settings_frame, text="输出设置", 
                                    padding=15, style='Card.TLabelframe')
        path_frame.pack(fill=tk.X, padx=20, pady=10)
        
        path_input_frame = ttk.Frame(path_frame)
        path_input_frame.pack(fill=tk.X)
        
        tk.Label(path_input_frame, text="保存路径：", bg=self.colors['card'],
                fg=self.colors['text'], font=("微软雅黑", 10)).grid(row=0, column=0, sticky=tk.W)
        self.path_entry = ttk.Entry(path_input_frame, font=("微软雅黑", 10), width=60)
        self.path_entry.grid(row=0, column=1, padx=10)
        self.path_entry.insert(0, self.config.get('save_path', './output/infographics'))
        
        tk.Button(path_input_frame, text="浏览", command=self._browse_folder,
                 font=("微软雅黑", 9), bg=self.colors['card'],
                 relief='solid', bd=1, padx=10, pady=5, cursor='hand2').grid(row=0, column=2)

        # 底部固定保存按钮
        save_btn_frame = tk.Frame(path_frame, bg=self.colors['card'])
        save_btn_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(15, 0))
        
        tk.Button(save_btn_frame, text="💾 保存路径设置", command=self._save_path_settings,
                 font=("微软雅黑", 11, "bold"), bg=self.colors['secondary'],
                 fg='white', relief='flat', padx=30, pady=12, cursor='hand2').pack(fill=tk.X, padx=10)
        
        self._load_api_presets()

    def _update_style_desc(self):
        style_key = self.style_var.get()
        desc = self.config.get_style_categories().get(style_key, "")
        self.style_desc_label.config(text=f"风格描述：{desc}")

    def _update_ratio_desc(self):
        ratio_key = self.ratio_var.get()
        desc = self.config.get_ratio_presets().get(ratio_key, "")
        resolution = self.config.get_resolution_by_ratio(ratio_key)
        self.ratio_desc_label.config(text=f"{desc} - {resolution}")

    def _generate_prompt_only(self):
        mode = self.prompt_mode.get()
        
        try:
            if mode == "simple":
                # 简易模式
                style_key = self.style_var.get()
                ratio = self.ratio_var.get()
                content = self.content_text.get("1.0", tk.END).strip()
                usage_scene = self.scene_entry.get().strip() or "通用场景"

                if not content:
                    messagebox.showerror("错误", "请输入核心内容！")
                    return

                prompt = self.prompt_gen.generate(style_key, ratio, content, usage_scene)
                self.history.add_prompt(prompt, style_key, ratio, content)
            else:
                # 专业模式
                purpose = self.purpose_var.get()
                content = self.adv_content_text.get("1.0", tk.END).strip()
                ratio = self.adv_ratio_var.get()
                image_size = self.image_size_var.get()
                
                if not content:
                    messagebox.showerror("错误", "请输入核心内容描述！")
                    return
                
                # 收集额外参数
                additional_params = {}
                shot_type = None
                lighting = None
                art_style = None
                
                if purpose == "逼真场景摄影":
                    shot_type = self.shot_type_var.get()
                    lighting = self.lighting_var.get()
                    additional_params = {
                        'subject': '场景',
                        'mood': '专业',
                        'camera_details': '专业相机',
                        'key_details': '清晰细节'
                    }
                elif purpose in ["风格化插画贴纸", "信息图表数据可视化"]:
                    art_style = self.art_style_var.get()
                    additional_params = {
                        'subject': '主体',
                        'line_style': '清晰线条',
                        'color_palette': '鲜艳配色',
                        'background_type': 'transparent'
                    } if purpose == "风格化插画贴纸" else {
                        'key_elements': '数据点',
                        'visual_style': '清晰多彩',
                        'target_audience': '普通受众'
                    }
                
                prompt = self.prompt_gen.generate_advanced(
                    purpose=purpose,
                    content=content,
                    ratio=ratio,
                    image_size=image_size,
                    shot_type=shot_type,
                    lighting=lighting,
                    art_style=art_style,
                    additional_params=additional_params
                )
                self.history.add_prompt(prompt, purpose, ratio, content)
            
            self.prompt_display.delete("1.0", tk.END)
            self.prompt_display.insert(tk.END, prompt)
            self.image_prompt_text.delete("1.0", tk.END)
            self.image_prompt_text.insert(tk.END, prompt)
            
            messagebox.showinfo("成功", "提示词已生成！")
        except Exception as e:
            messagebox.showerror("失败", f"生成出错：{str(e)}")
    
    def _save_to_library(self):
        """保存当前提示词到提示词库"""
        prompt = self.prompt_display.get("1.0", tk.END).strip()
        if not prompt:
            messagebox.showwarning("提示", "请先生成提示词！")
            return
        
        # 简单对话框获取标题和分类
        dialog = tk.Toplevel(self.root)
        dialog.title("保存到提示词库")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 居中显示
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - 400) // 2
        y = (dialog.winfo_screenheight() - 200) // 2
        dialog.geometry(f"400x200+{x}+{y}")
        
        tk.Label(dialog, text="提示词标题：", font=("微软雅黑", 10)).pack(pady=(20, 5))
        title_entry = ttk.Entry(dialog, font=("微软雅黑", 10))
        title_entry.pack(fill=tk.X, padx=20)
        title_entry.insert(0, "新提示词")
        
        tk.Label(dialog, text="选择分类：", font=("微软雅黑", 10)).pack(pady=(10, 5))
        category_var = tk.StringVar()
        categories = [cat['name'] for cat in self.prompt_library.get_all_categories()]
        if not categories:
            categories = ["默认分类"]
            self.prompt_library.add_category("默认分类", "默认分类")
        
        category_combo = ttk.Combobox(dialog, textvariable=category_var, 
                                     values=categories, state="readonly",
                                     font=("微软雅黑", 10))
        category_combo.pack(fill=tk.X, padx=20, pady=5)
        if categories:
            category_combo.current(0)
        
        def save():
            title = title_entry.get().strip()
            category = category_var.get()
            if not title:
                messagebox.showerror("错误", "请输入标题！", parent=dialog)
                return
            if not category:
                messagebox.showerror("错误", "请选择分类！", parent=dialog)
                return
            
            # 查找分类ID
            cat_id = None
            for cat in self.prompt_library.get_all_categories():
                if cat['name'] == category:
                    cat_id = cat['id']
                    break
            
            if cat_id is None:
                messagebox.showerror("错误", "分类不存在！", parent=dialog)
                return
            
            self.prompt_library.add_prompt(cat_id, title, prompt)
            messagebox.showinfo("成功", "已保存到提示词库！", parent=dialog)
            dialog.destroy()
            # 刷新提示词库页面
            if hasattr(self, '_load_library_categories'):
                self._load_library_categories()
        
        tk.Button(dialog, text="保存", command=save, font=("微软雅黑", 10, "bold"),
                 bg=self.colors['primary'], fg='white', relief='flat',
                 padx=20, pady=8, cursor='hand2').pack(pady=20)

    def _copy_prompt(self):
        prompt = self.prompt_display.get("1.0", tk.END).strip()
        if prompt:
            self.root.clipboard_clear()
            self.root.clipboard_append(prompt)
            messagebox.showinfo("成功", "提示词已复制到剪贴板！")
        else:
            messagebox.showwarning("提示", "请先生成提示词！")

    def _generate_image(self):
        default_preset = self.config.get_default_api_preset()
        if not default_preset or not default_preset.get("api_key"):
            messagebox.showerror("错误", "未配置API！\n请先在【API设置】中添加并配置API。")
            self.notebook.select(3)
            return

        try:
            self.image_gen = ImageGenerator(self.config, default_preset)
        except Exception as e:
            messagebox.showerror("错误", f"初始化API失败：{str(e)}")
            self.notebook.select(3)
            return

        prompt = self.image_prompt_text.get("1.0", tk.END).strip()
        if not prompt:
            messagebox.showerror("错误", "请输入提示词！")
            return
        
        # 添加确认弹框
        if not messagebox.askyesno("确认生成", f"将使用 [{default_preset['name']}] 生成图片\n\n是否继续？"):
            return

        # 在后台线程执行生成
        import threading
        
        def generate_in_background():
            try:
                # 如果有参考图片，使用参考图片生成方法
                if self.reference_images:
                    # 获取参考方式
                    ref_mode = self.ref_mode_var.get() if hasattr(self, 'ref_mode_var') else "full"
                    # 提取所有图片对象
                    ref_image_objs = [ref['obj'] for ref in self.reference_images]
                    save_path = self.image_gen.generate_with_reference(prompt, ref_image_objs, ref_mode)
                else:
                    save_path = self.image_gen.generate(prompt)
                
                # 在主线程更新UI
                self.root.after(0, lambda: self._on_generate_success(save_path, prompt))
                
            except Exception as e:
                # 在主线程显示错误
                self.root.after(0, lambda: self._on_generate_error(str(e)))
        
        # 禁用按钮并显示进度
        self.generate_image_btn.config(state=tk.DISABLED)
        if self.reference_images:
            self.progress_label.config(text=f"🔄 正在使用 {len(self.reference_images)} 张参考图片和 [{default_preset['name']}] 生成图片...")
        else:
            self.progress_label.config(text=f"🔄 正在使用 [{default_preset['name']}] 生成图片...")
        
        # 启动后台线程
        thread = threading.Thread(target=generate_in_background, daemon=True)
        thread.start()
    
    def _on_generate_success(self, save_path, prompt):
        """生成成功的回调（在主线程执行）"""
        if self.reference_images:
            self.progress_label.config(text=f"✅ 基于 {len(self.reference_images)} 张参考图片生成成功！{save_path}")
            self.logger.success(f"图片生成成功 (基于 {len(self.reference_images)} 张参考图片): {save_path}")
        else:
            self.progress_label.config(text=f"✅ 生成成功！{save_path}")
            self.logger.success(f"图片生成成功: {save_path}")
        
        self.current_image_path = save_path
        self._display_image(save_path)
        self.save_image_btn.config(state=tk.NORMAL)
        self.open_image_btn.config(state=tk.NORMAL)
        self.show_in_folder_btn.config(state=tk.NORMAL)
        
        style = self.style_var.get() if hasattr(self, 'style_var') and self.style_var.get() else "自定义"
        ratio = self.ratio_var.get() if hasattr(self, 'ratio_var') and self.ratio_var.get() else "未知"
        self.history.add_image(prompt, save_path, style, ratio)
        
        # 刷新历史记录显示
        self._load_image_history()
        
        self.generate_image_btn.config(state=tk.NORMAL)
    
    def _on_generate_error(self, error_msg):
        """生成失败的回调（在主线程执行）"""
        self.progress_label.config(text=f"❌ 生成失败：{error_msg}")
        self.logger.error(f"图片生成失败: {error_msg}")
        messagebox.showerror("失败", f"生成出错：{error_msg}")
        self.generate_image_btn.config(state=tk.NORMAL)

    def _display_image(self, image_path):
        try:
            # 保存图片路径，用于窗口大小改变时重新显示
            self.current_image_path = image_path
            
            img = Image.open(image_path)
            
            # 强制更新窗口以获取正确的画布尺寸
            self.image_canvas.update_idletasks()
            
            # 获取画布尺寸
            canvas_width = self.image_canvas.winfo_width()
            canvas_height = self.image_canvas.winfo_height()
            
            # 如果画布尺寸还未初始化，使用默认值
            if canvas_width <= 1:
                canvas_width = 600
                canvas_height = 500
            
            # 计算缩放比例（保持宽高比，留出边距）
            img_width, img_height = img.size
            scale_w = (canvas_width - 40) / img_width
            scale_h = (canvas_height - 40) / img_height
            scale = min(scale_w, scale_h)  # 移除1.0限制，允许放大
            
            # 缩放图片
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            
            if new_width > 0 and new_height > 0:
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            self.current_photo = ImageTk.PhotoImage(img)
            self.image_canvas.delete("all")
            # 在画布中心显示图片
            self.image_canvas.create_image(canvas_width // 2, canvas_height // 2, 
                                          image=self.current_photo, anchor=tk.CENTER)
        except Exception as e:
            messagebox.showerror("错误", f"无法显示图片：{str(e)}")

    def _on_canvas_resize(self, event):
        """画布大小改变时重新调整图片显示"""
        # 如果有当前图片，重新显示以适应新尺寸
        if hasattr(self, 'current_image_path') and self.current_image_path:
            # 使用after延迟执行，避免频繁调整
            if hasattr(self, '_resize_after_id'):
                self.root.after_cancel(self._resize_after_id)
            self._resize_after_id = self.root.after(100, lambda: self._display_image(self.current_image_path))

    def _select_reference_image(self):
        """选择参考图片（支持多选）"""
        from tkinter import filedialog
        from PIL import Image
        
        # 检查当前模型是否支持参考图片
        if self.image_gen:
            model = self.image_gen.model.lower()
            if "nano-banana" in model or "dall-e" in model or "dalle" in model:
                result = messagebox.askyesno(
                    "模型兼容性提示",
                    f"当前模型 [{self.image_gen.model}] 不支持参考图片功能。\n\n"
                    "建议使用 Gemini 系列模型（如 gemini-3-pro-image-preview）以获得最佳效果。\n\n"
                    "是否继续上传？（系统将仅使用提示词生成）"
                )
                if not result:
                    return
        
        # 支持多选
        file_paths = filedialog.askopenfilenames(
            title="选择参考图片（可多选）",
            filetypes=[("图片文件", "*.png *.jpg *.jpeg *.gif *.bmp"), ("所有文件", "*.*")]
        )
        
        if file_paths:
            try:
                for file_path in file_paths:
                    # 检查是否已添加
                    if any(ref['path'] == file_path for ref in self.reference_images):
                        continue
                    
                    # 加载图片
                    img = Image.open(file_path)
                    
                    # 添加到列表
                    self.reference_images.append({
                        'path': file_path,
                        'obj': img
                    })
                
                # 更新显示
                self._update_reference_display()
                
            except Exception as e:
                messagebox.showerror("错误", f"加载图片失败：{str(e)}")
                
    def _update_reference_display(self):
        """更新参考图片显示"""
        if not self.reference_images:
            self.ref_image_label.config(text="未选择参考图片（支持多张）", fg=self.colors['text_light'])
            self.ref_preview_frame.pack_forget()
            if hasattr(self, 'ref_mode_frame_widget'):
                self.ref_mode_frame_widget.pack_forget()
            return
        
        # 更新标签
        count = len(self.reference_images)
        total_size = sum(ref['obj'].size[0] * ref['obj'].size[1] for ref in self.reference_images)
        self.ref_image_label.config(
            text=f"✅ 已添加 {count} 张参考图片",
            fg=self.colors['secondary']
        )
        
        # 清空并重新创建缩略图
        for widget in self.ref_thumbnails_container.winfo_children():
            widget.destroy()
        
        # 显示所有缩略图
        for idx, ref in enumerate(self.reference_images):
            self._add_thumbnail(ref, idx)
        
        # 显示预览区域和参考方式选择器
        self.ref_preview_frame.pack(fill=tk.X, pady=(5, 0))
        if hasattr(self, 'ref_mode_frame_widget'):
            self.ref_mode_frame_widget.pack(fill=tk.X, pady=(5, 0))
    
    def _add_thumbnail(self, ref_data, index):
        """添加单个缩略图"""
        from PIL import Image, ImageTk
        
        # 创建缩略图容器
        thumb_frame = tk.Frame(self.ref_thumbnails_container, bg='white', 
                              relief='solid', bd=1)
        thumb_frame.pack(side=tk.LEFT, padx=5, pady=5)
        
        # 创建缩略图（最大100x100）
        img = ref_data['obj']
        max_size = 100
        img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        
        # 图片标签
        img_label = tk.Label(thumb_frame, image=photo, bg='white')
        img_label.image = photo  # 保持引用
        img_label.pack()
        
        # 文件名和删除按钮
        info_frame = tk.Frame(thumb_frame, bg='white')
        info_frame.pack(fill=tk.X, padx=2, pady=2)
        
        filename = os.path.basename(ref_data['path'])
        if len(filename) > 12:
            filename = filename[:9] + "..."
        
        tk.Label(info_frame, text=filename, bg='white', 
                font=("微软雅黑", 7), fg=self.colors['text']).pack(side=tk.LEFT)
        
        del_btn = tk.Button(info_frame, text="✕", bg='#FFE5E5', fg='#D32F2F',
                           font=("微软雅黑", 8, "bold"), relief='flat',
                           command=lambda: self._remove_reference(index),
                           cursor='hand2', padx=3, pady=0)
        del_btn.pack(side=tk.RIGHT)
    
    def _remove_reference(self, index):
        """删除指定索引的参考图片"""
        if 0 <= index < len(self.reference_images):
            filename = os.path.basename(self.reference_images[index]['path'])
            if messagebox.askyesno("确认删除", f"确定要删除参考图片\n{filename}\n吗？"):
                self.reference_images.pop(index)
                self._update_reference_display()
    
    def _clear_reference_image(self):
        """清除所有参考图片"""
        if not self.reference_images:
            return
        
        count = len(self.reference_images)
        if messagebox.askyesno("确认清除", f"确定要清除所有 {count} 张参考图片吗？"):
            self.reference_images = []
            self._update_reference_display()
    
    def _show_reference_thumbnail(self, img):
        """显示参考图片缩略图（已废弃，使用_update_reference_display）"""
        pass
    
    def _save_image(self):
        if not self.current_image_path:
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG图片", "*.png"), ("所有文件", "*.*")]
        )
        
        if file_path:
            try:
                import shutil
                shutil.copy2(self.current_image_path, file_path)
                self.logger.success(f"图片已保存: {file_path}")
                messagebox.showinfo("成功", f"图片已保存到：{file_path}")
            except Exception as e:
                self.logger.error(f"保存图片失败: {str(e)}")
                messagebox.showerror("错误", f"保存失败：{str(e)}")
    
    def _open_image(self):
        """使用默认程序打开图片"""
        if not self.current_image_path or not os.path.exists(self.current_image_path):
            messagebox.showwarning("提示", "图片文件不存在！")
            return
        
        try:
            import subprocess
            import platform
            
            system = platform.system()
            if system == 'Windows':
                os.startfile(self.current_image_path)
            elif system == 'Darwin':  # macOS
                subprocess.run(['open', self.current_image_path])
            else:  # Linux
                subprocess.run(['xdg-open', self.current_image_path])
        except Exception as e:
            messagebox.showerror("错误", f"打开失败：{str(e)}")
    
    def _show_in_folder(self):
        """在文件夹中显示图片"""
        if not self.current_image_path or not os.path.exists(self.current_image_path):
            messagebox.showwarning("提示", "图片文件不存在！")
            return
        
        try:
            import subprocess
            import platform
            
            system = platform.system()
            if system == 'Windows':
                subprocess.run(['explorer', '/select,', os.path.abspath(self.current_image_path)])
            elif system == 'Darwin':  # macOS
                subprocess.run(['open', '-R', self.current_image_path])
            else:  # Linux
                # 打开包含文件的目录
                folder_path = os.path.dirname(os.path.abspath(self.current_image_path))
                subprocess.run(['xdg-open', folder_path])
        except Exception as e:
            messagebox.showerror("错误", f"打开失败：{str(e)}")

    def _load_prompt_history(self):
        for item in self.prompt_tree.get_children():
            self.prompt_tree.delete(item)
        
        records = self.history.get_prompt_history()
        for record in records:
            self.prompt_tree.insert("", tk.END, values=(
                record["timestamp"],
                record["style"],
                record["ratio"],
                record["content"]
            ), tags=(record["id"],))

    def _load_image_history(self):
        for item in self.image_tree.get_children():
            self.image_tree.delete(item)
        
        records = self.history.get_image_history()
        for record in records:
            status = "✅ 存在" if record["exists"] else "❌ 已删除"
            self.image_tree.insert("", tk.END, values=(
                record["timestamp"],
                record["style"],
                record["ratio"],
                record["image_path"],
                status
            ), tags=(record["id"],))

    def _refresh_history(self):
        self._load_prompt_history()
        self._load_image_history()
        messagebox.showinfo("提示", "历史记录已刷新")

    def _clear_history(self):
        if messagebox.askyesno("确认", "确定要清空所有历史记录吗？\n\n此操作不可恢复！"):
            self.history.clear_all()
            self._load_prompt_history()
            self._load_image_history()

    def _show_prompt_menu(self, event):
        item = self.prompt_tree.identify_row(event.y)
        if item:
            self.prompt_tree.selection_set(item)
            self.prompt_menu.post(event.x_root, event.y_root)

    def _show_image_menu(self, event):
        item = self.image_tree.identify_row(event.y)
        if item:
            self.image_tree.selection_set(item)
            self.image_menu.post(event.x_root, event.y_root)

    def _show_prompt_detail(self, event):
        selection = self.prompt_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        record_id = int(self.prompt_tree.item(item, "tags")[0])
        records = self.history.get_prompt_history()
        record = next((r for r in records if r["id"] == record_id), None)
        if not record:
            return
        
        detail_window = tk.Toplevel(self.root)
        detail_window.title("提示词详情")
        detail_window.geometry("700x500")
        
        info_frame = ttk.Frame(detail_window, padding=20)
        info_frame.pack(fill=tk.X)
        
        ttk.Label(info_frame, text=f"时间: {record['timestamp']}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"风格: {record['style']}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"比例: {record['ratio']}").pack(anchor=tk.W)
        
        prompt_text = scrolledtext.ScrolledText(detail_window, height=15, wrap=tk.WORD)
        prompt_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        prompt_text.insert(tk.END, record["prompt"])
        prompt_text.config(state=tk.DISABLED)
        
        # 底部按钮
        btn_frame = ttk.Frame(detail_window)
        btn_frame.pack(pady=10)
        
        def copy_prompt():
            self.root.clipboard_clear()
            self.root.clipboard_append(record["prompt"])
            messagebox.showinfo("成功", "提示词已复制到剪贴板")
        
        ttk.Button(btn_frame, text="📋 复制提示词", command=copy_prompt).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="关闭", command=detail_window.destroy).pack(side=tk.LEFT, padx=5)

    def _copy_prompt_to_page(self):
        selection = self.prompt_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        record_id = int(self.prompt_tree.item(item, "tags")[0])
        records = self.history.get_prompt_history()
        record = next((r for r in records if r["id"] == record_id), None)
        if not record:
            return
        
        self.image_prompt_text.delete("1.0", tk.END)
        self.image_prompt_text.insert(tk.END, record["prompt"])
        self.notebook.select(1)
        messagebox.showinfo("成功", "提示词已复制")

    def _delete_prompt_record(self):
        selection = self.prompt_tree.selection()
        if selection:
            if messagebox.askyesno("确认删除", "确定要删除此提示词历史记录吗？\n\n此操作不可恢复！"):
                item = selection[0]
                record_id = int(self.prompt_tree.item(item, "tags")[0])
                self.history.delete_prompt(record_id)
                self._load_prompt_history()
                messagebox.showinfo("成功", "历史记录已删除")

    def _open_image_from_history(self, event):
        selection = self.image_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        record_id = int(self.image_tree.item(item, "tags")[0])
        records = self.history.get_image_history()
        record = next((r for r in records if r["id"] == record_id), None)
        if not record or not record["exists"]:
            messagebox.showerror("错误", "图片文件不存在")
            return
        
        os.startfile(record["image_path"])

    def _show_image_prompt(self):
        selection = self.image_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        record_id = int(self.image_tree.item(item, "tags")[0])
        records = self.history.get_image_history()
        record = next((r for r in records if r["id"] == record_id), None)
        if record:
            messagebox.showinfo("提示词", record["prompt"])

    def _show_in_folder(self):
        selection = self.image_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        record_id = int(self.image_tree.item(item, "tags")[0])
        records = self.history.get_image_history()
        record = next((r for r in records if r["id"] == record_id), None)
        if not record or not record["exists"]:
            messagebox.showerror("错误", "图片文件不存在")
            return
        
        import subprocess
        subprocess.run(["explorer", "/select,", os.path.abspath(record["image_path"])])

    def _delete_image_record(self):
        selection = self.image_tree.selection()
        if selection:
            if messagebox.askyesno("确认删除", "确定要删除此图片历史记录吗？\n\n注意：只删除记录，不删除图片文件\n\n此操作不可恢复！"):
                item = selection[0]
                record_id = int(self.image_tree.item(item, "tags")[0])
                self.history.delete_image(record_id)
                self._load_image_history()
                messagebox.showinfo("成功", "历史记录已删除")

    def _load_api_presets(self):
        for item in self.api_tree.get_children():
            self.api_tree.delete(item)
        
        presets = self.config.get_api_presets()
        for i, preset in enumerate(presets):
            default_mark = "✓" if preset.get("is_default", False) else ""
            self.api_tree.insert("", tk.END, values=(
                preset["name"],
                preset["api_url"],
                preset["model"],
                default_mark
            ), tags=(i,))

    def _add_api_preset(self):
        self._show_api_preset_dialog()

    def _edit_api_preset(self):
        selection = self.api_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请先选择API配置")
            return
        
        item = selection[0]
        index = int(self.api_tree.item(item, "tags")[0])
        presets = self.config.get_api_presets()
        if index < len(presets):
            self._show_api_preset_dialog(presets[index], index)

    def _delete_api_preset(self):
        selection = self.api_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请先选择API配置")
            return
        
        if messagebox.askyesno("确认", "确定要删除此API配置吗？\n\n此操作不可恢复！"):
            item = selection[0]
            index = int(self.api_tree.item(item, "tags")[0])
            self.config.delete_api_preset(index)
            self._load_api_presets()

    def _set_default_api(self, event):
        selection = self.api_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        index = int(self.api_tree.item(item, "tags")[0])
        self.config.set_default_api(index)
        self._load_api_presets()
        
        # 刷新图片编辑页面的模型状态
        if hasattr(self, '_update_edit_model_status'):
            self._update_edit_model_status()
        
        try:
            default_preset = self.config.get_default_api_preset()
            if default_preset and default_preset.get("api_key"):
                self.image_gen = ImageGenerator(self.config, default_preset)
        except:
            pass

    def _show_api_preset_dialog(self, preset=None, index=None):
        dialog = tk.Toplevel(self.root)
        dialog.title("编辑API配置" if preset else "添加API配置")
        dialog.geometry("600x400")
        dialog.transient(self.root)
        dialog.grab_set()

        content_frame = ttk.Frame(dialog, padding=20)
        content_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(content_frame, text="配置名称：").grid(row=0, column=0, sticky=tk.W, pady=10)
        name_entry = ttk.Entry(content_frame, width=50)
        name_entry.grid(row=0, column=1, sticky=tk.W, pady=10, padx=10)
        if preset:
            name_entry.insert(0, preset["name"])

        ttk.Label(content_frame, text="API 密钥：").grid(row=1, column=0, sticky=tk.W, pady=10)
        key_entry = ttk.Entry(content_frame, width=50, show="*")
        key_entry.grid(row=1, column=1, sticky=tk.W, pady=10, padx=10)
        if preset:
            key_entry.insert(0, preset["api_key"])
        
        def toggle_key():
            if key_entry.cget('show') == '*':
                key_entry.config(show='')
                show_btn.config(text="🔒")
            else:
                key_entry.config(show='*')
                show_btn.config(text="👁")
        
        show_btn = ttk.Button(content_frame, text="👁", command=toggle_key, width=3)
        show_btn.grid(row=1, column=2, pady=10)

        ttk.Label(content_frame, text="API 地址：").grid(row=2, column=0, sticky=tk.W, pady=10)
        url_entry = ttk.Entry(content_frame, width=50)
        url_entry.grid(row=2, column=1, sticky=tk.W, pady=10, padx=10)
        if preset:
            url_entry.insert(0, preset["api_url"])
        else:
            url_entry.insert(0, "https://generativelanguage.googleapis.com")

        ttk.Label(content_frame, text="模型名称：").grid(row=3, column=0, sticky=tk.W, pady=10)
        model_entry = ttk.Entry(content_frame, width=50)
        model_entry.grid(row=3, column=1, sticky=tk.W, pady=10, padx=10)
        if preset:
            model_entry.insert(0, preset["model"])
        else:
            model_entry.insert(0, "gemini-2.0-flash-exp")

        # 设为默认选项
        is_default_var = tk.BooleanVar()
        if preset:
            is_default_var.set(preset.get("is_default", False))
        else:
            is_default_var.set(True)  # 新添加的API默认设为默认
        
        default_check = ttk.Checkbutton(content_frame, text="设为默认API", variable=is_default_var)
        default_check.grid(row=4, column=1, sticky=tk.W, pady=10, padx=10)

        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=20)

        def save_preset():
            name = name_entry.get().strip()
            api_key = key_entry.get().strip()
            api_url = url_entry.get().strip()
            model = model_entry.get().strip()

            if not all([name, api_key, api_url, model]):
                messagebox.showerror("错误", "请填写完整信息！")
                return

            if index is not None:
                self.config.update_api_preset(index, name, api_key, api_url, model)
                if is_default_var.get():
                    self.config.set_default_api(index)
            else:
                self.config.add_api_preset(name, api_key, api_url, model)
                if is_default_var.get():
                    # 新添加的API，设为最后一个索引
                    presets = self.config.get_api_presets()
                    self.config.set_default_api(len(presets) - 1)

            self._load_api_presets()
            dialog.destroy()
            messagebox.showinfo("成功", "API配置已保存")

        ttk.Button(btn_frame, text="💾 保存", command=save_preset).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def _browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, folder)

    def _save_path_settings(self):
        new_path = self.path_entry.get().strip()
        if new_path:
            self.config.update('save_path', new_path)
            messagebox.showinfo("成功", "保存路径已更新")

    # ============ 提示词库相关方法 ============
    
    def _load_categories(self):
        """加载分类列表"""
        self.category_listbox.delete(0, tk.END)
        categories = self.prompt_library.get_categories()
        for category in categories:
            self.category_listbox.insert(tk.END, f"{category['name']} ({len(category['prompts'])})")
        
        if categories:
            self.category_listbox.select_set(0)
            self._on_category_select(None)
    
    def _on_category_select(self, event):
        """分类选择事件"""
        selection = self.category_listbox.curselection()
        if not selection:
            return
        
        category_index = selection[0]
        categories = self.prompt_library.get_categories()
        if category_index < len(categories):
            category = categories[category_index]
            self._load_prompts(category['id'])
    
    def _load_prompts(self, category_id):
        """加载指定分类的提示词"""
        for item in self.library_tree.get_children():
            self.library_tree.delete(item)
        
        # 获取分类名称
        category = self.prompt_library.get_category_by_id(category_id)
        category_name = category['name'] if category else "未知"
        
        prompts = self.prompt_library.get_prompts_by_category(category_id)
        for prompt in prompts:
            self.library_tree.insert("", tk.END, values=(
                category_name,
                prompt['title'],
                prompt.get('tags', ''),
                prompt.get('style', ''),
                prompt.get('ratio', ''),
                prompt.get('updated_at', '')
            ), tags=(category_id, prompt['id']))
    
    def _add_category(self):
        """添加分类"""
        dialog = tk.Toplevel(self.root)
        dialog.title("添加分类")
        dialog.geometry("500x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 内容区域
        content_frame = ttk.Frame(dialog, padding=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(content_frame, text="分类名称：").grid(row=0, column=0, sticky=tk.W, pady=10)
        name_entry = ttk.Entry(content_frame, width=40, font=("微软雅黑", 10))
        name_entry.grid(row=0, column=1, sticky=tk.W, pady=10, padx=10)
        
        ttk.Label(content_frame, text="分类描述：").grid(row=1, column=0, sticky=tk.NW, pady=10)
        desc_text = scrolledtext.ScrolledText(content_frame, width=40, height=5, font=("微软雅黑", 10))
        desc_text.grid(row=1, column=1, sticky=tk.W, pady=10, padx=10)
        
        def save():
            name = name_entry.get().strip()
            desc = desc_text.get("1.0", tk.END).strip()
            
            if not name:
                messagebox.showerror("错误", "请输入分类名称！")
                return
            
            self.prompt_library.add_category(name, desc)
            self._load_categories()
            dialog.destroy()
            self.logger.info(f"添加分类: {name}")
            messagebox.showinfo("成功", "分类已添加")
        
        # 按钮区域（固定在底部）
        btn_frame = tk.Frame(dialog, bg='white')
        btn_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=10)
        
        tk.Button(btn_frame, text="保存", command=save, font=("微软雅黑", 10),
                 bg=self.colors['primary'], fg='white', relief='flat',
                 padx=20, pady=8, cursor='hand2').pack(side=tk.LEFT, padx=(150, 5))
        tk.Button(btn_frame, text="取消", command=dialog.destroy, font=("微软雅黑", 10),
                 relief='solid', bd=1, padx=20, pady=8, cursor='hand2').pack(side=tk.LEFT, padx=5)
    
    def _edit_category(self):
        """编辑分类"""
        selection = self.category_listbox.curselection()
        if not selection:
            messagebox.showwarning("提示", "请先选择分类")
            return
        
        category_index = selection[0]
        categories = self.prompt_library.get_categories()
        category = categories[category_index]
        
        dialog = tk.Toplevel(self.root)
        dialog.title("编辑分类")
        dialog.geometry("500x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 内容区域
        content_frame = ttk.Frame(dialog, padding=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(content_frame, text="分类名称：").grid(row=0, column=0, sticky=tk.W, pady=10)
        name_entry = ttk.Entry(content_frame, width=40, font=("微软雅黑", 10))
        name_entry.grid(row=0, column=1, sticky=tk.W, pady=10, padx=10)
        name_entry.insert(0, category['name'])
        
        ttk.Label(content_frame, text="分类描述：").grid(row=1, column=0, sticky=tk.NW, pady=10)
        desc_text = scrolledtext.ScrolledText(content_frame, width=40, height=5, font=("微软雅黑", 10))
        desc_text.grid(row=1, column=1, sticky=tk.W, pady=10, padx=10)
        desc_text.insert("1.0", category.get('description', ''))
        
        def save():
            name = name_entry.get().strip()
            desc = desc_text.get("1.0", tk.END).strip()
            
            if not name:
                messagebox.showerror("错误", "请输入分类名称！")
                return
            
            self.prompt_library.update_category(category['id'], name, desc)
            self._load_categories()
            dialog.destroy()
            self.logger.info(f"更新分类: {name}")
            messagebox.showinfo("成功", "分类已更新")
        
        # 按钮区域（固定在底部）
        btn_frame = tk.Frame(dialog, bg='white')
        btn_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=10)
        
        tk.Button(btn_frame, text="保存", command=save, font=("微软雅黑", 10),
                 bg=self.colors['primary'], fg='white', relief='flat',
                 padx=20, pady=8, cursor='hand2').pack(side=tk.LEFT, padx=(150, 5))
        tk.Button(btn_frame, text="取消", command=dialog.destroy, font=("微软雅黑", 10),
                 relief='solid', bd=1, padx=20, pady=8, cursor='hand2').pack(side=tk.LEFT, padx=5)
    
    def _delete_category(self):
        """删除分类"""
        selection = self.category_listbox.curselection()
        if not selection:
            messagebox.showwarning("提示", "请先选择分类")
            return
        
        category_index = selection[0]
        categories = self.prompt_library.get_categories()
        category = categories[category_index]
        
        prompt_count = len(category.get('prompts', []))
        msg = f"确定要删除分类「{category['name']}」吗？\n\n"
        if prompt_count > 0:
            msg += f"该分类下有 {prompt_count} 条提示词，也将被一并删除！\n\n"
        msg += "此操作不可恢复！"
        
        if messagebox.askyesno("确认删除", msg):
            self.prompt_library.delete_category(category['id'])
            self._load_categories()
            self.logger.warning(f"删除分类: {category['name']}")
            messagebox.showinfo("成功", "分类已删除")
    
    def _add_prompt_to_library(self):
        """添加提示词到库"""
        selection = self.category_listbox.curselection()
        if not selection:
            messagebox.showwarning("提示", "请先选择分类")
            return
        
        category_index = selection[0]
        categories = self.prompt_library.get_categories()
        category = categories[category_index]
        
        self._show_prompt_editor_dialog(category['id'])
    
    def _edit_prompt_in_library(self):
        """编辑库中的提示词"""
        selection = self.library_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请先选择提示词")
            return
        
        item = selection[0]
        tags = self.library_tree.item(item, "tags")
        category_id = int(tags[0])
        prompt_id = int(tags[1])
        
        # 获取提示词详情
        prompts = self.prompt_library.get_prompts_by_category(category_id)
        prompt = next((p for p in prompts if p['id'] == prompt_id), None)
        
        if prompt:
            self._show_prompt_editor_dialog(category_id, prompt)
    
    def _delete_prompt_from_library(self):
        """从库中删除提示词"""
        selection = self.library_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请先选择提示词")
            return
        
        item = selection[0]
        tags = self.library_tree.item(item, "tags")
        category_id = int(tags[0])
        prompt_id = int(tags[1])
        
        # 获取提示词标题
        prompts = self.prompt_library.get_prompts_by_category(category_id)
        prompt = next((p for p in prompts if p['id'] == prompt_id), None)
        
        msg = "确定要删除此提示词吗？\n\n"
        if prompt:
            msg += f"标题：{prompt['title']}\n\n"
        msg += "此操作不可恢复！"
        
        if messagebox.askyesno("确认删除", msg):
            self.prompt_library.delete_prompt(category_id, prompt_id)
            self._load_prompts(category_id)
            self._load_categories()  # 更新分类数量
            self.logger.warning(f"删除提示词: {prompt['title'] if prompt else '未知'}")
            messagebox.showinfo("成功", "提示词已删除")
    
    def _show_prompt_editor_dialog(self, category_id, prompt=None):
        """显示提示词编辑对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("编辑提示词" if prompt else "添加提示词")
        dialog.geometry("700x650")
        dialog.transient(self.root)
        dialog.grab_set()
        
        content_frame = ttk.Frame(dialog, padding=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # 分类选择
        ttk.Label(content_frame, text="分类：").grid(row=0, column=0, sticky=tk.W, pady=5)
        categories = self.prompt_library.get_categories()
        category_names = [cat['name'] for cat in categories]
        category_ids = [cat['id'] for cat in categories]
        
        selected_category_var = tk.StringVar()
        category_combo = ttk.Combobox(content_frame, textvariable=selected_category_var,
                                     values=category_names, state="readonly",
                                     font=("微软雅黑", 10), width=57)
        category_combo.grid(row=0, column=1, sticky=tk.W, pady=5, padx=10)
        
        # 设置默认选中的分类
        try:
            current_index = category_ids.index(category_id)
            category_combo.current(current_index)
        except ValueError:
            if category_names:
                category_combo.current(0)
        
        # 标题
        ttk.Label(content_frame, text="标题：").grid(row=1, column=0, sticky=tk.W, pady=5)
        title_entry = ttk.Entry(content_frame, width=60, font=("微软雅黑", 10))
        title_entry.grid(row=1, column=1, sticky=tk.W, pady=5, padx=10)
        if prompt:
            title_entry.insert(0, prompt['title'])
        
        # 标签
        ttk.Label(content_frame, text="标签：").grid(row=2, column=0, sticky=tk.W, pady=5)
        tags_entry = ttk.Entry(content_frame, width=60, font=("微软雅黑", 10))
        tags_entry.grid(row=2, column=1, sticky=tk.W, pady=5, padx=10)
        if prompt:
            tags_entry.insert(0, prompt.get('tags', ''))
        
        # 风格
        ttk.Label(content_frame, text="风格：").grid(row=3, column=0, sticky=tk.W, pady=5)
        style_entry = ttk.Entry(content_frame, width=60, font=("微软雅黑", 10))
        style_entry.grid(row=3, column=1, sticky=tk.W, pady=5, padx=10)
        if prompt:
            style_entry.insert(0, prompt.get('style', ''))
        
        # 比例
        ttk.Label(content_frame, text="比例：").grid(row=4, column=0, sticky=tk.W, pady=5)
        ratio_entry = ttk.Entry(content_frame, width=60, font=("微软雅黑", 10))
        ratio_entry.grid(row=4, column=1, sticky=tk.W, pady=5, padx=10)
        if prompt:
            ratio_entry.insert(0, prompt.get('ratio', ''))
        
        # 内容
        ttk.Label(content_frame, text="提示词内容：").grid(row=5, column=0, sticky=tk.NW, pady=5)
        content_text = scrolledtext.ScrolledText(content_frame, width=60, height=13, font=("微软雅黑", 10))
        content_text.grid(row=5, column=1, sticky=tk.W, pady=5, padx=10)
        if prompt:
            content_text.insert("1.0", prompt['content'])
        
        def save():
            # 获取选中的分类
            selected_index = category_combo.current()
            if selected_index < 0:
                messagebox.showerror("错误", "请选择分类！")
                return
            
            target_category_id = category_ids[selected_index]
            
            title = title_entry.get().strip()
            tags = tags_entry.get().strip()
            style = style_entry.get().strip()
            ratio = ratio_entry.get().strip()
            content = content_text.get("1.0", tk.END).strip()
            
            if not title or not content:
                messagebox.showerror("错误", "请填写标题和内容！")
                return
            
            if prompt:
                # 更新 - 如果分类变了，需要移动
                if target_category_id != category_id:
                    # 先删除旧的，再添加到新分类
                    self.prompt_library.delete_prompt(category_id, prompt['id'])
                    self.prompt_library.add_prompt(target_category_id, title, content, tags, style, ratio)
                else:
                    self.prompt_library.update_prompt(category_id, prompt['id'], title, content, tags, style, ratio)
                self.logger.info(f"更新提示词: {title}")
                messagebox.showinfo("成功", "提示词已更新")
            else:
                # 添加到选定的分类
                self.prompt_library.add_prompt(target_category_id, title, content, tags, style, ratio)
                self.logger.info(f"添加提示词: {title}")
                messagebox.showinfo("成功", "提示词已添加")
            
            # 刷新当前分类的列表
            self._load_prompts(target_category_id)
            # 更新分类列表（显示数量变化）
            self._load_categories()
            dialog.destroy()
        
        # 按钮区域（固定在底部）
        btn_frame = tk.Frame(dialog, bg='white')
        btn_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=10)
        
        tk.Button(btn_frame, text="💾 保存", command=save, font=("微软雅黑", 10),
                 bg=self.colors['primary'], fg='white', relief='flat',
                 padx=20, pady=8, cursor='hand2').pack(side=tk.LEFT, padx=(250, 5))
        tk.Button(btn_frame, text="取消", command=dialog.destroy, font=("微软雅黑", 10),
                 relief='solid', bd=1, padx=20, pady=8, cursor='hand2').pack(side=tk.LEFT, padx=5)
    
    def _view_prompt_detail(self, event=None):
        """查看提示词详情"""
        selection = self.library_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        tags = self.library_tree.item(item, "tags")
        category_id = int(tags[0])
        prompt_id = int(tags[1])
        
        prompts = self.prompt_library.get_prompts_by_category(category_id)
        prompt = next((p for p in prompts if p['id'] == prompt_id), None)
        
        if not prompt:
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("提示词详情")
        dialog.geometry("700x500")
        dialog.transient(self.root)
        
        content_frame = ttk.Frame(dialog, padding=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # 显示信息
        info_text = f"""标题：{prompt['title']}
标签：{prompt.get('tags', '')}
风格：{prompt.get('style', '')}
比例：{prompt.get('ratio', '')}
创建时间：{prompt.get('created_at', '')}
更新时间：{prompt.get('updated_at', '')}

提示词内容：
"""
        
        info_label = tk.Text(dialog, height=5, wrap=tk.WORD, font=("微软雅黑", 10))
        info_label.pack(fill=tk.X, padx=20, pady=5)
        info_label.insert("1.0", info_text)
        info_label.config(state=tk.DISABLED)
        
        content_text = scrolledtext.ScrolledText(dialog, wrap=tk.WORD, font=("微软雅黑", 10))
        content_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        content_text.insert("1.0", prompt['content'])
        content_text.config(state=tk.DISABLED)
        
        # 按钮
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        def use_prompt():
            self.image_prompt_text.delete("1.0", tk.END)
            self.image_prompt_text.insert(tk.END, prompt['content'])
            self.notebook.select(1)  # 切换到图片生成页
            dialog.destroy()
            messagebox.showinfo("成功", "提示词已复制到生成页面")
        
        def copy_prompt():
            self.root.clipboard_clear()
            self.root.clipboard_append(prompt['content'])
            messagebox.showinfo("成功", "提示词已复制到剪贴板")
        
        ttk.Button(btn_frame, text="🎨 使用此提示词", command=use_prompt).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📋 复制内容", command=copy_prompt).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="关闭", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def _use_library_prompt(self):
        """使用库中的提示词"""
        selection = self.library_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        tags = self.library_tree.item(item, "tags")
        category_id = int(tags[0])
        prompt_id = int(tags[1])
        
        prompts = self.prompt_library.get_prompts_by_category(category_id)
        prompt = next((p for p in prompts if p['id'] == prompt_id), None)
        
        if prompt:
            self.image_prompt_text.delete("1.0", tk.END)
            self.image_prompt_text.insert(tk.END, prompt['content'])
            self.notebook.select(1)  # 切换到图片生成页
            messagebox.showinfo("成功", "提示词已复制到生成页面")
    
    def _search_prompts(self):
        """搜索提示词"""
        keyword = self.library_search_var.get().strip()
        if not keyword:
            messagebox.showwarning("提示", "请输入搜索关键词")
            return
        
        results = self.prompt_library.search_prompts(keyword)
        
        if not results:
            messagebox.showinfo("搜索结果", "未找到匹配的提示词")
            return
        
        # 清空列表
        for item in self.library_tree.get_children():
            self.library_tree.delete(item)
        
        # 显示搜索结果
        for prompt in results:
            self.library_tree.insert("", tk.END, values=(
                prompt['category_name'],
                prompt['title'],
                prompt.get('tags', ''),
                prompt.get('style', ''),
                prompt.get('ratio', ''),
                prompt.get('updated_at', '')
            ), tags=(prompt['category_id'], prompt['id']))
        
        messagebox.showinfo("搜索结果", f"找到 {len(results)} 条匹配的提示词")
    
    def _show_library_menu(self, event):
        """显示右键菜单"""
        item = self.library_tree.identify_row(event.y)
        if item:
            self.library_tree.selection_set(item)
            self.library_menu.post(event.x_root, event.y_root)
    
    # ==================== 图片编辑功能方法 ====================
    
    def _update_edit_model_status(self):
        """更新图片编辑页面的模型状态显示"""
        default_preset = self.config.get_default_api_preset()
        if default_preset:
            model = default_preset.get('model', '')
            api_name = default_preset.get('name', '')
            
            if 'gemini-3-pro-image' in model.lower():
                status_text = f"✅ 当前模型：{model} ({api_name}) - 完美支持图片编辑"
                fg_color = '#27AE60'
            elif 'gemini' in model.lower() and '2.5' in model:
                status_text = f"✅ 当前模型：{model} ({api_name}) - 支持图片编辑"
                fg_color = '#27AE60'
            elif 'nano-banana' in model.lower():
                status_text = f"⚠️ 当前模型：{model} ({api_name}) - 不支持精确图片编辑，结果可能不可控！建议切换到 gemini-3-pro-image-preview"
                fg_color = '#E74C3C'
            else:
                status_text = f"❓ 当前模型：{model} ({api_name}) - 图片编辑能力未知"
                fg_color = '#F39C12'
            
            self.edit_model_status_label.config(text=status_text, fg=fg_color)
        else:
            self.edit_model_status_label.config(text="⚠️ 未配置API模型", fg='#E74C3C')
    
    def _update_edit_instruction_template(self):
        """根据选择的编辑类型更新提示文本和示例（已禁用以节省空间）"""
        pass
        # 提示文本已移除以节省界面空间
    
    def _select_edit_image(self):
        """选择要编辑的图片"""
        file_path = filedialog.askopenfilename(
            title="选择要编辑的图片",
            filetypes=[("图片文件", "*.png *.jpg *.jpeg *.bmp *.gif"), ("所有文件", "*.*")]
        )
        if file_path:
            # 检查当前使用的模型
            default_preset = self.config.get_default_api_preset()
            if default_preset:
                model = default_preset.get('model', '').lower()
                if 'nano-banana' in model and 'gemini' not in model:
                    response = messagebox.askyesno(
                        "⚠️ 模型警告",
                        f"当前使用的模型是：{default_preset.get('model')}\n\n"
                        "此模型不支持精确的图片编辑功能！\n"
                        "编辑结果可能不可控（如自动添加元素、改变构图等）。\n\n"
                        "推荐使用：gemini-3-pro-image-preview\n\n"
                        "是否继续使用当前模型？",
                        icon='warning'
                    )
                    if not response:
                        messagebox.showinfo("提示", "请前往【API设置】页面切换到支持图片编辑的模型。")
                        return
            
            self.edit_image_path_var.set(file_path)
            self.edit_session['original_image_path'] = file_path
            self.edit_session['current_image_path'] = file_path
            self.logger.info(f"选择编辑图片: {file_path}")
            # self._display_edit_image(file_path)  # 预览功能已移除
            self.edit_apply_btn.config(state=tk.NORMAL)
            
            # 清空对话历史显示
            for widget in self.edit_history_container.winfo_children():
                widget.destroy()
            
            # 添加原始图片到历史
            self._add_to_edit_history("原始图片", file_path, is_user=False)
    
    def _start_new_edit_session(self):
        """开始新的编辑会话"""
        if messagebox.askyesno("确认", "开始新会话将清空当前的编辑历史。\n\n是否继续？"):
            # 保存当前会话到历史
            if self.edit_session.get('chat_history'):
                self.history.save_edit_session(self.edit_session)
            
            # 重置会话数据
            self.edit_session = {
                'chat_history': [],
                'current_image_path': None,
                'original_image_path': None,
                'images': []
            }
            
            # 清空界面
            self.edit_image_path_var.set("")
            self.edit_instruction_text.delete("1.0", tk.END)
            self.edit_progress_label.config(text="")
            self.edit_apply_btn.config(state=tk.DISABLED)
            # self.save_edited_btn.config(state=tk.DISABLED)
            # self.open_edited_btn.config(state=tk.DISABLED)
            # self.show_edited_in_folder_btn.config(state=tk.DISABLED)
            
            # 清空对话历史
            for widget in self.edit_history_container.winfo_children():
                widget.destroy()
            
            # 清空预览
            # self.edit_preview_canvas.delete("all")
            
            self.logger.info("开始新的编辑会话")
            messagebox.showinfo("提示", "新会话已开始，请上传图片开始编辑。")
    
    def _apply_edit_instruction(self):
        """应用编辑指令"""
        instruction = self.edit_instruction_text.get("1.0", tk.END).strip()
        if not instruction:
            messagebox.showerror("错误", "请输入编辑指令！")
            return
        
        if not self.edit_session['current_image_path']:
            messagebox.showerror("错误", "请先上传要编辑的图片！")
            return
        
        # 检查API配置
        default_preset = self.config.get_default_api_preset()
        if not default_preset or not default_preset.get("api_key"):
            messagebox.showerror("错误", "未配置API！\n请先在【API设置】中添加并配置API。")
            return
        
        # 检查是否为Gemini模型（图片编辑需要Gemini）
        model = default_preset.get('model', '')
        if 'nano-banana' in model.lower() and 'gemini' not in model.lower():
            messagebox.showwarning("提示", 
                "图片编辑功能需要使用 Gemini 3 Pro Image 模型。\n" +
                "当前模型可能不支持图片编辑。\n\n将尝试继续...")
        
        # 添加用户指令到历史
        self._add_to_edit_history(instruction, None, is_user=True)
        
        # 禁用按钮，显示进度（直接在按钮上显示）
        self.edit_apply_btn.config(state=tk.DISABLED, text="🔄 正在处理...")
        self.logger.info(f"开始处理编辑指令: {instruction[:50]}...")
        
        # 使用后台线程执行编辑操作
        def edit_in_background():
            try:
                # 更新进度：直接更新按钮文本
                def update_progress(msg):
                    self.root.after(0, lambda m=msg: self.edit_apply_btn.config(text=m))
                    self.logger.info(msg)
                
                update_progress("📡 正在连接API...")
                
                # 初始化图片生成器
                if not self.image_gen:
                    self.image_gen = ImageGenerator(self.config, default_preset)
                
                update_progress("📤 正在上传图片...")
                
                # 调用图片编辑API（使用当前图片 + 编辑指令）
                current_image = Image.open(self.edit_session['current_image_path'])
                
                update_progress("🎨 正在构建提示词...")
                
                # 根据编辑类型构建精确的提示词
                edit_type = self.edit_type_var.get() if hasattr(self, 'edit_type_var') else 'custom'
                strict_mode = self.strict_mode_var.get() if hasattr(self, 'strict_mode_var') else True
                
                if edit_type == 'modify':
                    if strict_mode:
                        # 严格模式：使用最强约束，禁止添加任何新元素
                        prompt = f"""Using the provided image as the base, {instruction}. 

CRITICAL CONSTRAINTS (MUST FOLLOW):
- Keep EVERYTHING else EXACTLY the same as the original image
- Do NOT add any new objects, decorations, or background elements
- Do NOT change the background (keep it solid/simple if it was)
- Do NOT add books, holders, stands, or any props
- Do NOT add books, holders, stands, or any props
- Do NOT change the composition, layout, framing, or camera angle
- ONLY modify what is explicitly mentioned: {instruction}
- If the original was minimal/simple, keep it minimal/simple
- Preserve the exact background style (solid color, gradient, etc.)"""
                    else:
                        # 普通模式：允许适度美化
                        prompt = f"Using the provided image, {instruction}. Keep the overall composition similar but you may enhance the scene aesthetically."
                elif edit_type == 'add':
                    # 添加元素：明确是添加而不是替换
                    prompt = f"Using the provided image, add {instruction} to the scene. Ensure the new element integrates naturally with the existing image style and lighting."
                elif edit_type == 'remove':
                    # 移除元素：明确删除并补全背景
                    prompt = f"Using the provided image, remove {instruction} from the scene. Fill in the removed area naturally to match the surrounding background."
                elif edit_type == 'style':
                    # 风格转换：保持构图改变风格
                    prompt = f"Transform the provided image into {instruction}. Preserve the original composition and subject matter, but render it in the specified artistic style."
                elif edit_type == 'language':
                    # 语言修改：只改文字
                    prompt = f"Using the provided image, {instruction}. Do not change any other visual elements, colors, composition, or layout - only modify the text/language."
                else:
                    # 自定义：使用原始指令
                    prompt = instruction
                
                update_progress("⚙️ 正在生成编辑后的图片（可能需要1-3分钟）...")
                
                # 生成编辑后的图片
                new_image_path = self.image_gen.generate_with_image(prompt, current_image)
                
                update_progress("💾 正在保存结果...")
                
                # 更新会话数据
                self.edit_session['current_image_path'] = new_image_path
                self.edit_session['images'].append(new_image_path)
                self.edit_session['chat_history'].append({
                    'instruction': instruction,
                    'result_image': new_image_path
                })
                
                # 在主线程中更新UI
                def update_ui():
                    # 显示新图片
                    self._add_to_edit_history("编辑结果", new_image_path, is_user=False)
                    
                    # 清空输入框
                    self.edit_instruction_text.delete("1.0", tk.END)
                    
                    # 恢复按钮状态
                    self.edit_apply_btn.config(text="✅ 编辑完成", state=tk.NORMAL)
                    self.logger.success("图片编辑完成")
                    # 2秒后恢复按钮文本
                    self.root.after(2000, lambda: self.edit_apply_btn.config(text="应用编辑"))
                
                self.root.after(0, update_ui)
                
            except Exception as e:
                # 在主线程中显示错误
                def show_error():
                    self.edit_apply_btn.config(text="❌ 编辑失败", state=tk.NORMAL, bg='#E74C3C')
                    self.logger.error(f"编辑失败: {str(e)}")
                    messagebox.showerror("失败", f"编辑失败：{str(e)}")
                    # 2秒后恢复按钮
                    self.root.after(2000, lambda: self.edit_apply_btn.config(text="应用编辑", bg=self.colors['primary']))
                
                self.root.after(0, show_error)
        
        # 启动后台线程
        import threading
        thread = threading.Thread(target=edit_in_background, daemon=True)
        thread.start()
    
    def _add_to_edit_history(self, text, image_path, is_user=True):
        """添加对话历史条目"""
        # 创建历史条目容器
        item_frame = tk.Frame(self.edit_history_container, bg=self.colors['card'])
        item_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 时间戳
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        if is_user:
            # 用户指令
            header = tk.Label(item_frame, text=f"👤 用户指令 ({timestamp})",
                            bg=self.colors['card'], fg=self.colors['primary'],
                            font=("微软雅黑", 9, "bold"))
            header.pack(anchor=tk.W, pady=(5, 2))
            
            text_label = tk.Label(item_frame, text=text, bg='#E8F4FD',
                                fg=self.colors['text'], font=("微软雅黑", 10),
                                wraplength=350, justify=tk.LEFT, padx=10, pady=8,
                                relief='solid', bd=1)
            text_label.pack(anchor=tk.W, fill=tk.X, padx=(10, 0))
        else:
            # AI响应
            header = tk.Label(item_frame, text=f"🤖 {text} ({timestamp})",
                            bg=self.colors['card'], fg=self.colors['secondary'],
                            font=("微软雅黑", 9, "bold"))
            header.pack(anchor=tk.W, pady=(5, 2))
            
            if image_path:
                # 显示缩略图
                try:
                    img = Image.open(image_path)
                    img.thumbnail((300, 300), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    
                    img_label = tk.Label(item_frame, image=photo, bg=self.colors['card'],
                                       relief='solid', bd=1)
                    img_label.image = photo  # 保持引用
                    img_label.pack(anchor=tk.W, padx=(10, 0), pady=(5, 2))
                    
                    # 操作按钮容器
                    btn_frame = tk.Frame(item_frame, bg=self.colors['card'])
                    btn_frame.pack(anchor=tk.W, padx=(10, 0), pady=(0, 5))
                    
                    # 打开按钮
                    open_btn = tk.Button(btn_frame, text="打开",
                                        command=lambda p=image_path: self._open_image_by_path(p),
                                        font=("微软雅黑", 9),
                                        bg=self.colors['primary'], fg='white',
                                        relief='flat', padx=12, pady=4,
                                        cursor='hand2')
                    open_btn.pack(side=tk.LEFT, padx=(0, 5))
                    
                    # 在文件夹中显示按钮
                    folder_btn = tk.Button(btn_frame, text="在文件夹中显示",
                                          command=lambda p=image_path: self._show_in_folder_by_path(p),
                                          font=("微软雅黑", 9),
                                          bg=self.colors['primary'], fg='white',
                                          relief='flat', padx=12, pady=4,
                                          cursor='hand2')
                    folder_btn.pack(side=tk.LEFT, padx=5)
                    
                    # 另存为按钮
                    save_btn = tk.Button(btn_frame, text="另存为",
                                        command=lambda p=image_path: self._save_image_by_path(p),
                                        font=("微软雅黑", 9),
                                        bg=self.colors['secondary'], fg='white',
                                        relief='flat', padx=12, pady=4,
                                        cursor='hand2')
                    save_btn.pack(side=tk.LEFT)
                    
                except Exception as e:
                    error_label = tk.Label(item_frame, text=f"无法加载图片: {str(e)}",
                                         bg=self.colors['card'], fg='red',
                                         font=("微软雅黑", 9))
                    error_label.pack(anchor=tk.W, padx=(10, 0))
        
        # 分隔线
        separator = tk.Frame(item_frame, bg=self.colors['text_light'], height=1)
        separator.pack(fill=tk.X, pady=(5, 0))
        
        # 滚动到底部
        self.edit_history_canvas.update_idletasks()
        self.edit_history_canvas.yview_moveto(1.0)
    
    # def _display_edit_image(self, image_path):
    #     """在预览区域显示图片"""
    #     # 已移除预览canvas，此功能不再需要
    #     pass
    
    # def _on_edit_canvas_resize(self, event):
    #     """编辑预览canvas大小改变时重新显示图片"""
    #     # 已移除预览canvas，此功能不再需要
    #     pass
    
    def _open_image_by_path(self, image_path):
        """使用默认程序打开指定路径的图片"""
        if not image_path or not os.path.exists(image_path):
            messagebox.showwarning("提示", "图片文件不存在！")
            return
        
        try:
            import subprocess
            import platform
            
            system = platform.system()
            if system == 'Windows':
                os.startfile(image_path)
            elif system == 'Darwin':  # macOS
                subprocess.run(['open', image_path])
            else:  # Linux
                subprocess.run(['xdg-open', image_path])
        except Exception as e:
            messagebox.showerror("错误", f"打开失败：{str(e)}")
    
    def _show_in_folder_by_path(self, image_path):
        """在文件夹中显示指定路径的图片"""
        if not image_path or not os.path.exists(image_path):
            messagebox.showwarning("提示", "图片文件不存在！")
            return
        
        try:
            import subprocess
            import platform
            
            system = platform.system()
            if system == 'Windows':
                subprocess.run(['explorer', '/select,', os.path.abspath(image_path)])
            elif system == 'Darwin':  # macOS
                subprocess.run(['open', '-R', image_path])
            else:  # Linux
                folder_path = os.path.dirname(os.path.abspath(image_path))
                subprocess.run(['xdg-open', folder_path])
        except Exception as e:
            messagebox.showerror("错误", f"打开失败：{str(e)}")
    
    def _save_image_by_path(self, image_path):
        """另存为指定路径的图片"""
        if not image_path or not os.path.exists(image_path):
            messagebox.showwarning("提示", "图片文件不存在！")
            return
        
        save_path = filedialog.asksaveasfilename(
            title="保存图片",
            defaultextension=".png",
            filetypes=[("PNG图片", "*.png"), ("JPEG图片", "*.jpg"), ("所有文件", "*.*")]
        )
        
        if save_path:
            try:
                import shutil
                shutil.copy(image_path, save_path)
                self.logger.success(f"图片已另存为: {save_path}")
                messagebox.showinfo("成功", f"图片已保存到：\n{save_path}")
            except Exception as e:
                self.logger.error(f"保存图片失败: {str(e)}")
                messagebox.showerror("错误", f"保存失败：{str(e)}")
    
    def _save_edited_image(self):
        """保存编辑后的图片"""
        if not self.edit_session['current_image_path']:
            messagebox.showwarning("提示", "没有可保存的图片！")
            return
        
        save_path = filedialog.asksaveasfilename(
            title="保存编辑后的图片",
            defaultextension=".png",
            filetypes=[("PNG图片", "*.png"), ("JPEG图片", "*.jpg"), ("所有文件", "*.*")]
        )
        
        if save_path:
            try:
                import shutil
                shutil.copy(self.edit_session['current_image_path'], save_path)
                self.logger.success(f"编辑后的图片已保存: {save_path}")
                messagebox.showinfo("成功", f"图片已保存到：\n{save_path}")
            except Exception as e:
                self.logger.error(f"保存图片失败: {str(e)}")
                messagebox.showerror("失败", f"保存失败：{str(e)}")
    
    def _open_edited_image(self):
        """使用默认程序打开编辑后的图片"""
        if not self.edit_session['current_image_path'] or not os.path.exists(self.edit_session['current_image_path']):
            messagebox.showwarning("提示", "图片文件不存在！")
            return
        
        try:
            import subprocess
            import platform
            
            system = platform.system()
            if system == 'Windows':
                os.startfile(self.edit_session['current_image_path'])
            elif system == 'Darwin':  # macOS
                subprocess.run(['open', self.edit_session['current_image_path']])
            else:  # Linux
                subprocess.run(['xdg-open', self.edit_session['current_image_path']])
        except Exception as e:
            messagebox.showerror("错误", f"打开失败：{str(e)}")
    
    def _show_edited_in_folder(self):
        """在文件夹中显示编辑后的图片"""
        if not self.edit_session['current_image_path'] or not os.path.exists(self.edit_session['current_image_path']):
            messagebox.showwarning("提示", "图片文件不存在！")
            return
        
        try:
            import subprocess
            import platform
            
            system = platform.system()
            if system == 'Windows':
                subprocess.run(['explorer', '/select,', os.path.abspath(self.edit_session['current_image_path'])])
            elif system == 'Darwin':  # macOS
                subprocess.run(['open', '-R', self.edit_session['current_image_path']])
            else:  # Linux
                folder_path = os.path.dirname(os.path.abspath(self.edit_session['current_image_path']))
                subprocess.run(['xdg-open', folder_path])
        except Exception as e:
            messagebox.showerror("错误", f"打开失败：{str(e)}")
    
    def _load_last_edit_session(self):
        """加载上次的编辑会话"""
        try:
            last_session = self.history.get_latest_edit_session()
            if not last_session:
                return
            
            # 恢复会话数据
            self.edit_session = {
                'chat_history': last_session.get('chat_history', []),
                'current_image_path': last_session.get('current_image_path'),
                'original_image_path': last_session.get('original_image_path'),
                'images': last_session.get('images', [])
            }
            
            # 恢复上传的图片路径显示
            if self.edit_session.get('original_image_path'):
                self.edit_image_path_var.set(self.edit_session['original_image_path'])
                self.edit_apply_btn.config(state=tk.NORMAL)
            
            # 恢复对话历史显示
            for item in last_session.get('chat_history', []):
                if 'instruction' in item:
                    # 用户指令
                    self._add_to_edit_history(item['instruction'], None, is_user=True)
                    # 编辑结果
                    if 'result_image' in item and item['result_image']:
                        self._add_to_edit_history("编辑结果", item['result_image'], is_user=False)
            
            self.logger.info(f"已恢复上次编辑会话（{len(last_session.get('chat_history', []))}条记录）")
        except Exception as e:
            self.logger.error(f"加载编辑会话失败: {str(e)}")
    
    def _on_closing(self):
        """窗口关闭时保存编辑会话"""
        try:
            # 保存当前编辑会话
            if self.edit_session.get('chat_history'):
                self.history.save_edit_session(self.edit_session)
                self.logger.info("已保存编辑会话")
        except Exception as e:
            self.logger.error(f"保存编辑会话失败: {str(e)}")
        finally:
            self.logger.info("应用程序退出")
            self.root.destroy()

def gui_main():
    root = tk.Tk()
    app = InfographicGUI(root)
    root.mainloop()

if __name__ == "__main__":
    gui_main()

