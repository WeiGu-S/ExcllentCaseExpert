"""
OCR 引擎测试模块

测试 OCR 引擎的基本功能，包括图像预处理、文本识别等。
"""

import pytest
import numpy as np
import cv2
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from core.ocr_engine import OCREngine
from utils.exceptions import OCRException
from utils.cache_manager import CacheManager


class TestOCREngineInit:
    """测试 OCR 引擎初始化"""
    
    def test_init_with_both_engines(self):
        """测试同时启用两个引擎"""
        engine = OCREngine(use_paddle=True, use_tesseract=True)
        assert engine.use_paddle is True
        assert engine.use_tesseract is True
    
    def test_init_with_paddle_only(self):
        """测试仅启用 PaddleOCR"""
        engine = OCREngine(use_paddle=True, use_tesseract=False)
        assert engine.use_paddle is True
        assert engine.use_tesseract is False
    
    def test_init_with_tesseract_only(self):
        """测试仅启用 Tesseract"""
        engine = OCREngine(use_paddle=False, use_tesseract=True)
        assert engine.use_paddle is False
        assert engine.use_tesseract is True
    
    def test_init_with_no_engines(self):
        """测试不启用任何引擎应该抛出异常"""
        with pytest.raises(OCRException) as exc_info:
            OCREngine(use_paddle=False, use_tesseract=False)
        assert "至少需要启用一个 OCR 引擎" in str(exc_info.value)
    
    def test_init_with_custom_languages(self):
        """测试自定义语言配置"""
        engine = OCREngine(languages=["en", "ch_sim"])
        assert engine.languages == ["en", "ch_sim"]
    
    def test_init_with_cache_manager(self):
        """测试使用自定义缓存管理器"""
        cache_manager = CacheManager()
        engine = OCREngine(cache_manager=cache_manager)
        assert engine.cache_manager is cache_manager


class TestImagePreprocessing:
    """测试图像预处理功能"""
    
    def test_preprocess_color_image(self):
        """测试彩色图像预处理"""
        # 创建测试图像 (100x100 BGR)
        image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        engine = OCREngine()
        processed = engine.preprocess_image(image)
        
        # 验证输出是灰度图像
        assert len(processed.shape) == 2
        assert processed.shape == (100, 100)
    
    def test_preprocess_grayscale_image(self):
        """测试灰度图像预处理"""
        # 创建测试图像 (100x100 灰度)
        image = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
        
        engine = OCREngine()
        processed = engine.preprocess_image(image)
        
        # 验证输出仍是灰度图像
        assert len(processed.shape) == 2
        assert processed.shape == (100, 100)
    
    def test_correct_skew_no_lines(self):
        """测试角度校正（无明显线条）"""
        # 创建纯色图像
        image = np.ones((100, 100), dtype=np.uint8) * 128
        
        engine = OCREngine()
        corrected = engine._correct_skew(image)
        
        # 应该返回原图像（无法检测角度）
        assert corrected.shape == image.shape


class TestExtractText:
    """测试文本提取功能"""
    
    def test_extract_text_file_not_found(self):
        """测试文件不存在的情况"""
        engine = OCREngine()
        
        with pytest.raises(OCRException) as exc_info:
            engine.extract_text("/nonexistent/file.png")
        
        assert "文件不存在" in str(exc_info.value)
    
    def test_extract_text_unsupported_format(self, tmp_path):
        """测试不支持的文件格式"""
        # 创建一个不支持的文件
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")
        
        engine = OCREngine()
        
        with pytest.raises(OCRException) as exc_info:
            engine.extract_text(str(test_file))
        
        assert "不支持的文件格式" in str(exc_info.value)
    
    @patch.object(CacheManager, 'get_ocr_cache')
    def test_extract_text_from_cache(self, mock_get_cache, tmp_path):
        """测试从缓存读取"""
        # 创建测试图像文件
        test_file = tmp_path / "test.png"
        image = np.ones((100, 100, 3), dtype=np.uint8) * 255
        cv2.imwrite(str(test_file), image)
        
        # 模拟缓存命中
        mock_get_cache.return_value = "缓存的文本内容"
        
        engine = OCREngine()
        result = engine.extract_text(str(test_file))
        
        assert result == "缓存的文本内容"
        mock_get_cache.assert_called_once()


class TestMergeResults:
    """测试结果融合功能
    
    这些测试直接测试 _merge_results 方法的逻辑，
    不依赖于 OCR 引擎的初始化状态。
    """
    
    @pytest.fixture
    def engine(self):
        """创建 OCR 引擎实例"""
        return OCREngine()
    
    def test_merge_paddle_only(self, engine):
        """测试仅有 PaddleOCR 结果"""
        paddle_result = ["第一行", "第二行", "第三行"]
        tesseract_result = []
        
        merged = engine._merge_results(paddle_result, tesseract_result)
        
        assert merged == "第一行\n第二行\n第三行"
    
    def test_merge_tesseract_only(self, engine):
        """测试仅有 Tesseract 结果"""
        paddle_result = []
        tesseract_result = ["Line 1", "Line 2"]
        
        merged = engine._merge_results(paddle_result, tesseract_result)
        
        assert merged == "Line 1\nLine 2"
    
    def test_merge_both_results_paddle_preferred(self, engine):
        """测试两个引擎都有结果，PaddleOCR 结果更长时优先使用"""
        # PaddleOCR 结果更长
        paddle_result = ["这是一段比较长的中文文本内容", "第二行也很长"]
        tesseract_result = ["Short", "Text"]
        
        merged = engine._merge_results(paddle_result, tesseract_result)
        
        # 应该使用 PaddleOCR 结果（更长）
        assert "这是一段比较长的中文文本内容" in merged
    
    def test_merge_both_results_tesseract_much_longer(self, engine):
        """测试两个引擎都有结果，Tesseract 明显更长时使用 Tesseract"""
        paddle_result = ["短"]
        tesseract_result = ["这是一段很长的文本内容，明显比 PaddleOCR 的结果要长很多，超过了1.5倍的阈值"]
        
        merged = engine._merge_results(paddle_result, tesseract_result)
        
        # 应该使用 Tesseract 结果（长度超过 1.5 倍）
        assert "这是一段很长的文本内容" in merged
    
    def test_merge_empty_results(self, engine):
        """测试两个引擎都没有结果"""
        paddle_result = []
        tesseract_result = []
        
        merged = engine._merge_results(paddle_result, tesseract_result)
        
        assert merged == ""


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
