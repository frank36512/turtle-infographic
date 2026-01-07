import json
import os
import sys
from datetime import datetime

class HistoryManager:
    def __init__(self, history_path=None):
        if history_path is None:
            # 获取程序运行目录（支持打包后的exe）
            if getattr(sys, 'frozen', False):
                # 打包后的exe运行
                base_path = os.path.dirname(sys.executable)
            else:
                # 开发环境运行
                base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            history_path = os.path.join(base_path, "data", "history.json")
        self.history_path = history_path
        self.history = self._load_history()

    def _load_history(self):
        """加载历史记录"""
        os.makedirs(os.path.dirname(self.history_path), exist_ok=True)
        if not os.path.exists(self.history_path):
            return {"prompts": [], "images": [], "edit_sessions": []}
        try:
            with open(self.history_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # 确保有edit_sessions字段
                if "edit_sessions" not in data:
                    data["edit_sessions"] = []
                return data
        except:
            return {"prompts": [], "images": [], "edit_sessions": []}

    def _save_history(self):
        """保存历史记录"""
        os.makedirs(os.path.dirname(self.history_path), exist_ok=True)
        with open(self.history_path, "w", encoding="utf-8") as f:
            json.dump(self.history, f, ensure_ascii=False, indent=4)

    def add_prompt(self, prompt, style, ratio, content):
        """添加提示词记录"""
        record = {
            "id": len(self.history["prompts"]) + 1,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "prompt": prompt,
            "style": style,
            "ratio": ratio,
            "content": content[:100] + "..." if len(content) > 100 else content
        }
        self.history["prompts"].insert(0, record)  # 最新的在前面
        # 只保留最近100条
        if len(self.history["prompts"]) > 100:
            self.history["prompts"] = self.history["prompts"][:100]
        self._save_history()
        return record["id"]

    def add_image(self, prompt, image_path, style, ratio):
        """添加图片生成记录"""
        record = {
            "id": len(self.history["images"]) + 1,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "prompt": prompt[:100] + "..." if len(prompt) > 100 else prompt,
            "image_path": image_path,
            "style": style,
            "ratio": ratio,
            "exists": os.path.exists(image_path)
        }
        self.history["images"].insert(0, record)  # 最新的在前面
        # 只保留最近100条
        if len(self.history["images"]) > 100:
            self.history["images"] = self.history["images"][:100]
        self._save_history()
        return record["id"]

    def get_prompt_history(self, limit=50):
        """获取提示词历史记录"""
        return self.history["prompts"][:limit]

    def get_image_history(self, limit=50):
        """获取图片生成历史记录"""
        # 更新文件存在状态
        for record in self.history["images"]:
            record["exists"] = os.path.exists(record["image_path"])
        self._save_history()
        return self.history["images"][:limit]

    def delete_prompt(self, record_id):
        """删除提示词记录"""
        self.history["prompts"] = [r for r in self.history["prompts"] if r["id"] != record_id]
        self._save_history()

    def delete_image(self, record_id):
        """删除图片记录"""
        self.history["images"] = [r for r in self.history["images"] if r["id"] != record_id]
        self._save_history()

    def clear_all(self):
        """清空所有历史记录"""
        self.history = {"prompts": [], "images": [], "edit_sessions": []}
        self._save_history()
    
    def save_edit_session(self, session_data):
        """保存编辑会话"""
        if not session_data.get('chat_history'):
            return  # 没有对话历史，不保存
        
        record = {
            "id": len(self.history.get("edit_sessions", [])) + 1,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "original_image_path": session_data.get('original_image_path'),
            "current_image_path": session_data.get('current_image_path'),
            "chat_history": session_data.get('chat_history', []),
            "images": session_data.get('images', [])
        }
        
        if "edit_sessions" not in self.history:
            self.history["edit_sessions"] = []
        
        self.history["edit_sessions"].insert(0, record)
        # 只保留最近10个会话
        if len(self.history["edit_sessions"]) > 10:
            self.history["edit_sessions"] = self.history["edit_sessions"][:10]
        self._save_history()
        return record["id"]
    
    def get_latest_edit_session(self):
        """获取最新的编辑会话"""
        sessions = self.history.get("edit_sessions", [])
        if sessions:
            return sessions[0]
        return None
    
    def clear_edit_sessions(self):
        """清空编辑会话历史"""
        self.history["edit_sessions"] = []
        self._save_history()
