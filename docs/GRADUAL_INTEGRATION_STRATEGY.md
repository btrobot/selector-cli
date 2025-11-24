# V2功能渐进式集成方案 - "水乳交融"式开发

**版本**: v2.0-Integration-Plan
**日期**: 2025-11-24
**策略**: 渐进式、优雅集成，不创建新文件，保持向后兼容

---

## 一、核心原则

### 1.1 设计哲学

**拒绝**:
- ❌ 创建新的`*_v2.py`文件
- ❌ 独立的分支开发
- ❌ 一次性大爆炸式重构

**拥抱**:
- ✅ 在现有文件中逐步增强
- ✅ 向后兼容（v1语法100%保留）
- ✅ 每一步都可独立测试
- ✅ 代码优雅、无重复
- ✅ 水乳交融，浑然一体

### 1.2 向后兼容保证

所有v1功能必须继续工作，无需用户修改：

```python
# v1语法（继续支持）
Context.all_elements  # ✅ 保持工作
Context.collection    # ✅ 保持工作
add button           # ✅ 保持工作
list                 # ✅ 保持工作
```

```python
# v2语法（新增）
Context.candidates   # ✅ 新功能
Context.temp         # ✅ 新功能
cContext.workspace   # ✅ 新功能
find button          # ✅ 新功能
add from temp        # ✅ 新功能
```

---

## 二、集成路线图（6个阶段）

### 阶段1: Context三层架构重构（1天）

#### 目标
在现有`Context`类中优雅地添加三层支持，保持API兼容

#### 改造方案

**文件**: `src/selector_cli/core/context.py`

```python
class Context:
    def __init__(self, enable_history_file: bool = True):
        # ... existing code ...

        # === Phase 1: Three-layer architecture ===
        # v2: Three-layer element management
        # candidates: SCAN results (read-only source) - maps to v1 all_elements
        self._candidates: List[Element] = []

        # temp: FIND results (30s TTL cache) - NEW
        self._temp: List[Element] = []
        self._last_find_time: Optional[datetime] = None
        self.TEMP_TTL = 30  # seconds

        # workspace: User collection (persistent) - maps to v1 collection
        # Already exists: self.collection

        # Focus tracking (which layer is currently being operated on)
        self._focus: str = 'candidates'  # candidates | temp | workspace

    # === Backward compatibility properties ===
    @property
    def all_elements(self) -> List[Element]:
        """v1 compatibility: maps to candidates"""
        return self.candidates

    @all_elements.setter
    def all_elements(self, elements: List[Element]):
        """v1 compatibility: sets candidates"""
        self.candidates = elements

    # === v2 layer properties ===
    @property
    def candidates(self) -> List[Element]:
        """Get candidates (SCAN results) - read-only"""
        return self._candidates.copy()

    @candidates.setter
    def candidates(self, elements: List[Element]):
        """Set candidates (SCAN results)"""
        self._candidates = elements

    @property
    def temp(self) -> List[Element]:
        """Get temp with TTL-based expiration"""
        if self._is_temp_expired():
            return []
        return self._temp.copy()

    @temp.setter
    def temp(self, elements: List[Element]):
        """Set temp and reset TTL timer"""
        self._temp = elements
        self._last_find_time = datetime.now()

    @property
    def workspace(self) -> ElementCollection:
        """v2: Get workspace (maps to v1 collection)"""
        return self.collection

    # === TTL helpers ===
    def _is_temp_expired(self) -> bool:
        """Check if temp has expired"""
        if self._last_find_time is None:
            return True
        age = datetime.now() - self._last_find_time
        return age.total_seconds() > self.TEMP_TTL

    def has_temp_results(self) -> bool:
        """Check if temp has non-expired results"""
        return len(self.temp) > 0

    # === Focus management ===
    def set_focus(self, layer: str):
        """Set current focus layer"""
        if layer in ['candidates', 'temp', 'workspace']:
            self._focus = layer

    def get_focused_elements(self) -> List[Element]:
        """Get elements from current focus layer"""
        if self._focus == 'candidates':
            return self.candidates
        elif self._focus == 'temp':
            return self.temp
        else:
            return list(self.workspace.elements)
```

