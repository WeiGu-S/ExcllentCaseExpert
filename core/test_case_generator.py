"""
移动C端测试用例生成器

基于AI分析的测试要点，生成贴近真实移动端测试场景的测试用例。
专注于实用性和可执行性，避免冗余和模板化。
使用AI模型优化测试步骤和期望结果，提升用例质量。
"""

from typing import Dict, List, Tuple, Optional
from utils.models import TestCase, TestStep, TestCategory, Priority, TestPoint
from utils.log_manager import StructuredLogger
from core.ai_model_provider import AIModelFactory
import re
import random
import json


class TestCaseGenerator:
    """移动C端测试用例生成器 - 重构版"""
    
    def __init__(self, ai_provider=None):
        """初始化测试用例生成器"""
        self.case_counter = 0
        self.logger = StructuredLogger("TestCaseGenerator")
        
        # AI模型提供者
        self.ai_provider = ai_provider
        if not self.ai_provider:
            try:
                # 尝试从环境变量获取API密钥
                import os
                api_key = os.getenv("OPENAI_API_KEY")
                if api_key:
                    self.ai_provider = AIModelFactory.create_provider("openai", api_key)
                    self.logger.info("成功初始化AI提供者")
                else:
                    self.logger.info("未配置AI API密钥，将使用智能模板化生成")
                    self.ai_provider = None
            except Exception as e:
                self.logger.warning(f"无法初始化AI提供者: {e}")
                self.ai_provider = None
        
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
        # 优先使用AI生成具体的期望结果
        if self.ai_provider:
            ai_result = self._generate_ai_expected_result(scenario, action_type)
            if ai_result:
                return ai_result
        
        # 回退到模板化结果
        result_templates = {
            "点击": "界面响应及时，功能执行正确",
            "输入": "数据输入成功，格式验证正确",
            "滑动": "页面滑动流畅，内容加载正常",
            "查看": "信息显示完整，布局适配良好",
            "切换": "页面跳转成功，状态保持正确",
            "操作": "功能执行成功，用户体验良好"
        }
        
        return result_templates.get(action_type, "功能正常，符合预期")
    
    def _generate_ai_expected_result(self, scenario: str, action_type: str) -> Optional[str]:
        """使用AI生成具体的期望结果"""
        try:
            prompt = f"""作为移动端测试专家，请为以下测试场景生成具体、可验证的期望结果。

测试场景: {scenario}
操作类型: {action_type}

要求:
1. 期望结果要具体明确，可以验证
2. 包含用户界面、数据状态、交互反馈等方面
3. 避免模糊的描述，使用具体的验证点
4. 长度控制在30字以内
5. 体现移动端特色（如响应速度、界面适配等）

请直接返回期望结果描述，不需要其他格式："""

            response = self.ai_provider.chat(prompt)
            
            if response and response.strip():
                result = response.strip()
                # 长度控制
                if len(result) > 50:
                    result = result[:47] + "..."
                return result
                
        except Exception as e:
            self.logger.warning(f"AI期望结果生成失败: {e}")
        
        return None
    
    def _generate_realistic_steps(self, test_point: TestPoint, scenario_info: Dict) -> List[TestStep]:
        """生成贴近真实的测试步骤"""
        # 优先使用AI优化步骤
        if self.ai_provider:
            ai_steps = self._generate_ai_optimized_steps(test_point, scenario_info)
            if ai_steps:
                return ai_steps
        
        # 回退到模板化步骤
        return self._generate_template_steps(test_point, scenario_info)
    
    def _generate_ai_optimized_steps(self, test_point: TestPoint, scenario_info: Dict) -> Optional[List[TestStep]]:
        """使用AI生成优化的测试步骤"""
        try:
            prompt = self._build_step_optimization_prompt(test_point, scenario_info)
            response = self.ai_provider.chat(prompt)
            
            if response and response.strip():
                steps_data = self._parse_ai_steps_response(response)
                if steps_data:
                    return self._create_steps_from_ai_data(steps_data)
            
        except Exception as e:
            self.logger.warning(f"AI步骤生成失败: {e}")
        
        return None
    
    def _build_step_optimization_prompt(self, test_point: TestPoint, scenario_info: Dict) -> str:
        """构建AI步骤优化提示词"""
        # 根据场景复杂度动态确定步骤数量范围
        complexity = self._analyze_scenario_complexity(scenario_info['description'])
        step_range = self._get_step_range_by_complexity(complexity)
        
        return f"""作为移动端测试专家，请为以下测试场景生成具体、可执行的测试步骤。

测试要点: {test_point.description}
测试场景: {scenario_info['description']}
测试类别: {test_point.category.value}
优先级: {test_point.priority.value}
场景复杂度: {complexity}

要求:
1. 根据场景复杂度生成{step_range}个测试步骤
2. 每个步骤包含具体的操作和明确的期望结果
3. 步骤要贴近真实的移动端使用场景
4. 避免模板化语言，使用具体的操作描述
5. 期望结果要具体可验证
6. 步骤数量要合理，不要为了凑数而添加无意义的步骤

请按以下JSON格式返回:
{{
  "steps": [
    {{
      "action": "具体的操作步骤描述",
      "expected": "具体的期望结果"
    }}
  ]
}}

步骤数量指导:
- 简单场景(如单一操作): 1-3步
- 中等场景(如登录流程): 2-4步
- 复杂场景(如购物流程): 3-6步
- 复合场景(如多步骤验证): 4-8步

请根据实际测试需要生成合适数量的步骤:"""
    
    def _analyze_scenario_complexity(self, scenario: str) -> str:
        """分析场景复杂度"""
        # 计算复杂度指标
        action_count = len(re.findall(r'(输入|点击|选择|滑动|切换|查看|验证|确认|检查)', scenario))
        condition_count = len(re.findall(r'(如果|当|在.*情况下|需要|要求)', scenario))
        validation_count = len(re.findall(r'(验证|确认|检查|显示|提示)', scenario))
        
        # 场景长度
        scenario_length = len(scenario)
        
        # 复杂度评分
        complexity_score = (
            action_count * 2 +           # 动作数量权重最高
            condition_count * 1.5 +      # 条件判断
            validation_count * 1 +       # 验证点
            scenario_length / 20         # 场景长度
        )
        
        # 分类复杂度
        if complexity_score <= 4:
            return "简单"
        elif complexity_score <= 8:
            return "中等"
        elif complexity_score <= 12:
            return "复杂"
        else:
            return "复合"
    
    def _get_step_range_by_complexity(self, complexity: str) -> str:
        """根据复杂度获取步骤数量范围"""
        ranges = {
            "简单": "1-3",
            "中等": "2-4", 
            "复杂": "3-6",
            "复合": "4-8"
        }
        return ranges.get(complexity, "3-5")
    
    def _parse_ai_steps_response(self, response: str) -> Optional[List[Dict]]:
        """解析AI返回的步骤数据"""
        try:
            # 提取JSON内容
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if not json_match:
                return None
            
            json_str = json_match.group()
            data = json.loads(json_str)
            
            steps = data.get("steps", [])
            if not steps or not isinstance(steps, list):
                return None
            
            # 验证步骤格式
            valid_steps = []
            for step in steps:
                if isinstance(step, dict) and "action" in step and "expected" in step:
                    if step["action"].strip() and step["expected"].strip():
                        valid_steps.append(step)
            
            return valid_steps if valid_steps else None
            
        except Exception as e:
            self.logger.warning(f"解析AI步骤响应失败: {e}")
            return None
    
    def _create_steps_from_ai_data(self, steps_data: List[Dict]) -> List[TestStep]:
        """从AI数据创建测试步骤对象"""
        steps = []
        for i, step_data in enumerate(steps_data, 1):
            step = TestStep(
                step_no=i,
                action=step_data["action"].strip(),
                expected=step_data["expected"].strip()
            )
            steps.append(step)
        
        return steps
    
    def _generate_template_steps(self, test_point: TestPoint, scenario_info: Dict) -> List[TestStep]:
        """生成智能模板化的测试步骤（回退方案）"""
        steps = []
        scenario = scenario_info["description"]
        
        # 从场景中提取关键信息来生成更具体的步骤
        extracted_steps = self._extract_steps_from_scenario(scenario, test_point)
        
        if extracted_steps:
            return extracted_steps
        
        # 如果提取失败，使用基础模板
        return self._generate_basic_template_steps(test_point, scenario_info)
    
    def _extract_steps_from_scenario(self, scenario: str, test_point: TestPoint) -> Optional[List[TestStep]]:
        """从场景描述中智能提取测试步骤"""
        steps = []
        
        # 分析场景复杂度
        complexity = self._analyze_scenario_complexity(scenario)
        
        # 分析场景中的关键动作
        actions = self._identify_scenario_actions(scenario, complexity)
        
        if not actions:
            return None
        
        # 为每个动作生成步骤
        for i, action_info in enumerate(actions, 1):
            step = TestStep(
                step_no=i,
                action=action_info["action"],
                expected=action_info["expected"]
            )
            steps.append(step)
        
        # 根据复杂度确定最少步骤数
        min_steps = self._get_min_steps_by_complexity(complexity)
        
        return steps if len(steps) >= min_steps else None
    
    def _identify_scenario_actions(self, scenario: str, complexity: str = "中等") -> List[Dict]:
        """识别场景中的关键动作"""
        actions = []
        
        # 扩展的动作模式，支持更多场景
        action_patterns = [
            {
                "pattern": r"(打开|启动|进入).*?(应用|页面|界面|功能)",
                "action_template": "打开应用，进入{}",
                "expected": "页面加载完成，界面显示正常",
                "priority": 1
            },
            {
                "pattern": r"输入.*?(用户名|密码|手机号|邮箱|信息|内容|关键词)",
                "action_template": "在相应输入框中输入{}",
                "expected": "信息输入成功，格式验证通过",
                "priority": 2
            },
            {
                "pattern": r"点击.*?(按钮|链接|选项|图标|标签)",
                "action_template": "点击{}",
                "expected": "按钮响应，操作执行成功",
                "priority": 2
            },
            {
                "pattern": r"(选择|勾选).*?(选项|商品|服务|类别)",
                "action_template": "选择{}",
                "expected": "选择成功，状态更新正确",
                "priority": 2
            },
            {
                "pattern": r"(滑动|拖拽|滚动).*?(页面|列表|元素)",
                "action_template": "通过滑动操作{}",
                "expected": "滑动流畅，内容正常显示",
                "priority": 2
            },
            {
                "pattern": r"验证.*?(显示|跳转|提示|结果|状态)",
                "action_template": "验证{}",
                "expected": "验证结果符合预期",
                "priority": 3
            },
            {
                "pattern": r"(检查|确认|查看).*?(信息|内容|状态|结果)",
                "action_template": "检查{}",
                "expected": "信息显示正确，状态符合预期",
                "priority": 3
            },
            {
                "pattern": r"(等待|观察).*?(加载|响应|变化)",
                "action_template": "等待{}",
                "expected": "系统响应正常，状态更新及时",
                "priority": 2
            }
        ]
        
        # 提取动作
        for pattern_info in action_patterns:
            matches = re.findall(pattern_info["pattern"], scenario, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match = " ".join(match)
                
                action = pattern_info["action_template"].format(match)
                expected = pattern_info["expected"]
                
                actions.append({
                    "action": action,
                    "expected": expected,
                    "priority": pattern_info["priority"]
                })
        
        # 如果没有提取到足够的动作，添加通用步骤
        if len(actions) < 2:
            actions.extend(self._generate_fallback_actions(scenario))
        
        # 按优先级排序
        actions.sort(key=lambda x: x["priority"])
        
        # 去重和优化
        unique_actions = []
        seen_actions = set()
        
        for action_info in actions:
            action_key = action_info["action"][:25]  # 使用前25个字符作为去重键
            if action_key not in seen_actions:
                seen_actions.add(action_key)
                unique_actions.append(action_info)
        
        # 根据复杂度限制步骤数量
        max_steps = self._get_max_steps_by_complexity(complexity)
        return unique_actions[:max_steps]
    
    def _get_min_steps_by_complexity(self, complexity: str) -> int:
        """根据复杂度获取最少步骤数"""
        min_steps = {
            "简单": 2,
            "中等": 2,
            "复杂": 3,
            "复合": 4
        }
        return min_steps.get(complexity, 2)
    
    def _get_max_steps_by_complexity(self, complexity: str) -> int:
        """根据复杂度获取最多步骤数"""
        max_steps = {
            "简单": 3,
            "中等": 5,
            "复杂": 7,
            "复合": 10
        }
        return max_steps.get(complexity, 5)
    
    def _generate_fallback_actions(self, scenario: str) -> List[Dict]:
        """生成回退动作（当无法从场景中提取足够动作时）"""
        fallback_actions = []
        
        # 基础前置步骤
        if "登录" in scenario or "用户" in scenario:
            fallback_actions.append({
                "action": "打开应用，进入相关功能页面",
                "expected": "页面加载完成，界面显示正常",
                "priority": 1
            })
        
        # 核心操作步骤
        fallback_actions.append({
            "action": "执行场景中描述的核心操作",
            "expected": "操作执行成功，系统响应正常",
            "priority": 2
        })
        
        # 结果验证步骤
        if "验证" in scenario or "检查" in scenario or "确认" in scenario:
            fallback_actions.append({
                "action": "验证操作结果和系统状态",
                "expected": "结果符合预期，功能正常",
                "priority": 3
            })
        
        return fallback_actions
    
    def _generate_basic_template_steps(self, test_point: TestPoint, scenario_info: Dict) -> List[TestStep]:
        """生成基础模板步骤"""
        steps = []
        scenario = scenario_info["description"]
        action_type = scenario_info["action_type"]
        
        # 分析场景复杂度
        complexity = self._analyze_scenario_complexity(scenario)
        
        # 根据复杂度和场景内容动态生成步骤
        step_templates = self._build_step_templates(test_point, scenario_info, complexity)
        
        # 生成步骤
        for i, template in enumerate(step_templates, 1):
            step = TestStep(
                step_no=i,
                action=template["action"],
                expected=template["expected"]
            )
            steps.append(step)
        
        return steps
    
    def _build_step_templates(self, test_point: TestPoint, scenario_info: Dict, complexity: str) -> List[Dict]:
        """构建步骤模板"""
        templates = []
        scenario = scenario_info["description"]
        action_type = scenario_info["action_type"]
        
        # 1. 前置条件（根据需要添加）
        if self._needs_precondition_step(test_point, scenario):
            templates.append({
                "action": f"打开应用，进入{self._get_feature_context(test_point.description)}",
                "expected": "页面加载完成，界面显示正常"
            })
        
        # 2. 准备步骤（复杂场景需要）
        if complexity in ["复杂", "复合"] and self._needs_preparation_step(scenario):
            prep_action = self._generate_preparation_action(scenario)
            if prep_action:
                templates.append({
                    "action": prep_action,
                    "expected": "准备工作完成，环境设置正确"
                })
        
        # 3. 核心操作步骤
        core_actions = self._generate_core_action_steps(scenario, action_type, complexity)
        templates.extend(core_actions)
        
        # 4. 中间验证（复杂场景需要）
        if complexity in ["复合"] and len(templates) > 3:
            templates.append({
                "action": "检查中间状态和反馈信息",
                "expected": "中间状态正确，反馈信息明确"
            })
        
        # 5. 结果验证
        templates.append({
            "action": f"验证{self._extract_verification_point(scenario)}",
            "expected": scenario_info["expected_result"]
        })
        
        return templates
    
    def _needs_precondition_step(self, test_point: TestPoint, scenario: str) -> bool:
        """判断是否需要前置条件步骤"""
        precondition_keywords = ["登录", "权限", "设置", "配置", "打开", "进入"]
        return any(keyword in scenario for keyword in precondition_keywords)
    
    def _needs_preparation_step(self, scenario: str) -> bool:
        """判断是否需要准备步骤"""
        preparation_keywords = ["准备", "设置", "配置", "选择", "添加"]
        return any(keyword in scenario for keyword in preparation_keywords)
    
    def _generate_preparation_action(self, scenario: str) -> Optional[str]:
        """生成准备步骤的操作"""
        if "商品" in scenario:
            return "选择测试商品，准备测试数据"
        elif "用户" in scenario:
            return "准备测试用户账号和相关信息"
        elif "数据" in scenario:
            return "准备测试数据和环境配置"
        elif "网络" in scenario:
            return "设置网络环境（如弱网、断网等）"
        return None
    
    def _generate_core_action_steps(self, scenario: str, action_type: str, complexity: str) -> List[Dict]:
        """生成核心操作步骤"""
        core_steps = []
        
        # 根据复杂度决定核心步骤数量
        if complexity == "简单":
            # 简单场景：1个核心步骤
            core_steps.append({
                "action": self._generate_smart_core_action(scenario, action_type),
                "expected": self._generate_smart_action_expected(scenario, action_type)
            })
        elif complexity == "中等":
            # 中等场景：1-2个核心步骤
            core_steps.append({
                "action": self._generate_smart_core_action(scenario, action_type),
                "expected": self._generate_smart_action_expected(scenario, action_type)
            })
            
            # 如果场景包含多个动作，添加第二个步骤
            if len(re.findall(r'(然后|接着|再|继续)', scenario)) > 0:
                core_steps.append({
                    "action": "继续执行后续操作",
                    "expected": "后续操作执行成功"
                })
        else:
            # 复杂/复合场景：2-3个核心步骤
            actions = re.findall(r'(输入|点击|选择|滑动|切换|查看).*?[，。]', scenario)
            
            if len(actions) >= 2:
                for i, action in enumerate(actions[:3]):
                    core_steps.append({
                        "action": action.rstrip('，。'),
                        "expected": f"第{i+1}步操作执行成功"
                    })
            else:
                # 回退到基础步骤
                core_steps.append({
                    "action": self._generate_smart_core_action(scenario, action_type),
                    "expected": self._generate_smart_action_expected(scenario, action_type)
                })
                core_steps.append({
                    "action": "完成相关后续操作",
                    "expected": "所有操作执行完成"
                })
        
        return core_steps
    
    def _generate_smart_core_action(self, scenario: str, action_type: str) -> str:
        """生成智能的核心操作步骤"""
        # 从场景中提取关键操作词
        key_actions = re.findall(r'(输入|点击|选择|滑动|切换|查看|验证).*?[，。]', scenario)
        
        if key_actions:
            # 使用提取的操作
            return key_actions[0].rstrip('，。')
        
        # 回退到基础模板
        action_templates = {
            "点击": "点击相关按钮执行操作",
            "输入": "在输入框中输入相关信息",
            "滑动": "通过滑动手势进行操作",
            "查看": "查看页面显示的内容",
            "切换": "切换到目标状态或页面",
            "操作": "执行相关功能操作"
        }
        
        return action_templates.get(action_type, "执行相关功能操作")
    
    def _generate_smart_action_expected(self, scenario: str, action_type: str) -> str:
        """生成智能的操作期望结果"""
        # 从场景中提取期望关键词
        expected_keywords = re.findall(r'(成功|正确|显示|跳转|提示|验证)', scenario)
        
        if expected_keywords:
            return f"操作{expected_keywords[0]}，功能正常执行"
        
        # 回退到基础模板
        expected_templates = {
            "点击": "按钮响应及时，操作执行成功",
            "输入": "信息输入成功，格式验证通过",
            "滑动": "页面滑动流畅，内容正常显示",
            "查看": "信息显示完整，布局正确",
            "切换": "状态切换成功，界面更新正确",
            "操作": "功能执行成功，结果正确"
        }
        
        return expected_templates.get(action_type, "操作执行成功")
    
    def _extract_verification_point(self, scenario: str) -> str:
        """从场景中提取验证要点"""
        verification_patterns = [
            r'验证(.*?)(?:[，。]|$)',
            r'检查(.*?)(?:[，。]|$)',
            r'确认(.*?)(?:[，。]|$)'
        ]
        
        for pattern in verification_patterns:
            matches = re.findall(pattern, scenario)
            if matches:
                return matches[0].strip()
        
        return "功能执行结果"
    
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
        
        # 尝试使用AI生成兼容性测试步骤
        if self.ai_provider:
            ai_steps = self._generate_ai_compatibility_steps(test_point)
            if ai_steps:
                case.steps = ai_steps
            else:
                case.steps = self._get_default_compatibility_steps()
        else:
            case.steps = self._get_default_compatibility_steps()
        
        case.expected_result = "功能在各种设备上兼容性良好，用户体验一致"
        return case
    
    def _generate_ai_compatibility_steps(self, test_point: TestPoint) -> Optional[List[TestStep]]:
        """使用AI生成兼容性测试步骤"""
        try:
            # 分析功能复杂度来确定步骤数量
            complexity = self._analyze_scenario_complexity(test_point.description)
            step_range = self._get_step_range_by_complexity(complexity)
            
            prompt = f"""作为移动端测试专家，请为以下功能生成兼容性测试步骤。

功能描述: {test_point.description}
测试类别: {test_point.category.value}
功能复杂度: {complexity}

要求:
1. 根据功能复杂度生成{step_range}个兼容性测试步骤
2. 重点关注移动端设备差异（屏幕尺寸、系统版本、横竖屏等）
3. 每个步骤要具体可执行
4. 期望结果要明确可验证
5. 步骤数量要合理，避免为了凑数而添加无意义步骤

兼容性测试重点:
- 不同屏幕尺寸适配
- 横竖屏切换
- 不同系统版本
- 不同设备性能
- 网络环境差异

请按以下JSON格式返回:
{{
  "steps": [
    {{
      "action": "具体的兼容性测试操作",
      "expected": "具体的兼容性验证结果"
    }}
  ]
}}"""

            response = self.ai_provider.chat(prompt)
            steps_data = self._parse_ai_steps_response(response)
            
            if steps_data:
                return self._create_steps_from_ai_data(steps_data)
                
        except Exception as e:
            self.logger.warning(f"AI兼容性步骤生成失败: {e}")
        
        return None
    
    def _get_default_compatibility_steps(self) -> List[TestStep]:
        """获取默认的兼容性测试步骤"""
        return [
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
    
    def _create_usability_case(self, test_point: TestPoint) -> Optional[TestCase]:
        """创建易用性测试用例"""
        case = self._create_base_case(test_point, "易用性")
        case.title = f"{test_point.description} - 用户体验"
        case.description = "验证功能的易用性和用户体验"
        
        # 尝试使用AI生成易用性测试步骤
        if self.ai_provider:
            ai_steps = self._generate_ai_usability_steps(test_point)
            if ai_steps:
                case.steps = ai_steps
            else:
                case.steps = self._get_default_usability_steps()
        else:
            case.steps = self._get_default_usability_steps()
        
        case.expected_result = "功能易于理解和使用，用户体验良好"
        return case
    
    def _generate_ai_usability_steps(self, test_point: TestPoint) -> Optional[List[TestStep]]:
        """使用AI生成易用性测试步骤"""
        try:
            # 分析功能复杂度来确定步骤数量
            complexity = self._analyze_scenario_complexity(test_point.description)
            step_range = self._get_step_range_by_complexity(complexity)
            
            prompt = f"""作为移动端用户体验专家，请为以下功能生成易用性测试步骤。

功能描述: {test_point.description}
测试类别: {test_point.category.value}
功能复杂度: {complexity}

要求:
1. 根据功能复杂度生成{step_range}个易用性测试步骤
2. 重点关注用户体验（操作便捷性、界面友好性、错误处理等）
3. 从新用户角度考虑操作流程
4. 每个步骤要具体可执行
5. 步骤数量要合理，关注质量而非数量

易用性测试重点:
- 首次使用体验
- 操作流程直观性
- 错误提示友好性
- 界面元素可用性
- 交互反馈及时性

请按以下JSON格式返回:
{{
  "steps": [
    {{
      "action": "具体的易用性测试操作",
      "expected": "具体的用户体验验证结果"
    }}
  ]
}}"""

            response = self.ai_provider.chat(prompt)
            steps_data = self._parse_ai_steps_response(response)
            
            if steps_data:
                return self._create_steps_from_ai_data(steps_data)
                
        except Exception as e:
            self.logger.warning(f"AI易用性步骤生成失败: {e}")
        
        return None
    
    def _get_default_usability_steps(self) -> List[TestStep]:
        """获取默认的易用性测试步骤"""
        return [
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
            
            # 步骤数量合理性检查（动态范围）
            step_count = len(case.steps)
            if step_count < 2:
                self.logger.debug(f"移除步骤过少用例: {case.title} (步骤数: {step_count})")
                continue
            elif step_count > 10:
                self.logger.debug(f"移除步骤过多用例: {case.title} (步骤数: {step_count})")
                continue
            
            # 标题长度检查
            if len(case.title) > 60:
                self.logger.debug(f"移除标题过长用例: {case.title}")
                continue
            
            # 步骤内容质量检查
            if self._has_low_quality_steps(case.steps):
                self.logger.debug(f"移除低质量步骤用例: {case.title}")
                continue
            
            quality_cases.append(case)
        
        return quality_cases
    
    def _has_low_quality_steps(self, steps: List[TestStep]) -> bool:
        """检查是否包含低质量的步骤"""
        if not steps:
            return True
            
        low_quality_count = 0
        
        for step in steps:
            # 检查步骤是否过于简单
            if len(step.action) < 3 or len(step.expected) < 3:
                low_quality_count += 1
                continue
            
            # 检查是否包含过多完全模板化的语言
            highly_template_phrases = ["执行操作", "检查结果"]
            if any(phrase == step.action.strip() or phrase == step.expected.strip() for phrase in highly_template_phrases):
                low_quality_count += 1
        
        # 如果超过80%的步骤都是低质量的，才认为整体质量低
        return low_quality_count > len(steps) * 0.8
    
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
