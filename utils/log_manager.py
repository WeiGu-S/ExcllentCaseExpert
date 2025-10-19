"""
日志管理
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import json
from datetime import datetime
import traceback
from typing import Optional, Dict, Any


class StructuredLogger:
    """结构化日志管理器
    提供统一的日志记录接口
    """
    
    def __init__(self, name: str = "ExcellentCaseExpert", log_dir: str = "logs"):
        """初始化日志管理器"""
        self.logger = logging.getLogger(name)
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True, parents=True)
        self.setup_handlers()
    
    def setup_handlers(self):
        """设置日志处理器"""
        # 清除已有的处理器，避免重复
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        # 文件处理器 - 所有日志
        file_handler = RotatingFileHandler(
            self.log_dir / "app.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        # 文件处理器 - 错误日志
        error_handler = RotatingFileHandler(
            self.log_dir / "error.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        error_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 添加处理器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(error_handler)
        self.logger.addHandler(console_handler)
        self.logger.setLevel(logging.DEBUG)
    
    def log_operation(self, operation: str, **kwargs):
        """记录操作日志

        Example:
            logger.log_operation("OCR_START", file_path="/path/to/file.png", file_size=1024)
        """
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            **kwargs
        }
        self.logger.info(f"OPERATION: {json.dumps(log_data, ensure_ascii=False)}")
    
    def log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None):
        """记录错误日志"""
        error_data = {
            "timestamp": datetime.now().isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "context": context or {}
        }
        self.logger.error(f"ERROR: {json.dumps(error_data, ensure_ascii=False)}")
    
    def log_performance(self, operation: str, duration: float, **kwargs):
        """记录性能日志"""
        perf_data = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "duration_seconds": round(duration, 3),
            **kwargs
        }
        self.logger.info(f"PERFORMANCE: {json.dumps(perf_data, ensure_ascii=False)}")
    
    def debug(self, message: str, **kwargs):
        """记录调试日志"""
        if kwargs:
            message = f"{message} | {json.dumps(kwargs, ensure_ascii=False)}"
        self.logger.debug(message)
    
    def info(self, message: str, **kwargs):
        """记录信息日志"""
        if kwargs:
            message = f"{message} | {json.dumps(kwargs, ensure_ascii=False)}"
        self.logger.info(message)
    
    def warning(self, message: str, **kwargs):
        """记录警告日志"""
        if kwargs:
            message = f"{message} | {json.dumps(kwargs, ensure_ascii=False)}"
        self.logger.warning(message)
    
    def error(self, message: str, **kwargs):
        """记录错误日志"""
        if kwargs:
            message = f"{message} | {json.dumps(kwargs, ensure_ascii=False)}"
        self.logger.error(message)
    
    def cleanup_old_logs(self, days: int = 30):
        """清理过期日志文件"""
        from datetime import timedelta
        
        expiry_time = datetime.now() - timedelta(days=days)
        expiry_timestamp = expiry_time.timestamp()
        
        cleaned_count = 0
        for log_file in self.log_dir.glob("*.log*"):
            try:
                if log_file.stat().st_mtime < expiry_timestamp:
                    log_file.unlink()
                    cleaned_count += 1
            except Exception as e:
                self.logger.warning(f"清理日志文件失败: {log_file}, 错误: {e}")
        
        if cleaned_count > 0:
            self.logger.info(f"清理了 {cleaned_count} 个过期日志文件")


# 全局日志实例
_global_logger: Optional[StructuredLogger] = None


def get_logger(name: str = "ExcellentCaseExpert", 
               log_dir: str = "logs") -> StructuredLogger:
    """获取全局日志实例"""
    global _global_logger
    if _global_logger is None:
        _global_logger = StructuredLogger(name, log_dir)
    return _global_logger
