# Selector CLI - 核心模块详细分析文档（第二部分）

**项目版本**: v1.0.6 (main分支)
**代码总行数**: 约4,800行
**文档生成日期**: 2025-11-24

---

## 1. 解析层（Parser Layer）

### 1.1 词法分析器（Lexer）

**文件**: `src/selector_cli/parser/lexer.py`
**代码行数**: 412行
**核心职责**: 将输入字符串转换为Token序列

#### 1.1.1 Token类型定义

```python
class TokenType(Enum):
    # 关键字
    OPEN = 'OPEN'
    SCAN = 'SCAN'
    ADD = 'ADD'
    REMOVE = 'REMOVE'
    LIST = 'LIST'
    QUIT = 'QUIT'
    ...,  # 更多关键字

    # 操作符
    WHERE = 'WHERE'
    AND = 'AND'
    OR = 'OR'
    NOT = 'NOT'
    EQUALS = '='
    NOT_EQUALS = '!='
    GREATER = '>'
    LESS = '<'
    CONTAINS = 'CONTAINS'
    STARTS = 'STARTS'
    ENDS = 'ENDS'
    MATCHES = 'MATCHES'

    # 字面量
    STRING = 'STRING'
    NUMBER = 'NUMBER'
    INDENTIFIER = 'IDENTIFIER'

    # v2增强
    FIND = 'FIND'
    PREVIEW = 'PREVIEW'
    EXPORT = 'EXPORT'
    FROM = 'FROM'
    TEMP = 'TEMP'
    WORKSPACE = 'WORKSPACE'
    APPEND = 'APPEND'
    DOT = '.'

    EOF = 'EOF'
```

#### 1.1.2 Lexer核心算法

```python
def tokenize(self, input_str: str) -> List[Token]:
    """
    将输入字符串转换为Token序列

    算法复杂度: O(n)，n为输入长度
    内存复杂度: O(n)，存储Token序列

    处理流程:
    1. 跳过空白字符（空格、制表符）
    2. 识别关键字（通过KEYWORDS字典）
    3. 处理字符串字面量（支持引号转义）
    4. 处理数字（整数、小数）
    5. 处理操作符（多字符操作符如!=）
    6. 剩余作为标识符（IDENTIFIER）
    """

    while self.pos < len(input_str):
        ch = input_str[self.pos]

        # 1. 空白跳过
        if ch.isspace():
            self._skip_whitespace()
            continue

        # 2. URL特殊处理（: / .）
        if self.pos < len(input_str) - 2 and ch.isalpha():
            if self._try_match_url():
                continue

        # 3. 字符串字面量
        if ch in ('"', "'"):
            tokens.append(self._read_string(ch))
            continue

        # 4. 数字
        if ch.isdigit() or ch == '.':
            tokens.append(self._read_number())
            continue

        # 5. 操作符匹配（最长匹配优先）
        token = self._try_match_operator()
        if token:
            tokens.append(token)
            continue

        # 6. 关键字匹配
        token = self._try_match_keyword()
        if token:
            tokens.append(token)
            continue

        # 7. 默认：标识符
        tokens.append(self._read_identifier())
```

#### 1.1.3 URL解析特殊处理

```python
def _try_match_url(self) -> bool:
    """
    尝试匹配URL（例如：http://example.com/path?param=value#anchor）

    特点:
    - 识别URL特有字符: / : . ? # = &
    - 支持http://, https:// 等协议前缀
    - 支持域名 (example.com)
    - 支持路径 (/path)
    - 支持查询参数 (?key=value)
    - 支持锚点 (#section)
    """

    start = self.pos

    # 匹配协议 (http://, https://)
    if self.input_str[self.pos:self.pos+7] in ('http://', 'https://'):
        self.pos += 7

    # 匹配域名路径部分（允许字母、数字、特殊字符）
    url_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._~:/?#[]@!$&\'()*+,;=')

    while self.pos < len(self.input_str) and self.input_str[self.pos] in url_chars:
        self.pos += 1

    # 如果匹配成功，返回URL token
    if self.pos > start:
        self.tokens.append(Token(
            type=TokenType.IDENTIFIER,
            value=self.input_str[start:self.pos],
            position=start
        ))
        return True

    return False
```

#### 1.1.4 字符串解析（支持转义）

```python
def _read_string(self, quote_char: str) -> Token:
    """
    读取字符串字面量，支持转义字符

    示例:
    - "hello world"           → hello world
    - 'value with "quotes"'  → value with "quotes"
    - "escape \"quote\""       → escape "quote"

    实现:
    1. 记录起始引号
    2. 逐个字符读取，检查转义
    3. 遇到闭合引号停止
    4. 处理转义序列（", \n, \t, \\）
    """

    start = self.pos
    value = []
    self.pos += 1  # 跳过起始引号

    while self.pos < len(self.input_str):
        ch = self.input_str[self.pos]

        # 闭合引号
        if ch == quote_char:
            self.pos += 1
            break

        # 转义字符
        if ch == '\\':
            self.pos += 1

            if self.pos < len(self.input_str):
                next_ch = self.input_str[self.pos]

                if next_ch == 'n':
                    value.append('\n')
                elif next_ch == 't':
                    value.append('\t')
                else:
                    value.append(next_ch)

                self.pos += 1
                continue

        # 普通字符
        value.append(ch)
        self.pos += 1

    return Token(
        type=TokenType.STRING,
        value=''.join(value),
        position=start
    )
```

### 1.2 语法分析器（Parser）

**文件**: `src/selector_cli/parser/parser.py` (v1: 856行)
**文件**: `src/selector_cli_v2/v2/parser.py` (v2: 14,792行)
**核心职责**: 构建抽象语法树（AST），转换为Command对象

#### 1.2.1 v1 Parser架构

**支持的命令格式**：
```ebnf
command := verb target? (where condition)?

verb    := 'open' | 'scan' | 'add' | 'remove' | 'list' | ...
target  := element_type | index | indices | 'all'
condition := field operator value (and|or condition)*
```

