# Phase 2 开发进度 - 继续指南

**当前状态**: 词法和数据结构完成，语法分析器待实现
**更新时间**: 2025-11-22

---

## ✅ 已完成 (2025-11-22)

### 1. 词法分析器扩展 ✅
**文件**: `src/parser/lexer.py`

**新增 Token 类型**:
```python
# Comparison operators
GT, GTE, LT, LTE         # >, >=, <, <=

# String operators
CONTAINS, STARTS, ENDS, MATCHES   # 字符串操作

# Delimiters
LPAREN, RPAREN          # (, )
DASH                    # - (for ranges)

# Literals
TRUE, FALSE             # boolean literals
```

**新增关键字**:
- `contains`, `starts`, `ends`, `matches` - 字符串操作
- `true`, `false` - 布尔字面量

**测试**: `tests/test_phase2_lexer.py` - 全部通过 ✅

### 2. 命令数据结构扩展 ✅
**文件**: `src/parser/command.py`

**新增数据结构**:
```python
class ConditionType(Enum):
    SIMPLE = auto()      # field op value
    COMPOUND = auto()    # left logic_op right
    UNARY = auto()       # not operand

class ConditionNode:
    """条件树节点，支持递归嵌套"""
    type: ConditionType
    # SIMPLE
    field, operator, value
    # COMPOUND
    left, right, logic_op
    # UNARY
    operand
```

**扩展操作符**:
```python
class Operator(Enum):
    EQUALS, NOT_EQUALS      # =, !=
    GT, GTE, LT, LTE        # >, >=, <, <=
    CONTAINS, STARTS, ENDS, MATCHES  # 字符串

class LogicOp(Enum):
    AND, OR, NOT
```

**向后兼容**: 保留了 Phase 1 的 `Condition` 类

---

## ⏳ 进行中 (下一步)

### 3. 语法分析器扩展
**文件**: `src/parser/parser.py`

**需要实现的方法**:

#### 3.1 复杂条件解析（核心）

```python
def _parse_where_clause_v2(self) -> ConditionNode:
    """Parse complex WHERE clause with and/or/not and parentheses

    Grammar (with operator precedence):
        condition = or_condition
        or_condition = and_condition ('or' and_condition)*
        and_condition = not_condition ('and' not_condition)*
        not_condition = 'not' not_condition | primary_condition
        primary_condition = '(' condition ')' | simple_condition
        simple_condition = field operator value

    Operator precedence (high to low):
        1. Parentheses ()
        2. NOT
        3. AND
        4. OR
    """
    self._consume(TokenType.WHERE)
    return self._parse_or_condition()

def _parse_or_condition(self) -> ConditionNode:
    """Parse OR expressions (lowest precedence)"""
    left = self._parse_and_condition()

    while self._current_token().type == TokenType.OR:
        self._advance()
        right = self._parse_and_condition()
        left = ConditionNode(
            type=ConditionType.COMPOUND,
            left=left,
            right=right,
            logic_op=LogicOp.OR
        )

    return left

def _parse_and_condition(self) -> ConditionNode:
    """Parse AND expressions (higher precedence than OR)"""
    left = self._parse_not_condition()

    while self._current_token().type == TokenType.AND:
        self._advance()
        right = self._parse_not_condition()
        left = ConditionNode(
            type=ConditionType.COMPOUND,
            left=left,
            right=right,
            logic_op=LogicOp.AND
        )

    return left

def _parse_not_condition(self) -> ConditionNode:
    """Parse NOT expressions (highest precedence)"""
    if self._current_token().type == TokenType.NOT:
        self._advance()
        operand = self._parse_not_condition()  # Right associative
        return ConditionNode(
            type=ConditionType.UNARY,
            operand=operand
        )

    return self._parse_primary_condition()

def _parse_primary_condition(self) -> ConditionNode:
    """Parse primary condition (parentheses or simple)"""
    # Parentheses
    if self._current_token().type == TokenType.LPAREN:
        self._consume(TokenType.LPAREN)
        condition = self._parse_or_condition()  # Recurse from top
        self._consume(TokenType.RPAREN)
        return condition

    # Simple condition
    return self._parse_simple_condition()

def _parse_simple_condition(self) -> ConditionNode:
    """Parse simple condition: field operator value"""
    # Field
    if self._current_token().type != TokenType.IDENTIFIER:
        raise ValueError("Expected field name")
    field = self._current_token().value
    self._advance()

    # Operator
    op_token = self._current_token()
    operator = self._token_to_operator(op_token)
    self._advance()

    # Value
    value = self._parse_value()

    return ConditionNode(
        type=ConditionType.SIMPLE,
        field=field,
        operator=operator,
        value=value
    )

def _token_to_operator(self, token: Token) -> Operator:
    """Convert token to Operator enum"""
    mapping = {
        TokenType.EQUALS: Operator.EQUALS,
        TokenType.NOT_EQUALS: Operator.NOT_EQUALS,
        TokenType.GT: Operator.GT,
        TokenType.GTE: Operator.GTE,
        TokenType.LT: Operator.LT,
        TokenType.LTE: Operator.LTE,
        TokenType.CONTAINS: Operator.CONTAINS,
        TokenType.STARTS: Operator.STARTS,
        TokenType.ENDS: Operator.ENDS,
        TokenType.MATCHES: Operator.MATCHES,
    }
    if token.type not in mapping:
        raise ValueError(f"Invalid operator: {token.type}")
    return mapping[token.type]

def _parse_value(self) -> Any:
    """Parse value (string, number, boolean, identifier)"""
    token = self._current_token()

    if token.type == TokenType.STRING:
        value = token.value
        self._advance()
        return value
    elif token.type == TokenType.NUMBER:
        value = int(token.value)
        self._advance()
        return value
    elif token.type == TokenType.TRUE:
        self._advance()
        return True
    elif token.type == TokenType.FALSE:
        self._advance()
        return False
    elif token.type == TokenType.IDENTIFIER:
        # Field reference (like "visible" as boolean field)
        value = token.value
        self._advance()
        return value
    else:
        raise ValueError(f"Expected value, got {token.type}")
```

