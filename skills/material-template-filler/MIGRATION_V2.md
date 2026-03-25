# DocxFiller V2 迁移指南

## 📋 概述

DocxFiller V2 是基于 Anthropic docx skill 最佳实践重构的专业级文档填充引擎，相比 V1 有以下改进：

### 主要改进

| 改进点 | V1 | V2 | 说明 |
|--------|-----|-----|------|
| **页面设置** | 使用模板默认 | 标准化 A4/边距 | 支持 A4/Letter 等纸张尺寸，标准 1 英寸边距 |
| **样式管理** | 无样式覆盖 | 专业样式系统 | 统一标题/正文字体、字号、行距 |
| **字体兼容** | 仅设置英文字体 | 中英文字体映射 | 支持 Windows/macOS/Linux 多平台 |
| **表格样式** | 无样式 | Table Grid 默认 | 自动应用表格样式 |
| **文档验证** | 无验证 | ZIP/XML 验证 | 生成后验证.docx 合法性 |
| **填充报告** | 简单报告 | 详细报告数据 | 结构化存储填充状态、置信度 |
| **占位符支持** | 基础支持 | 增强模糊匹配 | 支持 `{{field_name}}` 占位符 |

---

## 🚀 快速开始

### 方式 1：直接使用 V2

```python
from docx_filler_v2 import DocxFillerV2

# 创建填充器
filler = DocxFillerV2(
    template_path='templates/申报书.docx',
    output_path='filled/申报书_filled.docx'
)

# 填充内容
content_map = {
    '项目背景': '当前在线教育平台缺乏个性化推荐...',
    '研究目标': '开发一个智能学习推荐系统...',
    '研究内容': '包括用户行为分析、内容推荐算法...',
}

report_data = filler.fill(content_map)

# 添加填充报告
filler.add_fill_report()

print(f"✅ 填充完成：{filler.get_output_info()}")
```

### 方式 2：运行验证脚本

```bash
cd ~/.openclaw/workspace/skills/material-template-filler/scripts
python test_v2.py
```

这将对比 V1 和 V2 的填充效果，验证改进点。

---

## 📦 API 变更

### DocxFillerV2 类

```python
class DocxFillerV2:
    def __init__(self, template_path: str, output_path: str):
        """
        初始化填充器
        
        Args:
            template_path: 模板文件路径
            output_path: 输出文件路径
        """
    
    def fill(self, content_map: dict, auto_detect_paper_size=True) -> dict:
        """
        填充内容到文档
        
        Args:
            content_map: 内容字典 {模块标题：内容}
            auto_detect_paper_size: 是否自动检测纸张尺寸
            
        Returns:
            填充报告数据 {
                'sections': {标题：{status, word_count, confidence}},
                'tables': [{field, status, word_count, confidence}],
                'personal_info_missing': [{field, reason}]
            }
        """
    
    def add_fill_report(self, report_data: dict = None) -> None:
        """
        在文档末尾添加填充报告
        
        Args:
            report_data: 填充报告数据（可选，默认使用内部数据）
        """
    
    def get_output_info(self) -> dict:
        """
        返回输出文件信息
        
        Returns:
            {
                'output_path': str,
                'template_path': str,
                'file_size': int,
                'page_count': int
            }
        """
```

### 与 V1 的兼容性

| 方法 | V1 | V2 | 兼容性 |
|------|-----|-----|--------|
| `__init__` | ✅ | ✅ | 完全兼容 |
| `fill` | ✅ | ✅ | 返回值变更（V2 返回报告数据） |
| `add_fill_report` | ✅ | ✅ | 参数变更（V2 接受报告数据） |
| `get_output_info` | ✅ | ✅ | 完全兼容 |

---

## 🔧 高级功能

### 1. 自定义页面设置

```python
from docx_filler_v2 import DocxFillerV2, PageSetupManager

filler = DocxFillerV2(template_path, output_path)

# 手动设置页面（在 fill 之前调用）
filler.page_manager.setup_page(
    paper_size='A4',          # A4, A3, Letter, Legal
    orientation='portrait',   # portrait (纵向) 或 landscape (横向)
    margin_style='normal'     # normal, narrow, wide
)

filler.fill(content_map)
```

### 2. 自定义样式

```python
from docx_filler_v2 import DocxFillerV2, StyleManager

filler = DocxFillerV2(template_path, output_path)

# 应用自定义样式（在 fill 之前调用）
filler.style_manager.apply_professional_styles()

# 可以扩展 StyleManager 添加自定义样式
```

