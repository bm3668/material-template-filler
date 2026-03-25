# Material-Template-Filler 升级路线图

## 🎯 最终愿景

**从 "模板填充工具" 升级为 "项目申报材料智能生成系统"**

```
┌─────────────────────────────────────────────────────────────────┐
│                     用户输入层                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐     │
│  │ 项目说明.md  │  │ 对话式输入  │  │ 历史项目档案        │     │
│  └─────────────┘  └─────────────┘  └─────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    智能处理层                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ 内容理解     │  │ 模块匹配     │  │ 置信度评估   │          │
│  │ (LLM)        │  │ (Matcher)    │  │ (Scoring)    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    多格式输出层                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ 申报书.docx  │  │ 预算表.xlsx  │  │ 答辩 PPT.pptx │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ 进度计划表   │  │ PDF 版本      │  │ 填充报告.md  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                     交付物                                       │
│   📦 完整的项目申报材料包（一键打包下载）                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📅 实施阶段总览

| 阶段 | 周期 | 主题 | 核心交付物 | 状态 |
|------|------|------|------------|------|
| **Phase 1** | 第 1-2 周 | 文档处理核心升级 | 专业级 .docx 引擎 + 测试基准 | ✅ 已完成 (2026-03-21) |
| **Phase 2** | 第 3-4 周 | 评估体系与技能优化 | 自动化测试集 + SKILL 优化 | 🔄 进行中 |
| **Phase 3** | 第 5-6 周 | Excel 预算表支持 | xlsx 填充引擎 | ⏳ 待开始 |
| **Phase 4** | 第 7-8 周 | PDF 输入输出支持 | PDF 转换管道 | ⏳ 待开始 |
| **Phase 5** | 第 9-10 周 | PPT 答辩演示生成 | pptx 生成引擎 | ⏳ 待开始 |
| **Phase 6** | 第 11-12 周 | Web 界面重构 | 专业级前端界面 | ⏳ 待开始 |
| **Phase 7** | 第 13-16 周 | 系统集成与打包 | 一键生成全套材料 |

---

## 📋 Phase 1: 文档处理核心升级（第 1-2 周）

### 目标
引入 Anthropic **docx skill** 的最佳实践，将 `docx_filler.py` 重写为专业级文档处理引擎。

### 改进点

| 当前问题 | 改进方案 | 优先级 |
|----------|----------|--------|
| 仅使用 `python-docx` 基础功能 | 引入完整 .docx 规范支持（页面设置、样式、页眉页脚） | 🔴 高 |
| 模板样式识别有限 | 正确覆盖内置 Heading 样式，使用通用字体 | 🔴 高 |
| 缺少高级功能 | 支持书签、超链接、脚注、分栏、表格样式 | 🟡 中 |
| 页面尺寸默认 A4 | 显式设置页面尺寸，支持横向/纵向混合 | 🟡 中 |
| 无文档验证 | 引入 .docx 合法性验证 | 🟢 低 |

### 技术实现

#### 1.1 页面设置标准化
```python
# 新增：page_setup.py
from docx import Document
from docx.shared import Inches

def setup_page_layout(doc, paper_size='A4', orientation='portrait'):
    """
    设置页面尺寸和边距
    
    支持:
    - A4: 210mm × 297mm (默认)
    - US Letter: 8.5" × 11"
    - 自定义尺寸
    
    方向:
    - portrait: 纵向
    - landscape: 横向
    """
    section = doc.sections[0]
    
    if paper_size == 'A4':
        section.page_width = Inches(8.27)
        section.page_height = Inches(11.69)
    elif paper_size == 'letter':
        section.page_width = Inches(8.5)
        section.page_height = Inches(11)
    
    # 标准边距（1 英寸）
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)
    
    if orientation == 'landscape':
        section.orientation = docx.enum.section.WD_ORIENT.LANDSCAPE
```

#### 1.2 样式覆盖系统
```python
# 新增：style_manager.py
def apply_professional_styles(doc):
    """
    应用专业文档样式
    
    - 标题：Arial Black / 黑体
    - 正文：Arial / 宋体
    - 行距：1.5 倍
    - 段前段后：6pt
    """
    styles = doc.styles
    
    # 覆盖 Heading 1
    heading1 = styles['Heading 1']
    heading1.font.name = 'Arial Black'
    heading1.font.size = Inches(0.2)  # 14pt
    heading1.paragraph_format.space_before = Inches(0.15)  # 12pt
    heading1.paragraph_format.space_after = Inches(0.1)  # 6pt
    
    # 覆盖正文样式
    normal = styles['Normal']
    normal.font.name = 'Arial'
    normal.font.size = Inches(0.15)  # 12pt
    normal.paragraph_format.line_spacing = 1.5
