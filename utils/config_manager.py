"""配置管理"""

from pydantic import BaseModel, Field, field_validator
from typing import List
from pathlib import Path
import yaml
import os
import re


class AIModelConfig(BaseModel):
    """AI 模型配置"""
    provider: str = Field(default="openai", description="AI 提供商")
    api_key: str = Field(default="your_api_key_here", description="API 密钥")
    base_url: str = Field(
        default="https://api.openai.com/v1",
        description="API 基础 URL"
    )
    model_name: str = Field(default="gpt-4o-mini", description="模型名称")
    max_tokens: int = Field(default=2000, description="最大 token 数")
    temperature: float = Field(default=0.7, description="温度参数")
    
    @field_validator('api_key')
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """验证 API Key"""
        # 允许空值或默认占位符，但会在实际使用时提示用户配置
        if not v:
            return "your_api_key_here"
        return v
    
    @field_validator('provider')
    @classmethod
    def validate_provider(cls, v: str) -> str:
        """验证提供商名称"""
        valid_providers = ["openai", "qwen", "deepseek", "custom"]
        if v not in valid_providers:
            raise ValueError(
                f"不支持的提供商: {v}，支持的提供商: {', '.join(valid_providers)}"
            )
        return v
    
    @field_validator('max_tokens')
    @classmethod
    def validate_max_tokens(cls, v: int) -> int:
        """验证最大 token 数"""
        if v < 100 or v > 10000:
            raise ValueError("max_tokens 必须在 100-10000 之间")
        return v
    
    @field_validator('temperature')
    @classmethod
    def validate_temperature(cls, v: float) -> float:
        """验证温度参数"""
        if v < 0.0 or v > 2.0:
            raise ValueError("temperature 必须在 0.0-2.0 之间")
        return v


class OCRConfig(BaseModel):
    """OCR 配置"""
    use_paddle_ocr: bool = Field(default=True, description="使用 PaddleOCR")
    use_tesseract: bool = Field(default=True, description="使用 Tesseract")
    languages: List[str] = Field(
        default=["ch_sim", "en"], 
        description="OCR 语言"
    )
    max_file_size_mb: int = Field(default=50, description="最大文件大小(MB)")
    
    @field_validator('max_file_size_mb')
    @classmethod
    def validate_max_file_size(cls, v: int) -> int:
        """验证最大文件大小"""
        if v < 1 or v > 500:
            raise ValueError("max_file_size_mb 必须在 1-500 之间")
        return v
    
    @field_validator('use_paddle_ocr', 'use_tesseract')
    @classmethod
    def validate_at_least_one_engine(cls, v: bool, info) -> bool:
        """验证至少启用一个 OCR 引擎"""
        # 注意：这个验证在单个字段级别无法完全实现
        # 需要在 AppConfig 级别进行额外验证
        return v


class PerformanceConfig(BaseModel):
    """性能配置"""
    max_concurrent_tasks: int = Field(default=3, description="最大并发任务数")
    memory_cleanup_interval: int = Field(
        default=30, 
        description="内存清理间隔(秒)"
    )
    max_memory_mb: int = Field(default=1024, description="最大内存使用(MB)")
    
    @field_validator('max_concurrent_tasks')
    @classmethod
    def validate_max_concurrent_tasks(cls, v: int) -> int:
        """验证最大并发任务数"""
        if v < 1 or v > 10:
            raise ValueError("max_concurrent_tasks 必须在 1-10 之间")
        return v
    
    @field_validator('memory_cleanup_interval')
    @classmethod
    def validate_memory_cleanup_interval(cls, v: int) -> int:
        """验证内存清理间隔"""
        if v < 10 or v > 300:
            raise ValueError("memory_cleanup_interval 必须在 10-300 秒之间")
        return v
    
    @field_validator('max_memory_mb')
    @classmethod
    def validate_max_memory(cls, v: int) -> int:
        """验证最大内存使用"""
        if v < 256 or v > 8192:
            raise ValueError("max_memory_mb 必须在 256-8192 之间")
        return v


