# Selector CLI - 开发计划

**项目**: Selector CLI - 交互式网页元素选择工具
**版本**: v1.0
**当前阶段**: Phase 1 MVP ✅ 完成
**更新日期**: 2025-11-22

---

## 总体规划

Selector CLI 是一个使用 SQL 风格语法的交互式命令行工具，用于网页元素选择、过滤和代码生成。

### 6 阶段开发路线

```
Phase 1: MVP (2-3周) ✅ 已完成
    └── 基础 REPL + 简单命令 + 基本 WHERE

Phase 2: 增强过滤 (2周) ⏳ 进行中
    └── 复杂 WHERE + 字符串操作 + 范围

Phase 3: 代码生成 (1-2周)
    └── 导出多种格式 + 文件重定向

Phase 4: 持久化 (1-2周)
    └── save/load + 变量 + 宏

Phase 5: 高级功能 (2-3周)
    └── Shadow DOM + 集合运算 + 历史

Phase 6: 完善 (1-2周)
    └── 测试 + 文档 + 性能优化
```

**总预期时间**: 9-13 周

---

## Phase 1: MVP ✅ 已完成

**目标**: 基础交互式元素选择
**状态**: ✅ 完成 (2025-11-22)
**实际时间**: 3 小时

### 已实现功能

#### 1. REPL 基础
- ✅ 交互式主循环
- ✅ 上下文提示符
  - `selector>` - 无页面
  - `selector(domain)>` - 已加载页面
  - `selector(domain)[N]>` - 集合有 N 个元素
- ✅ 命令历史
- ✅ 错误处理

#### 2. 浏览器命令
- ✅ `open <url>` - 打开网页
- ✅ 自动添加 https:// 协议
- ✅ 支持 file:// 本地文件
- ✅ 页面状态跟踪

#### 3. 扫描命令
- ✅ `scan` - 扫描页面元素
- ✅ 支持元素类型: input, button, select, textarea, a
- ✅ 提取元素属性和元数据

#### 4. 集合管理命令
- ✅ `add <target>` - 添加元素到集合
- ✅ `add <target> where <condition>` - 条件添加
- ✅ `remove <target>` - 从集合移除
- ✅ `remove <target> where <condition>` - 条件移除
- ✅ `clear` - 清空集合

#### 5. 查询命令
- ✅ `list` - 列出集合元素
- ✅ `list <target>` - 列出特定类型
- ✅ `list where <condition>` - 条件列出
- ✅ `show` - 显示集合详细信息
- ✅ `show <target>` - 显示元素详细信息
- ✅ `count` - 统计集合大小

#### 6. 目标类型
- ✅ 元素类型: `input`, `button`, `select`, `textarea`, `a`
- ✅ 单个索引: `[5]`
- ✅ 多个索引: `[1,2,3]`
- ✅ 全部: `all`

#### 7. WHERE 子句 (简单)
- ✅ 等于: `where type="email"`
- ✅ 不等于: `where id!="hidden"`
- ✅ 字段: type, id, name, placeholder, text, 等

#### 8. 实用命令
- ✅ `help` - 显示帮助
- ✅ `quit`, `exit`, `q` - 退出

#### 9. 特性
- ✅ 自动清除：打开新页面时清空元素和集合
- ✅ 完整测试套件
- ✅ 详细文档

### 可交付成果
- ✅ 工作的 REPL
- ✅ 基础命令集
- ✅ 简单过滤
- ✅ 手动测试
- ✅ 用户文档

---

## Phase 2: 增强过滤 ⏳ 下一阶段

**目标**: 复杂条件和高级过滤
**预期时间**: 2 周
**优先级**: 高

### 计划功能

#### 1. 复杂 WHERE 子句
- ⏳ 逻辑运算符
  - `and` - 与: `where type="text" and visible`
  - `or` - 或: `where type="email" or type="text"`
  - `not` - 非: `where not disabled`
- ⏳ 括号分组
  - `where (type="text" or type="email") and not disabled`
- ⏳ 优先级处理

#### 2. 字符串操作符
- ⏳ `contains` - 包含: `where text contains "Submit"`
- ⏳ `starts` - 开头: `where id starts "user_"`
- ⏳ `ends` - 结尾: `where name ends "_input"`
- ⏳ `matches` - 正则: `where text matches "^[0-9]+$"`

#### 3. 比较操作符
- ⏳ `>` - 大于: `where index > 5`
- ⏳ `>=` - 大于等于: `where index >= 10`
- ⏳ `<` - 小于: `where index < 20`
- ⏳ `<=` - 小于等于: `where index <= 30`

