# Selector CLI - 项目框架上下文

**文档版本**: 1.0
**创建日期**: 2025-11-22
**用途**: 保持开发方向一致，维护工作质量标准

---

## 🎯 项目北极星

### 核心使命
**为前端测试工程师提供一个简洁、强大、易用的命令行工具，用于快速定位和导出网页元素选择器。**

### 核心价值主张
1. **简洁性**: SQL 风格的直观语法，零学习曲线
2. **交互性**: 实时反馈，即时验证
3. **实用性**: 直接导出可用代码，无需手动转换
4. **可靠性**: 稳定的选择器，跨页面访问一致

### 不是什么
- ❌ 不是自动化测试框架（只生成选择器）
- ❌ 不是 Web Scraper（只辅助定位元素）
- ❌ 不是浏览器自动化工具（只是辅助工具）
- ❌ 不是可视化界面（纯命令行）

---

## 🏗️ 核心设计原则

### 1. 简洁优于复杂 (Simplicity over Complexity)

**原则**: 用户应该能在 5 分钟内上手使用

**实践**:
```bash
# ✅ 好 - 简洁直观
selector> add input where type="email"

# ❌ 差 - 过于复杂
selector> collection.add(element_filter(tag="input", attributes={"type": "email"}))
```

**检查点**:
- [ ] 新命令是否需要超过 1 行文档说明？
- [ ] 用户是否需要记住超过 3 个概念？
- [ ] 是否可以用更简单的方式实现？

### 2. 约定优于配置 (Convention over Configuration)

**原则**: 默认行为应该满足 80% 的使用场景

**实践**:
```bash
# ✅ 好 - 智能默认
selector> open example.com
# 自动添加 https://，自动等待加载

# ❌ 差 - 需要过多配置
selector> open example.com --protocol=https --wait=true --timeout=30000
```

**检查点**:
- [ ] 是否需要用户指定常见的配置？
- [ ] 默认值是否覆盖常见场景？
- [ ] 高级选项是否可选而非必需？

### 3. 反馈即时性 (Immediate Feedback)

**原则**: 每个操作都应该有清晰的反馈

**实践**:
```bash
# ✅ 好 - 明确反馈
selector> add input
Added 5 element(s) to collection. Total: 5

# ❌ 差 - 无反馈
selector> add input
selector>
```

**检查点**:
- [ ] 用户是否清楚操作是否成功？
- [ ] 错误消息是否具有可操作性？
- [ ] 是否显示了相关的状态变化？

### 4. 渐进式增强 (Progressive Enhancement)

**原则**: 基础功能简单，高级功能可选

**实践**:
```bash
# 初学者 - 简单命令
selector> add input
selector> list

# 进阶用户 - 条件过滤
selector> add input where type="email" and visible

# 专家用户 - 复杂查询
selector> add input where (type="text" or type="email") and not disabled and index > 5
```

**检查点**:
- [ ] 基础功能是否独立可用？
- [ ] 高级功能是否自然扩展？
- [ ] 是否有清晰的能力层次？

### 5. 一致性 (Consistency)

**原则**: 相似的操作应该有相似的语法

**实践**:
```bash
# ✅ 好 - 一致的模式
add <target> [where <condition>]
remove <target> [where <condition>]
list [<target>] [where <condition>]

# ❌ 差 - 不一致
add <target> where <condition>
delete from collection where <condition>
show elements matching <condition>
```

**检查点**:
- [ ] 命令结构是否遵循已有模式？
- [ ] 参数顺序是否一致？
- [ ] 术语使用是否统一？

---

## 🏛️ 架构核心原则

### 架构图

```
┌─────────────────────────────────────────────┐
│              User Input                      │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│             REPL (main.py)                   │
│  - 提示符生成                                 │
│  - 命令读取                                   │
│  - 异常处理                                   │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│        Parser (lexer.py + parser.py)        │
│  - 词法分析                                   │
│  - 语法分析                                   │
│  - 命令对象构建                               │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│      Executor (executor.py)                 │
│  - 命令分发                                   │
│  - 业务逻辑                                   │
│  - 结果格式化                                 │
└──────┬────────┬────────┬────────┬───────────┘
       │        │        │        │
   ┌───▼──┐ ┌──▼───┐ ┌──▼───┐ ┌──▼────┐
   │Browser│ │Scanner│ │Element│ │Context│
   │Manager│ │       │ │Coll.  │ │       │
   └───────┘ └───────┘ └───────┘ └───────┘
```