#### 改动说明

| v1 API | v2实现 | 兼容性 |
|--------|--------|--------|
| `Context.all_elements` | 映射到`candidates` | ✅ 100%兼容 |
| `Context.collection` | 映射到`workspace` | ✅ 100%兼容 |
| `update_elements()` | 同时更新candidates | ✅ 100%兼容 |
| **新增** | `Context.temp` | ✅ 新功能 |
| **新增** | `Context._focus` | ✅ 新功能 |

#### 测试验证

```bash
# 测试v1兼容性
pytest tests/test_context.py -v  # 所有测试通过

# 测试v2新功能
pytest tests/test_v2_context.py -v  # 新增测试
```

---

### 阶段2: 增强Command模型（4小时）

#### 目标
在`Command`中添加v2字段，不破坏现有结构

#### 改造方案

**文件**: `src/selector_cli/parser/command.py`

```python
@dataclass
class Command:
    """Parsed command"""
    verb: str  # open, scan, add, etc.
    target: Optional[Target] = None

    # Phase 1 simple condition (deprecated, use condition_tree)
    condition: Optional[Condition] = None

    # Phase 2 complex condition tree
    condition_tree: Optional[ConditionNode] = None

    argument: Optional[str] = None  # For open URL, etc.
    raw: str = ""

    # === Phase 3: v2 enhancements ===
    # Source layer for commands (add from temp, list candidates, etc.)
    source: Optional[str] = None  # "temp", "candidates", "workspace", or None

    # Append mode for add command (add append <target>)
    append_mode: bool = False

    # Find mode: regular find vs refine (.find)
    is_refine: bool = False  # True for ".find", False for "find"

    # Multiple element types for find/scan
    # target.element_type already supports single type
    # For multiple types, we can extend target or add new field
```

#### 改动说明

- 新增3个可选字段，不破坏现有Command使用
- 所有现有代码继续工作（字段有默认值）
- 新增字段用于v2功能

---

### 阶段3: Parser增强（1天）

#### 目标
添加FIND命令和v2语法支持

#### 改造方案

**文件**: `src/selector_cli/parser/parser.py`

