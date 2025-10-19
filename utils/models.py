"""
数据模型定义

使用 Pydantic 定义系统中使用的所有数据模型，包括测试要点、测试用例等。
"""

from pydantic import BaseModel, Field
from typing import List
from enum import Enum


class TestCategory(str, Enum):
    """测试类别枚举"""
    FUNCTIONAL = "功能测试"
    PERFORMANCE = "性能测试"
    SECURITY = "安全测试"
    COMPATIBILITY = "兼容性测试"
    USABILITY = "易用性测试"


class TestType(str, Enum):
    """测试类型枚举"""
    POSITIVE = "正向测试"
    NEGATIVE = "负向测试"
    BOUNDARY = "边界测试"


class Priority(str, Enum):
    """优先级枚举"""
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"


class TestPoint(BaseModel):
    """测试要点模型"""
    id: str = Field(..., description="测试要点 ID")
    category: TestCategory = Field(..., description="测试类别")
    description: str = Field(..., description="测试要点描述")
    test_type: TestType = Field(..., description="测试类型")
    priority: Priority = Field(..., description="优先级")
    scenarios: List[str] = Field(default_factory=list, description="测试场景")

    class Config:
        """Pydantic 配置"""
        use_enum_values = False


class TestPointsResult(BaseModel):
    """测试要点分析结果模型"""
    feature_name: str = Field(..., description="功能名称")
    test_points: List[TestPoint] = Field(..., description="测试要点列表")

    class Config:
        """Pydantic 配置"""
        use_enum_values = False


class TestStep(BaseModel):
    """测试步骤模型"""
    step_no: int = Field(..., description="步骤编号")
    action: str = Field(..., description="操作步骤")
    expected: str = Field(..., description="期望结果")

    class Config:
        """Pydantic 配置"""
        use_enum_values = False


class TestCase(BaseModel):
    """测试用例模型"""
    test_case_id: str = Field(..., description="测试用例 ID")
    title: str = Field(..., description="用例标题")
    category: TestCategory = Field(..., description="测试类别")
    priority: Priority = Field(..., description="优先级")
    case_type: str = Field(..., description="用例类型")
    steps: List[TestStep] = Field(..., description="测试步骤")
    expected_result: str = Field(..., description="最终期望结果")
    automation_feasible: bool = Field(..., description="自动化可行性")
    description: str = Field(default="", description="用例描述")

    class Config:
        """Pydantic 配置"""
        use_enum_values = False
