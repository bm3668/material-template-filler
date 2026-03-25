#!/usr/bin/env python3
"""
LLM 智能内容解析器 - 用大模型解析项目说明文档，提取结构化内容
"""

import json
import os
from typing import Dict, List, Optional


class LLMContentParser:
    """使用 LLM 智能解析项目说明文档"""
    
    # 目标字段列表
    TARGET_FIELDS = [
        '摘要',
        '设计目标',
        '作品详情',
        '经济社会价值',
        '进度计划',
        '项目背景',
        '研究目标',
        '研究内容',
        '技术方案',
        '创新点',
        '预期成果',
        '经费预算',
        # 个人信息字段
        '项目名称',
        '参赛赛项',
        '学校名称',
        '团队名称',
        '联系电话',
        '邮箱',
        '指导教师',
        '队长姓名',
        '队员姓名',
    ]
    
    def __init__(self):
        self.client = None
        self._init_client()
    
    def _init_client(self):
        """初始化 DashScope 客户端"""
        try:
            import dashscope
            # API Key 从环境变量读取
            api_key = os.environ.get('DASHSCOPE_API_KEY')
            if api_key:
                dashscope.api_key = api_key
            self.client = dashscope
        except ImportError:
            print("⚠️  dashscope 未安装，LLM 解析不可用")
            self.client = None
        except Exception as e:
            print(f"⚠️  初始化 DashScope 失败：{e}")
            self.client = None
    
    def parse(self, user_input: str) -> Dict[str, str]:
        """
        使用 LLM 解析项目说明文档，提取结构化内容
        
        Args:
            user_input: 用户输入的项目说明文档
        
        Returns:
            结构化内容字典 {field_name: content}
        """
        if not self.client:
            return {}
        
        prompt = self._build_prompt(user_input)
        
        try:
            response = self.client.Generation.call(
                model='qwen-plus',
                prompt=prompt,
                temperature=0.1,  # 低温度，确保提取准确
            )
            
            if response.status_code == 200:
                result_text = response.output.text
                return self._parse_result(result_text)
            else:
                print(f"⚠️  LLM 调用失败：{response.code} - {response.message}")
                return {}
                
        except Exception as e:
            print(f"⚠️  LLM 解析异常：{e}")
            return {}
    
    def _build_prompt(self, user_input: str) -> str:
        """构建 LLM 提示词"""
        
        # 截断过长的输入（避免 token 超限）
        max_input_length = 15000
        if len(user_input) > max_input_length:
            user_input = user_input[:max_input_length] + "...（内容截断）"
        
        fields_json = json.dumps(self.TARGET_FIELDS, ensure_ascii=False)
        
        prompt = f"""你是一个智能文档解析助手。请从以下项目说明文档中提取指定字段的内容。

## 任务要求
1. 仔细阅读项目说明文档
2. 识别并提取以下字段的内容
3. 保持原文内容，不要修改或扩展
4. 如果某个字段没有找到内容，返回空字符串
5. 输出必须是严格的 JSON 格式

## 目标字段
{fields_json}

## 项目说明文档
{user_input}

## 输出格式
请输出严格的 JSON 格式，如下所示：
{{
    "摘要": "提取的内容或空字符串",
    "设计目标": "提取的内容或空字符串",
    "作品详情": "提取的内容或空字符串",
    ...
}}

## 注意事项
- 每个字段的内容应该是完整的段落，不要截断
- 如果文档中有多个相关段落，合并它们
- 个人信息字段（如学校名称、联系电话等）只提取明确给出的信息
- 不要添加原文中没有的内容

现在请开始解析，只输出 JSON，不要有其他文字。"""
        
        return prompt
    
    def _parse_result(self, result_text: str) -> Dict[str, str]:
        """解析 LLM 返回的结果"""
        try:
            # 清理可能的 markdown 标记
            result_text = result_text.strip()
            if result_text.startswith('```json'):
                result_text = result_text[7:]
            if result_text.endswith('```'):
                result_text = result_text[:-3]
            result_text = result_text.strip()
            
            result = json.loads(result_text)
            return result
        except json.JSONDecodeError as e:
            print(f"⚠️  解析 LLM 返回结果失败：{e}")
            print(f"返回内容：{result_text[:500]}...")
            return {}


def main():
    """测试"""
    test_input = """
    项目名称：AI 辅助学习系统
    项目背景：当前在线教育缺乏个性化推荐。
    设计目标：开发智能学习推荐系统，提高效率 30%。
    技术方案：使用机器学习和 TensorFlow。
    创新点：首次将强化学习应用于学习路径。
    进度计划：第一阶段需求分析，第二阶段开发，第三阶段测试。
    """
    
    parser = LLMContentParser()
    result = parser.parse(test_input)
    
    print("解析结果:")
    for field, content in result.items():
        if content:
            print(f"  {field}: {content[:50]}...")


if __name__ == "__main__":
    main()
