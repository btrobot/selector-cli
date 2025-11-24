# Selector CLI - 系统架构分析文档（第一部分）

**项目版本**: v1.0.6 (main分支)
**分析日期**: 2025-11-24
**代码总行数**: 约4,800行
**项目状态**: 生产就绪（95%+完成度）

---

## 1. 项目概述

### 1.1 项目定位
Selector CLI 是一个智能网页元素选择器和代码生成工具，主要面向自动化测试开发者和网页爬虫工程师。项目提供交互式命令行界面，通过17种智能选择器策略和4维成本模型，自动生成最优的、稳定的CSS/XPath选择器，并支持导出为6种格式的代码（Playwright、Selenium、Puppeteer、JSON、CSV、YAML）。

### 1.2 核心功能特性

- **智能选择器生成**: 17种定位策略，基于4维成本模型自动选择最优选择器
- **多格式代码导出**: 支持6种导出格式（Playwright、Selenium、Puppeteer、JSON、CSV、YAML）
- **复杂过滤系统**: Phase 2增强过滤，支持逻辑运算符、字符串操作、比较操作
- **三层架构模型**: v2.0引入（candidates → temp → workspace）的渐进式元素管理
- **完整持久化**: 集合、变量、脚本、历史的全方位持久化
- **元素高亮可视化**: 实时高亮网页元素
- **命令历史和补全**: readline集成，支持历史查询和Tab补全
- **参数化宏系统**: 定义和运行参数化工作流

### 1.3 技术栈

```
核心技术:
├── 基础语言: Python 3.8+
├── 浏览器自动化: Playwright ≥1.40.0
├── 命令行UI: Rich (Terminal formatting)
├── 配置管理: PyYAML
└── 数据持久化: JSON / CSV / YAML
```

### 1.4 性能基准

```
指标              实际值      目标        倍数
────────────────────────────────────────
扫描速度         5ms/元素    <10ms       2x ✅
大集合处理       0.10s/20    <5s         50x ✅
吞吐量           200/s       >100/s      2x ✅
选择器生成       5ms/元素    -           - ✅
────────────────────────────────────────
```

---

## 2. 项目结构分析

### 2.1 双版本架构

项目包含两个版本：
- **selector_cli v1**: 原始版本，代码量约4,800行
- **selector_cli_v2**: 增强版本，采用三层架构（v2.0）

### 2.2 源代码目录结构

```
src/
├── selector_cli/                      # v1.0版本
│   ├── main.py                        # 主入口（42行）
│   ├── cli/repl/main.py               # REPL主循环（196行）
│   ├── commands/
│   │   └── executor.py                # 命令执行器（40523行，包含v2代码）
│   ├── core/                          # 核心业务逻辑
│   │   ├── element.py                 # 元素模型（114行）
│   │   ├── collection.py              # 元素集合（224行）
│   │   ├── browser.py                 # 浏览器管理（~100行）
│   │   ├── scanner.py                 # 元素扫描器（307行）
│   │   ├── context.py                 # 执行上下文（201行）
│   │   ├── completer.py               # Tab补全（~180行）
│   │   ├── highlighter.py             # 元素高亮（224行）
│   │   ├── macro.py                   # 宏系统（94行）
│   │   ├── storage.py                 # 数据持久化（126行）
│   │   └── variable_expander.py       # 变量展开（65行）
│   ├── core/locator/                  # 定位策略引擎（BONUS系统）
│   │   ├── strategy.py                # 17种策略（19,950行）
│   │   ├── strategy_fixed.py          # 备选策略（21,853行）
│   │   ├── cost.py                    # 4维成本模型（9,945行）
│   │   ├── validator.py               # 验证器（7,570行）
│   │   ├── scanner_integration.py     # 扫描器集成（5,574行）
│   │   └── logging.py                 # 日志系统（3,950行）
│   ├── parser/                        # 命令解析器
│   │   ├── lexer.py                   # 词法分析器（412行）
│   │   ├── parser.py                  # 语法分析器（856行）
│   │   └── command.py                 # 命令数据模型（113行）
│   └── generators/                    # 代码生成器
│       ├── base.py                    # 基类（93行）
│       ├── playwright_gen.py          # Playwright生成器（126行）
│       ├── selenium_gen.py            # Selenium生成器（120行）
│       ├── puppeteer_gen.py           # Puppeteer生成器（114行）
│       └── data_exporters.py          # 数据导出（127行）
└── selector_cli_v2/                   # v2.0版本（三层架构）
    ├── repl.py                        # v2 REPL主循环（249行）
    └── v2/
        ├── command.py                 # v2命令模型（5,072行）
        ├── context.py                 # v2执行上下文（13,206行）
        ├── executor.py                # v2执行器（17,836行）
        └── parser.py                  # v2解析器（14,792行）
```

