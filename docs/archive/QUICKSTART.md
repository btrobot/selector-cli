# Selector CLI - Quick Start Guide

## Get Started in 30 Seconds

### 1. Install Dependencies
```bash
cd F:\browser-use\selector-cli
pip install -r requirements.txt
playwright install chromium
```

### 2. Run the Test Suite
```bash
python tests/test_mvp.py
```

Expected output:
```
============================================================
Selector CLI - Phase 1 MVP Test Suite
============================================================
...
[OK] All tests complete!
```

### 3. Start the CLI
```bash
python selector-cli.py
```

### 4. Try Basic Commands
```bash
selector> help
selector> open https://www.google.com
selector(google.com)> scan
selector(google.com)> list input
selector(google.com)> add input
selector(google.com)[N]> show
selector(google.com)[N]> quit
```

## Common Workflows

### Workflow 1: Analyze a Login Form
```bash
selector> open https://example.com/login
selector> scan
selector> add input where type="email"
selector> add input where type="password"
selector> add button where type="submit"
selector> list
selector> show
```

### Workflow 2: Explore All Buttons
```bash
selector> open https://example.com
selector> scan
selector> list button
selector> add button
selector> count
```

### Workflow 3: Select Specific Elements
```bash
selector> open https://example.com
selector> scan
selector> list
selector> add [0,2,5]
selector> show
```

## Command Cheat Sheet

| Command | Description | Example |
|---------|-------------|---------|
| `open <url>` | Open URL | `open https://example.com` |
| `scan` | Scan page | `scan` |
| `add <target>` | Add to collection | `add input` |
| `add <target> where <cond>` | Add with filter | `add button where type="submit"` |
| `remove <target>` | Remove from collection | `remove [0]` |
| `list` | List collection | `list` |
| `list <target>` | List elements | `list input` |
| `show` | Show details | `show` |
| `show <target>` | Show specific | `show [0]` |
| `count` | Count collection | `count` |
| `clear` | Clear collection | `clear` |
| `help` | Show help | `help` |
| `quit` | Exit | `quit` |

## Prompt Explained

```
selector>                      # No page loaded
selector(example.com)>         # Page loaded
selector(example.com)[3]>      # Page loaded + 3 items in collection
```

## Tips

1. **Use `list` first** to see all scanned elements before adding
2. **Use `show [N]`** to inspect element details
3. **WHERE clause** supports `=` and `!=` operators
4. **Target types**: `input`, `button`, `select`, `textarea`, `a`
5. **Press Ctrl+C** if stuck, then use `quit` to exit

## Troubleshooting

**Browser doesn't open?**
```bash
playwright install chromium
```

**Parse error?**
- Check command syntax with `help`
- URLs don't need quotes: `open https://example.com`

**No elements found?**
- Make sure page is loaded: `open <url>`
- Run `scan` after opening page

## Next Steps

- Read `README.md` for full documentation
- Check `IMPLEMENTATION.md` for technical details
- See `examples/example-session.txt` for more examples

## Questions?

Check the design documents:
- `../selector-explorer/selector-cli-design-v1.0.md`
- `../selector-explorer/selector-cli-grammar-v1.0.md`

---

**Happy element hunting!** 🔍