```

#### 1.3 高级元素支持
```python
# 新增：advanced_elements.py
def insert_bookmark(paragraph, bookmark_name):
    """插入书签（用于目录和导航）"""
    pass

def insert_internal_hyperlink(paragraph, text, bookmark_target):
    """插入内部超链接"""
    pass

def insert_footnote(paragraph, footnote_text):
    """插入脚注"""
    pass

def create_styled_table(doc, rows, cols, style='Table Grid'):
    """创建带样式的表格"""
    pass
```

#### 1.4 文档验证
```python
# 新增：docx_validator.py
def validate_docx(file_path):
    """
    验证 .docx 文件合法性
    
    检查项:
    - ZIP 结构完整性
    - XML 格式正确性
    - 必需文件存在性
    - 样式表有效性
    """
    pass
```

### 交付物
- [ ] `docx_filler_v2.py` - 重写后的文档填充引擎
- [ ] `page_setup.py` - 页面设置模块
- [ ] `style_manager.py` - 样式管理系统
- [ ] `advanced_elements.py` - 高级元素支持
- [ ] `docx_validator.py` - 文档验证工具
- [ ] 更新 `requirements.txt`（如需要新依赖）

### 验收标准
- [ ] 支持 A4/US Letter 页面尺寸切换
- [ ] 支持纵向/横向混合布局
- [ ] 正确覆盖 Heading 1-9 样式
- [ ] 支持书签和内部超链接
- [ ] 支持脚注和尾注
- [ ] 支持表格样式自定义
- [ ] 生成的 .docx 通过验证工具检查
- [ ] 向后兼容现有模板

---

## 📋 Phase 2: 评估体系与技能优化（第 3-4 周）

### 目标
引入 Anthropic **skill-creator** 方法，建立自动化测试和评估体系，优化技能触发准确性。

### 改进点

| 当前问题 | 改进方案 | 优先级 |
|----------|----------|--------|
| 无系统测试用例 | 创建多模板类型测试集 | 🔴 高 |
| 缺少性能指标 | 建立填充准确率基准 | 🔴 高 |
| 置信度评分无基准 | 量化评估置信度算法 | 🟡 中 |
| 技能描述简单 | 优化 SKILL.md description | 🟡 中 |

### 技术实现

#### 2.1 测试集构建
```
tests/
├── templates/              # 测试模板
│   ├── simple_heading.docx     # 简单标题模板
│   ├── complex_table.docx      # 复杂表格模板
│   ├── mixed_layout.docx       # 混合布局模板
│   ├── funding_application.docx # 基金申请模板
│   └── competition_entry.docx  # 竞赛申报模板
├── inputs/                 # 测试输入
│   ├── project_a.md
│   ├── project_b.md
│   └── project_c.md
├── expected_outputs/       # 期望输出（人工标注）
│   ├── project_a_simple_heading.json
│   └── ...
└── test_runner.py          # 测试执行器
```

#### 2.2 评估指标
```python
# 新增：eval_metrics.py
class EvaluationMetrics:
    """
    填充效果评估指标
    """
    
    def module_fill_rate(self, filled_doc, expected):
        """模块填充率：已填充模块数 / 总模块数"""
        pass
    
    def content_accuracy(self, filled_content, expected_content):
        """内容准确率：使用文本相似度算法"""
        pass
    
    def confidence_calibration(self, predicted_confidence, actual_accuracy):
        """置信度校准：预测置信度与实际准确率的关联度"""
        pass
    
    def format_preservation(self, original_template, filled_doc):
        """格式保持度：样式、布局的保持程度"""
        pass
```

#### 2.3 批量测试执行器
```python
# 新增：test_runner.py
class TestRunner:
    """
    批量测试执行器
    """
    
    def run_all_tests(self):
        """运行所有测试用例"""
        pass
    
    def generate_report(self):
        """生成测试报告（含统计图表）"""
        pass
    
    def compare_versions(self, version_a, version_b):
        """对比两个版本的性能差异"""
        pass
```

#### 2.4 SKILL.md 优化
```markdown
# 优化前
description: 通用项目模板智能填充。读取 docx 模板和用户输入，自动匹配内容并填充到对应模块。