#### 3.2 范围解析

```python
def _parse_target(self) -> Target:
    """Parse target with range support"""
    # ... existing code ...

    # Range: [1-10] or mixed [1,3,5-8,10]
    if current.type == TokenType.LBRACKET:
        self._consume(TokenType.LBRACKET)

        indices = []
        ranges = []

        while self._current_token().type != TokenType.RBRACKET:
            # Parse number
            if self._current_token().type == TokenType.NUMBER:
                start = int(self._current_token().value)
                self._advance()

                # Check for range
                if self._current_token().type == TokenType.DASH:
                    self._consume(TokenType.DASH)
                    if self._current_token().type == TokenType.NUMBER:
                        end = int(self._current_token().value)
                        self._advance()
                        ranges.append((start, end))
                    else:
                        raise ValueError("Expected number after -")
                else:
                    indices.append(start)

                # Check for comma
                if self._current_token().type == TokenType.COMMA:
                    self._consume(TokenType.COMMA)

        self._consume(TokenType.RBRACKET)

        # Expand ranges to indices
        for start, end in ranges:
            indices.extend(range(start, end + 1))

        if len(indices) == 1 and not ranges:
            return Target(type=TargetType.INDEX, indices=indices)
        else:
            return Target(type=TargetType.INDICES, indices=indices)
```

#### 3.3 更新命令解析方法

```python
def _parse_add(self, raw: str) -> Command:
    """Parse: add <target> [where <complex_condition>]"""
    self._consume(TokenType.ADD)
    target = self._parse_target()

    # Use v2 WHERE parser for complex conditions
    condition_tree = None
    if self._current_token().type == TokenType.WHERE:
        condition_tree = self._parse_where_clause_v2()

    return Command(
        verb='add',
        target=target,
        condition_tree=condition_tree,  # Use new field
        raw=raw
    )
```

---

## 📋 待实现功能清单

### 高优先级
- [ ] 语法分析器：复杂条件解析（见上文）
- [ ] 语法分析器：范围解析 `[1-10]`
- [ ] 条件求值器：`executor.py` 中的 `_evaluate_condition_tree()`
- [ ] 测试：复杂条件解析测试
- [ ] 测试：范围选择测试

### 中优先级
- [ ] 新命令：`keep <condition>`
- [ ] 新命令：`filter <condition>`
- [ ] 布尔字段支持：`visible`, `enabled`, `disabled` 等
- [ ] 帮助信息更新

### 低优先级
- [ ] 文档更新：README.md
- [ ] 文档更新：示例脚本
- [ ] CHANGELOG 更新

---

## 🧪 测试用例设计

### 复杂条件测试

```python
def test_complex_conditions():
    """Test complex WHERE clause parsing"""
    parser = Parser()

    # AND
    cmd = parser.parse("add input where type=\"text\" and visible")
    assert cmd.condition_tree.type == ConditionType.COMPOUND
    assert cmd.condition_tree.logic_op == LogicOp.AND

    # OR
    cmd = parser.parse("add input where type=\"text\" or type=\"email\"")
    assert cmd.condition_tree.type == ConditionType.COMPOUND
    assert cmd.condition_tree.logic_op == LogicOp.OR

    # NOT
    cmd = parser.parse("add input where not disabled")
    assert cmd.condition_tree.type == ConditionType.UNARY

    # Parentheses
    cmd = parser.parse("add input where (type=\"text\" or type=\"email\") and visible")
    assert cmd.condition_tree.type == ConditionType.COMPOUND
    assert cmd.condition_tree.logic_op == LogicOp.AND

    # Complex
    cmd = parser.parse("add input where (type=\"text\" or type=\"email\") and not disabled and visible")

    # String operators
    cmd = parser.parse("add button where text contains \"Submit\"")
    assert cmd.condition_tree.operator == Operator.CONTAINS

    # Comparison
    cmd = parser.parse("list where index > 5 and index < 20")
```

### 范围选择测试

