"""
移动C端测试用例生成器

基于AI分析的测试要点，生成贴近真实移动端测试场景的测试用例。
专注于实用性和可执行性，避免冗余和模板化。
"""

from typing import Dict, List, Tuple, Optional
from utils.models import TestCase, TestStep, TestCategory, Priority, TestPoint
from utils.log_manager import StructuredLogger
import re
import random


class TestCaseGenerator:
    """移动C端测试用例生成器 - 重构版"""
    
    def __init__(self):
        """初始化测试用例生成器"""
        self.case_counter = 0
        self.logger = StructuredLogger("TestCaseGenerator")
        
        # 移动端核心测试维度
        self.mobile_dimensions = {
            "基础功能": {
                "weight": 0.6,  # 权重，决定生成用例的比例
                "scenarios": ["正常操作", "数据验证", "状态切换"]
            },
            "网络环境": {
                "weight": 0.2,
                "scenarios": ["弱网环境", "网络切换", "离线状态"]
            },
            "设备适配": {
                "weight": 0.15,
                "scenarios": ["横竖屏切换", "不同屏幕尺寸", "系统版本差异"]
            },
            "异常处理": {
                "weight": 0.05,
                "scenarios": ["中断恢复", "错误输入", "边界条件"]
            }
        }
        
        # 移动端常见操作模式
        self.mobile_actions = {
            "点击": ["轻点", "长按", "双击"],
            "滑动": ["上滑", "下滑", "左滑", "右滑"],
            "输入": ["键盘输入", "语音输入", "复制粘贴"],
            "导航": ["返回", "前进", "跳转", "刷新"]
        }
        
        # 移动端验证要点
        self.mobile_validations = {
            "界面": ["布局正确", "元素显示", "响应及时"],
            "数据": ["内容准确", "状态同步", "缓存有效"],
            "交互": ["操作流畅", "反馈明确", "逻辑正确"]
        }
        

    def generate_test_cases(self, test_points: Dict) -> List[Dict]:
        """生成移动端测试用例 - 重构版"""
        feature_name = test_points.get("feature_name", "")
        self.logger.log_operation("generate_test_cases_start", feature_name=feature_name)
        
        self.case_counter = 0
        all_cases = []
        
        test_point_list = test_points.get("test_points", [])
        
        for test_point_dict in test_point_list:
            try:
                test_point = TestPoint(**test_point_dict) if isinstance(test_point_dict, dict) else test_point_dict
                
                # 基于AI场景直接生成实用测试用例
                cases = self._generate_practical_cases(test_point)
                all_cases.extend(cases)
                
            except Exception as e:
                self.logger.error(f"处理测试要点失败: {str(e)}")
                continue
        
        # 质量控制和去重
        final_cases = self._optimize_test_cases(all_cases)
        
        # 转换为字典格式
        result = [case.dict() for case in final_cases]
        
        self.logger.log_operation("generate_test_cases_complete", total_cases=len(result))
        return result
    
    def _generate_practical_cases(self, test_point: TestPoint) -> List[TestCase]:
        """基于测试要点生成实用的测试用例"""
        cases = []
        
        # 1. 基于AI场景生成核心用例（每个场景1个用例）
        if test_point.scenarios:
            for i, scenario in enumerate(test_point.scenarios[:3]):  # 限制最多3个场景
                case = self._create_scenario_based_case(test_point, scenario, i + 1)
                if case:
                    cases.append(case)
        
        # 2. 根据测试类别和优先级补充关键用例
        additional_cases = self._generate_category_specific_cases(test_point)
        cases.extend(additional_cases)
        
        return cases
    
    def _create_scenario_based_case(self, test_point: TestPoint, scenario: str, index: int) -> Optional[TestCase]:
        """基于AI场景创建测试用例"""
        case = self._create_base_case(test_point, f"场景{index}")
        
        # 从场景描述中提取关键信息
        scenario_info = self._analyze_scenario(scenario)
        
        case.title = f"{test_point.description} - {scenario_info['name']}"
        case.description = f"验证{scenario_info['description']}"
        
        # 生成贴近真实的测试步骤
        case.steps = self._generate_realistic_steps(test_point, scenario_info)
        case.expected_result = scenario_info['expected_result']
        
        return case
    
    def _analyze_scenario(self, scenario: str) -> Dict:
        """分析AI生成的场景，提取关键信息"""
        # 简化场景名称
        name = self._extract_scenario_name(scenario)
        
        # 识别操作类型
        action_type = self._identify_action_type(scenario)
        
        # 生成期望结果
        expected_result = self._generate_expected_result(scenario, action_type)
        
        return {
            "name": name,
            "description": scenario,
            "action_type": action_type,
            "expected_result": expected_result
        }
    
    def _extract_scenario_name(self, scenario: str) -> str:
        """从场景描述中提取简洁的名称"""
        # 移除常见的前缀词
        name = re.sub(r'^(验证|测试|检查|确保)', '', scenario)
        name = re.sub(r'(的功能|的正确性|是否正常)$', '', name)
        
        # 限制长度
        if len(name) > 15:
            name = name[:12] + "..."
        
        return name.strip() or "基础功能"
    
    def _identify_action_type(self, scenario: str) -> str:
        """识别场景中的主要操作类型"""
        action_keywords = {
            "点击": ["点击", "按下", "选择", "触摸"],
            "输入": ["输入", "填写", "编辑", "修改"],
            "滑动": ["滑动", "拖拽", "滚动", "翻页"],
            "查看": ["查看", "显示", "展示", "浏览"],
            "切换": ["切换", "跳转", "导航", "返回"]
        }
        
        for action, keywords in action_keywords.items():
            if any(keyword in scenario for keyword in keywords):
                return action
        
        return "操作"
    
    def _generate_expected_result(self, scenario: str, action_type: str) -> str:
        """根据场景和操作类型生成期望结果"""
        result_templates = {
            "点击": "界面响应及时，功能执行正确",
            "输入": "数据输入成功，格式验证正确",
            "滑动": "页面滑动流畅，内容加载正常",
            "查看": "信息显示完整，布局适配良好",
            "切换": "页面跳转成功，状态保持正确",
            "操作": "功能执行成功，用户体验良好"
        }
        
        return result_templates.get(action_type, "功能正常，符合预期")
    
    def _generate_realistic_steps(self, test_point: TestPoint, scenario_info: Dict) -> List[TestStep]:
        """生成贴近真实的测试步骤"""
        steps = []
        action_type = scenario_info["action_type"]
        
        # 步骤1: 前置条件（简化）
        if self._needs_precondition(test_point):
            steps.append(TestStep(
                step_no=1,
                action=f"打开应用，进入{self._get_feature_context(test_point.description)}",
                expected="页面加载完成，界面显示正常"
            ))
        
        # 步骤2: 核心操作
        core_action = self._generate_core_action(scenario_info["description"], action_type)
        steps.append(TestStep(
            step_no=len(steps) + 1,
            action=core_action,
            expected=self._generate_action_expected(action_type)
        ))
        
        # 步骤3: 结果验证（如果需要）
        if self._needs_verification(test_point, action_type):
            steps.append(TestStep(
                step_no=len(steps) + 1,
                action="检查功能执行结果和界面状态",
                expected=scenario_info["expected_result"]
            ))
        
        return steps
    
    def _generate_category_specific_cases(self, test_point: TestPoint) -> List[TestCase]:
        """根据测试类别生成特定用例"""
        cases = []
        
        # 只为高优先级的测试要点生成额外用例
        if test_point.priority not in [Priority.P0, Priority.P1]:
            return cases
        
        # 根据类别生成1个关键用例
        if test_point.category == TestCategory.COMPATIBILITY:
            case = self._create_compatibility_case(test_point)
            if case:
                cases.append(case)
        elif test_point.category == TestCategory.USABILITY:
            case = self._create_usability_case(test_point)
            if case:
                cases.append(case)
        
        return cases
    
    def _create_compatibility_case(self, test_point: TestPoint) -> Optional[TestCase]:
        """创建兼容性测试用例"""
        case = self._create_base_case(test_point, "兼容性")
        case.title = f"{test_point.description} - 设备兼容性"
        case.description = "验证功能在不同设备和系统版本上的兼容性"
        
        case.steps = [
            TestStep(
                step_no=1,
                action="在不同屏幕尺寸的设备上打开功能页面",
                expected="页面布局自适应，元素显示完整"
            ),
            TestStep(
                step_no=2,
                action="执行核心功能操作",
                expected="功能正常执行，无兼容性问题"
            ),
            TestStep(
                step_no=3,
                action="切换横竖屏模式测试",
                expected="界面适配正确，功能保持正常"
            )
        ]
        
        case.expected_result = "功能在各种设备上兼容性良好，用户体验一致"
        return case
    
    def _create_usability_case(self, test_point: TestPoint) -> Optional[TestCase]:
        """创建易用性测试用例"""
        case = self._create_base_case(test_point, "易用性")
        case.title = f"{test_point.description} - 用户体验"
        case.description = "验证功能的易用性和用户体验"
        
        case.steps = [
            TestStep(
                step_no=1,
                action="首次使用该功能，观察操作引导",
                expected="操作流程清晰，引导信息明确"
            ),
            TestStep(
                step_no=2,
                action="执行常见操作，注意交互反馈",
                expected="操作响应及时，反馈信息友好"
            ),
            TestStep(
                step_no=3,
                action="测试错误操作的处理",
                expected="错误提示清晰，恢复操作简单"
            )
        ]
        
        case.expected_result = "功能易于理解和使用，用户体验良好"
        return case
    
    def _needs_precondition(self, test_point: TestPoint) -> bool:
        """判断是否需要前置条件步骤"""
        # 简化逻辑：只有涉及登录、权限等才需要前置条件
        precondition_keywords = ["登录", "权限", "设置", "配置"]
        return any(keyword in test_point.description for keyword in precondition_keywords)
    
    def _get_feature_context(self, description: str) -> str:
        """从描述中提取功能上下文"""
        # 提取关键功能词
        if "购物车" in description:
            return "购物车页面"
        elif "登录" in description:
            return "登录页面"
        elif "搜索" in description:
            return "搜索页面"
        elif "支付" in description:
            return "支付页面"
        else:
            return "相关功能页面"
    
    def _generate_core_action(self, scenario: str, action_type: str) -> str:
        """生成核心操作步骤"""
        action_templates = {
            "点击": f"点击相关按钮或元素，{scenario}",
            "输入": f"在输入框中{scenario}",
            "滑动": f"通过滑动手势{scenario}",
            "查看": f"查看页面内容，{scenario}",
            "切换": f"切换到目标状态，{scenario}",
            "操作": scenario
        }
        
        return action_templates.get(action_type, scenario)
    
    def _generate_action_expected(self, action_type: str) -> str:
        """生成操作的期望结果"""
        expected_templates = {
            "点击": "按钮响应，相关操作执行",
            "输入": "内容输入成功，格式验证通过",
            "滑动": "页面滑动流畅，内容正常显示",
            "查看": "信息显示完整，布局正确",
            "切换": "状态切换成功，界面更新正确",
            "操作": "操作执行成功"
        }
        
        return expected_templates.get(action_type, "操作执行成功")
    
    def _needs_verification(self, test_point: TestPoint, action_type: str) -> bool:
        """判断是否需要额外的验证步骤"""
        # 对于重要功能或复杂操作，需要验证步骤
        return (test_point.priority in [Priority.P0, Priority.P1] or 
                action_type in ["输入", "切换"] or
                len(test_point.scenarios) > 2)
    
    def _create_base_case(self, test_point: TestPoint, case_type: str) -> TestCase:
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
            case_type=case_type,
            steps=[],  # 将在具体生成方法中设置
            expected_result="",  # 将在具体生成方法中设置
            description=""  # 将在具体生成方法中设置
        )
        
        return case
    
    def _get_category_abbreviation(self, category: TestCategory) -> str:
        """获取测试类别缩写"""
        abbreviations = {
            TestCategory.FUNCTIONAL: "功能",
            TestCategory.COMPATIBILITY: "兼容",
            TestCategory.USABILITY: "易用"
        }
        return abbreviations.get(category, "其他")
    
    def _optimize_test_cases(self, cases: List[TestCase]) -> List[TestCase]:
        """优化测试用例：去重、排序、质量控制"""
        if not cases:
            return []
        
        # 1. 去重
        unique_cases = self._remove_duplicates(cases)
        
        # 2. 质量过滤
        quality_cases = self._filter_quality_cases(unique_cases)
        
        # 3. 按优先级排序
        sorted_cases = sorted(quality_cases, key=lambda x: (
            x.priority.value,  # 优先级排序
            x.category.value,  # 类别排序
            x.title  # 标题排序
        ))
        
        # 4. 控制数量（避免用例过多）
        final_cases = self._limit_case_count(sorted_cases)
        
        return final_cases
    
    def _remove_duplicates(self, cases: List[TestCase]) -> List[TestCase]:
        """移除重复的测试用例"""
        unique_cases = []
        seen_signatures = set()
        
        for case in cases:
            signature = self._generate_case_signature(case)
            if signature not in seen_signatures:
                seen_signatures.add(signature)
                unique_cases.append(case)
            else:
                self.logger.debug(f"移除重复用例: {case.title}")
        
        return unique_cases
    
    def _filter_quality_cases(self, cases: List[TestCase]) -> List[TestCase]:
        """过滤低质量的测试用例"""
        quality_cases = []
        
        for case in cases:
            # 基本质量检查
            if not case.title or not case.steps or not case.expected_result:
                self.logger.debug(f"移除不完整用例: {case.title}")
                continue
            
            # 步骤质量检查
            if not all(step.action and step.expected for step in case.steps):
                self.logger.debug(f"移除步骤不完整用例: {case.title}")
                continue
            
            # 长度合理性检查
            if len(case.title) > 50 or len(case.steps) > 5:
                self.logger.debug(f"移除过长用例: {case.title}")
                continue
            
            quality_cases.append(case)
        
        return quality_cases
    
    def _limit_case_count(self, cases: List[TestCase]) -> List[TestCase]:
        """限制用例数量，避免过多"""
        max_cases_per_priority = {
            Priority.P0: 3,  # P0最多3个
            Priority.P1: 4,  # P1最多4个
            Priority.P2: 2,  # P2最多2个
            Priority.P3: 1   # P3最多1个
        }
        
        limited_cases = []
        priority_counts = {p: 0 for p in Priority}
        
        for case in cases:
            max_count = max_cases_per_priority.get(case.priority, 2)
            if priority_counts[case.priority] < max_count:
                limited_cases.append(case)
                priority_counts[case.priority] += 1
        
        return limited_cases
    
    def _generate_case_signature(self, case: TestCase) -> str:
        """生成用例签名用于去重"""
        # 使用标题的关键词生成签名
        title_words = re.findall(r'\w+', case.title.lower())
        title_key = '_'.join(sorted(title_words)[:3])  # 取前3个关键词
        
        # 使用步骤数量和类型
        steps_key = f"{len(case.steps)}_{case.category.value}"
        
        return f"{title_key}_{steps_key}"