```python
class Parser:
    # ... existing methods ...

    # === Phase 3: FIND command ===
    def parse_find(self, tokens: List[str], is_refine: bool = False) -> Command:
        """
        Parse: find <element_type>[,<type2>,...] [where <condition>]
              .find [where <condition>]  (refine mode)

        Args:
            tokens: Token list starting after "find" or ".find"
            is_refine: True if this is a .find (refine) command
        """
        if not tokens:
            raise ValueError("FIND command requires element type(s)")

        cmd = Command(verb="find", raw=" ".join(tokens))
        cmd.is_refine = is_refine

        if is_refine:
            # .find [where <condition>]
            next_token = tokens[0] if tokens else None
            if next_token == "where":
                # Parse WHERE condition
                condition_tokens = tokens[1:]
                cmd.condition_tree = self._parse_where_clause(condition_tokens)
            # No target needed for refine mode (uses temp)
            return cmd

        else:
            # Regular find: find <type>[,<type2>,...] [where <condition>]
            element_types = tokens[0]

            # Support comma-separated types: "button,input,div"
            if "," in element_types:
                # For now, we'll handle the first type
                # Full multi-type support can be added later
                primary_type = element_types.split(",")[0]
            else:
                primary_type = element_types

            cmd.target = Target(
                type=TargetType.ELEMENT_TYPE,
                element_type=primary_type
            )

            # Check for WHERE clause
            if len(tokens) > 1 and tokens[1] == "where":
                condition_tokens = tokens[2:]
                cmd.condition_tree = self._parse_where_clause(condition_tokens)

            return cmd

    # === Enhanced ADD with source ===
    def parse_add(self, tokens: List[str]) -> Command:
        """
        Parse: add [from <source>] [append] <target> [where <condition>]

        Examples:
            add button                    # v1 style
            add from temp                 # v2: from temp
            add append button             # v2: append mode
            add from candidates where visible  # v2: with condition
        """
        cmd = Command(verb="add", raw=" ".join(tokens))

        # Check for "from <source>"
        if len(tokens) >= 2 and tokens[0] == "from":
            cmd.source = tokens[1]  # "temp", "candidates", or "workspace"
            tokens = tokens[2:]     # Remove "from <source>"

        # Check for "append"
        if tokens and tokens[0] == "append":
            cmd.append_mode = True
            tokens = tokens[1:]     # Remove "append"

        # Now parse the target (remaining tokens)
        if tokens:
            cmd.target = self._parse_target(tokens[0])

            # Check for WHERE clause
            if len(tokens) > 1 and tokens[1] == "where":
                condition_tokens = tokens[2:]
                cmd.condition_tree = self._parse_where_clause(condition_tokens)

        return cmd

    # === Enhanced LIST with source ===
    def parse_list(self, tokens: List[str]) -> Command:
        """
        Parse: list [candidates|temp|workspace] [where <condition>]
               list [where <condition>]  (defaults to workspace)
        """
        cmd = Command(verb="list", raw=" ".join(tokens))

        if not tokens:
            # Plain "list" - defaults to workspace (v1 compatible)
            cmd.source = "workspace"
            return cmd

        first_token = tokens[0]

        # Check if first token is a source layer
        if first_token in ["candidates", "temp", "workspace"]:
            cmd.source = first_token
            tokens = tokens[1:] if len(tokens) > 1 else []
        else:
            # No explicit source, default to workspace
            cmd.source = "workspace"

        # Check for WHERE clause
        if len(tokens) >= 2 and tokens[0] == "where":
            condition_tokens = tokens[1:]
            cmd.condition_tree = self._parse_where_clause(condition_tokens)

        return cmd

    # === Modified main parser loop ===
    def parse(self, input_str: str) -> Command:
        """Parse command string"""
        tokens = self._tokenize(input_str)
        if not tokens:
            return Command(verb="", raw=input_str)

        verb = tokens[0].lower()
        remaining = tokens[1:]

        # ... existing verb handling ...

        # === NEW: FIND command ===
        if verb == "find":
            return self.parse_find(remaining, is_refine=False)

        # === NEW: .find (refine) command ===
        if verb == ".find":
            return self.parse_find(remaining, is_refine=True)

        # === ENHANCED: ADD command ===
        if verb == "add":
            return self.parse_add(remaining)

        # === ENHANCED: LIST command ===
        if verb == "list":
            return self.parse_list(remaining)

        # ... rest of existing verbs ...
```

#### 改动说明

- 在现有Parser类中添加新方法
- 不破坏现有parse逻辑
- 新增FIND、增强ADD/LIST
- Refine模式通过`.find`前缀区分

---

### 阶段4: Executor增强（2天）

#### 目标
实现FIND命令执行和增强ADD/LIST逻辑

#### 改造方案

**文件**: `src/selector_cli/commands/executor.py`

