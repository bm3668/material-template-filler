# 材料模板填充 Web 应用

基于 [material-template-filler](../material-template-filler) skill 的网页前端，**完全保留原有逻辑**，只做文件收发。

## 🚀 快速启动

### 方式 1：使用启动脚本（推荐）

```bash
cd ~/.openclaw/workspace/skills/material-template-filler/web
./start.sh
```

### 方式 2：手动启动

```bash
cd ~/.openclaw/workspace/skills/material-template-filler/web
pip3 install --user flask python-docx
python3 app.py
```

### 方式 3：独立部署

如果你是从 GitHub 克隆的独立副本：

```bash
git clone https://github.com/bm3668/material-template-filler.git
cd material-template-filler/web
./start.sh
```

---

### 访问应用

打开浏览器访问：**http://localhost:5000** （或服务器公网 IP:5000）

## ✨ 功能特性

- 📄 **模板上传** - 自动保存到 `workspace/templates/`
- 📝 **三种输入方式**：
  - 直接输入项目内容
  - 上传项目说明文件（.md/.txt/.docx）
  - 选择历史项目说明
- ⚡ **完整 Skill 逻辑** - 调用原始 material-template-filler 的所有功能
- 📊 **填充报告** - 查看详细填充状态
- 📥 **一键下载** - 从 `workspace/filled/` 下载结果

## 📖 使用流程

### 步骤 1：上传模板
- 点击上传区域
- 选择或拖拽 `.docx` 模板文件
- 文件保存到 `~/.openclaw/workspace/templates/`

### 步骤 2：提供项目内容

**方式 A：直接输入**
```
项目名称：AI 辅助学习系统
项目背景：当前在线教育平台缺乏个性化推荐...
研究目标：开发智能学习推荐系统...
团队成员：3 人
项目周期：6 个月
预算：2 万元
```

**方式 B：上传文件**
- 上传已有的项目说明文档
- 支持 .md、.txt、.docx 格式
- 文件保存到 `~/.openclaw/workspace/inputs/`

**方式 C：历史文件**
- 从列表中选择之前上传的项目说明
- 可重复使用，无需重复输入

### 步骤 3：开始填充
- 点击"🚀 开始填充"
- 调用原始 skill 的 main.py 进行处理
- 实时查看处理日志

### 步骤 4：下载结果
- 📥 下载填充后的 .docx 文件
- 📊 查看填充报告（包含置信度、填充状态等）

## 🏗️ 架构说明

```
┌─────────────────────────────────────────────────────────┐
│                    Web 前端                              │
│  - 上传模板 → /api/upload/template                      │
│  - 上传输入 → /api/upload/input                         │
│  - 执行填充 → /api/fill                                 │
│  - 下载结果 → /api/download/:filename                   │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│              Flask 后端 (app.py)                         │
│  - 文件保存到 workspace/ 目录                            │
│  - 调用原始 skill 的 main.py                             │
│  - 从 filled/ 目录提供下载                               │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│        material-template-filler skill                    │
│  - 解析模板 (template_parser.py)                        │
│  - 匹配内容 (content_matcher.py)                        │
│  - 填充文档 (docx_filler.py)                            │
│  - 生成报告 (report_generator.py)                       │
└─────────────────────────────────────────────────────────┘
```

## 📁 目录结构

```
~/.openclaw/workspace/
├── templates/              # 上传的模板文件（Web 应用）
├── inputs/                 # 项目说明文件（Web 应用）
├── filled/                 # 填充结果（原始 skill 输出）
└── skills/
    └── material-template-filler/      # 原始 skill
    └── material-template-filler-web/  # Web 应用
        ├── app.py                     # Flask 后端
        ├── templates/index.html       # 前端页面
        └── static/                    # CSS/JS
```

## 🔌 API 接口

| 端点 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 主页面 |
| `/api/upload/template` | POST | 上传模板到 `workspace/templates/` |
| `/api/upload/input` | POST | 上传项目说明到 `workspace/inputs/` |
| `/api/list-inputs` | GET | 列出历史项目说明文件 |
| `/api/fill` | POST | 执行填充（调用原始 skill） |
| `/api/download/:filename` | GET | 从 `workspace/filled/` 下载 |

## ✅ 与原始 Skill 的兼容性

| 功能 | 原始 Skill | Web 应用 | 说明 |
|------|-----------|---------|------|
| 模板解析 | ✅ | ✅ | 完全相同 |
| 内容匹配 | ✅ | ✅ | 完全相同 |
| 文档填充 | ✅ | ✅ | 完全相同 |
| 生成报告 | ✅ | ✅ | 完全相同 |
| inputs/目录 | ✅ | ✅ | Web 也使用此目录 |
| filled/输出 | ✅ | ✅ | Web 也输出到此目录 |
| 历史复用 | ✅ | ✅ | Web 支持选择历史文件 |

## ⚠️ 注意事项

1. **依赖**：需要已安装 material-template-filler skill 及其依赖
   ```bash
   pip3 install python-docx
   ```

2. **文件格式**：
   - 模板：仅支持 .docx
   - 项目说明：支持 .md、.txt、.docx

3. **文件管理**：
   - 所有文件保存在 `~/.openclaw/workspace/` 下
   - 与原始 skill 共享目录结构
   - 可在两个工具间互用文件

4. **生产部署**：
   - 建议使用反向代理（nginx）
   - 启用 HTTPS
   - 配置防火墙

## 🎨 界面预览

```
┌─────────────────────────────────────────────────────────┐
│  📋 材料模板填充                                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ① 上传模板文件                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  📄 拖拽 .docx 模板到此处                          │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ② 提供项目内容                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ [📝 直接输入] [📎 上传文件] [📂 历史文件]        │   │
│  ├─────────────────────────────────────────────────┤   │
│  │ 项目名称：xxx                                   │   │
│  │ 项目背景：xxx                                   │   │
│  │ ...                                             │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ③ 执行填充                                             │
│  ┌─────────────────────────────────────────────────┐   │
│  │            [ 🚀 开始填充 ]                       │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## 🔗 相关资源

- [material-template-filler 原技能](../material-template-filler)
- [GitHub 仓库](https://github.com/openclaw/skills/material-template-filler)
