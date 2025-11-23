# Feature: Auto-clear on New Page

## Change Summary

**Date**: 2025-11-22
**Type**: Enhancement
**Status**: ✅ Implemented and Tested

## Description

When the user opens a new page with the `open` command, the CLI now automatically clears:
- All scanned elements (`context.all_elements`)
- The current collection (`context.collection`)
- The last scan timestamp (`context.last_scan_time`)

This ensures that elements from the previous page don't contaminate the new page's analysis.

## Rationale

User feedback: "open 新页面的时候要清除元素集合" (When opening a new page, clear the element collection)

Previously, when opening a new page:
- Old scanned elements remained in `all_elements`
- Elements in the collection remained
- This could cause confusion or errors when trying to interact with elements from a different page

## Implementation

**File**: `src/commands/executor.py`
**Method**: `_execute_open()`

```python
async def _execute_open(self, command: Command, context: Context) -> str:
    # ... URL validation ...

    success = await context.browser.open(url)
    if success:
        context.current_url = url
        context.is_page_loaded = True

        # Clear previous page's elements and collection
        context.all_elements.clear()
        context.collection.clear()
        context.last_scan_time = None

        return f"Opened: {url}"
```

## Behavior

### Before
```bash
selector> open https://page1.com
selector(page1.com)> scan
Scanned 10 elements

selector(page1.com)> add input
Added 5 element(s) to collection. Total: 5

selector(page1.com)[5]> open https://page2.com
Opened: https://page2.com

selector(page2.com)[5]>  # Still shows [5] - old collection!
```

### After
```bash
selector> open https://page1.com
selector(page1.com)> scan
Scanned 10 elements

selector(page1.com)> add input
Added 5 element(s) to collection. Total: 5

selector(page1.com)[5]> open https://page2.com
Opened: https://page2.com

selector(page2.com)>  # Collection cleared! No [5]
selector(page2.com)> scan
Scanned 8 elements  # Fresh scan of new page
```

## Test Coverage

**New Test**: `tests/test_clear_on_open.py`

Test steps:
1. Open page and scan (8 elements found)
2. Add elements to collection (4 inputs added)
3. Verify elements and collection exist
4. Open new page (same URL to isolate the test)
5. **Assert**: `all_elements` is empty
6. **Assert**: `collection` is empty
7. **Assert**: `last_scan_time` is None
8. Scan again to verify functionality still works

**Result**: ✅ All assertions pass

## User Impact

**Positive**:
- Cleaner workflow when analyzing multiple pages
- No confusion from stale elements
- Prompt correctly shows empty collection after opening new page
- More predictable behavior

**Breaking Changes**: None
- Users who relied on keeping elements across pages will need to re-scan
- This is the expected behavior for most use cases

## Related Commands

Commands that interact with cleared data:
- `scan` - Must be run after `open` to populate elements
- `add` - Will have no elements to add until `scan` is run
- `list` - Will show "No elements found" until `scan` is run
- `show` - Will show empty collection until elements are added

## Documentation Updates

Updated files:
- `CHANGELOG.md` - Added entry for this feature
- `README.md` - Updated example session to show clear behavior
- Test suite - Added `test_clear_on_open.py`

## Examples

### Example 1: Analyzing Multiple Pages
```bash
selector> open https://site.com/login
selector(site.com)> scan
Scanned 15 elements

selector(site.com)> add input
Added 3 element(s). Total: 3

selector(site.com)[3]> list
[0] input[type="email"]
[1] input[type="password"]
[2] button[type="submit"]

# Open new page - collection automatically cleared
selector(site.com)[3]> open https://site.com/register
Opened: https://site.com/register

# Prompt shows no collection
selector(site.com)> scan
Scanned 20 elements

selector(site.com)> add input
Added 5 element(s). Total: 5

selector(site.com)[5]> list
# Shows only elements from /register page
```

### Example 2: Switching Between Pages
```bash
selector> open https://google.com
selector(google.com)> scan
selector(google.com)> count
Collection contains 0 element(s)

selector(google.com)> add input
Added 1 element(s). Total: 1

# Switch to different site
selector(google.com)[1]> open https://github.com
Opened: https://github.com

# Collection cleared - prompt reflects this
selector(github.com)> count
Collection contains 0 element(s)
```

## Future Enhancements

Potential future features:
- Add `--keep` flag to `open` command to preserve collection
- Add command to save/restore collections across page changes
- Add history of collections from previous pages

## Conclusion

✅ **Feature Complete**
✅ **Tested and Working**
✅ **User Request Satisfied**

The CLI now provides cleaner, more predictable behavior when working with multiple pages.
