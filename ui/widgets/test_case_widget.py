"""
测试用例展示组件

提供测试用例表格展示，支持详细信息查看。
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QLabel,
    QTableWidgetItem, QHeaderView, QMessageBox, QTextEdit, QDialog,
    QVBoxLayout as QVBoxLayoutDialog, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from typing import List, Dict

from utils.models import TestCase, TestStep
from utils.log_manager import get_logger


class TestCaseWidget(QWidget):
    """测试用例展示组件"""
    
    # 信号定义
    case_selected = pyqtSignal(int)  # 测试用例被选中，参数为索引
    
    def __init__(self, parent=None):
        """初始化测试用例组件
        
        Args:
            parent: 父组件
        """
        super().__init__(parent)
        self.logger = get_logger()
        self.test_cases: List[TestCase] = []
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # 标题
        title = QLabel("📋 测试用例")
        title.setProperty("class", "subtitle")
        layout.addWidget(title)
        
        # 统计标签
        self.stats_label = QLabel("共 0 个测试用例")
        self.stats_label.setProperty("class", "info")
        layout.addWidget(self.stats_label)
        
        # 表格
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "ID", "标题", "类别", "优先级", "类型"
        ])
        
        # 设置列宽模式
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # 标题
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # 类别
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # 优先级
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # 类型
        
        # 设置表格属性
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        # 双击查看详情
        self.table.cellDoubleClicked.connect(self._on_cell_double_clicked)
        
        layout.addWidget(self.table)
        
        self.logger.debug("TestCaseWidget 初始化完成")
    
    def set_test_cases(self, test_cases_data: List):
        """设置测试用例
        
        Args:
            test_cases_data: 测试用例数据列表
        """
        self.table.setRowCount(0)
        self.test_cases = []
        
        for case_data in test_cases_data:
            try:
                # 转换为 TestCase 对象
                if isinstance(case_data, TestCase):
                    case = case_data
                else:
                    case = TestCase(**case_data)
                
                self.test_cases.append(case)
                
            except Exception as e:
                self.logger.error(f"添加测试用例失败: {e}, 数据: {case_data}")
        
        # 设置表格行数
        self.table.setRowCount(len(self.test_cases))
        
        # 填充表格
        for i, case in enumerate(self.test_cases):
            self._populate_row(i, case)
        
        # 更新统计信息
        self._update_stats()
        
        self.logger.info(f"已加载 {len(self.test_cases)} 个测试用例")
    
    def _populate_row(self, row: int, case: TestCase):
        """填充表格行
        
        Args:
            row: 行索引
            case: 测试用例对象
        """
        # ID
        id_item = QTableWidgetItem(case.test_case_id)
        id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row, 0, id_item)
        
        # 标题
        title_item = QTableWidgetItem(case.title)
        self.table.setItem(row, 1, title_item)
        
        # 类别
        category = case.category.value if hasattr(case.category, 'value') else str(case.category)
        category_item = QTableWidgetItem(category)
        category_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row, 2, category_item)
        
        # 优先级
        priority = case.priority.value if hasattr(case.priority, 'value') else str(case.priority)
        priority_item = QTableWidgetItem(priority)
        priority_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 根据优先级设置背景色
        priority_color = self._get_priority_color(priority)
        priority_item.setBackground(priority_color)
        
        self.table.setItem(row, 3, priority_item)
        
        # 类型
        type_item = QTableWidgetItem(case.case_type)
        type_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row, 4, type_item)
        
        # 设置行工具提示
        tooltip = self._create_tooltip(case)
        for col in range(5):
            item = self.table.item(row, col)
            if item:
                item.setToolTip(tooltip)
    
    def _get_priority_color(self, priority: str) -> QColor:
        """根据优先级获取背景颜色
        
        Args:
            priority: 优先级字符串
            
        Returns:
            对应的颜色
        """
        color_map = {
            "P0": QColor(255, 200, 200),  # 浅红色
            "P1": QColor(255, 230, 200),  # 浅橙色
            "P2": QColor(200, 255, 200),  # 浅绿色
            "P3": QColor(230, 230, 230),  # 浅灰色
        }
        
        return color_map.get(priority, QColor(255, 255, 255))
    
    def _create_tooltip(self, case: TestCase) -> str:
        """创建工具提示文本
        
        Args:
            case: 测试用例对象
            
        Returns:
            工具提示文本
        """
        category = case.category.value if hasattr(case.category, 'value') else str(case.category)
        priority = case.priority.value if hasattr(case.priority, 'value') else str(case.priority)
        
        tooltip_parts = [
            f"ID: {case.test_case_id}",
            f"标题: {case.title}",
            f"类别: {category}",
            f"优先级: {priority}",
            f"类型: {case.case_type}",
            f"步骤数: {len(case.steps)}",
            "",
            "双击查看详细信息"
        ]
        
        return "\n".join(tooltip_parts)
    
    def _update_stats(self):
        """更新统计信息"""
        total = len(self.test_cases)
        
        # 统计各类别数量
        category_counts = {}
        priority_counts = {}
        
        for case in self.test_cases:
            # 类别统计
            category = case.category.value if hasattr(case.category, 'value') else str(case.category)
            category_counts[category] = category_counts.get(category, 0) + 1
            
            # 优先级统计
            priority = case.priority.value if hasattr(case.priority, 'value') else str(case.priority)
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        # 构建统计文本
        stats_parts = [f"共 {total} 个测试用例"]
        
        self.stats_label.setText(" ".join(stats_parts))
    
    def _on_cell_double_clicked(self, row: int, column: int):
        """单元格被双击
        
        Args:
            row: 行索引
            column: 列索引
        """
        if 0 <= row < len(self.test_cases):
            case = self.test_cases[row]
            self._show_case_details(case)
            self.case_selected.emit(row)
    
    def _show_case_details(self, case: TestCase):
        """显示测试用例详情
        
        Args:
            case: 测试用例对象
        """
        dialog = QDialog(self)
        dialog.setWindowTitle(f"测试用例详情 - {case.test_case_id}")
        dialog.setMinimumWidth(600)
        dialog.setMinimumHeight(400)
        
        layout = QVBoxLayoutDialog(dialog)
        
        # 创建详情文本
        details = self._format_case_details(case)
        
        # 文本编辑器
        text_edit = QTextEdit()
        text_edit.setPlainText(details)
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)
        
        # 关闭按钮
        close_button = QPushButton("关闭")
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button)
        
        dialog.exec()
    
    def _format_case_details(self, case: TestCase) -> str:
        """格式化测试用例详情
        
        Args:
            case: 测试用例对象
            
        Returns:
            格式化后的详情文本
        """
        category = case.category.value if hasattr(case.category, 'value') else str(case.category)
        priority = case.priority.value if hasattr(case.priority, 'value') else str(case.priority)
        
        lines = [
            f"测试用例 ID: {case.test_case_id}",
            f"标题: {case.title}",
            f"类别: {category}",
            f"优先级: {priority}",
            f"类型: {case.case_type}",
            "",
        ]
        
        if case.description:
            lines.extend([
                "描述:",
                case.description,
                "",
            ])
        
        lines.append("测试步骤:")
        for step in case.steps:
            lines.append(f"  {step.step_no}. {step.action}")
            lines.append(f"     期望: {step.expected}")
        
        lines.extend([
            "",
            "最终期望结果:",
            case.expected_result,
        ])
        
        return "\n".join(lines)
    
    def clear(self):
        """清空测试用例"""
        self.table.setRowCount(0)
        self.test_cases = []
        self.stats_label.setText("共 0 个测试用例")
        self.logger.debug("测试用例已清空")
    
    def get_test_cases(self) -> List[TestCase]:
        """获取所有测试用例
        
        Returns:
            测试用例列表
        """
        return self.test_cases
