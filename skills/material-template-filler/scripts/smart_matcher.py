#!/usr/bin/env python3
"""
智能语义匹配器 - 自动分析章节与表格字段的对应关系

基于以下策略：
1. 标题语义相似度分析
2. 内容特征识别（关键词、结构模式）
3. 上下文关联分析
"""

import re
from typing import Dict, List, Tuple


class SmartSectionMatcher:
    """
    智能章节匹配器 - 通过语义和内容特征自动匹配章节到表格字段
    """
    
    # 表格字段定义：每个字段有关键词、内容特征、优先级
    TABLE_FIELDS = {
        '参赛赛项名称': {
            'keywords': ['赛项', '参赛', '竞赛名称', '比赛'],
            'content_patterns': [r'赛项', r'竞赛', r'比赛'],
            'expected_length': (2, 50),  # 预期内容长度
            'priority': 1,  # 个人信息优先级高
        },
        '作品/方案名称': {
            'keywords': ['作品', '方案', '项目', '系统', '名称'],
            'content_patterns': [r'系统', r'方案', r'项目', r'基于'],
            'expected_length': (5, 100),
            'priority': 1,
        },
        '摘要': {
            'keywords': ['摘要', '概述', '简介', '总结'],
            'content_patterns': [r'背景', r'痛点', r'本方案', r'提出', r'旨在'],
            'expected_length': (100, 1000),
            'priority': 2,
        },
        '设计目标': {
            'keywords': ['目标', '目的', '预期', '指标'],
            'content_patterns': [
                r'设计.*[≥≤][\d.]+',  # 量化指标
                r'达到.*[\d.]+',
                r'控制在.*[\d.]+',
                r'提升.*[\d.]+',
                r'降低.*[\d.]+',
            ],
            'expected_length': (50, 2000),
            'priority': 2,
        },
        '作品详情/解决方案详情': {
            'keywords': ['详情', '方案', '解决', '实现', '技术', '架构'],
            'content_patterns': [
                r'思路', r'框架', r'架构', r'流程',
                r'可行性', r'技术.*[一二三四]',
                r'集成', r'部署', r'运维',
            ],
            'expected_length': (200, 10000),
            'priority': 2,
        },
        '经济与社会\n价值': {
            'keywords': ['价值', '效益', '经济', '社会', '意义', '影响'],
            'content_patterns': [
                r'经济.*价值', r'社会.*价值', r'效益',
                r'成本', r'市场', r'产业', r'战略',
            ],
            'expected_length': (100, 5000),
            'priority': 2,
        },
        '项目进度计划\n（里程碑制定）': {
            'keywords': ['进度', '计划', '里程碑', '时间', '周期', '阶段', '周'],
            'content_patterns': [
                r'第 [一二三四五六七八九十\d]+[周阶段]',
                r'\d+-\d+[周阶段]',
                r'里程碑', r'阶段', r'输出',
            ],
            'expected_length': (100, 5000),
            'priority': 2,
        },
    }
    
    def __init__(self, sections: Dict[str, str]):
        """
        Args:
            sections: {章节标题：内容}
        """
        self.sections = sections
        self.matches = {}  # {表格字段：(章节标题，置信度)}
        
    def match_all(self) -> Dict[str, Tuple[str, float]]:
        """
        匹配所有章节到表格字段
        
        Returns:
            {表格字段：(匹配的章节标题，置信度)}
        """
        for field_name, field_info in self.TABLE_FIELDS.items():
            best_match = self._find_best_match(field_name, field_info)
            if best_match:
                self.matches[field_name] = best_match
        
        return self.matches
    
    def _find_best_match(self, field_name: str, field_info: dict) -> Tuple[str, float]:
        """
        为指定字段找到最佳匹配的章节
        
        Returns:
            (章节标题，置信度 0-1)
        """
        candidates = []
        
        for section_title, section_content in self.sections.items():
            score = self._calculate_match_score(
                section_title, section_content, field_name, field_info
            )
            if score > 0.3:  # 阈值
                candidates.append((section_title, score))
        
        if not candidates:
            return None
        
        # 返回最高分
        return max(candidates, key=lambda x: x[1])
    
    def _calculate_match_score(
        self, 
        section_title: str, 
        section_content: str,
        field_name: str,
        field_info: dict
    ) -> float:
        """
        计算章节与字段的匹配分数
        
        综合考虑：
        1. 标题关键词匹配 (40%)
        2. 内容特征匹配 (40%)
        3. 内容长度匹配 (20%)
        """
        scores = {}
        
        # 1. 标题关键词匹配
        scores['title'] = self._match_title_keywords(section_title, field_info)
        
        # 2. 内容特征匹配
        scores['content'] = self._match_content_patterns(section_content, field_info)
        
        # 3. 内容长度匹配
        scores['length'] = self._match_length(len(section_content), field_info)
        
        # 加权总分
        total = (
            scores['title'] * 0.4 +
            scores['content'] * 0.4 +
            scores['length'] * 0.2
        )
        
        return total
    
    def _match_title_keywords(self, title: str, field_info: dict) -> float:
        """标题关键词匹配"""
        title_lower = title.lower()
        
        # 完全包含关键词
        for keyword in field_info['keywords']:
            if keyword in title_lower:
                return 1.0
        
        # 部分匹配
        title_words = set(re.split(r'[、,，.．\s]+', title_lower))
        keyword_words = set(field_info['keywords'])
        
        if title_words & keyword_words:
            return 0.7
        
        # 字符级相似度
        for keyword in keyword_words:
            if len(keyword) >= 2 and any(k in title_lower for k in keyword):
                return 0.5
        
        return 0.0
    
    def _match_content_patterns(self, content: str, field_info: dict) -> float:
        """内容特征匹配"""
        if not content:
            return 0.0
        
        content_lower = content.lower()
        matched_patterns = 0
        
        for pattern in field_info['content_patterns']:
            if re.search(pattern, content_lower):
                matched_patterns += 1
        
        if matched_patterns == 0:
            return 0.0
        
        # 匹配的模式越多，分数越高
        max_patterns = len(field_info['content_patterns'])
        return min(1.0, matched_patterns / max(1, max_patterns) * 1.5)
    
    def _match_length(self, content_length: int, field_info: dict) -> float:
        """内容长度匹配"""
        min_len, max_len = field_info['expected_length']
        
        if min_len <= content_length <= max_len:
            return 1.0
        
        # 接近范围也给一定分数
        if content_length < min_len:
            return max(0.3, content_length / min_len)
        else:
            return max(0.3, max_len / content_length)
    
    def get_match_report(self) -> str:
        """生成匹配报告"""
        lines = ["=== 智能匹配报告 ===\n"]
        
        for field, (section, confidence) in self.matches.items():
            status = '✅' if confidence >= 0.7 else '⚠️' if confidence >= 0.5 else '❓'
            lines.append(f"{status} {field}")
            lines.append(f"   匹配章节：{section}")
            lines.append(f"   置信度：{confidence:.0%}")
            lines.append("")
        
        # 未匹配的字段
        unmatched = set(self.TABLE_FIELDS.keys()) - set(self.matches.keys())
        if unmatched:
            lines.append("⚪ 未匹配字段:")
            for field in unmatched:
                lines.append(f"   - {field}")
        
        return '\n'.join(lines)