### 2.3 测试结构

```
tests/
├── test_mvp.py                      # Phase 1测试（~110行）
├── test_phase2.py                   # Phase 2测试
├── test_phase3.py                   # Phase 3测试
├── test_complete.py                 # 综合测试
├── test_integration.py              # 集成测试
└── test_locator.py                  # Element Locator测试
```

### 2.4 文档结构

```
docs/
├── USER_MANUAL.md                   # 用户手册
├── DEVELOPMENT_PLAN.md              # 开发计划
├── FAQ.md                           # 常见问题
├── PROGRESS_TABLE.md                # 进度追踪
├── INTEGRATION_REPORT.md            # Element Locator集成报告
├── DOCS_GUIDE.md                    # 文档指南
└── [本系列分析文档]
```

---

## 3. 系统架构设计

### 3.1 核心架构思想

#### 3.1.1 三层架构模型（v2.0）

```
┌─────────────────────────────────────────────────────────┐
│                    用户交互层 (REPL)                       │
└──────────────────────┬────────────────────────────────────┘
                       │
┌──────────────────────▼────────────────────────────────────┐
│                 命令处理层 (Parser + Executor)            │
│                                                          │
│  ┌─────────┐      ┌──────────────┐      ┌──────────┐  │
│  │ Parser  │  →   │  CommandV2   │  →   │ Executor │  │
│  └─────────┘      └──────────────┘      └──────────┘  │
└──────────────────────┬────────────────────────────────────┘
                       │
┌──────────────────────▼────────────────────────────────────┐
│                三层状态管理 (ContextV2)                   │
│                                                          │
│  ┌──────────────┐    ┌──────────┐    ┌──────────────┐  │
│  │ candidates   │ →  │   temp   │ →  │  workspace   │  │
│  │ (SCAN结果)    │    │(FIND临时)│    │(用户集合)     │   │
│  └──────────────┘    └──────────┘    └──────────────┘  │
└──────────────────────────────────────────────────────────┘
```

**三层流转逻辑**：
- **candidates**: 所有通过 `scan` 命令扫描的元素，是原始数据源
- **temp**: 通过 `find` 命令查询DOM的临时结果（30秒过期），用于渐进式筛选
- **workspace**: 用户通过 `add` 命令持久化保存的元素集合，最终导出数据来源

#### 3.1.2 命令处理流水线

```
输入字符串
    ↓
┌─────────────────────────┐
│  Lexer（词法分析器）     │  → Token序列
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│  Parser（语法分析器）    │  → Command对象
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│  Executor（执行器）      │  → 操作结果
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│  Context（执行上下文）   │  → 状态更新
└─────────────────────────┘
```

---

## 4. 各版本架构对比

### 4.1 v1.0 版本架构

```
┌─────────────────────────┐
│    REPL (交互式循环)     │
 └──────────┬─────────────┘
            ↓
┌─────────────────────────┐
│  Parser + Executor      │
│  (命令解析 + 执行)       │
 └──────────┬─────────────┘
            ↓
┌─────────────────────────┐
│  Context (单一层集合)     │
│  • 单个元素列表          │
│  • 简单过滤             │
│  • 基础持久化           │
└─────────────────────────┘
```

**特点**：
- 单层集合设计
- 简单直接，适合MVP阶段
- 模块清晰，职责单一
- 性能良好（5ms/元素）

### 4.2 v2.0 版本架构（三层架构）

```
┌──────────────────────────┐
│    SelectorREPLV2         │
│  (增强REPL主循环)         │
 └───────────▲─────────────┘
             │
┌────────────┼──────────────┐
│   ParserV2 │   ExecutorV2 │
│ (增强解析) │  (三层执行)  │
 └───────────┴──────────────┘
             │
┌─────────────▼──────────────┐
│        ContextV2           │
│  ┌─────┐  ┌─────┐  ┌─────┐  │
│  │Cand │→ │Temp │→ │Work │
│  └─────┘  └─────┘  └─────┘  │
│  (SCAN)  (FIND)   (集合)    │
└──────────────────────────────┘
```

**升级点**：
1. **三层状态管理**: candidates → temp → workspace
2. **智能查询**: `.find` 命令直接查询DOM
3. **渐进式筛选**: 从temp层逐步精简到workspace
4. **来源追踪**: 所有操作可追踪到数据来源（from candidates/temp/workspace）
5. **过期机制**: temp层30秒后自动过期，防止使用过时数据

**优势**：
- 支持复杂探索式工作流
- 数据分级明确，避免污染原始数据
- temp缓存提升性能
- 渐进式操作更直观

