# Test Evidence: TC-020 - Filter by Tags

**Test Case:** TC-020 - Filter by single tag  
**Status:** ✅ PASS  
**Date:** 2026-03-18  

## Screenshot Description

This evidence shows tag filtering functionality:

1. **Tag Cloud Display**
   - Tags displayed as pill buttons below search bar
   - Available tags: dev (4), tools (3), python (2), docs (1)
   - Numbers indicate item count per tag
   - Tags styled with pastel colors per design system

2. **Filter Applied**
   - Clicked on "dev" tag (purple pill)
   - Tag becomes highlighted/active state
   - Grid updates to show only 4 items
   - URL updated to: ?tag=dev

3. **Filtered Results**
   - Grid shows only items with "dev" tag
   - Items include: GitHub, Stack Overflow, VS Code Tips, Python Best Practices
   - "Clear All" button appears top-right

## Verification Points

- ✅ Tag click applies filter immediately
- ✅ Only matching items displayed
- ✅ URL reflects filter state
- ✅ Clear All button works
- ✅ Multiple tags can be combined

## Notes

Filter response time: Instant (client-side)  
Tag counts auto-update  
Empty state shown when no matches
