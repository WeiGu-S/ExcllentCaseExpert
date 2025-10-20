"""
OCR 结果展示组件

提供 OCR 识别结果的展示、复制和清空功能。
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QLabel, QPushButton, QApplication, QMessageBox
)
from PyQt6.QtCore import pyqtSignal

from utils.log_manager import get_logger


class OCRResultWidget(QWidget):
    """OCR 结果展示组件"""
    
    # 信号定义
    text_copied = pyqtSignal()  # 文本已复制
    text_cleared = pyqtSignal()  # 文本已清空
    
    def __init__(self, parent=None):
        """初始化 OCR 结果组件
        
        Args:
            parent: 父组件
        """
        super().__init__(parent)
        self.logger = get_logger()
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # 标题
        title = QLabel("📄 OCR 识别结果")
        title.setProperty("class", "subtitle")
        layout.addWidget(title)
        
        # 文本编辑器
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("OCR 识别的文本将显示在这里...\n\n您也可以手动输入或编辑文本。")
        self.text_edit.setReadOnly(False)
        layout.addWidget(self.text_edit)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        
        self.copy_button = QPushButton("📋 复制")
        self.copy_button.setToolTip("复制文本到剪贴板")
        self.copy_button.setMinimumHeight(36)
        self.copy_button.clicked.connect(self.copy_text)
        button_layout.addWidget(self.copy_button)
        
        self.clear_button = QPushButton("🗑️ 清空")
        self.clear_button.setToolTip("清空文本内容")
        self.clear_button.setMinimumHeight(36)
        self.clear_button.setProperty("class", "danger")
        self.clear_button.clicked.connect(self.clear_text)
        button_layout.addWidget(self.clear_button)
        
        layout.addLayout(button_layout)
        
        self.logger.debug("OCRResultWidget 初始化完成")
    
    def set_text(self, text: str):
        """设置文本内容
        
        Args:
            text: 要显示的文本
        """
        self.text_edit.setPlainText(text)
        self.logger.debug(f"设置 OCR 文本，长度: {len(text)}")
    
    def get_text(self) -> str:
        """获取文本内容
        
        Returns:
            当前文本内容
        """
        return self.text_edit.toPlainText()
    
    def copy_text(self):
        """复制文本到剪贴板"""
        text = self.text_edit.toPlainText()
        
        if not text:
            QMessageBox.information(
                self,
                "无内容",
                "没有可复制的内容"
            )
            return
        
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        
        self.logger.info(f"OCR 文本已复制到剪贴板，长度: {len(text)}")
        self.text_copied.emit()
        
        # 显示状态栏消息（如果有父窗口）
        parent_window = self.window()
        if hasattr(parent_window, 'statusBar'):
            parent_window.statusBar().showMessage(f"✓ 已复制 {len(text)} 个字符到剪贴板", 3000)
    
    def clear_text(self):
        """清空文本内容"""
        if not self.text_edit.toPlainText():
            return
        
        reply = QMessageBox.question(
            self,
            "确认清空",
            "确定要清空 OCR 识别结果吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.text_edit.clear()
            self.logger.info("OCR 文本已清空")
            self.text_cleared.emit()
    
    def is_empty(self) -> bool:
        """检查文本是否为空
        
        Returns:
            True 如果文本为空，否则 False
        """
        return not self.text_edit.toPlainText().strip()