#### 4. 索引范围
- ⏳ `[1-10]` - 范围选择
- ⏳ `[1,3,5-8,10]` - 混合选择

#### 5. 新命令
- ⏳ `keep <condition>` - 保留符合条件的元素
- ⏳ `filter <condition>` - 过滤（移除符合条件的）

#### 6. 布尔字段
- ⏳ `visible` - 可见性
- ⏳ `enabled` - 可用性
- ⏳ `disabled` - 禁用状态
- ⏳ `required` - 必填
- ⏳ `readonly` - 只读

### 实现任务

#### 2.1 词法分析器扩展
```python
# 新增 Token 类型
- CONTAINS, STARTS, ENDS, MATCHES
- GT, GTE, LT, LTE
- LPAREN, RPAREN
- RANGE (-)
```

#### 2.2 语法分析器扩展
```python
# 复杂条件解析
def parse_complex_condition():
    - 处理 and/or/not
    - 处理括号
    - 运算符优先级
    - 构建条件树
```

#### 2.3 条件求值器
```python
# 条件树求值
def evaluate_condition_tree():
    - 递归求值
    - 逻辑运算
    - 字符串匹配
    - 数值比较
```

#### 2.4 测试
- 复杂 WHERE 子句测试
- 字符串操作测试
- 范围选择测试
- 边界情况测试

### 可交付成果
- 支持复杂 WHERE 子句的解析器
- 字符串操作符实现
- 范围选择功能
- keep/filter 命令
- 扩展测试套件
- 更新文档

### 示例

```bash
# 复杂条件
selector> add input where (type="text" or type="email") and not disabled

# 字符串操作
selector> add button where text contains "Submit" or text contains "确认"

# 范围选择
selector> add [1-10]
selector> remove [5,7-9]

# keep/filter
selector> keep where visible and enabled
selector> filter where type="hidden"

# 比较
selector> list where index > 5 and index < 20
```

---

## Phase 3: 代码生成

**目标**: 导出为可执行代码
**预期时间**: 1-2 周
**优先级**: 高

### 计划功能

#### 1. 导出命令
- ⏳ `export <format>` - 导出当前集合
- ⏳ `export <format> <target>` - 导出特定元素
- ⏳ 文件重定向: `export playwright > test.py`

#### 2. 导出格式

##### Playwright (Python)
```python
selector> export playwright

# 输出:
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto('https://example.com')

    email = page.locator('input[type="email"]')
    password = page.locator('input[type="password"]')
    submit = page.locator('button[type="submit"]')
```

##### Selenium (Python)
```python
selector> export selenium

# 输出:
from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
driver.get('https://example.com')

email = driver.find_element(By.CSS_SELECTOR, 'input[type="email"]')
password = driver.find_element(By.CSS_SELECTOR, 'input[type="password"]')
submit = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
```

##### Puppeteer (JavaScript)
```javascript
selector> export puppeteer

// 输出:
const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  await page.goto('https://example.com');

  const email = await page.$('input[type="email"]');
  const password = await page.$('input[type="password"]');
  const submit = await page.$('button[type="submit"]');
})();
```

#### 3. 数据导出

##### JSON
```json
selector> export json
[
  {
    "index": 0,
    "tag": "input",
    "type": "email",
    "selector": "input[type=\"email\"]",
    "xpath": "//input[@type='email']"
  }
]
```

##### CSV
```csv
selector> export csv
index,tag,type,selector,xpath
0,input,email,"input[type=""email""]",//input[@type='email']
```

##### YAML
```yaml
selector> export yaml
- index: 0
  tag: input
  type: email
  selector: input[type="email"]
  xpath: //input[@type='email']
```

#### 4. 选择器导出
- ⏳ `selectors` - 仅导出选择器列表
- ⏳ `xpaths` - 仅导出 XPath 列表

### 实现任务

#### 3.1 代码生成器基类
```python
class CodeGenerator:
    def generate(self, elements, url):
        pass
    def format_selector(self, element):
        pass
```

#### 3.2 具体生成器
- PlaywrightGenerator
- SeleniumGenerator
- PuppeteerGenerator
- JSONExporter
- CSVExporter
- YAMLExporter

#### 3.3 文件操作
```python
def export_to_file(content, filename):
    # 文件重定向
    # 覆盖/追加选项
```

### 可交付成果
- 3 种代码生成器 (Playwright, Selenium, Puppeteer)
- 3 种数据导出格式 (JSON, CSV, YAML)
- 文件重定向功能
- 模板系统
- 测试用例
- 导出示例文档

---

## Phase 4: 持久化

