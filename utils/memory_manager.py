"""内存管理模块"""

import gc
import psutil
from contextlib import contextmanager
from typing import Dict


class MemoryManager:
    """负责监控应用程序的内存使用情况，并在必要时执行垃圾回收和资源清理。"""
    
    def __init__(self, max_memory_mb: int = 1024):
        """初始化内存管理器"""
        self.max_memory_mb = max_memory_mb
        self.process = psutil.Process()
    
    def get_memory_usage(self) -> float:
        """获取当前内存使用量"""
        return self.process.memory_info().rss / 1024 / 1024
    
    def get_memory_percent(self) -> float:
        """获取内存使用百分比"""
        return self.process.memory_percent()
    
    def cleanup_if_needed(self) -> bool:
        """根据需要清理内存"""
        current_memory = self.get_memory_usage()
        if current_memory > self.max_memory_mb:
            gc.collect()
            return True
        return False
    
    @contextmanager
    def memory_efficient_processing(self):
        """内存高效处理上下文管理器,在处理完成后自动检查内存使用情况，如果内存增长超过 100MB，
        则触发垃圾回收。"""
        initial_memory = self.get_memory_usage()
        try:
            yield
        finally:
            self.cleanup_if_needed()
            final_memory = self.get_memory_usage()
            memory_delta = final_memory - initial_memory
            if memory_delta > 100:  # 增长超过 100MB
                gc.collect()
    
    def get_system_memory_info(self) -> Dict[str, float]:
        """获取系统内存信息
        
        Returns:
            包含系统内存信息的字典，包括：
            - total_mb: 总内存（MB）
            - available_mb: 可用内存（MB）
            - used_mb: 已使用内存（MB）
            - percent: 内存使用百分比
        """
        mem = psutil.virtual_memory()
        return {
            "total_mb": mem.total / 1024 / 1024,
            "available_mb": mem.available / 1024 / 1024,
            "used_mb": mem.used / 1024 / 1024,
            "percent": mem.percent
        }
