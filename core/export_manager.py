"""
导出管理器

负责将测试用例导出为多种格式（JSON、XMind）。
"""

import json
from typing import List, Dict
from pathlib import Path
from datetime import datetime
from utils.models import TestCase, TestCategory, Priority
from utils.exceptions import ExportException
from utils.log_manager import StructuredLogger

logger = StructuredLogger()


class ExportManager:
    """导出管理器"""
    
    def __init__(self):
        """初始化导出管理器"""
        self.logger = logger
    
    def export_to_json(self, test_cases: List[TestCase], output_path: str) -> bool:
        """导出为 JSON 格式
        
        Args:
            test_cases: 测试用例列表
            output_path: 输出文件路径
            
        Returns:
            是否成功
            
        Raises:
            ExportException: 导出失败
        """
        try:
            self.logger.log_operation("export_to_json", 
                                     case_count=len(test_cases),
                                     output_path=output_path)
            
            # 分组用例
            grouped_cases = self._group_by_category(test_cases)
            
            # 计算统计信息
            statistics = self._calculate_statistics(test_cases)
            
            # 构建导出数据
            export_data = {
                "metadata": {
                    "export_time": datetime.now().isoformat(),
                    "total_cases": len(test_cases),
                    "version": "1.0"
                },
                "statistics": statistics,
                "test_cases_by_category": {}
            }
            
            # 添加分组的测试用例
            for category, cases in grouped_cases.items():
                export_data["test_cases_by_category"][category] = [
                    {
                        "test_case_id": case.test_case_id,
                        "title": case.title,
                        "category": case.category.value,
                        "priority": case.priority.value,
                        "case_type": case.case_type,
                        "steps": [
                            {
                                "step_no": step.step_no,
                                "action": step.action,
                                "expected": step.expected
                            }
                            for step in case.steps
                        ],
                        "expected_result": case.expected_result,
                        "automation_feasible": case.automation_feasible,
                        "description": case.description
                    }
                    for case in cases
                ]
            
            # 写入文件
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            self.logger.log_operation("export_to_json_success", 
                                     output_path=output_path)
            return True
            
        except Exception as e:
            self.logger.log_error(e, {"operation": "export_to_json", 
                                     "output_path": output_path})
            raise ExportException(f"JSON 导出失败: {str(e)}")
    
    def export_to_xmind(self, test_cases: List[TestCase], output_path: str) -> bool:
        """导出为 XMind 格式
        
        Args:
            test_cases: 测试用例列表
            output_path: 输出文件路径
            
        Returns:
            是否成功
            
        Raises:
            ExportException: 导出失败
        """
        try:
            from core.xmind_exporter import XMindExporter
            
            self.logger.log_operation("export_to_xmind", 
                                     case_count=len(test_cases),
                                     output_path=output_path)
            
            # 创建 XMind 导出器
            exporter = XMindExporter()
            
            # 创建工作簿
            project_name = Path(output_path).stem
            exporter.create_workbook(project_name)
            
            # 分组用例
            grouped_cases = self._group_by_category(test_cases)
            
            # 添加测试用例
            for category, cases in grouped_cases.items():
                for case in cases:
                    exporter.add_test_case_topic(case)
            
            # 添加统计信息
            exporter.add_statistics_topic(test_cases)
            
            # 保存文件
            exporter.save(output_path)
            
            self.logger.log_operation("export_to_xmind_success", 
                                     output_path=output_path)
            return True
            
        except Exception as e:
            self.logger.log_error(e, {"operation": "export_to_xmind", 
                                     "output_path": output_path})
            raise ExportException(f"XMind 导出失败: {str(e)}")
    
    def _group_by_category(self, test_cases: List[TestCase]) -> Dict[str, List[TestCase]]:
        """按类别分组用例
        
        Args:
            test_cases: 测试用例列表
            
        Returns:
            分组后的用例字典，键为类别名称
        """
        grouped = {}
        for case in test_cases:
            category_name = case.category.value
            if category_name not in grouped:
                grouped[category_name] = []
            grouped[category_name].append(case)
        
        return grouped
    
    def _calculate_statistics(self, test_cases: List[TestCase]) -> Dict:
        """计算统计信息
        
        Args:
            test_cases: 测试用例列表
            
        Returns:
            统计信息字典
        """
        if not test_cases:
            return {
                "total_count": 0,
                "priority_distribution": {},
                "category_distribution": {},
                "type_distribution": {},
                "automation_ratio": 0.0
            }
        
        # 优先级分布
        priority_dist = {}
        for priority in Priority:
            count = sum(1 for case in test_cases if case.priority == priority)
            if count > 0:
                priority_dist[priority.value] = count
        
        # 类别分布
        category_dist = {}
        for category in TestCategory:
            count = sum(1 for case in test_cases if case.category == category)
            if count > 0:
                category_dist[category.value] = count
        
        # 用例类型分布
        type_dist = {}
        for case in test_cases:
            case_type = case.case_type
            type_dist[case_type] = type_dist.get(case_type, 0) + 1
        
        # 自动化比例
        automation_count = sum(1 for case in test_cases if case.automation_feasible)
        automation_ratio = (automation_count / len(test_cases)) * 100 if test_cases else 0.0
        
        return {
            "total_count": len(test_cases),
            "priority_distribution": priority_dist,
            "category_distribution": category_dist,
            "type_distribution": type_dist,
            "automation_ratio": round(automation_ratio, 2),
            "automation_count": automation_count
        }
