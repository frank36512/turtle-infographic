import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler


class AppLogger:
    """应用程序日志管理器"""
    
    def __init__(self, log_dir=None):
        # 获取日志目录
        if log_dir is None:
            if getattr(sys, 'frozen', False):
                # 打包后的exe运行
                base_path = os.path.dirname(sys.executable)
            else:
                # 开发环境运行
                base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            log_dir = os.path.join(base_path, "logs")
        
        os.makedirs(log_dir, exist_ok=True)
        
        # 创建日志文件路径
        self.log_file_path = os.path.join(log_dir, f"app_{datetime.now().strftime('%Y%m%d')}.log")
        
        # 配置日志
        self.logger = logging.getLogger('InfoGraphics')
        self.logger.setLevel(logging.DEBUG)
        
        # 清除已有的处理器
        self.logger.handlers.clear()
        
        # 文件处理器 - 轮转日志，最大5MB，保留3个文件
        file_handler = RotatingFileHandler(
            self.log_file_path, 
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        # 控制台处理器（开发环境使用）
        if not getattr(sys, 'frozen', False):
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_formatter = logging.Formatter('%(levelname)s - %(message)s')
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)
        
        # GUI回调列表
        self.gui_callbacks = []
        
    def get_log_file_path(self):
        """获取当前日志文件路径"""
        return self.log_file_path

    def add_gui_callback(self, callback):
        """添加GUI回调函数，用于实时显示日志"""
        self.gui_callbacks.append(callback)
    
    def _notify_gui(self, level, message):
        """通知所有GUI回调"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        for callback in self.gui_callbacks:
            try:
                callback(timestamp, level, message)
            except Exception as e:
                # 避免GUI回调错误影响日志记录
                self.logger.error(f"GUI回调错误: {str(e)}")
    
    def debug(self, message):
        """调试信息"""
        self.logger.debug(message)
        self._notify_gui("DEBUG", message)
    
    def info(self, message):
        """普通信息"""
        self.logger.info(message)
        self._notify_gui("INFO", message)
    
    def warning(self, message):
        """警告信息"""
        self.logger.warning(message)
        self._notify_gui("WARNING", message)
    
    def error(self, message):
        """错误信息"""
        self.logger.error(message)
        self._notify_gui("ERROR", message)
    
    def success(self, message):
        """成功信息（自定义级别）"""
        self.logger.info(f"✓ {message}")
        self._notify_gui("SUCCESS", message)


# 全局日志实例
_logger_instance = None

def get_logger():
    """获取全局日志实例"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = AppLogger()
    return _logger_instance
