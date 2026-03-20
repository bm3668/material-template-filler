#!/usr/bin/env python3
"""
模板解析器 - 识别 docx 模板的结构和各模块要求
"""

from docx import Document
import re
import json
import sys
import os

class TemplateParser:
    def __init__(self, template_path: str):
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"模板文件不存在：{template_path}")
        self.template_path = template_path
        self.doc = Document(template_path)
        self.sections = []
        
    def parse(self) -> list:
        """解析模板，识别各模块"""
        sections = []
        current_section = None
        
        for para in self.doc.paragraphs:
            text = para.text.strip()
            style = para.style.name
            
            # 识别标题（模块名）
            if style.startswith('Heading'):
                if current_section:
                    sections.append(current_section)
                current_section = {
                    'title': text,
                    'level': int(style[-1]) if style[-1].isdigit() else 1,
                    'requirements': self._extract_requirements(text),
                    'content': '',
                    'word_limit': self._extract_word_limit(text)
                }
            # 识别表格（字段）
            elif current_section and text:
                current_section['content'] += text + '\n'
                
        if current_section:
            sections.append(current_section)
            
        self.sections = sections
        return sections
    
    def _extract_requirements(self, text: str) -> str:
        """从模块标题/说明中提取填写要求"""
        patterns = [
            r'[（(]限？(\d+)[字字以内][)）]',
            r'请 [描述说明填写].*?[。：:]',
        ]
        requirements = []
        for p in patterns:
            match = re.search(p, text)
            if match:
                requirements.append(match.group(0))
        return ' '.join(requirements)
    
    def _extract_word_limit(self, text: str) -> int:
        """提取字数限制"""
        match = re.search(r'[（(]限？(\d+)[字字以内][)）]', text)
        return int(match.group(1)) if match else None
    
    def get_structure(self) -> dict:
        """返回模板结构"""
        return {
            'template_path': self.template_path,
            'total_sections': len(self.sections),
            'sections': [
                {
                    'title': s['title'],
                    'level': s['level'],
                    'word_limit': s['word_limit'],
                    'requirements': s['requirements']
                }
                for s in self.sections
            ]
        }
    
    def print_structure(self):
        """打印模板结构"""
        print(f"\n📋 模板结构：{self.template_path}")
        print(f"   共 {len(self.sections)} 个模块\n")
        for i, section in enumerate(self.sections, 1):
            limit = f" (限{section['word_limit']}字)" if section['word_limit'] else ""
            print(f"   {i}. {section['title']}{limit}")


def main():
    if len(sys.argv) < 2:
        print("用法：python template_parser.py <模板文件路径>")
        sys.exit(1)
    
    template_path = sys.argv[1]
    
    try:
        parser = TemplateParser(template_path)
        parser.parse()
        parser.print_structure()
        
        # 输出 JSON 结构
        print("\n📄 JSON 结构:")
        print(json.dumps(parser.get_structure(), ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(f"❌ 错误：{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
