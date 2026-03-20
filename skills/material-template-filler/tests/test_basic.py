#!/usr/bin/env python3
"""
基础测试脚本
"""

import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
scripts_dir = os.path.join(script_dir, '..', 'scripts')
sys.path.insert(0, scripts_dir)

from template_parser import TemplateParser
from content_matcher import ContentMatcher


def test_content_matcher():
    """测试内容匹配器"""
    print("🧪 测试内容匹配器...\n")
    
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
    print("-" * 50)
    for title, content in result['matches'].items():
        conf = result['confidence'][title]
        status = "✅" if conf >= 0.7 else "⚠️" if conf >= 0.4 else "❌"
        print(f"{status} {title}: {conf:.0%}")
        print(f"   内容：{content[:60]}...")
        print()
    
    print("-" * 50)
    print("✅ 内容匹配器测试完成\n")
    return True


def test_template_parser():
    """测试模板解析器（需要实际模板文件）"""
    print("🧪 测试模板解析器...\n")
    
    # 检查是否有测试模板
    test_template = os.path.join(script_dir, "..", "examples", "test_template.docx")
    if os.path.exists(test_template):
        try:
            parser = TemplateParser(test_template)
            parser.parse()
            parser.print_structure()
            print("✅ 模板解析器测试完成\n")
            return True
        except Exception as e:
            print(f"⚠️ 模板解析测试跳过：{e}\n")
            return False
    else:
        print(f"⚠️ 测试模板不存在，跳过测试：{test_template}\n")
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("材料模板填写 Skill - 基础测试")
    print("=" * 50)
    print()
    
    test_content_matcher()
    test_template_parser()
    
    print("=" * 50)
    print("所有测试完成！")
    print("=" * 50)