# 优化后
description: 通用项目模板智能填充系统。支持基金申报、竞赛材料、项目计划书等场景。
自动识别 Word 模板的标题模块和表格字段，智能匹配项目内容并填充。
输出填充后的.docx 文件 + 详细填充报告（含置信度评分）。
支持批量填充、历史项目复用、Web 界面操作。
触发场景：用户需要填写申报书/竞赛材料/项目计划书等模板文档时。
```

### 交付物
- [ ] `tests/templates/` - 5+ 种测试模板
- [ ] `tests/inputs/` - 3+ 个测试输入文档
- [ ] `tests/expected_outputs/` - 人工标注的期望输出
- [ ] `test_runner.py` - 测试执行器
- [ ] `eval_metrics.py` - 评估指标系统
- [ ] 更新后的 `SKILL.md`

### 验收标准
- [ ] 测试集覆盖 5+ 种模板类型
- [ ] 自动化测试可在 5 分钟内完成
- [ ] 生成可视化测试报告
- [ ] 建立填充准确率基线（目标：≥85%）
- [ ] 置信度评分与实际准确率相关性 ≥0.7

---

## 📋 Phase 3: Excel 预算表支持（第 5-6 周）

### 目标
引入 Anthropic **xlsx skill**，扩展支持 Excel 预算表、进度表等模板。

### 改进点

| 当前能力 | 扩展能力 | 优先级 |
|----------|----------|--------|
| 仅支持 .docx | 支持 .xlsx/.xlsm/.csv | 🔴 高 |
| 无公式处理 | 支持公式自动计算 | 🔴 高 |
| 无颜色编码 | 引入金融行业颜色规范 | 🟡 中 |
| 无图表支持 | 支持图表生成 | 🟢 低 |

### 技术实现

#### 3.1 核心引擎
```python
# 新增：xlsx_filler.py
from openpyxl import load_workbook
from openpyxl.styles import Font, Color, PatternFill

class XLSXFiller:
    """
    Excel 预算表填充引擎
    """
    
    def __init__(self, template_path):
        self.wb = load_workbook(template_path)
        self.ws = self.wb.active
        
    def fill_cell(self, cell_ref, value, cell_type='input'):
        """
        填充单元格
        
        cell_type:
        - input: 硬编码输入（蓝色字体）
        - formula: 公式（黑色字体）
        - link_internal: 内部链接（绿色字体）
        - link_external: 外部链接（红色字体）
        """
        pass
    
    def apply_color_coding(self):
        """
        应用金融行业颜色编码标准
        
        - 蓝色 (0,0,255): 硬编码输入
        - 黑色 (0,0,0): 公式
        - 绿色 (0,128,0): 内部链接
        - 红色 (255,0,0): 外部链接
        - 黄色背景：关键假设
        """
        pass
    
    def recalculate_formulas(self):
        """使用 LibreOffice 重算公式"""
        pass
    
    def save(self, output_path):
        """保存文件"""
        pass
```

#### 3.2 预算表模板支持
```python
# 新增：budget_templates.py
BUDGET_TEMPLATES = {
    'funding_application': {
        'sections': [
            '人员费',
            '设备费',
            '材料费',
            '测试化验加工费',
            '差旅费',
            '会议费',
            '出版/文献/信息传播费',
            '其他费用'
        ],
        'formulas': {
            'total': '=SUM(B2:B9)',
            'subtotal': '=SUM(B2:B5)'
        }
    },
    'competition_budget': {
        # 竞赛预算模板结构
    }
}
```

#### 3.3 统一填充接口
```python
# 更新：main.py
def fill_template(template_path, project_data, output_dir='filled/'):
    """
    统一的模板填充接口
    
    自动识别模板类型并调用相应引擎：
    - .docx → DocxFiller
    - .xlsx/.xlsm → XLSXFiller
    - .csv → XLSXFiller (转换为 Excel)
    """
    ext = os.path.splitext(template_path)[1].lower()
    
    if ext in ['.docx']:
        return fill_docx_template(template_path, project_data)
    elif ext in ['.xlsx', '.xlsm', '.csv']:
        return fill_xlsx_template(template_path, project_data)
    else:
        raise ValueError(f"不支持的模板格式：{ext}")
```

### 交付物
- [ ] `xlsx_filler.py` - Excel 填充引擎
- [ ] `budget_templates.py` - 预算表模板库
- [ ] 更新 `main.py` - 统一填充接口
- [ ] 测试模板：`tests/templates/budget_simple.xlsx`
- [ ] 更新 `SKILL.md` - 添加 Excel 支持说明

### 验收标准
- [ ] 支持 .xlsx/.xlsm/.csv 格式
- [ ] 正确应用颜色编码规范
- [ ] 公式自动重算无错误
- [ ] 支持常见预算表模板
- [ ] 与 docx 填充流程无缝集成

---

## 📋 Phase 4: PDF 输入输出支持（第 7-8 周）

### 目标
引入 Anthropic **pdf skill**，支持 PDF 模板转换和 PDF 输出。

### 改进点

| 场景 | 能力 | 优先级 |
|------|------|--------|
| 用户只有 PDF 模板 | PDF → .docx 转换后填充 | 🔴 高 |
| 需要输出 PDF | 填充完成后自动转 PDF | 🔴 高 |
| 参考材料是 PDF | 从 PDF 提取项目信息 | 🟡 中 |

### 技术实现

#### 4.1 PDF 输入处理
```python
# 新增：pdf_input_handler.py
import pdfplumber
from pypdf import PdfReader

