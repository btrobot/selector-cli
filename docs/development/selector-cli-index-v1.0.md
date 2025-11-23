# Selector CLI - Documentation Index v1.0

## 📚 Overview

This directory contains the complete design and specification documents for **Selector CLI v1.0** - an interactive command-line tool for web element selection and manipulation.

---

## 📖 Documents

### 1. Design Document v1.0
**File**: `selector-cli-design-v1.0.md`
**Size**: ~35KB
**Last Updated**: 2025-11-22

**Contents**:
1. Project Overview
2. System Architecture
3. Command Reference
4. Data Model
5. Core Components
6. User Interface
7. Implementation Plan
8. Technical Specifications
9. Use Cases
10. Appendix

**Key Sections**:
- Complete architecture diagrams
- All 50+ commands documented
- Data structures and classes
- Component responsibilities
- 6-phase implementation plan
- Real-world use cases

**Audience**:
- Developers implementing the system
- Architects reviewing the design
- Product managers understanding scope

---

### 2. Grammar Specification v1.0
**File**: `selector-cli-grammar-v1.0.md`
**Size**: ~12KB
**Last Updated**: 2025-11-22

**Contents**:
- Complete EBNF grammar definition
- Command syntax rules
- WHERE clause syntax
- Token categories
- Operator precedence
- Reserved words
- Error productions
- 50+ grammar examples

**Key Sections**:
- Formal EBNF notation
- All command productions
- Condition expression grammar
- Index specification syntax
- Terminal definitions

**Audience**:
- Parser developers
- Language designers
- Compiler students
- Tool builders

---

## 🎯 Quick Start

### For Implementers
1. Read **Design Document** Section 2 (Architecture)
2. Review **Grammar Specification** for syntax
3. Read **Design Document** Section 5 (Core Components)
4. Check **Design Document** Section 7 (Implementation Plan)

### For Users
1. Read **Design Document** Section 3 (Command Reference)
2. Check **Grammar Specification** examples
3. Review **Design Document** Section 9 (Use Cases)

### For Reviewers
1. Read **Design Document** Section 1 (Overview)
2. Review **Design Document** Section 2 (Architecture)
3. Check **Design Document** Section 7 (Implementation Plan)
4. Review **Grammar Specification** completeness

---

## 📊 Document Statistics

| Metric | Design Doc | Grammar Doc | Total |
|--------|-----------|-------------|-------|
| **Sections** | 10 | 8 | 18 |
| **Commands** | 50+ | 50+ | - |
| **Examples** | 30+ | 50+ | 80+ |
| **Tables** | 15 | 5 | 20 |
| **Code Blocks** | 40+ | 60+ | 100+ |
| **Diagrams** | 5 | - | 5 |

---

## 🏗️ Architecture Overview

```
User Input ──▶ REPL ──▶ Parser ──▶ Executor
                         (Grammar)    │
                                      ├──▶ Browser Manager
                                      ├──▶ Element Manager
                                      └──▶ Collection Manager
                                            │
                                            ▼
                                      Playwright API
```

---

## 📝 Command Categories

### Browser Control (5 commands)
- open, refresh, wait, back, forward

### Element Discovery (1 command)
- scan (with options)

### Collection Management (7 commands)
- add, remove, clear, keep, unique, union, intersect, difference

### Querying (5 commands)
- list, show, count, stats, filter

### Visualization (3 commands)
- highlight, unhighlight, blink

### Export (1 command)
- export (7 formats)

### Storage (4 commands)
- save, load, saved, delete

### Utilities (8 commands)
- set, vars, macro, run, exec, history, help, exit

**Total**: 34 base commands + variations

---

## 🔍 Grammar Highlights

### Command Syntax
```ebnf
command = browser_command
        | scan_command
        | collection_command
        | query_command
        | visual_command
        | export_command
        | storage_command
        | utility_command
        ;
```

### WHERE Clause
```ebnf
where_clause = "where" , condition ;

condition = simple_condition
          | compound_condition
          ;

simple_condition = field , operator , value ;

compound_condition = simple_condition , logic_operator , condition
                   | "(" , condition , ")"
                   ;
```

### Examples
```bash
add input where type="email"
add button where text contains "Submit" and not disabled
list where (type="text" or type="email") and has placeholder
```

---

## 💡 Key Features

### 1. SQL-Like Syntax
```bash
selector> add input where type="email" and placeholder != ""
selector> filter where visible=true and enabled=true
```

### 2. Visual Feedback
```bash
selector> highlight collection --label --color=red
```

