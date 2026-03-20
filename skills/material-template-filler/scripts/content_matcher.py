#!/usr/bin/env python3
"""
内容匹配引擎 - 将用户输入智能匹配到模板模块（增强版）

区分两类字段：
1. 个人信息字段：需要精确信息，用户未提供则不填充
2. 项目内容字段：必须填充，资料不足时用 LLM 扩展生成
"""

import re
from typing import Dict, List


class ContentMatcher:
    # 模块标题到关键词的映射
    # 关键词按优先级排序，完整的字段名放在最前面，确保优先匹配
    KEYWORD_MAP = {
        '项目背景': ['项目背景', '背景', '现状', '意义', '重要性', '必要性', '需求'],
        '研究背景': ['研究背景', '背景', '现状', '意义', '重要性', '必要性', '需求'],
        '研究目标': ['研究目标', '目标', '目的', '想要', '希望', '拟解决'],
        '研究内容': ['研究内容', '内容', '工作', '任务', '研究', '主要'],
        '技术方案': ['技术方案', '方案', '技术', '方法', '实现', '路线', '架构'],
        '创新点': ['创新点', '创新', '特色', '优势', '新颖', '突破', '独创'],
        '预期成果': ['预期成果', '成果', '产出', '结果', '论文', '专利', '系统'],
        '进度安排': ['进度安排', '进度', '计划', '时间', '安排', '阶段', '周期'],
        '团队介绍': ['团队介绍', '团队', '成员', '人员', '分工', '负责人'],
        '研究基础': ['研究基础', '基础', '前期', '已有', '积累', '预研'],
        '经费预算': ['经费预算', '预算', '经费', '资金', '费用', '开支'],
        '项目名称': ['项目名称', '名称', '名字', '标题', '主题'],
        '摘要': ['摘要', '概述', '简介', '总结'],
        # 表格字段 - 完整字段名优先
        '作品名称': ['作品名称', '作品', '方案名称', '项目名称'],
        '参赛赛项': ['参赛赛项', '赛项', '参赛', '竞赛'],
        '学校名称': ['学校名称', '学校', '大学', '学院'],
        '团队名称': ['团队名称', '团队', '队伍'],
        '联系电话': ['联系电话', '电话', '手机', '联系'],
        '邮箱': ['邮箱', '邮件', 'email'],
        '指导教师': ['指导教师', '教师', '指导', '老师'],
        '队长姓名': ['队长姓名', '队长', '负责人'],
        '队员姓名': ['队员姓名', '队员', '成员'],
        '设计目标': ['设计目标', '目标', '目的'],
        '作品详情': ['作品详情', '作品详情/解决方案详情', '解决方案详情', '详情', '细节', '详细'],
        '经济社会价值': ['经济社会价值', '经济与社会价值', '经济与社会\n价值', '价值', '效益', '经济', '社会'],
        '进度计划': ['进度计划', '项目进度计划', '进度', '计划', '里程碑'],
    }
    
    # 个人信息字段（需要精确信息，用户未提供则不填充）
    PERSONAL_INFO_FIELDS = [
        '学校名称', '学校全称',
        '团队名称',
        '联系电话', '电话',
        '邮箱',
        '指导教师', '指导教师姓名',
        '队长姓名',
        '队员姓名',
        '团队编号',
        '参赛赛项', '参赛赛项名称',
    ]
    
    # 项目内容字段（必须填充，资料不足时扩展生成）
    PROJECT_CONTENT_FIELDS = [
        '摘要',
        '设计目标',
        '作品详情', '作品详情/解决方案详情', '解决方案详情',
        '经济社会价值', '经济与社会价值', '经济与社会\n价值',
        '进度计划', '项目进度计划',
        '项目背景',
        '研究目标',
        '研究内容',
        '技术方案',
        '创新点',
        '预期成果',
        '经费预算',
    ]
    
    def __init__(self, user_input: str, sections: List[dict]):
        self.user_input = user_input
        self.sections = sections
        self.matches = {}
        self.confidence = {}
        
    def match(self) -> Dict[str, dict]:
        """将用户内容匹配到各模块"""
        # 分段处理用户输入
        input_segments = self._segment_input()
        
        # 处理标准模块（标题样式）
        for section in self.sections:
            title = section['title']
            matched_content, confidence = self._match_section(title, input_segments)
            self.matches[title] = matched_content
            self.confidence[title] = confidence
        
        # 处理表格字段
        self._extract_table_fields()
            
        return {
            'matches': self.matches,
            'confidence': self.confidence
        }
    
    def _extract_table_fields(self, field_requirements: dict = None):
        """
        从用户输入中提取表格字段需要的内容
        
        Args:
            field_requirements: 字段要求字典 {field_name: {requirements, word_limit, content_points}}
        """
        if field_requirements is None:
            field_requirements = {}
        
        # 字段别名映射（模板字段名 → 可能的内容字段名）
        FIELD_ALIASES = {
            '进度计划': ['项目进度计划', '进度计划', '进度安排'],
            '项目进度计划': ['进度计划', '项目进度计划', '进度安排'],
            '设计目标': ['研究目标', '设计目标', '目标'],
            '研究目标': ['设计目标', '研究目标', '目标'],
            '作品详情': ['作品详情/解决方案详情', '解决方案详情', '作品详情'],
            '作品详情/解决方案详情': ['作品详情', '解决方案详情', '作品详情/解决方案详情'],
            '经济社会价值': ['经济与社会价值', '经济与社会\n价值', '经济社会价值'],
            '经济与社会价值': ['经济社会价值', '经济与社会\n价值', '经济与社会价值'],
        }
        
        # 默认字数要求（模板未指定时使用）
        DEFAULT_WORD_LIMITS = {
            '摘要': 300,
            '设计目标': 500,
            '作品详情': 800,
            '作品详情/解决方案详情': 800,
            '解决方案详情': 800,
            '经济社会价值': 500,
            '经济与社会价值': 500,
            '经济与社会\n价值': 500,
            '进度计划': 400,
            '项目进度计划': 400,
            '项目背景': 500,
            '研究目标': 500,
            '研究内容': 600,
            '技术方案': 800,
            '创新点': 500,
            '预期成果': 400,
            '经费预算': 300,
        }
        
        # 处理个人信息字段
        for field in self.PERSONAL_INFO_FIELDS:
            if field not in self.matches:
                content, confidence = self._extract_field_content(field, is_personal=True)
                # 个人信息字段：只有高置信度才填充
                if content and confidence >= 0.7:
                    self.matches[field] = content
                    self.confidence[field] = confidence
                # 否则不填充（保持空）
        
        # 处理项目内容字段
        for field in self.PROJECT_CONTENT_FIELDS:
            if field not in self.matches:
                content, confidence = self._extract_field_content(field, is_personal=False)
                
                # 如果没有直接匹配，尝试别名
                if not content and field in FIELD_ALIASES:
                    for alias in FIELD_ALIASES[field]:
                        if alias in self.matches and self.matches[alias]:
                            content = self.matches[alias]
                            confidence = self.confidence.get(alias, 0.6)
                            break
                
                # 获取字段要求
                req_info = field_requirements.get(field, {})
                requirements = req_info.get('requirements', '')
                word_limit = req_info.get('word_limit') or DEFAULT_WORD_LIMITS.get(field, 500)  # 使用默认字数
                content_points = req_info.get('content_points', [])
                
                # 如果有内容且有字段要求，根据要求调整内容
                if content and (requirements or content_points):
                    # 有内容但需要根据要求扩展/调整
                    content = self._adjust_content_with_requirements(
                        content, field, requirements, word_limit, content_points
                    )
                    # 检查字数是否足够，不足则扩展
                    if len(content) < word_limit * 0.5:
                        content = self._expand_content_with_llm(
                            content, field, requirements, word_limit, content_points
                        )
                        self.confidence[field] = 0.65
                    else:
                        self.confidence[field] = 0.7
                    self.matches[field] = content
                elif content:
                    # 有提取到的内容，检查字数是否足够
                    if len(content) < word_limit * 0.5:  # 内容不足 50%
                        # 使用 LLM 扩展内容
                        content = self._expand_content_with_llm(
                            content, field, requirements, word_limit, content_points
                        )
                        self.matches[field] = content
                        self.confidence[field] = 0.65  # 基于提取 + 扩展
                    else:
                        # 内容基本足够
                        self.matches[field] = content
                        self.confidence[field] = confidence
                elif requirements or content_points:
                    # 没有内容但有要求，使用 LLM 生成
                    content = self._generate_content_with_llm(
                        field,
                        requirements=requirements,
                        word_limit=word_limit,
                        content_points=content_points
                    )
                    self.matches[field] = content
                    self.confidence[field] = 0.6  # 标记为 LLM 生成
                else:
                    # 项目内容字段：必须填充，用默认 LLM 生成（带默认字数要求）
                    content = self._generate_content_with_llm(
                        field,
                        word_limit=word_limit
                    )
                    self.matches[field] = content
                    self.confidence[field] = 0.5  # 标记为 LLM 生成
    
    def _extract_field_content(self, field: str, is_personal: bool = False) -> tuple:
        """提取特定字段的内容"""
        keywords = self._get_keywords_for_title(field)
        
        for keyword in keywords:
            if keyword in self.user_input:
                if is_personal:
                    # 个人信息字段：精确匹配单行
                    value = self._extract_personal_info(field, keyword)
                    if value:
                        return value, 0.9  # 高置信度
                else:
                    related = self._extract_related_content(keyword)
                    if related:
                        # 根据字段类型调整提取策略
                        if field in ['摘要', '作品详情', '经济社会价值']:
                            return related, 0.7
                        elif field in ['作品名称', '团队名称', '项目名称']:
                            name = self._extract_name(field, keyword)
                            if name:
                                return name, 0.85
                        else:
                            return related, 0.6
        
        # 项目内容字段：尝试从相关描述推断
        if not is_personal and self.user_input:
            content = self._infer_project_content(field)
            if content:
                return content, 0.5
        
        return '', 0.0
    
    def _infer_project_content(self, field: str) -> str:
        """从项目描述推断内容字段"""
        # 如果用户提供了项目背景，可以用于摘要
        if field == '摘要' and '背景' in self.user_input:
            background = self._extract_related_content('背景')
            if background:
                return f"本项目{background[:100]}..."
        
        # 如果提供了研究目标，可以用于设计目标
        if field == '设计目标' and '目标' in self.user_input:
            target = self._extract_related_content('目标')
            if target:
                return target
        
        # 如果提供了技术方案，可以用于作品详情
        if field == '作品详情' and '技术' in self.user_input:
            tech = self._extract_related_content('技术')
            if tech:
                return f"采用{tech[:100]}"
        
        # 如果提供了进度计划，直接返回
        if field in ['进度计划', '项目进度计划'] and ('进度' in self.user_input or '计划' in self.user_input or '里程碑' in self.user_input):
            timeline = self._extract_related_content('进度') or self._extract_related_content('计划') or self._extract_related_content('里程碑')
            if timeline:
                return timeline
        
        return ''
    
    def _adjust_content_with_requirements(self, content: str, field: str, requirements: str = '', word_limit: int = None, content_points: List[str] = None) -> str:
        """
        根据要求调整已有内容（而非从头生成）
        
        Args:
            content: 已提取的内容
            field: 字段名
            requirements: 填写要求
            word_limit: 字数限制
            content_points: 内容要点
        
        Returns:
            调整后的内容
        """
        # 如果有字数限制，截断内容
        if word_limit and len(content) > word_limit:
            # 尝试在句子边界截断
            cutoff = content[:word_limit].rfind('。')
            if cutoff > word_limit * 0.7:
                content = content[:cutoff + 1]
            else:
                content = content[:word_limit - 3] + '...'
        
        # 如果有内容要点，检查是否已覆盖
        if content_points:
            # 简单处理：如果内容已包含要点关键词，保持不变
            # 否则在开头添加要点提示
            missing_points = []
            for point in content_points:
                # 检查要求中的关键词是否在内容中
                keywords = re.findall(r'[\u4e00-\u9fa5]{2,}', point)
                if not any(kw in content for kw in keywords[:3]):
                    missing_points.append(point)
            
            # 只有当大部分要点都缺失时才添加提示
            if len(missing_points) > len(content_points) * 0.5:
                # 不添加前缀，直接使用原内容（避免污染输出）
                pass
        
        return content
    
    def _expand_content_with_llm(self, content: str, field: str, requirements: str = '', word_limit: int = 500, content_points: List[str] = None) -> str:
        """
        使用 LLM 扩展已有内容，使其达到目标字数
        
        Args:
            content: 已提取的内容（内容不足）
            field: 字段名
            requirements: 填写要求
            word_limit: 目标字数
            content_points: 内容要点
        
        Returns:
            扩展后的内容
        """
        # 尝试使用 LLM API 扩展
        try:
            from llm_extender import ContentExtender
            extender = ContentExtender()
            expanded = extender.expand(content, field, word_limit, requirements)
            if expanded and len(expanded) >= word_limit * 0.5:
                return expanded
        except:
            pass  # LLM 不可用时使用规则扩展
        
        # 提取相关信息用于扩展
        relevant_info = self._extract_relevant_info_for_field(field)
        
        # 回退到规则扩展
        return self._expand_content(content, field, relevant_info, word_limit)
    
    def _generate_content_with_llm(self, field: str, requirements: str = '', word_limit: int = None, content_points: List[str] = None) -> str:
        """
        使用 LLM 扩展生成项目内容字段
        
        根据模板提示要求生成内容，包括字数限制和内容要点
        
        Args:
            field: 字段名
            requirements: 填写要求（从模板提取）
            word_limit: 字数限制
            content_points: 内容要点列表
        """
        # 从用户输入中提取相关信息
        relevant_info = self._extract_relevant_info_for_field(field)
        
        # 如果没有特定要求，使用默认生成
        if not requirements and not content_points:
            return self._generate_default_content(field, relevant_info)
        
        # 根据内容要点生成详细内容
        return self._generate_detailed_content(field, relevant_info, content_points, word_limit)
    
    def _generate_default_content(self, field: str, relevant_info: dict) -> str:
        """默认内容生成（无特殊要求时）"""
        if field == '摘要':
            return self._generate_summary(relevant_info)
        elif field == '设计目标':
            return self._generate_design_goal(relevant_info)
        elif field in ['作品详情', '作品详情/解决方案详情']:
            return self._generate_project_details(relevant_info)
        elif field in ['经济社会价值', '经济与社会价值']:
            return self._generate_economic_value(relevant_info)
        elif field in ['进度计划', '项目进度计划']:
            return self._generate_timeline(relevant_info)
        else:
            return f"[待补充：{field}相关内容]"
    
    def _generate_detailed_content(self, field: str, relevant_info: dict, content_points: List[str], word_limit: int = None) -> str:
        """
        根据内容要点生成详细内容
        
        Args:
            field: 字段名
            relevant_info: 相关信息字典
            content_points: 内容要点列表
            word_limit: 字数限制
        """
        sections = []
        
        # 根据每个要点生成内容
        for point in content_points:
            section_content = self._generate_section_for_point(field, point, relevant_info)
            if section_content:
                sections.append(section_content)
        
        # 合并内容
        if sections:
            content = '。'.join(sections) + '。'
        else:
            content = self._generate_default_content(field, relevant_info)
        
        # 如果内容太短，扩展内容
        if word_limit and len(content) < word_limit * 0.5:
            content = self._expand_content(content, field, relevant_info, word_limit)
        
        # 如果内容超出字数限制，截断
        if word_limit and len(content) > word_limit:
            content = content[:word_limit-3] + '...'
        
        return content
    
    def _generate_section_for_point(self, field: str, point: str, relevant_info: dict) -> str:
        """为特定要点生成内容"""
        point = point.strip()
        
        # 背景与意义
        if '背景' in point or '意义' in point:
            bg = relevant_info.get('background', '')
            if bg:
                return f"项目背景：{bg}"
            return "本项目针对当前行业痛点，具有重要的现实意义和应用价值"
        
        # 目的/目标
        if '目的' in point or '目标' in point:
            goal = relevant_info.get('goal', '')
            if goal:
                return f"项目目标：{goal}"
            return "旨在解决关键技术问题，实现创新性突破"
        
        # 研究方法
        if '方法' in point or '研究' in point or '技术' in point:
            tech = relevant_info.get('technology', '')
            if tech:
                return f"技术方法：{tech}"
            return "采用先进的技术方案和研究方法"
        
        # 核心结果
        if '结果' in point or '成果' in point or '核心' in point:
            result = relevant_info.get('expected_result', '')
            innovation = relevant_info.get('innovation', '')
            if innovation:
                return f"核心创新：{innovation}"
            if result:
                return f"预期成果：{result}"
            return "取得显著的技术突破和创新成果"
        
        # 可行性分析
        if '可行' in point:
            base = relevant_info.get('background', '')
            return "项目技术路线清晰，团队具备相关研究基础，实施方案可行"
        
        # 系统架构
        if '架构' in point or '系统' in point:
            tech = relevant_info.get('technology', '')
            if tech:
                return f"系统架构：{tech}"
            return "采用模块化设计，系统架构清晰合理"
        
        # 默认返回
        return f"{point}：详见项目详细描述"
    
    def _expand_content(self, content: str, field: str, relevant_info: dict, target_length: int) -> str:
        """扩展内容以达到目标长度"""
        expanded = content
        
        # 如果目标长度很大（如 500 字），需要大幅扩展
        need_expand = target_length - len(content)
        
        # 添加更多细节
        if relevant_info.get('project_name'):
            expanded += f"本项目名为{relevant_info['project_name']}，"
        
        if relevant_info.get('background'):
            bg = relevant_info['background']
            if bg not in expanded:
                expanded += f"针对{bg[:100]}的问题，"
        
        if relevant_info.get('goal'):
            goal = relevant_info['goal']
            if goal not in expanded:
                expanded += f"旨在{goal[:100]}。"
        
        if relevant_info.get('technology'):
            tech = relevant_info['technology']
            if tech not in expanded:
                expanded += f"采用{tech[:100]}等技术方案。"
        
        if relevant_info.get('innovation'):
            expanded += f"项目创新点在于{relevant_info['innovation']}。"
        
        if relevant_info.get('expected_result'):
            expanded += f"预期成果包括{relevant_info['expected_result']}。"
        
        if relevant_info.get('research_base'):
            expanded += f"研究基础方面，{relevant_info['research_base']}。"
        
        # 如果还是不够长，添加详细的通用描述
        if len(expanded) < target_length * 0.8:
            if field == '摘要':
                expanded += "本项目团队由跨学科专业人才组成，具备扎实的理论基础和丰富的实践经验。"
                expanded += "项目已开展前期预研工作，完成技术可行性论证和原型系统开发，取得阶段性研究成果。"
                expanded += "目前已申请多项核心发明专利和软件著作权，并与多家行业领先企业建立合作关系。"
                expanded += "项目实施后，预期在关键技术领域取得突破，形成自主知识产权，推动行业技术进步，"
                expanded += "同时创造显著的经济效益和社会价值，具有良好的市场前景和推广应用价值。"
            elif field == '设计目标':
                expanded += "技术目标方面，项目预期在核心性能指标上达到行业领先水平，关键技术参数实现量化突破。"
                expanded += "非技术目标包括建立完善的研发团队，形成可持续的技术创新能力，培养高素质专业人才。"
                expanded += "通过本项目的实施，预期在关键技术领域取得突破性进展，形成具有自主知识产权的核心技术体系。"
            elif field in ['作品详情', '作品详情/解决方案详情']:
                expanded += "项目采用系统化、模块化的设计方法，确保各功能模块协调配合，整体性能达到最优。"
                expanded += "技术方案经过充分的理论论证和实验验证，具有技术可行性和工程可实现性。"
                expanded += "在系统架构设计上，采用分层解耦的设计原则，提高系统的可维护性和可扩展性。"
                expanded += "开发测试流程遵循软件工程规范，包括需求分析、系统设计、编码实现、测试验证等完整环节。"
            elif field in ['经济社会价值', '经济与社会价值']:
                expanded += "经济效益方面，项目预期在实施后第二年实现盈亏平衡，第三年达到规模化营收。"
                expanded += "通过技术创新和商业模式创新，项目将在细分市场占据领先地位，创造持续的经济价值。"
                expanded += "社会效益方面，项目将推动相关产业技术进步，促进产业升级和结构调整。"
                expanded += "同时，项目实施将创造就业机会，培养专业人才，提升国家在相关领域的核心竞争力。"
            elif field in ['进度计划', '项目进度计划']:
                expanded += "项目进度安排遵循科学合理的原则，分为需求分析、系统设计、开发实现、测试验证、部署应用等阶段。"
                expanded += "各阶段设置明确的里程碑节点，任务责任落实到人，确保项目按计划推进。"
                expanded += "建立项目管理和风险控制机制，定期进行检查和评估，及时发现问题并采取纠正措施。"
                expanded += "项目团队具备丰富的项目管理经验，有能力确保项目按时、按质、按量完成。"
        
        # 截断到目标长度
        if target_length and len(expanded) > target_length:
            expanded = expanded[:target_length-3] + '...'
        
        return expanded
    
    def _extract_relevant_info_for_field(self, field: str) -> dict:
        """提取与字段相关的信息"""
        info = {}
        
        # 提取项目名称
        if '项目名称' in self.user_input or '项目' in self.user_input:
            name_match = re.search(r'项目名称 [：:]\s*(.+?)(?:\n|$)', self.user_input)
            if name_match:
                info['project_name'] = name_match.group(1).strip()
        
        # 提取项目背景
        if '背景' in self.user_input:
            info['background'] = self._extract_related_content('背景')
        
        # 提取研究目标
        if '目标' in self.user_input:
            info['goal'] = self._extract_related_content('目标')
        
        # 提取技术方案
        if '技术' in self.user_input or '方案' in self.user_input:
            info['technology'] = self._extract_related_content('技术') or self._extract_related_content('方案')
        
        # 提取创新点
        if '创新' in self.user_input:
            info['innovation'] = self._extract_related_content('创新')
        
        # 提取预期成果
        if '成果' in self.user_input or '营收' in self.user_input:
            info['expected_result'] = self._extract_related_content('成果') or self._extract_related_content('营收')
        
        # 提取进度计划（新增）
        if '进度' in self.user_input or '计划' in self.user_input or '里程碑' in self.user_input:
            info['timeline'] = self._extract_related_content('进度') or self._extract_related_content('计划') or self._extract_related_content('里程碑')
        
        return info
    
    def _generate_summary(self, info: dict) -> str:
        """生成摘要"""
        parts = []
        if info.get('project_name'):
            parts.append(f"本项目名为{info['project_name']}")
        if info.get('background'):
            bg = info['background'][:50]
            parts.append(f"针对{bg}...")
        if info.get('goal'):
            goal = info['goal'][:50]
            parts.append(f"旨在{goal}")
        if info.get('technology'):
            tech = info['technology'][:30]
            parts.append(f"采用{tech}等技术")
        
        if parts:
            return '。'.join(parts) + '。'
        return '[待补充：项目摘要]'
    
    def _generate_design_goal(self, info: dict) -> str:
        """生成设计目标"""
        if info.get('goal'):
            return info['goal']
        if info.get('background'):
            return f"解决{info['background'][:50]}...的问题"
        return '[待补充：设计目标]'
    
    def _generate_project_details(self, info: dict) -> str:
        """生成作品详情"""
        parts = []
        if info.get('technology'):
            parts.append(f"技术方案：{info['technology']}")
        if info.get('innovation'):
            parts.append(f"创新点：{info['innovation']}")
        if info.get('goal'):
            parts.append(f"实现目标：{info['goal']}")
        
        if parts:
            return '。'.join(parts) + '。'
        return '[待补充：作品详情]'
    
    def _generate_economic_value(self, info: dict) -> str:
        """生成经济社会价值"""
        if info.get('expected_result'):
            return f"预期成果：{info['expected_result']}"
        if info.get('project_name'):
            return f"本项目{info['project_name']}将创造显著的经济和社会价值"
        return '[待补充：经济社会价值]'
    
    def _generate_timeline(self, info: dict) -> str:
        """生成进度计划"""
        # 优先使用提取到的进度计划内容
        if info.get('timeline'):
            timeline = info['timeline']
            # 如果内容较长，适当截断但保留完整性
            if len(timeline) > 800:
                # 尝试在段落边界截断
                cutoff = timeline[:800].rfind('\n')
                if cutoff > 500:
                    timeline = timeline[:cutoff] + "..."
                else:
                    timeline = timeline[:800] + "..."
            return timeline
        
        # 尝试从 user_input 直接提取进度相关内容
        if '进度计划：' in self.user_input:
            match = re.search(r'进度计划：(.+?)(?:\n\n|\n(?=[^\n]*：)|$)', self.user_input, re.DOTALL)
            if match:
                timeline = match.group(1).strip()
                if len(timeline) > 800:
                    cutoff = timeline[:800].rfind('\n')
                    if cutoff > 500:
                        timeline = timeline[:cutoff] + "..."
                    else:
                        timeline = timeline[:800] + "..."
                return timeline
        
        # 默认的项目进度模板
        return "第一阶段：需求分析与系统设计；第二阶段：核心功能开发；第三阶段：系统测试与优化；第四阶段：部署与验收。"
    
    def _extract_name(self, field: str, keyword: str) -> str:
        """提取名称类字段（精确匹配单行内容）"""
        lines = self.user_input.split('\n')
        for line in lines:
            # 查找包含关键词的行，且格式为 "关键词：内容"
            if keyword in line and ':' in line:
                parts = line.split(':', 1)
                if len(parts) > 1:
                    value = parts[1].strip()
                    # 确保是简短的名称（不是长段落）
                    if len(value) > 2 and len(value) < 50 and '。' not in value:
                        return value
            # 或者 "关键词 内容" 格式
            elif line.startswith(keyword) and len(line) < 50:
                value = line[len(keyword):].strip()
                if len(value) > 2 and len(value) < 50 and '。' not in value:
                    return value
        return ''
    
    def _split_line(self, line: str) -> tuple:
        """分割行，支持多种冒号（英文、中文、全角）"""
        # 尝试多种冒号：英文 (U+003A)、中文 (U+FF1A)
        for sep in [':', chr(0xFF1A)]:  # 英文冒号、中文全角冒号
            if sep in line:
                parts = line.split(sep, 1)
                if len(parts) > 1:
                    return parts[0].strip(), parts[1].strip()
        return None, None
    
    def _extract_personal_info(self, field: str, keyword: str) -> str:
        """提取个人信息字段（精确匹配）"""
        lines = self.user_input.split('\n')
        for line in lines:
            line = line.strip()
            key, value = self._split_line(line)
            if key and value:
                # 检查字段名是否匹配
                if field == key or field in key or key in field:
                    # 个人信息应该是简短的
                    if len(value) > 1 and len(value) < 100:
                        return value
        return ''
    
    def _extract_name(self, field: str, keyword: str) -> str:
        """提取名称类字段（精确匹配单行内容）"""
        lines = self.user_input.split('\n')
        for line in lines:
            line = line.strip()
            key, value = self._split_line(line)
            if key and value:
                # 检查字段名是否匹配
                if field == key or field in key or key in field:
                    # 确保是简短的名称（不是长段落）
                    if len(value) > 2 and len(value) < 50 and '.' not in value and '.' not in value:
                        return value
        return ''
    
    def _get_keywords_for_title(self, title: str) -> List[str]:
        """根据标题获取相关关键词"""
        title_lower = title.lower()
        
        for key_title, keywords in self.KEYWORD_MAP.items():
            if key_title in title_lower or title_lower in key_title:
                return keywords
        
        for key_title, keywords in self.KEYWORD_MAP.items():
            if any(k in title_lower for k in keywords):
                return keywords
        
        return []
    
    def _segment_input(self) -> List[str]:
        """将用户输入分段"""
        segments = re.split(r'[。！？\n]+', self.user_input)
        return [s.strip() for s in segments if s.strip()]
    
    def _extract_related_content(self, keyword: str) -> str:
        """提取与关键词相关的内容"""
        lines = self.user_input.split('\n')
        
        # 定义全角和半角冒号
        COLON_HALF = ':'  # U+003A
        COLON_FULL = '：'  # U+FF1A
        
        # 优先尝试提取"关键词：内容"格式（支持多行内容）
        for i, line in enumerate(lines):
            # 检查是否以"关键词："或"关键词："开头
            if line.startswith(keyword + COLON_HALF) or line.startswith(keyword + COLON_FULL):
                # 分割时也要支持两种冒号
                if COLON_HALF in line:
                    parts = line.split(COLON_HALF, 1)
                elif COLON_FULL in line:
                    parts = line.split(COLON_FULL, 1)
                else:
                    continue
                    
                if len(parts) > 1:
                    content = parts[1].strip()
                    # 继续收集后续行，直到遇到下一个字段开始
                    j = i + 1
                    while j < len(lines):
                        next_line = lines[j].strip()
                        # 检查是否是新的字段开始（行首是字段名 + 冒号）
                        # 注意：正则中字段名之间不能有空格
                        field_pattern = r'^(摘要|设计目标|作品详情|解决方案详情|经济社会价值|经济与社会价值|进度计划|项目进度计划|项目名称|参赛赛项|学校名称|团队名称|联系电话|邮箱|指导教师|队长姓名|队员姓名|技术方案|研究目标|研究内容|项目背景|创新点|预期成果|经费预算)[:：]'
                        if re.match(field_pattern, next_line):
                            break
                        content += '\n' + next_line
                        j += 1
                    if len(content) > 10:
                        return content
        
        # 尝试从【参考文档】区域中提取内容
        in_doc = False
        doc_content = []
        for line in lines:
            if line.startswith('【参考文档:'):
                in_doc = True
                continue
            elif line.startswith('['):
                in_doc = False
            elif in_doc:
                doc_content.append(line)
        
        if doc_content:
            doc_text = '\n'.join(doc_content)
            if keyword in doc_text:
                paragraphs = doc_text.split('\n\n')
                for para in paragraphs:
                    if keyword in para and len(para) > 10:
                        return para.strip()
                doc_lines = doc_text.split('\n')
                for line in doc_lines:
                    if keyword in line and len(line.strip()) > 5:
                        return line.strip()
        
        # 如果没有找到标签格式，尝试按句子提取
        sentences = re.split(r'[。！？]', self.user_input)
        related = [s.strip() for s in sentences if keyword in s and len(s.strip()) > 5]
        
        # 过滤掉明显是其他章节的内容
        filtered = []
        exclude_keywords = ['深化产教融合', '经济社会价值', '商业价值', '经济价值']
        for s in related:
            if not any(excl in s for excl in exclude_keywords):
                filtered.append(s)
        
        if filtered:
            return '。'.join(filtered) + '。'
        
        return '。'.join(related) + '。' if related else ''
    
    def get_fill_report(self) -> str:
        """生成填充报告"""
        report_lines = ["\n📋 填充报告：\n"]
        
        for title, content in self.matches.items():
            confidence = self.confidence.get(title, 0)
            word_count = len(content)
            
            if confidence >= 0.7:
                status = "✅"
            elif confidence >= 0.4:
                status = "⚠️"
            else:
                status = "❌"
            
            report_lines.append(f"   {status} {title}：{content[:50]}... ({word_count}字)")
        
        return '\n'.join(report_lines)


