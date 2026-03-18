# Test Cases for Knowbie

This folder contains QA test reports and evidence for the Knowbie Personal Knowledge Manager project.

## Files

| File | Description |
|------|-------------|
| `knowbie-test-report.md` | Complete test report with all test cases and results |
| `QA_SUMMARY.md` | Quick summary of test results and recommendations |
| `evidence/` | Test evidence and screenshots |

## Test Summary

- **Total Test Cases:** 28
- **Passed:** 23 (82.1%)
- **Failed:** 2
- **Blocked:** 3
- **Status:** ⚠️ Conditional Pass

## Evidence Files

- `TC-001-add-link.md` - Adding link knowledge
- `TC-004-add-image.md` - Image upload process
- `TC-010-search.md` - Search functionality
- `TC-020-filter-tags.md` - Tag filtering
- `TC-030-edit-item.md` - Edit knowledge item
- `TC-070-mobile-responsive.md` - Mobile layout testing

## Known Issues

1. **BUG-001:** File upload accepts executable files (.exe) - Security risk
2. **BUG-002:** No rate limiting on API endpoints - DDoS vulnerability

See full report for details and recommendations.

---

**Last Updated:** 2026-03-18  
**QA Engineer:** vibe-qa
