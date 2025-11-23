# Selector CLI - 常见问题 (FAQ)

**版本**: v1.0
**更新日期**: 2025-11-23

---

## 安装和运行

### Q1: 如何安装 Selector CLI？

**A**: 使用 pip 安装（发布到 PyPI 后）：
```bash
pip install selector-cli
selector
```

### Q2: 运行时报错 "playwright not found"

**A**: 需要安装 Playwright 浏览器驱动：
```bash
playwright install chromium
```

### Q3: 支持哪些操作系统？

**A**: 支持 Windows、macOS 和 Linux。需要 Python 3.8+ 和 Playwright。

---

## 基本使用

### Q4: 如何退出 Selector CLI？

**A**: 使用以下任一命令：
```bash
selector> quit
selector> exit
selector> q
```

### Q5: 如何清除屏幕？

**A**: 使用 `clear` 命令：
```bash
selector> clear
```

### Q6: 如何查看所有可用命令？

**A**: 使用 `help` 命令或 Tab 键补全：
```bash
selector> help
```

---

## 元素扫描和选择

### Q7: 为什么有些元素扫描不到？

**A**: 可能原因：
1. 元素在 iframe 中 - 需要切换到 iframe 上下文
2. 元素在 Shadow DOM 中 - 使用 `scan --deep`（待实现）
3. 元素是动态生成的 - 等待页面加载完成再扫描
4. 元素类型不在默认扫描列表中

**解决**: 明确指定元素类型：
```bash
selector> scan input button select textarea a
```

### Q8: 如何选择特定元素？

**A**: 多种方式：
```bash
# 按索引
selector> add [0]           # 单个
selector> add [1,2,3]       # 多个
selector> add [1-5]         # 范围（待实现）

# 按类型
selector> add input
selector> add button

# 按条件
selector> add input where type="email"
selector> add button where text contains "Submit"
```

### Q9: 什么是 "selector_cost"？

**A**: 成本是 Selector CLI 评估选择器质量的指标：**值越低，选择器越稳定可靠**。

**成本范围**：
- 0.04-0.10: 优秀 (ID、data-testid)
- 0.10-0.25: 良好 (CSS 属性组合)
- 0.25-0.40: 一般 (class、文本)
- 0.40+: 较差 (XPath position)

**示例**：
```bash
selector> list where selector_cost < 0.2   # 只显示高质量选择器
```

### Q10: 如何知道使用了哪种选择器策略？

**A**: 查看 `strategy_used` 字段：
```bash
selector> list
[0] input#email (cost: 0.044, strategy: ID_SELECTOR)
[1] input[type="text"] (cost: 0.165, strategy: TYPE_NAME)
```

常见策略：
- `ID_SELECTOR` - ID 选择器（最佳）
- `DATA_TESTID` - data-testid 属性
- `TYPE_NAME` - type + name 组合
- `CLASS_UNIQUE` - 唯一 class
- `XPATH_ID` - XPath ID
- `XPATH_POSITION` - XPath 位置（避免）

---

## 代码导出

### Q11: 支持哪些导出格式？

**A**: 6 种格式：
- **Python**: Playwright, Selenium
- **JavaScript**: Puppeteer
- **数据**: JSON, CSV, YAML

### Q12: 如何将代码保存到文件？

**A**: 使用重定向操作符 `>`：
```bash
selector> export playwright > test.py
```

### Q13: 导出的代码需要修改吗？

**A**: 通常不需要，代码可以直接运行。Selector CLI 生成的选择器已经过优化和验证。

如果需要填写表单：
```python
# 添加交互代码
email.fill('your-email@example.com')
password.fill('your-password')
submit.click()
```

---

## 宏系统

### Q14: 什么是宏？

**A**: 宏是一组命令的集合，可以重复执行。支持参数化。

### Q15: 如何创建带参数的宏？

**A**: 使用大括号定义参数：
```bash
selector> macro login-form {url} {username} {
  open {url}
  add input where type="email" or type="text"
  add input where type="password"
  list
}

selector> run login-form https://github.com/login user123
```

### Q16: 宏参数数量不匹配怎么办？