class ContentFeatureAnalyzer:
    """
    内容特征分析器 - 分析章节内容的特征，辅助匹配
    """
    
    # 内容类型特征
    CONTENT_TYPES = {
        'quantitative': [  # 量化指标型
            r'[\d.]+[%\d]',
            r'[≥≤][\d.]+',
            r'控制在.*[\d.]+',
            r'达到.*[\d.]+',
        ],
        'temporal': [  # 时间规划型
            r'第 [一二三四五六七八九十\d]+[周阶段月]',
            r'\d+-\d+[周阶段]',
            r'时间', r'周期', r'阶段',
        ],
        'technical': [  # 技术描述型
            r'技术', r'算法', r'架构', r'系统',
            r'模块', r'功能', r'实现',
        ],
        'value': [  # 价值描述型
            r'价值', r'效益', r'意义', r'影响',
            r'经济', r'社会', r'市场',
        ],
        'summary': [  # 摘要概述型
            r'背景', r'痛点', r'本方案', r'提出',
            r'旨在', r'概述', r'简介',
        ],
    }
    
    def __init__(self, content: str):
        self.content = content
        self.features = {}
        
    def analyze(self) -> Dict[str, float]:
        """
        分析内容特征
        
        Returns:
            {特征类型：置信度}
        """
        content_lower = self.content.lower()
        
        for feature_type, patterns in self.CONTENT_TYPES.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, content_lower):
                    score += 1
            self.features[feature_type] = min(1.0, score / len(patterns))
        
        return self.features
    
    def get_primary_type(self) -> str:
        """获取主要内容类型"""
        if not self.features:
            self.analyze()
        
        if not self.features:
            return 'unknown'
        
        return max(self.features.items(), key=lambda x: x[1])[0]


def test_smart_matcher():
    """测试智能匹配器"""
    # 模拟章节数据
    test_sections = {
        '一、摘要': '当前 5G 广域覆盖存在短板，低轨卫星视频传输面临高误码、大时延、带宽稀缺的行业痛点。本方案提出基于 MDVSC 的 5G+ 低轨卫星视频语义通信系统。',
        '二、设计目标': '1. 抗误码性能：1e-3 误码率时 PSNR≥32dB\n2. 传输效率：带宽≤1.2Mbps，降低 70%\n3. 时延控制：端到端时延≤300ms',
        '三、作品详情/解决方案详情': '本方案以"痛点聚焦 - 技术适配 - 架构简化"为核心逻辑。包括解决思路框架、可行性分析、关键技术应用、系统架构等。',
        '四、经济与社会价值': '社会价值：助力 5G+ 卫星空天地一体化建设，提升应急救援能力。经济价值：成本效益分析，行业经济贡献。',
        '五、项目进度计划': '里程碑一（第 1-3 周）：需求收口与方案定型。里程碑二（第 4-9 周）：核心模块开发。里程碑三（第 10-12 周）：原型机调试。',
    }
    
    print("=" * 60)
    print("🧠 智能语义匹配器测试")
    print("=" * 60)
    
    matcher = SmartSectionMatcher(test_sections)
    matches = matcher.match_all()
    
    print(matcher.get_match_report())
    
    # 测试内容特征分析
    print("\n=== 内容特征分析测试 ===")
    for title, content in test_sections.items():
        analyzer = ContentFeatureAnalyzer(content)
        features = analyzer.analyze()
        primary = analyzer.get_primary_type()
        print(f"\n{title}:")
        print(f"  主要类型：{primary}")
        print(f"  特征：{features}")
    
    return matches


if __name__ == "__main__":
    test_smart_matcher()
