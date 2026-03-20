# 材料模板填写 Skill

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-Skill-blue)](https://openclaw.ai)

智能填充各类项目申报/竞赛材料模板，支持 **命令行** 和 **网页界面** 两种使用方式。

## 🎯 两种使用方式

### 方式 1：OpenClaw Skill（命令行/对话）
在 OpenClaw 对话中使用，适合快速填充：
```
/fill-template templates/申报书.docx
项目内容是：...
```

### 方式 2：Web 界面（浏览器）
启动本地 Web 服务，可视化操作：
```bash
cd web && pip3 install flask && python3 app.py
# 访问 http://localhost:5000
```

详见 [web/README.md](web/README.md)

## 🚀 快速开始

### 1. 安装依赖

```bash
cd ~/.openclaw/workspace/skills/material-template-filler
pip install -r requirements.txt
```

### 2. 准备模板文件

将你的 .docx 模板文件放到：
```
/home/admin/.openclaw/workspace/templates/
```

### 3. 使用

在对话中：
```
/fill-template templates/你的模板.docx
项目内容是：...
```

### 4. 查看结果

生成的文件保存在：
```
/home/admin/.openclaw/workspace/filled/
```

## 📁 目录结构

```
material-template-filler/
├── SKILL.md                  # Skill 定义（OpenClaw 集成）
├── README.md                 # 本文件
├── README_UPLOAD.md          # 上传版 README（含徽章）
├── requirements.txt          # Python 依赖
├── scripts/                  # 核心 Python 脚本
│   ├── main.py               # 主入口
│   ├── template_parser.py    # 模板解析器
│   ├── content_matcher.py    # 内容匹配引擎
│   ├── docx_filler.py        # docx 填充器
│   ├── validator.py          # 格式校验器
│   └── report_generator.py   # 填充报告生成器
├── web/                      # Web 前端界面
│   ├── app.py                # Flask 后端
│   ├── templates/index.html  # 前端页面
│   ├── static/               # CSS/JS
│   └── README.md             # Web 使用说明
├── examples/
│   └── sample_input.md       # 示例输入
└── tests/
    └── test_basic.py         # 基础测试
```

## 支持的模板类型

- 基金申请书（国自然、省部级等）
- 项目申报书（大学生创新、创业等）
- 竞赛材料（互联网 +、挑战杯等）
- 项目计划书
- 其他结构化文档

## 技术原理

1. **模板解析**：识别 docx 中的标题样式，提取模块结构
2. **内容匹配**：基于关键词和语义将用户输入映射到模块
3. **文档填充**：在模板基础上填充内容，保持原格式
4. **格式校验**：检查字数限制、完整性等

## 常见问题

### Q: 支持 .doc 格式吗？
A: 不支持。请使用 Word 另存为 .docx 格式。

### Q: 模板中有表格怎么办？
A: 表格中的占位符 `{{字段名}}` 会被自动替换。

### Q: 填充不准确怎么办？
A: 填充报告中标注了⚠️的内容建议人工检查。

## 开发者

OpenClaw Community

## 许可证

MIT
