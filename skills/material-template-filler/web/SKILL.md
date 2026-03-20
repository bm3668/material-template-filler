---
name: material-template-filler-web
description: 网页前端版材料模板填充。对话式界面，支持附件上传，填充完成后直接下载文件。
emoji: 🌐
requires:
  bins: [python3, pip]
metadata: {"openclaw":{"requires":{"config":{"env":{"PYTHON_PATH":{"description":"Python 路径","default":"python3"}}}}}}
---

# 材料模板填充 Web 应用

基于现有 material-template-filler skill 的网页前端版本。

## 启动方式

```bash
cd ~/.openclaw/workspace/skills/material-template-filler-web
python3 app.py
```

默认访问：http://localhost:5000

## 功能特性

- 📄 **模板上传**：拖拽或点击上传 .docx 模板文件
- 💬 **对话式输入**：像聊天一样提供项目内容
- 📎 **附件支持**：可上传多个参考文档
- ⚡ **实时填充**：调用后端 skill 进行智能填充
- 📥 **一键下载**：填充完成后直接下载结果文件
- 📊 **填充报告**：查看详细的填充状态报告

## 界面预览

```
┌─────────────────────────────────────────────────────────┐
│  📋 材料模板填充 Web 应用                                  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────┐  ┌─────────────┐                       │
│  │ 上传模板    │  │ 上传附件    │                       │
│  │ 📄.docx     │  │ 📎.md/.txt  │                       │
│  └─────────────┘  └─────────────┘                       │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ 💬 请输入项目内容...                             │   │
│  │                                                 │   │
│  │                                                 │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│                    [ 开始填充 ]                         │
│                                                         │
│  ───────────────────────────────────────────────────    │
│                                                         │
│  对话历史：                                             │
│  👤 用户：上传了 template.docx                          │
│  🤖 AI：收到模板，请输入项目内容...                      │
│  👤 用户：项目名称：AI 学习系统...                        │
│  🤖 AI：正在填充... ✅ 完成！[下载] [查看报告]           │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## 目录结构

```
material-template-filler-web/
├── SKILL.md              # 本文件
├── app.py                # Flask 后端服务器
├── requirements.txt      # Python 依赖
├── static/
│   ├── style.css         # 样式文件
│   └── script.js         # 前端交互逻辑
├── templates/
│   └── index.html        # 主页面
└── uploads/              # 临时上传目录（自动创建）
    ├── templates/        # 上传的模板
    ├── attachments/      # 上传的附件
    └── outputs/          # 填充结果
```

## API 接口

| 端点 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 主页面 |
| `/api/upload/template` | POST | 上传模板文件 |
| `/api/upload/attachment` | POST | 上传附件 |
| `/api/fill` | POST | 执行填充 |
| `/api/download/:filename` | GET | 下载结果文件 |
| `/api/status/:taskId` | GET | 查询任务状态 |

## 依赖安装

```bash
cd ~/.openclaw/workspace/skills/material-template-filler-web
pip install -r requirements.txt
```

## 使用流程

1. **启动服务**
   ```bash
   python3 app.py
   ```

2. **访问页面**
   打开浏览器访问 http://localhost:5000

3. **上传模板**
   - 点击"上传模板"按钮
   - 或拖拽 .docx 文件到上传区域

4. **输入项目内容**
   - 在对话框中输入项目信息
   - 或上传参考文档（.md/.txt/.docx）

5. **执行填充**
   - 点击"开始填充"按钮
   - 等待处理完成

6. **下载结果**
   - 点击"下载"按钮获取填充后的文档
   - 点击"查看报告"查看填充详情

## 配置选项

在 `app.py` 中可配置：

```python
# 服务端口
PORT = 5000

# 上传文件大小限制（MB）
MAX_UPLOAD_SIZE = 50

# 临时文件保留时间（小时）
FILE_RETENTION_HOURS = 24

# 调用的 skill 路径
SKILL_PATH = "../material-template-filler/scripts/main.py"
```

## 注意事项

- 需要已安装 material-template-filler skill 及其依赖
- 上传的文件会临时保存在 `uploads/` 目录
- 定期清理 `uploads/` 目录避免占用过多空间
- 建议在生产环境中使用反向代理（nginx）和 HTTPS
