"""
异步工作线程

提供 OCR、AI 分析和测试用例生成的异步工作线程，避免阻塞 UI。
"""

from PyQt6.QtCore import QThread, pyqtSignal
from typing import Dict, List
from utils.log_manager import get_logger


class OCRWorker(QThread):
    """OCR 工作线程"""
    
    # 信号定义
    progress = pyqtSignal(int)  # 进度百分比 (0-100)
    status = pyqtSignal(str)  # 状态消息
    finished = pyqtSignal(str)  # 完成，返回识别的文本
    error = pyqtSignal(str)  # 错误消息
    
    def __init__(self, ocr_engine, file_path: str):
        """初始化 OCR 工作线程"""
        super().__init__()
        self.ocr_engine = ocr_engine
        self.file_path = file_path
        self.logger = get_logger()
    
    def run(self):
        """执行 OCR 识别"""
        try:
            self.logger.info(f"OCR 工作线程启动: {self.file_path}")
            
            import time
            
            # 阶段 1: 开始处理
            self.progress.emit(5)
            self.status.emit("正在加载文件...")
            time.sleep(0.2)
            
            # 阶段 2: 图像预处理
            self.progress.emit(15)
            self.status.emit("正在读取图像...")
            time.sleep(0.3)
            
            self.progress.emit(25)
            self.status.emit("正在预处理图像（去噪、增强对比度）...")
            time.sleep(0.3)
            
            # 阶段 3: OCR 识别（主要耗时操作）
            self.progress.emit(40)
            self.status.emit("正在识别文字（这可能需要几秒钟）...")
            
            text = self.ocr_engine.extract_text(self.file_path)
            
            # 阶段 4: 后处理
            self.progress.emit(90)
            self.status.emit("正在整理识别结果...")
            time.sleep(0.2)
            
            # 阶段 5: 完成
            self.progress.emit(100)
            self.status.emit("OCR 识别完成")
            
            self.logger.info(f"OCR 识别成功，文本长度: {len(text)}")
            self.finished.emit(text)
            
        except Exception as e:
            self.logger.error(f"OCR 识别失败: {str(e)}")
            self.error.emit(str(e))


class AIAnalysisWorker(QThread):
    """AI 分析工作线程"""
    
    # 信号定义
    progress = pyqtSignal(int)  # 进度百分比 (0-100)
    status = pyqtSignal(str)  # 状态消息
    finished = pyqtSignal(dict)  # 完成，返回测试要点字典
    error = pyqtSignal(str)  # 错误消息
    
    def __init__(self, analyzer, text: str):
        """初始化 AI 分析工作线程"""
        super().__init__()
        self.analyzer = analyzer
        self.text = text
        self.logger = get_logger()
    
    def run(self):
        """执行 AI 分析"""
        try:
            self.logger.info(f"AI 分析工作线程启动，文本长度: {len(self.text)}")
            
            # 阶段 1: 准备分析
            self.progress.emit(5)
            self.status.emit("正在准备 AI 分析...")
            
            # 阶段 2: 构建提示词
            self.progress.emit(10)
            self.status.emit("正在构建分析提示词...")
            
            # 阶段 3: 调用 AI 模型（主要耗时操作）
            self.progress.emit(15)
            self.status.emit("正在连接 AI 服务...")
            
            import time
            import threading
            
            # 创建一个标志来跟踪 AI 调用是否完成
            ai_completed = False
            result = None
            error = None
            
            # 在单独的线程中调用 AI
            def call_ai():
                nonlocal result, error, ai_completed
                try:
                    self.logger.info("开始调用 AI 模型...")
                    result = self.analyzer.extract_test_points(self.text)
                    self.logger.info("AI 模型调用成功")
                except Exception as e:
                    self.logger.error(f"AI 模型调用失败: {str(e)}")
                    error = e
                finally:
                    ai_completed = True
            
            # 启动 AI 调用
            ai_thread = threading.Thread(target=call_ai, daemon=True)
            ai_thread.start()
            
            # 进度更新配置
            progress_value = 20
            progress_messages = [
                "正在发送请求到 AI 模型...",
                "AI 模型正在分析需求文本...",
                "正在提取功能测试要点...",
                "正在提取兼容性测试要点...",
                "正在提取易用性测试要点...",
                "正在整理分析结果...",
            ]
            
            message_index = 0
            elapsed_time = 0
            max_wait_time = 300  # 最多等待 5 分钟
            
            # 循环更新进度，直到 AI 完成或超时
            while not ai_completed and elapsed_time < max_wait_time:
                # 更新进度条（最多到 85%）
                if progress_value < 85:
                    progress_value = min(85, progress_value + 3)
                    self.progress.emit(progress_value)
                
                # 更新状态消息（循环显示）
                if message_index < len(progress_messages):
                    self.status.emit(progress_messages[message_index])
                    message_index += 1
                else:
                    # 循环回到开始，但添加提示
                    message_index = 0
                    self.status.emit(f"AI 模型正在深度分析... (已用时 {elapsed_time}秒)")
                
                time.sleep(2)  # 每 2 秒更新一次
                elapsed_time += 2
            
            # 检查是否超时
            if not ai_completed:
                self.logger.error(f"AI 分析超时，已等待 {elapsed_time} 秒")
                raise TimeoutError(f"AI 分析超时，已等待 {elapsed_time} 秒。请检查网络连接和 API 配置。")
            
            # 等待 AI 线程完成（应该已经完成了）
            ai_thread.join(timeout=5)
            
            # 检查是否有错误
            if error:
                raise error
            
            # 检查结果是否有效
            if result is None:
                raise ValueError("AI 分析返回空结果")
            
            # 阶段 4: 解析和验证结果
            self.progress.emit(90)
            self.status.emit("正在验证分析结果...")
            time.sleep(0.3)
            
            # 阶段 5: 完成
            self.progress.emit(100)
            self.status.emit("AI 分析完成")
            
            test_point_count = len(result.get("test_points", []))
            self.logger.info(f"AI 分析成功，提取测试要点数: {test_point_count}")
            self.finished.emit(result)
            
        except Exception as e:
            self.logger.error(f"AI 分析失败: {str(e)}")
            self.error.emit(str(e))


