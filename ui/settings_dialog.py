"""
设置对话框

提供 AI 模型、OCR、性能和 UI 的配置界面。
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QPushButton, QTabWidget,
    QWidget, QSpinBox, QDoubleSpinBox, QMessageBox
)
from PyQt6.QtCore import Qt
from utils.config_manager import AppConfig


class SettingsDialog(QDialog):
    """设置对话框"""
    
    def __init__(self, config: AppConfig, parent=None):
        """初始化设置对话框
        
        Args:
            config: 应用配置实例
            parent: 父窗口
        """
        super().__init__(parent)
        self.config = config
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("设置")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        
        layout = QVBoxLayout(self)
        
        # 标签页
        tabs = QTabWidget()
        
        # AI 模型设置
        ai_tab = self.create_ai_tab()
        tabs.addTab(ai_tab, "AI 模型")
        
        # OCR 设置
        ocr_tab = self.create_ocr_tab()
        tabs.addTab(ocr_tab, "OCR 设置")
        
        # 性能设置
        perf_tab = self.create_performance_tab()
        tabs.addTab(perf_tab, "性能设置")
        
        # UI 设置
        ui_tab = self.create_ui_tab()
        tabs.addTab(ui_tab, "界面设置")
        
        layout.addWidget(tabs)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        save_button = QPushButton("保存")
        save_button.clicked.connect(self.save_settings)
        button_layout.addWidget(save_button)
        
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
    
    def create_ai_tab(self) -> QWidget:
        """创建 AI 设置标签页"""
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setSpacing(15)
        
        # 提供商选择
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["openai", "qwen", "deepseek", "custom"])
        self.provider_combo.setCurrentText(self.config.ai_model.provider)
        layout.addRow("提供商:", self.provider_combo)
        
        # API Key
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setText(self.config.ai_model.api_key)
        self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_edit.setPlaceholderText("请输入 API Key")
        layout.addRow("API Key:", self.api_key_edit)
        
        # Base URL
        self.base_url_edit = QLineEdit()
        self.base_url_edit.setText(self.config.ai_model.base_url)
        self.base_url_edit.setPlaceholderText("https://api.openai.com/v1")
        layout.addRow("Base URL:", self.base_url_edit)
        
        # 模型名称
        self.model_name_edit = QLineEdit()
        self.model_name_edit.setText(self.config.ai_model.model_name)
        self.model_name_edit.setPlaceholderText("gpt-4o-mini")
        layout.addRow("模型名称:", self.model_name_edit)
        
        # 最大 Token 数
        self.max_tokens_spin = QSpinBox()
        self.max_tokens_spin.setRange(100, 10000)
        self.max_tokens_spin.setValue(self.config.ai_model.max_tokens)
        self.max_tokens_spin.setSuffix(" tokens")
        layout.addRow("最大 Token 数:", self.max_tokens_spin)
        
        # 温度参数
        self.temperature_spin = QDoubleSpinBox()
        self.temperature_spin.setRange(0.0, 2.0)
        self.temperature_spin.setSingleStep(0.1)
        self.temperature_spin.setValue(self.config.ai_model.temperature)
        layout.addRow("温度参数:", self.temperature_spin)
        
        return widget
    
    def create_ocr_tab(self) -> QWidget:
        """创建 OCR 设置标签页"""
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setSpacing(15)
        
        # 使用 PaddleOCR
        self.use_paddle_combo = QComboBox()
        self.use_paddle_combo.addItems(["是", "否"])
        self.use_paddle_combo.setCurrentText(
            "是" if self.config.ocr.use_paddle_ocr else "否"
        )
        layout.addRow("使用 PaddleOCR:", self.use_paddle_combo)
        
        # 使用 Tesseract
        self.use_tesseract_combo = QComboBox()
        self.use_tesseract_combo.addItems(["是", "否"])
        self.use_tesseract_combo.setCurrentText(
            "是" if self.config.ocr.use_tesseract else "否"
        )
        layout.addRow("使用 Tesseract:", self.use_tesseract_combo)
        
        # 最大文件大小
        self.max_file_size_spin = QSpinBox()
        self.max_file_size_spin.setRange(1, 500)
        self.max_file_size_spin.setValue(self.config.ocr.max_file_size_mb)
        self.max_file_size_spin.setSuffix(" MB")
        layout.addRow("最大文件大小:", self.max_file_size_spin)
        
        return widget
    
    def create_performance_tab(self) -> QWidget:
        """创建性能设置标签页"""
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setSpacing(15)
        
        # 最大并发任务数
        self.max_tasks_spin = QSpinBox()
        self.max_tasks_spin.setRange(1, 10)
        self.max_tasks_spin.setValue(self.config.performance.max_concurrent_tasks)
        layout.addRow("最大并发任务数:", self.max_tasks_spin)
        
        # 内存清理间隔
        self.cleanup_interval_spin = QSpinBox()
        self.cleanup_interval_spin.setRange(10, 300)
        self.cleanup_interval_spin.setValue(self.config.performance.memory_cleanup_interval)
        self.cleanup_interval_spin.setSuffix(" 秒")
        layout.addRow("内存清理间隔:", self.cleanup_interval_spin)
        
        # 最大内存使用
        self.max_memory_spin = QSpinBox()
        self.max_memory_spin.setRange(256, 8192)
        self.max_memory_spin.setValue(self.config.performance.max_memory_mb)
        self.max_memory_spin.setSuffix(" MB")
        layout.addRow("最大内存使用:", self.max_memory_spin)
        
        return widget
    
    def create_ui_tab(self) -> QWidget:
        """创建 UI 设置标签页"""
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setSpacing(15)
        
        # 主题
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["light", "dark", "auto"])
        self.theme_combo.setCurrentText(self.config.ui.theme)
        layout.addRow("主题:", self.theme_combo)
        
        # 语言
        self.language_combo = QComboBox()
        self.language_combo.addItems(["zh_CN", "en_US"])
        self.language_combo.setCurrentText(self.config.ui.language)
        layout.addRow("语言:", self.language_combo)
        
        # 窗口宽度
        self.window_width_spin = QSpinBox()
        self.window_width_spin.setRange(800, 3840)
        self.window_width_spin.setValue(self.config.ui.window_width)
        self.window_width_spin.setSuffix(" px")
        layout.addRow("窗口宽度:", self.window_width_spin)
        
        # 窗口高度
        self.window_height_spin = QSpinBox()
        self.window_height_spin.setRange(600, 2160)
        self.window_height_spin.setValue(self.config.ui.window_height)
        self.window_height_spin.setSuffix(" px")
        layout.addRow("窗口高度:", self.window_height_spin)
        
        return widget
    
    def save_settings(self):
        """保存设置"""
        try:
            # 验证 API Key
            api_key = self.api_key_edit.text().strip()
            if not api_key or api_key == "your_api_key_here":
                reply = QMessageBox.question(
                    self,
                    "API Key 未配置",
                    "API Key 未配置或使用默认值，这将导致 AI 分析功能无法使用。\n\n是否继续保存？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.No:
                    return
            
            # 验证至少启用一个 OCR 引擎
            use_paddle = self.use_paddle_combo.currentText() == "是"
            use_tesseract = self.use_tesseract_combo.currentText() == "是"
            
            if not use_paddle and not use_tesseract:
                QMessageBox.warning(
                    self,
                    "配置错误",
                    "至少需要启用一个 OCR 引擎（PaddleOCR 或 Tesseract）"
                )
                return
            
            # 更新配置
            self.config.ai_model.provider = self.provider_combo.currentText()
            self.config.ai_model.api_key = api_key
            self.config.ai_model.base_url = self.base_url_edit.text().strip()
            self.config.ai_model.model_name = self.model_name_edit.text().strip()
            self.config.ai_model.max_tokens = self.max_tokens_spin.value()
            self.config.ai_model.temperature = self.temperature_spin.value()
            
            self.config.ocr.use_paddle_ocr = use_paddle
            self.config.ocr.use_tesseract = use_tesseract
            self.config.ocr.max_file_size_mb = self.max_file_size_spin.value()
            
            self.config.performance.max_concurrent_tasks = self.max_tasks_spin.value()
            self.config.performance.memory_cleanup_interval = self.cleanup_interval_spin.value()
            self.config.performance.max_memory_mb = self.max_memory_spin.value()
            
            self.config.ui.theme = self.theme_combo.currentText()
            self.config.ui.language = self.language_combo.currentText()
            self.config.ui.window_width = self.window_width_spin.value()
            self.config.ui.window_height = self.window_height_spin.value()
            
            # 保存到文件
            self.config.save_to_file()
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "保存失败",
                f"保存配置失败：{str(e)}"
            )
