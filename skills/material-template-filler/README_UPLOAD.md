# 材料模板填写 Skill

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-Skill-blue)](https://openclaw.ai)
[![GitHub Stars](https://img.shields.io/github/stars/bm3668/material-template-filler)](https://github.com/bm3668/material-template-filler)

智能填充各类项目申报/竞赛材料模板的 OpenClaw Skill。

## ✨ 特性

- 📋 **智能解析模板**：自动识别标题模块和表格字段
- 📝 **内容智能匹配**：基于关键词和语义将用户输入映射到对应模块
- 📄 **表格字段支持**：解析模板中的填写要求（字数限制、内容要点）
- 🤖 **LLM 扩展生成**：内容不足时自动扩展，达到字数要求
- 📊 **独立报告生成**：输出 Markdown 格式的详细填充报告
- 🔒 **隐私保护**：个人信息字段用户未提供则不填充

## 📦 安装

### 1. 克隆仓库

```bash
git clone https://github.com/bm3668/material-template-filler.git
cd material-template-filler
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置到 OpenClaw

将 skill 目录链接到 OpenClaw workspace：

```bash
ln -s /path/to/material-template-filler ~/.openclaw/workspace/skills/material-template-filler
```

## 🚀 使用

### 在 OpenClaw 对话中

```
用户：/fill-template templates/申报书.docx
用户：项目内容是：我有一个大学生创新项目...
```

### 命令行直接调用

```bash
cd scripts
python3 main.py /path/to/template.docx "项目名称：xxx。项目背景：xxx。研究目标：xxx。"
```

### 输出

生成的文件保存在 `workspace/filled/` 目录：

- `xxx_filled_YYYYMMDD_HHMMSS.docx` - 填充后的文档
- `xxx_fill_report_YYYYMMDD_HHMMSS.md` - 填充报告

## 📊 填充策略

### 个人信息字段
| 字段 | 策略 |
|------|------|
| 学校名称、团队名称 | 用户提供则填充，未提供则跳过 |
| 队长姓名、队员姓名 | 用户提供则填充，未提供则跳过 |
| 联系电话、邮箱 | 用户提供则填充，未提供则跳过 |

### 项目内容字段
| 字段 | 策略 |
|------|------|
| 摘要、设计目标 | 必须填充，根据模板要求生成 |
| 作品详情、经济社会价值 | 必须填充，根据模板要求生成 |
| 进度计划 | 必须填充，根据模板要求生成 |

## 📁 目录结构

```
material-template-filler/
├── SKILL.md                  # OpenClaw Skill 定义
├── README.md                 # 本文件
├── LICENSE                   # MIT 许可证
├── requirements.txt          # Python 依赖
├── .gitignore               # Git 忽略文件
│
├── scripts/
│   ├── main.py               # 主入口
│   ├── template_parser.py    # 模板解析器
│   ├── content_matcher.py    # 内容匹配引擎
│   ├── docx_filler.py        # docx 填充器（支持表格）
│   ├── table_parser.py       # 表格字段解析器
│   ├── report_generator.py   # 填充报告生成器
│   └── validator.py          # 格式校验器
│
├── examples/
│   └── sample_input.md       # 示例输入
│
└── tests/
    └── test_basic.py         # 基础测试
```

## 🧪 测试

```bash
# 运行基础测试
python3 tests/test_basic.py

# 运行演示
python3 scripts/demo_test.py
```

## 📝 示例

### 输入

```
项目名称：AI 辅助的个性化学习系统
项目背景：当前在线教育平台缺乏个性化推荐...
研究目标：开发一个智能学习推荐系统...
团队成员：3 人，分别负责后端、前端、算法
项目周期：6 个月
预算：2 万元
```

### 输出报告（摘要）

```markdown
# 📋 材料模板填充报告

**模板模块数**: 0
**表格字段数**: 12

## 📊 填充摘要

| 状态 | 数量 | 说明 |
|------|------|------|
| ✅ 已基于材料内容填充 | 7 | 从用户提供的材料中提取并填充 |
| ⚠️ LLM 扩展生成内容 | 5 | 内容不足，由 AI 扩展生成 |
| ❌ 未填充 | 0 | 未找到相关内容，需人工补充 |
```

## 🔧 改进历史

### v2.0 (2026-03-09)
- ✅ 新增表格字段解析，支持填写要求提取
- ✅ 新增字数限制解析，自动扩展内容达到要求
- ✅ 新增内容要点解析，根据要点逐项生成
- ✅ 优化个人信息字段处理，用户未提供则不填充
- ✅ 优化项目内容字段处理，必须填充，不足则扩展

### v1.0 (2026-03-08)
- ✅ 基础功能：模板解析、内容匹配、文档填充
- ✅ 独立报告生成
- ✅ OpenClaw 集成

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 支持

- OpenClaw 文档：https://openclaw.ai
- 问题反馈：[GitHub Issues](https://github.com/bm3668/material-template-filler/issues)