### 模块职责边界

#### REPL Layer
**职责**:
- 用户交互
- 提示符生成
- 输入读取
- 顶层异常处理

**禁止**:
- ❌ 业务逻辑
- ❌ 数据处理
- ❌ 浏览器操作

#### Parser Layer
**职责**:
- 词法分析
- 语法分析
- 命令对象构建
- 语法错误检测

**禁止**:
- ❌ 命令执行
- ❌ 浏览器交互
- ❌ 数据存储

#### Executor Layer
**职责**:
- 命令分发
- 业务流程编排
- 结果格式化
- 业务逻辑验证

**禁止**:
- ❌ 语法解析
- ❌ 直接浏览器操作（应调用 Browser Manager）
- ❌ 复杂的数据转换（应在专门的类中）

#### Core Layer
**职责**:
- 核心数据模型
- 浏览器交互
- 元素扫描
- 状态管理

**禁止**:
- ❌ 命令解析
- ❌ 用户交互
- ❌ 格式化输出

---

## 📐 代码质量标准

### 代码风格

```python
# ✅ 好的代码示例

class ElementScanner:
    """Scan page for elements

    This scanner identifies interactive elements on a webpage
    and extracts their properties for selector generation.
    """

    async def scan(
        self,
        page: Page,
        element_types: List[str] = None,
        deep: bool = False
    ) -> List[Element]:
        """Scan page and return elements

        Args:
            page: Playwright page object
            element_types: List of element tags to scan (default: standard form elements)
            deep: Whether to scan Shadow DOM (default: False)

        Returns:
            List of Element objects

        Raises:
            ScanError: If page is not loaded or scan fails
        """
        if element_types is None:
            element_types = self.DEFAULT_ELEMENT_TYPES

        elements = []

        for elem_type in element_types:
            # Clear comment explaining the step
            locators = await page.locator(elem_type).all()

            for locator in locators:
                element = await self._build_element(locator, len(elements), elem_type)
                elements.append(element)

        return elements
```

### 强制要求

#### 1. 类型提示 (Type Hints)
```python
# ✅ 必须
def execute(self, command: Command, context: Context) -> str:
    pass

# ❌ 禁止
def execute(self, command, context):
    pass
```

#### 2. 文档字符串 (Docstrings)
```python
# ✅ 必须 - 所有公共方法
def scan(self, page: Page) -> List[Element]:
    """Scan page for elements

    Args:
        page: Playwright page object

    Returns:
        List of Element objects
    """
    pass

# ✅ 可选 - 私有方法（但推荐）
def _build_element(self, locator) -> Element:
    """Build Element from locator"""
    pass
```

#### 3. 错误处理
```python
# ✅ 好 - 具体的错误处理
try:
    await page.goto(url, timeout=60000)
except TimeoutError as e:
    logger.error(f"Timeout loading {url}: {e}")
    return "Error: Page load timeout. Check network connection."
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    return f"Error: {e}"

# ❌ 差 - 吞掉所有错误
try:
    await page.goto(url)
except:
    pass
```

#### 4. 命名规范
```python
# ✅ 好
class ElementScanner:        # 类: PascalCase
    DEFAULT_TYPES = []       # 常量: UPPER_SNAKE_CASE

    def scan_page(self):     # 方法: snake_case
        element_count = 0    # 变量: snake_case

# ❌ 差
class element_scanner:
    defaultTypes = []

    def ScanPage(self):
        ElementCount = 0
```

---

## ✅ 功能开发检查清单

### 新功能开发前

