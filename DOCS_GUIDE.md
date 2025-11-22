# 项目文档导航 📚

**快速找到你需要的文档**

---

## 🎯 我想...

### ...快速开始使用 Selector CLI
👉 **[README.md](README.md)** - 用户指南
👉 **[QUICKSTART.md](QUICKSTART.md)** - 5分钟快速上手

### ...开始开发新功能
1. 📋 **[CHECKLIST.md](CHECKLIST.md)** - 开发前 5 分钟检查清单（先看这个！）
2. 🧭 **[PROJECT_CONTEXT.md](PROJECT_CONTEXT.md)** - 核心原则和质量标准（必读）
3. 📅 **[DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md)** - 确认要开发的功能在计划中

### ...了解项目设计
👉 **[selector-explorer/selector-cli-design-v1.0.md](../selector-explorer/selector-cli-design-v1.0.md)** - 完整系统设计（38KB）
👉 **[selector-explorer/selector-cli-grammar-v1.0.md](../selector-explorer/selector-cli-grammar-v1.0.md)** - EBNF 语法规范（14KB）

### ...查看实现细节
👉 **[IMPLEMENTATION.md](IMPLEMENTATION.md)** - Phase 1 实现总结
👉 **[SESSION_SUMMARY.md](SESSION_SUMMARY.md)** - 完整开发会话总结

### ...解决问题
👉 **[IMPORT_FIX.md](IMPORT_FIX.md)** - 导入错误修复
👉 **[AUTO_CLEAR_FEATURE.md](AUTO_CLEAR_FEATURE.md)** - 自动清除功能说明
👉 **README.md** - 故障排除章节

### ...查看版本历史
👉 **[CHANGELOG.md](CHANGELOG.md)** - 版本变更记录

---

## 📊 文档结构

```
selector-cli/
│
├── 用户文档（使用相关）
│   ├── README.md                    # 用户指南和参考
│   ├── QUICKSTART.md               # 快速入门（5分钟）
│   └── examples/                   # 示例脚本
│
├── 开发文档（开发必读）⭐
│   ├── CHECKLIST.md                # 开发前检查清单（每次必看！）
│   ├── PROJECT_CONTEXT.md          # 框架上下文（核心原则）
│   ├── DEVELOPMENT_PLAN.md         # 开发路线图（6个阶段）
│   └── CHANGELOG.md                # 版本历史
│
├── 实现文档（技术细节）
│   ├── IMPLEMENTATION.md           # 实现总结
│   ├── SESSION_SUMMARY.md          # 开发会话总结
│   ├── IMPORT_FIX.md              # 导入问题修复
│   └── AUTO_CLEAR_FEATURE.md      # 功能说明
│
├── 设计文档（深入了解）
│   ├── ../selector-explorer/
│   │   ├── selector-cli-design-v1.0.md      # 完整设计（38KB）
│   │   ├── selector-cli-grammar-v1.0.md     # 语法规范（14KB）
│   │   └── selector-cli-index-v1.0.md       # 文档索引（9KB）
│
└── 测试（质量保证）
    └── tests/
        ├── test_mvp.py             # 单元测试
        ├── test_integration.py     # 集成测试
        └── test_clear_on_open.py   # 功能测试
```

---

## 🎯 开发者工作流

### 第一次开发（30分钟）
```
1. 读 README.md（了解项目）                    [5分钟]
2. 读 PROJECT_CONTEXT.md（理解核心原则）       [15分钟]
3. 读 DEVELOPMENT_PLAN.md（了解路线图）        [10分钟]
```

### 每次开发前（5分钟）⭐
```
1. 完成 CHECKLIST.md                          [5分钟]
   ├─ 明确目标
   ├─ 设计检查
   ├─ 编码标准
   ├─ 测试计划
   └─ 文档计划
```

### 遇到问题时
```
1. 查看 CHECKLIST.md 的"快速决策树"
2. 对照 PROJECT_CONTEXT.md 的"核心原则"
3. 检查是否违反"质量红线"
```

### 提交代码前
```
1. 完成 CHECKLIST.md 的"提交前检查"
2. 更新 CHANGELOG.md
3. git commit（使用规范的 commit message）
```

---

## ⭐ 最重要的文档

### 对于用户
1. **README.md** - 完整用户指南
2. **QUICKSTART.md** - 5分钟上手

