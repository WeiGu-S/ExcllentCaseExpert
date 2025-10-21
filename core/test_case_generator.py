"""
移动C端测试用例生成器

基于AI分析的测试要点，生成贴近真实移动端测试场景的测试用例。
专注于实用性和可执行性，避免冗余和模板化。
使用AI模型优化测试步骤和期望结果，提升用例质量。
"""

from typing import Dict, List, Tuple, Optional
from utils.models import TestCase, TestStep, TestCategory, Priority, TestPoint
from utils.log_manager import StructuredLogger
from utils.config_manager import AppConfig
from core.ai_model_provider import AIModelFactory
import re
import random
import json


class TestCaseGenerator:
    """移动C端测试用例生成器 - 重构版"""
    
    def __init__(self, ai_provider=None, config: AppConfig = None):
        """初始化测试用例生成器"""
        self.case_counter = 0
        self.logger = StructuredLogger("TestCaseGenerator")
        
        # 加载配置
        if config is None:
            try:
                config = AppConfig.load_from_file()
                self.logger.info("成功加载配置文件")
            except Exception as e:
                self.logger.warning(f"加载配置文件失败，使用默认配置: {e}")
                config = AppConfig.create_default()
        
        self.config = config
        
        # AI调用控制
        self.ai_call_count = 0
        self.max_ai_calls = 10  # 允许适量的AI调用，平衡质量和性能
        
        # AI模型提供者
        self.ai_provider = ai_provider
        if not self.ai_provider:
            try:
                # 使用配置文件中的AI模型配置
                ai_config = self.config.ai_model
                
                # 检查API密钥是否有效
                if ai_config.api_key and ai_config.api_key != "your_api_key_here":
                    self.ai_provider = AIModelFactory.create_provider(
                        provider_name=ai_config.provider,
                        api_key=ai_config.api_key,
                        base_url=ai_config.base_url,
                        model_name=ai_config.model_name
                    )
                    # 保存配置参数供后续使用
                    self.ai_max_tokens = ai_config.max_tokens
                    self.ai_temperature = ai_config.temperature
                    self.logger.info(f"成功初始化AI提供者: {ai_config.provider} - {ai_config.model_name}")
                else:
                    self.logger.info("未配置有效的AI API密钥，将使用智能模板化生成")
                    self.ai_provider = None
                    self.ai_max_tokens = 2000
                    self.ai_temperature = 0.7
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
        
        # 重置计数器
        self.case_counter = 0
        self.ai_call_count = 0
        all_cases = []
        
        test_point_list = test_points.get("test_points", [])
        self.max_ai_calls = len(test_point_list) / 2  # 限制最大AI调用次数
        
        for test_point_dict in test_point_list:
            try:
                # 如果是字典，先检查类别是否支持
                if isinstance(test_point_dict, dict):
                    if not self._is_supported_category(test_point_dict.get("category")):
                        self.logger.info(f"跳过不支持的测试类别: {test_point_dict.get('category')} - {test_point_dict.get('description', 'N/A')}")
                        continue
                    test_point = TestPoint(**test_point_dict)
                else:
                    test_point = test_point_dict
                
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
            # 限制场景数量以减少AI调用次数
            max_scenarios = 2
            for i, scenario in enumerate(test_point.scenarios[:max_scenarios]):
                case = self._create_scenario_based_case(test_point, scenario, i + 1)
                if case:
                    cases.append(case)
        
        # 2. 根据测试类别和优先级补充关键用例（仅对P0优先级且AI调用次数未超限）
        if (test_point.priority == Priority.P0 and 
            self.ai_call_count < self.max_ai_calls):
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
        case.expected_result = self._generate_final_expected_result(test_point, scenario_info)
        
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
        # 只对重要场景使用AI生成具体的期望结果
        if (self.ai_provider and 
            self.ai_call_count < self.max_ai_calls and
            len(scenario) > 20):  # 只对较复杂的场景使用AI
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
        # 检查AI调用次数限制
        if self.ai_call_count >= self.max_ai_calls:
            self.logger.warning("已达到AI调用次数限制，跳过AI生成")
            return None
            
        try:
            self.ai_call_count += 1
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

            response = self.ai_provider.chat(
                prompt, 
                temperature=self.ai_temperature, 
                max_tokens=300  # 大幅限制token数量，加快响应
            )
            
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
        # 只对P0/P1优先级的测试要点使用AI优化
        if (self.ai_provider and 
            test_point.priority in [Priority.P0, Priority.P1] and
            self.ai_call_count < self.max_ai_calls):
            ai_steps = self._generate_ai_optimized_steps(test_point, scenario_info)
            if ai_steps:
                return ai_steps
        
        # 回退到模板化步骤
        return self._generate_template_steps(test_point, scenario_info)
    
    def _generate_ai_optimized_steps(self, test_point: TestPoint, scenario_info: Dict) -> Optional[List[TestStep]]:
        """使用AI生成优化的测试步骤"""
        # 检查AI调用次数限制
        if self.ai_call_count >= self.max_ai_calls:
            self.logger.warning("已达到AI调用次数限制，跳过AI步骤生成")
            return None
            
        try:
            self.ai_call_count += 1
            prompt = self._build_step_optimization_prompt(test_point, scenario_info)
            
            # 添加超时控制，减少max_tokens以加快响应
            response = self.ai_provider.chat(
                prompt, 
                temperature=self.ai_temperature, 
                max_tokens=800  # 限制token数量加快响应
            )
            
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
        # 使用更智能的场景解析
        parsed_scenario = self._parse_scenario_structure(scenario)
        
        if not parsed_scenario:
            return None
        
        steps = []
        step_no = 1
        seen_actions = set()
        
        # 合并所有步骤并去重
        all_actions = []
        if parsed_scenario.get("preconditions"):
            all_actions.extend(parsed_scenario["preconditions"])
        if parsed_scenario.get("main_actions"):
            all_actions.extend(parsed_scenario["main_actions"])
        if parsed_scenario.get("validations"):
            all_actions.extend(parsed_scenario["validations"])
        
        # 生成去重的步骤
        for action_info in all_actions:
            action_key = action_info["action"][:30]  # 使用前30个字符作为去重键
            if action_key not in seen_actions:
                seen_actions.add(action_key)
                step = TestStep(
                    step_no=step_no,
                    action=action_info["action"],
                    expected=action_info["expected"]
                )
                steps.append(step)
                step_no += 1
        
        return steps if len(steps) >= 2 else None
    
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
    
    def _parse_scenario_structure(self, scenario: str) -> Optional[Dict]:
        """解析场景结构，提取前置条件、主要操作和验证点"""
        if not scenario or len(scenario) < 10:
            return None
        
        parsed = {
            "preconditions": [],
            "main_actions": [],
            "validations": []
        }
        
        # 分句处理
        sentences = self._split_scenario_sentences(scenario)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # 分类句子类型
            sentence_type = self._classify_sentence_type(sentence)
            
            if sentence_type == "precondition":
                action_expected = self._extract_action_expected_from_sentence(sentence, "precondition")
                if action_expected:
                    parsed["preconditions"].append(action_expected)
            elif sentence_type == "main_action":
                action_expected = self._extract_action_expected_from_sentence(sentence, "main_action")
                if action_expected:
                    parsed["main_actions"].append(action_expected)
            elif sentence_type == "validation":
                action_expected = self._extract_action_expected_from_sentence(sentence, "validation")
                if action_expected:
                    parsed["validations"].append(action_expected)
        
        # 确保至少有主要操作
        if not parsed["main_actions"] and sentences:
            # 如果没有识别出主要操作，将第一个句子作为主要操作
            first_sentence = sentences[0].strip()
            action_expected = self._extract_action_expected_from_sentence(first_sentence, "main_action")
            if action_expected:
                parsed["main_actions"].append(action_expected)
        
        return parsed if any(parsed.values()) else None
    
    def _split_scenario_sentences(self, scenario: str) -> List[str]:
        """将场景分割成句子"""
        # 按常见分隔符分割
        import re
        sentences = re.split(r'[，。；,;]|，然后|，接着|，再|，最后|，验证', scenario)
        
        # 清理空句子
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return sentences
    
    def _classify_sentence_type(self, sentence: str) -> str:
        """分类句子类型"""
        # 前置条件关键词
        precondition_keywords = ["打开", "进入", "启动", "登录", "准备", "设置"]
        
        # 验证关键词
        validation_keywords = ["验证", "检查", "确认", "查看", "观察", "测试"]
        
        # 检查是否为前置条件
        if any(keyword in sentence[:10] for keyword in precondition_keywords):
            return "precondition"
        
        # 检查是否为验证步骤
        if any(keyword in sentence for keyword in validation_keywords):
            return "validation"
        
        # 默认为主要操作
        return "main_action"
    
    def _extract_action_expected_from_sentence(self, sentence: str, sentence_type: str) -> Optional[Dict]:
        """从句子中提取操作和期望结果"""
        if not sentence:
            return None
        
        # 根据句子类型生成不同的操作和期望
        if sentence_type == "precondition":
            return self._generate_precondition_step(sentence)
        elif sentence_type == "main_action":
            return self._generate_main_action_step(sentence)
        elif sentence_type == "validation":
            return self._generate_validation_step(sentence)
        
        return None
    
    def _generate_precondition_step(self, sentence: str) -> Dict:
        """生成前置条件步骤"""
        # 提取关键信息
        if "登录" in sentence:
            return {
                "action": "使用有效账号登录应用",
                "expected": "登录成功，进入主界面"
            }
        elif "打开" in sentence or "启动" in sentence:
            app_context = self._extract_app_context(sentence)
            return {
                "action": f"打开应用，进入{app_context}",
                "expected": "应用启动成功，页面加载完成"
            }
        elif "进入" in sentence:
            page_context = self._extract_page_context(sentence)
            return {
                "action": f"导航到{page_context}",
                "expected": "页面跳转成功，内容正常显示"
            }
        else:
            return {
                "action": sentence,
                "expected": "前置条件满足，环境准备就绪"
            }
    
    def _generate_main_action_step(self, sentence: str) -> Dict:
        """生成主要操作步骤"""
        # 根据操作类型生成具体的步骤
        if "输入" in sentence:
            input_content = self._extract_input_content(sentence)
            if "用户名" in sentence:
                return {
                    "action": f"在用户名输入框中输入有效的用户名",
                    "expected": "用户名输入成功，字段显示正常"
                }
            elif "密码" in sentence:
                return {
                    "action": f"在密码输入框中输入正确的密码",
                    "expected": "密码输入成功，显示为密文"
                }
            elif "关键词" in sentence or "搜索" in sentence:
                return {
                    "action": f"在搜索框中输入商品关键词",
                    "expected": "搜索词输入成功，搜索建议显示"
                }
            else:
                return {
                    "action": f"在相应字段输入{input_content}",
                    "expected": "输入内容正确显示，格式验证通过"
                }
        elif "点击" in sentence:
            click_target = self._extract_click_target(sentence)
            if "登录" in sentence:
                return {
                    "action": "点击登录按钮",
                    "expected": "登录请求发送，显示加载状态"
                }
            elif "搜索" in sentence:
                return {
                    "action": "点击搜索按钮或按回车键",
                    "expected": "搜索请求发送，开始加载结果"
                }
            elif "购物车" in sentence or "加入" in sentence:
                return {
                    "action": "点击加入购物车按钮",
                    "expected": "商品添加成功，购物车图标更新"
                }
            elif "结算" in sentence:
                return {
                    "action": "点击结算按钮",
                    "expected": "跳转到结算页面，商品信息显示"
                }
            elif "支付" in sentence:
                return {
                    "action": "点击支付按钮",
                    "expected": "跳转到支付页面，显示支付金额和支付方式选项"
                }
            elif "保存" in sentence:
                return {
                    "action": "点击保存按钮",
                    "expected": "数据保存成功，显示保存确认提示"
                }
            elif "确认" in sentence:
                return {
                    "action": "点击确认按钮",
                    "expected": "操作确认执行，相关状态更新"
                }
            elif "取消" in sentence:
                return {
                    "action": "点击取消按钮",
                    "expected": "操作取消，返回上一步状态"
                }
            else:
                return {
                    "action": f"点击{click_target}",
                    "expected": self._generate_context_specific_expected(sentence, "点击")
                }
        elif "选择" in sentence:
            if "商品" in sentence:
                return {
                    "action": "选择目标商品或商品规格",
                    "expected": "商品高亮显示，规格选项展开，价格信息更新"
                }
            elif "地址" in sentence:
                return {
                    "action": "选择收货地址",
                    "expected": "地址被标记为选中状态，配送费用和时间更新"
                }
            elif "支付方式" in sentence:
                return {
                    "action": "选择支付方式",
                    "expected": "支付方式图标高亮，相关支付信息显示"
                }
            elif "类别" in sentence or "分类" in sentence:
                return {
                    "action": "选择商品类别",
                    "expected": "类别被选中，相关商品筛选显示"
                }
            else:
                select_target = self._extract_select_target(sentence)
                return {
                    "action": f"选择{select_target}",
                    "expected": self._generate_context_specific_expected(sentence, "选择")
                }
        elif "浏览" in sentence:
            return {
                "action": "浏览页面内容和商品信息",
                "expected": "页面内容正常显示，图片加载完成"
            }
        elif "修改" in sentence or "编辑" in sentence:
            if "信息" in sentence:
                return {
                    "action": "修改个人信息字段",
                    "expected": "信息修改成功，字段内容更新"
                }
            else:
                return {
                    "action": "执行修改操作",
                    "expected": "修改内容保存，界面更新"
                }
        elif "保存" in sentence:
            return {
                "action": "点击保存按钮确认修改",
                "expected": "保存操作执行，显示保存状态"
            }
        elif "滑动" in sentence or "拖拽" in sentence:
            return {
                "action": "执行滑动或拖拽操作",
                "expected": "界面响应流畅，内容正常更新"
            }
        else:
            # 通用操作，尽量保持原句的具体性
            return {
                "action": sentence,
                "expected": "操作执行成功，功能正常响应"
            }
    
    def _generate_validation_step(self, sentence: str) -> Dict:
        """生成验证步骤"""
        # 更具体的验证步骤生成
        if "跳转" in sentence:
            if "主页" in sentence or "首页" in sentence:
                return {
                    "action": "检查页面跳转结果",
                    "expected": "成功跳转到主页，显示用户个人信息和主要功能入口"
                }
            elif "详情" in sentence:
                return {
                    "action": "检查页面跳转结果", 
                    "expected": "成功跳转到详情页，商品图片、价格、描述信息完整显示"
                }
            elif "结果" in sentence:
                return {
                    "action": "检查搜索结果页面",
                    "expected": "显示相关商品列表，包含商品图片、名称、价格等关键信息"
                }
            elif "订单" in sentence:
                return {
                    "action": "检查订单页面跳转",
                    "expected": "跳转到订单详情页，显示订单号、商品信息、支付状态"
                }
            else:
                target_page = self._extract_target_page(sentence)
                return {
                    "action": "检查页面跳转结果",
                    "expected": f"成功跳转到{target_page}，页面内容加载完整"
                }
        elif "显示" in sentence:
            if "商品" in sentence:
                return {
                    "action": "检查商品显示效果",
                    "expected": "商品列表正确显示，图片清晰，价格、评分等信息准确"
                }
            elif "错误" in sentence or "提示" in sentence:
                return {
                    "action": "检查错误提示信息",
                    "expected": "显示明确的错误提示，提示内容友好易懂"
                }
            elif "成功" in sentence:
                return {
                    "action": "检查成功提示信息",
                    "expected": "显示操作成功提示，界面状态正确更新"
                }
            else:
                display_content = self._extract_display_content(sentence)
                return {
                    "action": "检查界面显示内容",
                    "expected": f"正确显示{display_content}，布局整齐美观"
                }
        elif "添加" in sentence and "购物车" in sentence:
            return {
                "action": "验证商品添加到购物车",
                "expected": "购物车图标显示商品数量，商品信息正确保存"
            }
        elif "数量" in sentence:
            return {
                "action": "验证数量变化",
                "expected": "数量显示正确更新，相关价格计算准确"
            }
        elif "信息" in sentence and "更新" in sentence:
            return {
                "action": "验证信息更新结果",
                "expected": "个人信息成功更新，页面显示最新内容"
            }
        elif "支付" in sentence and "成功" in sentence:
            return {
                "action": "验证支付完成状态",
                "expected": "支付成功，生成订单号，发送确认短信或邮件"
            }
        elif "登录" in sentence and "成功" in sentence:
            return {
                "action": "验证登录状态",
                "expected": "用户头像和昵称显示，个人中心功能可正常访问"
            }
        else:
            # 从句子中提取具体的验证内容
            verification_content = self._extract_specific_verification(sentence)
            return {
                "action": f"验证{verification_content['action']}",
                "expected": verification_content['expected']
            }
    
    def _extract_app_context(self, sentence: str) -> str:
        """提取应用上下文"""
        contexts = ["主页", "首页", "登录页", "商品页", "购物车", "个人中心", "设置页"]
        for context in contexts:
            if context in sentence:
                return context
        return "相关页面"
    
    def _extract_page_context(self, sentence: str) -> str:
        """提取页面上下文"""
        if "详情" in sentence:
            return "详情页面"
        elif "列表" in sentence:
            return "列表页面"
        elif "设置" in sentence:
            return "设置页面"
        elif "个人" in sentence:
            return "个人中心"
        else:
            return "目标页面"
    
    def _extract_input_content(self, sentence: str) -> str:
        """提取输入内容"""
        if "用户名" in sentence:
            return "用户名"
        elif "密码" in sentence:
            return "密码"
        elif "手机号" in sentence:
            return "手机号码"
        elif "邮箱" in sentence:
            return "邮箱地址"
        elif "关键词" in sentence:
            return "搜索关键词"
        else:
            return "相关信息"
    
    def _extract_click_target(self, sentence: str) -> str:
        """提取点击目标"""
        if "登录" in sentence:
            return "登录按钮"
        elif "搜索" in sentence:
            return "搜索按钮"
        elif "提交" in sentence:
            return "提交按钮"
        elif "确认" in sentence:
            return "确认按钮"
        elif "按钮" in sentence:
            return "相关按钮"
        else:
            return "目标元素"
    
    def _extract_select_target(self, sentence: str) -> str:
        """提取选择目标"""
        if "商品" in sentence:
            return "目标商品"
        elif "选项" in sentence:
            return "相关选项"
        elif "类别" in sentence:
            return "商品类别"
        else:
            return "目标项目"
    
    def _extract_target_page(self, sentence: str) -> str:
        """提取目标页面"""
        if "主页" in sentence or "首页" in sentence:
            return "主页面"
        elif "详情" in sentence:
            return "详情页面"
        elif "结果" in sentence:
            return "结果页面"
        else:
            return "目标页面"
    
    def _extract_display_content(self, sentence: str) -> str:
        """提取显示内容"""
        if "错误" in sentence:
            return "错误提示信息"
        elif "成功" in sentence:
            return "成功提示信息"
        elif "结果" in sentence:
            return "操作结果"
        else:
            return "相关内容"
    
    def _extract_specific_verification(self, sentence: str) -> Dict:
        """提取具体的验证内容"""
        # 根据句子内容生成具体的验证动作和期望
        if "功能" in sentence:
            return {
                "action": "功能可用性",
                "expected": "功能正常运行，响应及时，无异常错误"
            }
        elif "界面" in sentence:
            return {
                "action": "界面显示效果",
                "expected": "界面布局合理，元素对齐，色彩搭配协调"
            }
        elif "数据" in sentence:
            return {
                "action": "数据准确性",
                "expected": "数据内容准确，格式正确，实时同步"
            }
        elif "状态" in sentence:
            return {
                "action": "系统状态",
                "expected": "状态显示正确，状态变化及时反馈"
            }
        elif "流程" in sentence:
            return {
                "action": "业务流程",
                "expected": "流程执行顺畅，各环节衔接正常"
            }
        else:
            # 提取句子中的关键词作为验证点
            key_words = self._extract_key_words(sentence)
            return {
                "action": f"{key_words}的正确性",
                "expected": f"{key_words}符合预期要求，无异常情况"
            }
    
    def _extract_key_words(self, sentence: str) -> str:
        """从句子中提取关键词"""
        # 移除常见的动词和助词
        import re
        cleaned = re.sub(r'(验证|检查|确认|测试|是否|能够|正确|成功)', '', sentence)
        cleaned = cleaned.strip()
        
        # 如果清理后为空，返回默认值
        if not cleaned:
            return "操作结果"
        
        # 限制长度
        if len(cleaned) > 10:
            cleaned = cleaned[:8] + "..."
        
        return cleaned
    
    def _generate_context_specific_expected(self, sentence: str, action_type: str) -> str:
        """根据上下文生成具体的期望结果"""
        # 根据句子中的业务上下文生成期望结果
        if "登录" in sentence:
            if action_type == "点击":
                return "登录验证开始，显示加载动画，验证用户凭据"
            elif action_type == "选择":
                return "登录选项被选中，相关登录方式激活"
        elif "搜索" in sentence:
            if action_type == "点击":
                return "搜索执行，显示搜索进度，准备展示结果"
            elif action_type == "选择":
                return "搜索条件被应用，筛选范围更新"
        elif "购物车" in sentence:
            if action_type == "点击":
                return "商品添加到购物车，购物车数量增加，显示添加成功动画"
            elif action_type == "选择":
                return "购物车商品被选中，可进行批量操作"
        elif "支付" in sentence:
            if action_type == "点击":
                return "支付流程启动，验证支付环境，显示支付选项"
            elif action_type == "选择":
                return "支付选项确认，显示支付详情和安全提示"
        elif "个人" in sentence or "用户" in sentence:
            if action_type == "点击":
                return "个人信息页面打开，显示用户详细资料"
            elif action_type == "选择":
                return "个人设置选项被选中，相关配置显示"
        elif "商品" in sentence:
            if action_type == "点击":
                return "商品详情展开，显示商品图片、价格、评价等信息"
            elif action_type == "选择":
                return "商品被加入选择列表，可进行对比或批量操作"
        else:
            # 通用的上下文相关期望
            context_expectations = {
                "点击": "界面响应迅速，相关功能模块激活，用户反馈明确",
                "选择": "选项状态更新，相关信息联动显示，操作反馈及时",
                "输入": "输入内容实时验证，格式提示友好，错误处理得当",
                "滑动": "页面滑动流畅，内容加载及时，交互体验良好"
            }
            return context_expectations.get(action_type, "操作执行成功，系统响应正常")
    
    def _generate_final_expected_result(self, test_point: TestPoint, scenario_info: Dict) -> str:
        """生成最终的期望结果"""
        scenario = scenario_info["description"]
        
        # 根据测试要点和场景生成具体的最终期望结果
        if "登录" in test_point.description:
            if "成功" in scenario:
                return "用户成功登录系统，个人信息正确显示，可正常访问各功能模块"
            elif "错误" in scenario:
                return "系统正确识别错误信息，显示友好的错误提示，引导用户重新输入"
            else:
                return "登录流程完整执行，用户身份验证准确，系统安全性得到保障"
        
        elif "搜索" in test_point.description:
            return "搜索功能正常运行，结果准确相关，用户能够快速找到目标商品"
        
        elif "购物车" in test_point.description:
            return "购物车功能完整可用，商品信息准确保存，数量和价格计算正确"
        
        elif "支付" in test_point.description:
            return "支付流程安全可靠，订单生成成功，用户收到确认通知"
        
        elif "个人" in test_point.description or "信息" in test_point.description:
            return "个人信息管理功能正常，数据更新及时，隐私保护到位"
        
        elif test_point.category == TestCategory.COMPATIBILITY:
            return "功能在不同设备和环境下表现一致，兼容性良好，用户体验统一"
        
        elif test_point.category == TestCategory.USABILITY:
            return "界面操作直观易懂，用户体验流畅，功能易于发现和使用"
        
        else:
            # 根据场景内容生成通用的最终期望
            if "验证" in scenario and "成功" in scenario:
                return "功能验证通过，操作结果符合预期，系统运行稳定可靠"
            elif "显示" in scenario:
                return "信息显示准确完整，界面布局合理，用户获得良好的视觉体验"
            elif "跳转" in scenario:
                return "页面跳转流畅自然，内容加载及时，导航逻辑清晰明确"
            else:
                return "功能执行完整准确，用户操作得到及时反馈，整体体验良好"
    
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
        # 检查AI调用次数限制
        if self.ai_call_count >= self.max_ai_calls:
            self.logger.warning("已达到AI调用次数限制，跳过兼容性步骤生成")
            return None
            
        try:
            self.ai_call_count += 1
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

            response = self.ai_provider.chat(
                prompt, 
                temperature=self.ai_temperature, 
                max_tokens=600  # 限制兼容性测试的token数量
            )
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
        # 检查AI调用次数限制
        if self.ai_call_count >= self.max_ai_calls:
            self.logger.warning("已达到AI调用次数限制，跳过易用性步骤生成")
            return None
            
        try:
            self.ai_call_count += 1
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

            response = self.ai_provider.chat(
                prompt, 
                temperature=self.ai_temperature, 
                max_tokens=600  # 限制易用性测试的token数量
            )
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
    
    def _is_supported_category(self, category: str) -> bool:
        """检查测试类别是否被支持"""
        if not category:
            return False
            
        # 支持的测试类别
        supported_categories = {
            "功能测试",
            "兼容性测试", 
            "易用性测试"
        }
        
        return category in supported_categories