- [ ] **需求明确**: 功能解决什么问题？
- [ ] **用户价值**: 至少 20% 用户会用到？
- [ ] **设计简洁**: 能否用现有机制实现？
- [ ] **向后兼容**: 是否破坏现有功能？
- [ ] **文档计划**: 如何向用户解释？

### 实现过程中

- [ ] **遵循架构**: 放在正确的层级？
- [ ] **单一职责**: 每个类/方法只做一件事？
- [ ] **类型提示**: 所有函数签名都有类型？
- [ ] **错误处理**: 异常情况都处理了？
- [ ] **测试驱动**: 写测试了吗？

### 提交代码前

- [ ] **自测**: 手动测试了常见场景？
- [ ] **边界测试**: 测试了边界情况？
- [ ] **单元测试**: 测试覆盖核心逻辑？
- [ ] **文档更新**: README/CHANGELOG 更新了？
- [ ] **代码审查**: 自己审查了代码？

---

## 🧪 测试标准

### 测试金字塔

```
        /\
       /  \  E2E Tests (10%)
      /────\
     /      \  Integration Tests (30%)
    /────────\
   /          \  Unit Tests (60%)
  /────────────\
```

### 测试要求

#### 1. 单元测试 (必须)
```python
# 每个核心功能必须有单元测试

def test_lexer_tokenizes_simple_command():
    """Test lexer can tokenize simple command"""
    lexer = Lexer()
    tokens = lexer.tokenize("add input")

    assert len(tokens) == 3  # ADD, INPUT, EOF
    assert tokens[0].type == TokenType.ADD
    assert tokens[1].type == TokenType.INPUT

def test_parser_parses_add_command():
    """Test parser can parse add command"""
    parser = Parser()
    command = parser.parse("add input where type='email'")

    assert command.verb == "add"
    assert command.target.element_type == "input"
    assert command.condition.field == "type"
```

#### 2. 集成测试 (推荐)
```python
# 测试多个组件协作

async def test_full_workflow():
    """Test complete workflow from open to export"""
    repl = SelectorREPL()
    await repl.context.browser.initialize()

    # Open page
    cmd = repl.parser.parse("open https://example.com")
    result = await repl.executor.execute(cmd, repl.context)
    assert "Opened" in result

    # Scan
    cmd = repl.parser.parse("scan")
    result = await repl.executor.execute(cmd, repl.context)
    assert len(repl.context.all_elements) > 0
```

#### 3. E2E 测试 (Phase 6)
```python
# 测试真实用户场景（自动化脚本）
```

### 测试覆盖率目标

- **Phase 1-2**: > 60% 核心功能
- **Phase 3-4**: > 70%
- **Phase 5-6**: > 80% 生产就绪

---

## 📝 文档标准

### 必须文档

1. **README.md** - 用户快速开始
2. **QUICKSTART.md** - 5 分钟上手
3. **CHANGELOG.md** - 版本变更
4. **每个功能都有示例** - 代码示例

### 文档原则

#### 1. 示例优先
```markdown
# ✅ 好 - 先给示例
## 添加元素

添加所有邮箱输入框：
```bash
selector> add input where type="email"
Added 1 element(s). Total: 1
```

语法：`add <target> [where <condition>]`

# ❌ 差 - 只有语法
## 添加元素
语法：add <target> [where <condition>]
```

#### 2. 常见场景覆盖
```markdown
# ✅ 好
## 常见场景

### 分析登录表单
```bash
selector> open https://example.com/login
selector> scan
selector> add input where type="email"
selector> add input where type="password"
selector> add button where type="submit"
selector> export playwright
```

### 批量选择元素
```bash
selector> add [1,3,5-10]
```
```

#### 3. 故障排除
```markdown
# ✅ 必须包含
## 常见问题

**Q: 为什么 scan 没有找到元素？**
A: 确保页面已加载完成。可以等待几秒后再 scan。

**Q: 导出的代码无法运行？**
A: 检查选择器是否在新页面访问时仍然有效。
```

---

## ⚠️ 常见陷阱和注意事项

### 1. 不要破坏简洁性

```bash
# ❌ 陷阱：添加过多选项
selector> add input --type email --visible true --enabled true --index-greater-than 5

# ✅ 保持简洁
selector> add input where type="email" and visible and enabled and index > 5
```