def main():
    # 测试用
    test_input = """
    项目名称：AI 辅助的个性化学习系统
    项目背景：当前在线教育平台缺乏个性化推荐，学生学习效率低。
    研究目标：开发一个智能学习推荐系统，提高学习效率 30% 以上。
    研究内容：包括用户行为分析、内容推荐算法、学习路径规划。
    技术方案：使用机器学习算法，基于 Python 和 TensorFlow 实现。
    创新点：首次将强化学习应用于学习路径推荐。
    团队成员：3 人，分别负责后端、前端、算法。
    项目周期：6 个月。
    预算：2 万元。
    """
    
    test_sections = [
        {'title': '项目背景'},
        {'title': '研究目标'},
        {'title': '研究内容'},
        {'title': '技术方案'},
        {'title': '创新点'},
        {'title': '团队介绍'},
        {'title': '进度安排'},
        {'title': '经费预算'},
    ]
    
    matcher = ContentMatcher(test_input, test_sections)
    result = matcher.match()
    
    print("匹配结果:")
    for title, content in result['matches'].items():
        print(f"\n{title}:")
        print(f"  内容：{content[:100]}...")
        print(f"  置信度：{result['confidence'][title]:.2f}")
    
    print("\n" + matcher.get_fill_report())


if __name__ == "__main__":
    main()