---

## 5. 模块划分与职责

### 5.1 解析层（Parser Layer）

```
parser/
├── lexer.py          (412行) - 词法分析器
├── parser.py         (856行) - 语法分析器
└── command.py        (113行) - 命令数据模型

v2/
└── parser.py         (14,792行) - v2增强解析器
```

**职责**：
- **Lexer**: 将输入字符串转换为Token序列
  - Token类型：KEYWORD、IDENTIFIER、STRING、NUMBER、OPERATOR等
  - 支持URL友好解析（支持`:`, `/`, `.`等特殊字符）
  - 支持字符串引号转义

- **Parser**: 构建抽象语法树（AST）
  - 递归下降解析器
  - WHERE子句解析（树形结构）
  - 复杂逻辑运算符（and, or, not）

- **Command Model**: 定义命令数据结构
  - CommandV1: verb-target-condition模型
  - CommandV2: 扩展支持三层架构、模式、来源等

### 5.2 执行层（Executor Layer）

```
commands/
└── executor.py       (40,523行) - 主要执行器

v2/
└── executor.py       (17,836行) - v2执行器
```

**核心功能**：
- 命令分发：根据verb调用对应处理器
- 元素操作：add/remove/list/count等
- 条件过滤：WHERE子句求值
- 来源管理：三层架构数据流转
- 结果格式化：人性化的输出

### 5.3 元素管理层（Element Management）

```
core/
├── element.py        (114行) - 元素模型
├── collection.py     (224行) - 集合操作
├── scanner.py        (307行) - 元素扫描器
└── browser.py        (~100行) - 浏览器管理
```

**Element模型**（src/core/element.py:1-115）：
- 基础属性：tag, type, text, id, name, classes
- 定位信息：selector, xpath, path
- **策略元数据**：selector_cost, strategy_used（4维成本模型标记）
- 状态：visible, enabled, disabled
- Shadow DOM支持：in_shadow, shadow_host, shadow_path
- Playwright集成：locator, handle

**ElementCollection**（src/core/collection.py:1-160）：
- 集合操作：filter, union, intersection, difference
- 快速索引：`_index: Dict[int, Element]`提供O(1)查找
- 原地操作：union_in_place, intersect_in_place等
- 序列化：to_dict/from_dict支持JSON持久化

**ElementScanner**（src/core/scanner.py:1-308）：
- 多类型扫描：input, button, a, select, textarea
- LocationStrategyEngine集成：每元素5ms选择器生成
- 稳定性验证：自动检查选择器唯一性
- 智能降级：策略失败时回退到基础选择器

### 5.4 核心算法层（Core Algorithm - BONUS系统）

```
core/locator/
├── strategy.py        (19,950行) - 17种策略实现
├── cost.py            (9,945行) - 4维成本模型
└── validator.py       (7,570行) - 验证器
```

这是最核心的创新模块，详细分析见第三部分《核心算法分析文档》。

### 5.5 代码生成器（Code Generators）

```
generators/
├── base.py            (93行) - 基类
├── playwright_gen.py  (126行) - Playwright生成
├── selenium_gen.py    (120行) - Selenium生成
├── puppeteer_gen.py   (114行) - Puppeteer生成
└── data_exporters.py  (127行) - 数据导出
```

设计特点：
- 模板方法模式：基类定义接口，子类实现具体生成
- 统一API：generate_code(elements, options)
- 语义映射：Element属性 → 框架特定API
- 可读性优先：生成代码带注释和描述

---

## 6. 依赖关系分析

### 6.1 核心依赖树

```
┌─────────────────────────────┐
│   Main Entry Point          │
│   (src/selector_cli/main.py)│
└──────────┬──────────────────┘
           ↓
┌─────────────────────────────┐
│   SelectorREPL / SelectorREPLV2
│   (repl/main.py | v2/repl.py)
└──────────┬──────────────────┘
           ↓
┌────────────────────────────────┐
│  Parser ┼ Executor              │
└──────────┬───────────────────────┘
           ↓
┌────────────────────────────────┐
│  Context / ContextV2          │ ←───┐
└──────────┬───────────────────────┘     │
           ↓                            │ REFERENCE
┌────────────────────────────────┐     │
│  Element (Models)              │ ←───┘
│  ElementCollection             │
└──────────┬───────────────────────┘
           ↓
┌────────────────────────────────┐
│  Scanner ┼ BrowserManager       │
│        ↓
│  LocationStrategyEngine ←──── LocationStrategyEngine
│                                   (cost.py, validator.py)
└────────────────────────────────┘
```

### 6.2 关键依赖路径