```python
class CommandExecutor:
    # ... existing methods ...

    # === Phase 4: FIND command execution ===
    async def execute_find(self, command: Command, context: Context) -> str:
        """Execute find command - query DOM directly"""

        if command.is_refine:
            # .find (refine mode) - filter existing temp results
            return await self._execute_refine(command, context)

        # Regular find - query DOM
        if not command.target or not command.target.element_type:
            return "Error: FIND requires element type"

        element_type = command.target.element_type

        # Query DOM directly (using scanner)
        if not context.browser or not context.browser.page:
            return "Error: No page loaded. Use 'open <url>' first."

        try:
            # Use existing scanner infrastructure
            elements = await context.browser.query_selector_all(element_type)

            # Convert to Element objects
            from ..core.element import Element
            result_elements = []

            for i, elem in enumerate(elements):
                # Get element properties
                tag_name = await elem.evaluate("el => el.tagName.toLowerCase()")

                element = Element(
                    index=i,
                    tag=tag_name,
                    # ... other properties ...
                )
                result_elements.append(element)

            # Apply WHERE condition if present
            if command.condition_tree:
                result_elements = self._apply_condition(
                    result_elements,
                    command.condition_tree,
                    context
                )

            # Store to temp layer
            context.temp = result_elements

            return f"Found {len(result_elements)} {element_type}(s) → temp"

        except Exception as e:
            return f"FIND error: {e}"

    async def _execute_refine(self, command: Command, context: Context) -> str:
        """Execute .find (refine mode) - filter temp layer"""

        if not context.has_temp_results():
            return "Error: No temp results to refine. Use 'find' first."

        temp_elements = context.temp

        # Apply WHERE condition
        if command.condition_tree:
            filtered = self._apply_condition(
                temp_elements,
                command.condition_tree,
                context
            )
        else:
            filtered = temp_elements

        # Update temp (resets TTL)
        context.temp = filtered

        return f"Refined to {len(filtered)} element(s) → temp"

    # === Enhanced ADD with source ===
    async def execute_add(self, command: Command, context: Context) -> str:
        """Enhanced ADD with source and append mode"""

        # Determine source elements
        source_elements = self._get_source_elements(command.source, context)

        if not source_elements:
            layer_name = command.source or "source"
            return f"No elements in {layer_name}"

        # Apply WHERE condition if present
        if command.condition_tree:
            source_elements = self._apply_condition(
                source_elements,
                command.condition_tree,
                context
            )

        # Get target filter
        target_filter = None
        if command.target:
            target_filter = self._target_to_filter(command.target)

        # Filter by target
        if target_filter:
            elements_to_add = [
                elem for elem in source_elements
                if self._element_matches_filter(elem, target_filter)
            ]
        else:
            elements_to_add = source_elements

        # Add to workspace
        if command.append_mode:
            # Append mode - add without clearing
            existing_count = len(context.workspace.elements)
            for elem in elements_to_add:
                context.workspace.add(elem)
            new_count = len(context.workspace.elements)
            added = new_count - existing_count
            return f"Appended {added} element(s) → workspace ({new_count} total)"
        else:
            # Regular mode - clear and add (v1 compatible)
            context.workspace.clear()
            for elem in elements_to_add:
                context.workspace.add(elem)
            return f"Added {len(elements_to_add)} element(s) → workspace"

    def _get_source_elements(self, source: Optional[str], context: Context) -> List[Element]:
        """Get elements from specified source layer"""
        if source == "temp":
            return context.temp
        elif source == "candidates":
            return context.candidates
        else:
            # Default to candidates (v1 behavior)
            return context.candidates

    # === Enhanced LIST with source ===
    async def execute_list(self, command: Command, context: Context) -> str:
        """Enhanced LIST with source layer and conditions"""

        # Get source elements
        source_elements = self._get_source_elements(command.source, context)

        # Apply WHERE condition
        if command.condition_tree:
            elements = self._apply_condition(
                source_elements,
                command.condition_tree,
                context
            )
        else:
            elements = source_elements

        # Format output
        if not elements:
            layer_name = command.source or "workspace"
            # Check if temp expired
            if command.source == "temp" and context._is_temp_expired():
                return "0 elements (temp expired)"
            return f"0 elements in {layer_name}"

        # Generate list output (existing logic)
        return self._format_list_output(elements)

    # === Helper: Apply WHERE conditions ===
    def _apply_condition(self, elements: List[Element],
                        condition: ConditionNode,
                        context: Context) -> List[Element]:
        """Apply WHERE condition to element list"""
        # Reuse existing _execute_filter/_execute_keep logic
        # This method would extract and generalize the filtering logic
        pass
```

#### 改动说明

- 新增`execute_find`和`execute_refine`方法
- 增强`execute_add`支持source和append_mode
- 增强`execute_list`支持source和conditions
- 新增辅助方法`_get_source_elements`和`_apply_condition`

---

### 阶段5: REPL增强（4小时）

