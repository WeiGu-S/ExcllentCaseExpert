"""
设置对话框

提供 AI 模型、OCR、性能和 UI 的配置界面。
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QPushButton, QTabWidget,
    QWidget, QSpinBox, QDoubleSpinBox, QMessageBox, QLabel, QGroupBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
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
        self.setWindowTitle("⚙️ 系统设置")
        self.setMinimumWidth(650)
        self.setMinimumHeight(550)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # 标签页
        tabs = QTabWidget()
        
        # AI 模型设置
        ai_tab = self.create_ai_tab()
        tabs.addTab(ai_tab, "🤖 AI 模型")
        
        # OCR 设置
        ocr_tab = self.create_ocr_tab()
        tabs.addTab(ocr_tab, "🔍 OCR 设置")
        
        # 性能设置
        perf_tab = self.create_performance_tab()
        tabs.addTab(perf_tab, "⚡ 性能设置")
        
        # UI 设置
        ui_tab = self.create_ui_tab()
        tabs.addTab(ui_tab, "🎨 界面设置")
        
        layout.addWidget(tabs)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.addStretch()
        
        cancel_button = QPushButton("取消")
        cancel_button.setMinimumWidth(100)
        cancel_button.setMinimumHeight(36)
        cancel_button.setProperty("class", "secondary")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        save_button = QPushButton("保存设置")
        save_button.setMinimumWidth(100)
        save_button.setMinimumHeight(36)
        save_button.clicked.connect(self.save_settings)
        button_layout.addWidget(save_button)
        
        layout.addLayout(button_layout)
    
    def create_ai_tab(self) -> QWidget:
        """创建 AI 设置标签页"""
        widget = QWidget()
        main_layout = QVBoxLayout(widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 连接配置组
        connection_group = QGroupBox("🔗 连接配置")
        connection_layout = QFormLayout()
        connection_layout.setSpacing(12)
        connection_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        connection_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        
        # 提供商选择
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["openai", "qwen", "deepseek", "custom"])
        self.provider_combo.setCurrentText(self.config.ai_model.provider)
        self.provider_combo.setMinimumHeight(32)
        self.provider_combo.setToolTip("选择 AI 模型提供商")
        connection_layout.addRow("提供商:", self.provider_combo)
        
        # API Key
        api_key_container = QVBoxLayout()
        api_key_container.setSpacing(4)
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setText(self.config.ai_model.api_key)
        self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_edit.setPlaceholderText("请输入 API Key")
        self.api_key_edit.setMinimumHeight(32)
        self.api_key_edit.setToolTip("输入您的 API 密钥")
        api_key_hint = QLabel("💡 用于身份验证的密钥，请妥善保管")
        api_key_hint.setStyleSheet("color: #666; font-size: 11px;")
        api_key_container.addWidget(self.api_key_edit)
        api_key_container.addWidget(api_key_hint)
        connection_layout.addRow("API Key:", api_key_container)
        
        # Base URL
        base_url_container = QVBoxLayout()
        base_url_container.setSpacing(4)
        self.base_url_edit = QLineEdit()
        self.base_url_edit.setText(self.config.ai_model.base_url)
        self.base_url_edit.setPlaceholderText("https://api.openai.com/v1")
        self.base_url_edit.setMinimumHeight(32)
        self.base_url_edit.setToolTip("API 服务的基础 URL")
        base_url_hint = QLabel("💡 API 服务地址，使用代理时需修改")
        base_url_hint.setStyleSheet("color: #666; font-size: 11px;")
        base_url_container.addWidget(self.base_url_edit)
        base_url_container.addWidget(base_url_hint)
        connection_layout.addRow("Base URL:", base_url_container)
        
        connection_group.setLayout(connection_layout)
        main_layout.addWidget(connection_group)
        
        # 模型参数组
        model_group = QGroupBox("⚙️ 模型参数")
        model_layout = QFormLayout()
        model_layout.setSpacing(12)
        model_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        model_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        
        # 模型名称
        model_name_container = QVBoxLayout()
        model_name_container.setSpacing(4)
        self.model_name_edit = QLineEdit()
        self.model_name_edit.setText(self.config.ai_model.model_name)
        self.model_name_edit.setPlaceholderText("gpt-4o-mini")
        self.model_name_edit.setMinimumHeight(32)
        self.model_name_edit.setToolTip("使用的模型名称")
        model_name_hint = QLabel("💡 例如: gpt-4o-mini, qwen-plus, deepseek-chat")
        model_name_hint.setStyleSheet("color: #666; font-size: 11px;")
        model_name_container.addWidget(self.model_name_edit)
        model_name_container.addWidget(model_name_hint)
        model_layout.addRow("模型名称:", model_name_container)
        
        # 最大 Token 数
        token_container = QVBoxLayout()
        token_container.setSpacing(4)
        self.max_tokens_spin = QSpinBox()
        self.max_tokens_spin.setRange(100, 10000)
        self.max_tokens_spin.setValue(self.config.ai_model.max_tokens)
        self.max_tokens_spin.setSuffix(" tokens")
        self.max_tokens_spin.setMinimumHeight(32)
        self.max_tokens_spin.setToolTip("单次请求的最大 token 数量")
        token_hint = QLabel("💡 控制生成内容的长度，建议 2000-4000")
        token_hint.setStyleSheet("color: #666; font-size: 11px;")
        token_container.addWidget(self.max_tokens_spin)
        token_container.addWidget(token_hint)
        model_layout.addRow("最大 Token 数:", token_container)
        
        # 温度参数
        temp_container = QVBoxLayout()
        temp_container.setSpacing(4)
        self.temperature_spin = QDoubleSpinBox()
        self.temperature_spin.setRange(0.0, 2.0)
        self.temperature_spin.setSingleStep(0.1)
        self.temperature_spin.setValue(self.config.ai_model.temperature)
        self.temperature_spin.setMinimumHeight(32)
        self.temperature_spin.setToolTip("控制输出的随机性")
        temp_hint = QLabel("💡 0.0-2.0，值越高越随机，建议 0.7")
        temp_hint.setStyleSheet("color: #666; font-size: 11px;")
        temp_container.addWidget(self.temperature_spin)
        temp_container.addWidget(temp_hint)
        model_layout.addRow("温度参数:", temp_container)
        
        model_group.setLayout(model_layout)
        main_layout.addWidget(model_group)
        
        main_layout.addStretch()
        return widget
    
    def create_ocr_tab(self) -> QWidget:
        """创建 OCR 设置标签页"""
        widget = QWidget()
        main_layout = QVBoxLayout(widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # OCR 引擎组
        engine_group = QGroupBox("🔍 OCR 引擎")
        engine_layout = QFormLayout()
        engine_layout.setSpacing(12)
        engine_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        engine_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        
        # 使用 PaddleOCR
        paddle_container = QVBoxLayout()
        paddle_container.setSpacing(4)
        self.use_paddle_combo = QComboBox()
        self.use_paddle_combo.addItems(["是", "否"])
        self.use_paddle_combo.setCurrentText(
            "是" if self.config.ocr.use_paddle_ocr else "否"
        )
        self.use_paddle_combo.setMinimumHeight(32)
        self.use_paddle_combo.setToolTip("是否启用 PaddleOCR 引擎")
        paddle_hint = QLabel("💡 推荐使用，支持中文识别效果好")
        paddle_hint.setStyleSheet("color: #666; font-size: 11px;")
        paddle_container.addWidget(self.use_paddle_combo)
        paddle_container.addWidget(paddle_hint)
        engine_layout.addRow("使用 PaddleOCR:", paddle_container)
        
        # 使用 Tesseract
        tesseract_container = QVBoxLayout()
        tesseract_container.setSpacing(4)
        self.use_tesseract_combo = QComboBox()
        self.use_tesseract_combo.addItems(["是", "否"])
        self.use_tesseract_combo.setCurrentText(
            "是" if self.config.ocr.use_tesseract else "否"
        )
        self.use_tesseract_combo.setMinimumHeight(32)
        self.use_tesseract_combo.setToolTip("是否启用 Tesseract 引擎")
        tesseract_hint = QLabel("💡 备用引擎，需要单独安装")
        tesseract_hint.setStyleSheet("color: #666; font-size: 11px;")
        tesseract_container.addWidget(self.use_tesseract_combo)
        tesseract_container.addWidget(tesseract_hint)
        engine_layout.addRow("使用 Tesseract:", tesseract_container)
        
        engine_group.setLayout(engine_layout)
        main_layout.addWidget(engine_group)
        
        # 文件限制组
        limit_group = QGroupBox("📁 文件限制")
        limit_layout = QFormLayout()
        limit_layout.setSpacing(12)
        limit_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        limit_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        
        # 最大文件大小
        filesize_container = QVBoxLayout()
        filesize_container.setSpacing(4)
        self.max_file_size_spin = QSpinBox()
        self.max_file_size_spin.setRange(1, 500)
        self.max_file_size_spin.setValue(self.config.ocr.max_file_size_mb)
        self.max_file_size_spin.setSuffix(" MB")
        self.max_file_size_spin.setMinimumHeight(32)
        self.max_file_size_spin.setToolTip("允许导入的最大文件大小")
        filesize_hint = QLabel("💡 限制导入文件的大小，避免内存溢出")
        filesize_hint.setStyleSheet("color: #666; font-size: 11px;")
        filesize_container.addWidget(self.max_file_size_spin)
        filesize_container.addWidget(filesize_hint)
        limit_layout.addRow("最大文件大小:", filesize_container)
        
        limit_group.setLayout(limit_layout)
        main_layout.addWidget(limit_group)
        
        main_layout.addStretch()
        return widget
    
    def create_performance_tab(self) -> QWidget:
        """创建性能设置标签页"""
        widget = QWidget()
        main_layout = QVBoxLayout(widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 性能配置组
        perf_group = QGroupBox("⚡ 性能配置")
        perf_layout = QFormLayout()
        perf_layout.setSpacing(12)
        perf_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        perf_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        
        # 最大并发任务数
        tasks_container = QVBoxLayout()
        tasks_container.setSpacing(4)
        self.max_tasks_spin = QSpinBox()
        self.max_tasks_spin.setRange(1, 10)
        self.max_tasks_spin.setValue(self.config.performance.max_concurrent_tasks)
        self.max_tasks_spin.setMinimumHeight(32)
        self.max_tasks_spin.setToolTip("同时运行的最大任务数")
        tasks_hint = QLabel("💡 建议 1-3，过高可能导致系统卡顿")
        tasks_hint.setStyleSheet("color: #666; font-size: 11px;")
        tasks_container.addWidget(self.max_tasks_spin)
        tasks_container.addWidget(tasks_hint)
        perf_layout.addRow("最大并发任务数:", tasks_container)
        
        # 内存清理间隔
        cleanup_container = QVBoxLayout()
        cleanup_container.setSpacing(4)
        self.cleanup_interval_spin = QSpinBox()
        self.cleanup_interval_spin.setRange(10, 300)
        self.cleanup_interval_spin.setValue(self.config.performance.memory_cleanup_interval)
        self.cleanup_interval_spin.setSuffix(" 秒")
        self.cleanup_interval_spin.setMinimumHeight(32)
        self.cleanup_interval_spin.setToolTip("自动清理内存的时间间隔")
        cleanup_hint = QLabel("💡 定期清理释放内存，建议 60-120 秒")
        cleanup_hint.setStyleSheet("color: #666; font-size: 11px;")
        cleanup_container.addWidget(self.cleanup_interval_spin)
        cleanup_container.addWidget(cleanup_hint)
        perf_layout.addRow("内存清理间隔:", cleanup_container)
        
        # 最大内存使用
        memory_container = QVBoxLayout()
        memory_container.setSpacing(4)
        self.max_memory_spin = QSpinBox()
        self.max_memory_spin.setRange(256, 8192)
        self.max_memory_spin.setValue(self.config.performance.max_memory_mb)
        self.max_memory_spin.setSuffix(" MB")
        self.max_memory_spin.setMinimumHeight(32)
        self.max_memory_spin.setToolTip("程序允许使用的最大内存")
        memory_hint = QLabel("💡 超过限制时会自动清理，建议 1024-2048 MB")
        memory_hint.setStyleSheet("color: #666; font-size: 11px;")
        memory_container.addWidget(self.max_memory_spin)
        memory_container.addWidget(memory_hint)
        perf_layout.addRow("最大内存使用:", memory_container)
        
        perf_group.setLayout(perf_layout)
        main_layout.addWidget(perf_group)
        
        main_layout.addStretch()
        return widget
    
    def create_ui_tab(self) -> QWidget:
        """创建 UI 设置标签页"""
        widget = QWidget()
        main_layout = QVBoxLayout(widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 外观设置组
        appearance_group = QGroupBox("🎨 外观设置")
        appearance_layout = QFormLayout()
        appearance_layout.setSpacing(12)
        appearance_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        appearance_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        
        # 主题
        theme_container = QVBoxLayout()
        theme_container.setSpacing(4)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["light", "dark", "auto"])
        self.theme_combo.setCurrentText(self.config.ui.theme)
        self.theme_combo.setMinimumHeight(32)
        self.theme_combo.setToolTip("选择界面主题")
        theme_hint = QLabel("💡 light=浅色, dark=深色, auto=跟随系统")
        theme_hint.setStyleSheet("color: #666; font-size: 11px;")
        theme_container.addWidget(self.theme_combo)
        theme_container.addWidget(theme_hint)
        appearance_layout.addRow("主题:", theme_container)
        
        # 语言
        language_container = QVBoxLayout()
        language_container.setSpacing(4)
        self.language_combo = QComboBox()
        self.language_combo.addItems(["zh_CN", "en_US"])
        self.language_combo.setCurrentText(self.config.ui.language)
        self.language_combo.setMinimumHeight(32)
        self.language_combo.setToolTip("选择界面语言")
        language_hint = QLabel("💡 zh_CN=简体中文, en_US=英语")
        language_hint.setStyleSheet("color: #666; font-size: 11px;")
        language_container.addWidget(self.language_combo)
        language_container.addWidget(language_hint)
        appearance_layout.addRow("语言:", language_container)
        
        appearance_group.setLayout(appearance_layout)
        main_layout.addWidget(appearance_group)
        
        # 窗口设置组
        window_group = QGroupBox("🪟 窗口设置")
        window_layout = QFormLayout()
        window_layout.setSpacing(12)
        window_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        window_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        
        # 窗口宽度
        width_container = QVBoxLayout()
        width_container.setSpacing(4)
        self.window_width_spin = QSpinBox()
        self.window_width_spin.setRange(800, 3840)
        self.window_width_spin.setValue(self.config.ui.window_width)
        self.window_width_spin.setSuffix(" px")
        self.window_width_spin.setMinimumHeight(32)
        self.window_width_spin.setToolTip("设置窗口的默认宽度")
        width_hint = QLabel("💡 建议 1200-1600，根据屏幕大小调整")
        width_hint.setStyleSheet("color: #666; font-size: 11px;")
        width_container.addWidget(self.window_width_spin)
        width_container.addWidget(width_hint)
        window_layout.addRow("窗口宽度:", width_container)
        
        # 窗口高度
        height_container = QVBoxLayout()
        height_container.setSpacing(4)
        self.window_height_spin = QSpinBox()
        self.window_height_spin.setRange(600, 2160)
        self.window_height_spin.setValue(self.config.ui.window_height)
        self.window_height_spin.setSuffix(" px")
        self.window_height_spin.setMinimumHeight(32)
        self.window_height_spin.setToolTip("设置窗口的默认高度")
        height_hint = QLabel("💡 建议 800-1000，根据屏幕大小调整")
        height_hint.setStyleSheet("color: #666; font-size: 11px;")
        height_container.addWidget(self.window_height_spin)
        height_container.addWidget(height_hint)
        window_layout.addRow("窗口高度:", height_container)
        
        window_group.setLayout(window_layout)
        main_layout.addWidget(window_group)
        
        main_layout.addStretch()
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