class PDFInputHandler:
    """
    PDF 输入处理器
    """
    
    def extract_text(self, pdf_path):
        """提取 PDF 文本内容"""
        pass
    
    def extract_tables(self, pdf_path):
        """提取 PDF 表格"""
        pass
    
    def convert_to_docx(self, pdf_path, output_path):
        """
        PDF → .docx 转换
        
        使用 LibreOffice 或 pandoc
        """
        pass
    
    def ocr_scan(self, pdf_path):
        """OCR 处理扫描版 PDF"""
        pass
```

#### 4.2 PDF 输出处理
```python
# 新增：pdf_output_handler.py
class PDFOutputHandler:
    """
    PDF 输出处理器
    """
    
    def docx_to_pdf(self, docx_path, output_path):
        """
        .docx → PDF 转换
        
        使用 LibreOffice (推荐) 或 weasyprint
        """
        pass
    
    def xlsx_to_pdf(self, xlsx_path, output_path):
        """Excel → PDF 转换"""
        pass
    
    def merge_pdfs(self, pdf_paths, output_path):
        """合并多个 PDF 文件"""
        pass
```

#### 4.3 统一转换管道
```python
# 新增：conversion_pipeline.py
class ConversionPipeline:
    """
    文档转换管道
    """
    
    def process_input(self, input_file):
        """
        处理输入文件
        
        - .pdf → 提取文本/转.docx
        - .docx → 直接使用
        - .md/.txt → 直接使用
        """
        pass
    
    def process_output(self, filled_file, output_format='pdf'):
        """
        处理输出文件
        
        支持输出格式：pdf, docx, xlsx, 或组合
        """
        pass
```

### 交付物
- [ ] `pdf_input_handler.py` - PDF 输入处理
- [ ] `pdf_output_handler.py` - PDF 输出处理
- [ ] `conversion_pipeline.py` - 转换管道
- [ ] 更新 `requirements.txt`（pdfplumber, pypdf 等）
- [ ] 更新 `SKILL.md` - 添加 PDF 支持说明

### 验收标准
- [ ] 支持 PDF 模板 → .docx 转换
- [ ] 支持填充后 → PDF 输出
- [ ] 支持扫描版 PDF 的 OCR 处理
- [ ] 支持多个 PDF 合并
- [ ] 转换后格式保持良好

---

## 📋 Phase 5: PPT 答辩演示生成（第 9-10 周）

### 目标
引入 Anthropic **pptx skill**，支持从项目说明自动生成答辩 PPT。

### 改进点

| 场景 | 能力 | 优先级 |
|------|------|--------|
| 项目申报需要答辩 PPT | 从申报书自动提取内容生成 PPT | 🔴 高 |
| PPT 设计质量参差不齐 | 应用专业设计规范 | 🔴 高 |
| 手动制作 PPT 耗时 | 一键生成初稿 | 🟡 中 |

### 技术实现

#### 5.1 PPT 生成引擎
```python
# 新增：pptx_generator.py
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

class PPTXGenerator:
    """
    PPT 答辩演示生成器
    """
    
    def __init__(self, template_path=None):
        if template_path:
            self.prs = Presentation(template_path)
        else:
            self.prs = Presentation()
            self.setup_professional_theme()
    
    def setup_professional_theme(self):
        """设置专业主题"""
        # 配色方案、字体、背景等
        pass
    
    def extract_content_from_docx(self, docx_path):
        """
        从申报书提取 PPT 内容
        
        提取结构:
        - 项目名称 → 标题页
        - 项目背景 → 背景页
        - 研究目标 → 目标页
        - 技术方案 → 方案页
        - 预期成果 → 成果页
        - 团队介绍 → 团队页
        - 预算 → 预算页
        """
        pass
    
    def generate_slides(self, project_data):
        """
        生成幻灯片
        
        默认结构（8-10 页）:
        1. 标题页
        2. 目录
        3. 项目背景
        4. 研究目标
        5. 技术方案
        6. 创新点
        7. 预期成果
        8. 团队介绍
        9. 进度计划
        10. 预算概述
        """
        pass
    
    def apply_design_elements(self):
        """应用设计元素（图标、图表、图片占位符）"""
        pass
    
    def save(self, output_path):
        """保存 PPT"""
        pass