**核心解析流程**：
```python
def parse(self, command_str: str) -> Command:
    """
    主解析入口

    步骤:
    1. Lexer生成Token序列
    2. 解析verb（parse_verb）
    3. 解析target（parse_target）
    4. 可选：解析WHERE子句（parse_where_clause）
    """

    tokens = self.lexer.tokenize(command_str)
    self._reset(tokens)

    # 解析verb
    verb_token = self._current_token()
    if verb_token.type not in VERB_TOKENS:
        raise SyntaxError(f"Expected verb, got {verb_token.value}")

    verb = verb_token.value
    self._advance()

    # 解析target（可选）
    target = None
    if self._current_token().type == IDENTIFIER:
        target = self._parse_target()

    # 解析WHERE子句（可选）
    condition = None
    if self._current_token().type == WHERE:
        condition = self._parse_where_clause()

    return Command(
        verb=verb,
        target=target,
        condition=condition
    )
```

#### 1.2.2 WHERE子句解析（递归下降）

```python
def _parse_where_clause(self) -> ConditionNode:
    """
    解析WHERE子句，返回条件树（ConditionNode）

    BNF文法:
    where_clause := "where" expression
    expression   := term ("and" term | "or" term)*
    term         := "not" term | condition | "(" expression ")"
    condition    := field operator value

    示例:
    - where type="email"
    - where visible and enabled
    - where text contains "Submit" or id="submit"
    - where (type="email" or type="text") and visible
    """

    self._consume(WHERE)

    # 解析顶层表达式
    return self._parse_expression()

def _parse_expression(self) -> ConditionNode:
    """解析表达式（支持and/or组合）"""

    # 解析左项
    left = self._parse_term()

    # 检查是否有逻辑运算符
    token = self._current_token()
    if token.type in (AND, OR):
        op = token.value  # 'and' or 'or'
        self._advance()

        # 递归解析右项
        right = self._parse_expression()

        # 构建逻辑节点
        return ConditionNode(
            type=LOGICAL,
            operator=op,
            left=left,
            right=right
        )

    return left

def _parse_term(self) -> ConditionNode:
    """解析单个项（可能是not、条件或括号表达式）"""

    token = self._current_token()

    # "not" 否定
    if token.type == NOT:
        self._advance()
        node = self._parse_term()
        return ConditionNode(
            type=LOGICAL,
            operator='not',
            left=node
        )

    # 括号表达式
    if token.type == LEFT_PAREN:
        self._consume(LEFT_PAREN)
        node = self._parse_expression()
        self._consume(RIGHT_PAREN)
        return node

    # 基础条件（field operator value）
    return self._parse_condition()

def _parse_condition(self) -> ConditionNode:
    """解析基础条件: field operator value"""

    # 解析字段
    field_token = self._current_token()
    field = field_token.value
    self._advance()

    # 解析操作符
    op_token = self._current_token()
    operator = self._map_operator(op_token.type)
    self._advance()

    # 解析值
    value = self._parse_value()

    return ConditionNode(
        type=CONDITION,
        field=field,
        operator=operator,
        value=value
    )
```

#### 1.2.3 复杂操作符映射

```python
def _map_operator(self, token_type) -> Operator:
    """Token类型 → Operator枚举"""

    mapping = {
        EQUALS: Operator.EQUALS,              # =
        NOT_EQUALS: Operator.NOT_EQUALS,      # !=
        GREATER: Operator.GREATER,            # >
        LESS: Operator.LESS,                  # <
        CONTAINS: Operator.CONTAINS,          # contains
        STARTS: Operator.STARTS_WITH,         # starts
        ENDS: Operator.ENDS_WITH,             # ends
        MATCHES: Operator.MATCHES,            # matches (regex)
    }

    if token_type not in mapping:
        raise SyntaxError(f"Unknown operator: {token_type}")

    return mapping[token_type]
```

### 1.3 v2 Parser增强

**文件**: `src/selector_cli_v2/v2/parser.py`
**主要增强**:
1. 支持 `.find` 命令（直接查询DOM）
2. 支持 `from <source>` 语法
3. 支持逗号分隔的多个元素类型（`scan button, input, div`）
4. 支持 `append` 模式

#### 1.3.1 多元素类型解析

```python
def _parse_element_types(self) -> List[str]:
    """
    解析逗号分隔的元素类型列表

    示例:
    - "scan button"           → ['button']
    - "scan button, input"    → ['button', 'input']
    - "scan button, input, div" → ['button', 'input', 'div']
    - "scan *"               → ['*'] (wildcard)

    算法:
    1. 解析第一个元素类型
    2. 如果后续是逗号，继续解析下一个
    3. 重复直到没有逗号
    """

    types: List[str] = []

    # 解析第一个类型
    current = self._current_token()
    types.append(current.value)
    self._advance()

    # 解析逗号分隔的后续类型
    while self._current_token().type == COMMA:
        self._consume(COMMA)
        current = self._current_token()
        types.append(current.value)
        self._advance()

    return types
```

#### 1.3.2 v2命令增强

```python
def parse(self, command_str: str) -> CommandV2:
    """
    v2增强解析入口

    新增语法:
    - find button where visible          # 查询DOM
    - .find where enabled               # 基于temp层筛选
    - add from temp where type="email"  # 从temp层添加
    - add append button                 # append模式（不覆盖）
    - list temp                         # 查看temp层
    """

    # 检查是否v2命令
    if self._is_v2_verb():
        return self._parse_v2_command()

    # 回退到v1解析
    return self._parse_v1_command()
```

---

## 2. 执行层（Executor Layer）

### 2.1 v2 Executor架构

**文件**: `src/selector_cli_v2/v2/executor.py`
**代码行数**: 17,836行
**核心职责**: 命令分发、条件求值、三层数据流转

#### 2.1.1 主执行循环

```python
async def execute(self, cmd: CommandV2) -> Tuple[bool, Any]:
    """
    主执行入口 - 分发到对应处理器

    返回:
    - success: bool - 执行是否成功
    - result: Any - 结果（字符串或对象）
    """

    handlers = {
        'find': self.execute_find,
        'add': self.execute_add,
        'list': self.execute_list,
        'scan': self.execute_scan,
        'preview': self.execute_preview,
        'export': self.execute_export,
        'remove': self.execute_remove,
        'clear': self.execute_clear,
    }

    if cmd.verb not in handlers:
        return False, f"Unsupported command: {cmd.verb}"

    try:
        result = await handlers[cmd.verb](cmd)
        return True, result
    except Exception as e:
        return False, str(e)
```

#### 2.1.2 find命令实现（核心创新）