**目标**: 保存和复用工作成果
**预期时间**: 1-2 周
**优先级**: 中

### 计划功能

#### 1. 集合持久化
- ⏳ `save <name>` - 保存当前集合
- ⏳ `load <name>` - 加载已保存的集合
- ⏳ `saved` - 列出所有已保存的集合
- ⏳ `delete <name>` - 删除已保存的集合

#### 2. 变量系统
- ⏳ `set <var> = <value>` - 设置变量
- ⏳ `vars` - 列出所有变量
- ⏳ 在命令中使用: `open $homepage`

#### 3. 宏系统
- ⏳ `macro <name> { commands }` - 定义宏
- ⏳ `run <macro>` - 执行宏
- ⏳ `macros` - 列出所有宏
- ⏳ 参数化宏: `macro login {url} { open $url; scan; ... }`

#### 4. 脚本执行
- ⏳ `exec <file>` - 执行脚本文件
- ⏳ 脚本格式: `.sel` 文件
- ⏳ 批量处理

### 示例

```bash
# 保存集合
selector> add input where type="email"
selector> add input where type="password"
selector> save login_form
Saved collection 'login_form' (2 elements)

# 加载集合
selector> load login_form
Loaded collection 'login_form' (2 elements)

# 变量
selector> set homepage = https://example.com
selector> set timeout = 30
selector> open $homepage

# 宏
selector> macro analyze_form {
  scan
  add input
  add button
  list
}
selector> run analyze_form

# 脚本
# login.sel 文件:
open https://example.com/login
scan
add input where type="email"
add input where type="password"
add button where type="submit"
export playwright > login_test.py

selector> exec login.sel
```

### 实现任务

#### 4.1 存储层
```python
class Storage:
    def save_collection(name, collection)
    def load_collection(name)
    def list_collections()
    def delete_collection(name)
```

#### 4.2 变量管理
```python
class VariableManager:
    def set(name, value)
    def get(name)
    def list_all()
    def expand(text)  # 展开 $var
```

#### 4.3 宏系统
```python
class MacroManager:
    def define(name, commands, params)
    def execute(name, args)
    def list_all()
```

#### 4.4 脚本解释器
```python
class ScriptExecutor:
    def execute_file(filename)
    def execute_commands(commands)
```

### 可交付成果
- 集合持久化功能
- 变量系统
- 宏定义和执行
- 脚本执行器
- .sel 文件格式规范
- 测试用例
- 使用示例

---

## Phase 5: 高级功能

**目标**: 强大的高级特性
**预期时间**: 2-3 周
**优先级**: 中

### 计划功能

#### 1. Shadow DOM 支持
- ⏳ `scan --deep` - 深度扫描 Shadow DOM
- ⏳ 自动穿透 Shadow Root
- ⏳ Shadow DOM 路径显示
- ⏳ 支持 Closed Shadow DOM

#### 2. 集合运算
- ⏳ `union <collection>` - 并集
- ⏳ `intersect <collection>` - 交集
- ⏳ `difference <collection>` - 差集
- ⏳ `unique` - 去重

#### 3. 命令历史
- ⏳ `history` - 显示命令历史
- ⏳ `history <n>` - 显示最近 n 条
- ⏳ `!n` - 执行历史命令 n
- ⏳ `!!` - 执行上一条命令
- ⏳ Ctrl+R - 搜索历史

#### 4. 自动补全
- ⏳ Tab 补全命令
- ⏳ 补全字段名
- ⏳ 补全文件路径
- ⏳ 补全保存的集合名

#### 5. 高级查询
- ⏳ `find <pattern>` - 模糊查找
- ⏳ `locate <text>` - 按文本定位
- ⏳ `parents` - 显示父元素
- ⏳ `children` - 显示子元素

#### 6. 视觉反馈
- ⏳ `highlight` - 高亮集合中的元素
- ⏳ `highlight <target>` - 高亮特定元素
- ⏳ `unhighlight` - 取消高亮
- ⏳ 颜色编码

### 示例

```bash
# Shadow DOM
selector> scan --deep
Scanned 50 elements (15 in Shadow DOM)

# 集合运算
selector> add input
selector> save inputs
selector> add button
selector> intersect inputs  # 空集

# 历史
selector> history
1: open https://example.com
2: scan
3: add input
selector> !2  # 重新执行 scan

# 自动补全
selector> add in<TAB>
input

# 高级查询
selector> find "submit"
Found 3 elements containing "submit"

# 高亮
selector> highlight
Highlighted 5 elements in browser
```

### 实现任务