### 2. 不要过早优化

```python
# ❌ 陷阱：Phase 1 就实现复杂缓存
class ElementScanner:
    def __init__(self):
        self.cache = LRUCache(maxsize=1000)
        self.index = InvertedIndex()
        self.bloom_filter = BloomFilter()

# ✅ 先让它工作，再优化
class ElementScanner:
    async def scan(self, page):
        elements = []
        for elem_type in self.types:
            locators = await page.locator(elem_type).all()
            # 简单直接
```

### 3. 不要忽略边界情况

```python
# ❌ 陷阱：只考虑正常情况
def get_element_by_index(self, index: int) -> Element:
    return self.elements[index]

# ✅ 处理边界
def get_element_by_index(self, index: int) -> Optional[Element]:
    if index < 0 or index >= len(self.elements):
        return None
    return self.elements[index]
```

### 4. 不要硬编码

```python
# ❌ 陷阱：硬编码值
def scan(self, page):
    for tag in ['input', 'button', 'select']:
        ...

# ✅ 使用配置
DEFAULT_ELEMENT_TYPES = ['input', 'button', 'select', 'textarea', 'a']

def scan(self, page, element_types=None):
    if element_types is None:
        element_types = self.DEFAULT_ELEMENT_TYPES
```

### 5. 不要吞掉错误

```python
# ❌ 陷阱：静默失败
try:
    await page.goto(url)
except:
    pass

# ✅ 适当处理
try:
    await page.goto(url, timeout=60000)
except TimeoutError:
    logger.error(f"Timeout loading {url}")
    return "Error: Page load timeout"
except Exception as e:
    logger.error(f"Error loading page: {e}")
    raise
```

---

## 🔄 开发工作流

### 每次开发前（重新对齐）

1. **重读本文档** - 确保方向一致
2. **检查 DEVELOPMENT_PLAN.md** - 确认在正确阶段
3. **查看 CHANGELOG.md** - 了解最新状态
4. **运行测试** - 确保基线正常

### 开发过程中

1. **小步迭代** - 每个 PR 只做一件事
2. **频繁提交** - 功能完成就提交
3. **持续测试** - 写一点测试一点
4. **及时文档** - 代码写完文档就写

### 提交前检查

```bash
# 1. 运行所有测试
python tests/test_mvp.py
python tests/test_integration.py

# 2. 检查代码风格（将来可添加 flake8/black）

# 3. 更新 CHANGELOG.md

# 4. 提交
git add -A
git commit -m "feat: ..."
```

---

## 🎯 决策框架

### 当你不确定时，问自己：

#### 关于功能
1. **这符合核心使命吗？** (定位和导出选择器)
2. **至少 20% 用户会用吗？** (避免功能膨胀)
3. **能用现有机制实现吗？** (避免重复)
4. **用户能在 1 分钟内理解吗？** (保持简洁)
5. **这会让核心流程更复杂吗？** (保护简洁性)

#### 关于设计
1. **这遵循已有模式吗？** (保持一致性)
2. **这是最简单的实现吗？** (避免过度设计)
3. **用户能轻松发现这个功能吗？** (可发现性)
4. **错误消息是否可操作？** (用户体验)
5. **这需要文档说明吗？** (自解释性)

#### 关于代码
1. **职责是否单一？** (单一职责原则)
2. **是否放在正确的层级？** (架构一致性)
3. **是否有类型提示？** (类型安全)
4. **是否有测试？** (质量保证)
5. **是否需要重构？** (代码质量)

### 决策记录模板

当做重要决策时，记录在 `docs/ADR/` (Architecture Decision Records):

```markdown
# ADR-001: 使用 SQL 风格语法

## 状态
已采纳

## 背景
需要设计命令语法，有多种选择：
1. SQL 风格: `add input where type="email"`
2. 函数风格: `add(input, {type: "email"})`
3. 自然语言: `add all email inputs`

## 决策
采用 SQL 风格语法

## 理由
1. 目标用户（测试工程师）熟悉 SQL
2. 简洁且强大
3. 易于扩展（WHERE 子句）
4. 直观易学

## 后果
- 正面：学习曲线低，功能强大
- 负面：语法解析稍复杂
- 缓解：手写解析器，可控
```

