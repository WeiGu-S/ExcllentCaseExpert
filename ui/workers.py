"""
异步工作线程

提供 OCR、AI 分析和测试用例生成的异步工作线程，避免阻塞 UI。
"""

from PyQt6.QtCore import QThread, pyqtSignal
from typing import Dict, List


class OCRWorker(QThread):
    """OCR 工作线程"""
    
    # 信号定义
    progress = pyqtSignal(int)  # 进度
    finished = pyqtSignal(str)  # 完成，返回文本
    error = pyqtSignal(str)  # 错误
    
    def __init__(self, ocr_engine, file_path: str):
        """初始化 OCR 工作线程
        
        Args:
            ocr_engine: OCR 引擎实例
            file_path: 文件路径
        """
        super().__init__()
        self.ocr_engine = ocr_engine
        self.file_path = file_path
    
    def run(self):
        """执行 OCR"""
        try:
            self.progress.emit(10)
            text = self.ocr_engine.extract_text(self.file_path)
            self.progress.emit(100)
            self.finished.emit(text)
        except Exception as e:
            self.error.emit(str(e))


class AIAnalysisWorker(QThread):
    """AI 分析工作线程"""
    
    # 信号定义
    progress = pyqtSignal(int)  # 进度
    finished = pyqtSignal(dict)  # 完成，返回测试要点
    error = pyqtSignal(str)  # 错误
    
    def __init__(self, analyzer, text: str):
        """初始化 AI 分析工作线程
        
        Args:
            analyzer: AI 分析器实例
            text: 需求文本
        """
        super().__init__()
        self.analyzer = analyzer
        self.text = text
    
    def run(self):
        """执行 AI 分析"""
        try:
            self.progress.emit(10)
            result = self.analyzer.extract_test_points(self.text)
            self.progress.emit(100)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class TestCaseGenerationWorker(QThread):
    """测试用例生成工作线程"""
    
    # 信号定义
    progress = pyqtSignal(int)  # 进度
    finished = pyqtSignal(list)  # 完成，返回测试用例列表
    error = pyqtSignal(str)  # 错误
    
    def __init__(self, generator, test_points: Dict):
        """初始化测试用例生成工作线程
        
        Args:
            generator: 测试用例生成器实例
            test_points: 测试要点字典
        """
        super().__init__()
        self.generator = generator
        self.test_points = test_points
    
    def run(self):
        """生成测试用例"""
        try:
            self.progress.emit(10)
            cases = self.generator.generate_test_cases(self.test_points)
            self.progress.emit(100)
            self.finished.emit(cases)
        except Exception as e:
            self.error.emit(str(e))
