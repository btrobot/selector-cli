# Selector CLI - 用户手册

**版本**: v1.0 (Production Ready)
**更新日期**: 2025-11-23

## 目录

1. [快速开始](#快速开始)
2. [核心功能](#核心功能)
3. [高级功能](#高级功能)
4. [宏系统](#宏系统)
5. [脚本执行](#脚本执行)
6. [示例](#示例)
7. [故障排除](#故障排除)

---

## 快速开始

### 安装

```bash
pip install selector-cli
```

### 启动

```bash
selector
```

### 基本工作流

```bash
# 1. 打开网页
selector> open https://github.com/login

# 2. 扫描元素
selector> scan
[INFO] Scanned 3 elements
[0] input#login_field (cost: 0.044, strategy: ID_SELECTOR)
[1] input#password (cost: 0.044, strategy: ID_SELECTOR)
[2] button[type="submit"] (cost: 0.044, strategy: ID_SELECTOR)

# 3. 导出代码
selector> export playwright > github_login.py
Generated github_login.py with intelligent selectors!
```

---

## 核心功能

### 1. 浏览器控制

#### 打开网页
```bash
selector> open https://example.com
selector> open file:///path/to/local/file.html
```

#### 扫描元素
```bash
selector> scan                           # 扫描所有元素
selector> scan input button              # 只扫描 input 和 button
```

### 2. 元素管理

#### 添加元素到集合
```bash
selector> add input                      # 添加所有 input
selector> add [0,1,2]                    # 添加索引 0,1,2
selector> add input where type="email"   # 条件添加
```

#### 查看集合
```bash
selector> list                           # 列出所有元素
selector> list input                     # 只列出 input
selector> show                           # 显示详细信息
selector> count                          # 统计数量
```

#### 过滤集合
```bash
selector> keep where visible and enabled # 保留可见且启用的
selector> filter where type="hidden"     # 移除隐藏的
```

### 3. 智能选择器生成 (Element Locator)

Selector CLI 使用 **17种智能策略** 自动生成最优选择器：

**策略类型**:
- **P0 (最佳)**: ID选择器、data-testid、label-for
- **P1 (优秀)**: type+name、type+placeholder、href
- **P2 (良好)**: aria-label、title、class_unique
- **P3 (一般)**: nth-of-type、text_content

**成本模型**:
- 稳定性 (40%)
- 可读性 (30%)
- 速度 (20%)
- 维护性 (10%)

**示例输出**:
```
[0] input#email-input (cost: 0.044, strategy: ID_SELECTOR)
[1] input[type="text"] (cost: 0.165, strategy: TYPE_NAME)
[2] button:nth-of-type(1) (cost: 0.570, strategy: XPATH_POSITION)
```

### 4. 代码导出

**支持的格式**:
- Python: Playwright, Selenium
- JavaScript: Puppeteer
- 数据: JSON, CSV, YAML

**示例**:
```bash
selector> export playwright > test.py
selector> export selenium
selector> export json
selector> export csv > elements.csv
```

**生成的代码示例**:
```python
# 使用智能选择器 (ID - 最稳定)
email = page.locator('#email-input')
password = page.locator('#password-input')
submit = page.locator('#submit-btn')
```

---

## 高级功能

### 1. 复杂WHERE子句

**逻辑运算符**:
```bash
selector> add input where type="email" and visible
selector> add button where text contains "Submit" or text contains "确认"
selector> remove where not enabled
```

**字符串操作**:
- `contains` - 包含
- `starts` - 开头匹配
- `ends` - 结尾匹配
- `matches` - 正则匹配

**比较操作**:
```bash
selector> list where index > 5 and index < 20
selector> list where selector_cost < 0.2  # 高质量选择器
```

### 2. 集合运算

```bash
# 合并两个集合
collectionA> union collectionB

# 交集（共同元素）
collectionA> intersect collectionB

# 差集（在A但不在B）
collectionA> difference collectionB

# 去重
collection> unique
```

### 3. 元素高亮

```bash
# 高亮当前集合
selector> highlight

# 高亮特定元素
selector> highlight input                    # 所有 input
selector> highlight [0,1,2]                  # 索引 0,1,2
selector> highlight button where text contains "Submit"

# 取消高亮
selector> unhighlight
```

**颜色主题** (可选):
- `default` (红色) - 默认
- `success` (绿色) - 成功状态
- `info` (蓝色) - 信息状态
- `warning` (黄色) - 警告状态

### 4. 命令历史

```bash
selector> history              # 显示所有历史
selector> history 10           # 显示最近10条
selector> !5                   # 执行第5条命令
selector> !!                   # 执行上一条
```

### 5. 自动补全

按 **Tab** 键补全：
- 命令名称
- 字段名 (id, name, type, ...)
- 变量名 ($var)
- 文件路径
- 保存的集合名

---

## 宏系统

### 定义宏 (参数化)

```bash
# 基本宏
selector> macro quick-scan scan; add input; add button; list

# 参数化宏
selector> macro analyze-form {url} {
  open {url}
  scan
  add input
  add button
  list
}

# 使用参数
selector> run analyze-form https://github.com/login
```

**参数使用场景**:
```bash
# 登录表单分析
selector> macro login-form {url} {username_field} {password_field} {
  open {url}
  add input where name='{username_field}'
  add input where name='{password_field}'
  add button where type='submit'
  export playwright
}

selector> run login-form https://example.com/login user pass
```

### 管理宏

```bash
selector> macros              # 列出所有宏
selector> macro test scan     # 定义新宏
selector> run test            # 执行宏
```

---

## 脚本执行

### 创建脚本文件 (.sel)

**示例: login_test.sel**
```bash
# 打开登录页面
open https://github.com/login

# 扫描并收集表单元素
scan
add input where type="email" or type="text"
add input where type="password"
add button where type="submit"

# 验证收集的元素
list

# 导出测试代码
export playwright > github_login_test.py
```

### 执行脚本

```bash
selector> exec login_test.sel
```

**脚本特性**:
- 支持注释 (以 `#` 开头)
- 支持空行
- 支持所有 Selector CLI 命令
- 错误时显示行号和错误信息

---

## 变量系统

### 设置变量

```bash
selector> set homepage = https://example.com
selector> set timeout = 30
```

### 使用变量

```bash
selector> open $homepage
selector> set url = https://github.com/login
selector> open $url
```

### 查看变量

```bash
selector> vars
Variables:
  homepage = https://example.com
  timeout = 30
```

**变量持久化**: 变量自动保存到 `~/.selector-cli/vars.json`，重启后仍然有效。

---

## 集合持久化

### 保存集合

```bash
selector> add input where type="email"
selector> add input where type="password"
selector> save login_form
Saved collection 'login_form' (2 elements)
```

### 加载集合

```bash
selector> load login_form
Loaded collection 'login_form' (2 elements)
```

### 管理保存的集合

```bash
selector> saved          # 列出所有保存的集合
selector> delete old_form # 删除集合
```

---

## 示例

### 示例 1: 自动化测试生成

```bash
# 1. 打开目标页面
selector> open https://github.com/login

# 2. 扫描并收集登录表单元素
selector> scan
selector> keep where visible
selector> list

# 输出:
# [0] input#login_field (cost: 0.044, strategy: ID_SELECTOR)
# [1] input#password (cost: 0.044, strategy: ID_SELECTOR)
# [2] button[type="submit"] (cost: 0.044, strategy: ID_SELECTOR)

# 3. 导出测试代码
selector> export playwright > github_login_test.py
```

**生成的代码**:
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto('https://github.com/login')

    # 智能选择器 (基于成本优化)
    login_field = page.locator('#login_field')
    password = page.locator('#password')
    submit_button = page.locator('#submit-btn')

    # 示例: 填充表单
    login_field.fill('your-username')
    password.fill('your-password')
    submit_button.click()

    browser.close()
```

### 示例 2: 复杂表单分析

```bash
# 创建参数化宏
selector> macro analyze-form {url} {
  open {url}
  scan
  keep where visible and enabled and not disabled
  list
}

# 分析多个表单
selector> run analyze-form https://github.com/login
selector> save github_login

selector> run analyze-form https://google.com
selector> save google_search

# 比较两个表单
selector> clear
selector> load github_login
selector> union google_search
selector> list
```

### 示例 3: 批量处理

创建脚本 `batch_analyze.sel`:
```bash
# 分析的URL列表
set urls = https://github.com/login,https://google.com,https://example.com

# 分析每个URL
macro quick {url} {
  open {url}
  scan
  export json > {url.replace('https://', '').replace('/', '_')}.json
}

# 批量执行
run quick https://github.com/login
run quick https://google.com
run quick https://example.com
```

执行:
```bash
selector> exec batch_analyze.sel
```

---

## 故障排除

### 问题 1: 无法打开浏览器

**错误**: 浏览器未能启动

**解决**:
```bash
# 确保 Playwright 已安装
playwright install chromium
```

### 问题 2: 元素未找到

**错误**: 选择器未匹配到元素

**可能原因**:
1. 页面未完全加载 - 等待几秒再试
2. 元素在 iframe 或 Shadow DOM 中
3. 元素是动态生成的

**解决**:
```bash
selector> scan  # 重新扫描
selector> list  # 检查当前元素
```

### 问题 3: 选择器不稳定

**现象**: 同样的操作有时成功有时失败

**解决**:
- 检查 `selector_cost` 值（越低越稳定）
- 使用 `keep where selector_cost < 0.2` 只保留高质量选择器
- 优先使用 ID 选择器

### 问题 4: 宏执行失败

**错误**: Macro 'name' expects X parameters

**解决**: 确保提供正确数量的参数
```bash
# 如果宏定义为: macro test {p1} {p2} command
# 执行时需提供: run test arg1 arg2
```

### 问题 5: 脚本执行错误

**错误**: Error at line X

**解决**:
- 检查脚本语法
- 确保命令正确
- 参考行号附近的错误

---

## 性能优化

**扫描性能**:
- 平均 5ms/元素
- 支持 200元素/秒

**优化建议**:
1. 使用 `scan input button` 只扫描需要的类型
2. 使用 `keep where selector_cost < 0.2` 过滤高质量选择器
3. 对大型页面使用集合运算而非多次扫描

---

## 最佳实践

1. **优先使用 ID 选择器**: 最稳定，成本最低 (0.044)
2. **使用 data-testid**: 如果页面提供，这是第二好的选择
3. **避免复杂 XPath**: 成本高 (0.40+) 且难以维护
4. **参数化宏**: 对重复任务使用宏，提高可维护性
5. **脚本化**: 将复杂工作流保存为 .sel 脚本
6. **保持集合简洁**: 使用 keep/filter 只保留需要的元素

---

## 获得帮助

- **文档**: 查看 DEVELOPMENT_PLAN.md 了解技术细节
- **示例**: 查看 examples/ 目录
- **报告问题**: 提交到 GitHub Issues

---

**Selector CLI v1.0** - 智能网页元素选择工具
© 2025