```

#### 5.2 设计规范
```python
# 新增：pptx_design.py
DESIGN_THEMES = {
    'professional': {
        'colors': {
            'primary': '#1E2761',    # 深蓝
            'secondary': '#CADCFC',  # 冰蓝
            'accent': '#FFFFFF'      # 白色
        },
        'fonts': {
            'heading': 'Arial Black',
            'body': 'Arial'
        }
    },
    'academic': {
        # 学术风格主题
    },
    'startup': {
        # 创业路演风格主题
    }
}

SLIDE_LAYOUTS = {
    'title': '标题页布局',
    'content': '内容页布局',
    'comparison': '对比页布局',
    'timeline': '时间线布局',
    'team': '团队页布局',
    'budget': '预算页布局'
}
```

#### 5.3 一键生成管道
```python
# 新增：one_click_generator.py
class OneClickGenerator:
    """
    一键生成全套材料
    """
    
    def generate_all(self, project_data, output_dir='output/'):
        """
        从项目说明生成全套材料
        
        输出:
        - 申报书.docx
        - 预算表.xlsx
        - 答辩 PPT.pptx
        - 进度计划表.xlsx
        - 全套材料.pdf（合并版）
        - 填充报告.md
        """
        pass
    
    def package_for_submission(self, output_dir):
        """
        打包为提交格式
        
        - 创建文件夹结构
        - 压缩为.zip
        """
        pass
```

### 交付物
- [ ] `pptx_generator.py` - PPT 生成引擎
- [ ] `pptx_design.py` - PPT 设计规范
- [ ] `one_click_generator.py` - 一键生成器
- [ ] 3+ 个 PPT 主题模板
- [ ] 更新 `SKILL.md` - 添加 PPT 支持说明

### 验收标准
- [ ] 支持从申报书自动提取内容生成 PPT
- [ ] 生成 8-10 页标准答辩 PPT
- [ ] 应用专业设计规范
- [ ] 支持自定义主题
- [ ] 与 docx/xlsx 流程无缝集成

---

## 📋 Phase 6: Web 界面重构（第 11-12 周）

### 目标
引入 Anthropic **frontend-design** 原则，重构 Web 界面，打造专业、美观、易用的用户体验。

### 改进点

| 当前问题 | 改进方案 | 优先级 |
|----------|----------|--------|
| 基础功能界面 | 专业级 UI 设计 | 🔴 高 |
| 简单布局 | 精美排版、配色、动效 | 🔴 高 |
| 无品牌感 | 一致的视觉风格 | 🟡 中 |
| 交互体验一般 | 流畅的交互设计 | 🟡 中 |

### 设计原则

```
┌─────────────────────────────────────────────────────────────┐
│                    设计愿景                                  │
│                                                             │
│  "让项目申报材料准备变得像填写在线表单一样简单"              │
│                                                             │
│  设计风格：专业、简洁、可信赖                                │
│  目标用户：大学生、科研人员、企业项目申报负责人              │
│                                                             │
│  核心体验：                                                  │
│  1. 3 步完成材料准备（上传→预览→下载）                       │
│  2. 实时预览填充效果                                        │
│  3. 智能提示和引导                                          │
└─────────────────────────────────────────────────────────────┘
```

### 技术实现

#### 6.1 前端架构
```
web/
├── index.html              # 主页面
├── css/
│   ├── variables.css       # CSS 变量（配色、字体）
│   ├── layout.css          # 布局样式
│   ├── components.css      # 组件样式
│   └── animations.css      # 动画效果
├── js/
│   ├── app.js              # 主应用逻辑
│   ├── uploader.js         # 文件上传
│   ├── preview.js          # 实时预览
│   └── api.js              # API 调用
├── components/             # Web Components
│   ├── file-uploader.js    # 文件上传组件
│   ├── template-selector.js # 模板选择器
│   ├── content-editor.js   # 内容编辑器
│   └── preview-panel.js    # 预览面板
└── assets/                 # 静态资源
    ├── fonts/
    ├── icons/
    └── images/