#### 目标
更新提示符显示层状态，添加友好提示

#### 改造方案

**文件**: `src/selector_cli/repl/main.py`

```python
class SelectorREPL:
    # ... existing code ...

    def _get_prompt(self) -> str:
        """Get prompt string showing current state"""
        parts = ["selector"]

        # Add URL if page loaded
        if self.context.current_url:
            url = self.context.current_url
            if '://' in url:
                domain = url.split('://')[1].split('/')[0]
            else:
                domain = url.split('/')[0]
            parts.append(f"({domain})")

        # === Phase 5: Show layer counts ===
        # Only show if v2 features are being used
        counts = []
        if len(self.context.candidates) > 0:
            counts.append(f"c:{len(self.context.candidates)}")
        if len(self.context.temp) > 0:
            counts.append(f"t:{len(self.context.temp)}")
        if len(self.context.workspace.elements) > 0:
            counts.append(f"w:{len(self.context.workspace.elements)}")

        if counts:
            parts.append(f"({' '.join(counts)})")

        return " ".join(parts) + "> "

    async def run(self):
        """Main REPL loop"""
        await self._initialize()

        print("\n" + "=" * 60)
        print("Selector CLI - Interactive element selection")
        print("=" * 60)

        # === Show v2 features ===
        print("Features:")
        print("  • scan button, input      - Multiple types")
        print("  • find input where visible  - Direct DOM query")
        print("  • add from temp           - Source parameter")
        print("  • list temp / candidates  - View layers")
        print("=" * 60)
        print("Type 'help' for commands, 'quit' to exit\n")

        # ... rest of loop ...

        # === Add TTL expiration hint ===
        if command.verb == 'list' and command.source is None:
            # Check temp expiration
            if self.context.has_temp_results():
                import time
                if self.context._last_find_time:
                    age = time.time() - self.context._last_find_time.timestamp()
                    if age > 25:  # Warn when 5+ seconds old
                        print(f"\n[Hint] Temp results are {int(age)}s old "
                              f"(expire in {30-int(age)}s)")
```

#### 改动说明

- 增强提示符显示c:t:w计数
- 添加友好的功能提示
- 在temp即将过期时给出提示

---

### 阶段6: 集成测试（1天）

#### 测试策略

1. **向后兼容测试**: 确保v1测试100%通过
2. **增量测试**: 为每个新功能添加测试
3. **集成测试**: 验证完整v2工作流

#### 测试文件

```python
# tests/test_v2_integration.py

class TestV2Integration:
    """Integration tests for v2 features"""

    async def test_three_layer_workflow(self):
        """Test complete three-layer workflow"""
        # Step 1: SCAN → candidates
        result = await executor.execute_scan(command, context)
        assert len(context.candidates) > 0

        # Step 2: FIND → temp
        result = await executor.execute_find(find_command, context)
        assert len(context.temp) > 0
        assert len(context.temp) < len(context.candidates)

        # Step 3: ADD → workspace
        result = await executor.execute_add(add_command, context)
        assert len(context.workspace.elements) > 0

    async def test_ttl_expiration(self):
        """Test temp TTL expiration"""
        # Add elements to temp
        context.temp = [element1, element2]
        assert len(context.temp) == 2

        # Wait for expiration (31 seconds)
        import time
        time.sleep(31)

        # Should return empty list
        assert len(context.temp) == 0

    async def test_refine_mode(self):
        """Test .find refine mode"""
        # First find (regular)
        await executor.execute_find(find_command, context)

        # Then refine
        result = await executor.execute_refine(refine_command, context)
        assert len(context.temp) < initial_count

    async def test_v1_backward_compatibility(self):
        """Ensure v1 commands still work"""
        # Old style add
        result = await executor.execute_add(old_style_command, context)
        assert "Added" in result

        # Old style list
        result = await executor.execute_list(old_style_command, context)
        assert isinstance(result, str)
```

---

## 三、开发时间表（6天）

### 详细时间规划

