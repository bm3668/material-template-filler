#!/usr/bin/env python3
"""
材料模板填写 - 主入口脚本

用法:
    python main.py <模板文件> "<项目内容>"
    
示例:
    python main.py templates/申报书.docx "项目名称：AI 辅助学习系统。项目背景：当前在线教育..."
"""

import sys
import os
import json
from datetime import datetime

# 添加脚本目录到路径
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from template_parser import TemplateParser
from content_matcher import ContentMatcher
from docx_filler import DocxFiller
from validator import Validator
from report_generator import ReportGenerator


def generate_output_path(template_path: str) -> str:
    """生成输出文件路径（保存到 filled/ 目录）"""
    # 获取模板文件名（不含路径）
    template_name = os.path.basename(template_path)
    base, ext = os.path.splitext(template_name)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 输出到 filled/ 目录
    workspace_dir = os.path.expanduser("~/.openclaw/workspace")
    filled_dir = os.path.join(workspace_dir, "filled")
    
    # 确保 filled 目录存在
    os.makedirs(filled_dir, exist_ok=True)
    
    output_path = os.path.join(filled_dir, f"{base}_filled_{timestamp}.docx")
    return output_path


def main():
    if len(sys.argv) < 3:
        print("📋 材料模板填写 Skill")
        print("=" * 50)
        print("\n用法:")
        print("  python main.py <模板文件> \"<项目内容>\"")
        print("\n示例:")
        print("  python main.py templates/申报书.docx \"项目名称：AI 辅助学习系统。项目背景：...\"")
        print("\n参数:")
        print("  模板文件  - .docx 格式的模板文件路径")
        print("  项目内容  - 项目描述文本，用引号包裹")
        sys.exit(1)
    
    template_path = sys.argv[1]
    user_input = sys.argv[2] if len(sys.argv) > 2 else ""
    
    # 如果是相对路径，尝试从工作区 templates 目录查找
    if not os.path.isabs(template_path):
        workspace_templates = os.path.expanduser("~/.openclaw/workspace/templates")
        alt_path = os.path.join(workspace_templates, template_path)
        if os.path.exists(alt_path):
            template_path = alt_path
    
    print("\n📋 材料模板填写 Skill")
    print("=" * 50)
    
    # 步骤 1: 解析模板
    print(f"\n🔍 步骤 1/5: 解析模板...")
    print(f"   模板文件：{template_path}")
    
    try:
        parser = TemplateParser(template_path)
        parser.parse()
        parser.print_structure()
        template_structure = parser.get_structure()
    except Exception as e:
        print(f"❌ 模板解析失败：{e}")
        sys.exit(1)
    
    # 步骤 2: 解析表格字段要求
    print(f"\n📋 步骤 2/5: 解析表格字段要求...")
    
    try:
        from table_parser import TableFieldParser
        parser_obj = TemplateParser(template_path)
        parser_obj.parse()
        
        field_requirements = {}
        for table in parser_obj.doc.tables:
            field_parser = TableFieldParser()
            fields = field_parser.parse_table(table)
            for field in fields:
                std_name = field['std_name']
                if std_name not in field_requirements:
                    field_requirements[std_name] = {
                        'requirements': field['requirements'],
                        'word_limit': field['word_limit'],
                        'content_points': field['content_points'],
                    }
        
        print(f"   解析到 {len(field_requirements)} 个字段要求")
    except Exception as e:
        print(f"   ⚠️ 解析字段要求失败：{e}")
        field_requirements = {}
    
    # 步骤 3: 匹配内容
    print(f"\n🤖 步骤 3/5: 匹配内容到模板模块...")
    
    matcher = ContentMatcher(user_input, template_structure['sections'])
    # 传递字段要求给 matcher
    matcher._extract_table_fields(field_requirements)
    match_result = matcher.match()
    content_map = match_result['matches']
    confidence = match_result['confidence']
    
    # 步骤 4: 填充文档
    output_path = generate_output_path(template_path)
    print(f"\n✏️  步骤 4/5: 填充文档...")
    print(f"   输出文件：{output_path}")
    
    try:
        filler = DocxFiller(template_path, output_path)
        filler.fill(content_map)
        # 不再在 docx 中添加报告（已改为独立文件）
    except Exception as e:
        print(f"❌ 文档填充失败：{e}")
        sys.exit(1)
    
    # 步骤 5: 校验
    print(f"\n🔍 步骤 5/5: 校验文档...")
    
    try:
        validator = Validator(output_path)
        result = validator.validate(template_structure)
        validator.print_report()
    except Exception as e:
        print(f"❌ 文档校验失败：{e}")
    
    # 步骤 6: 生成独立报告
    print(f"\n📄 步骤 6/6: 生成填充报告...")
    
    try:
        report_generator = ReportGenerator(template_structure, match_result, user_input)
        report_path = report_generator.generate_report_path(template_path)
        report_generator.generate_report(report_path)
        print(f"   报告文件：{report_path}")
    except Exception as e:
        print(f"❌ 报告生成失败：{e}")
        report_path = None
    
    # 输出总结
    print("\n" + "=" * 50)
    print("✅ 完成！")
    print(f"\n📄 输出文件：{output_path}")
    if report_path:
        print(f"📊 填充报告：{report_path}")
    print(f"\n📊 填充置信度:")
    
    for title, conf in confidence.items():
        if conf >= 0.7:
            status = "✅"
        elif conf >= 0.4:
            status = "⚠️"
        else:
            status = "❌"
        print(f"   {status} {title}: {conf:.0%}")
    
    print("\n💡 建议：打开文档检查填充内容，特别是 ⚠️ 和 ❌ 标记的部分。")
    print("=" * 50 + "\n")
    
    # 返回输出文件路径（供调用方使用）
    return output_path, report_path


if __name__ == "__main__":
    main()