```

#### 6.2 配色方案
```css
/* variables.css */
:root {
  /* 主色调 - 专业蓝 */
  --primary-900: #1E2761;
  --primary-700: #2C3E8A;
  --primary-500: #4A69BD;
  --primary-300: #8FA4DC;
  --primary-100: #CADCFC;
  
  /* 强调色 - 活力橙 */
  --accent-500: #F96167;
  --accent-300: #F9A19F;
  
  /* 中性色 */
  --gray-900: #141413;
  --gray-700: #3D3D3D;
  --gray-500: #808080;
  --gray-300: #C0C0C0;
  --gray-100: #F5F5F5;
  --white: #FFFFFF;
  
  /* 功能色 */
  --success: #28A745;
  --warning: #FFC107;
  --error: #DC3545;
  
  /* 字体 */
  --font-heading: 'Poppins', 'Arial Black', sans-serif;
  --font-body: 'Lora', 'Georgia', serif;
  --font-mono: 'Fira Code', 'Consolas', monospace;
  
  /* 间距 */
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;
  
  /* 圆角 */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 16px;
  --radius-full: 9999px;
  
  /* 阴影 */
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
  --shadow-md: 0 4px 6px rgba(0,0,0,0.1);
  --shadow-lg: 0 10px 15px rgba(0,0,0,0.1);
}
```

#### 6.3 核心页面设计

**首页（三步引导）**
```
┌─────────────────────────────────────────────────────────────┐
│  📋 项目申报材料智能生成系统                                  │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Step 1: 选择模板                                    │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐               │   │
│  │  │ 📄 申报书│ │ 📊 预算表│ │ 📽️ 答辩 PPT│               │   │
│  │  └─────────┘ └─────────┘ └─────────┘               │   │
│  │  或拖拽上传自定义模板                                │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Step 2: 填写项目内容                                │   │
│  │  ┌───────────────────────────────────────────────┐  │   │
│  │  │ 项目名称：[_______________________________]    │  │   │
│  │  │ 项目背景：                                     │  │   │
│  │  │ [_________________________________________]   │  │   │
│  │  │ [_________________________________________]   │  │   │
│  │  │ [_________________________________________]   │  │   │
│  │  └───────────────────────────────────────────────┘  │   │
│  │  或上传项目说明文档 (.md/.docx/.txt)                │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Step 3: 预览并下载                                  │   │
│  │  [👁️ 预览]  [📥 下载全套材料]                        │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

#### 6.4 动画效果
```css
/* animations.css */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes slideIn {
  from { transform: translateX(-20px); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

.step-card {
  animation: fadeIn 0.5s ease-out;
}

.step-card:nth-child(2) {
  animation-delay: 0.2s;
}

.step-card:nth-child(3) {
  animation-delay: 0.4s;
}

.upload-area.drag-over {
  animation: pulse 0.5s ease-in-out infinite;
}
```

### 交付物
- [ ] 重构后的 `web/` 目录
- [ ] `css/variables.css` - 设计系统变量
- [ ] `css/components.css` - 组件样式库
- [ ] `js/app.js` - 前端应用逻辑
- [ ] 3+ 个 Web Components
- [ ] 响应式设计（支持移动端）
- [ ] 更新 `README.md` - Web 界面使用说明

### 验收标准
- [ ] 页面加载时间 < 2 秒
- [ ] 支持拖拽上传文件
- [ ] 实时预览填充效果
- [ ] 响应式设计（手机/平板/桌面）
- [ ] 通过 Lighthouse 性能测试（≥90 分）
- [ ] 视觉设计专业、一致

---

## 📋 Phase 7: 系统集成与打包（第 13-16 周）

### 目标
整合所有模块，实现"一键生成全套申报材料"的最终愿景。

### 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        用户界面层                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Web 界面     │  │ 命令行工具   │  │ API 接口     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                        核心服务层                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ 内容理解     │  │ 模板解析     │  │ 智能匹配     │          │
│  │ (LLM)        │  │ (Parser)     │  │ (Matcher)    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                        文档引擎层                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ DocxEngine   │  │ XlsxEngine   │  │ PptxEngine   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ PdfConverter │  │ Validator    │  │ Packager     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                        输出层                                    │
│  📦 申报材料包.zip                                               │
│     ├── 01_申报书.docx                                          │
│     ├── 02_预算表.xlsx                                          │
│     ├── 03_答辩 PPT.pptx                                        │
│     ├── 04_进度计划.xlsx                                        │
│     ├── 05_全套材料.pdf                                         │
│     └── 填充报告.md                                             │
└─────────────────────────────────────────────────────────────────┘
```

### 技术实现

#### 7.1 统一 CLI 入口
```python
# 更新：main.py
#!/usr/bin/env python3
"""
项目申报材料智能生成系统 - 命令行入口
"""

import argparse
import sys