```python
def test_range_selection():
    """Test range parsing"""
    parser = Parser()

    # Simple range
    cmd = parser.parse("add [1-10]")
    assert cmd.target.type == TargetType.INDICES
    assert 1 in cmd.target.indices
    assert 10 in cmd.target.indices
    assert len(cmd.target.indices) == 10

    # Mixed range
    cmd = parser.parse("add [1,3,5-8,10]")
    assert cmd.target.indices == [1, 3, 5, 6, 7, 8, 10]
```

---

## 🔧 实现条件求值器

**文件**: `src/commands/executor.py`

```python
def _evaluate_condition_tree(self, elem: Element, condition: ConditionNode) -> bool:
    """Evaluate complex condition tree"""

    if condition.type == ConditionType.SIMPLE:
        return self._evaluate_simple_condition(elem, condition)

    elif condition.type == ConditionType.COMPOUND:
        left_result = self._evaluate_condition_tree(elem, condition.left)
        right_result = self._evaluate_condition_tree(elem, condition.right)

        if condition.logic_op == LogicOp.AND:
            return left_result and right_result
        elif condition.logic_op == LogicOp.OR:
            return left_result or right_result

    elif condition.type == ConditionType.UNARY:
        operand_result = self._evaluate_condition_tree(elem, condition.operand)
        return not operand_result

    return False

def _evaluate_simple_condition(self, elem: Element, condition: ConditionNode) -> bool:
    """Evaluate simple condition"""
    # Get field value
    field_value = self._get_field_value(elem, condition.field)
    compare_value = condition.value
    operator = condition.operator

    # Comparison
    if operator == Operator.EQUALS:
        return str(field_value) == str(compare_value)
    elif operator == Operator.NOT_EQUALS:
        return str(field_value) != str(compare_value)
    elif operator == Operator.GT:
        return self._to_number(field_value) > self._to_number(compare_value)
    elif operator == Operator.GTE:
        return self._to_number(field_value) >= self._to_number(compare_value)
    elif operator == Operator.LT:
        return self._to_number(field_value) < self._to_number(compare_value)
    elif operator == Operator.LTE:
        return self._to_number(field_value) <= self._to_number(compare_value)

    # String operators
    elif operator == Operator.CONTAINS:
        return str(compare_value) in str(field_value)
    elif operator == Operator.STARTS:
        return str(field_value).startswith(str(compare_value))
    elif operator == Operator.ENDS:
        return str(field_value).endswith(str(compare_value))
    elif operator == Operator.MATCHES:
        import re
        return bool(re.search(str(compare_value), str(field_value)))

    return False

def _get_field_value(self, elem: Element, field: str) -> Any:
    """Get field value from element"""
    # Direct attribute
    if hasattr(elem, field):
        return getattr(elem, field)

    # From attributes dict
    if field in elem.attributes:
        return elem.attributes[field]

    # Boolean fields (treat as boolean if field name is a boolean keyword)
    if field in ['visible', 'enabled', 'disabled', 'required', 'readonly']:
        if field == 'visible':
            return elem.visible
        elif field == 'enabled':
            return elem.enabled
        elif field == 'disabled':
            return elem.disabled
        # Add more as needed

    return ""

def _to_number(self, value: Any) -> float:
    """Convert value to number for comparison"""
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0
```

---

## 📝 下次会话开始时

### 1. 检查当前状态
```bash
cd F:/browser-use/selector-cli
python tests/test_phase2_lexer.py  # 应该通过
python tests/test_mvp.py           # 确保没有破坏 Phase 1
```

### 2. 继续开发步骤

1. **实现语法分析器**
   - 复制上文的代码到 `parser.py`
   - 更新所有命令解析方法使用 `condition_tree`

2. **实现条件求值器**
   - 更新 `executor.py` 中的 `_execute_add/remove/list`
   - 添加 `_evaluate_condition_tree` 方法

3. **测试**
   - 创建 `tests/test_phase2_parser.py`
   - 创建 `tests/test_phase2_integration.py`

4. **文档**
   - 更新 README.md
   - 更新 CHANGELOG.md

### 3. 快速验证脚本

```python
# test_phase2_quick.py
from src.parser.parser import Parser

parser = Parser()

# Test cases
tests = [
    "add input where (type=\"text\" or type=\"email\") and not disabled",
    "list where index > 5 and index < 20",
    "add button where text contains \"Submit\"",
    "add [1-10]",
]

for test in tests:
    try:
        cmd = parser.parse(test)
        print(f"✓ {test}")
        print(f"  Condition tree: {cmd.condition_tree}")
    except Exception as e:
        print(f"✗ {test}")
        print(f"  Error: {e}")
```

---

## 🎯 Phase 2 完成标准

- [ ] 所有 Phase 1 测试仍然通过
- [ ] 复杂 WHERE 子句正常工作
- [ ] 范围选择正常工作
- [ ] 字符串操作符正常工作
- [ ] 比较操作符正常工作
- [ ] 新增测试覆盖 Phase 2 功能
- [ ] 文档已更新
- [ ] CHANGELOG 已更新

---

**预计剩余工作量**: 3-4 小时

**下次会话请从"实现语法分析器"开始！**
