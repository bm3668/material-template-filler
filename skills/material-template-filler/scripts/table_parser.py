#!/usr/bin/env python3
"""
表格字段解析器 - 从表格中识别可填充的字段
"""

import re
from typing import Dict, List, Tuple


class TableFieldParser:
    """解析表格中的字段"""
    
    # 字段标签到标准字段名的映射
    FIELD_MAPPING = {
        # 作品信息
        '作品名称': '作品名称',
        '作品/方案名称': '作品名称',
        '方案名称': '作品名称',
        '项目名称': '项目名称',
        '参赛赛项名称': '参赛赛项',
        '赛项名称': '参赛赛项',
        
        # 团队信息
        '学校全称': '学校名称',
        '学校': '学校名称',
        '团队名称': '团队名称',
        '团队编号': '团队编号',
        '联系电话': '联系电话',
        '电话': '联系电话',
        '邮箱': '邮箱',
        '指导教师姓名': '指导教师',
        '指导教师': '指导教师',
        '任课专业': '专业',
        '队长姓名': '队长姓名',
        '队员姓名': '队员姓名',
        '所在专业': '专业',
        
        # 设计方案
        '摘要': '摘要',
        '设计目标': '设计目标',
        '目标': '设计目标',
        '作品详情/解决方案详情': '作品详情',
        '作品详情': '作品详情',
        '解决方案详情': '作品详情',
        '解决方案': '作品详情',
        '设计思路': '作品详情',
        '技术框架': '作品详情',
        '经济与社会\n价值': '经济社会价值',
        '经济与社会价值': '经济社会价值',
        '商业价值': '经济社会价值',
        '社会价值': '经济社会价值',
        '项目进度计划\n（里程碑制定）': '进度计划',
        '项目进度计划': '进度计划',
        '进度计划': '进度计划',
        '里程碑': '进度计划',
        
        # 通用字段
        '背景': '项目背景',
        '项目背景': '项目背景',
        '研究目标': '研究目标',
        '研究内容': '研究内容',
        '技术方案': '技术方案',
        '创新点': '创新点',
        '团队介绍': '团队介绍',
        '研究基础': '研究基础',
        '预期成果': '预期成果',
        '经费预算': '经费预算',
        '预算': '经费预算',
    }
    
    def __init__(self):
        self.fields = []
        
    def parse_table(self, table) -> List[Dict]:
        """解析表格，提取字段信息"""
        fields = []
        
        for row_idx, row in enumerate(table.rows):
            cells = row.cells
            if len(cells) >= 2:
                # 两列格式：第一列是标签，第二列是内容
                label = cells[0].text.strip()
                if label and len(cells) > 1:
                    field = self._parse_field(label, cells[1], row_idx, 0)
                    if field:
                        fields.append(field)
                elif len(cells) >= 4:
                    # 多列格式（如团队信息表）
                    for col_idx in range(0, len(cells), 2):
                        if col_idx + 1 < len(cells):
                            label = cells[col_idx].text.strip()
                            if label:
                                field = self._parse_field(label, cells[col_idx + 1], row_idx, col_idx)
                                if field:
                                    fields.append(field)
        
        return fields
    
    def _parse_field(self, label: str, cell, row_idx: int, col_idx: int) -> Dict:
        """解析单个字段"""
        # 标准化字段名
        std_name = self._standardize_field_name(label)
        
        # 提取字段的说明/要求（从标签和相邻单元格）
        requirements = self._extract_requirements(label)
        
        # 尝试从相邻单元格获取更多信息
        cell_text = cell.text.strip() if cell else ''
        if cell_text and not requirements:
            requirements = self._extract_requirements(cell_text)
        
        # 解析字数限制
        word_limit = self._extract_word_limit(requirements)
        
        # 解析内容要点
        content_points = self._extract_content_points(requirements)
        
        return {
            'label': label,  # 原始标签
            'std_name': std_name,  # 标准化名称
            'requirements': requirements,  # 完整填写要求
            'word_limit': word_limit,  # 字数限制
            'content_points': content_points,  # 内容要点列表
            'cell': cell,  # 单元格对象
            'row_idx': row_idx,
            'col_idx': col_idx,
        }
    
    def _standardize_field_name(self, label: str) -> str:
        """标准化字段名称"""
        # 清理标签（去除括号、换行等）
        clean_label = re.sub(r'[\n（(].*', '', label).strip()
        
        # 查找映射
        if clean_label in self.FIELD_MAPPING:
            return self.FIELD_MAPPING[clean_label]
        
        # 模糊匹配
        for key, value in self.FIELD_MAPPING.items():
            if key in clean_label or clean_label in key:
                return value
        
        # 返回清理后的标签
        return clean_label
    
    def _extract_requirements(self, label: str) -> str:
        """从标签中提取填写要求"""
        # 提取括号中的说明（支持中文和英文括号）
        match = re.search(r'[（(](.+?)[)）]', label)
        if match:
            return match.group(1)
        return ''
    
    def _extract_word_limit(self, requirements: str) -> int:
        """从要求中提取字数限制"""
        if not requirements:
            return None
        # 匹配 "不超过 XXX 字" 或 "限 XXX 字" 或 "XXX 字以内"
        # 更灵活的正则
        patterns = [
            r'不.*?(\d+).*?[个字符字]',  # 不超过 XXX 字
            r'限.*?(\d+).*?[个字符字]',   # 限 XXX 字
            r'(\d+).*?[个字符字] 以内',   # XXX 字以内
            r'(\d+)[个字符字]',          # 直接 XXX 字
        ]
        for pattern in patterns:
            match = re.search(pattern, requirements)
            if match:
                return int(match.group(1))
        return None
    
    def _extract_content_points(self, requirements: str) -> List[str]:
        """从要求中提取内容要点"""
        if not requirements:
            return []
        
        points = []
        # 清理要求文本（去除字数限制）
        clean_req = re.sub(r'不超过？[的]?\d+[个字符字]|限？[的]?\d+[个字符字]|\d+[个字符字]以内', '', requirements)
        
        # 分割要点（支持顿号、逗号、分号）
        raw_points = re.split(r'[、,;,.]', clean_req)
        
        for point in raw_points:
            point = point.strip()
            # 过滤掉太短的片段
            if len(point) > 1 and not point.isdigit():
                points.append(point)
        
        return points


def main():
    # 测试
    print("表格字段解析器 - 测试")
    print("=" * 50)
    
    test_labels = [
        '作品/方案名称',
        '摘要（作品/方案背景与意义、目的、方法，不超过 500 字。）',
        '经济与社会\n价值',
        '项目进度计划\n（里程碑制定）',
    ]
    
    parser = TableFieldParser()
    for label in test_labels:
        std_name = parser._standardize_field_name(label)
        req = parser._extract_requirements(label)
        print(f"\n原始标签：{label}")
        print(f"标准名称：{std_name}")
        print(f"填写要求：{req}")


if __name__ == "__main__":
    main()
