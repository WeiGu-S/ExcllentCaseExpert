"""
测试要点展示组件

提供测试要点列表展示，支持优先级颜色标识。
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QLabel, QListWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from typing import List, Dict

from utils.models import TestPoint, Priority
from utils.log_manager import get_logger


class TestPointWidget(QWidget):
    """测试要点展示组件"""
    
    # 信号定义
    point_selected = pyqtSignal(int)  # 测试要点被选中，参数为索引
    
    def __init__(self, parent=None):
        """初始化测试要点组件
        
        Args:
            parent: 父组件
        """
        super().__init__(parent)
        self.logger = get_logger()
        self.test_points: List[TestPoint] = []
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 标题
        title = QLabel("🎯 测试要点")
        title.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px;")
        layout.addWidget(title)
        
        # 统计标签
        self.stats_label = QLabel("共 0 个测试要点")
        self.stats_label.setStyleSheet("color: gray; padding: 2px 5px;")
        layout.addWidget(self.stats_label)
        
        # 列表
        self.list_widget = QListWidget()
        self.list_widget.setAlternatingRowColors(True)
        self.list_widget.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self.list_widget)
        
        self.logger.debug("TestPointWidget 初始化完成")
    
    def set_test_points(self, test_points_data: Dict):
        """设置测试要点
        
        Args:
            test_points_data: 测试要点数据字典，包含 feature_name 和 test_points
        """
        self.list_widget.clear()
        self.test_points = []
        
        feature_name = test_points_data.get("feature_name", "")
        points_data = test_points_data.get("test_points", [])
        
        # 添加功能名称作为标题
        if feature_name:
            title_item = QListWidgetItem(f"【{feature_name}】")
            title_item.setForeground(QColor(0, 0, 255))
            title_item.setFlags(Qt.ItemFlag.NoItemFlags)  # 不可选中
            font = title_item.font()
            font.setBold(True)
            title_item.setFont(font)
            self.list_widget.addItem(title_item)
        
        # 添加测试要点
        for point_data in points_data:
            try:
                # 转换为 TestPoint 对象
                if isinstance(point_data, TestPoint):
                    point = point_data
                else:
                    point = TestPoint(**point_data)
                
                self.test_points.append(point)
                
                # 创建列表项
                item_text = self._format_test_point(point)
                item = QListWidgetItem(item_text)
                
                # 根据优先级设置颜色
                color = self._get_priority_color(point.priority)
                item.setForeground(color)
                
                # 设置工具提示
                tooltip = self._create_tooltip(point)
                item.setToolTip(tooltip)
                
                self.list_widget.addItem(item)
                
            except Exception as e:
                self.logger.error(f"添加测试要点失败: {e}, 数据: {point_data}")
        
        # 更新统计信息
        self._update_stats()
        
        self.logger.info(f"已加载 {len(self.test_points)} 个测试要点")
    
    def _format_test_point(self, point: TestPoint) -> str:
        """格式化测试要点显示文本
        
        Args:
            point: 测试要点对象
            
        Returns:
            格式化后的文本
        """
        priority = point.priority.value if hasattr(point.priority, 'value') else str(point.priority)
        category = point.category.value if hasattr(point.category, 'value') else str(point.category)
        test_type = point.test_type.value if hasattr(point.test_type, 'value') else str(point.test_type)
        
        return f"[{priority}] {point.description} ({category} - {test_type})"
    
    def _get_priority_color(self, priority: Priority) -> QColor:
        """根据优先级获取颜色
        
        Args:
            priority: 优先级
            
        Returns:
            对应的颜色
        """
        priority_str = priority.value if hasattr(priority, 'value') else str(priority)
        
        color_map = {
            "P0": QColor(255, 0, 0),      # 红色 - 核心功能
            "P1": QColor(255, 140, 0),    # 橙色 - 重要功能
            "P2": QColor(0, 128, 0),      # 绿色 - 一般功能
            "P3": QColor(128, 128, 128),  # 灰色 - 次要功能
        }
        
        return color_map.get(priority_str, QColor(0, 0, 0))
    
    def _create_tooltip(self, point: TestPoint) -> str:
        """创建工具提示文本
        
        Args:
            point: 测试要点对象
            
        Returns:
            工具提示文本
        """
        category = point.category.value if hasattr(point.category, 'value') else str(point.category)
        test_type = point.test_type.value if hasattr(point.test_type, 'value') else str(point.test_type)
        priority = point.priority.value if hasattr(point.priority, 'value') else str(point.priority)
        
        tooltip_parts = [
            f"ID: {point.id}",
            f"类别: {category}",
            f"类型: {test_type}",
            f"优先级: {priority}",
            f"描述: {point.description}",
        ]
        
        if point.scenarios:
            scenarios_text = "\n  - ".join(point.scenarios)
            tooltip_parts.append(f"场景:\n  - {scenarios_text}")
        
        return "\n".join(tooltip_parts)
    
    def _update_stats(self):
        """更新统计信息"""
        total = len(self.test_points)
        
        # 统计各优先级数量
        priority_counts = {}
        for point in self.test_points:
            priority_str = point.priority.value if hasattr(point.priority, 'value') else str(point.priority)
            priority_counts[priority_str] = priority_counts.get(priority_str, 0) + 1
        
        # 构建统计文本
        stats_parts = [f"共 {total} 个测试要点"]
        
        if priority_counts:
            priority_stats = ", ".join([f"{p}: {c}" for p, c in sorted(priority_counts.items())])
            stats_parts.append(f"({priority_stats})")
        
        self.stats_label.setText(" ".join(stats_parts))
    
    def _on_item_clicked(self, item: QListWidgetItem):
        """列表项被点击
        
        Args:
            item: 被点击的列表项
        """
        index = self.list_widget.row(item)
        
        # 跳过标题行
        if index > 0 and self.test_points:
            # 调整索引（减去标题行）
            point_index = index - 1
            if 0 <= point_index < len(self.test_points):
                self.point_selected.emit(point_index)
                self.logger.debug(f"选中测试要点: {point_index}")
    
    def clear(self):
        """清空测试要点"""
        self.list_widget.clear()
        self.test_points = []
        self.stats_label.setText("共 0 个测试要点")
        self.logger.debug("测试要点已清空")
    
    def get_test_points(self) -> List[TestPoint]:
        """获取所有测试要点
        
        Returns:
            测试要点列表
        """
        return self.test_points