| 阶段 | 时间 | 工作内容 | 完成标准 |
|------|------|----------|---------|
| **阶段1** | 1天 | Context三层重构 | v1测试100%通过，v2新API可用 |
| **阶段2** | 4小时 | Command模型增强 | 所有字段有默认值 |
| **阶段3** | 1天 | Parser增强 | 新增FIND/ADD/LIST解析测试通过 |
| **阶段4** | 2天 | Executor增强 | find/add/list命令执行测试通过 |
| **阶段5** | 4小时 | REPL增强 | 提示符显示层状态 |
| **阶段6** | 1天 | 集成测试 | 所有测试通过，向后兼容验证 |
| **总计** | **6天** | 完整v2集成 | 生产就绪 |

### 里程碑

**Milestone 1 (第2天)**: Context重构完成
- ✅ Context有三层架构
- ✅ TTL机制工作
- ✅ v1测试全部通过

**Milestone 2 (第4天)**: 核心命令实现
- ✅ FIND命令可用
- ✅ ADD from可用
- ✅ LIST multi-source可用

**Milestone 3 (第6天)**: 完整v2特性
- ✅ Refine模式(.find)
- ✅ Append模式
- ✅ Focus状态显示
- ✅ 完整集成测试

---

## 四、代码质量保障

### 4.1 向后兼容测试

```python
# 每个阶段后运行
pytest tests/ -v -k "not v2"  # 所有v1测试必须通过
```

### 4.2 新功能测试

```python
# 每个新功能添加单元测试
pytest tests/test_v2_*.py -v
```

### 4.3 集成测试

```python
# 完整工作流测试
pytest tests/test_v2_integration.py -v
```

### 4.4 代码规范

```bash
# 保持代码质量
pylint src/selector_cli/core/context.py
pylint src/selector_cli/parser/parser.py
pylint src/selector_cli/commands/executor.py
```

目标评分：≥ 8.5/10

---

## 五、风险与缓解

### 5.1 主要风险

| 风险 | 概率 | 影响 | 缓解策略 |
|------|------|------|---------|
| 向后兼容破坏 | 中 | 高 | 每阶段运行v1测试套件 |
| TTL机制bug | 低 | 中 | 充分的边界条件测试 |
| 三层数据污染 | 低 | 高 | 只读candidates，复制temp |
| 代码复杂度增加 | 中 | 中 | 保持方法短小，注释清晰 |

### 5.2 回滚策略

如果某个阶段出现问题：

1. **阶段1问题**: 回退Context修改（git reset）
2. **阶段2问题**: Command新增字段可选，不影响现有功能
3. **阶段3问题**: Parser新增方法独立，不影响现有解析
4. **阶段4问题**: Executor新增方法独立，不影响现有执行
5. **阶段5问题**: REPL修改影响小，容易回退

### 5.3 监控指标

- **v1测试通过率**: 必须保持100%
- **代码覆盖率**: ≥ 90%
- **pylint评分**: ≥ 8.5/10
- **循环复杂度**: 每个方法 ≤ 10

---

## 六、实施验证清单

### 6.1 阶段1验证（Context）

- [ ] `Context.candidates`属性可用
- [ ] `Context.temp`属性可用（带TTL）
- [ ] `Context.workspace`属性可用
- [ ] `Context.all_elements`仍指向candidates
- [ ] `Context.collection`仍指向workspace
- [ ] 所有v1测试通过

### 6.2 阶段2验证（Command）

- [ ] Command新增字段有默认值
- [ ] 现有Command使用不受影响
- [ ] JSON序列化/反序列化正常

### 6.3 阶段3验证（Parser）

- [ ] `find button`可解析
- [ ] `find button where visible`可解析
- [ ] `.find where visible`可解析
- [ ] `add from temp`可解析
- [ ] `list candidates`可解析
- [ ] 现有命令解析不受影响

### 6.4 阶段4验证（Executor）

- [ ] `find button`执行成功
- [ ] `find button where visible`执行成功
- [ ] `.find where visible`执行成功
- [ ] `add from temp`执行成功
- [ ] `list candidates`执行成功
- [ ] TTL过期机制工作