### 对于开发者（按优先级）
1. **CHECKLIST.md** ⭐⭐⭐ - 每次开发必看
2. **PROJECT_CONTEXT.md** ⭐⭐⭐ - 核心原则（第一次必读）
3. **DEVELOPMENT_PLAN.md** ⭐⭐ - 功能路线图
4. **CHANGELOG.md** ⭐ - 了解最新变更

---

## 📝 文档更新规则

### 必须更新
- ✅ **CHANGELOG.md** - 每次 commit 都要更新
- ✅ **README.md** - 新增/修改命令时更新
- ✅ **tests/** - 新功能必须有测试

### 建议更新
- 📝 **CHECKLIST.md** - 发现新的常见错误时
- 📝 **PROJECT_CONTEXT.md** - 重要架构决策时
- 📝 **DEVELOPMENT_PLAN.md** - Phase 完成时

### 不需要频繁更新
- 📄 设计文档（selector-cli-design-v1.0.md 等）- 稳定后很少改
- 📄 实现总结（IMPLEMENTATION.md）- 只在大版本更新

---

## 🔍 快速查找

### 命令语法
👉 **README.md** → "Commands" 章节
👉 **selector-cli-grammar-v1.0.md** → EBNF 规范

### 代码规范
👉 **PROJECT_CONTEXT.md** → "代码质量标准"

### 测试标准
👉 **PROJECT_CONTEXT.md** → "测试标准"

### 架构设计
👉 **PROJECT_CONTEXT.md** → "架构核心原则"
👉 **selector-cli-design-v1.0.md** → 完整设计

### 功能计划
👉 **DEVELOPMENT_PLAN.md** → Phase 2-6 计划

### 常见问题
👉 **README.md** → "Troubleshooting"
👉 **CHECKLIST.md** → "常见错误提醒"

---

## 💡 文档使用技巧

### 打印出来
建议打印并贴在显示器旁：
- **CHECKLIST.md** - 每次开发前检查
- **PROJECT_CONTEXT.md** 的"核心原则"部分

### 设置书签
浏览器/编辑器中添加书签：
- CHECKLIST.md - 最常用
- PROJECT_CONTEXT.md - 经常参考
- DEVELOPMENT_PLAN.md - 了解方向

### 搜索技巧
- Ctrl+F 在文档中搜索关键词
- 所有 .md 文件都有清晰的标题结构
- 使用 IDE 的全文搜索功能

---

## 🎓 学习路径

### 新加入开发者
```
Day 1: README.md + QUICKSTART.md
       └─ 了解项目是什么，怎么用

Day 2: PROJECT_CONTEXT.md
       └─ 理解设计原则和质量标准

Day 3: DEVELOPMENT_PLAN.md + selector-cli-design-v1.0.md
       └─ 了解路线图和详细设计

Day 4+: CHECKLIST.md + 开始开发
        └─ 每次开发前完成检查清单
```

### 临时贡献者
```
1. README.md - 了解项目
2. CHECKLIST.md - 开发前检查
3. 开始编码 + 参考 PROJECT_CONTEXT.md
```

---

## 📞 需要帮助？

### 开发问题
1. 查看 **CHECKLIST.md** 的"快速决策树"
2. 对照 **PROJECT_CONTEXT.md** 的"常见陷阱"
3. 参考 **DEVELOPMENT_PLAN.md** 了解功能计划

### 使用问题
1. 查看 **README.md** 的示例
2. 参考 **QUICKSTART.md** 的工作流
3. 查看 **examples/** 目录的示例脚本

### 设计问题
1. 阅读 **PROJECT_CONTEXT.md** 的"决策框架"
2. 参考 **selector-cli-design-v1.0.md** 的详细设计
3. 查看 **DEVELOPMENT_PLAN.md** 的功能规划

---

## ✨ 文档原则

我们的文档遵循：
- **示例优先** - 先给示例，再讲原理
- **分层清晰** - 快速入门 → 用户指南 → 深入设计
- **及时更新** - 代码改了，文档就改
- **易于查找** - 清晰的结构和导航

---

**记住：好的文档是成功项目的一半！** 📚✨

---

_最后更新: 2025-11-22_
_如有疑问，从 CHECKLIST.md 开始_ 👈
