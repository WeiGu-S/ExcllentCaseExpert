# ExcellentCaseExpert - AI 测试用例生成系统

<div align="center">

![ExcellentCaseExpert Logo](assets/icon.png)

**智能化测试用例生成工具，让测试设计更高效**

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)](https://github.com)

</div>

## 📖 简介

ExcellentCaseExpert 是一个基于 AI 的智能测试用例生成工具，通过 OCR 技术识别需求文档，利用大语言模型智能分析生成测试要点与用例，并支持导出为多种格式。

### ✨ 核心特性

- 🔍 **智能 OCR 识别**：支持 PNG、JPG、PDF 格式，双引擎识别（PaddleOCR + Tesseract），准确率 ≥ 95%
- 🤖 **AI 智能分析**：基于大语言模型，从多维度提取测试要点（功能、性能、安全、兼容性、易用性）
- 📋 **自动用例生成**：智能生成正向、负向、边界、异常测试用例，覆盖率 ≥ 90%
- 💾 **多格式导出**：支持 JSON 和 XMind 思维导图格式，便于团队协作
- ⚡ **高性能处理**：异步处理、智能缓存、内存优化，单文档处理 ≤ 30 秒
- 🎨 **现代化界面**：基于 PyQt6 的精美界面，支持亮色/暗色主题，提供流畅的用户体验

### 🎯 适用场景

- 快速从需求文档生成测试用例
- 提升测试设计效率 70%+
- 标准化测试用例格式
- 团队测试知识沉淀

## 🚀 快速开始

### 系统要求

**最低配置**：
- 操作系统：Windows 10+, macOS 10.15+, Ubuntu 18.04+
- Python：3.8+
- 内存：4GB RAM
- 存储：2GB 可用空间
- 网络：稳定的互联网连接（用于 AI API 调用）

**推荐配置**：
- 内存：8GB+ RAM
- 存储：5GB+ 可用空间
- CPU：多核处理器

### 安装方式

#### 方式一：使用预编译版本（推荐）

1. 从 [Releases](https://github.com/your-repo/releases) 下载对应平台的安装包
2. 解压并运行可执行文件
3. 首次运行时配置 AI 模型 API Key

#### 方式二：从源码安装

```bash
# 1. 克隆仓库
git clone https://github.com/your-repo/ExcellentCaseExpert.git
cd ExcellentCaseExpert

# 2. 安装 uv (Python 包管理器)
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 3. 创建虚拟环境并安装依赖
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt

# 4. 运行应用
python main.py
```

### 配置 AI 模型

首次运行时，需要配置 AI 模型的 API Key：

1. **OpenAI**（推荐）
   ```yaml
   ai_model:
     provider: "openai"
     api_key: "sk-your-api-key-here"
     base_url: "https://api.openai.com/v1"
     model_name: "gpt-4o-mini"
   ```

2. **通义千问（Qwen）**
   ```yaml
   ai_model:
     provider: "qwen"
     api_key: "your-dashscope-api-key"
     base_url: "https://dashscope.aliyuncs.com/compatible-mode/v1"
     model_name: "qwen-turbo"
   ```

3. **Deepseek**
   ```yaml
   ai_model:
     provider: "deepseek"
     api_key: "your-deepseek-api-key"
     base_url: "https://api.deepseek.com/v1"
     model_name: "deepseek-chat"
   ```

4. **自定义 API**
   ```yaml
   ai_model:
     provider: "custom"
     api_key: "your-api-key"
     base_url: "https://your-api-endpoint.com/v1"
     model_name: "your-model-name"
   ```

### 环境变量配置（推荐）

为了保护 API Key，建议使用环境变量：

```bash
# Linux/macOS
export OPENAI_API_KEY="sk-your-api-key-here"

# Windows
set OPENAI_API_KEY=sk-your-api-key-here
```

然后在 `config.yaml` 中使用：
```yaml
ai_model:
  api_key: "${OPENAI_API_KEY}"
```

## 📚 使用指南

### 基本工作流程

```
1. 导入文档 → 2. OCR 识别 → 3. AI 分析 → 4. 生成用例 → 5. 导出结果
```

### 详细步骤

#### 1. 导入需求文档

- 点击工具栏的 **📁 导入文档** 按钮
- 选择需求文档（支持 PNG、JPG、JPEG、PDF 格式）
- 文件大小限制：50MB

#### 2. OCR 文本识别

- 点击 **🔍 OCR 识别** 按钮
- 系统自动识别文档中的文本
- 识别结果显示在左侧 "OCR 识别结果" 区域
- 支持手动编辑识别结果

#### 3. AI 智能分析

- 点击 **🤖 AI 分析** 按钮
- AI 从需求文本中提取测试要点
- 测试要点显示在右上方 "测试要点" 区域
- 包含测试类别、优先级、测试场景等信息

#### 4. 生成测试用例

- 点击 **📋 生成用例** 按钮
- 系统根据测试要点自动生成测试用例
- 包含正向、负向、边界、异常用例
- 测试用例显示在右下方 "测试用例" 区域

#### 5. 导出测试用例

- 点击 **💾 导出** 按钮
- 选择导出格式：
  - **JSON**：结构化数据，便于程序处理
  - **XMind**：思维导图，便于人工查看和编辑
- 选择保存位置并导出

### 高级功能

#### 缓存机制

- **OCR 缓存**：识别结果缓存 7 天，相同文件无需重复识别
- **AI 缓存**：分析结果缓存 24 小时，节省 API 调用成本
- 缓存位置：`~/.excellentcase/cache/`

#### 性能优化

- **异步处理**：所有耗时操作在后台线程执行，界面保持响应
- **内存管理**：自动监控和清理内存，支持大文件处理
- **并发控制**：可配置最大并发任务数（默认 3）

#### 主题切换

- 在 **⚙️ 设置** 中选择主题：
  - **light**：亮色主题（清新明亮，适合日间使用）
  - **dark**：暗色主题（护眼舒适，适合夜间使用）
  - **auto**：自动跟随系统（仅 macOS）

## 🔧 配置说明

配置文件位置：`config.yaml`

### 完整配置示例

```yaml
# AI 模型配置
ai_model:
  provider: "openai"
  api_key: "${OPENAI_API_KEY}"
  base_url: "https://api.openai.com/v1"
  model_name: "gpt-4o-mini"
  max_tokens: 2000
  temperature: 0.7

# OCR 配置
ocr:
  use_paddle_ocr: true
  use_tesseract: true
  languages: ["ch_sim", "en"]
  max_file_size_mb: 50

# 性能配置
performance:
  max_concurrent_tasks: 3
  memory_cleanup_interval: 30
  max_memory_mb: 1024

# UI 配置
ui:
  theme: "light"
  language: "zh_CN"
  window_width: 1200
  window_height: 800
```

### 配置项说明

| 配置项 | 说明 | 默认值 | 可选值 |
|--------|------|--------|--------|
| `ai_model.provider` | AI 提供商 | openai | openai, qwen, deepseek, custom |
| `ai_model.temperature` | 温度参数 | 0.7 | 0.0-1.0 |
| `ocr.use_paddle_ocr` | 使用 PaddleOCR | true | true, false |
| `ocr.use_tesseract` | 使用 Tesseract | true | true, false |
| `performance.max_concurrent_tasks` | 最大并发任务数 | 3 | 1-10 |
| `ui.theme` | 界面主题 | light | light, dark, auto |
| `ui.language` | 界面语言 | zh_CN | zh_CN, en_US |

## 📊 测试用例格式

### JSON 格式

```json
{
  "feature_name": "用户登录功能",
  "test_cases": [
    {
      "test_case_id": "TC_功能_001",
      "title": "正常登录流程",
      "category": "功能测试",
      "priority": "P0",
      "case_type": "正向用例",
      "steps": [
        {
          "step_no": 1,
          "action": "打开登录页面",
          "expected": "页面正常显示"
        },
        {
          "step_no": 2,
          "action": "输入正确的用户名和密码",
          "expected": "输入成功"
        },
        {
          "step_no": 3,
          "action": "点击登录按钮",
          "expected": "登录成功，跳转到首页"
        }
      ],
      "expected_result": "用户成功登录系统",
      "description": "验证用户使用正确凭据登录系统"
    }
  ]
}
```

### XMind 格式

XMind 导出包含以下结构：
- 按测试类别分组（功能、性能、安全等）
- 每个用例包含基本信息、测试步骤、预期结果
- 优先级标签和图标美化
- 统计信息汇总

## 🛠️ 开发指南

### 项目结构

```
ExcellentCaseExpert/
├── assets/                 # 资源文件
│   ├── icon.png           # 应用图标
│   ├── icon.ico           # Windows 图标
│   ├── icon.icns          # macOS 图标
│   └── config.template.yaml  # 配置模板
├── core/                   # 核心业务逻辑
│   ├── ocr_engine.py      # OCR 识别引擎
│   ├── ai_model_provider.py  # AI 模型提供商
│   ├── ai_test_point_analyzer.py  # 测试要点分析器
│   ├── test_case_generator.py  # 测试用例生成器
│   ├── export_manager.py  # 导出管理器
│   └── xmind_exporter.py  # XMind 导出器
├── ui/                     # 用户界面
│   ├── main_window.py     # 主窗口
│   ├── settings_dialog.py # 设置对话框
│   ├── workers.py         # 异步工作线程
│   └── widgets/           # UI 组件
├── utils/                  # 工具模块
│   ├── config_manager.py  # 配置管理
│   ├── log_manager.py     # 日志管理
│   ├── cache_manager.py   # 缓存管理
│   ├── memory_manager.py  # 内存管理
│   ├── models.py          # 数据模型
│   └── exceptions.py      # 异常定义
├── tests/                  # 测试代码
├── logs/                   # 日志文件
├── main.py                # 程序入口
├── config.yaml            # 配置文件
├── requirements.txt       # 依赖列表
└── README.md             # 本文件
```

### 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行测试并生成覆盖率报告
pytest tests/ -v --cov=. --cov-report=html

# 查看覆盖率报告
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### 代码质量检查

```bash
# 代码格式化
black .

# 代码质量检查
flake8 .

# 类型检查
mypy .
```

### 构建可执行文件

```bash
# 安装 PyInstaller
uv pip install pyinstaller

# 构建应用
pyinstaller ExcellentCaseExpert.spec

# 可执行文件位于 dist/ 目录
```

## 🐛 故障排除

### 常见问题

#### 1. OCR 识别失败

**问题**：OCR 识别不出文字或准确率低

**解决方案**：
- 确保图片清晰，分辨率足够
- 检查 PaddleOCR 和 Tesseract 是否正确安装
- 尝试调整图片对比度和亮度
- 查看日志文件 `logs/error.log` 获取详细错误信息

#### 2. AI 分析失败

**问题**：AI 分析时报错或无响应

**解决方案**：
- 检查网络连接是否正常
- 验证 API Key 是否正确配置
- 检查 API 额度是否充足
- 尝试切换其他 AI 模型
- 查看日志文件 `logs/error.log`

#### 3. 内存占用过高

**问题**：处理大文件时内存占用过高

**解决方案**：
- 在配置中降低 `max_concurrent_tasks`
- 降低 `max_memory_mb` 触发更频繁的内存清理
- 分批处理大量文件
- 关闭其他占用内存的应用

#### 4. 导出失败

**问题**：导出 XMind 或 JSON 时失败

**解决方案**：
- 检查目标目录是否有写入权限
- 确保磁盘空间充足
- 检查文件名是否包含非法字符
- 尝试导出到其他目录

### 日志文件

日志文件位置：`logs/`
- `app.log`：所有日志
- `error.log`：错误日志

查看日志以获取详细的错误信息和堆栈跟踪。

## 📝 更新日志

### v1.0.0 (2025-10-20)

- ✨ 首次发布
- 🔍 支持 OCR 文本识别（PaddleOCR + Tesseract）
- 🤖 支持 AI 智能分析（OpenAI、Qwen、Deepseek）
- 📋 支持自动生成测试用例
- 💾 支持导出 JSON 和 XMind 格式
- ⚡ 实现缓存和性能优化
- 🎨 提供现代化的图形界面
- 🌓 支持亮色/暗色主题切换
- 💬 优化用户交互和消息提示
- 📐 改进布局和视觉设计

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出建议！

### 贡献流程

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 代码规范

- 遵循 PEP 8 代码风格
- 使用 black 进行代码格式化
- 添加必要的注释和文档字符串
- 编写单元测试覆盖新功能
- 确保所有测试通过

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) - 优秀的 OCR 引擎
- [Tesseract](https://github.com/tesseract-ocr/tesseract) - 开源 OCR 引擎
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - Python GUI 框架
- [OpenAI](https://openai.com/) - 强大的 AI 模型
- [XMind](https://www.xmind.net/) - 思维导图工具

## 📧 联系方式

- 项目主页：[GitHub](https://github.com/WeiGu-S/ExcellentCaseExpert)
- 问题反馈：[Issues](https://github.com/WeiGu-S/ExcellentCaseExpert/issues)
---

<div align="center">

**如果这个项目对你有帮助，请给一个 ⭐️ Star！**

Made with ❤️ by WeiGu-S

</div>