### 6.5 阶段5验证（REPL）

- [ ] 提示符显示c:t:w计数
- [ ] Temp过期有友好提示
- [ ] 启动时显示v2功能列表

### 6.6 阶段6验证（集成）

- [ ] 完整三层工作流测试通过
- [ ] v1向后兼容测试通过
- [ ] 所有新功能集成测试通过
- [ ] 性能基准测试通过

---

## 七、提交策略

### 7.1 分支管理

```bash
# 创建集成分支
git checkout -b integrate-v2-gradual

# 每个阶段一个commit
git commit -m "Phase 1: Add three-layer architecture to Context"
git commit -m "Phase 2: Enhance Command with v2 fields"
git commit -m "Phase 3: Add FIND command to Parser"
git commit -m "Phase 4: Implement v2 command execution"
git commit -m "Phase 5: Enhance REPL with layer status"
git commit -m "Phase 6: Add integration tests for v2"

# 最终合并到main
git checkout main
git merge integrate-v2-gradual --no-ff
```

### 7.2 Commit Message规范

```
Phase X: 简短描述

详细说明：
- 新增功能
- 向后兼容说明
- 测试覆盖

影响的文件：
- file1.py
- file2.py

Issue: #XX
```

---

## 八、文档更新

### 8.1 README更新

在README.md中添加v2特性章节：

```markdown
## v2.0 Features (New)

### Three-Layer Architecture
- **candidates**: Scan results (read-only)
- **temp**: Find results (30s TTL)
- **workspace**: Your collection

### New Commands
- `find <type> [where <condition>]` - Query DOM directly
- `.find [where <condition>]` - Refine temp results
- `add from <temp|candidates|workspace>` - Specify source
- `list <candidates|temp|workspace>` - View different layers

### Example Workflow
```bash
selector> scan button, input
candidates: 8 elements

selector> find button where visible
Found 3 → temp

selector> add from temp
Added 3 → workspace
```
```

### 8.2 命令帮助更新

在help命令中添加v2说明：

```python
# In REPL help
def _execute_help(self, command: Command, context: Context) -> str:
    help_text = ""
    help_text += "v2.0 Features:\n"
    help_text += "  find <type> [where <condition>]    Query DOM directly\n"
    help_text += "  .find [where <condition>]          Refine temp results\n"
    help_text += "  add from <source>                  Add from layer\n"
    help_text += "  list <candidates|temp|workspace>   View layer\n"
    return help_text
```

---

## 九、发布计划

### 9.1 版本号

**v2.0.0** - 完整v2功能发布

### 9.2 发布检查清单

- [ ] 所有阶段完成
- [ ] 所有测试通过
- [ ] 向后兼容验证
- [ ] README更新
- [ ] 帮助文档更新
- [ ] 版本号更新
- [ ] CHANGELOG.md更新
- [ ] PyPI发布准备

---

## 十、结论

### 10.1 方案优势

**vs. 快速移植（复制文件）**:
- ✅ 真正的"水乳交融"，代码统一
- ✅ 更容易维护（无重复代码）
- ✅ 更好的向后兼容
- ✅ 代码质量更高（原始实现更高）

**vs. 重写实现**:
- ✅ 利用现有代码（成熟稳定）
- ✅ v1测试继续有效
- ✅ 开发速度更快（6天 vs 2周）
- ✅ 风险更低（逐步验证）

### 10.2 最终交付物

完成本计划后，main分支将：
- ✅ 拥有完整的三层架构
- ✅ 支持FIND命令和Refine模式
- ✅ 支持add from/list source/export from
- ✅ 拥有TTL过期机制
- ✅ 显示层状态的智能提示符
- ✅ 100%向后兼容v1语法
- ✅ 完整的测试覆盖
- ✅ 生产就绪的代码质量

---

**方案制定**: 2025-11-24
**预计完成**: 6天后（2025-11-30）
**核心原则**: 水乳交融、渐进式、向后兼容

**下一步**: 开始阶段1 - Context三层架构重构