#### 5.1 Shadow DOM 扫描器
```python
class ShadowDOMScanner:
    def scan_deep(page)
    def traverse_shadow_roots(element)
    def build_shadow_path(element)
```

#### 5.2 集合运算
```python
# 已在 ElementCollection 中实现基础
def union(self, other)
def intersection(self, other)
def difference(self, other)
```

#### 5.3 历史管理
```python
class HistoryManager:
    def add(command)
    def get(index)
    def search(pattern)
    def execute(index)
```

#### 5.4 自动补全
```python
class Completer:
    def complete_command(text)
    def complete_field(text)
    def complete_file(text)
```

#### 5.5 可视化
```python
class Highlighter:
    def highlight_elements(elements, color)
    def unhighlight_all()
```

### 可交付成果
- Shadow DOM 深度扫描
- 集合运算实现
- 历史和补全系统
- 视觉反馈功能
- 性能优化
- 测试用例

---

## Phase 6: 完善

**目标**: 生产就绪
**预期时间**: 1-2 周
**优先级**: 高

### 计划任务

#### 1. 全面测试
- ⏳ 单元测试覆盖率 > 80%
- ⏳ 集成测试套件
- ⏳ 端到端测试
- ⏳ 性能测试
- ⏳ 边界情况测试

#### 2. 文档完善
- ⏳ 完整用户手册
- ⏳ API 文档
- ⏳ 教程和示例
- ⏳ FAQ
- ⏳ 故障排除指南

#### 3. 性能优化
- ⏳ 大量元素处理
- ⏳ 内存使用优化
- ⏳ 扫描速度提升
- ⏳ 缓存机制

#### 4. 错误处理
- ⏳ 友好的错误消息
- ⏳ 详细的错误提示
- ⏳ 错误恢复
- ⏳ 调试模式

#### 5. 用户体验
- ⏳ 进度指示
- ⏳ 彩色输出
- ⏳ 表格格式化
- ⏳ 配置文件支持

#### 6. 打包发布
- ⏳ PyPI 包
- ⏳ 安装脚本
- ⏳ 版本管理
- ⏳ 更新日志

### 可交付成果
- 完整测试套件
- 用户文档
- 开发者文档
- 性能报告
- 发布包
- 1.0 版本

---

## 优先级矩阵

### 高优先级 🔴
1. **Phase 2**: 增强过滤 - 核心功能扩展
2. **Phase 3**: 代码生成 - 主要价值输出
3. **Phase 6**: 完善 - 生产就绪

### 中优先级 🟡
1. **Phase 4**: 持久化 - 提升可用性
2. **Phase 5**: 高级功能 - 增强能力

---

## 里程碑

### M1: Phase 1 完成 ✅
- **日期**: 2025-11-22
- **状态**: ✅ 完成
- **交付**: MVP 可用，基础功能完整

### M2: Phase 2 完成 ⏳
- **预期**: 2025-12-06
- **目标**: 复杂查询和过滤

### M3: Phase 3 完成
- **预期**: 2025-12-20
- **目标**: 代码生成功能

### M4: Phase 4+5 完成
- **预期**: 2026-01-17
- **目标**: 高级功能完整

### M5: v1.0 发布
- **预期**: 2026-01-31
- **目标**: 生产就绪

---

## 技术债务

### 当前已知问题
1. ⚠️ 中文字符在 Windows 控制台显示乱码 (placeholder)
2. ⚠️ 大量元素时扫描速度慢
3. ⚠️ XPath 生成不够完善

### 改进计划
1. 编码问题：Phase 6 统一处理
2. 性能问题：Phase 6 优化
3. XPath：Phase 3 完善

---

## 依赖和风险

### 技术依赖
- Playwright >= 1.40.0
- Python >= 3.8

### 潜在风险
1. **Shadow DOM 兼容性** - 某些网站的 Closed Shadow DOM 无法访问
2. **动态页面** - 单页应用的动态元素可能难以捕获
3. **性能** - 复杂页面扫描可能较慢

### 缓解措施
1. 提供手动 Shadow DOM 路径指定
2. 等待策略和重试机制
3. 缓存和增量扫描

---

## 总结

**当前状态**: Phase 1 ✅ 完成
**下一步**: Phase 2 - 增强过滤
**预计完成**: 2026-01-31 (v1.0)

### 关键成功因素
1. ✅ 简洁的命令语法
2. ✅ 强大的过滤能力
3. ⏳ 多格式代码生成
4. ⏳ 良好的用户体验
5. ⏳ 完整的文档

**Phase 1 已成功完成，准备进入 Phase 2 开发！** 🚀