```python
async def execute_find(self, cmd: CommandV2) -> List[Element]:
    """
    执行find命令 - 查询DOM并存储到temp层

    工作流程:
    1. 确定数据源（DOM或temp层）
    2. 查询元素（调用ElementScanner）
    3. 应用WHERE条件过滤
    4. 存储到temp层（30秒有效期）
    5. 更新focus状态

    示例:
    - find input where type="email"    # 从DOM查询
    - .find where visible              # 从temp层筛选
    """

    if not self.ctx.browser or not self.ctx.browser.get_page():
        raise ValueError("No browser/page loaded")

    page = self.ctx.browser.get_page()

    # 1. 确定数据源
    if cmd.is_refine_command():  # .find
        elements = self.ctx.temp.copy()
    elif cmd.source == "temp":
        elements = self.ctx.temp.copy()
    elif cmd.source == "candidates":
        elements = self.ctx.candidates.copy()
    elif cmd.source == "workspace":
        elements = self.ctx.workspace.get_all()
    else:
        # 默认：直接查询DOM
        elements = await self._query_dom(page, cmd)

    # 2. 应用条件过滤
    if cmd.condition_tree:
        elements = self._filter_elements(elements, cmd.condition_tree)

    # 3. 存储到temp（触发TTL计时）
    self.ctx.temp = elements

    # 4. 更新focus
    self.ctx.focus = 'temp'

    return elements
```

#### 2.1.2 DOM查询实现

```python
async def _query_dom(self, page: Page, cmd: CommandV2) -> List[Element]:
    """
    从DOM查询元素（类似scan，但支持WHERE条件预筛选）

    挑战:
    - Playwright获取元素后，才能读取属性
    - 需要先获取所有元素，再应用条件过滤
      → O(n)时间复杂度

    优化思路:
    - 可以尝试在JavaScript中预筛选（但需要同步Attribute）
    """

    scanner = ElementScanner()

    # 查询指定类型的所有元素
    element_types = cmd.element_types or ['input', 'button', 'a', 'select', 'textarea']

    all_elements = []
    for elem_type in element_types:
        elements = await scanner.scan(page, [elem_type])
        all_elements.extend(elements)

    return all_elements
```

#### 2.1.3 条件求值引擎

```python
def _filter_elements(
    self,
    elements: List[Element],
    condition_tree: ConditionNode
) -> List[Element]:
    """
    基于条件树过滤元素

    支持的操作:
    - 逻辑运算: and, or, not
    - 字段比较: type="email", id!="", cost<0.2
    - 字符串操作: contains, starts, ends, matches(regex)
    """

    result = []

    for element in elements:
        if self._evaluate_condition(element, condition_tree):
            result.append(element)

    return result

def _evaluate_condition(
    self,
    element: Element,
    node: ConditionNode
) -> bool:
    """
    对单个元素求值条件节点

    处理三种节点类型:
    1. CONDITION: 基础条件（字段比较）
    2. LOGICAL with 操作符 and/or: 左右递归求值
    3. LOGICAL with 操作符 not: 单节点求值后取反
    """

    # 基础条件
    if node.type == ConditionType.CONDITION:
        return self._evaluate_base_condition(element, node)

    # 逻辑节点
    if node.type == ConditionType.LOGICAL:
        if node.operator == 'and':
            return (self._evaluate_condition(element, node.left) and
                    self._evaluate_condition(element, node.right))

        elif node.operator == 'or':
            return (self._evaluate_condition(element, node.left) or
                    self._evaluate_condition(element, node.right))

        elif node.operator == 'not':
            return not self._evaluate_condition(element, node.left)

    return False

def _evaluate_base_condition(
    self,
    element: Element,
    node: ConditionNode
) -> bool:
    """
    求值基础条件: field operator value

    支持的字段:
    - tag, type, id, name, class, text, selector, xpath
    - visible, enabled, disabled (布尔值)
    - selector_cost, index (数值)

    操作符:
    - EQUALS, NOT_EQUALS, GREATER, LESS
    - CONTAINS, STARTS_WITH, ENDS_WITH, MATCHES
    """

    field = node.field
    value = node.value
    operator = node.operator

    # 获取元素字段值
    element_value = self._get_field_value(element, field)

    # 字符串操作
    if operator == Operator.CONTAINS:
        return value.lower() in str(element_value).lower()

    if operator == Operator.STARTS_WITH:
        return str(element_value).lower().startswith(value.lower())

    if operator == Operator.ENDS_WITH:
        return str(element_value).lower().endswith(value.lower())

    if operator == Operator.MATCHES:
        pattern = re.compile(value, re.IGNORECASE)
        return bool(pattern.search(str(element_value)))

    # 数值比较
    if operator == Operator.EQUALS:
        return element_value == value

    if operator == Operator.NOT_EQUALS:
        return element_value != value

    if operator == Operator.GREATER:
        return float(element_value) > float(value)

    if operator == Operator.LESS:
        return float(element_value) < float(value)

    return False
```

#### 2.1.4 add命令实现（数据流转）

```python
async def execute_add(self, cmd: CommandV2) -> int:
    """
    执行add命令 - 从指定源添加元素到workspace

    工作流程:
    1. 确定源（candidates/temp/workspace）
    2. 获取源元素
    3. 按类型筛选（如果指定element_types）
    4. 应用WHERE条件过滤
    5. 添加到workspace（overwrite或append模式）

    示例:
    - add input                 # 从candidates添加所有input
    - add from temp             # 从temp层添加所有
    - add append button         # append模式（不覆盖）
    - add where selector_cost < 0.2  # 添加高质量选择器
    """

    # 1. 确定源（默认为candidates）
    source = cmd.source or "candidates"

    # 2. 获取源元素
    if source == "candidates":
        source_elements = self.ctx.candidates
    elif source == "temp":
        source_elements = self.ctx.temp
    elif source == "workspace":
        source_elements = self.ctx.workspace.get_all()

    # 3. 按元素类型筛选
    if cmd.element_types:
        elements_to_add = []
        for elem_type in cmd.element_types:
            if elem_type == "*":
                elements_to_add.extend(source_elements)
            else:
                elements_to_add.extend(
                    [e for e in source_elements if e.tag == elem_type]
                )
    else:
        elements_to_add = source_elements

    # 4. 应用WHERE条件
    if cmd.condition_tree:
        elements_to_add = self._filter_elements(
            elements_to_add,
            cmd.condition_tree
        )

    # 5. 添加到workspace
    if cmd.is_append_mode():
        # append模式：仅添加不存在的
        added_count = 0
        for elem in elements_to_add:
            if not self.ctx.workspace.contains(elem):
                self.ctx.workspace.add(elem)
                added_count += 1
    else:
        # overwrite模式：智能添加
        added_count = self.ctx.add_many_to_workspace(elements_to_add)

    return added_count
```

