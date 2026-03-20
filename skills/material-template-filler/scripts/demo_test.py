#!/usr/bin/env python3
"""
测试脚本 - 演示材料模板填充技能的完整功能

运行此脚本将生成示例填充文档和报告文件。
"""

import sys
import os

# 添加脚本目录到路径
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from template_parser import TemplateParser
from content_matcher import ContentMatcher
from docx_filler import DocxFiller
from report_generator import ReportGenerator

# 测试数据
TEMPLATE_PATH = os.path.expanduser("~/.openclaw/workspace/templates/template_test.docx")

TEST_INPUT = """
项目名称：5G+ 智慧校园物联网平台

项目背景：当前校园管理缺乏智能化手段，学生在生活和学习中遇到诸多不便。
我们计划开发一个基于 5G 和物联网技术的智慧校园系统，实现校园设施的智能化管理。

研究目标：
1. 实现校园设施智能管理
2. 提升学生生活体验 30% 以上
3. 降低管理成本 20%

研究内容：
- 物联网设备接入模块
- 5G 通信模块开发
- 数据分析平台建设
- 移动端应用开发

技术方案：
采用 NB-IoT 和 5G 网络作为通信基础，后端使用 Python + Django 框架，
前端使用 Vue.js，数据库使用 PostgreSQL。

创新点：
首次将 5G 网络切片技术应用于校园物联网场景，实现低延迟、高可靠的通信。

团队成员：共 5 人
- 张三：硬件开发
- 李四：后端开发
- 王五：前端开发
- 赵六：算法设计
- 钱七：测试

项目周期：12 个月

经费预算：5 万元
"""

def main():
    print("\n" + "=" * 60)
    print("📋 材料模板填充技能 - 功能演示")
    print("=" * 60)
    
    # 步骤 1: 解析模板
    print("\n🔍 步骤 1/5: 解析模板...")
    try:
        parser = TemplateParser(TEMPLATE_PATH)
        parser.parse()
        parser.print_structure()
        template_structure = parser.get_structure()
    except Exception as e:
        print(f"⚠️ 模板解析提示：{e}")
        template_structure = {
            'template_path': TEMPLATE_PATH,
            'sections': [
                {'title': '项目背景', 'level': 1, 'word_limit': 500},
                {'title': '研究目标', 'level': 1, 'word_limit': 300},
                {'title': '研究内容', 'level': 1, 'word_limit': 800},
                {'title': '技术方案', 'level': 1},
                {'title': '创新点', 'level': 1, 'word_limit': 200},
                {'title': '团队介绍', 'level': 1},
                {'title': '进度安排', 'level': 1},
                {'title': '经费预算', 'level': 1},
            ]
        }
        print("   使用预设模板结构继续...")
    
    # 步骤 2: 匹配内容
    print("\n🤖 步骤 2/5: 匹配内容到模板模块...")
    matcher = ContentMatcher(TEST_INPUT, template_structure['sections'])
    match_result = matcher.match()
    
    # 步骤 3: 填充文档
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base, _ = os.path.splitext(TEMPLATE_PATH)
    output_path = f"{base}_demo_filled_{timestamp}.docx"
    
    print(f"\n✏️  步骤 3/5: 填充文档...")
    print(f"   输出文件：{output_path}")
    
    try:
        filler = DocxFiller(TEMPLATE_PATH, output_path)
        filler.fill(match_result['matches'])
    except Exception as e:
        print(f"⚠️ 文档填充提示：{e}")
    
    # 步骤 4: 生成报告
    report_path = f"{base}_demo_fill_report_{timestamp}.md"
    print(f"\n📄 步骤 4/5: 生成填充报告...")
    print(f"   报告文件：{report_path}")
    
    try:
        report_generator = ReportGenerator(template_structure, match_result, TEST_INPUT)
        report_generator.generate_report(report_path)
    except Exception as e:
        print(f"❌ 报告生成失败：{e}")
        return 1
    
    # 输出总结
    print("\n" + "=" * 60)
    print("✅ 演示完成！")
    print("=" * 60)
    print(f"\n📄 填充文档：{output_path}")
    print(f"📊 填充报告：{report_path}")
    
    print("\n📊 填充置信度:")
    for title, conf in match_result['confidence'].items():
        if conf >= 0.7:
            status = "✅"
        elif conf >= 0.4:
            status = "⚠️"
        else:
            status = "❌"
        print(f"   {status} {title}: {conf:.0%}")
    
    print("\n💡 查看报告：")
    print(f"   cat {report_path}")
    print("\n" + "=" * 60 + "\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
