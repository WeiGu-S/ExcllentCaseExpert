"""
测试用例生成器

根据测试要点生成详细的测试用例，支持正向、负向、边界和异常用例生成。
"""

from typing import Dict, List
from enum import Enum
from utils.models import TestCase, TestStep, TestCategory, Priority, TestPoint
from utils.log_manager import StructuredLogger
import re


class CaseType(Enum):
    """测试用例类型枚举"""
    POSITIVE = "正向用例"
    NEGATIVE = "负向用例"
    BOUNDARY = "边界用例"
    EXCEPTION = "异常用例"


class TestCaseGenerator:
    """测试用例生成器"""
    
    def __init__(self):
        """初始化测试用例生成器"""
        self.case_counter = 0
        self.generated_cases = []
        self.logger = StructuredLogger("TestCaseGenerator")
        
        # 负向测试关键词
        self.negative_keywords = [
            "无效", "错误", "空值", "权限", "非法", "异常",
            "失败", "拒绝", "禁止", "超时", "不存在"
        ]
        
        # 边界测试关键词
        self.boundary_keywords = [
            "最大", "最小", "长度", "范围", "限制", "上限",
            "下限", "边界", "临界", "极限"
        ]
        

    
    def generate_test_cases(self, test_points: Dict) -> List[Dict]:
        """生成测试用例"""
        self.logger.log_operation("generate_test_cases_start", 
                                  feature_name=test_points.get("feature_name", ""))
        
        self.case_counter = 0
        self.generated_cases = []
        
        test_point_list = test_points.get("test_points", [])
        
        for test_point_dict in test_point_list:
            # 将字典转换为 TestPoint 对象
            try:
                if isinstance(test_point_dict, dict):
                    test_point = TestPoint(**test_point_dict)
                else:
                    test_point = test_point_dict
            except Exception as e:
                self.logger.error(f"转换测试要点失败: {str(e)}, 数据: {test_point_dict}")
                continue
            
            # 根据测试要点生成不同类型的用例
            cases = []
            
            # 生成正向用例
            positive_cases = self._generate_positive_cases(test_point)
            cases.extend(positive_cases)
            
            # 生成负向用例
            negative_cases = self._generate_negative_cases(test_point)
            cases.extend(negative_cases)
            
            # 生成边界用例
            boundary_cases = self._generate_boundary_cases(test_point)
            cases.extend(boundary_cases)
            
            # 生成异常用例
            exception_cases = self._generate_exception_cases(test_point)
            cases.extend(exception_cases)
            
            self.generated_cases.extend(cases)
        
        # 验证和去重
        validated_cases = self._validate_and_deduplicate(self.generated_cases)
        
        # 转换为字典格式
        result = [case.dict() for case in validated_cases]
        
        self.logger.log_operation("generate_test_cases_complete", 
                                  total_cases=len(result))
        
        return result
    
    def _generate_positive_cases(self, test_point: TestPoint) -> List[TestCase]:
        """生成正向测试用例"""
        cases = []
        
        # 为每个场景生成一个正向用例
        if test_point.scenarios:
            for scenario in test_point.scenarios:
                case = self._create_base_case(test_point, CaseType.POSITIVE)
                case.title = f"{test_point.description} - {scenario}"
                case.description = f"验证{scenario}的正常功能"
                
                # 生成测试步骤
                steps = self._generate_positive_steps(test_point, scenario)
                case.steps = steps
                
                # 设置预期结果
                case.expected_result = f"{scenario}执行成功，系统功能正常"
                

                
                cases.append(case)
        else:
            # 如果没有场景，生成一个通用正向用例
            case = self._create_base_case(test_point, CaseType.POSITIVE)
            case.title = f"{test_point.description} - 正常流程"
            case.description = f"验证{test_point.description}的正常功能"
            
            steps = self._generate_positive_steps(test_point, "标准操作")
            case.steps = steps
            
            case.expected_result = "功能执行成功，系统运行正常"
            
            cases.append(case)
        
        return cases
    
    def _generate_negative_cases(self, test_point: TestPoint) -> List[TestCase]:
        """生成负向测试用例"""
        cases = []
        
        # 检查是否包含负向测试关键词
        has_negative = any(keyword in test_point.description 
                          for keyword in self.negative_keywords)
        
        if has_negative or test_point.test_type.value == "负向测试":
            # 生成常见的负向场景
            negative_scenarios = [
                ("无效输入", "输入无效或非法数据"),
                ("空值输入", "输入空值或null"),
                ("权限不足", "使用无权限的用户操作")
            ]
            
            for scenario_name, scenario_desc in negative_scenarios:
                case = self._create_base_case(test_point, CaseType.NEGATIVE)
                case.title = f"{test_point.description} - {scenario_name}"
                case.description = f"验证{scenario_desc}时的错误处理"
                
                steps = self._generate_negative_steps(test_point, scenario_name)
                case.steps = steps
                
                case.expected_result = "系统正确处理异常，显示友好的错误提示"
                
                cases.append(case)
        
        return cases
    
    def _generate_boundary_cases(self, test_point: TestPoint) -> List[TestCase]:
        """生成边界测试用例"""
        cases = []
        
        # 检查是否包含边界测试关键词
        has_boundary = any(keyword in test_point.description 
                          for keyword in self.boundary_keywords)
        
        if has_boundary or test_point.test_type.value == "边界测试":
            # 生成边界场景
            boundary_scenarios = [
                ("最小值", "输入最小允许值"),
                ("最大值", "输入最大允许值"),
                ("超界值", "输入超出范围的值")
            ]
            
            for scenario_name, scenario_desc in boundary_scenarios:
                case = self._create_base_case(test_point, CaseType.BOUNDARY)
                case.title = f"{test_point.description} - {scenario_name}"
                case.description = f"验证{scenario_desc}时的边界处理"
                
                steps = self._generate_boundary_steps(test_point, scenario_name)
                case.steps = steps
                
                if scenario_name == "超界值":
                    case.expected_result = "系统拒绝超界输入，显示边界限制提示"
                else:
                    case.expected_result = f"系统正确处理{scenario_name}，功能正常"
                
                cases.append(case)
        
        return cases
    
    def _generate_exception_cases(self, test_point: TestPoint) -> List[TestCase]:
        """生成异常测试用例"""
        cases = []
        
        # 为高优先级测试要点生成异常用例
        if test_point.priority in [Priority.P0, Priority.P1]:
            exception_scenarios = [
                ("网络异常", "模拟网络中断或超时"),
                ("系统异常", "模拟系统资源不足或服务不可用")
            ]
            
            for scenario_name, scenario_desc in exception_scenarios:
                case = self._create_base_case(test_point, CaseType.EXCEPTION)
                case.title = f"{test_point.description} - {scenario_name}"
                case.description = f"验证{scenario_desc}时的异常处理"
                
                steps = self._generate_exception_steps(test_point, scenario_name)
                case.steps = steps
                
                case.expected_result = "系统优雅降级，保持稳定性，提供友好提示"
                
                cases.append(case)
        
        return cases
    
    def _generate_positive_steps(self, test_point: TestPoint, 
                                 scenario: str) -> List[TestStep]:
        """生成正向测试步骤"""
        steps = []
        
        # 步骤1: 准备
        steps.append(TestStep(
            step_no=1,
            action=f"准备测试环境和数据，确保满足{scenario}的前置条件",
            expected="测试环境就绪，数据准备完成"
        ))
        
        # 步骤2: 执行
        steps.append(TestStep(
            step_no=2,
            action=f"执行{test_point.description}的{scenario}操作",
            expected="操作执行成功，无错误提示"
        ))
        
        # 步骤3: 验证
        steps.append(TestStep(
            step_no=3,
            action="验证功能结果是否符合预期",
            expected="功能结果正确，数据一致"
        ))
        
        return steps
    
    def _generate_negative_steps(self, test_point: TestPoint, 
                                 scenario: str) -> List[TestStep]:
        """生成负向测试步骤"""
        steps = []
        
        # 步骤1: 准备异常数据
        steps.append(TestStep(
            step_no=1,
            action=f"准备{scenario}的测试数据",
            expected="异常测试数据准备完成"
        ))
        
        # 步骤2: 执行操作
        steps.append(TestStep(
            step_no=2,
            action=f"使用异常数据执行{test_point.description}",
            expected="系统检测到异常输入"
        ))
        
        # 步骤3: 验证错误处理
        steps.append(TestStep(
            step_no=3,
            action="验证系统的错误处理和提示信息",
            expected="显示明确的错误提示，系统保持稳定"
        ))
        
        return steps
    
    def _generate_boundary_steps(self, test_point: TestPoint, 
                                 scenario: str) -> List[TestStep]:
        """生成边界测试步骤"""
        steps = []
        
        # 步骤1: 准备边界数据
        steps.append(TestStep(
            step_no=1,
            action=f"准备{scenario}的边界测试数据",
            expected="边界测试数据准备完成"
        ))
        
        # 步骤2: 执行操作
        steps.append(TestStep(
            step_no=2,
            action=f"使用边界数据执行{test_point.description}",
            expected="系统接受并处理边界数据"
        ))
        
        # 步骤3: 验证边界处理
        steps.append(TestStep(
            step_no=3,
            action="验证系统对边界值的处理是否正确",
            expected="边界值处理符合规范，无异常"
        ))
        
        return steps
    
    def _generate_exception_steps(self, test_point: TestPoint, 
                                  scenario: str) -> List[TestStep]:
        """生成异常测试步骤"""
        steps = []
        
        # 步骤1: 模拟异常
        steps.append(TestStep(
            step_no=1,
            action=f"模拟{scenario}的异常环境",
            expected="异常环境模拟成功"
        ))
        
        # 步骤2: 执行操作
        steps.append(TestStep(
            step_no=2,
            action=f"在异常环境下执行{test_point.description}",
            expected="系统检测到异常情况"
        ))
        
        # 步骤3: 验证异常处理
        steps.append(TestStep(
            step_no=3,
            action="验证系统的异常处理和恢复机制",
            expected="系统优雅降级，提供友好提示，保持稳定"
        ))
        
        return steps
    
    def _create_base_case(self, test_point: TestPoint, 
                         case_type: CaseType) -> TestCase:
        """创建基础测试用例结构"""
        self.case_counter += 1
        
        # 生成用例ID
        category_abbr = self._get_category_abbreviation(test_point.category)
        test_case_id = f"TC_{category_abbr}_{self.case_counter:03d}"
        
        # 创建测试用例
        case = TestCase(
            test_case_id=test_case_id,
            title="",  # 将在具体生成方法中设置
            category=test_point.category,
            priority=test_point.priority,
            case_type=case_type.value,
            steps=[],  # 将在具体生成方法中设置
            expected_result="",  # 将在具体生成方法中设置
            description=""  # 将在具体生成方法中设置
        )
        
        return case
    
    def _get_category_abbreviation(self, category: TestCategory) -> str:
        """获取测试类别缩写"""
        abbreviations = {
            TestCategory.FUNCTIONAL: "功能",
            TestCategory.PERFORMANCE: "性能",
            TestCategory.SECURITY: "安全",
            TestCategory.COMPATIBILITY: "兼容",
            TestCategory.USABILITY: "易用"
        }
        return abbreviations.get(category, "其他")
    

    
    def _validate_and_deduplicate(self, cases: List[TestCase]) -> List[TestCase]:
        """验证和去重测试用例"""
        validated_cases = []
        seen_signatures = set()
        
        for case in cases:
            # 验证必填字段
            if not case.test_case_id or not case.title or not case.steps:
                self.logger.log_operation("invalid_case_skipped", 
                                         case_id=case.test_case_id)
                continue
            
            # 验证步骤完整性
            valid_steps = True
            for step in case.steps:
                if not step.action or not step.expected:
                    valid_steps = False
                    break
            
            if not valid_steps:
                self.logger.log_operation("invalid_steps_skipped", 
                                         case_id=case.test_case_id)
                continue
            
            # 生成用例签名用于去重
            signature = self._generate_case_signature(case)
            
            # 检查是否重复
            if signature in seen_signatures:
                self.logger.log_operation("duplicate_case_skipped", 
                                         case_id=case.test_case_id,
                                         title=case.title)
                continue
            
            seen_signatures.add(signature)
            validated_cases.append(case)
        
        return validated_cases
    
    def _generate_case_signature(self, case: TestCase) -> str:
        """生成用例签名用于去重 """
        # 使用标题和步骤生成签名
        title_normalized = re.sub(r'\s+', '', case.title.lower())
        steps_text = ''.join([f"{s.action}{s.expected}" for s in case.steps])
        steps_normalized = re.sub(r'\s+', '', steps_text.lower())
        
        signature = f"{title_normalized}_{steps_normalized}"
        return signature
