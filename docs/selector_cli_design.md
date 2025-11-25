# Selector CLI 三层架构设计文档

## 目录
1. [设计理念](#设计理念)
2. [三层架构详解](#三层架构详解)
3. [核心命令语法](#核心命令语法)
4. [使用场景与工作流程](#使用场景与工作流程)
5. [设计原则](#设计原则)

---

## 设计理念

### 核心思想：探索-筛选-确认

Selector CLI 的设计围绕**元素的渐进式分析流程**展开，模拟人类分析网页时的思维模式：

1. **探索（Explore）**："这个页面有什么元素？让我快速看看"
2. **筛选（Select）**："这些元素看起来有趣，值得研究"
3. **确认（Confirm）**："这几个最有价值，需要重点测试"

基于此，我们设计了三层递进式架构，分别对应三种不同的用户意图和元素生命周期。

### 存储哲学

查询命令采用不同的存储策略：

- **find**：精准查询，结果存储到 **temp**（覆盖语义）
- **scan**：宽泛探索，结果直接存储到 **candidates**（覆盖语义）
- **temp**：当前查询结果的草稿纸，支持反复精炼（find/.find）
- **candidates**：感兴趣的元素集合，等待深度分析
- **workspace**：确认有价值元素的持久存储

### 语法糖设计：scan 的便捷性

`scan` 是一个**语法糖**，提供了**免探索**的便捷方式：

```bash
# 完整流程（手动探索）
find button                   # 1. 探索：手动查询按钮 → temp
add to candidates             # 2. 筛选：添加到候选区
find input                    # 3. 再次探索：查询输入框 → temp
add to candidates             # 4. 筛选：添加到候选区
add [1,3] to workspace        # 5. 确认：从 candidates 挑选到 workspace

# 便捷流程（使用 scan）
scan                          # 1. 一键探索：自动扫描默认元素 → candidates
add [1,3,7] to workspace      # 2. 直接确认：从 candidates 挑选到 workspace
```

**设计考量**：
- **新手友好**：页面加载后执行一次 `scan`，立即获得可用元素
- **高效**：标准页面（登录、表单、购物车）的交互元素往往就是默认 5 种
- **可扩展**：`scan +img` 快速扩展探索范围，无需多次 `find`
- **不冲突**：scan 不影响 `find` → `add to candidates` 的常规流程

**适用场景**：
- ✅ 首次分析页面，快速建立全局观
- ✅ 标准交互页面（登录、注册、表单）
- ✅ 作为分析起点，之后再通过 `find` 补充特定元素

---

## 三层架构详解

### 1. Candidates（候选区）

**来源**：`scan` 命令 + `add to candidates`
**用途**：**感兴趣、值得研究**的元素集合
**生命周期**：持久（页面级，直到手动清理）
**用户意图**："这些元素看起来不错，值得仔细研究"

```bash
scan              # 探索页面，存入 candidates
count candidates  # 查看候选区元素数量
scan +img         # 扩展探索，加入 img
candidates        # 清空并重新探索 img

# 从 temp 添加感兴趣的元素
add to candidates          # 将 temp 全部添加到 candidates
add [1,3,5] to candidates  # 从 temp 选择添加
```

**特点**：
- 页面加载后执行 scan 初始化候选区
- 累积待研究的元素集合
- 作为筛选层，保存所有潜在有价值的元素
- 支持从 temp 补充添加

### 2. Temp（当前查询结果）

**来源**：`find` / `.find` 命令
**用途**：当前查询结果，支持精炼
**生命周期**：瞬时（下次 `find` 覆盖）
**用户意图**："当前查询结果"

```bash
find button           # 查询按钮 → temp（覆盖）
.find where visible   # 精炼当前 temp 结果
find input            # 新查询 → temp（覆盖）
count temp            # 查看当前 temp 数量
```

**特点**：
- `find` 结果的草稿纸，反复覆盖
- 支持链式精炼（`.find` 从当前 temp 过滤）
- 仅用于快速试探，不长期保存

### 3. Workspace（工作区）

**来源**：`add to workspace` 命令
**用途**：确认有价值的元素
**生命周期**：会话级持久
**用户意图**："这个真的有用"

```bash
add to workspace                # 从当前视图（candidates/temp）全部添加
add [1,3,5] to workspace        # 从当前视图选择添加
add [2,4] to workspace from candidates  # 明确从 candidates 添加

# 查看工作区
list workspace    # 列出工作区元素详情
count workspace   # 统计工作区元素数量
```

**特点**：
- 累积确认的元素
- 用于预览（preview）、高亮（highlight）
- 跨查询持久保存
- 来源可以是 candidates 或 temp

### 架构关系图

```
temp         ← find / .find（当前查询，反复覆盖）
candidates   ← scan（页面级探索）
             ← add to candidates（从 temp 筛选）
workspace    ← add to workspace（从 candidates/temp 确认）
```

**三层递进流程**:
1. **探索层（temp）**: 通过 `find` 快速试探，反复覆盖
2. **筛选层（candidates）**: 通过 `add to candidates` 累积感兴趣的元素
3. **确认层（workspace）**: 通过 `add to workspace` 从 candidates 挑选最有价值的元素

**数据流动示例**:
```bash
find button              # 探索：button → temp
add to candidates        # 筛选：temp → candidates
add to workspace [1,3]   # 确认：candidates → workspace
```

---

## 核心命令语法

### scan - 探索命令

**语义**：探索页面元素，直接存入候选区

**语法**：
```bash
scan              # 扫描默认原子元素 → candidates（覆盖）
scan +img         # 扩展：默认 + img
candidates        # 覆盖：只扫描 img
```

**默认原子元素**（5个）：
- `button` - 按钮
- `input` - 输入框
- `select` - 下拉选择
- `textarea` - 多行文本
- `a` - 链接

**存储行为**：**覆盖 candidates（页面级持久）**
**使用建议**：页面加载后执行，建立全局候选集

### find - 定位命令

**语义**：精准查询特定元素，存入 temp（覆盖）

**语法**：
```bash
find button                 # 查询所有 button → temp（覆盖）
find input where visible    # 带条件的查询
find div where class contains "modal"  # 查询容器

# 精炼模式（从当前 temp 过滤）
.find where visible         # 过滤当前 temp，结果仍存储到 temp
.find where text contains "Login"  # 进一步精炼
```

**支持的所有 HTML 元素**：任何有效的 HTML 标签
**存储行为**：**覆盖 temp**
**使用建议**：用于快速试探和精炼，反复使用

**注意**：`.find` 也是从当前 temp 过滤，结果仍存入 temp（覆盖）

### add - 确认命令

**语义**：将结果从一层移动到另一层（筛选与确认）

**完整语法**：
```bash
# 筛选：从 temp 添加到 candidates
add [1,3,5] to candidates        # 从 temp 选择添加到 candidates
add [2,4] to candidates from temp  # 明确从 temp 源

# 确认：从 candidates/temp 添加到 workspace
add to workspace                   # 从当前视图（candidates/temp）全部添加
add [1,3,5] to workspace           # 从当前视图选择添加
add [2,4] to workspace from candidates  # 明确从 candidates 源
```

**存储行为**：
- `add to candidates`: temp → candidates（累积，筛选层）
- `add to workspace`: candidates/temp → workspace（累积，确认层）

**使用建议**：
- 发现 temp 中元素有价值 → `add to candidates`（筛选）
- 从 candidates 中确认最有用 → `add to workspace`（确认）
- 也可以跳过滤选，直接从 temp 到 workspace

---

## 使用场景与工作流程

### 场景 1：分析表单页面（登录）

```bash
# 页面加载
open https://example.com/login

# 第一步：探索页面，建立候选集
scan
# candidates: [button x3, input x2, select x1, a x5]
# 共 11 个元素

# 第二步：通过 find 探索表单容器
find form where id="login-form"
# temp: [form x1]

# 第三步：从表单内探索输入框
find input
# temp: [input#username, input#password]

# 第四步：精炼到密码框
.find where type="password"
# temp: [input#password]

# 第五步：筛选到 candidates
add to candidates
# candidates: [原有元素 + input#password 置顶]

# 第六步：继续探索按钮
find button
# temp: [button x3]

# 第七步：精炼到登录按钮
.find where text contains "Login"
# temp: [button#login]

# 第八步：直接确认到 workspace（跳过筛选）
add to workspace
# workspace: [button#login]

# 第九步：从 candidates 确认密码框
add [1] to workspace from candidates
# workspace: [button#login, input#password]

# 第十步：预览研究
preview workspace
# 高亮显示这两个元素，分析选择器
```

### 场景 2：分析商品列表页

```bash
# 第一步：探索页面，建立候选集
scan
# candidates: [button x5, input x1, select x2, a x20]
# 共 28 个元素

# 第二步：发现图片不够，扩展候选集
scan +img
# candidates: [原有 + img x30]
# 共 58 个元素

# 第三步：图片太多，只关注主图
scan img where class contains "main"
# candidates: [img x5]（覆盖）

# 第四步：先把主图筛选到 candidates（已经在 candidates）
count candidates
# candidates: [img x5]

# 第五步：从 candidates 挑选主图确认到 workspace
add [1,3,5] to workspace
# workspace: [3 个主图]

# 第六步：探索购买按钮
find button where text contains "Buy"
# temp: [button x3]

# 第七步：直接确认到 workspace（跳过筛选）
add to workspace
# workspace: [3 个主图, 3 个购买按钮]

# 第八步：高亮所有元素
preview workspace
```

### 场景 3：快速试探（不保存）

```bash
# 快速验证页面是否有登录按钮
find button where text contains "Login"
# temp: [button x1]

# 看一眼就丢弃（不 add），继续其他探索
find input
# temp: [input x2]（原结果已被覆盖）

# 使用 .find 精炼当前 temp（从 input 中找 password）
.find where type="password"
# temp: [input#password]
```

---

## 设计原则

### 1. 语义明确原则

- `scan` = 探索（宽泛、覆盖 candidates）
- `find` = 定位（精准、覆盖 temp）
- `add to candidates` = 筛选（从 temp 到 candidates）
- `add to workspace` = 确认（从 candidates/temp 到 workspace）
- `.find` = 精炼（从 temp 过滤，结果仍存 temp）

### 2. 分层存储原则

不同命令存储到不同层级：

- **find**：**temp**（探索层，反复覆盖）
- **scan**：**candidates**（筛选层，页面级持久）
- **add to candidates**：temp → candidates（累积筛选）
- **add to workspace**：candidates/temp → workspace（累积确认）

### 3. 零噪音原则

**默认只探索原子元素**（5个），避免容器和装饰元素带来的噪音：

✅ **默认包含**：button, input, select, textarea, a
❌ **需要扩展才包含**：img, form, div, span, label

### 4. 覆盖语义原则

- **temp**：查询覆盖，每次 `find` 都会覆盖上次结果
- **candidates**：页面级持久，作为全局探索层
- **workspace**：会话级累积，只增不减（除非手动 clear）

### 5. 渐进式探索原则

支持从宽泛到精准的自然探索流程：

```bash
# 经典渐进式（三层完整流程）
scan                          # 宽泛探索 → candidates
find button                   # 精准定位 → temp
add to candidates             # 筛选感兴趣 → candidates
find button where visible     # 进一步精细 → temp
add [1] to workspace          # 确认价值 → workspace

# 快速确认式（跳过筛选层）
find button                   # 探索 → temp
add to workspace              # 直接确认 → workspace
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

1. **页面加载后先 scan**：使用语法糖快速建立候选集
   ```bash
   open https://example.com
   scan                    # 一键探索：按钮/输入框/链接 → candidates
   count candidates        # 查看数量
   list candidates [1-5]   # 查看前5个
   ```

2. **标准页面直接用 scan**：登录、表单等常见页面
   ```bash
   # 分析登录表单 → 2步完成
   scan                                      # 1. scan 一步到位 → candidates
   add [1,2,3] to workspace                  # 2. 直接挑选到 workspace

   # 对比：完整流程需要 4 步
   find button; add to candidates            # 1-2
   find input; add to candidates             # 3-4
   add [1,2] to workspace                    # 5
   ```

3. **使用 find 快速试探**：不确定时快速验证
   ```bash
   find button where text contains "Submit"
   # temp: [button]，看一眼即可，不 add
   ```

4. **先筛选到 candidates，再确认到 workspace**
   ```bash
   scan                           # 初始探索 → candidates
   find button where visible      # 进一步探索 → temp
   add to candidates              # 筛选保存到 candidates

   # 继续分析 candidates...
   list candidates
   add [1,2] to workspace         # 仅确认最有价值的
   ```

5. **ctrl-c ctrl-v（复制粘贴）模式：跳过筛选**
   ```bash
   # 当元素已经很有把握时，跳过 candidates 直接到 workspace
   find button where text="Login"
   add to workspace               # 直接确认（跳过筛选层）
   ```

6. **定期清理 workspace**：长时间分析后
   ```bash
   clear workspace
   ```

### ❌ 避免做法

1. **不要 scan 所有元素**：噪音太大
   ```bash
   scan +img +span +div +form  # ❌ 可能 500+ 元素
   ```

2. **不要滥用 workspace**：只存最有价值的元素
   ```bash
   find input
   add to workspace      # ❌ 所有输入框都存？没必要，应先 add to candidates
   ```

3. **忘记 add 导致 temp 丢失**：temp 会被下次 find 覆盖
   ```bash
   find button
   # ... 执行其他查询
   find input         # temp 被覆盖
   ### 错误：忘记在覆盖前 add to candidates
   list temp          # ❌ 显示的是 input，不是 button
   ```

4. **不要过度依赖 scan**：scan 用于初始探索，精细查询用 find
   ```bash
   # ❌ 错误
   scan button        # 意图不明确

   # ✅ 正确
   find button        # 意图清晰，精准查询
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

| 命令 | 语法 | 存储位置 | 用途 | 模式 |
|------|------|----------|------|------|
| `scan` | `scan [+tag]` | **candidates**（覆盖） | 语法糖：一键探索页面 | 便捷 |
| `find` | `find <tag> [where ...]` | **temp**（覆盖） | 精准查询，快速试探 | 标准 |
| `.find` | `.find where ...` | **temp**（覆盖） | 精炼当前 temp 结果 | 标准 |
| `add to candidates` | `add [indices] to candidates` | candidates（累积） | 筛选：temp → candidates | 标准 |
| `add to workspace` | `add [indices] to workspace [from candidates]` | workspace（累积） | 确认：candidates/temp → workspace | 标准 |
| `clear candidates` | `clear candidates` | - | 清空候选区 | - |
| `clear workspace` | `clear workspace` | - | 清空工作区 | - |

### 使用模式

**便捷模式**（语法糖）：
```bash
scan                          # 1步：一键探索 → candidates
add [1,3] to workspace        # 2步：直接确认 → workspace
```

**标准模式**：
```bash
find button                   # 1. 探索 → temp
add to candidates             # 2. 筛选 → candidates
find input                    # 3. 再探索 → temp
add to candidates             # 4. 再筛选 → candidates
add [1,2] to workspace        # 5. 确认 → workspace
```

**三层架构口诀**：**探（find/temp）→ 筛（add/candidates）→ 确（add/workspace）**

**数据流动**：`find` → `temp` → `add to candidates` → `candidates` → `add to workspace` → `workspace`
