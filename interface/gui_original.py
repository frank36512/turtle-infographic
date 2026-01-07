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

class InfographicGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("小乌龟信息图 (Turtle Infographic)")
        self.root.geometry("1000x750")
        
        # 设置图标
        try:
            icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'turtle.ico')
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception as e:
            print(f"Warning: Could not load icon: {e}")
        
        # 设置主题颜色
        self.colors = {
            'primary': '#4A90E2',      # 主色调-蓝色
            'secondary': '#50C878',     # 次要色-绿色
            'accent': '#FF6B6B',        # 强调色-红色
            'bg_light': '#F8F9FA',      # 浅色背景
            'bg_dark': '#FFFFFF',       # 深色背景
            'text_dark': '#2C3E50',     # 深色文字
            'text_light': '#7F8C8D',    # 浅色文字
            'border': '#E0E0E0'         # 边框色
        }
        
        # 配置根窗口样式
        self.root.configure(bg=self.colors['bg_light'])
        
        # 配置ttk样式
        self._setup_styles()
        # 检查API密钥
        default_preset = self.config.get_default_api_preset()
        if not default_preset or not default_preset.get('api_key'):
            messagebox.showwarning("提示", "未配置 API！\n请先在【API设置】中添加API配置。")

    def _setup_styles(self):
        """配置ttk样式"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # 配置Notebook样式
        style.configure('TNotebook', background=self.colors['bg_light'], borderwidth=0)
        style.configure('TNotebook.Tab', 
                       background=self.colors['bg_dark'],
                       foreground=self.colors['text_dark'],
                       padding=[20, 10],
                       font=('微软雅黑', 10, 'bold'))
        style.map('TNotebook.Tab',
                 background=[('selected', self.colors['primary'])],
                 foreground=[('selected', 'white')])
        
        # 配置Frame样式
        style.configure('TFrame', background=self.colors['bg_light'])
    def _init_widgets(self):
        # 顶部标题栏
        header_frame = tk.Frame(self.root, bg=self.colors['primary'], height=80)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.pack_propagate(False)
        
        # Logo和标题
        title_container = tk.Frame(header_frame, bg=self.colors['primary'])
        title_container.pack(expand=True)
        
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
                
                title_label = tk.Label(title_container, 
                                      text=" 小乌龟信息图 (Turtle Infographic)",
                                      image=self.header_logo,
                                      compound=tk.LEFT,
                                      font=("微软雅黑", 24, "bold"),
                                      bg=self.colors['primary'],
                                      fg='white')
                title_label.pack(side=tk.LEFT, padx=10)
            else:
                 title_label = tk.Label(title_container, 
                                      text="小乌龟信息图 (Turtle Infographic)",
                                      font=("微软雅黑", 24, "bold"),
                                      bg=self.colors['primary'],
                                      fg='white')
                 title_label.pack(side=tk.LEFT, padx=10)
        except Exception as e:
            print(f"Error loading logo: {e}")
            title_label = tk.Label(title_container, 
                                  text="小乌龟信息图 (Turtle Infographic)",
                                  font=("微软雅黑", 24, "bold"),
                                  bg=self.colors['primary'],
                                  fg='white')
            title_label.pack(side=tk.LEFT, padx=10)
        
        subtitle_label = tk.Label(title_container,
                                 text="快速生成专业级信息图",
                                 font=("微软雅黑", 11),
                                 bg=self.colors['primary'],
                                 fg='white')
        subtitle_label.pack(side=tk.LEFT, padx=5)

        # 主内容区域
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        # 创建Notebook（标签页）
    def _init_prompt_page(self):
        """提示词生成页面"""
        # 滚动区域
        canvas = tk.Canvas(self.prompt_frame, bg=self.colors['bg_light'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.prompt_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 页面说明
        info_frame = tk.Frame(scrollable_frame, bg=self.colors['bg_light'])
        info_frame.pack(fill=tk.X, padx=25, pady=(20, 10))
        
        tk.Label(info_frame, 
                text="📝 智能提示词生成器",
                font=("微软雅黑", 14, "bold"),
                bg=self.colors['bg_light'],
                fg=self.colors['text_dark']).pack(anchor=tk.W)
        
        tk.Label(info_frame,
                text="通过简单的四步选择，自动生成专业的AI提示词",
                font=("微软雅黑", 10),
    def _init_image_page(self):
        """信息图生成页面"""
        # 页面说明
        info_frame = tk.Frame(self.image_frame, bg=self.colors['bg_light'])
        info_frame.pack(fill=tk.X, padx=25, pady=(20, 10))
        
        tk.Label(info_frame, 
                text="🎨 AI 图片生成",
                font=("微软雅黑", 14, "bold"),
                bg=self.colors['bg_light'],
                fg=self.colors['text_dark']).pack(anchor=tk.W)
        
        tk.Label(info_frame,
                text="输入提示词，让AI为你创作精美的信息图",
                font=("微软雅黑", 10),
                bg=self.colors['bg_light'],
                fg=self.colors['text_light']).pack(anchor=tk.W, pady=(5, 0))
        
        # 提示词输入区域
        input_frame = ttk.LabelFrame(self.image_frame, text="💬 输入提示词", 
                                     padding=15, style='Card.TLabelframe')
        input_frame.pack(fill=tk.X, padx=25, pady=10)
        
        ttk.Label(input_frame, 
                 text="可以从【提示词生成】页面生成，也可以直接输入自定义提示词：",
                 style='Hint.TLabel').pack(anchor=tk.W, pady=(0, 10))
        
        self.image_prompt_text = scrolledtext.ScrolledText(input_frame, 
                                                          height=6, 
                                                          wrap=tk.WORD, 
                                                          font=("微软雅黑", 10),
                                                          relief='flat',
                                                          bg='#FAFAFA',
                                                          padx=10,
                                                          pady=10)
        self.image_prompt_text.pack(fill=tk.X, pady=5)

        # 生成按钮
        btn_frame = tk.Frame(self.image_frame, bg=self.colors['bg_light'])
        btn_frame.pack(pady=15)
        
        self.generate_image_btn = ttk.Button(btn_frame, 
                                            text="🎨 开始生成", 
                                            command=self._generate_image,
                                            style='Primary.TButton')
        self.generate_image_btn.pack(side=tk.LEFT, padx=5)
        
        self.save_image_btn = ttk.Button(btn_frame, 
                                        text="💾 另存为", 
                                        command=self._save_image,
                                        style='Secondary.TButton',
                                        state=tk.DISABLED)
        self.save_image_btn.pack(side=tk.LEFT, padx=5)

        # 进度提示
        self.progress_label = tk.Label(self.image_frame, 
                                      text="", 
                                      font=("微软雅黑", 10),
                                      bg=self.colors['bg_light'],
                                      fg=self.colors['text_light'])
        self.progress_label.pack(pady=5)

        # 图片预览区域
        preview_frame = ttk.LabelFrame(self.image_frame, text="🖼 图片预览", 
                                      padding=15, style='Card.TLabelframe')
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=10) 生成的提示词", 
                                             padding=15, style='Card.TLabelframe')
        prompt_display_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=15)
        
        self.prompt_display = scrolledtext.ScrolledText(prompt_display_frame, 
                                                       height=8, 
                                                       wrap=tk.WORD, 
                                                       font=("微软雅黑", 10),
                                                       relief='flat',
                                                       bg='#FAFAFA',
                                                       padx=10,
                                                       pady=10)
        self.prompt_display.pack(fill=tk.BOTH, expand=True)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
                       borderwidth=0,
                       relief='flat',
                       padding=[20, 10])
        
        # 配置LabelFrame样式
        style.configure('Card.TLabelframe', 
                       background=self.colors['bg_dark'],
                       foreground=self.colors['text_dark'],
                       borderwidth=1,
                       relief='solid')
        style.configure('Card.TLabelframe.Label',
                       background=self.colors['bg_dark'],
                       foreground=self.colors['primary'],
                       font=('微软雅黑', 11, 'bold'))

    def _init_widgets(self):e
        
        # 尝试初始化图片生成器
        try:
            default_preset = self.config.get_default_api_preset()
            if default_preset and default_preset.get('api_key'):
                self.image_gen = ImageGenerator(self.config, default_preset)
        except:
            pass

        # 界面组件
        self._init_widgets()
        
        # 检查API密钥
        default_preset = self.config.get_default_api_preset()
        if not default_preset or not default_preset.get('api_key'):
            messagebox.showwarning("提示", "未配置 API！\n请先在【API设置】中添加API配置。")

    def _init_widgets(self):
        # 标题栏
        title_frame = ttk.Frame(self.root)
        title_frame.pack(fill=tk.X, padx=20, pady=15)
        
        title_label = ttk.Label(title_frame, text="小乌龟信息图", font=("微软雅黑", 20, "bold"))
        title_label.pack(side=tk.LEFT)

        # 创建Notebook（标签页）
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        # 三个功能页面
        self.prompt_frame = ttk.Frame(self.notebook)
        self.image_frame = ttk.Frame(self.notebook)
        self.history_frame = ttk.Frame(self.notebook)
        self.settings_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.prompt_frame, text="📝 提示词生成")
        self.notebook.add(self.image_frame, text="🎨 信息图生成")
        self.notebook.add(self.history_frame, text="📋 生成记录")
        self.notebook.add(self.settings_frame, text="⚙ API设置")

        # 初始化各个页面
        self._init_prompt_page()
        self._init_image_page()
        self._init_history_page()
        self._init_settings_page()
        self._init_settings_page()

    def _init_prompt_page(self):
        """提示词生成页面"""
        # 风格选择区域
        self._create_style_frame()

        # 比例选择区域
        self._create_ratio_frame()

        # 内容输入区域
        self._create_content_frame()

        # 生成提示词按钮
        btn_frame = ttk.Frame(self.prompt_frame)
        btn_frame.pack(pady=20)
        
        generate_prompt_btn = ttk.Button(btn_frame, text="🔄 生成提示词", command=self._generate_prompt_only, width=20)
        generate_prompt_btn.pack(side=tk.LEFT, padx=5)
        
        copy_prompt_btn = ttk.Button(btn_frame, text="📋 复制提示词", command=self._copy_prompt, width=20)
        copy_prompt_btn.pack(side=tk.LEFT, padx=5)

        # 提示词显示区域
        prompt_display_frame = ttk.LabelFrame(self.prompt_frame, text="生成的提示词", padding=10)
        prompt_display_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.prompt_display = scrolledtext.ScrolledText(prompt_display_frame, height=8, width=80, wrap=tk.WORD, font=("微软雅黑", 10))
        self.prompt_display.pack(fill=tk.BOTH, expand=True)

    def _init_image_page(self):
        """信息图生成页面"""
        # 提示词输入区域
        input_frame = ttk.LabelFrame(self.image_frame, text="输入提示词", padding=10)
        input_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(input_frame, text="可以从【提示词生成】页面生成，也可以直接输入自定义提示词：").pack(anchor=tk.W)
        
        self.image_prompt_text = scrolledtext.ScrolledText(input_frame, height=8, width=80, wrap=tk.WORD, font=("微软雅黑", 10))
        self.image_prompt_text.pack(fill=tk.X, pady=5)

        # 生成按钮
        btn_frame = ttk.Frame(self.image_frame)
        btn_frame.pack(pady=10)
        
        self.generate_image_btn = ttk.Button(btn_frame, text="🎨 生成信息图", command=self._generate_image, width=20)
        self.generate_image_btn.pack(side=tk.LEFT, padx=5)
        
        self.save_image_btn = ttk.Button(btn_frame, text="💾 保存图片", command=self._save_image, width=20, state=tk.DISABLED)
        self.save_image_btn.pack(side=tk.LEFT, padx=5)

        # 进度提示
        self.progress_label = ttk.Label(self.image_frame, text="", font=("微软雅黑", 10), foreground="#666")
        self.progress_label.pack(pady=5)

        # 图片预览区域
        preview_frame = ttk.LabelFrame(self.image_frame, text="图片预览", padding=10)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 使用Canvas来显示图片，支持滚动
        canvas_frame = ttk.Frame(preview_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.image_canvas = tk.Canvas(canvas_frame, bg='#F5F5F5', highlightthickness=0)
        scrollbar_y = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.image_canvas.yview)
        scrollbar_x = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.image_canvas.xview)
        
        self.image_canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.image_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.current_image_path = None
        self.current_photo = None

    def _init_settings_page(self):
        """API设置页面"""
        settings_container = ttk.Frame(self.settings_frame)
        settings_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # API预设管理区域
        presets_frame = ttk.LabelFrame(settings_container, text="API 预设管理", padding=15)
        presets_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # 工具栏
        toolbar = ttk.Frame(presets_frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(toolbar, text="管理多个API配置，可快速切换", foreground="#666").pack(side=tk.LEFT)
        
        add_btn = ttk.Button(toolbar, text="➕ 添加API", command=self._add_api_preset, width=12)
        add_btn.pack(side=tk.RIGHT, padx=2)
        
        edit_btn = ttk.Button(toolbar, text="✏ 编辑", command=self._edit_api_preset, width=10)
        edit_btn.pack(side=tk.RIGHT, padx=2)
        
        delete_btn = ttk.Button(toolbar, text="🗑 删除", command=self._delete_api_preset, width=10)
        delete_btn.pack(side=tk.RIGHT, padx=2)

        # API列表
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
        
        # 双击设置为默认
        self.api_tree.bind("<Double-1>", self._set_default_api)

        # 保存路径设置
        path_frame = ttk.LabelFrame(settings_container, text="输出设置", padding=15)
        path_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(path_frame, text="保存路径：", font=("微软雅黑", 10)).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.path_entry = ttk.Entry(path_frame, width=60)
        self.path_entry.grid(row=0, column=1, sticky=tk.W, pady=5, padx=10)
        self.path_entry.insert(0, self.config.get('save_path', './output/infographics'))
        
        browse_btn = ttk.Button(path_frame, text="浏览", command=self._browse_folder, width=8)
        browse_btn.grid(row=0, column=2, pady=5)

        # 保存按钮
        save_btn = ttk.Button(settings_container, text="💾 保存路径设置", command=self._save_path_settings, width=20)
        save_btn.pack(pady=10)
        
        # 帮助信息
        help_frame = ttk.LabelFrame(settings_container, text="帮助", padding=15)
        help_frame.pack(fill=tk.X, pady=10)
        
        help_text = """• 获取 API 密钥：访问 https://aistudio.google.com/app/apikey
