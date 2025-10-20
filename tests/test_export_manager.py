"""
导出管理器测试
"""

import pytest
import json
from pathlib import Path
from core.export_manager import ExportManager
from utils.models import TestCase, TestStep, TestCategory, Priority


@pytest.fixture
def sample_test_cases():
    """创建示例测试用例"""
    return [
        TestCase(
            test_case_id="TC_功能_001",
            title="用户登录验证",
            category=TestCategory.FUNCTIONAL,
            priority=Priority.P1,
            case_type="正向用例",
            steps=[
                TestStep(step_no=1, action="打开登录页面", expected="页面正常显示"),
                TestStep(step_no=2, action="输入用户名密码", expected="输入成功"),
                TestStep(step_no=3, action="点击登录按钮", expected="登录成功")
            ],
            expected_result="用户成功登录系统",
            description="验证用户登录功能"
        ),
        TestCase(
            test_case_id="TC_功能_002",
            title="密码错误提示",
            category=TestCategory.FUNCTIONAL,
            priority=Priority.P2,
            case_type="负向用例",
            steps=[
                TestStep(step_no=1, action="打开登录页面", expected="页面正常显示"),
                TestStep(step_no=2, action="输入错误密码", expected="输入成功"),
                TestStep(step_no=3, action="点击登录按钮", expected="显示错误提示")
            ],
            expected_result="系统显示密码错误提示",
            description="验证密码错误处理"
        ),
        TestCase(
            test_case_id="TC_性能_001",
            title="登录响应时间",
            category=TestCategory.PERFORMANCE,
            priority=Priority.P1,
            case_type="性能测试",
            steps=[
                TestStep(step_no=1, action="发起登录请求", expected="请求发送成功"),
                TestStep(step_no=2, action="测量响应时间", expected="记录时间")
            ],
            expected_result="登录响应时间小于2秒",
            description="验证登录性能"
        )
    ]


@pytest.fixture
def export_manager():
    """创建导出管理器实例"""
    return ExportManager()


@pytest.fixture
def temp_output_dir(tmp_path):
    """创建临时输出目录"""
    output_dir = tmp_path / "exports"
    output_dir.mkdir()
    return output_dir


class TestExportManager:
    """导出管理器测试类"""
    
    def test_export_to_json_success(self, export_manager, sample_test_cases, temp_output_dir):
        """测试成功导出 JSON"""
        output_path = temp_output_dir / "test_cases.json"
        
        result = export_manager.export_to_json(sample_test_cases, str(output_path))
        
        assert result is True
        assert output_path.exists()
        
        # 验证 JSON 内容
        with open(output_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert "metadata" in data
        assert "statistics" in data
        assert "test_cases_by_category" in data
        assert data["metadata"]["total_cases"] == 3
    
    def test_export_to_json_with_empty_cases(self, export_manager, temp_output_dir):
        """测试导出空用例列表"""
        output_path = temp_output_dir / "empty_cases.json"
        
        result = export_manager.export_to_json([], str(output_path))
        
        assert result is True
        assert output_path.exists()
        
        with open(output_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert data["metadata"]["total_cases"] == 0
        assert data["statistics"]["total_count"] == 0
    
    def test_group_by_category(self, export_manager, sample_test_cases):
        """测试按类别分组"""
        grouped = export_manager._group_by_category(sample_test_cases)
        
        assert "功能测试" in grouped
        assert "性能测试" in grouped
        assert len(grouped["功能测试"]) == 2
        assert len(grouped["性能测试"]) == 1
    
    def test_calculate_statistics(self, export_manager, sample_test_cases):
        """测试统计信息计算"""
        stats = export_manager._calculate_statistics(sample_test_cases)
        
        assert stats["total_count"] == 3
        assert stats["priority_distribution"]["P1"] == 2
        assert stats["priority_distribution"]["P2"] == 1
        assert stats["category_distribution"]["功能测试"] == 2
        assert stats["category_distribution"]["性能测试"] == 1
    
    def test_calculate_statistics_empty(self, export_manager):
        """测试空列表的统计信息"""
        stats = export_manager._calculate_statistics([])
        
        assert stats["total_count"] == 0
    
    def test_export_to_xmind_success(self, export_manager, sample_test_cases, temp_output_dir):
        """测试成功导出 XMind"""
        output_path = temp_output_dir / "test_cases.xmind"
        
        result = export_manager.export_to_xmind(sample_test_cases, str(output_path))
        
        assert result is True
        assert output_path.exists()
    
    def test_json_export_structure(self, export_manager, sample_test_cases, temp_output_dir):
        """测试 JSON 导出结构完整性"""
        output_path = temp_output_dir / "structure_test.json"
        
        export_manager.export_to_json(sample_test_cases, str(output_path))
        
        with open(output_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 验证元数据
        assert "export_time" in data["metadata"]
        assert "version" in data["metadata"]
        
        # 验证统计信息
        assert "priority_distribution" in data["statistics"]
        assert "category_distribution" in data["statistics"]
        assert "type_distribution" in data["statistics"]
        
        # 验证测试用例结构
        for category, cases in data["test_cases_by_category"].items():
            for case in cases:
                assert "test_case_id" in case
                assert "title" in case
                assert "steps" in case
                assert isinstance(case["steps"], list)
                for step in case["steps"]:
                    assert "step_no" in step
                    assert "action" in step
                    assert "expected" in step
