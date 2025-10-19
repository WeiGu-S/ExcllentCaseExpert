"""
XMind 导出器

负责将测试用例导出为 XMind 思维导图格式。
"""

from typing import List, Dict
from datetime import datetime
from pathlib import Path
import xmind
from xmind.core.topic import TopicElement
from xmind.core.markerref import MarkerId
from utils.models import TestCase, Priority
from utils.log_manager import StructuredLogger

logger = StructuredLogger()


class XMindExporter:
    """XMind 导出器"""
    
    # 优先级颜色映射
    PRIORITY_COLORS = {
        Priority.P0: "#FF0000",  # 红色
        Priority.P1: "#FF8C00",  # 橙色
        Priority.P2: "#FFD700",  # 黄色
        Priority.P3: "#90EE90",  # 绿色
    }
    
    # 优先级图标映射
    PRIORITY_MARKERS = {
        Priority.P0: MarkerId.starRed,
        Priority.P1: MarkerId.starOrange,
        Priority.P2: MarkerId.starYellow,
        Priority.P3: MarkerId.starGreen,
    }
    
    def __init__(self):
        """初始化 XMind 导出器"""
        self.workbook = None
        self.sheet = None
        self.root_topic = None
        self.category_topics = {}
        self.logger = logger
    
    def create_workbook(self, title: str):
        """创建 XMind 工作簿"""
        try:
            # 创建新工作簿
            from xmind.core import workbook
            from xmind.core.styles import StylesBookDocument
            from xmind.core.comments import CommentsBookDocument
            import tempfile
            
            self.workbook = workbook.WorkbookDocument()
            
            # 设置临时路径（xmind 库需要一个路径来保存）
            temp_file = tempfile.NamedTemporaryFile(suffix='.xmind', delete=False)
            temp_path = temp_file.name
            temp_file.close()
            self.workbook.set_path(temp_path)
            
            # 初始化必需的组件
            if not self.workbook.stylesbook:
                self.workbook.stylesbook = StylesBookDocument()
            
            if not self.workbook.commentsbook:
                self.workbook.commentsbook = CommentsBookDocument()
            
            self.sheet = self.workbook.getPrimarySheet()
            
            # 设置根主题
            date_str = datetime.now().strftime("%Y-%m-%d")
            root_title = f"{title}-测试用例-{date_str}"
            self.root_topic = self.sheet.getRootTopic()
            self.root_topic.setTitle(root_title)
            
            self.logger.log_operation("xmind_workbook_created", title=root_title)
            
        except Exception as e:
            self.logger.log_error(e, {"operation": "create_workbook", "title": title})
            raise
    
    def add_test_case_topic(self, test_case: TestCase):
        """添加测试用例主题"""
        try:
            # 获取或创建类别主题
            category_name = test_case.category.value
            if category_name not in self.category_topics:
                category_topic = self.root_topic.addSubTopic()
                category_topic.setTitle(f"📁 {category_name}")
                self.category_topics[category_name] = category_topic
            
            category_topic = self.category_topics[category_name]
            
            # 创建测试用例主题
            case_topic = category_topic.addSubTopic()
            case_title = f"[{test_case.priority.value}] {test_case.title}"
            case_topic.setTitle(case_title)
            
            # 添加优先级标记
            self._add_priority_marker(case_topic, test_case.priority)
            
            # 添加基本信息子主题
            info_topic = case_topic.addSubTopic()
            info_topic.setTitle("📋 基本信息")
            
            # ID
            id_topic = info_topic.addSubTopic()
            id_topic.setTitle(f"ID: {test_case.test_case_id}")
            
            # 类型
            type_topic = info_topic.addSubTopic()
            type_topic.setTitle(f"类型: {test_case.case_type}")
            
            # 自动化可行性
            auto_topic = info_topic.addSubTopic()
            auto_text = "可行" if test_case.automation_feasible else "不可行"
            auto_icon = "✅" if test_case.automation_feasible else "❌"
            auto_topic.setTitle(f"自动化: {auto_icon} {auto_text}")
            
            # 添加描述（如果有）
            if test_case.description:
                desc_topic = info_topic.addSubTopic()
                desc_topic.setTitle(f"描述: {test_case.description}")
            
            # 添加测试步骤子主题
            if test_case.steps:
                steps_topic = case_topic.addSubTopic()
                steps_topic.setTitle("📝 测试步骤")
                
                for step in test_case.steps:
                    step_topic = steps_topic.addSubTopic()
                    step_text = f"{step.step_no}. {step.action} → {step.expected}"
                    step_topic.setTitle(step_text)
            
            # 添加预期结果子主题
            result_topic = case_topic.addSubTopic()
            result_topic.setTitle("✅ 预期结果")
            
            result_detail = result_topic.addSubTopic()
            result_detail.setTitle(test_case.expected_result)
            
        except Exception as e:
            self.logger.log_error(e, {"operation": "add_test_case_topic", 
                                     "case_id": test_case.test_case_id})
            raise
    
    def add_statistics_topic(self, test_cases: List[TestCase]):
        """添加统计信息主题"""
        try:
            # 创建统计信息主题
            stats_topic = self.root_topic.addSubTopic()
            stats_topic.setTitle("📊 统计信息")
            
            # 总用例数
            total_topic = stats_topic.addSubTopic()
            total_topic.setTitle(f"总用例数: {len(test_cases)}")
            
            # 优先级分布
            priority_dist = {}
            for case in test_cases:
                priority = case.priority.value
                priority_dist[priority] = priority_dist.get(priority, 0) + 1
            
            if priority_dist:
                priority_topic = stats_topic.addSubTopic()
                priority_parts = [f"{p}({c})" for p, c in sorted(priority_dist.items())]
                priority_topic.setTitle(f"优先级分布: {', '.join(priority_parts)}")
            
            # 类别分布
            category_dist = {}
            for case in test_cases:
                category = case.category.value
                category_dist[category] = category_dist.get(category, 0) + 1
            
            if category_dist:
                category_topic = stats_topic.addSubTopic()
                category_parts = [f"{c}({n})" for c, n in sorted(category_dist.items())]
                category_topic.setTitle(f"类别分布: {', '.join(category_parts)}")
            
            # 用例类型分布
            type_dist = {}
            for case in test_cases:
                case_type = case.case_type
                type_dist[case_type] = type_dist.get(case_type, 0) + 1
            
            if type_dist:
                type_topic = stats_topic.addSubTopic()
                type_parts = [f"{t}({n})" for t, n in sorted(type_dist.items())]
                type_topic.setTitle(f"类型分布: {', '.join(type_parts)}")
            
            # 自动化比例
            automation_count = sum(1 for case in test_cases if case.automation_feasible)
            automation_ratio = (automation_count / len(test_cases) * 100) if test_cases else 0
            
            auto_topic = stats_topic.addSubTopic()
            auto_topic.setTitle(f"自动化比例: {automation_ratio:.1f}% ({automation_count}/{len(test_cases)})")
            
        except Exception as e:
            self.logger.log_error(e, {"operation": "add_statistics_topic"})
            raise
    
    def save(self, output_path: str):
        """保存 XMind 文件
        
        Args:
            output_path: 输出文件路径
        """
        try:
            # 确保输出目录存在
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 保存工作簿（except_attachments=True 避免读取原始文件）
            xmind.save(self.workbook, str(output_file), except_attachments=True)
            
            self.logger.log_operation("xmind_saved", output_path=output_path)
            
        except Exception as e:
            self.logger.log_error(e, {"operation": "save", "output_path": output_path})
            raise
    
    def _add_priority_marker(self, topic: TopicElement, priority: Priority):
        """添加优先级标记"""
        try:
            # 添加优先级图标标记
            marker = self.PRIORITY_MARKERS.get(priority)
            if marker:
                topic.addMarker(marker)
            
            # 注意：xmind 库可能不支持直接设置颜色
            # 如果需要颜色，可能需要使用更底层的 API 或其他库
            
        except Exception as e:
            self.logger.log_error(e, {"operation": "_add_priority_marker", 
                                     "priority": priority.value})
            # 标记添加失败不应该中断整个流程
            pass