---

## 3. 元素管理层（Element Management）

### 3.1 Element模型

**文件**: `src/selector_cli/core/element.py`
**代码行数**: 114行
**设计模式**: Data Class（Python dataclass）

#### 3.1.1 字段设计

```python
@dataclass
class Element:
    """Web元素表示"""

    # =============================================
    # 基础识别信息
    # =============================================
    index: int                      # 在扫描中的顺序索引
    uuid: str                       # 唯一标识符（用于去重）

    # =============================================
    # 元素属性（从DOM读取）
    # =============================================
    tag: str                        # 标签名（input, button, div等）
    type: str = ""                  # type属性
    text: str = ""                  # 文本内容（截断100字符）
    value: str = ""                 # value属性

    # =============================================
    # 计算属性（从attributes提取）
    # =============================================
    name: str = ""
    id: str = ""
    classes: List[str] = field(default_factory=list)  # 类名列表
    placeholder: str = ""

    # =============================================
    # 定位信息
    # =============================================
    selector: str = ""              # CSS选择器（最优）
    xpath: str = ""                 # XPath（备用）
    path: str = ""                  # 元素路径

    # =============================================
    # 策略元数据（BONUS系统核心）
    # =============================================
    selector_cost: Optional[float] = None   # 4维成本（越低越好）
    strategy_used: Optional[str] = None     # 使用的策略名

    # =============================================
    # 状态信息
    # =============================================
    visible: bool = True            # 是否可见
    enabled: bool = True            # 是否启用
    disabled: bool = False          # 是否禁用

    # =============================================
    # Shadow DOM支持
    # =============================================
    in_shadow: bool = False         # 是否在Shadow DOM中
    shadow_host: Optional[str] = None  # Shadow Host信息
    shadow_path: Optional[str] = None  # Shadow路径

    # =============================================
    # Playwright运行时引用
    # =============================================
    locator: Optional[Locator] = None     # Playwright Locator
    handle: Optional[ElementHandle] = None # 元素句柄

    # =============================================
    # 元数据
    # =============================================
    scanned_at: datetime = field(default_factory=datetime.now)
    page_url: str = ""              # 扫描时的页面URL
```

#### 3.1.2 __str__格式化

```python
def __str__(self) -> str:
    """
    简洁字符串表示，用于list/show命令输出

    格式:
    [index] tag type="value" id="id" name="name" placeholder="text"

    示例:
    [0] input type="email" id="login_field" name="login"
    [1] button type="submit" text="Sign in"
    """

    parts = [f"[{self.index}]", self.tag]

    if self.type:
        parts.append(f'type="{self.type}"')
    if self.id:
        parts.append(f'id="{self.id}"')
    if self.name:
        parts.append(f'name="{self.name}"')
    if self.placeholder:
        parts.append(f'placeholder="{self.placeholder}"')
    if self.text and len(self.text) <= 30:
        parts.append(f'text="{self.text}"')

    # 显示成本（如果可用）
    if self.selector_cost is not None:
        stars = int(5 - self.selector_cost * 10)  # 0.2 = ⭐⭐⭐⭐⭐
        parts.append(f" ⭐{'⭐' * max(0, stars-1)}")

    return " ".join(parts)
```

#### 3.1.3 序列化（to_dict/from_dict）

```python
def to_dict(self) -> dict:
    """
    序列化为字典（用于JSON持久化）

    注意:
    - 排除locator/handle（内存对象无法JSON序列化）
    - datetime转换为ISO格式字符串
    - classes列表正常序列化
    """

    return {
        'index': self.index,
        'uuid': self.uuid,
        'tag': self.tag,
        'type': self.type,
        'text': self.text,
        'value': self.value,
        'attributes': self.attributes,
        'name': self.name,
        'id': self.id,
        'classes': self.classes,
        'placeholder': self.placeholder,
        'selector': self.selector,
        'xpath': self.xpath,
        'selector_cost': self.selector_cost,
        'strategy_used': self.strategy_used,
        'visible': self.visible,
        'enabled': self.enabled,
        'disabled': self.disabled,
        'in_shadow': self.in_shadow,
        'shadow_host': self.shadow_host,
        'shadow_path': self.shadow_path,
        'scanned_at': self.scanned_at.isoformat(),
        'page_url': self.page_url,
    }

@classmethod
def from_dict(cls, data: dict) -> 'Element':
    """
    从字典反序列化

    处理:
    1. 移除locator/handle（如果存在）
    2. 转换ISO字符串 → datetime
    """

    # 移除内存对象
    data.pop('locator', None)
    data.pop('handle', None)

    # 转换datetime
    if 'scanned_at' in data and isinstance(data['scanned_at'], str):
        data['scanned_at'] = datetime.fromisoformat(data['scanned_at'])

    return cls(**data)
```

### 3.2 ElementCollection

**文件**: `src/selector_cli/core/collection.py`
**代码行数**: 160行
**设计模式**: 组合模式（Composite Pattern）

#### 3.2.1 内部数据结构

```python
class ElementCollection:
    """元素集合，支持过滤和集合操作"""

    def __init__(self, name: Optional[str] = None):
        self.elements: List[Element] = []     # 元素列表（有序）
        self._index: Dict[int, Element] = {}  # 索引映射（O(1)查找）
        self.name = name                      # 集合名（用于识别）
        self.created_at = datetime.now()
        self.modified_at = datetime.now()
```

**设计权衡**：
- 使用两个数据结构：
  - `elements: List` - 保持插入顺序
  - `_index: Dict` - 提供O(1)索引查找
- 空间换时间：牺牲少量内存换取快速查找

#### 3.2.2 添加/删除操作

```python
def add(self, element: Element) -> None:
    """
    添加元素到集合

    复杂度分析:
    - List.append(): O(1)
    - Dict赋值: O(1)
    - 总体: O(1)

    去重检查:
    - 通过element.index保证唯一性
    - 不检查UUID（信任scanner唯一）
    """

    if element.index not in self._index:
        self.elements.append(element)
        self._index[element.index] = element
        self.modified_at = datetime.now()

def remove(self, element: Element) -> None:
    """
    从集合移除元素

    复杂度分析:
    - List.remove(): O(n)（需要搜索）
    - Dict删除: O(1)
    - 总体: O(n)
    """

    if element.index in self._index:
        self.elements.remove(element)  # O(n) 需要遍历
        del self._index[element.index]
        self.modified_at = datetime.now()
```