def main():
    parser = argparse.ArgumentParser(
        description='项目申报材料智能生成系统',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  # 填充单个模板
  %(prog)s fill --template 申报书.docx --input 项目说明.md
  
  # 一键生成全套材料
  %(prog)s generate-all --input 项目说明.md --output output/
  
  # 批量填充多个模板
  %(prog)s batch --templates templates/*.docx --input 项目说明.md
  
  # 启动 Web 服务
  %(prog)s serve --port 8080
        '''
    )
    
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # fill 命令
    fill_parser = subparsers.add_parser('fill', help='填充单个模板')
    fill_parser.add_argument('--template', required=True, help='模板文件路径')
    fill_parser.add_argument('--input', required=True, help='项目说明文件路径')
    fill_parser.add_argument('--output', default='filled/', help='输出目录')
    
    # generate-all 命令
    genall_parser = subparsers.add_parser('generate-all', help='一键生成全套材料')
    genall_parser.add_argument('--input', required=True, help='项目说明文件路径')
    genall_parser.add_argument('--output', default='output/', help='输出目录')
    genall_parser.add_argument('--templates', help='自定义模板目录')
    
    # batch 命令
    batch_parser = subparsers.add_parser('batch', help='批量填充')
    batch_parser.add_argument('--templates', required=True, help='模板文件通配符')
    batch_parser.add_argument('--input', required=True, help='项目说明文件路径')
    
    # serve 命令
    serve_parser = subparsers.add_parser('serve', help='启动 Web 服务')
    serve_parser.add_argument('--port', type=int, default=8080, help='服务端口')
    serve_parser.add_argument('--host', default='0.0.0.0', help='监听地址')
    
    args = parser.parse_args()
    
    if args.command == 'fill':
        from commands.fill import run_fill
        run_fill(args)
    elif args.command == 'generate-all':
        from commands.generate_all import run_generate_all
        run_generate_all(args)
    elif args.command == 'batch':
        from commands.batch import run_batch
        run_batch(args)
    elif args.command == 'serve':
        from commands.serve import run_serve
        run_serve(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
```

#### 7.2 一键生成器
```python
# 新增：commands/generate_all.py
class GenerateAllCommand:
    """
    一键生成全套材料命令
    """
    
    DEFAULT_TEMPLATES = [
        'templates/申报书模板.docx',
        'templates/预算表模板.xlsx',
        'templates/答辩 PPT 模板.pptx',
        'templates/进度计划模板.xlsx'
    ]
    
    def run(self, args):
        # 1. 读取项目说明
        project_data = self.load_project_data(args.input)
        
        # 2. 加载模板（使用默认或自定义）
        templates = self.load_templates(args.templates)
        
        # 3. 并行填充所有模板
        results = self.parallel_fill(templates, project_data)
        
        # 4. 生成 PDF 合并版
        self.generate_pdf_bundle(results, args.output)
        
        # 5. 生成填充报告
        self.generate_report(results, args.output)
        
        # 6. 打包为.zip
        package_path = self.create_package(args.output)
        
        print(f"✅ 生成完成！")
        print(f"📦 材料包：{package_path}")
        
        return package_path
```

#### 7.3 打包工具
```python
# 新增：packager.py
import zipfile
import os
from datetime import datetime

class MaterialPackager:
    """
    申报材料打包工具
    """
    
    def create_package(self, output_dir, package_name=None):
        """
        创建提交材料包
        
        目录结构:
        project_name_YYYYMMDD_HHMMSS/
        ├── 01_申报书/
        │   ├── 申报书.docx
        │   └── 申报书.pdf
        ├── 02_预算表/
        │   ├── 预算表.xlsx
        │   └── 预算表.pdf
        ├── 03_答辩 PPT/
        │   ├── 答辩 PPT.pptx
        │   └── 答辩 PPT.pdf
        ├── 04_进度计划/
        │   └── 进度计划.xlsx
        ├── 05_附件/
        │   └── ...
        └── 填充报告.md
        """
        pass
    
    def validate_package(self, package_path):
        """验证材料包完整性"""
        pass
```

### 交付物
- [ ] 更新 `main.py` - 统一 CLI 入口
- [ ] `commands/fill.py` - 填充命令
- [ ] `commands/generate_all.py` - 一键生成命令
- [ ] `commands/batch.py` - 批量命令
- [ ] `commands/serve.py` - Web 服务命令
- [ ] `packager.py` - 打包工具
- [ ] 默认模板集（申报书、预算表、PPT、进度计划）
- [ ] 完整的用户文档

### 验收标准
- [ ] 一键生成全套材料时间 < 30 秒
- [ ] 支持自定义模板
- [ ] 生成的材料包结构清晰、完整
- [ ] CLI 命令帮助文档完善
- [ ] Web 服务稳定运行
- [ ] 通过所有自动化测试

---

## 📊 项目里程碑

```
Week 1-2   ████░░░░░░░░░░░░░░░░ Phase 1: Docx 引擎升级
Week 3-4   ████████░░░░░░░░░░░░ Phase 2: 评估体系
Week 5-6   ████████████░░░░░░░░ Phase 3: Excel 支持
Week 7-8   ████████████████░░░░ Phase 4: PDF 支持
Week 9-10  ████████████████████ Phase 5: PPT 支持
Week 11-12 ████████████████████ Phase 6: Web 重构
Week 13-16 ████████████████████ Phase 7: 系统集成
                                   
           ●────●────●────●────●────●────●
           W1   W4   W6   W8   W10  W12  W16
           M1   M2   M3   M4   M5   M6   M7
```

### 关键里程碑

| 里程碑 | 时间 | 交付物 |
|--------|------|--------|
| **M1** | 第 2 周末 | 专业级 Docx 引擎上线 |
| **M2** | 第 4 周末 | 测试评估体系建立，SKILL 优化完成 |
| **M3** | 第 6 周末 | Excel 预算表支持上线 |
| **M4** | 第 8 周末 | PDF 输入输出支持完成 |
| **M5** | 第 10 周末 | PPT 答辩演示生成上线 |
| **M6** | 第 12 周末 | 新版 Web 界面发布 |
| **M7** | 第 16 周末 | 1.0 正式版发布，一键生成全套材料 |

---

## ⚠️ 风险评估与应对

| 风险 | 可能性 | 影响 | 应对措施 |
|------|--------|------|----------|
| python-docx 功能限制 | 中 | 高 | 预留时间研究底层 XML 操作 |
| LibreOffice 依赖问题 | 中 | 中 | 提供替代方案（pandoc/weasyprint） |
| LLM 匹配准确率不达标 | 中 | 高 | 建立人工校验流程，持续优化算法 |
| Web 界面开发延期 | 高 | 中 | 分阶段发布，先核心功能后美化 |
| 模板兼容性问题 | 高 | 中 | 建立模板测试集，广泛收集用户反馈 |
| 性能问题（大文件处理慢） | 中 | 中 | 引入缓存机制，优化算法复杂度 |

---

## 📈 成功指标

### 技术指标
- [ ] 文档填充准确率 ≥ 85%
- [ ] 置信度评分校准度 ≥ 0.7
- [ ] 单文档处理时间 < 10 秒
- [ ] 全套材料生成时间 < 30 秒
- [ ] Web 界面 Lighthouse 分数 ≥ 90
- [ ] 测试覆盖率 ≥ 80%

### 用户体验指标
- [ ] 用户满意度 ≥ 4.5/5
- [ ] 平均完成时间 < 5 分钟
- [ ] 重复使用率 ≥ 60%
- [ ] 推荐意愿 ≥ 8/10

---

## 🔄 持续改进计划

### Phase 8+ (未来规划)

1. **AI 内容增强**
   - 智能润色和扩写
   - 多语言支持
   - 领域特定优化（医学、工程、社科等）

2. **协作功能**
   - 多人在线协作编辑
   - 版本控制和历史追溯
   - 评论和批注系统

3. **模板市场**
   - 用户分享模板
   - 官方模板库
   - 模板评分和推荐

4. **企业版功能**
   - 私有化部署
   - 自定义品牌规范
   - API 集成

---

## 📝 版本规划

| 版本 | 时间 | 特性 |
|------|------|------|
| **v0.1** | 当前 | 基础 Docx 填充功能 |
| **v0.5** | 第 4 周 | 评估体系 + SKILL 优化 |
| **v0.7** | 第 8 周 | Excel + PDF 支持 |
| **v0.9** | 第 12 周 | PPT + Web 重构 |
| **v1.0** | 第 16 周 | 正式版发布 |
| **v1.5** | 第 24 周 | AI 增强 + 协作功能 |
| **v2.0** | 第 52 周 | 模板市场 + 企业版 |

---

## 🎬 开始行动

### 第一步（本周）
1. [ ] 创建 Phase 1 所需的新文件
2. [ ] 阅读 Anthropic docx skill 完整文档
3. [ ] 设计新的 `docx_filler_v2.py` 架构
4. [ ] 准备 3-5 个测试模板

### 立即可以做的
```bash
# 1. 创建 Phase 1 目录结构
cd ~/.openclaw/workspace/skills/material-template-filler
mkdir -p engines validators

# 2. 安装依赖
pip install python-docx openpyxl pdfplumber pypdf python-pptx

# 3. 开始编写 docx_filler_v2.py
```

---

**最后更新**: 2026-03-21  
**版本**: v0.1  
**状态**: 规划中

---

> "千里之行，始于足下" — 让我们一步步实现这个愿景！
