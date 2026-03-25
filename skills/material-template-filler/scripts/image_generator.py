#!/usr/bin/env python3
"""
图片生成模块 - 支持从 Mermaid/DOT 生成流程图、思维导图等图片

功能：
1. 从 Mermaid 文本生成 PNG（通过 step 工具）
2. 从 DOT 文件生成 PNG（通过 Graphviz）
3. 支持多种图表类型：flowchart, mindmap, pyramid
"""

import os
import subprocess
import tempfile
import shutil
from pathlib import Path


class MermaidGenerator:
    """
    Mermaid 图表生成器 - 使用 step 工具生成 Mermaid 图表
    """
    
    def __init__(self, step_dir: str = None):
        """
        Args:
            step_dir: step 工具的安装目录（可选，默认使用系统安装的 paper-insight）
        """
        self.step_dir = step_dir
        self.paper_insight_cmd = self._find_paper_insight()
    
    def _find_paper_insight(self) -> str:
        """查找 paper-insight 命令"""
        # 优先使用 step_dir 中的脚本
        if self.step_dir:
            script_path = os.path.join(self.step_dir, 'scripts', 'paper_insight.py')
            if os.path.exists(script_path):
                return f'python {script_path}'
        
        # 尝试使用系统安装的命令
        return 'paper-insight'
    
    def generate_from_text(self, text: str, diagram_type: str = 'mindmap', 
                          output_path: str = None) -> str:
        """
        从文本生成图表
        
        Args:
            text: 要分析的文本内容
            diagram_type: 图表类型 (flowchart, mindmap, pyramid)
            output_path: 输出图片路径（可选）
            
        Returns:
            生成的 PNG 文件路径
        """
        # 创建临时目录
        with tempfile.TemporaryDirectory() as tmpdir:
            # 写入临时文件
            input_file = os.path.join(tmpdir, 'input.txt')
            with open(input_file, 'w', encoding='utf-8') as f:
                f.write(text)
            
            # 调用 paper-insight 生成 Mermaid
            mmd_file = os.path.join(tmpdir, 'framework.mmd')
            cmd = f'{self.paper_insight_cmd} --input "{input_file}" --provider local --diagram-type {diagram_type} --output-dir "{tmpdir}"'
            
            try:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"⚠️ paper-insight 执行失败：{result.stderr}")
                    # 如果失败，尝试使用 mock provider
                    cmd = f'{self.paper_insight_cmd} --input "{input_file}" --provider mock --diagram-type {diagram_type} --output-dir "{tmpdir}"'
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            except Exception as e:
                print(f"⚠️ 调用 paper-insight 失败：{e}")
                return None
            
            # 读取生成的 Mermaid 文件
            if not os.path.exists(mmd_file):
                print(f"⚠️ 未找到生成的 Mermaid 文件：{mmd_file}")
                return None
            
            with open(mmd_file, 'r', encoding='utf-8') as f:
                mermaid_content = f.read()
            
            # 将 Mermaid 转换为 PNG
            return self.mermaid_to_png(mermaid_content, output_path)
    
    def mermaid_to_png(self, mermaid_content: str, output_path: str = None) -> str:
        """
        将 Mermaid 文本转换为 PNG
        
        方法：
        1. 使用 mermaid-cli (mmdc) 如果已安装
        2. 使用在线 API（备用方案）
        
        Args:
            mermaid_content: Mermaid 格式的图表定义
            output_path: 输出 PNG 路径（可选）
            
        Returns:
            生成的 PNG 文件路径
        """
        if output_path is None:
            output_path = f'mindmap_{os.getpid()}.png'
        
        # 尝试使用 mermaid-cli
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False) as f:
                f.write(mermaid_content)
                temp_mmd = f.name
            
            cmd = f'mmdc -i "{temp_mmd}" -o "{output_path}" -b transparent'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            # 清理临时文件
            os.unlink(temp_mmd)
            
            if result.returncode == 0 and os.path.exists(output_path):
                print(f"✅ Mermaid 图表已生成：{output_path}")
                return output_path
        except Exception as e:
            print(f"⚠️ mmdc 不可用，尝试备用方案：{e}")
        
        # 备用方案：返回 Mermaid 内容，让用户手动转换
        print(f"⚠️ 无法直接生成 PNG，已保存 Mermaid 文件")
        mmd_path = output_path.replace('.png', '.mmd')
        with open(mmd_path, 'w', encoding='utf-8') as f:
            f.write(mermaid_content)
        return mmd_path