#### 3.2.3 过滤操作

```python
def filter(self, condition: Callable[[Element], bool]) -> 'ElementCollection':
    """
    按条件过滤，返回新集合

    参数:
    - condition: Element → bool 的函数

    示例:
    - filter(lambda e: e.tag == 'input')
    - filter(lambda e: e.selector_cost < 0.2)

    复杂度: O(n)，n为元素数量
    """

    result = ElementCollection(name=f"{self.name}_filtered" if self.name else None)

    for elem in self.elements:
        if condition(elem):
            result.add(elem)

    return result
```

#### 3.2.4 集合操作

```python
def union(self, other: 'ElementCollection') -> 'ElementCollection':
    """
    并集操作: A ∪ B

    复杂度:
    - O(n + m)，其中n=len(A), m=len(B)
    - 因为需要遍历两个集合
    """

    result = ElementCollection()

    # 添加所有A
    for elem in self.elements:
        result.add(elem)

    # 添加不在A中的B
    for elem in other.elements:
        if elem.index not in result._index:
            result.add(elem)

    return result

def intersection(self, other: 'ElementCollection') -> 'ElementCollection':
    """
    交集操作: A ∩ B

    复杂度: O(n)，n=len(A)
    - 对每个A元素检查是否在B中存在
    - Dict查找: O(1)
    """

    result = ElementCollection()

    for elem in self.elements:
        if elem.index in other._index:
            result.add(elem)

    return result

def difference(self, other: 'ElementCollection') -> 'ElementCollection':
    """
    差集操作: A - B

    复杂度: O(n)，n=len(A)
    - 对每个A元素检查是否在B中
    - 不在B中 → 添加到结果
    """

    result = ElementCollection()

    for elem in self.elements:
        if elem.index not in other._index:
            result.add(elem)

    return result
```

#### 3.2.5 原地操作（In-Place Operations）

```python
def union_in_place(self, other: 'ElementCollection') -> None:
    """
    原地并集: A += B

    优势:
    - 避免创建新集合（节省内存）
    - 保持对象引用不变

    注意:
    - 修改当前对象
    - 不创建副本
    """

    for elem in other.elements:
        self.add(elem)

    self.modified_at = datetime.now()
def intersect_in_place(self, other: 'ElementCollection') -> None:
    """原地交集: A ∩= B"""

    to_remove = []
    for elem in self.elements:
        if elem.index not in other._index:
            to_remove.append(elem)

    for elem in to_remove:
        self.remove(elem)

def difference_in_place(self, other: 'ElementCollection') -> None:
    """原地差集: A -= B"""

    to_remove = []
    for elem in self.elements:
        if elem.index in other._index:
            to_remove.append(elem)

    for elem in to_remove:
        self.remove(elem)
```

#### 3.2.6 序列化支持

```python
def to_dict(self) -> dict:
    """
    序列化为字典（用于JSON持久化）

    格式:
    {
        "name": "workspace",
        "created_at": "2025-11-22T10:30:00",
        "modified_at": "2025-11-22T11:00:00",
        "elements": [Element.to_dict(), ...]
    }
    """

    return {
        'name': self.name,
        'created_at': self.created_at.isoformat(),
        'modified_at': self.modified_at.isoformat(),
        'elements': [elem.to_dict() for elem in self.elements]
    }

@classmethod
def from_dict(cls, data: dict) -> 'ElementCollection':
    """从字典反序列化"""

    collection = cls(name=data.get('name'))
    collection.created_at = datetime.fromisoformat(data['created_at'])
    collection.modified_at = datetime.fromisoformat(data['modified_at'])

    for elem_data in data.get('elements', []):
        elem = Element.from_dict(elem_data)
        collection.add(elem)

    return collection
```

### 3.3 ElementScanner

**文件**: `src/selector_cli/core/scanner.py`
**代码行数**: 307行
**核心职责**: 扫描网页并构建Element对象

#### 3.3.1 主扫描流程

```python
async def scan(
    self,
    page: Page,
    element_types: List[str] = None,
    deep: bool = False
) -> List[Element]:
    """
    扫描页面并返回元素列表

    性能目标: < 10ms/元素（实际5ms）

    流程:
    1. 确定要扫描的元素类型
    2. 对每个类型，查询Playwright locator
    3. 对每个locator，构建Element对象
    4. 集成LocationStrategyEngine生成最优selector

    参数:
    - page: Playwright Page对象
    - element_types: 要扫描的类型列表（默认['input', 'button', 'a', 'select', 'textarea']）
    - deep: 是否深度扫描（扫描嵌套元素）

    返回:
    - List[Element] - 扫描到的元素
    """

    if element_types is None:
        element_types = self.DEFAULT_ELEMENT_TYPES

    elements = []
    index = 0

    for elem_type in element_types:
        # Playwright查询（批量）
        locators = await page.locator(elem_type).all()
        # 注意：locator.all() 返回的是轻量级引用，不是实际元素
        # 实际属性获取会在_build_element中逐个调用

        for locator in locators:
            # 逐个构建Element（这一步会触发异步IO）
            element = await self._build_element(
                locator, index, elem_type, page.url, page
            )
            elements.append(element)
            index += 1

    return elements
```

#### 3.3.2 构建Element对象

