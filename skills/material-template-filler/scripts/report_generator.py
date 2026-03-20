#!/usr/bin/env python3
"""
报告生成器 - 生成独立的填充报告文件 (.md 格式)
"""

import os
from datetime import datetime
from typing import Dict, List


class ReportGenerator:
    """生成填充报告"""
    
    # 填充状态分类
    STATUS_EMPTY = "未填充"  # 没有相关内容
    STATUS_FILLED = "已基于材料内容填充"  # 从用户输入中提取并填充
    STATUS_EXPANDED = "LLM 扩展生成内容"  # 内容不足，由 LLM 扩展生成
    
    def __init__(self, template_structure: dict, match_result: dict, user_input: str):
        self.template_structure = template_structure
        self.matches = match_result.get('matches', {})
        self.confidence = match_result.get('confidence', {})
        self.user_input = user_input
        self.sections = template_structure.get('sections', [])
        
    def classify_fill_status(self, title: str, content: str, confidence: float) -> str:
        """
        分类填充状态
        
        - 未填充：置信度 < 0.3 或内容为空/待补充
        - 已基于材料内容填充：置信度 >= 0.7 且有实际内容
        - LLM 扩展生成内容：0.3 <= 置信度 < 0.7，有内容但需要扩展
        """
        if not content or content.strip() == '' or '待补充' in content:
            return self.STATUS_EMPTY
        
        if confidence >= 0.7:
            return self.STATUS_FILLED
        else:
            return self.STATUS_EXPANDED
    
    def generate_report(self, output_path: str = None) -> str:
        """
        生成 Markdown 格式的报告
        
        Args:
            output_path: 报告输出路径，如果为 None 则返回字符串
            
        Returns:
            报告内容字符串
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 统计各状态数量
        status_counts = {
            self.STATUS_EMPTY: 0,
            self.STATUS_FILLED: 0,
            self.STATUS_EXPANDED: 0
        }
        
        report_lines = []
        
        # 报告标题
        report_lines.append("# 📋 材料模板填充报告")
        report_lines.append("")
        report_lines.append(f"**生成时间**: {timestamp}")
        report_lines.append(f"**模板文件**: {self.template_structure.get('template_path', '未知')}")
        
        # 区分模板模块和表格字段
        template_sections = self.sections if self.sections else []
        table_fields = [f for f in self.matches.keys() if f not in [s['title'] for s in template_sections]]
        
        report_lines.append(f"**模板模块数**: {len(template_sections)}")
        report_lines.append(f"**表格字段数**: {len(table_fields)}")
        report_lines.append("")
        
        # 填充摘要
        report_lines.append("## 📊 填充摘要")
        report_lines.append("")
        
        for title in self.matches:
            content = self.matches.get(title, '')
            conf = self.confidence.get(title, 0)
            status = self.classify_fill_status(title, content, conf)
            status_counts[status] += 1
        
        report_lines.append("| 状态 | 数量 | 说明 |")
        report_lines.append("|------|------|------|")
        report_lines.append(f"| ✅ {self.STATUS_FILLED} | {status_counts[self.STATUS_FILLED]} | 从用户提供的材料中提取并填充 |")
        report_lines.append(f"| ⚠️ {self.STATUS_EXPANDED} | {status_counts[self.STATUS_EXPANDED]} | 内容不足，由 AI 扩展生成 |")
        report_lines.append(f"| ❌ {self.STATUS_EMPTY} | {status_counts[self.STATUS_EMPTY]} | 未找到相关内容，需人工补充 |")
        report_lines.append("")
        
        # 填充率
        filled_rate = (status_counts[self.STATUS_FILLED] + status_counts[self.STATUS_EXPANDED]) / len(self.sections) * 100 if self.sections else 0
        report_lines.append(f"**整体填充率**: {filled_rate:.1f}%")
        report_lines.append("")
        
        # 各模块详细填充情况
        report_lines.append("## 📝 各模块填充详情")
        report_lines.append("")
        
        # 模板模块（标题样式）
        if template_sections:
            report_lines.append("### 模板模块")
            report_lines.append("")
            for i, section in enumerate(template_sections, 1):
                title = section['title']
                content = self.matches.get(title, '')
                conf = self.confidence.get(title, 0)
                status = self.classify_fill_status(title, content, conf)
                word_limit = section.get('word_limit')
                requirements = section.get('requirements', '')
                
                # 状态图标
                if status == self.STATUS_FILLED:
                    status_icon = "✅"
                elif status == self.STATUS_EXPANDED:
                    status_icon = "⚠️"
                else:
                    status_icon = "❌"
                
                report_lines.append(f"### {i}. {title}")
                report_lines.append("")
            report_lines.append(f"- **填充状态**: {status_icon} {status}")
            report_lines.append(f"- **置信度**: {conf:.0%}")
            
            if word_limit:
                report_lines.append(f"- **字数限制**: {word_limit}字")
            
            if requirements:
                report_lines.append(f"- **填写要求**: {requirements}")
            
            # 内容预览
            if content and '待补充' not in content:
                content_preview = content[:200].replace('\n', ' ')
                if len(content) > 200:
                    content_preview += "..."
                report_lines.append(f"- **填充内容预览**: {content_preview}")
                report_lines.append(f"- **内容字数**: {len(content)}字")
            else:
                report_lines.append(f"- **填充内容**: 无（需人工补充）")
            
            report_lines.append("")
        
        # 表格字段
        if table_fields:
            report_lines.append("### 表格字段")
            report_lines.append("")
            report_lines.append("| 字段名 | 状态 | 置信度 | 内容预览 |")
            report_lines.append("|--------|------|--------|----------|")
            
            for field in table_fields:
                content = self.matches.get(field, '')
                conf = self.confidence.get(field, 0)
                status = self.classify_fill_status(field, content, conf)
                
                if status == self.STATUS_FILLED:
                    status_icon = "✅"
                elif status == self.STATUS_EXPANDED:
                    status_icon = "⚠️"
                else:
                    status_icon = "❌"
                
                preview = content[:30].replace('\n', ' ') + '...' if len(content) > 30 else content
                if not preview or preview.strip() == '':
                    preview = '（无内容）'
                
                report_lines.append(f"| {field} | {status_icon} {status} | {conf:.0%} | {preview} |")
            
            report_lines.append("")
        
        # 建议
        report_lines.append("## 💡 建议与注意事项")
        report_lines.append("")
        
        if status_counts[self.STATUS_EMPTY] > 0:
            report_lines.append("### 需要人工补充的模块")
            report_lines.append("")
            for section in self.sections:
                title = section['title']
                content = self.matches.get(title, '')
                conf = self.confidence.get(title, 0)
                status = self.classify_fill_status(title, content, conf)
                if status == self.STATUS_EMPTY:
                    report_lines.append(f"- {title}")
            report_lines.append("")
        
        if status_counts[self.STATUS_EXPANDED] > 0:
            report_lines.append("### 建议检查的模块（AI 扩展内容）")
            report_lines.append("")
            for section in self.sections:
                title = section['title']
                content = self.matches.get(title, '')
                conf = self.confidence.get(title, 0)
                status = self.classify_fill_status(title, content, conf)
                if status == self.STATUS_EXPANDED:
                    report_lines.append(f"- {title}（置信度：{conf:.0%}）")
            report_lines.append("")
        
        report_lines.append("### 通用建议")
        report_lines.append("")
        report_lines.append("1. 打开填充后的文档，检查所有内容")
        report_lines.append("2. 重点检查标记为 ⚠️ 的模块，确认 AI 扩展内容是否准确")
        report_lines.append("3. 补充标记为 ❌ 的模块内容")
        report_lines.append("4. 调整格式以符合模板要求")
        report_lines.append("5. 核实字数是否符合限制")
        report_lines.append("")
        
        # 报告结尾
        report_lines.append("---")
        report_lines.append("")
        report_lines.append("*本报告由 材料模板填写 Skill 自动生成*")
        
        report_content = '\n'.join(report_lines)
        
        # 写入文件
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
        
        return report_content
    
    def generate_report_path(self, template_path: str) -> str:
        """根据模板路径生成报告文件路径（保存到 filled/ 目录）"""
        # 获取模板文件名（不含路径）
        template_name = os.path.basename(template_path)
        base, _ = os.path.splitext(template_name)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 输出到 filled/ 目录
        workspace_dir = os.path.expanduser("~/.openclaw/workspace")
        filled_dir = os.path.join(workspace_dir, "filled")
        
        # 确保 filled 目录存在
        os.makedirs(filled_dir, exist_ok=True)
        
        report_path = os.path.join(filled_dir, f"{base}_fill_report_{timestamp}.md")
        return report_path


def main():
    # 测试用
    template_structure = {
        'template_path': 'templates/test.docx',
        'sections': [
            {'title': '项目背景', 'word_limit': 500},
            {'title': '研究目标', 'word_limit': 300},
            {'title': '研究内容', 'word_limit': 800},
            {'title': '技术方案'},
            {'title': '创新点', 'word_limit': 200},
            {'title': '团队介绍'},
            {'title': '进度安排'},
            {'title': '经费预算'},
        ]
    }
    
    match_result = {
        'matches': {
            '项目背景': '当前在线教育平台缺乏个性化推荐，学生学习效率低。',
            '研究目标': '开发一个智能学习推荐系统，提高学习效率 30% 以上。',
            '研究内容': '包括用户行为分析、内容推荐算法、学习路径规划。',
            '技术方案': '[待补充：技术方案相关内容]',
            '创新点': '首次将强化学习应用于学习路径推荐。',
            '团队介绍': '3 人，分别负责后端、前端、算法。',
            '进度安排': '',
            '经费预算': '2 万元。',
        },
        'confidence': {
            '项目背景': 0.85,
            '研究目标': 0.90,
            '研究内容': 0.75,
            '技术方案': 0.15,
            '创新点': 0.65,
            '团队介绍': 0.80,
            '进度安排': 0.10,
            '经费预算': 0.70,
        }
    }
    
    generator = ReportGenerator(template_structure, match_result, "")
    report = generator.generate_report()
    print(report)
    
    # 保存到文件
    output_path = generator.generate_report_path('templates/test.docx')
    generator.generate_report(output_path)
    print(f"\n报告已保存到：{output_path}")


if __name__ == "__main__":
    main()