**A**: 会报错。确保提供正确数量的参数：
```bash
# 宏定义: macro test {p1} {p2} command
# 正确: run test arg1 arg2
# 错误: run test arg1      # 缺少参数
```

### Q17: 如何查看所有宏？

**A**: 使用 `macros` 命令：
```bash
selector> macros
```

---

## 脚本执行

### Q18: 如何执行脚本文件？

**A**: 使用 `exec` 命令：
```bash
selector> exec test.sel
```

### Q19: 脚本文件格式是什么？

**A**: `.sel` 文件，包含 Selector CLI 命令，支持注释：
```bash
# 这是注释
open https://example.com
scan
add input
export playwright
```

### Q20: 脚本执行出错怎么办？

**A**: 会显示错误行号。检查：
1. 命令语法是否正确
2. 页面是否加载完成
3. 元素是否存在

---

## 变量系统

### Q21: 变量保存在哪里？

**A**: 保存在 `~/.selector-cli/vars.json`，重启后仍然有效。

### Q22: 变量支持哪些类型？

**A**: 支持字符串、数字，保存在 JSON 中。

### Q23: 如何在命令中使用变量？

**A**: 使用 `$` 前缀：
```bash
selector> set homepage = https://example.com
selector> open $homepage
```

---

## 集合持久化

### Q24: 集合保存在哪里？

**A**: 保存在 `~/.selector-cli/collections/` 目录，每个集合一个 JSON 文件。

### Q25: 集合可以跨会话使用吗？

**A**: 可以。使用 `save` 保存，之后使用 `load` 加载：
```bash
selector> save my_form
# ... 之后 ...
selector> load my_form
```

---

## 性能问题

### Q26: 扫描大量元素很慢怎么办？

**A**: 优化建议：
1. 只扫描需要的类型：`scan input button` 而非 `scan`
2. 提高扫描间隔（如果需要多次扫描）
3. 使用 `keep/filter` 减少集合大小

扫描性能：平均 5ms/元素，支持 200元素/秒。

### Q27: 如何减少内存使用？

**A**: 建议：
1. 使用 `clear` 清空不需要的集合
2. 只保留需要的元素类型
3. 定期删除旧的保存集合

---

## 高级问题

### Q28: 如何选择稳定的选择器？

**A**: 使用成本过滤：
```bash
selector> keep where selector_cost < 0.2
```

优先选择：
1. ID 选择器（成本 ~0.044）
2. data-testid（成本 ~0.044）
3. type+name 组合（成本 ~0.165）

避免：
- XPath position（成本 ~0.570）
- 长 class 链

### Q29: 如何处理动态页面？

**A**: 对于单页应用(SPA)：
1. 等待页面加载完成（使用高亮检查元素是否出现）
2. 重新扫描：`scan`
3. 使用成本过滤选择稳定的选择器

### Q30: 支持 Shadow DOM 吗？

**A**: 当前版本基础支持已存在，正在完善 `scan --deep` 命令。

---

## 故障排除

### Q31: 如何重置所有数据？

**A**: 删除配置目录：
```bash
# Windows
rmdir /s /q %USERPROFILE%\.selector-cli

# macOS/Linux
rm -rf ~/.selector-cli
```

### Q32: 日志和调试信息在哪里？

**A**: 当前版本在控制台输出 INFO 级别日志。可以使用：
```bash
# 查看命令历史
cat ~/.selector-cli/history

# 查看保存的变量
cat ~/.selector-cli/vars.json
```

---

## 其他

### Q33: 支持哪些浏览器？

**A**: 基于 Playwright，支持 Chromium、Firefox、WebKit。默认使用 Chromium。

### Q34: 可以并行运行吗？

**A**: 当前版本是单线程的。可以使用多个实例或脚本来实现并行。

### Q35: 如何贡献代码？

**A**: 欢迎提交 Pull Request！请确保：
1. 添加测试
2. 更新文档
3. 保持代码风格一致

---

## 联系支持

- **报告 Bug**: GitHub Issues
- **功能请求**: GitHub Discussions
- **文档问题**: 提交 PR 更新文档

---

**提示**: 使用 `help` 命令查看所有可用命令，或使用 Tab 键补全。