• 支持添加多个API配置（如国内代理、不同模型等）
• 双击API配置可设置为默认，生成图片时将使用默认配置
• 模型支持：gemini-2.0-flash-exp、gemini-1.5-pro 等"""
        
        ttk.Label(help_frame, text=help_text, font=("微软雅黑", 9), foreground="#666", justify=tk.LEFT).pack()

        # 加载API列表
        self._load_api_presets()

    def _init_history_page(self):
        """生成记录页面"""
        # 顶部工具栏
        toolbar = ttk.Frame(self.history_frame)
        toolbar.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(toolbar, text="历史记录", font=("微软雅黑", 14, "bold")).pack(side=tk.LEFT)
        
        refresh_btn = ttk.Button(toolbar, text="🔄 刷新", command=self._refresh_history, width=10)
        refresh_btn.pack(side=tk.RIGHT, padx=5)
        
        clear_btn = ttk.Button(toolbar, text="🗑 清空记录", command=self._clear_history, width=12)
        clear_btn.pack(side=tk.RIGHT, padx=5)

        # 创建子标签页
        history_notebook = ttk.Notebook(self.history_frame)
        history_notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # 提示词历史
        prompt_history_frame = ttk.Frame(history_notebook)
        history_notebook.add(prompt_history_frame, text="提示词历史")
        self._create_prompt_history_list(prompt_history_frame)

        # 图片历史
        image_history_frame = ttk.Frame(history_notebook)
        history_notebook.add(image_history_frame, text="图片历史")
        self._create_image_history_list(image_history_frame)

    def _create_prompt_history_list(self, parent):
        """创建提示词历史列表"""
        # 创建Treeview
        columns = ("时间", "风格", "比例", "内容摘要")
        self.prompt_tree = ttk.Treeview(parent, columns=columns, show="headings", height=15)
        
        # 设置列标题和宽度
        self.prompt_tree.heading("时间", text="生成时间")
        self.prompt_tree.heading("风格", text="风格")
        self.prompt_tree.heading("比例", text="比例")
        self.prompt_tree.heading("内容摘要", text="内容摘要")
        
        self.prompt_tree.column("时间", width=150)
        self.prompt_tree.column("风格", width=150)
        self.prompt_tree.column("比例", width=80)
        self.prompt_tree.column("内容摘要", width=300)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.prompt_tree.yview)
        self.prompt_tree.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        self.prompt_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 双击查看详情
        self.prompt_tree.bind("<Double-1>", self._show_prompt_detail)
        
        # 右键菜单
        self.prompt_menu = tk.Menu(self.prompt_tree, tearoff=0)
        self.prompt_menu.add_command(label="查看详情", command=lambda: self._show_prompt_detail(None))
        self.prompt_menu.add_command(label="复制到生成页面", command=self._copy_prompt_to_page)
        self.prompt_menu.add_separator()
        self.prompt_menu.add_command(label="删除记录", command=self._delete_prompt_record)
        
        self.prompt_tree.bind("<Button-3>", self._show_prompt_menu)
        
        # 加载数据
        self._load_prompt_history()

    def _create_image_history_list(self, parent):
        """创建图片历史列表"""
        # 创建Treeview
        columns = ("时间", "风格", "比例", "路径", "状态")
        self.image_tree = ttk.Treeview(parent, columns=columns, show="headings", height=15)
        
        # 设置列标题和宽度
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
        
        # 滚动条
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.image_tree.yview)
        self.image_tree.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        self.image_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 双击打开图片
        self.image_tree.bind("<Double-1>", self._open_image_from_history)
        
        # 右键菜单
        self.image_menu = tk.Menu(self.image_tree, tearoff=0)
        self.image_menu.add_command(label="打开图片", command=lambda: self._open_image_from_history(None))
        self.image_menu.add_command(label="查看提示词", command=self._show_image_prompt)
        self.image_menu.add_command(label="在文件夹中显示", command=self._show_in_folder)
        self.image_menu.add_separator()
        self.image_menu.add_command(label="删除记录", command=self._delete_image_record)
        
        self.image_tree.bind("<Button-3>", self._show_image_menu)
        
        # 加载数据
        self._load_image_history()

    def _load_prompt_history(self):
        """加载提示词历史"""
        # 清空列表
        for item in self.prompt_tree.get_children():
            self.prompt_tree.delete(item)
        
        # 加载数据
        records = self.history.get_prompt_history()
        for record in records:
            self.prompt_tree.insert("", tk.END, values=(
                record["timestamp"],
                record["style"],
                record["ratio"],
                record["content"]
            ), tags=(record["id"],))

    def _load_image_history(self):
        """加载图片历史"""
        # 清空列表
        for item in self.image_tree.get_children():
            self.image_tree.delete(item)
        
        # 加载数据
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
        """刷新历史记录"""
        self._load_prompt_history()
        self._load_image_history()
        messagebox.showinfo("提示", "历史记录已刷新")

    def _clear_history(self):
        """清空历史记录"""
        if messagebox.askyesno("确认", "确定要清空所有历史记录吗？\n此操作不可恢复！"):
            self.history.clear_all()
            self._load_prompt_history()
            self._load_image_history()
            messagebox.showinfo("成功", "历史记录已清空")

    def _show_prompt_menu(self, event):
        """显示提示词右键菜单"""
        item = self.prompt_tree.identify_row(event.y)
        if item:
            self.prompt_tree.selection_set(item)
            self.prompt_menu.post(event.x_root, event.y_root)

    def _show_image_menu(self, event):
        """显示图片右键菜单"""
        item = self.image_tree.identify_row(event.y)
        if item:
            self.image_tree.selection_set(item)
            self.image_menu.post(event.x_root, event.y_root)

    def _show_prompt_detail(self, event):
        """显示提示词详情"""
        selection = self.prompt_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        record_id = int(self.prompt_tree.item(item, "tags")[0])
        
        # 查找记录
        records = self.history.get_prompt_history()
        record = next((r for r in records if r["id"] == record_id), None)
        if not record:
            return
        
        # 显示详情窗口
        detail_window = tk.Toplevel(self.root)
        detail_window.title("提示词详情")
        detail_window.geometry("700x500")
        detail_window.transient(self.root)
        
        info_frame = ttk.Frame(detail_window)
        info_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(info_frame, text=f"生成时间: {record['timestamp']}", font=("微软雅黑", 10)).pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"风格: {record['style']}", font=("微软雅黑", 10)).pack(anchor=tk.W, pady=2)
        ttk.Label(info_frame, text=f"比例: {record['ratio']}", font=("微软雅黑", 10)).pack(anchor=tk.W, pady=2)
        
        ttk.Label(detail_window, text="完整提示词:", font=("微软雅黑", 10, "bold")).pack(anchor=tk.W, padx=20, pady=(10, 5))
        
        prompt_text = scrolledtext.ScrolledText(detail_window, height=15, wrap=tk.WORD, font=("微软雅黑", 10))
        prompt_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        prompt_text.insert(tk.END, record["prompt"])
        prompt_text.config(state=tk.DISABLED)
        
        btn_frame = ttk.Frame(detail_window)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="复制", command=lambda: self._copy_text(record["prompt"]), width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="关闭", command=detail_window.destroy, width=15).pack(side=tk.LEFT, padx=5)

    def _copy_prompt_to_page(self):
        """复制提示词到生成页面"""
        selection = self.prompt_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        record_id = int(self.prompt_tree.item(item, "tags")[0])
        
        records = self.history.get_prompt_history()
        record = next((r for r in records if r["id"] == record_id), None)
        if not record:
            return
        
        # 复制到信息图生成页面
        self.image_prompt_text.delete("1.0", tk.END)
        self.image_prompt_text.insert(tk.END, record["prompt"])
        
        # 切换到信息图生成页面
        self.notebook.select(1)
        messagebox.showinfo("成功", "提示词已复制到【信息图生成】页面")

    def _delete_prompt_record(self):
        """删除提示词记录"""
        selection = self.prompt_tree.selection()
        if not selection:
            return
        
        if messagebox.askyesno("确认", "确定要删除此记录吗？"):
            item = selection[0]
            record_id = int(self.prompt_tree.item(item, "tags")[0])
            self.history.delete_prompt(record_id)
            self._load_prompt_history()

    def _open_image_from_history(self, event):
        """从历史记录打开图片"""
        selection = self.image_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        record_id = int(self.image_tree.item(item, "tags")[0])
        
        records = self.history.get_image_history()
        record = next((r for r in records if r["id"] == record_id), None)
        if not record:
            return
        
        if not record["exists"]:
            messagebox.showerror("错误", "图片文件不存在或已被删除")
            return
        
        # 使用系统默认程序打开
        import subprocess
        try:
            os.startfile(record["image_path"])
        except:
            subprocess.run(["start", record["image_path"]], shell=True)

    def _show_image_prompt(self):
        """显示图片的提示词"""
        selection = self.image_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        record_id = int(self.image_tree.item(item, "tags")[0])
        
        records = self.history.get_image_history()
        record = next((r for r in records if r["id"] == record_id), None)
        if not record:
            return
        
        messagebox.showinfo("提示词", record["prompt"])

    def _show_in_folder(self):
        """在文件夹中显示"""
        selection = self.image_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        record_id = int(self.image_tree.item(item, "tags")[0])
        
        records = self.history.get_image_history()
        record = next((r for r in records if r["id"] == record_id), None)
        if not record:
            return
        
        if not record["exists"]:
            messagebox.showerror("错误", "图片文件不存在或已被删除")
            return
        
        # 在资源管理器中显示文件
        import subprocess
        subprocess.run(["explorer", "/select,", os.path.abspath(record["image_path"])])

    def _delete_image_record(self):
        """删除图片记录"""
        selection = self.image_tree.selection()
        if not selection:
            return
        
        if messagebox.askyesno("确认", "确定要删除此记录吗？\n（不会删除实际文件）"):
            item = selection[0]
            record_id = int(self.image_tree.item(item, "tags")[0])
            self.history.delete_image(record_id)
            self._load_image_history()

    def _copy_text(self, text):
        """复制文本到剪贴板"""
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        messagebox.showinfo("成功", "已复制到剪贴板")

    def _create_style_frame(self, parent):
        frame = ttk.LabelFrame(parent, text="📌 第一步：选择风格", 
                              padding=15, style='Card.TLabelframe')
        frame.pack(fill=tk.X, padx=25, pady=10)

        # 风格下拉框
        self.style_var = tk.StringVar()
        styles = list(self.config.get_style_categories().keys())
        
        combo_frame = tk.Frame(frame, bg=self.colors['bg_dark'])
        combo_frame.pack(fill=tk.X)
        
        self.style_combobox = ttk.Combobox(combo_frame, 
                                          textvariable=self.style_var, 
                                          values=styles, 
                                          state="readonly",
                                          font=("微软雅黑", 10),
                                          width=85)
        self.style_combobox.pack(pady=5)
        
        # 风格描述标签（先创建）
        self.style_desc_label = tk.Label(frame, 
                                         text="", 
                                         wraplength=850, 
                                         bg=self.colors['bg_dark'],
                                         fg=self.colors['text_light'],
                                         font=("微软雅黑", 9),
                                         justify=tk.LEFT)
    def _create_ratio_frame(self, parent):
        frame = ttk.LabelFrame(parent, text="📐 第二步：选择比例", 
                              padding=15, style='Card.TLabelframe')
        frame.pack(fill=tk.X, padx=25, pady=10)

        self.ratio_var = tk.StringVar()
        ratios = list(self.config.get_ratio_presets().keys())
        
        # 创建水平布局
        ratio_inner_frame = tk.Frame(frame, bg=self.colors['bg_dark'])
        ratio_inner_frame.pack()
        
        self.ratio_combobox = ttk.Combobox(ratio_inner_frame, 
                                          textvariable=self.ratio_var, 
                                          values=ratios, 
                                          state="readonly",
                                          font=("微软雅黑", 10),
                                          width=25)
        self.ratio_combobox.pack(side=tk.LEFT, padx=5)
        
        # 比例描述标签
        self.ratio_desc_label = tk.Label(ratio_inner_frame, 
                                        text="",
                                        bg=self.colors['bg_dark'],
                                        fg=self.colors['text_light'],
                                        font=("微软雅黑", 9))
        self.ratio_desc_label.pack(side=tk.LEFT, padx=10)
        
        if ratios:
            self.ratio_combobox.current(2)  # 默认选中16:9
            self._update_ratio_desc()
        
    def _create_content_frame(self, parent):
        frame = ttk.LabelFrame(parent, text="✍ 第三步：输入内容", 
                              padding=15, style='Card.TLabelframe')
        frame.pack(fill=tk.X, padx=25, pady=10)

        # 核心内容输入框
        ttk.Label(frame, text="核心内容：", style='Subtitle.TLabel').pack(anchor=tk.W, pady=(0, 5))
        self.content_text = scrolledtext.ScrolledText(frame, 
                                                     height=5, 
                                                     wrap=tk.WORD,
                                                     font=("微软雅黑", 10),
                                                     relief='flat',
                                                     bg='#FAFAFA',
                                                     padx=10,
                                                     pady=10)
        self.content_text.pack(fill=tk.X, pady=5)
        self.content_text.insert(tk.END, "示例：2026年法定节假日安排、T细胞激活机制科普")

        # 使用场景输入框
        ttk.Label(frame, text="使用场景（可选）：", style='Subtitle.TLabel').pack(anchor=tk.W, pady=(10, 5))
        self.scene_entry = ttk.Entry(frame, font=("微软雅黑", 10))
        self.scene_entry.pack(fill=tk.X, pady=5)
        self.scene_entry.insert(tk.END, "公众号文章、论文插图、PPT演示")
        
        # 绑定比例选择事件
        self.ratio_combobox.bind("<<ComboboxSelected>>", lambda e: self._update_ratio_desc())

    def _update_ratio_desc(self):
        """更新比例描述"""
        ratio_key = self.ratio_var.get()
        desc = self.config.get_ratio_presets().get(ratio_key, "")
        resolution = self.config.get_resolution_by_ratio(ratio_key)
        self.ratio_desc_label.config(text=f"{desc} - {resolution}")

    def _create_content_frame(self):
        frame = ttk.LabelFrame(self.prompt_frame, text="第三步：输入内容", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        # 核心内容输入框
        ttk.Label(frame, text="核心内容：").pack(anchor=tk.W)
        self.content_text = scrolledtext.ScrolledText(frame, height=5, width=80, wrap=tk.WORD)
        self.content_text.pack(fill=tk.X, pady=5)
        self.content_text.insert(tk.END, "示例：2026年法定节假日安排、T细胞激活机制科普")

        # 使用场景输入框
        ttk.Label(frame, text="使用场景（可选）：").pack(anchor=tk.W, pady=(5, 0))
        self.scene_entry = ttk.Entry(frame, width=80)
        self.scene_entry.pack(fill=tk.X, pady=5)
        self.scene_entry.insert(tk.END, "公众号文章、论文插图、PPT演示")

    def _toggle_api_key_visibility(self):
        """切换API密钥显示/隐藏"""
        if self.api_key_entry.cget('show') == '*':
            self.api_key_entry.config(show='')
        else:
            self.api_key_entry.config(show='*')

    def _browse_folder(self):
        """浏览文件夹"""
        folder = filedialog.askdirectory()
        if folder:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, folder)

    def _load_api_presets(self):
        """加载API预设列表"""
        # 清空列表
        for item in self.api_tree.get_children():
            self.api_tree.delete(item)
        
        # 加载数据
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
        """添加API预设"""
        self._show_api_preset_dialog()

    def _edit_api_preset(self):
        """编辑API预设"""
        selection = self.api_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请先选择要编辑的API配置")
            return
        
        item = selection[0]
        index = int(self.api_tree.item(item, "tags")[0])
        presets = self.config.get_api_presets()
        if index < len(presets):
            preset = presets[index]
            self._show_api_preset_dialog(preset, index)

    def _delete_api_preset(self):
        """删除API预设"""
        selection = self.api_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请先选择要删除的API配置")
            return
        
        if messagebox.askyesno("确认", "确定要删除此API配置吗？"):
            item = selection[0]
            index = int(self.api_tree.item(item, "tags")[0])
            self.config.delete_api_preset(index)
            self._load_api_presets()
            messagebox.showinfo("成功", "API配置已删除")

    def _set_default_api(self, event):
        """设置默认API"""
        selection = self.api_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        index = int(self.api_tree.item(item, "tags")[0])
        self.config.set_default_api(index)
        self._load_api_presets()
        
        # 重新初始化图片生成器
        try:
            default_preset = self.config.get_default_api_preset()
            if default_preset and default_preset.get("api_key"):
                self.image_gen = ImageGenerator(self.config, default_preset)
        except:
            pass

    def _show_api_preset_dialog(self, preset=None, index=None):
        """显示API预设编辑对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("编辑API配置" if preset else "添加API配置")
        dialog.geometry("600x400")
        dialog.transient(self.root)
        dialog.grab_set()

        content_frame = ttk.Frame(dialog, padding=20)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # 配置名称
        ttk.Label(content_frame, text="配置名称：", font=("微软雅黑", 10)).grid(row=0, column=0, sticky=tk.W, pady=10)
        name_entry = ttk.Entry(content_frame, width=50)
        name_entry.grid(row=0, column=1, sticky=tk.W, pady=10, padx=10)
        if preset:
            name_entry.insert(0, preset["name"])

        # API密钥
        ttk.Label(content_frame, text="API 密钥：", font=("微软雅黑", 10)).grid(row=1, column=0, sticky=tk.W, pady=10)
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

        # API地址
        ttk.Label(content_frame, text="API 地址：", font=("微软雅黑", 10)).grid(row=2, column=0, sticky=tk.W, pady=10)
        url_entry = ttk.Entry(content_frame, width=50)
        url_entry.grid(row=2, column=1, sticky=tk.W, pady=10, padx=10)
        if preset:
            url_entry.insert(0, preset["api_url"])
        else:
            url_entry.insert(0, "https://generativelanguage.googleapis.com")

        # 模型名称
        ttk.Label(content_frame, text="模型名称：", font=("微软雅黑", 10)).grid(row=3, column=0, sticky=tk.W, pady=10)
        model_entry = ttk.Entry(content_frame, width=50)
        model_entry.grid(row=3, column=1, sticky=tk.W, pady=10, padx=10)
        if preset:
            model_entry.insert(0, preset["model"])
        else:
            model_entry.insert(0, "gemini-2.0-flash-exp")

        # 提示信息
        tip_text = """常用配置示例：
• Google官方：https://generativelanguage.googleapis.com
• 模型：gemini-2.0-flash-exp (快速), gemini-1.5-pro (高质量)"""
        
        tip_label = ttk.Label(content_frame, text=tip_text, font=("微软雅黑", 9), foreground="#666", justify=tk.LEFT)
        tip_label.grid(row=4, column=0, columnspan=3, sticky=tk.W, pady=10)

        # 按钮
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=20)

        def save_preset():
            name = name_entry.get().strip()
            api_key = key_entry.get().strip()
            api_url = url_entry.get().strip()
            model = model_entry.get().strip()

            if not name or not api_key or not api_url or not model:
                messagebox.showerror("错误", "请填写完整信息！")
                return

            if index is not None:
                # 更新
                self.config.update_api_preset(index, name, api_key, api_url, model)
                messagebox.showinfo("成功", "API配置已更新")
            else:
                # 添加
                self.config.add_api_preset(name, api_key, api_url, model)
                messagebox.showinfo("成功", "API配置已添加")

            self._load_api_presets()
            dialog.destroy()

        ttk.Button(btn_frame, text="💾 保存", command=save_preset, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="取消", command=dialog.destroy, width=15).pack(side=tk.LEFT, padx=5)

    def _save_path_settings(self):
        """保存路径设置"""
        new_path = self.path_entry.get().strip()
        if new_path:
            self.config.update('save_path', new_path)
            messagebox.showinfo("成功", "保存路径已更新")

    def _save_settings(self):
        """保存API设置（已废弃，保留以避免错误）"""
        pass

    def _generate_prompt_only(self):
        """仅生成提示词"""
        style_key = self.style_var.get()
        ratio = self.ratio_var.get()
        content = self.content_text.get("1.0", tk.END).strip()
        usage_scene = self.scene_entry.get().strip() or "通用场景"

        if not content:
            messagebox.showerror("错误", "请输入核心内容！")
            return

        try:
            prompt = self.prompt_gen.generate(style_key, ratio, content, usage_scene)
            self.prompt_display.delete("1.0", tk.END)
            self.prompt_display.insert(tk.END, prompt)
            # 同时更新到信息图生成页面
            self.image_prompt_text.delete("1.0", tk.END)
            self.image_prompt_text.insert(tk.END, prompt)
            
            # 保存到历史记录
            self.history.add_prompt(prompt, style_key, ratio, content)
            
            messagebox.showinfo("成功", "提示词已生成！可以切换到【信息图生成】页面进行图片生成。")
        except Exception as e:
            messagebox.showerror("失败", f"生成出错：{str(e)}")

    def _copy_prompt(self):
        """复制提示词到剪贴板"""
        prompt = self.prompt_display.get("1.0", tk.END).strip()
        if prompt:
            self.root.clipboard_clear()
            self.root.clipboard_append(prompt)
            messagebox.showinfo("成功", "提示词已复制到剪贴板！")
        else:
            messagebox.showwarning("提示", "请先生成提示词！")

    def _generate_image(self):
        """生成信息图"""
        # 获取默认API配置
        default_preset = self.config.get_default_api_preset()
        if not default_preset or not default_preset.get("api_key"):
            messagebox.showerror("错误", "未配置API！\n请先在【API设置】中添加并配置API。")
            self.notebook.select(3)  # 切换到设置页面
            return

        # 使用默认API初始化生成器
        try:
            self.image_gen = ImageGenerator(self.config, default_preset)
        except Exception as e:
            messagebox.showerror("错误", f"初始化API失败：{str(e)}\n请检查【API设置】中的配置。")
            self.notebook.select(3)
            return

        prompt = self.image_prompt_text.get("1.0", tk.END).strip()
        if not prompt:
            messagebox.showerror("错误", "请输入提示词！\n可以从【提示词生成】页面生成提示词。")
            return

        # 禁用生成按钮
        self.generate_image_btn.config(state=tk.DISABLED)
        self.progress_label.config(text=f"🔄 正在使用 [{default_preset['name']}] 生成图片，请稍候...")
        self.root.update()

        try:
            save_path = self.image_gen.generate(prompt)
            self.current_image_path = save_path
            self.progress_label.config(text=f"✅ 生成成功！保存路径：{save_path}")
            
            # 显示图片
            self._display_image(save_path)
            self.save_image_btn.config(state=tk.NORMAL)
            
            # 保存到历史记录（尝试从提示词中提取风格和比例信息）
            style = "自定义"
            ratio = "未知"
            # 尝试从当前选择获取
            if hasattr(self, 'style_var') and self.style_var.get():
                style = self.style_var.get()
            if hasattr(self, 'ratio_var') and self.ratio_var.get():
                ratio = self.ratio_var.get()
            
            self.history.add_image(prompt, save_path, style, ratio)
            
        except Exception as e:
            self.progress_label.config(text=f"❌ 生成失败：{str(e)}")
            messagebox.showerror("失败", f"生成出错：{str(e)}")
        finally:
            self.generate_image_btn.config(state=tk.NORMAL)

    def _display_image(self, image_path):
        """在Canvas中显示图片"""
        try:
            # 读取图片
            img = Image.open(image_path)
            
            # 获取Canvas大小
            canvas_width = self.image_canvas.winfo_width()
            canvas_height = self.image_canvas.winfo_height()
            
            # 如果Canvas还没有渲染，使用默认大小
            if canvas_width <= 1:
                canvas_width = 800
                canvas_height = 400
            
            # 计算缩放比例以适应Canvas
            img_width, img_height = img.size
            scale = min(canvas_width / img_width, canvas_height / img_height, 1.0)
            
            if scale < 1.0:
                new_width = int(img_width * scale)
                new_height = int(img_height * scale)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # 转换为PhotoImage
            self.current_photo = ImageTk.PhotoImage(img)
            
            # 清除之前的内容
            self.image_canvas.delete("all")
            
            # 在Canvas中显示图片
            self.image_canvas.create_image(canvas_width//2, canvas_height//2, image=self.current_photo, anchor=tk.CENTER)
            self.image_canvas.config(scrollregion=self.image_canvas.bbox("all"))
            
        except Exception as e:
            messagebox.showerror("错误", f"无法显示图片：{str(e)}")

    def _save_image(self):
        """另存为图片"""
        if not self.current_image_path:
            messagebox.showwarning("提示", "请先生成图片！")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG图片", "*.png"), ("所有文件", "*.*")]
        )
        
        if file_path:
            try:
                import shutil
                shutil.copy2(self.current_image_path, file_path)
                messagebox.showinfo("成功", f"图片已保存到：{file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"保存失败：{str(e)}")



def gui_main():
    root = tk.Tk()
    app = InfographicGUI(root)
    root.mainloop()

if __name__ == "__main__":
    gui_main()