class TestCaseGenerationWorker(QThread):
    """测试用例生成工作线程"""
    
    # 信号定义
    progress = pyqtSignal(int)  # 进度百分比 (0-100)
    status = pyqtSignal(str)  # 状态消息
    finished = pyqtSignal(list)  # 完成，返回测试用例列表
    error = pyqtSignal(str)  # 错误消息
    
    def __init__(self, generator, test_points: Dict):
        """初始化测试用例生成工作线程
        
        Args:
            generator: 测试用例生成器实例
            test_points: 测试要点字典，包含 feature_name 和 test_points 列表
        """
        super().__init__()
        self.generator = generator
        self.test_points = test_points
        self.logger = get_logger()
    
    def run(self):
        """生成测试用例"""
        try:
            test_point_count = len(self.test_points.get("test_points", []))
            self.logger.info(f"测试用例生成工作线程启动，测试要点数: {test_point_count}")
            
            # 阶段 1: 准备生成
            self.progress.emit(5)
            self.status.emit("正在准备生成测试用例...")
            
            import time
            
            # 阶段 2: 分析测试要点
            self.progress.emit(10)
            self.status.emit(f"正在分析 {test_point_count} 个测试要点...")
            time.sleep(0.2)
            
            # 阶段 3: 生成正向用例
            self.progress.emit(20)
            self.status.emit("正在生成正向测试用例...")
            time.sleep(0.3)
            
            # 阶段 4: 生成负向用例
            self.progress.emit(40)
            self.status.emit("正在生成负向测试用例...")
            time.sleep(0.3)
            
            # 阶段 5: 生成边界用例
            self.progress.emit(55)
            self.status.emit("正在生成边界测试用例...")
            time.sleep(0.3)
            
            # 阶段 6: 生成异常用例
            self.progress.emit(70)
            self.status.emit("正在生成异常测试用例...")
            time.sleep(0.2)
            
            # 阶段 7: 执行生成（主要操作）
            self.progress.emit(75)
            self.status.emit("正在整合测试用例...")
            
            cases = self.generator.generate_test_cases(self.test_points)
            
            # 阶段 8: 验证和去重
            self.progress.emit(90)
            self.status.emit(f"正在验证和去重 {len(cases)} 个测试用例...")
            time.sleep(0.2)
            
            # 阶段 9: 完成
            self.progress.emit(100)
            self.status.emit("测试用例生成完成")
            
            self.logger.info(f"测试用例生成成功，用例数: {len(cases)}")
            self.finished.emit(cases)
            
        except Exception as e:
            self.logger.error(f"测试用例生成失败: {str(e)}")
            self.error.emit(str(e))
