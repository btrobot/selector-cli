# Selector CLI 三层架构设计文档

## 目录
1. [设计理念](#设计理念)
2. [三层架构详解](#三层架构详解)
3. [核心命令语法](#核心命令语法)
4. [使用场景与工作流程](#使用场景与工作流程)
5. [设计原则](#设计原则)

---

## 设计理念

### 核心思想：探索-精炼-确认

Selector CLI 的设计围绕**元素的探索与确认流程**展开，模拟人类分析网页时的思维模式：

1. **探索（Explore）**："这个页面有什么可交互的元素？"
2. **精炼（Refine）**："让我看看这些按钮中哪个是我要的"
3. **确认（Confirm）**："这个元素有价值，保存起来研究"

基于此，我们设计了三层存储架构，分别对应三种不同的用户意图和元素生命周期。

### 存储哲学

所有查询命令（`scan`/`find`）**统一存储到 temp**，差异在于**使用模式**：

- **scan**：宽泛采集，用于**探索未知**
- **find**：精准查询，用于**定位已知**
- **temp**：当前查询结果（覆盖语义），支持反复精炼
- **workspace**：确认有价值元素的持久存储

---

## 三层架构详解

### 1. Candidates（候选集）

**来源**：`scan` 命令
**用途**：可能有兴趣的元素集合
**生命周期**：持久（页面级，直到下次 scan）
**用户意图**："先收下来看看"

```bash
scan              # 探索页面，存入 candidates
scan +img         # 扩展探索范围，加入 img
scan img          # 专注探索 img，清空其他
```

**特点**：
- 页面加载后执行一次
- 支持增量扩展（`+tag`）和覆盖（`tag`）
- 作为全局探索层，元素相对稳定

### 2. Temp（当前查询结果）

**来源**：`find` / `.find` 命令
**用途**：当前查询结果，支持精炼
**生命周期**：瞬时（直到下次查询覆盖）
**用户意图**："当前查询结果"

```bash
find button           # 查询按钮 → temp
.find where visible   # 精炼结果 → temp（覆盖）
find input            # 新查询 → temp（覆盖）
```

**特点**：
- 反复覆盖的草稿纸
- 支持链式精炼（`.find`）
- 被下次查询覆盖，不影响其他层

### 3. Workspace（工作区）

**来源**：`add` 命令
**用途**：确认有价值的元素
**生命周期**：会话级持久
**用户意图**："这个真的有用"

```bash
add temp              # 将 temp 移到 workspace
add workspace [1,3]   # 从 candidates 或 temp 选择添加
```

**特点**：
- 累积确认的元素
- 用于预览（preview）、高亮（highlight）
- 跨查询持久保存

### 架构关系图

```
candidates   ← scan 存入
temp         ← find 存入（覆盖）
workspace    ← add 存入（累积）
```

---

## 核心命令语法

### scan - 探索命令

**语义**：探索页面元素，扩展候选集

**语法**：
```bash
scan              # 扫描默认原子元素（button/input/select/textarea/a）
scan +img         # 扩展：默认 + img
scan +img +span   # 扩展：默认 + img + span
scan img          # 覆盖：只扫描 img
scan img span     # 覆盖：只扫描 img 和 span
```

**默认原子元素**（5个）：
- `button` - 按钮
- `input` - 输入框
- `select` - 下拉选择
- `textarea` - 多行文本
- `a` - 链接

**存储行为**：**覆盖 temp**
**使用建议**：页面加载后执行，作为全局探索

### find - 定位命令

**语义**：精准查询特定元素，精炼结果

**语法**：
```bash
find button                 # 查询所有 button
find input where visible    # 带条件的查询
find div where class contains "modal"  # 查询容器

# 精炼模式（从 temp 过滤）
.find where visible         # 过滤出可见元素
.find where text contains "Login"  # 进一步过滤
```

**支持的所有 HTML 元素**：任何有效的 HTML 标签
**存储行为**：**覆盖 temp**
**使用建议**：用于快速试探和精炼，反复使用

### add - 确认命令

**语义**：将临时结果确认到工作区

**语法**：
```bash
add temp              # 将 temp 添加到 workspace
add workspace [1,3,5]  # 从当前视图选择添加
```

**存储行为**：temp → workspace（累积）
**使用建议**：确认元素有价值后执行

---

## 使用场景与工作流程

### 场景 1：分析表单页面（登录）

```bash
# 页面加载
open https://example.com/login

# 第一步：探索核心交互元素
scan
# temp: [button x3, input x2, select x1, a x5]
# 共 11 个元素

# 第二步：探索表单整体结构
find form where id="login-form"
# temp: [form x1]

# 第三步：从表单内探索输入框
find input
# temp: [input#username, input#password]

# 第四步：精炼到密码框
.find where type="password"
# temp: [input#password]

# 第五步：确认有价值
add workspace
# workspace: [input#password]

# 第六步：继续探索按钮
find button
# temp: [button x3]

# 第七步：精炼到登录按钮
.find where text contains "Login"
# temp: [button#login]

# 第八步：确认
add workspace
# workspace: [input#password, button#login]

# 第九步：预览研究
preview workspace
# 高亮显示这两个元素，分析选择器
```

### 场景 2：分析商品列表页

```bash
# 第一步：探索核心交互
scan
# temp: [button x5, input x1, select x2, a x20]

# 第二步：发现图片不够，扩展探索范围
scan +img
# temp: [原有 + img x30]
# 共 58 个元素

# 第三步：图片太多，只关注主图
scan img where class contains "main"
# temp: [img x5]

# 第四步：挑选主图加入工作区
add workspace [1,3,5]
# workspace: [3 个主图]

# 第五步：探索购买按钮
find button where text contains "Buy"
# temp: [button x3]

# 第六步：确认
add workspace
# workspace: [3 个主图, 3 个购买按钮]

# 第七步：高亮所有元素
preview workspace
```

### 场景 3：快速试探（不保存）

```bash
# 快速验证页面是否有登录按钮
find button where text contains "Login"

# 看一眼就丢弃（不 add）
# temp 30 秒后自动清空
```

---

## 设计原则

### 1. 语义明确原则

- `scan` = 探索（宽泛、增量/覆盖）
- `find` = 定位（精准、覆盖）
- `add` = 确认（累积）
- `.find` = 精炼（链式）

### 2. 存储统一原则

所有查询命令（`scan`/`find`）**统一存储到 temp**，差异在于**使用模式**：

- `scan`：支持增量扩展（`+tag`）和覆盖（`tag`）
- `find`：总是覆盖，支持精炼

### 3. 零噪音原则

**默认只探索原子元素**（5个），避免容器和装饰元素带来的噪音：

✅ **默认包含**：button, input, select, textarea, a
❌ **需要扩展才包含**：img, form, div, span, label

### 4. 覆盖语义原则

- **temp**：查询覆盖，每次 `find`/`scan` 都会覆盖上次结果
- **candidates**：页面级持久，作为全局探索层
- **workspace**：会话级累积，只增不减（除非手动 clear）

### 5. 渐进式探索原则

支持从宽泛到精准的自然探索流程：

```bash
scan              # 宽泛：页面有什么？
find button       # 精准：按钮有哪些？
.find where visible  # 精炼：可见的按钮
add workspace     # 确认：保存有用的
```

---

## 命令与其他系统交互

### 与 `preview` 命令

```bash
preview workspace      # 预览工作区元素
preview temp           # 预览临时结果
preview candidates     # 预览候选集
```

### 与 `highlight` 命令

```bash
highlight workspace    # 高亮工作区所有元素
highlight temp [1,3]   # 高亮临时结果的部分
```

### 与 `list` / `count` 命令

```bash
list workspace         # 列出工作区元素详情
count temp             # 统计临时结果数量
```

---

## 最佳实践

### ✅ 推荐做法

1. **页面加载后先 scan**：建立全局探索层
   ```bash
   open https://example.com
   scan
   ```

2. **使用 find 快速试探**：不确定时快速验证
   ```bash
   find button where text contains "Submit"
   # 看一眼，不 add = 临时验证
   ```

3. **确认价值再 add**：避免 workspace 臃肿
   ```bash
   .find where visible
   # 确认有用
   add workspace
   ```

4. **定期清理 workspace**：长时间分析后
   ```bash
   clear workspace
   ```

### ❌ 避免做法

1. **不要 scan 所有元素**：噪音太大
   ```bash
   scan +img +span +div +form  # ❌ 可能 500+ 元素
   ```

2. **不要滥用 add**：workspace 只存有价值的
   ```bash
   find input
   add workspace      # ❌ 所有输入框都存？没必要
   ```

3. **忘记 add 会导致结果丢失**：temp 会被下次查询覆盖
   ```bash
   find button
   # ... 执行其他查询
   find input         # temp 被覆盖
   list temp          # ❌ 显示的是 input，不是 button
   ```

---

## 未来扩展

### 支持的扩展语法

```bash
scan +video +canvas      # 扩展视频和画布
scan +table +tr +td      # 扩展表格元素
scan my-component        # 覆盖：扫描 Web Components
```

### 可配置的默认标签

```bash
# ~/.selectorclirc
[scan]
default_tags = button, input, select, textarea, a, img
```

---

## 附录：快速参考卡

| 命令 | 语法 | 存储 | 用途 |
|------|------|------|------|
| `scan` | `scan [+tag \| tag]` | temp（覆盖） | 探索页面 |
| `find` | `find <tag> [where ...]` | temp（覆盖） | 精准查询 |
| `.find` | `.find where ...` | temp（覆盖） | 精炼结果 |
| `add` | `add workspace` | workspace（累积） | 确认保存 |
| `preview` | `preview workspace` | - | 预览/高亮 |

**记忆口诀**：**扫（scan）探（temp）探（temp），确（add）存（workspace）**
