"""
自定义异常类模块

定义系统中使用的所有自定义异常类型，提供统一的异常处理机制。
"""

import functools
import traceback
from typing import Callable, Any, Optional


class ExcellentCaseExpertException(Exception):
    """ExcellentCaseExpert 基础异常类
    
    所有自定义异常的基类，提供统一的异常处理接口。
    """
    
    def __init__(self, message: str, details: Optional[dict] = None):
        """初始化异常
        
        Args:
            message: 异常消息
            details: 异常详细信息字典
        """
        self.message = message
        self.details = details or {}
        super().__init__(self.message)
    
    def __str__(self) -> str:
        """返回异常的字符串表示"""
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} ({details_str})"
        return self.message
    
    def to_dict(self) -> dict:
        """将异常转换为字典格式
        
        Returns:
            包含异常信息的字典
        """
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "details": self.details
        }


class OCRException(ExcellentCaseExpertException):
    """OCR 识别异常
    
    当 OCR 识别过程中发生错误时抛出此异常。
    """
    
    def __init__(self, message: str, file_path: Optional[str] = None, 
                 engine: Optional[str] = None, details: Optional[dict] = None):
        """初始化 OCR 异常
        
        Args:
            message: 异常消息
            file_path: 发生错误的文件路径
            engine: 使用的 OCR 引擎名称
            details: 其他详细信息
        """
        exception_details = details or {}
        if file_path:
            exception_details["file_path"] = file_path
        if engine:
            exception_details["engine"] = engine
        super().__init__(message, exception_details)


class AIAnalysisException(ExcellentCaseExpertException):
    """AI 分析异常
    
    当 AI 模型调用或分析过程中发生错误时抛出此异常。
    """
    
    def __init__(self, message: str, provider: Optional[str] = None,
                 model_name: Optional[str] = None, details: Optional[dict] = None):
        """初始化 AI 分析异常
        
        Args:
            message: 异常消息
            provider: AI 提供商名称
            model_name: 模型名称
            details: 其他详细信息
        """
        exception_details = details or {}
        if provider:
            exception_details["provider"] = provider
        if model_name:
            exception_details["model_name"] = model_name
        super().__init__(message, exception_details)


class ExportException(ExcellentCaseExpertException):
    """导出异常
    
    当测试用例导出过程中发生错误时抛出此异常。
    """
    
    def __init__(self, message: str, export_format: Optional[str] = None,
                 output_path: Optional[str] = None, details: Optional[dict] = None):
        """初始化导出异常
        
        Args:
            message: 异常消息
            export_format: 导出格式 (json/xmind)
            output_path: 输出文件路径
            details: 其他详细信息
        """
        exception_details = details or {}
        if export_format:
            exception_details["export_format"] = export_format
        if output_path:
            exception_details["output_path"] = output_path
        super().__init__(message, exception_details)


class ConfigException(ExcellentCaseExpertException):
    """配置异常
    
    当配置加载、验证或保存过程中发生错误时抛出此异常。
    """
    
    def __init__(self, message: str, config_key: Optional[str] = None,
                 config_file: Optional[str] = None, details: Optional[dict] = None):
        """初始化配置异常
        
        Args:
            message: 异常消息
            config_key: 配置项键名
            config_file: 配置文件路径
            details: 其他详细信息
        """
        exception_details = details or {}
        if config_key:
            exception_details["config_key"] = config_key
        if config_file:
            exception_details["config_file"] = config_file
        super().__init__(message, exception_details)


def handle_exceptions(logger=None, default_return: Any = None, 
                     reraise: bool = False):
    """统一异常处理装饰器
    
    用于捕获和处理函数执行过程中的异常，提供统一的日志记录和错误处理。
    
    Args:
        logger: 日志记录器实例，如果提供则记录异常信息
        default_return: 发生异常时的默认返回值
        reraise: 是否重新抛出异常
    
    Returns:
        装饰器函数
    
    Example:
        @handle_exceptions(logger=my_logger, default_return=None, reraise=False)
        def my_function():
            # 函数实现
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ExcellentCaseExpertException as e:
                # 处理自定义异常
                if logger:
                    logger.log_error(
                        e,
                        context={
                            "function": func.__name__,
                            "args": str(args)[:100],  # 限制长度避免日志过大
                            "kwargs": str(kwargs)[:100],
                            "exception_details": e.details
                        }
                    )
                
                if reraise:
                    raise
                return default_return
            
            except Exception as e:
                # 处理其他异常
                if logger:
                    logger.log_error(
                        e,
                        context={
                            "function": func.__name__,
                            "args": str(args)[:100],
                            "kwargs": str(kwargs)[:100],
                            "traceback": traceback.format_exc()
                        }
                    )
                
                if reraise:
                    raise
                return default_return
        
        return wrapper
    return decorator