**用户输入 → 元素生成**：
```
REPL._run() → Parser.parse() → Executor.execute_scan()
                                         ↓
                      Scanner.scan() → LocationStrategyEngine.find_best_locator()
                                         ↓
                                        17 strategies → CostCalculator → Validator
                                         ↓
                                      Element.selector (with cost metadata)
```

**命令执行 → 状态更新**：
```
REPL._run() → Parser.parse() → ExecutorV2.execute_find()
                                         ↓
                        ContextV2.temp = filtered_elements
                                         ↓
                        REPL._get_prompt() shows temp count
```

**代码生成 → 文件输出**：
```
Executor.execute_export() → GeneratorFactory.create()
                                         ↓
                        PlaywrightGenerator.generate_code()
                                         ↓
                                    sys.stdout.write()
```

### 6.3 循环依赖检查

项目架构良好，无循环依赖：
```
✅ Parser → Command (数据单向流动)
✅ Executor → Context (单向依赖)
✅ Scanner → Element (单向依赖)
✅ Locator → Element (单向依赖)
```

### 6.4 模块耦合度分析

**低耦合模块**（依赖<3）：
- element.py (耦合度: 1) - 纯数据模型
- collection.py (耦合度: 1) - 基于Element
- parsers/command.py (耦合度: 2) - 数据定义

**中度耦合模块**（依赖3-5）：
- browser.py (耦合度: 3)
- scanner.py (耦合度: 4)
- storage.py (耦合度: 3)

**高耦合模块**（依赖>5）：
- executor.py (耦合度: 7) - 作为协调器合理
- context.py (耦合度: 6) - 管理状态合理
- parser.py (耦合度: 6) - 导入多个Token类型合理

---

## 7. 目录与文件注释配置

为了确保IDE和开发工具的充分支持，建议添加如下文件注释配置：

### 7.1 Python Package配置

每个包目录应包含 `__init__.py` 文件，便于：
- 控制包导入行为
- 定义 `__all__` 公开API
- 添加模块级文档字符串

```python
# src/selector_cli/__init__.py
"""
Selector CLI - v1.0
Interactive web element selection and code generation tool
"""

__version__ = "1.0.6"
__author__ = "Selector CLI Team"
```

### 7.2 推荐IDE配置

**VS Code用户**：
在项目根目录添加 `.vscode/settings.json`：
```json
{
  "python.analysis.autoImportCompletions": true,
  "python.analysis.includeUserSymbols": true,
  "python.analysis.diagnosticSeverityOverrides": {
    "reportMissingImports": "none",
    "reportMissingModuleSource": "none"
  }
}
```

**PyCharm用户**：
- 将 `src/` 标记为 Sources Root
- 启用 "Optimize imports on the fly"
- 配置 import resolution order

### 7.3 Python路径配置

在代码中使用相对导入，避免硬编码sys.path：

```python
# 不推荐
import sys
sys.path.insert(0, '...')

# 推荐
from ..core.element import Element
from .command import CommandV2
```

如果使用相对导入不便，可考虑在 `setup.py` 中配置 entry points：

```python
entry_points={
    'console_scripts': [
        'selector=selector_cli.main:main',
        'selector-v2=selector_cli_v2.repl:main'
    ],
}
```

这将确保Python能够正确解析导入路径，无需手动修改sys.path。

---

## 8. 总结与后续

### 8.1 v1.0 → v2.0 演进价值

**解决的问题**：
- v1的单层集合无法支持复杂探索式工作流
- 每次操作需要重新扫描，性能低
- 数据污染风险（误操作无法回退）
- 无法追踪数据来源

**v2的优势**：
- 三层架构提供清晰的数据生命周期
- temp层缓存减少重复扫描
- candidates保持原始数据不变
- workspace作为最终导出层，保证数据质量

### 8.2 性能优化点

1. **缓存机制**:
   - temp层30秒TTL (src/selector_cli_v2/v2/context.py:29)
   - LocationStrategyEngine验证缓存 (src/core/locator/strategy.py:112)

2. **异步IO**:
   - 全程async/await使用
   - BrowserManager单例复用
   - ElementScanner批量获取属性

3. **数据结构优化**:
   - ElementCollection使用 `_index` 字典提供O(1)查找
   - 避免重复属性计算

### 8.3 下一步文档

下一部分将详细分析：
- **核心模块功能**：每个模块的接口设计和实现细节
- **定位策略算法**：17种策略的详细实现
- **成本计算模型**：4维成本计算逻辑
- **验证系统**：3级验证原理

---

**文档索引**: 📂 [系统架构分析文档 - 第一部分] | [核心模块详细分析文档 - 第二部分] | [算法与数据流分析文档 - 第三部分]

**生成时间**: 2025-11-24
**代码版本**: main分支 (commit: 1846e47)