### 3. 文档验证

```python
from docx_filler_v2 import DocxValidator

validator = DocxValidator('filled/申报书_filled.docx')
result = validator.validate()

if result['valid']:
    print("✅ 文档验证通过")
else:
    print(f"❌ 文档验证失败：{result['errors']}")
    print(f"⚠️ 警告：{result['warnings']}")
```

### 4. 获取填充报告数据

```python
filler = DocxFillerV2(template_path, output_path)
report_data = filler.fill(content_map)

# 分析填充情况
sections = report_data.get('sections', {})
filled_count = sum(1 for s in sections.values() if s.get('status') == 'filled')
empty_count = sum(1 for s in sections.values() if s.get('status') == 'empty')

print(f"填充率：{filled_count / len(sections) * 100:.1f}%")
print(f"缺失模块：{empty_count}个")

# 检查缺失的个人信息
missing = report_data.get('personal_info_missing', [])
for item in missing:
    print(f"  - {item['field']}: {item['reason']}")
```

---

## 📊 性能对比

基于测试模板的对比结果（示例）：

| 指标 | V1 | V2 | 变化 |
|------|-----|-----|------|
| 填充时间 | 0.15 秒 | 0.18 秒 | +20% |
| 文件大小 | 45KB | 47KB | +4% |
| 文档验证 | ❌ 不支持 | ✅ 通过 | - |
| 样式一致性 | ⚠️ 依赖模板 | ✅ 统一 | - |

V2 增加了样式管理和文档验证，性能略有下降（约 20%），但显著提升了文档质量和可靠性。

---

## ⚠️ 注意事项

### 1. 依赖要求

V2 需要以下依赖（与 V1 相同）：

```bash
pip install python-docx
```

### 2. 字体兼容性

V2 使用以下字体映射：

| 用途 | 英文字体 | 中文字体 |
|------|----------|----------|
| 标题 | Arial Black | 黑体 |
| 正文 | Arial | 宋体 |

如果系统缺少这些字体，Word 会自动使用替代字体。

### 3. 向后兼容

V2 设计为与 V1 向后兼容：

- 旧的调用方式仍然有效
- 模板文件格式不变
- 输出文件格式不变

但建议更新代码以使用 V2 的新功能（如填充报告数据）。

---

## 🔄 迁移步骤

### 步骤 1：安装依赖

```bash
cd ~/.openclaw/workspace/skills/material-template-filler
pip install -r requirements.txt
```

### 步骤 2：运行验证测试

```bash
cd scripts
python test_v2.py
```

检查 V2 是否能正确处理你的模板。

### 步骤 3：更新代码

将导入从 `docx_filler` 改为 `docx_filler_v2`：

```python
# 旧代码
from docx_filler import DocxFiller

# 新代码
from docx_filler_v2 import DocxFillerV2
```

### 步骤 4：利用新功能

```python
# 获取填充报告数据
report_data = filler.fill(content_map)

# 分析填充情况
for title, data in report_data.get('sections', {}).items():
    confidence = data.get('confidence', 0)
    if confidence < 0.7:
        print(f"⚠️ {title} 需要人工检查")
```

### 步骤 5：测试和验证

- 使用真实模板测试
- 检查输出文档质量
- 验证填充报告准确性

---

## 🐛 已知问题

### 问题 1：中文字体在某些系统不显示

**现象**: 在 macOS 或 Linux 系统上，中文可能显示为方框。

**解决**: 安装中文字体：

```bash
# Ubuntu/Debian
sudo apt-get install fonts-wqy-zenhei fonts-wqy-microhei

# macOS (使用 Homebrew)
brew install --cask font-wqy-zenhei
```

### 问题 2：复杂表格样式丢失

**现象**: 模板中的复杂表格样式在填充后可能丢失。

**解决**: V2 默认应用 `Table Grid` 样式。如需保持原样式，可在 `fill` 方法中禁用样式覆盖。

---

## 📚 参考资料

- [Anthropic docx skill](https://github.com/anthropics/skills/tree/main/skills/docx)
- [python-docx 文档](https://python-docx.readthedocs.io/)
- [Office Open XML 规范](https://docs.microsoft.com/en-us/office/open-xml/)

---

## 🤝 获取帮助

如有问题，请：

1. 查看本迁移指南
2. 运行 `python test_v2.py` 诊断问题
3. 检查 [SKILL.md](../SKILL.md) 了解使用示例
4. 提交 Issue 或联系维护者

---

**最后更新**: 2026-03-21  
**版本**: V2.0.0
