"""缓存管理"""

import hashlib
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Any


class CacheManager:
    """缓存管理器"""
    
    def __init__(self, cache_dir: str = "~/.excellentcase/cache"):
        """初始化缓存管理器"""
        self.cache_dir = Path(cache_dir).expanduser()
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建子目录
        self.ocr_cache_dir = self.cache_dir / "ocr"
        self.ai_cache_dir = self.cache_dir / "ai"
        self.ocr_cache_dir.mkdir(exist_ok=True)
        self.ai_cache_dir.mkdir(exist_ok=True)
    
    def get_ocr_cache(self, file_path: str) -> Optional[str]:
        """获取 OCR 缓存"""
        cache_key = self._get_file_hash(file_path)
        cache_file = self.ocr_cache_dir / f"{cache_key}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # 检查是否过期 (7天)
            cached_time = datetime.fromisoformat(cache_data['timestamp'])
            if datetime.now() - cached_time > timedelta(days=7):
                cache_file.unlink()
                return None
            
            return cache_data['text']
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # 缓存文件损坏，删除并返回 None
            cache_file.unlink()
            return None
    
    def set_ocr_cache(self, file_path: str, text: str):
        """设置 OCR 缓存"""
        cache_key = self._get_file_hash(file_path)
        cache_file = self.ocr_cache_dir / f"{cache_key}.json"
        
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'file_path': file_path,
            'text': text
        }
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
    
    def get_ai_cache(self, text: str, model_name: str) -> Optional[dict]:
        """获取 AI 分析缓存"""
        cache_key = self._get_text_hash(text, model_name)
        cache_file = self.ai_cache_dir / f"{cache_key}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # 检查是否过期 (24小时)
            cached_time = datetime.fromisoformat(cache_data['timestamp'])
            if datetime.now() - cached_time > timedelta(hours=24):
                cache_file.unlink()
                return None
            
            return cache_data['result']
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # 缓存文件损坏，删除并返回 None
            cache_file.unlink()
            return None
    
    def set_ai_cache(self, text: str, model_name: str, result: dict):
        """设置 AI 分析缓存"""
        cache_key = self._get_text_hash(text, model_name)
        cache_file = self.ai_cache_dir / f"{cache_key}.json"
        
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'model_name': model_name,
            'result': result
        }
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
    
    def cleanup_expired_cache(self):
        """清理过期缓存"""
        # 清理 OCR 缓存 (7天)
        self._cleanup_directory(self.ocr_cache_dir, days=7)
        # 清理 AI 缓存 (24小时)
        self._cleanup_directory(self.ai_cache_dir, hours=24)
    
    def _get_file_hash(self, file_path: str) -> str:
        """计算文件 MD5 哈希"""
        md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5.update(chunk)
        return md5.hexdigest()
    
    def _get_text_hash(self, text: str, model_name: str) -> str:
        """计算文本哈希"""
        content = f"{text}_{model_name}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def _cleanup_directory(self, directory: Path, days: int = 0, hours: int = 0):
        """清理目录中的过期文件"""
        expiry_time = datetime.now() - timedelta(days=days, hours=hours)
        for cache_file in directory.glob("*.json"):
            try:
                # 获取文件修改时间
                file_mtime = datetime.fromtimestamp(cache_file.stat().st_mtime)
                if file_mtime < expiry_time:
                    cache_file.unlink()
            except (OSError, FileNotFoundError):
                # 文件可能已被删除或无法访问，跳过
                continue