```python
async def _build_element(
    self,
    locator: Locator,
    index: int,
    elem_type: str,
    page_url: str,
    page: Page
) -> Element:
    """
    从Playwright locator构建Element对象

    关键挑战:
    - 每个属性获取都是异步IO → 累积延迟
    - 解决方案: 批量获取，避免不必要的等待

    获取的属性优先级:
    1. text, type, name, id, class → 基础识别
    2. placeholder, value, href → 辅助信息
    3. aria-label, title, data-testid, role → 策略专用
    4. visible, enabled, disabled → 状态信息
    """

    # 1. 基础属性（并行获取）
    text = await locator.inner_text() if await locator.count() > 0 else ""

    # 2. 关键属性（批量获取）
    attributes = {}
    for attr in ['type', 'name', 'id', 'class', 'placeholder', 'value',
                 'href', 'disabled', 'aria-label', 'title', 'data-testid', 'role']:
        try:
            attr_value = await locator.get_attribute(attr)
            if attr_value is not None:
                attributes[attr] = attr_value
        except Exception:
            # 如果元素已经消失，返回空
            pass

    # 3. 计算属性
    elem_id = attributes.get('id', '')
    name = attributes.get('name', '')
    placeholder = attributes.get('placeholder', '')
    classes = attributes.get('class', '').split()

    # 4. 创建临时Element（用于StrategyEngine）
    temp_element = Element(
        index=index,
        uuid=str(uuid.uuid4()),
        tag=elem_type,
        type=attributes.get('type', ''),
        text=text.strip()[:100],
        value=attributes.get('value', ''),
        attributes=attributes,
        name=name,
        id=elem_id,
        classes=classes,
        placeholder=placeholder,
        selector='',  # 待生成
        xpath='',     # 待生成
    )

    # 5. 使用LocationStrategyEngine生成最优selector
    strategy_engine = LocationStrategyEngine()
    locator_result = await strategy_engine.find_best_locator(temp_element, page)

    # 6. 提取selector和成本
    if locator_result and locator_result.is_unique:
        selector = locator_result.selector
        cost = locator_result.cost
        strategy_used = locator_result.strategy
    else:
        # 策略失败或返回非唯一selector → 回退到基础selector
        selector = await self._build_unique_selector(elem_type, attributes, text, page)
        cost = None
        strategy_used = None

    # 7. 构建XPath（备用）
    xpath = await self._build_xpath(locator)

    # 8. 获取状态
    try:
        visible = await locator.is_visible() if await locator.count() > 0 else False
        enabled = await locator.is_enabled() if await locator.count() > 0 else True
        disabled = attributes.get('disabled') is not None
    except Exception:
        visible = True
        enabled = True
        disabled = False

    # 9. 返回完整Element
    return Element(
        index=index,
        uuid=str(uuid.uuid4()),  # 生成新UUID（避免冲突）
        tag=elem_type,
        type=attributes.get('type', ''),
        text=text.strip()[:100],
        value=attributes.get('value', ''),
        attributes=attributes,
        name=name,
        id=elem_id,
        classes=classes,
        placeholder=placeholder,
        selector=selector,
        xpath=xpath,
        selector_cost=cost,
        strategy_used=strategy_used,
        visible=visible,
        enabled=enabled,
        disabled=disabled,
        locator=locator,
        page_url=page_url
    )
```

#### 3.3.3 构建唯一选择器（备选方案）

```python
async def _build_unique_selector(
    self,
    tag: str,
    attributes: dict,
    text: str,
    page: Page
) -> str:
    """
    尝试构建唯一的CSS选择器（策略引擎失败时使用）

    策略（优先级从高到低）:
    1. ID选择器（最可靠）
       → #element-id
       → 验证唯一性

    2. 唯一属性组合
       → input[type="email"][name="login"]
       → button[type="submit"].primary

    3. 文本内容（按钮/链接）
       → button:has-text("Submit")

    4. 回退（不保证唯一）
       → input[type="email"]
       → button
    """

    # 策略1: ID
    if 'id' in attributes and attributes['id']:
        selector = f"#{attributes['id']}"
        if await self._is_unique_selector(page, selector):
            return selector

        # 带tag的ID
        selector = f"{tag}#{attributes['id']}"
        if await self._is_unique_selector(page, selector):
            return selector

    # 策略2: 唯一属性组合
    selectors_to_try = []
    base = tag

    # type + name
    if 'type' in attributes and attributes['type']:
        type_sel = f'{base}[type="{attributes["type"]}"]'
        if 'name' in attributes and attributes['name']:
            selectors_to_try.append(
                f'{type_sel}[name="{attributes["name"]}"]'
            )

    # name alone
    if 'name' in attributes and attributes['name']:
        selectors_to_try.append(f'{base}[name="{attributes["name"]}"]')

    # placeholder
    if 'placeholder' in attributes and attributes['placeholder']:
        placeholder = attributes['placeholder'][:30]
        selectors_to_try.append(f'{base}[placeholder="{placeholder}"]')

    # href for links
    if 'href' in attributes and attributes['href']:
        href = attributes['href'][:50]
        selectors_to_try.append(f'{base}[href="{href}"]')

    # 尝试每个selector（验证唯一性）
    for selector in selectors_to_try:
        if await self._is_unique_selector(page, selector):
            return selector

    # 策略3: 文本内容（按钮和链接）
    if text and tag in ['button', 'a']:
        escaped_text = text[:30].replace('"', '\\"')
        selector = f'{tag}:has-text("{escaped_text}")'
        if await self._is_unique_selector(page, selector):
            return selector

    # 策略4: 回退（基础selector）
    if 'type' in attributes and attributes['type']:
        return f'{base}[type="{attributes["type"]}"]'
    elif 'name' in attributes and attributes['name']:
        return f'{base}[name="{attributes["name"]}"]'

    return tag  # 最基础的选择器
```

#### 3.3.4 验证选择器唯一性

```python
async def _is_unique_selector(self, page: Page, selector: str) -> bool:
    """
    验证选择器是否唯一匹配（优化技巧：避免生成非唯一selector）

    实现:
    - 使用page.locator(selector).count()
    - count() == 1 → 唯一
    - count() > 1 → 不唯一

    性能:
    - count() 返回Promise → 异步
    - 平均时间: ~2-5ms

    使用场景:
    1. _build_unique_selector中验证
    2. LocationStrategyEngine验证最优selector
    """

    try:
        count = await page.locator(selector).count()
        return count == 1
    except Exception:
        # locator无效或页面问题
        return False
```

#### 3.3.5 构建XPath（JavaScript）

