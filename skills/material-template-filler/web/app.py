#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
材料模板填充 Web 应用 - Flask 后端服务器
完全使用 material-template-filler skill 的原有逻辑和目录结构

支持三种部署模式：
1. 独立部署：web/ 目录放在 skill 根目录下，使用相对路径
2. OpenClaw 部署：自动检测 ~/.openclaw/workspace
3. 自定义：通过环境变量指定路径
"""

import os
import sys
import json
import uuid
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify, send_file, render_template
from werkzeug.utils import secure_filename

app = Flask(__name__)

# 配置
PORT = int(os.environ.get('PORT', 5000))
MAX_UPLOAD_SIZE = int(os.environ.get('MAX_UPLOAD_SIZE', 50)) * 1024 * 1024

# ============ 路径配置（优先级：环境变量 > 相对路径 > OpenClaw 默认路径）============

def detect_paths():
    """自动检测并配置路径"""
    
    # 1. 优先使用环境变量
    if os.environ.get('WORKSPACE_DIR'):
        print("📍 使用环境变量配置的路径")
        workspace = Path(os.environ['WORKSPACE_DIR'])
        templates = Path(os.environ.get('TEMPLATES_DIR', workspace / 'templates'))
        inputs = Path(os.environ.get('INPUTS_DIR', workspace / 'inputs'))
        filled = Path(os.environ.get('FILLED_DIR', workspace / 'filled'))
        skill_scripts = Path(os.environ.get('SKILL_SCRIPTS_DIR', workspace / 'skills' / 'material-template-filler' / 'scripts'))
        return workspace, templates, inputs, filled, skill_scripts
    
    # 2. 尝试相对路径（web/ 在 skill 根目录下）
    web_dir = Path(__file__).parent
    skill_root = web_dir.parent
    if (skill_root / 'scripts' / 'main.py').exists():
        print("📍 使用相对路径（独立部署模式）")
        # 独立部署：在 skill 目录下创建 workspace
        workspace = skill_root / 'workspace'
        templates = workspace / 'templates'
        inputs = workspace / 'inputs'
        filled = workspace / 'filled'
        skill_scripts = skill_root / 'scripts'
        return workspace, templates, inputs, filled, skill_scripts
    
    # 3. 回退到 OpenClaw 默认路径
    print("📍 使用 OpenClaw 默认路径")
    workspace = Path.home() / '.openclaw' / 'workspace'
    templates = workspace / 'templates'
    inputs = workspace / 'inputs'
    filled = workspace / 'filled'
    skill_scripts = workspace / 'skills' / 'material-template-filler' / 'scripts'
    return workspace, templates, inputs, filled, skill_scripts


WORKSPACE, TEMPLATES_DIR, INPUTS_DIR, FILLED_DIR, SKILL_DIR = detect_paths()
SKILL_MAIN = SKILL_DIR / 'main.py'

# 确保目录存在
for dir_path in [TEMPLATES_DIR, INPUTS_DIR, FILLED_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# 验证 skill 主程序存在
if not SKILL_MAIN.exists():
    print(f"⚠️  警告：未找到 skill 主程序 {SKILL_MAIN}")
    print("   请确保 material-template-filler skill 已正确安装")

app.config['MAX_CONTENT_LENGTH'] = MAX_UPLOAD_SIZE

# 允许的文件扩展名
ALLOWED_TEMPLATE_EXTENSIONS = {'docx'}
ALLOWED_INPUT_EXTENSIONS = {'md', 'txt', 'docx'}


def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def generate_timestamp():
    return datetime.now().strftime('%Y%m%d_%H%M%S')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/upload/template', methods=['POST'])
def upload_template():
    """上传模板文件到 workspace/templates/"""
    if 'file' not in request.files:
        return jsonify({'error': '没有文件上传'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    if not allowed_file(file.filename, ALLOWED_TEMPLATE_EXTENSIONS):
        return jsonify({'error': '只支持 .docx 格式的模板文件'}), 400
    
    timestamp = generate_timestamp()
    safe_filename = secure_filename(file.filename)
    save_path = TEMPLATES_DIR / f"{timestamp}_{safe_filename}"
    
    file.save(save_path)
    
    return jsonify({
        'success': True,
        'filename': safe_filename,
        'path': str(save_path)
    })


@app.route('/api/upload/input', methods=['POST'])
def upload_input():
    """上传项目说明文件到 workspace/inputs/"""
    if 'file' not in request.files:
        return jsonify({'error': '没有文件上传'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    if not allowed_file(file.filename, ALLOWED_INPUT_EXTENSIONS):
        return jsonify({'error': '只支持 .md, .txt, .docx 格式'}), 400
    
    timestamp = generate_timestamp()
    safe_filename = secure_filename(file.filename)
    name, ext = os.path.splitext(safe_filename)
    save_path = INPUTS_DIR / f"{name}_{timestamp}{ext}"
    
    file.save(save_path)
    
    return jsonify({
        'success': True,
        'filename': save_path.name,
        'path': str(save_path)
    })


@app.route('/api/list-inputs', methods=['GET'])
def list_inputs():
    """列出历史项目说明文件"""
    files = []
    for f in sorted(INPUTS_DIR.glob('*'), key=lambda x: x.stat().st_mtime, reverse=True):
        if f.is_file() and f.suffix in ['.md', '.txt', '.docx']:
            files.append({
                'name': f.name,
                'path': str(f),
                'size': f.stat().st_size,
                'mtime': datetime.fromtimestamp(f.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
            })
    return jsonify({'files': files})


@app.route('/api/fill', methods=['POST'])
def fill_template():
    """执行模板填充 - 完全使用原始 skill 逻辑"""
    data = request.json
    
    template_path = data.get('template_path')
    input_path = data.get('input_path')  # 项目说明文件路径
    content = data.get('content', '')    # 或直接输入的内容
    
    if not template_path or not Path(template_path).exists():
        return jsonify({'error': '模板文件不存在'}), 400
    
    # 确定输入内容
    user_input = ''
    
    if input_path and Path(input_path).exists():
        # 使用上传的项目说明文件 - 读取文件内容
        try:
            ext = Path(input_path).suffix.lower()
            if ext in ['.md', '.txt']:
                with open(input_path, 'r', encoding='utf-8') as f:
                    user_input = f.read()
            elif ext == '.docx':
                # 读取 docx 文件内容
                from docx import Document
                doc = Document(input_path)
                user_input = '\n'.join([p.text for p in doc.paragraphs if p.text.strip()])
            else:
                return jsonify({'error': '不支持的文件格式'}), 400
        except Exception as e:
            return jsonify({'error': f'读取文件失败：{str(e)}'}), 500
    elif content.strip():
        # 使用直接输入的内容，保存到 inputs/
        timestamp = generate_timestamp()
        # 尝试提取项目名称作为文件名
        project_name = "项目说明"
        for line in content.split('\n'):
            if '项目名称' in line and ':' in line:
                project_name = line.split(':')[1].strip()
                break
        input_path = INPUTS_DIR / f"{project_name}_{timestamp}.md"
        with open(input_path, 'w', encoding='utf-8') as f:
            f.write(content)
        user_input = content
    else:
        return jsonify({'error': '请提供项目内容或上传项目说明文件'}), 400
    
    # 调用原始 skill 的 main.py
    try:
        cmd = [
            sys.executable, str(SKILL_MAIN),
            template_path,
            user_input
        ]
        
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            timeout=300,
            cwd=str(SKILL_DIR)
        )
        
        if result.returncode != 0:
            return jsonify({
                'error': '填充失败',
                'details': result.stderr
            }), 500
        
        # 查找最新生成的文件
        filled_files = list(FILLED_DIR.glob('*_filled_*.docx'))
        report_files = list(FILLED_DIR.glob('*_fill_report_*.md'))
        
        if not filled_files:
            return jsonify({'error': '未生成输出文件'}), 500
        
        # 获取最新的文件
        output_file = max(filled_files, key=lambda x: x.stat().st_mtime)
        report_file = max(report_files, key=lambda x: x.stat().st_mtime) if report_files else None
        
        # 读取报告内容
        report_content = ''
        if report_file and report_file.exists():
            with open(report_file, 'r', encoding='utf-8') as f:
                report_content = f.read()
        
        return jsonify({
            'success': True,
            'output_filename': output_file.name,
            'report_filename': report_file.name if report_file else None,
            'report_content': report_content,
            'log': result.stdout
        })
        
    except subprocess.TimeoutExpired:
        return jsonify({'error': '处理超时，请重试'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/download/<filename>')
def download_file(filename):
    """从 filled/ 目录下载文件"""
    file_path = FILLED_DIR / filename
    
    if not file_path.exists():
        return jsonify({'error': '文件不存在'}), 404
    
    return send_file(
        file_path,
        as_attachment=True,
        download_name=filename
    )


if __name__ == '__main__':
    print(f"🚀 材料模板填充 Web 应用启动中...")
    print(f"📂 工作目录：{WORKSPACE}")
    print(f"📁 模板目录：{TEMPLATES_DIR}")
    print(f"📁 项目说明目录：{INPUTS_DIR}")
    print(f"📁 输出目录：{FILLED_DIR}")
    print(f"🌐 访问地址：http://localhost:{PORT}")
    app.run(host='0.0.0.0', port=PORT, debug=False)