class DotGenerator:
    """
    DOT 文件生成器 - 使用 Graphviz 生成 PNG
    """
    
    def __init__(self):
        self.dot_cmd = self._find_dot()
    
    def _find_dot(self) -> str:
        """查找 dot 命令"""
        # 检查是否在 PATH 中
        try:
            result = subprocess.run(['which', 'dot'], capture_output=True, text=True)
            if result.returncode == 0:
                return 'dot'
        except:
            pass
        
        # 常见安装路径
        common_paths = [
            '/usr/bin/dot',
            '/usr/local/bin/dot',
            'C:\\Program Files\\Graphviz\\bin\\dot.exe',
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                return path
        
        return 'dot'  # 假设在 PATH 中
    
    def generate_from_mermaid(self, mermaid_content: str, output_path: str = None) -> str:
        """
        从 Mermaid 内容生成 PNG（先转换为 DOT）
        
        Args:
            mermaid_content: Mermaid 格式的图表定义
            output_path: 输出 PNG 路径（可选）
            
        Returns:
            生成的 PNG 文件路径
        """
        # 将 Mermaid 转换为 DOT
        dot_content = self._mermaid_to_dot(mermaid_content)
        
        # 从 DOT 生成 PNG
        return self.dot_to_png(dot_content, output_path)
    
    def _mermaid_to_dot(self, mermaid_content: str) -> str:
        """
        将 Mermaid 转换为 DOT 格式
        
        这是一个简化实现，只支持 mindmap 类型
        """
        dot_lines = [
            "digraph mindmap {",
            "  rankdir=LR;",
            "  node [shape=box, style=rounded, fontname=\"Arial\"];",
            "  edge [fontname=\"Arial\"];",
        ]
        
        # 解析 Mermaid mindmap
        lines = [l.strip() for l in mermaid_content.strip().split('\n') 
                 if l.strip() and not l.strip().startswith('mindmap') and not l.strip().startswith('```')]
        
        current_parent = "root"
        parent_stack = [("root", -1)]
        
        for line in lines:
            if line.startswith('root('):
                # 提取根节点标签
                label = line[5:-2] if line.endswith('))') else line[5:-1]
                dot_lines.append(f'  root [label="{label}", shape=ellipse, style=filled, fillcolor=lightblue, fontsize=16];')
                continue
            
            indent = len(line) - len(line.lstrip())
            label = line.strip()
            
            # 弹出栈直到找到正确的父节点
            while parent_stack and parent_stack[-1][1] >= indent:
                parent_stack.pop()
            
            if parent_stack:
                current_parent = parent_stack[-1][0]
            
            # 创建节点 ID
            node_id = label.replace(' ', '_').replace('(', '').replace(')', '').replace('/', '_')
            
            # 添加节点
            dot_lines.append(f'  {node_id} [label="{label}"];')
            
            # 添加边
            dot_lines.append(f'  {current_parent} -> {node_id};')
            
            parent_stack.append((node_id, indent))
        
        dot_lines.append("}")
        return '\n'.join(dot_lines)
    
    def dot_to_png(self, dot_content: str, output_path: str = None) -> str:
        """
        从 DOT 内容生成 PNG
        
        Args:
            dot_content: DOT 格式的图表定义
            output_path: 输出 PNG 路径（可选）
            
        Returns:
            生成的 PNG 文件路径
        """
        if output_path is None:
            output_path = f'mindmap_{os.getpid()}.png'
        
        # 写入临时 DOT 文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.dot', delete=False) as f:
            f.write(dot_content)
            temp_dot = f.name
        
        try:
            # 调用 dot 命令生成 PNG
            cmd = f'{self.dot_cmd} -Tpng "{temp_dot}" -o "{output_path}"'
            result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            
            if result.returncode == 0:
                print(f"✅ PNG 已生成：{output_path}")
                return output_path
            else:
                print(f"❌ dot 命令失败：{result.stderr}")
                return None
        except Exception as e:
            print(f"❌ 生成 PNG 失败：{e}")
            return None
        finally:
            # 清理临时文件
            if os.path.exists(temp_dot):
                os.unlink(temp_dot)


class ImageGenerator:
    """
    统一的图片生成器 - 整合 MermaidGenerator 和 DotGenerator
    """
    
    def __init__(self, step_dir: str = None):
        self.mermaid_gen = MermaidGenerator(step_dir)
        self.dot_gen = DotGenerator()
    
    def generate_mindmap(self, mermaid_content: str, output_path: str = None, 
                        method: str = 'dot') -> str:
        """
        生成思维导图
        
        Args:
            mermaid_content: Mermaid 格式的思维导图定义
            output_path: 输出 PNG 路径
            method: 生成方法 ('dot' 或 'mermaid')
            
        Returns:
            生成的 PNG 文件路径
        """
        if method == 'dot':
            return self.dot_gen.generate_from_mermaid(mermaid_content, output_path)
        else:
            return self.mermaid_gen.mermaid_to_png(mermaid_content, output_path)
    
    def generate_from_text(self, text: str, diagram_type: str = 'mindmap',
                          output_path: str = None) -> str:
        """
        从文本生成图表
        
        Args:
            text: 要分析的文本
            diagram_type: 图表类型 (flowchart, mindmap, pyramid)
            output_path: 输出 PNG 路径
            
        Returns:
            生成的 PNG 文件路径
        """
        return self.mermaid_gen.generate_from_text(text, diagram_type, output_path)


# 便捷函数
def generate_mindmap_png(mermaid_content: str, output_path: str = None) -> str:
    """快速生成思维导图 PNG"""
    gen = ImageGenerator()
    return gen.generate_mindmap(mermaid_content, output_path)


if __name__ == '__main__':
    # 测试
    test_mermaid = """
mindmap
  root((测试主题))
    分支 1
      子节点 1
      子节点 2
    分支 2
      子节点 3
"""
    
    output = generate_mindmap_png(test_mermaid, 'test_mindmap.png')
    print(f"生成结果：{output}")