```python
async def _build_xpath(self, locator: Locator) -> str:
    """
    使用JavaScript在浏览器中构建XPath

    策略:
    - 如果有id: //*[@id="value"]
    - 否则: 递归构建路径
      /html/body/div[1]/form/input[2]

    优点:
    - 在浏览器中执行（有完整DOM访问）
    - 准确（考虑动态内容）

    缺点:
    - 需要定位器仍然有效
    - 异步（需要await）
    """

    try:
        xpath = await locator.evaluate("""
            (element) => {
                function getXPath(node) {
                    // ID优化
                    if (node.id) {
                        return `//*[@id="${node.id}"]`;
                    }

                    // 根节点
                    if (node === document.body) {
                        return '/html/body';
                    }

                    // 计算同类型兄弟节点的索引
                    let ix = 0;
                    const siblings = node.parentNode ? node.parentNode.childNodes : [];

                    for (let i = 0; i < siblings.length; i++) {
                        const sibling = siblings[i];

                        if (sibling === node) {
                            const tagName = node.tagName.toLowerCase();
                            return getXPath(node.parentNode)
                                 + '/' + tagName + '[' + (ix + 1) + ']';
                        }

                        if (sibling.nodeType === 1 && sibling.tagName === node.tagName) {
                            ix++;
                        }
                    }
                }

                return getXPath(element);
            }
        """)

        return xpath if xpath else ""
    except Exception:
        return ""
```

---

## 4. v2执行上下文（ContextV2）

### 4.1 三层状态管理

**文件**: `src/selector_cli_v2/v2/context.py`
**代码行数**: 13,206行
**设计模式**: 状态模式（State Pattern）

#### 4.1.1 三层设计

```python
class ContextV2:
    """v2执行上下文，管理三层状态"""

    # Temp层TTL（30秒）
    TEMP_TTL = 30

    def __init__(self, enable_history_file: bool = True):
        # =========================================
        # 三层元素存储
        # =========================================
        self._candidates: List[Element] = []    # SCAN结果（只读）
        self._temp: List[Element] = []          # FIND临时结果（30秒过期）
        self._workspace: ElementCollection = ElementCollection(name="workspace")

        # =========================================
        # 状态追踪
        # =========================================
        self._focus: str = 'candidates'  # 当前聚焦层
        self._last_find_time: Optional[datetime] = None  # 用于TTL

        # =========================================
        # 浏览器状态
        # =========================================
        self.browser: Optional[BrowserManager] = None
        self.current_url: Optional[str] = None
        self.is_page_loaded: bool = False

        # =========================================
        # 持久化数据
        # =========================================
        self.variables: Dict[str, Any] = {}  # 用户变量
        self.history: List[str] = []         # 命令历史
```

#### 4.1.2 三层访问控制

```python
@property
def candidates(self) -> List[Element]:
    """获取candidates（只读）"""
    return self._candidates.copy()  # 返回副本，防止外部修改

@candidates.setter
def candidates(self, elements: List[Element]):
    """设置candidates（仅由scan命令调用）"""
    self._candidates = elements
    self.last_scan_time = datetime.now()

@property
def temp(self) -> List[Element]:
    """获取temp（自动检查过期）"""
    if self._is_temp_expired():
        return []
    return self._temp.copy()

@temp.setter
def temp(self, elements: List[Element]):
    """设置temp（触发TTL计时）"""
    self._temp = elements
    self._last_find_time = datetime.now()

def clear_temp(self) -> None:
    """清空temp层"""
    self._temp.clear()
    self._last_find_time = None
    self._focus = 'candidates'  # Reset focus

def _is_temp_expired(self) -> bool:
    """检查temp是否过期"""
    if self._last_find_time is None:
        return True

    age = datetime.now() - self._last_find_time
    return age.total_seconds() > self.TEMP_TTL  # 30秒
```

#### 4.1.3 Focus管理

```python
@property
def focus(self) -> str:
    """获取当前聚焦层"""
    return self._focus

@focus.setter
def focus(self, value: str):
    """设置focus（只允许candidates/temp/workspace）"""
    if value in ['candidates', 'temp', 'workspace']:
        self._focus = value
    else:
        raise ValueError(f"Invalid focus: {value}")

def get_focused_elements(self) -> List[Element]:
    """获取当前focus层的元素"""
    if self._focus == 'candidates':
        return self.candidates
    elif self._focus == 'temp':
        return self.temp
    elif self._focus == 'workspace':
        return self.workspace.get_all()
    return []
```

#### 4.1.4 元素查找（安全访问）

```python
def get_element_by_index(
    self,
    index: int,
    layer: str = 'candidates'
) -> Optional[Element]:
    """
    按索引从指定层获取元素

    参数:
    - index: 元素索引
    - layer: 层名 (candidates/temp/workspace)

    实现:
    - temp层: 使用copy()防止过期问题
    - workspace: 使用index映射O(1)

    复杂度:
    - candidates/temp: O(n)
    - workspace: O(1)（通过_dict索引）
    """

    if layer == 'candidates':
        for elem in self._candidates:
            if elem.index == index:
                return elem

    elif layer == 'temp':
        for elem in self.temp:  # 使用property（检查过期）
            if elem.index == index:
                return elem

    elif layer == 'workspace':
        return self._workspace.get(index)  # O(1)

    return None
```

#### 4.1.5 命令历史管理

```python
def add_to_history(self, command: str) -> None:
    """添加命令到历史（自动持久化）"""
    self.history.append(command)
    if self.enable_history_file:
        self._save_history()

def _save_history(self):
    """持久化历史到文件"""
    try:
        self.HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)

        # 限制大小（最近 MAX_HISTORY_SIZE 条）
        history_to_save = self.history[-self.MAX_HISTORY_SIZE:]

        with open(self.HISTORY_FILE, 'w', encoding='utf-8') as f:
            for cmd in history_to_save:
                f.write(cmd + '\n')
    except Exception:
        pass  # 静默失败（历史记录非关键）
```

#### 4.1.6 变量管理（自动持久化）

```python
def set_variable(self, name: str, value: Any) -> bool:
    """
    设置变量（自动保存到文件）

    持久化路径:
    ~/.selector-cli/vars.json

    格式:
    {
      "homepage": "https://example.com",
      "username": "test@example.com",
      "timeout": 30
    }
    """

    try:
        self.variables[name] = value
        self._save_variables()
        return True
    except Exception:
        return False

def _save_variables(self):
    """持久化变量到JSON"""

    if not self.enable_history_file:
        return

    try:
        import json
        self.VARS_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(self.VARS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.variables, f, indent=2, ensure_ascii=False)
    except Exception:
        pass
```

---

## 5. 性能与复杂度分析

### 5.1 时间复杂度

| 操作 | 实现 | 复杂度 | 说明 |
|------|------|--------|------|
| **Element添加** | List.append + Dict赋值 | O(1) | 平均O(1)，扩容时O(n) |
| **Element删除** | List.remove + Dict删除 | O(n) | List.remove需要搜索 |
| **按索引查找** | Dict映射 | O(1) | ElementCollection._index |
| **按索引查找(candidates/temp)** | 线性遍历 | O(n) | 需要遍历列表 |
| **过滤(filter)** | 遍历 + 函数调用 | O(n × f) | f为condition求值时间 |
| **集合交集** | 遍历 + Dict查找 | O(n) | 使用O(1)查找 |
| **集合并集** | 两个遍历 | O(n + m) | 需要检查重复 |
| **扫描元素** | 每元素 ~10次异步IO | O(n × t) | t~5ms/element |
| **条件求值** | 递归树遍历 | O(d × e) | d=树深度, e=元素数 |

### 5.2 空间复杂度

| 数据结构 | 实现 | 空间复杂度 | 说明 |
|----------|------|------------|------|
| **Element** | 30+字段 | O(1) | 固定大小 |
| **ElementCollection** | List + Dict | O(n) | 2倍存储（2n） |
| **ContextV2** | 三层 + 元数据 | O(n) | candidates + temp + workspace |
| **条件树** | Node递归 | O(d) | d=树深度 |

### 5.3 核心性能数据

实测性能（基于README.md基准测试）：

```
操作            平均耗时    目标        倍数
------------------------------------------------
Lexer Tokenization  0.1ms/Token   <0.5ms    5x
Parser解析     1ms/命令     <5ms      5x
Element扫描     5ms/元素     <10ms     2x
selector生成    3ms/元素     N/A       -
条件过滤(100)   2ms         <50ms     25x
集合操作(1000)  5ms         <100ms    20x
批量添加(100)    1ms         <10ms     10x
```

### 5.4 缓存策略

**1. Temp层缓存（30秒TTL）**
```python
# ContextV2.temp 使用property + 过期检查
@property
def temp(self) -> List[Element]:
    if self._is_temp_expired():
        return []  # 过期返回空
    return self._temp.copy()
```

**2. LocationStrategyEngine验证缓存**
```python
class LocationStrategyEngine:
    def __init__(self):
        self._cache = {}  # selector → validation_result
```

**3. ElementCollection索引缓存**
```python
class ElementCollection:
    def __init__(self):
        self.elements: List[Element] = []
        self._index: Dict[int, Element] = {}  # 缓存索引
```

---

## 6. 核心设计模式应用

### 6.1 策略模式（Strategy Pattern）

**应用在**: LocationStrategyEngine + 17种策略

```python
class LocationStrategyEngine:
    def __init__(self):
        self.css_strategies = self._load_css_strategies()
        self.xpath_strategies = self._load_xpath_strategies()

def find_best_locator(self, element: Element, page: Page) -> LocationResult:
    """遍历所有策略，选择成本最低的"""

    best_result = None
    min_cost = float('inf')

    for strategy in self.css_strategies:
        if self._can_apply(strategy, element):
            result = await self._execute_strategy(strategy, element, page)

            if result.is_unique and result.cost < min_cost:
                best_result = result
                min_cost = result.cost

    return best_result
```

### 6.2 工厂模式（Factory Pattern）

**应用在**: GeneratorFactory（代码生成器）

```python
def create_generator(format: str) -> CodeGenerator:
    generators = {
        'playwright': PlaywrightGenerator,
        'selenium': SeleniumGenerator,
        'puppeteer': PuppeteerGenerator,
        'json': JsonExporter,
        'csv': CsvExporter,
    }

    return generators[format]()
```

### 6.3 观察者模式（Observer Pattern）

**应用在**: 变量持久化（自动保存）

```python
def set_variable(self, name: str, value: Any) -> bool:
    self.variables[name] = value
    self._save_variables()  # 观察点：任何修改触发保存
    return True
```

### 6.4 状态模式（State Pattern）

**应用在**: ContextV2的focus管理

```python
@property
def focus(self) -> str:  # 当前状态
    return self._focus

@focus.setter
def focus(self, value: str):  # 状态转换
    if value in ['candidates', 'temp', 'workspace']:
        self._focus = value
```

### 6.5 模板方法模式（Template Method）

**应用在**: CodeGenerator基类

```python
class CodeGenerator:
    def generate_code(self, elements: List[Element], options: dict) -> str:
        """模板方法"""
        header = self._generate_header()
        imports = self._generate_imports()
        element_selectors = self._generate_selectors(elements)
        actions = self._generate_actions(elements)
        footer = self._generate_footer()

        return f"{header}\n{imports}\n{element_selectors}\n{actions}\n{footer}"

    def _generate_header(self) -> str:  # 可被子类覆盖
        return "# Generated by Selector CLI\n"
```

---

## 7. 错误处理与健壮性

### 7.1 解析错误处理

```python
try:
    command = parser.parse(line)
except ValueError as e:
    print(f"Parse error: {e}")
    continue
except Exception as e:
    if debug:
        import traceback
        traceback.print_exc()
    continue
```

### 7.2 执行错误处理

```python
try:
    success, result = await executor.execute(command)
    if success:
        if result:
            print(result)
    else:
        print(f"Execution error: {result}")
except Exception as e:
    print(f"Unexpected error: {e}")
    if debug:
        traceback.print_exc()
```

### 7.3 浏览器错误处理

```python
try:
    await self.browser.initialize()
except Exception as e:
    print(f"Failed to initialize browser: {e}")
    print("Continuing without browser...")
    self.browser = None
```

### 7.4 元素获取错误

```python
# 惰性获取（按需尝试）
try:
    attr_value = await locator.get_attribute(attr)
except Exception:
    attr_value = None  # 元素已消失

# 计数检查（避免对无效元素操作）
if await locator.count() > 0:
    text = await locator.inner_text()
else:
    text = ""
```

### 7.5 持久化错误（静默失败）

```python
try:
    self._save_history()
except Exception:
    pass  # 历史记录非关键，静默失败

try:
    self._save_variables()
except Exception:
    pass  # 变量非关键，静默失败
```

### 7.6 Temp过期错误

```python
@property
def temp(self) -> List[Element]:
    """过期的temp自动返回空列表"""
    if self._is_temp_expired():
        return []  # 已过期，返回空
    return self._temp.copy()
```

---

**文档索引**: 📂 [第一部分：系统架构分析] | [第二部分：核心模块详细分析] | [第三部分：算法与数据流分析]

**当前进度**: [●●●●● 100%]

**下一部分**: 详细剖析Element Location Strategy系统（17种策略 + 4维成本模型 + 3级验证）

**文档状态**: ✅ 完成
**行长**: ~800行
**覆盖模块**: Lexer/Parser/Executor/Element/Collection/Scanner/ContextV2
**包含**: 算法分析 + 复杂度计算 + 设计模式
