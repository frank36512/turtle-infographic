import json
import os
from datetime import datetime

class PromptLibrary:
    def __init__(self, data_file="data/prompt_library.json"):
        self.data_file = data_file
        self.data = self._load_data()
    
    def _load_data(self):
        """加载提示词库数据"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return self._get_default_data()
        else:
            return self._get_default_data()
    
    def _get_default_data(self):
        """获取默认数据结构"""
        return {
            "categories": [
                {
                    "id": 1,
                    "name": "科技类",
                    "description": "科技、技术相关的提示词",
                    "prompts": []
                },
                {
                    "id": 2,
                    "name": "商业类",
                    "description": "商业、营销相关的提示词",
                    "prompts": []
                },
                {
                    "id": 3,
                    "name": "教育类",
                    "description": "教育、培训相关的提示词",
                    "prompts": []
                }
            ],
            "next_category_id": 4,
            "next_prompt_id": 1
        }
    
    def _save_data(self):
        """保存数据到文件"""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    # 分类管理
    def get_categories(self):
        """获取所有分类"""
        return self.data["categories"]
    
    def add_category(self, name, description=""):
        """添加分类"""
        category = {
            "id": self.data["next_category_id"],
            "name": name,
            "description": description,
            "prompts": []
        }
        self.data["categories"].append(category)
        self.data["next_category_id"] += 1
        self._save_data()
        return category
    
    def update_category(self, category_id, name, description=""):
        """更新分类"""
        for category in self.data["categories"]:
            if category["id"] == category_id:
                category["name"] = name
                category["description"] = description
                self._save_data()
                return True
        return False
    
    def delete_category(self, category_id):
        """删除分类（及其所有提示词）"""
        self.data["categories"] = [c for c in self.data["categories"] if c["id"] != category_id]
        self._save_data()
        return True
    
    def get_category_by_id(self, category_id):
        """根据ID获取分类"""
        for category in self.data["categories"]:
            if category["id"] == category_id:
                return category
        return None
    
    # 提示词管理
    def add_prompt(self, category_id, title, content, tags="", style="", ratio=""):
        """添加提示词到指定分类"""
        category = self.get_category_by_id(category_id)
        if not category:
            return None
        
        prompt = {
            "id": self.data["next_prompt_id"],
            "title": title,
            "content": content,
            "tags": tags,
            "style": style,
            "ratio": ratio,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        category["prompts"].append(prompt)
        self.data["next_prompt_id"] += 1
        self._save_data()
        return prompt
    
    def update_prompt(self, category_id, prompt_id, title, content, tags="", style="", ratio=""):
        """更新提示词"""
        category = self.get_category_by_id(category_id)
        if not category:
            return False
        
        for prompt in category["prompts"]:
            if prompt["id"] == prompt_id:
                prompt["title"] = title
                prompt["content"] = content
                prompt["tags"] = tags
                prompt["style"] = style
                prompt["ratio"] = ratio
                prompt["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self._save_data()
                return True
        return False
    
    def delete_prompt(self, category_id, prompt_id):
        """删除提示词"""
        category = self.get_category_by_id(category_id)
        if not category:
            return False
        
        category["prompts"] = [p for p in category["prompts"] if p["id"] != prompt_id]
        self._save_data()
        return True
    
    def get_prompts_by_category(self, category_id):
        """获取指定分类的所有提示词"""
        category = self.get_category_by_id(category_id)
        if category:
            return category["prompts"]
        return []
    
    def search_prompts(self, keyword):
        """搜索提示词（按标题、内容、标签）"""
        results = []
        for category in self.data["categories"]:
            for prompt in category["prompts"]:
                if (keyword.lower() in prompt["title"].lower() or 
                    keyword.lower() in prompt["content"].lower() or 
                    keyword.lower() in prompt.get("tags", "").lower()):
                    results.append({
                        "category_name": category["name"],
                        "category_id": category["id"],
                        **prompt
                    })
        return results
    
    def move_prompt(self, from_category_id, to_category_id, prompt_id):
        """移动提示词到另一个分类"""
        from_category = self.get_category_by_id(from_category_id)
        to_category = self.get_category_by_id(to_category_id)
        
        if not from_category or not to_category:
            return False
        
        prompt = None
        for p in from_category["prompts"]:
            if p["id"] == prompt_id:
                prompt = p
                break
        
        if not prompt:
            return False
        
        from_category["prompts"] = [p for p in from_category["prompts"] if p["id"] != prompt_id]
        to_category["prompts"].append(prompt)
        self._save_data()
        return True