---

## 🚨 质量红线（不可妥协）

### 绝对禁止

1. ❌ **破坏向后兼容** - 已有命令不能改变行为
2. ❌ **无错误处理** - 所有可能失败的地方必须处理
3. ❌ **无类型提示** - 所有公共 API 必须有类型
4. ❌ **无测试的核心功能** - 核心逻辑必须有测试
5. ❌ **硬编码敏感数据** - 不能有硬编码的 URL、密码等
6. ❌ **吞掉错误** - 不能静默失败
7. ❌ **不一致的命名** - 术语必须统一
8. ❌ **无文档的公共 API** - 用户可见功能必须有文档

### 必须遵守

1. ✅ **简洁优先** - 复杂功能必须有简单替代
2. ✅ **用户反馈** - 每个操作都有反馈
3. ✅ **错误可操作** - 错误消息要告诉用户怎么做
4. ✅ **测试先行** - 核心功能先写测试
5. ✅ **文档同步** - 代码改了文档就改
6. ✅ **渐进增强** - 基础功能独立可用
7. ✅ **性能意识** - 大量元素时要考虑性能
8. ✅ **安全意识** - 不执行不受信任的代码

---

## 📊 进度自查

### Phase 完成标准

每个 Phase 完成时，必须满足：

- [ ] 所有计划功能已实现
- [ ] 所有功能有测试
- [ ] 所有功能有文档
- [ ] 所有功能有示例
- [ ] 向后兼容测试通过
- [ ] 集成测试通过
- [ ] CHANGELOG 已更新
- [ ] 本文档已更新（如有架构变化）

### 质量自查

定期（每周）自查：

- [ ] 代码质量：遵循规范？
- [ ] 测试覆盖：达标？
- [ ] 文档完整：同步？
- [ ] 性能：可接受？
- [ ] 用户体验：简洁？
- [ ] 架构一致：遵循原则？

---

## 🎓 学习和改进

### 当发现问题时

1. **记录** - 在 GitHub Issues 或此文档
2. **分析** - 根本原因是什么？
3. **改进** - 更新检查清单/文档
4. **分享** - 团队讨论

### 持续改进

- **每个 Phase 结束后回顾**
  - 什么做得好？
  - 什么可以改进？
  - 更新本文档

- **遇到困难时**
  - 是否违反了某个原则？
  - 检查清单是否遗漏了什么？
  - 需要添加新的指导吗？

---

## 📌 快速参考卡

### 开发前必读
1. 🎯 核心使命：定位和导出选择器
2. 🏗️ 设计原则：简洁、一致、反馈
3. ✅ 检查清单：需求、设计、实现、测试、文档

### 实现时牢记
1. 类型提示 - 所有函数
2. 错误处理 - 所有异常
3. 单一职责 - 每个方法
4. 测试驱动 - 核心功能

### 提交前确认
1. 测试通过
2. 文档更新
3. CHANGELOG 记录
4. 代码审查

---

## 🔗 相关文档

- **DEVELOPMENT_PLAN.md** - 开发路线图
- **README.md** - 用户指南
- **CHANGELOG.md** - 版本历史
- **selector-explorer/selector-cli-design-v1.0.md** - 详细设计
- **selector-explorer/selector-cli-grammar-v1.0.md** - 语法规范

---

## 📝 版本历史

**v1.0** (2025-11-22)
- 初始版本
- Phase 1 完成后创建
- 确立核心原则和标准

---

**使用本文档**:

1. **每次开发前** - 重读"核心设计原则"和相关检查清单
2. **遇到选择时** - 查看"决策框架"
3. **提交代码前** - 过一遍"检查清单"
4. **质量问题时** - 对照"质量红线"
5. **偏离方向时** - 回到"项目北极星"

**这是我们的"北极星"，任何时候都可以回来重新对齐。** 🧭
