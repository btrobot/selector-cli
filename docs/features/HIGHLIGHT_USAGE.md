# Highlight 命令使用指南

`highlight` 命令用于在浏览器中高亮显示元素，方便您可视化选择结果。

## 基本用法

### 1. 高亮当前集合中的所有元素
```bash
# 先添加一些元素到集合
selector> add input
Added 5 element(s) to collection. Total: 5

# 高亮集合中的所有元素
selector> highlight
Highlighted 5 element(s) from collection
```

### 2. 高亮特定类型的元素
```bash
# 高亮所有按钮（不添加到集合）
selector> highlight button
Highlighted 3 element(s)

# 高亮所有输入框
selector> highlight input
Highlighted 5 element(s)

# 高亮所有元素
selector> highlight all
Highlighted 15 element(s)
```

### 3. 高亮特定索引的元素
```bash
# 高亮第0个元素
selector> highlight [0]
Highlighted 1 element(s)

# 高亮多个元素（索引 1, 3, 5）
selector> highlight [1,3,5]
Highlighted 3 element(s)

# 高亮一个范围的元素（索引 0-4）
selector> highlight [0-4]
Highlighted 5 element(s)
```

### 4. 使用条件高亮
```bash
# 高亮特定类型的输入框
selector> highlight input where type="email"
Highlighted 1 element(s)

# 高亮可见的按钮
selector> highlight button where visible
Highlighted 2 element(s)

# 高亮包含特定文本的按钮
selector> highlight button where text contains "Submit"
Highlighted 1 element(s)
```

### 5. 使用复杂条件高亮
```bash
# 使用 AND 逻辑
selector> highlight input where type="text" and visible
Highlighted 3 element(s)

# 使用 OR 逻辑
selector> highlight button where type="submit" or type="button"
Highlighted 4 element(s)

# 使用 NOT 逻辑
selector> highlight input where not disabled
Highlighted 4 element(s)

# 组合使用
selector> highlight button where (type="submit" or type="button") and not disabled
Highlighted 3 element(s)
```

## 取消高亮

```bash
# 移除所有高亮
selector> unhighlight
Removed highlights from 5 element(s)
```

## 常见使用场景

### 场景1：验证选择器是否正确
```bash
# 1. 添加元素到集合
selector> add input where type="email"
Added 1 element(s) to collection. Total: 1

# 2. 高亮以验证选择的是否正确
selector> highlight
Highlighted 1 element(s) from collection

# 3. 如果不对，清除并重新选择
selector> unhighlight
selector> clear
```

### 场景2：快速查看页面中的特定元素
```bash
# 快速查看所有按钮的位置
selector> highlight button
Highlighted 5 element(s)

# 查看完后取消高亮
selector> unhighlight
```

### 场景3：调试复杂条件
```bash
# 调试一个复杂的 WHERE 条件
selector> highlight input where (type="text" or type="email") and visible and not disabled
Highlighted 2 element(s)

# 如果结果不对，调整条件后重新尝试
selector> unhighlight
selector> highlight input where type="text" and visible
Highlighted 3 element(s)
```

## 注意事项

1. **highlight 不会修改集合**：`highlight` 命令只是可视化显示元素，不会修改当前集合。
   ```bash
   selector[5]> highlight button
   Highlighted 3 element(s)
   selector[5]>  # 集合还是5个元素
   ```

2. **highlight vs add**：
   - `add` - 添加元素到集合（持久化）
   - `highlight` - 只是临时高亮显示

   ```bash
   # add 会修改集合
   selector[0]> add input
   selector[5]>  # 集合有5个元素了

   # highlight 不会修改集合
   selector[5]> highlight button
   selector[5]>  # 集合还是5个元素
   ```

3. **需要先加载页面**：使用 highlight 之前必须先用 `open` 命令加载网页。
   ```bash
   selector> open https://example.com
   selector> scan
   selector> highlight input  # 现在可以高亮了
   ```

4. **unhighlight 会移除所有高亮**：不能选择性地移除某些高亮，只能全部移除。

## 您遇到的错误

您执行的命令：
```bash
selector(www.verdent.ai)[5]> highlight [0]
```

这个命令是**正确的**！错误是因为代码中有个 bug（我刚刚已经修复了）。现在这个命令应该可以正常工作：

- `highlight [0]` - 高亮第0个元素（在 all_elements 中的第0个）

## 完整工作流示例

```bash
# 1. 打开网页
selector> open https://www.verdent.ai
Opened: https://www.verdent.ai
Auto-scanned 15 elements

# 2. 高亮所有输入框查看位置
selector> highlight input
Highlighted 5 element(s)

# 3. 查看完后取消高亮
selector> unhighlight
Removed highlights from 5 element(s)

# 4. 添加需要的输入框到集合
selector> add input where type="email"
Added 1 element(s) to collection. Total: 1

# 5. 高亮集合验证
selector> highlight
Highlighted 1 element(s) from collection

# 6. 继续添加其他元素
selector> add button where type="submit"
Added 1 element(s) to collection. Total: 2

# 7. 再次高亮集合查看
selector> highlight
Highlighted 2 element(s) from collection
```

## 技术细节

高亮是通过在元素上注入 CSS 样式实现的：
- 边框：3px 红色实线
- 背景：半透明红色 (10% 不透明度)
- 样式在页面刷新后会消失
- 使用 `unhighlight` 可以手动移除样式