### 3. Code Generation
```bash
selector> export playwright
# email = page.locator('input[type="email"]')
# password = page.locator('input[type="password"]')
```

### 4. Persistence
```bash
selector> save login-form
selector> load login-form
```

### 5. Scripting
```bash
selector> macro test-setup {
    add input where type="email"
    add input where type="password"
    highlight
}
selector> run test-setup
```

---

## 🎓 Example Session

```bash
# Start and open page
selector> open https://example.com/login

# Scan for elements
selector> scan

# Build collection
selector> add input where type="email"
selector> add input where type="password"
selector> add button where text contains "Login"

# Verify
selector> show
# [0] input[type="email"]
# [1] input[type="password"]
# [2] button:has-text("Login")

# Visual check
selector> highlight --label

# Export code
selector> export playwright > login_test.py

# Save for reuse
selector> save login-elements
```

---

## 📋 Implementation Checklist

### Phase 1: MVP ✅
- [ ] REPL loop
- [ ] Basic parser
- [ ] Commands: open, scan, list, add, remove, show
- [ ] Simple WHERE (=, !=)
- [ ] Basic highlighting
- [ ] Export selectors

### Phase 2: Filtering ⏳
- [ ] Complex WHERE (and, or, not)
- [ ] String operators (contains, starts, ends, matches)
- [ ] Index ranges [1-10]
- [ ] keep, filter commands

### Phase 3: Export ⏳
- [ ] Playwright export
- [ ] Selenium export
- [ ] JSON/CSV export
- [ ] File redirection

### Phase 4: Persistence ⏳
- [ ] save/load collections
- [ ] Variable system
- [ ] Macros
- [ ] Script execution

### Phase 5: Advanced ⏳
- [ ] Shadow DOM support
- [ ] Set operations
- [ ] History
- [ ] Auto-completion

### Phase 6: Polish ⏳
- [ ] Testing
- [ ] Documentation
- [ ] Performance optimization

---

## 🔗 Related Files

### Current Project
```
selector-explorer/
├── selector-cli-design-v1.0.md      ← Design Document
├── selector-cli-grammar-v1.0.md     ← Grammar Specification
└── selector-cli-index-v1.0.md       ← This file
```

### Future Files (When Implemented)
```
selector-cli/
├── docs/
│   ├── design-v1.0.md
│   ├── grammar-v1.0.md
│   ├── user-guide.md
│   └── api-reference.md
├── src/
│   ├── repl/
│   ├── parser/
│   ├── commands/
│   └── core/
├── tests/
└── examples/
```

---

## 🚀 Next Steps

1. **Review**
   - Architecture review meeting
   - Grammar completeness check
   - Use case validation

2. **Prototype**
   - Implement basic REPL
   - Build simple parser
   - Test core commands

3. **Iterate**
   - User feedback
   - Grammar refinement
   - Feature prioritization

4. **Implement**
   - Follow 6-phase plan
   - Continuous testing
   - Documentation updates

---

## 📞 Questions & Feedback

### For Clarification
- Architecture questions → Design Document Section 2
- Syntax questions → Grammar Specification
- Implementation questions → Design Document Section 7

### For Contributions
1. Read both documents thoroughly
2. Propose changes via discussion
3. Update relevant sections
4. Increment version number

---

## 📜 Version History

### v1.0 (2025-11-22)
- Initial design document
- Complete EBNF grammar
- Full command reference
- Architecture definition
- Implementation plan

---

## 📖 Reading Guide

### Quick Overview (15 minutes)
1. This index file
2. Design Document - Section 1 (Overview)
3. Grammar Specification - Examples section

### Architecture Deep Dive (1 hour)
1. Design Document - Section 2 (Architecture)
2. Design Document - Section 4 (Data Model)
3. Design Document - Section 5 (Core Components)

### Command Reference (30 minutes)
1. Design Document - Section 3 (Commands)
2. Grammar Specification - All productions
3. Design Document - Section 9 (Use Cases)

### Implementation Guide (2 hours)
1. Design Document - Section 7 (Plan)
2. Design Document - Section 8 (Technical Specs)
3. Grammar Specification - Complete grammar
4. Design Document - Section 5 (Components)

---

**Total Documentation**: 47KB
**Total Commands**: 34 base + variations
**Total Examples**: 80+
**Estimated Read Time**: Full docs ~2-3 hours

---

**Selector CLI v1.0 - Design Complete** ✅
**Ready for Implementation** 🚀
