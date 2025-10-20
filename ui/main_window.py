"""
PyQt6 主窗口

实现应用程序的主窗口，包括工具栏、状态栏、界面布局和核心功能。
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QToolBar, QProgressBar, QLabel, QFileDialog, QMessageBox, QDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QSize
from PyQt6.QtGui import QAction
from pathlib import Path
from typing import Optional, List, Dict

from utils.config_manager import AppConfig
from utils.log_manager import get_logger
from utils.exceptions import handle_exceptions
from core.ocr_engine import OCREngine
from core.ai_model_provider import AIModelFactory
from core.ai_test_point_analyzer import AITestPointAnalyzer
from core.test_case_generator import TestCaseGenerator
from core.export_manager import ExportManager
from ui.widgets.ocr_result_widget import OCRResultWidget
from ui.widgets.test_point_widget import TestPointWidget
from ui.widgets.test_case_widget import TestCaseWidget
from ui.styles import get_theme_stylesheet


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        """初始化主窗口"""
        super().__init__()
        
        # 加载配置
        self.config = AppConfig.load_from_file()
        self.logger = get_logger()
        
        # 初始化核心组件
        self.ocr_engine: Optional[OCREngine] = None
        self.ai_analyzer: Optional[AITestPointAnalyzer] = None
        self.test_case_generator: Optional[TestCaseGenerator] = None
        self.export_manager: Optional[ExportManager] = None
        
        # 数据存储
        self.current_file_path: Optional[str] = None
        self.ocr_text: str = ""
        self.test_points: Optional[Dict] = None
        self.test_cases: List[Dict] = []
        
        # 工作线程
        self.ocr_worker: Optional[QThread] = None
        self.ai_worker: Optional[QThread] = None
        self.case_worker: Optional[QThread] = None
        
        # 初始化界面
        self.init_ui()
        
        # 初始化核心组件
        self._init_core_components()
        
        self.logger.info("主窗口初始化完成")
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("ExcellentCaseExpert - AI 测试用例生成系统（by @WeiGu-S）")
        self.setGeometry(
            100, 100,
            self.config.ui.window_width,
            self.config.ui.window_height
        )
        
        # 应用样式表
        self.setStyleSheet(get_theme_stylesheet(self.config.ui.theme))
        
        # 创建工具栏
        self.create_toolbar()
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # OCR 结果区域（左侧）
        self.ocr_widget = OCRResultWidget()
        splitter.addWidget(self.ocr_widget)
        
        # 右侧分割器
        right_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # 测试要点区域（右上）
        self.test_point_widget = TestPointWidget()
        right_splitter.addWidget(self.test_point_widget)
        
        # 测试用例区域（右下）
        self.test_case_widget = TestCaseWidget()
        right_splitter.addWidget(self.test_case_widget)
        
        splitter.addWidget(right_splitter)
        
        # 设置分割比例
        splitter.setSizes([400, 800])
        right_splitter.setSizes([300, 500])
        
        main_layout.addWidget(splitter)
        
        # 创建状态栏
        self.create_statusbar()
        
        self.logger.debug("界面初始化完成")
    
    def create_toolbar(self):
        """创建工具栏"""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        # 导入按钮
        import_action = QAction("📁 导入文档", self)
        import_action.setStatusTip("导入需求文档（支持 PNG、JPG、PDF）")
        import_action.setToolTip("导入需求文档\n支持格式：PNG、JPG、PDF")
        import_action.triggered.connect(self.import_document)
        toolbar.addAction(import_action)
        
        toolbar.addSeparator()
        
        # OCR 按钮
        ocr_action = QAction("🔍 OCR 识别", self)
        ocr_action.setStatusTip("对导入的文档进行 OCR 文字识别")
        ocr_action.setToolTip("OCR 文字识别\n提取文档中的文字内容")
        ocr_action.triggered.connect(self.start_ocr)
        toolbar.addAction(ocr_action)
        self.ocr_action = ocr_action
        self.ocr_action.setEnabled(False)
        
        # AI 分析按钮
        ai_action = QAction("🤖 AI 分析", self)
        ai_action.setStatusTip("使用 AI 分析需求文本，提取测试要点")
        ai_action.setToolTip("AI 智能分析\n自动提取测试要点")
        ai_action.triggered.connect(self.start_ai_analysis)
        toolbar.addAction(ai_action)
        self.ai_action = ai_action
        self.ai_action.setEnabled(False)
        
        # 生成用例按钮
        generate_action = QAction("📋 生成用例", self)
        generate_action.setStatusTip("根据测试要点生成详细测试用例")
        generate_action.setToolTip("生成测试用例\n基于测试要点自动生成")
        generate_action.triggered.connect(self.generate_test_cases)
        toolbar.addAction(generate_action)
        self.generate_action = generate_action
        self.generate_action.setEnabled(False)
        
        toolbar.addSeparator()
        
        # 导出按钮
        export_action = QAction("💾 导出", self)
        export_action.setStatusTip("导出测试用例为 JSON 或 XMind 格式")
        export_action.setToolTip("导出测试用例\n支持 JSON 和 XMind 格式")
        export_action.triggered.connect(self.export_cases)
        toolbar.addAction(export_action)
        self.export_action = export_action
        self.export_action.setEnabled(False)
        
        toolbar.addSeparator()
        
        # 设置按钮
        settings_action = QAction("⚙️ 设置", self)
        settings_action.setStatusTip("打开设置对话框")
        settings_action.setToolTip("系统设置\n配置 AI 模型和 OCR 参数")
        settings_action.triggered.connect(self.open_settings)
        toolbar.addAction(settings_action)
        
        self.logger.debug("工具栏创建完成")
    
    def create_statusbar(self):
        """创建状态栏"""
        self.statusbar = self.statusBar()
        
        # 状态标签
        self.status_label = QLabel("就绪")
        self.statusbar.addWidget(self.status_label)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setVisible(False)
        self.statusbar.addPermanentWidget(self.progress_bar)
        
        # 模型标签
        self.model_label = QLabel(f"模型: {self.config.ai_model.model_name}")
        self.statusbar.addPermanentWidget(self.model_label)

        # # author
        # self.author_label = QLabel("by @未卿尘")
        # self.statusbar.addPermanentWidget(self.author_label)
        
        self.logger.debug("状态栏创建完成")
    
    def _init_core_components(self):
        """初始化核心组件"""
        try:
            # 初始化 OCR 引擎
            self.ocr_engine = OCREngine(
                use_paddle=self.config.ocr.use_paddle_ocr,
                use_tesseract=self.config.ocr.use_tesseract,
                languages=self.config.ocr.languages
            )
            
            # 初始化 AI 模型提供商
            model_provider = AIModelFactory.create_provider(
                provider_name=self.config.ai_model.provider,
                api_key=self.config.ai_model.api_key,
                base_url=self.config.ai_model.base_url,
                model_name=self.config.ai_model.model_name,
                timeout=120,  # 设置 2 分钟超时
                max_retries=3  # 最多重试 3 次
            )
            
            # 初始化 AI 分析器
            self.ai_analyzer = AITestPointAnalyzer(model_provider)
            
            # 初始化测试用例生成器
            self.test_case_generator = TestCaseGenerator()
            
            # 初始化导出管理器
            self.export_manager = ExportManager()
            
            self.logger.info("核心组件初始化完成")
            
        except Exception as e:
            self.logger.log_error(e, {"operation": "init_core_components"})
            QMessageBox.critical(
                self,
                "初始化失败",
                f"核心组件初始化失败：{str(e)}\n\n请检查配置文件。"
            )
    
    def import_document(self):
        """导入文档"""
        try:
            self.logger.log_operation("import_document_start")
            
            # 打开文件对话框
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "选择需求文档",
                "",
                "支持的文件 (*.png *.jpg *.jpeg *.pdf);;图片文件 (*.png *.jpg *.jpeg);;PDF 文件 (*.pdf);;所有文件 (*.*)"
            )
            
            if not file_path:
                self.logger.debug("用户取消了文件选择")
                return
            
            # 验证文件
            file_path_obj = Path(file_path)
            
            # 检查文件是否存在
            if not file_path_obj.exists():
                QMessageBox.warning(
                    self,
                    "文件不存在",
                    f"文件不存在：{file_path}"
                )
                return
            
            # 检查文件大小
            file_size_mb = file_path_obj.stat().st_size / (1024 * 1024)
            if file_size_mb > self.config.ocr.max_file_size_mb:
                QMessageBox.warning(
                    self,
                    "文件过大",
                    f"文件大小 {file_size_mb:.2f} MB 超过限制 {self.config.ocr.max_file_size_mb} MB"
                )
                return
            
            # 检查文件格式
            supported_formats = ['.png', '.jpg', '.jpeg', '.pdf']
            if file_path_obj.suffix.lower() not in supported_formats:
                QMessageBox.warning(
                    self,
                    "不支持的格式",
                    f"不支持的文件格式：{file_path_obj.suffix}\n\n支持的格式：{', '.join(supported_formats)}"
                )
                return
            
            # 保存文件路径
            self.current_file_path = file_path
            
            # 更新状态
            self.status_label.setText(f"已导入：{file_path_obj.name}")
            
            # 启用 OCR 按钮
            self.ocr_action.setEnabled(True)
            
            # 清空之前的数据
            self.ocr_text = ""
            self.test_points = None
            self.test_cases = []
            self.ocr_widget.set_text("")
            self.test_point_widget.clear()
            self.test_case_widget.clear()
            
            # 禁用后续按钮
            self.ai_action.setEnabled(False)
            self.generate_action.setEnabled(False)
            self.export_action.setEnabled(False)
            
            self.logger.log_operation(
                "import_document_success",
                file_path=file_path,
                file_size_mb=file_size_mb
            )
            
            # 自动开始 OCR 识别
            self.logger.info("导入成功，自动开始 OCR 识别")
            self.start_ocr()
        except Exception as e:
            self.logger.log_error(e, {"operation": "import_document"})
            QMessageBox.critical(
                self,
                "导入失败",
                f"导入文档失败：{str(e)}"
            )
    
    def start_ocr(self):
        """启动 OCR 识别"""
        try:
            if not self.current_file_path:
                QMessageBox.warning(
                    self,
                    "未导入文件",
                    "请先导入需求文档"
                )
                return
            
            self.logger.log_operation("start_ocr", file_path=self.current_file_path)
            
            # 创建 OCR 工作线程
            from ui.workers import OCRWorker
            
            self.ocr_worker = OCRWorker(self.ocr_engine, self.current_file_path)
            
            # 连接信号
            self.ocr_worker.progress.connect(self._on_ocr_progress)
            self.ocr_worker.status.connect(self._on_ocr_status)
            self.ocr_worker.finished.connect(self._on_ocr_finished)
            self.ocr_worker.error.connect(self._on_ocr_error)
            
            # 更新界面状态
            self.status_label.setText("正在进行 OCR 识别...")
            self.progress_bar.setValue(0)
            self.progress_bar.setVisible(True)
            
            # 禁用按钮
            self.ocr_action.setEnabled(False)
            
            # 启动线程
            self.ocr_worker.start()
        except Exception as e:
            self.logger.log_error(e, {"operation": "start_ocr"})
            QMessageBox.critical(
                self,
                "启动失败",
                f"启动 OCR 识别失败：{str(e)}"
            )
    
    def _on_ocr_progress(self, value: int):
        """OCR 进度更新"""
        self.progress_bar.setValue(value)
    
    def _on_ocr_status(self, status: str):
        """OCR 状态更新"""
        self.status_label.setText(status)
    
    def _on_ocr_finished(self, text: str):
        """OCR 完成"""
        self.ocr_text = text
        self.ocr_widget.set_text(text)
        
        # 更新状态
        self.status_label.setText("OCR 识别完成")
        self.progress_bar.setVisible(False)
        
        # 启用按钮
        self.ocr_action.setEnabled(True)
        self.ai_action.setEnabled(True)
        
        self.logger.log_operation(
            "ocr_complete",
            text_length=len(text)
        )
        
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("✓ OCR 识别完成")
        msg.setText("<h3>OCR 识别完成</h3>")
        msg.setInformativeText(
            f"<p>✓ 成功识别 <b>{len(text)}</b> 个字符</p>"
            f"<p>📝 文本已显示在左侧区域，您可以编辑修改</p>"
            f"<p>👉 下一步：点击 <b>'AI 分析'</b> 按钮提取测试要点</p>"
        )
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()
    
    def _on_ocr_error(self, error_msg: str):
        """OCR 错误"""
        self.status_label.setText("OCR 识别失败")
        self.progress_bar.setVisible(False)
        
        # 启用按钮
        self.ocr_action.setEnabled(True)
        
        self.logger.error(f"OCR 识别失败: {error_msg}")
        
        QMessageBox.critical(
            self,
            "OCR 失败",
            f"OCR 识别失败：{error_msg}\n\n请检查图片质量或重试。"
        )
    
    def start_ai_analysis(self):
        """启动 AI 分析"""
        try:
            # 获取 OCR 文本（可能被用户编辑过）
            text = self.ocr_widget.get_text().strip()
            
            if not text:
                QMessageBox.warning(
                    self,
                    "文本为空",
                    "请先进行 OCR 识别或手动输入需求文本"
                )
                return
            
            self.logger.log_operation("start_ai_analysis", text_length=len(text))
            
            # 创建 AI 分析工作线程
            from ui.workers import AIAnalysisWorker
            
            self.ai_worker = AIAnalysisWorker(self.ai_analyzer, text)
            
            # 连接信号
            self.ai_worker.progress.connect(self._on_ai_progress)
            self.ai_worker.status.connect(self._on_ai_status)
            self.ai_worker.finished.connect(self._on_ai_finished)
            self.ai_worker.error.connect(self._on_ai_error)
            
            # 更新界面状态
            self.status_label.setText("正在进行 AI 分析...")
            self.progress_bar.setValue(0)
            self.progress_bar.setVisible(True)
            
            # 禁用按钮
            self.ai_action.setEnabled(False)
            
            # 启动线程
            self.ai_worker.start()
        except Exception as e:
            self.logger.log_error(e, {"operation": "start_ai_analysis"})
            QMessageBox.critical(
                self,
                "启动失败",
                f"启动 AI 分析失败：{str(e)}"
            )
    
    def _on_ai_progress(self, value: int):
        """AI 分析进度更新"""
        self.progress_bar.setValue(value)
    
    def _on_ai_status(self, status: str):
        """AI 分析状态更新"""
        self.status_label.setText(status)
    
    def _on_ai_finished(self, test_points: Dict):
        """AI 分析完成"""
        self.test_points = test_points
        
        # 显示测试要点
        self.test_point_widget.set_test_points(test_points)
        
        # 更新状态
        self.status_label.setText("AI 分析完成")
        self.progress_bar.setVisible(False)
        
        # 启用按钮
        self.ai_action.setEnabled(True)
        self.generate_action.setEnabled(True)
        
        test_point_count = len(test_points.get("test_points", []))
        self.logger.log_operation(
            "ai_analysis_complete",
            test_point_count=test_point_count
        )
        
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("✓ AI 分析完成")
        msg.setText("<h3>AI 分析完成</h3>")
        msg.setInformativeText(
            f"<p>✓ 成功提取 <b>{test_point_count}</b> 个测试要点</p>"
            f"<p>🎯 测试要点已显示在右上方区域</p>"
            f"<p>👉 下一步：点击 <b>'生成用例'</b> 按钮生成详细测试用例</p>"
        )
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()
    
    def _on_ai_error(self, error_msg: str):
        """AI 分析错误"""
        self.status_label.setText("AI 分析失败")
        self.progress_bar.setVisible(False)
        
        # 启用按钮
        self.ai_action.setEnabled(True)
        
        self.logger.error(f"AI 分析失败: {error_msg}")
        
        QMessageBox.critical(
            self,
            "AI 分析失败",
            f"AI 分析失败：{error_msg}\n\n请检查网络连接和 API 配置。"
        )
    
    def generate_test_cases(self):
        """生成测试用例"""
        try:
            if not self.test_points:
                QMessageBox.warning(
                    self,
                    "未进行 AI 分析",
                    "请先进行 AI 分析提取测试要点"
                )
                return
            
            self.logger.log_operation("generate_test_cases_start")
            
            # 创建测试用例生成工作线程
            from ui.workers import TestCaseGenerationWorker
            
            self.case_worker = TestCaseGenerationWorker(
                self.test_case_generator,
                self.test_points
            )
            
            # 连接信号
            self.case_worker.progress.connect(self._on_case_progress)
            self.case_worker.status.connect(self._on_case_status)
            self.case_worker.finished.connect(self._on_case_finished)
            self.case_worker.error.connect(self._on_case_error)
            
            # 更新界面状态
            self.status_label.setText("正在生成测试用例...")
            self.progress_bar.setValue(0)
            self.progress_bar.setVisible(True)
            
            # 禁用按钮
            self.generate_action.setEnabled(False)
            
            # 启动线程
            self.case_worker.start()
        except Exception as e:
            self.logger.log_error(e, {"operation": "generate_test_cases"})
            QMessageBox.critical(
                self,
                "启动失败",
                f"启动测试用例生成失败：{str(e)}"
            )
    
    def _on_case_progress(self, value: int):
        """测试用例生成进度更新"""
        self.progress_bar.setValue(value)
    
    def _on_case_status(self, status: str):
        """测试用例生成状态更新"""
        self.status_label.setText(status)
    
    def _on_case_finished(self, test_cases: List[Dict]):
        """测试用例生成完成"""
        self.test_cases = test_cases
        
        # 显示测试用例
        self.test_case_widget.set_test_cases(test_cases)
        
        # 更新状态
        self.status_label.setText("测试用例生成完成")
        self.progress_bar.setVisible(False)
        
        # 启用按钮
        self.generate_action.setEnabled(True)
        self.export_action.setEnabled(True)
        
        self.logger.log_operation(
            "generate_test_cases_complete",
            case_count=len(test_cases)
        )
        
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("✓ 测试用例生成完成")
        msg.setText("<h3>测试用例生成完成</h3>")
        msg.setInformativeText(
            f"<p>✓ 成功生成 <b>{len(test_cases)}</b> 个测试用例</p>"
            f"<p>📋 测试用例已显示在右下方表格中</p>"
            f"<p>💡 提示：双击表格行可查看用例详情</p>"
            f"<p>👉 下一步：点击 <b>'导出'</b> 按钮保存测试用例</p>"
        )
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()
    
    def _on_case_error(self, error_msg: str):
        """测试用例生成错误"""
        self.status_label.setText("测试用例生成失败")
        self.progress_bar.setVisible(False)
        
        # 启用按钮
        self.generate_action.setEnabled(True)
        
        self.logger.error(f"测试用例生成失败: {error_msg}")
        
        QMessageBox.critical(
            self,
            "生成失败",
            f"测试用例生成失败：{error_msg}"
        )
    
    def export_cases(self):
        """导出测试用例"""
        try:
            if not self.test_cases:
                QMessageBox.warning(
                    self,
                    "无测试用例",
                    "请先生成测试用例"
                )
                return
            
            # 选择导出格式
            from PyQt6.QtWidgets import QDialog, QVBoxLayout, QRadioButton, QDialogButtonBox
            
            dialog = QDialog(self)
            dialog.setWindowTitle("选择导出格式")
            layout = QVBoxLayout(dialog)
            
            json_radio = QRadioButton("JSON 格式")
            json_radio.setChecked(True)
            layout.addWidget(json_radio)
            
            xmind_radio = QRadioButton("XMind 格式")
            layout.addWidget(xmind_radio)
            
            buttons = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
            )
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)
            
            if dialog.exec() != QDialog.DialogCode.Accepted:
                return
            
            # 确定导出格式
            if json_radio.isChecked():
                export_format = "json"
                file_filter = "JSON 文件 (*.json)"
                default_ext = ".json"
            else:
                export_format = "xmind"
                file_filter = "XMind 文件 (*.xmind)"
                default_ext = ".xmind"
            
            # 选择保存路径
            default_name = f"测试用例_{Path(self.current_file_path).stem if self.current_file_path else '导出'}{default_ext}"
            
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "保存测试用例",
                default_name,
                file_filter
            )
            
            if not file_path:
                return
            
            # 确保文件扩展名正确
            if not file_path.endswith(default_ext):
                file_path += default_ext
            
            self.logger.log_operation(
                "export_cases_start",
                format=export_format,
                file_path=file_path
            )
            
            # 转换为 TestCase 对象
            from utils.models import TestCase
            test_case_objects = [TestCase(**case) for case in self.test_cases]
            
            # 执行导出
            if export_format == "json":
                success = self.export_manager.export_to_json(
                    test_case_objects,
                    file_path
                )
            else:
                success = self.export_manager.export_to_xmind(
                    test_case_objects,
                    file_path
                )
            
            if success:
                self.logger.log_operation(
                    "export_cases_success",
                    format=export_format,
                    file_path=file_path
                )
                
                # 询问是否打开文件
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Icon.Information)
                msg.setWindowTitle("✓ 导出成功")
                msg.setText("<h3>测试用例导出成功</h3>")
                msg.setInformativeText(
                    f"<p>✓ 文件已保存到：</p>"
                    f"<p style='color: #2196F3;'><b>{file_path}</b></p>"
                    f"<p>是否打开文件所在位置？</p>"
                )
                msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                yes_button = msg.button(QMessageBox.StandardButton.Yes)
                yes_button.setText("打开位置")
                no_button = msg.button(QMessageBox.StandardButton.No)
                no_button.setText("稍后查看")
                reply = msg.exec()
                
                if reply == QMessageBox.StandardButton.Yes:
                    import subprocess
                    import platform
                    
                    file_dir = str(Path(file_path).parent)
                    
                    if platform.system() == "Windows":
                        subprocess.run(["explorer", file_dir])
                    elif platform.system() == "Darwin":  # macOS
                        subprocess.run(["open", file_dir])
                    else:  # Linux
                        subprocess.run(["xdg-open", file_dir])
            
        except Exception as e:
            self.logger.log_error(e, {"operation": "export_cases"})
            QMessageBox.critical(
                self,
                "导出失败",
                f"导出失败：{str(e)}"
            )
    
    def open_settings(self):
        """打开设置对话框"""
        try:
            from ui.settings_dialog import SettingsDialog
            
            dialog = SettingsDialog(self.config, self)
            
            if dialog.exec() == QDialog.DialogCode.Accepted:
                # 配置已更新，重新初始化核心组件
                self.logger.info("配置已更新，重新初始化核心组件")
                
                # 重新加载配置
                self.config = AppConfig.load_from_file()
                
                # 重新初始化核心组件
                self._init_core_components()
                
                # 更新模型标签
                self.model_label.setText(f"模型: {self.config.ai_model.model_name}")
                
                # 重新应用样式表
                self.setStyleSheet(get_theme_stylesheet(self.config.ui.theme))
                
                QMessageBox.information(
                    self,
                    "设置已保存",
                    "设置已保存并应用。"
                )
        except Exception as e:
            self.logger.log_error(e, {"operation": "open_settings"})
            QMessageBox.critical(
                self,
                "设置失败",
                f"打开设置对话框失败：{str(e)}"
            )
