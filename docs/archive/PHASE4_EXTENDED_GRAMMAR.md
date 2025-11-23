# Selector CLI - Phase 4 Extended Grammar

## 宏系统 (Macro System)

### 定义宏

**单命令宏**：
```
macro <name> <command>
```

示例：
```bash
macro scan_inputs add input
macro list_buttons list button
```

**多命令宏** (通过分号分隔):
```
macro <name> <command1>; <command2>; <command3>
```

示例：
```bash
macro analyze_form add input; add button; list
macro save_login add input where type="email"; add input where type="password"; save login_form
```

### 执行宏

```
run <macro_name>
```

示例：
```bash
run scan_inputs
run analyze_form
```

### 列出宏

```
macros
```

输出示例：
```
Macros:
  scan_inputs: add input
  list_buttons: list button
  analyze_form: add input; add button; list
```

---

## 脚本执行 (Script Execution)

### 执行脚本文件

```
exec <filepath>
```

示例：
```bash
exec login_flow.sel
exec "C:\scripts\analyze.sel"
```

### 脚本文件格式 (.sel)

脚本文件是纯文本文件，每行一个命令：

```bash
# login_flow.sel
open https://example.com/login
scan
add input where type="email"
add input where type="password"
add button where type="submit"
export playwright > login_test.py
```

**特性**：
- 每行一个命令
- `#` 开头的行为注释
- 空行被忽略
- 支持所有 REPL 命令

---

## 变量展开 (Variable Expansion)

### 设置变量（已实现）

```
set <name> = <value>
```

示例：
```bash
set base_url = https://example.com
set timeout = 30
set max_elements = 100
```

### 使用变量

使用 `$变量名` 或 `${变量名}` 引用变量：

```bash
open $base_url
open ${base_url}/login
```

**展开规则**：
1. `$name` - 简单引用
2. `${name}` - 明确边界（用于拼接）
3. 未定义变量：保持原样或报错（取决于严格模式）

示例：
```bash
set domain = example.com
set protocol = https

# 简单引用
open $protocol://$domain

# 明确边界
open ${protocol}://${domain}/login

# 路径拼接
set base = /api/v1
export json > ${base}_elements.json
```

---

## 完整语法定义

### Macro 命令

```ebnf
macro_define ::= "macro" identifier command_list
command_list ::= command (";" command)*
macro_run    ::= "run" identifier
macro_list   ::= "macros"
```

### Exec 命令

```ebnf
exec ::= "exec" (identifier | string)
```

### 变量展开

```ebnf
variable_ref     ::= "$" identifier | "${" identifier "}"
expanded_command ::= command_with_vars
                   → command_with_values (变量替换后)
```

### 完整示例工作流

```bash
# 1. 设置变量
set base_url = https://example.com
set output_dir = ./tests

# 2. 定义宏
macro analyze_inputs add input; list where visible

# 3. 打开页面（使用变量）
open $base_url/login

# 4. 执行宏
run analyze_inputs

# 5. 导出（使用变量）
export playwright > ${output_dir}/login_test.py

# 6. 保存集合
save login_elements

# 7. 执行脚本
exec analyze_all.sel
```

### 脚本文件示例

**analyze_all.sel**:
```bash
# 分析所有表单页面
set base = https://example.com

open ${base}/login
macro scan_form add input; add button; add select
run scan_form
save login_form

open ${base}/register
run scan_form
save register_form

open ${base}/profile
run scan_form
save profile_form

# 列出所有保存的集合
saved
```

---

## 实现优先级

### 阶段 1: 基础功能
1. ✅ 变量设置 (set/vars)
2. ⏳ 单命令宏 (macro name command)
3. ⏳ 宏执行 (run name)
4. ⏳ 宏列表 (macros)

### 阶段 2: 变量展开
1. ⏳ 简单变量展开 ($var)
2. ⏳ 带边界变量展开 (${var})
3. ⏳ 命令中变量替换

### 阶段 3: 高级功能
1. ⏳ 多命令宏 (分号分隔)
2. ⏳ 脚本执行 (exec)
3. ⏳ 脚本注释支持

---

## 语法限制

### 当前不支持
1. ❌ 宏参数化 `macro login {url} { open $url }`
2. ❌ 条件执行 `if/else`
3. ❌ 循环 `for/while`
4. ❌ 宏嵌套调用
5. ❌ 变量运算 `set x = $y + 1`

### 未来可能支持
1. 宏参数 (Phase 5)
2. 简单条件 (Phase 5)
3. 宏内调用宏 (Phase 5)

---

## 错误处理

### 宏定义错误
```bash
macro             # Error: Missing macro name
macro test        # Error: Missing macro command
macro test invalid_cmd  # Error: Invalid command
```

### 宏执行错误
```bash
run nonexistent   # Error: Macro 'nonexistent' not found
run test          # 如果宏内命令失败，停止执行并报错
```

### 变量展开错误
```bash
open $undefined_var  # Error: Variable 'undefined_var' not defined
```

### 脚本执行错误
```bash
exec nonexistent.sel  # Error: File not found
exec invalid.sel      # 遇到错误命令时停止执行
```

---

## 测试用例

### 宏系统测试
```python
# test_macro.py
def test_macro_define():
    "macro test add input" → 定义成功

def test_macro_run():
    "run test" → 执行宏命令

def test_macro_list():
    "macros" → 列出所有宏
```

### 变量展开测试
```python
def test_variable_expansion():
    "set url = https://test.com"
    "open $url" → 展开为 "open https://test.com"

def test_variable_boundary():
    "open ${url}/login" → 正确拼接
```

### 脚本执行测试
```python
def test_exec():
    创建 test.sel 文件
    "exec test.sel" → 逐行执行命令
```