class UIConfig(BaseModel):
    """UI 配置"""
    theme: str = Field(default="light", description="主题")
    language: str = Field(default="zh_CN", description="语言")
    window_width: int = Field(default=1200, description="窗口宽度")
    window_height: int = Field(default=800, description="窗口高度")
    
    @field_validator('theme')
    @classmethod
    def validate_theme(cls, v: str) -> str:
        """验证主题"""
        valid_themes = ["light", "dark", "auto"]
        if v not in valid_themes:
            raise ValueError(
                f"不支持的主题: {v}，支持的主题: {', '.join(valid_themes)}"
            )
        return v
    
    @field_validator('language')
    @classmethod
    def validate_language(cls, v: str) -> str:
        """验证语言"""
        valid_languages = ["zh_CN", "en_US"]
        if v not in valid_languages:
            raise ValueError(
                f"不支持的语言: {v}，支持的语言: {', '.join(valid_languages)}"
            )
        return v
    
    @field_validator('window_width')
    @classmethod
    def validate_window_width(cls, v: int) -> int:
        """验证窗口宽度"""
        if v < 800 or v > 3840:
            raise ValueError("window_width 必须在 800-3840 之间")
        return v
    
    @field_validator('window_height')
    @classmethod
    def validate_window_height(cls, v: int) -> int:
        """验证窗口高度"""
        if v < 600 or v > 2160:
            raise ValueError("window_height 必须在 600-2160 之间")
        return v


class AppConfig(BaseModel):
    """应用配置"""
    ai_model: AIModelConfig
    ocr: OCRConfig
    performance: PerformanceConfig
    ui: UIConfig
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8"
    }
    
    def model_post_init(self, __context) -> None:
        """模型初始化后的验证"""
        # 验证至少启用一个 OCR 引擎
        if not self.ocr.use_paddle_ocr and not self.ocr.use_tesseract:
            raise ValueError("至少需要启用一个 OCR 引擎")
    
    @classmethod
    def load_from_file(cls, config_path: str = "config.yaml") -> "AppConfig":
        """从 YAML 文件加载配置"""
        config_file = Path(config_path)
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            # 处理环境变量替换
            config_data = cls._resolve_env_variables(config_data)
            
            return cls(**config_data)
        else:
            # 创建默认配置
            default_config = cls.create_default()
            default_config.save_to_file(config_path)
            return default_config
    
    def save_to_file(self, config_path: str = "config.yaml") -> None:
        """保存配置到文件"""
        config_file = Path(config_path)
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(
                self.model_dump(), 
                f, 
                allow_unicode=True,
                default_flow_style=False,
                sort_keys=False
            )
    
    @classmethod
    def create_default(cls) -> "AppConfig":
        """创建默认配置"""
        return cls(
            ai_model=AIModelConfig(api_key="your_api_key_here"),
            ocr=OCRConfig(),
            performance=PerformanceConfig(),
            ui=UIConfig()
        )
    
    @staticmethod
    def _resolve_env_variables(config_data: dict) -> dict:
        """递归解析配置中的环境变量"""
        if isinstance(config_data, dict):
            return {
                key: AppConfig._resolve_env_variables(value)
                for key, value in config_data.items()
            }
        elif isinstance(config_data, list):
            return [
                AppConfig._resolve_env_variables(item)
                for item in config_data
            ]
        elif isinstance(config_data, str):
            # 匹配 ${VAR_NAME} 格式
            pattern = r'\$\{([^}]+)\}'
            matches = re.findall(pattern, config_data)
            
            result = config_data
            for var_name in matches:
                env_value = os.environ.get(var_name, '')
                result = result.replace(f'${{{var_name}}}', env_value)
            
            return result
        else:
            return config_data
