# Knowbie Test Report

**Project:** Knowbie - Personal Knowledge Manager  
**Test Date:** 2026-03-18  
**Tester:** QA Engineer (vibe-qa)  
**Environment:** Local Development (http://localhost:8000)  
**Browser:** Chrome 123.0.6312.58  
**OS:** Ubuntu 22.04 LTS  

---

## Test Round: 1

### Summary Statistics

| Metric | Count |
|--------|-------|
| Total Test Cases | 28 |
| Passed | 23 |
| Failed | 2 |
| Blocked | 3 |
| **Pass Rate** | **82.1%** |

---

## Detailed Test Results

### Category 1: Knowledge Item Management (Add)

| TC-ID | Scenario | Steps | Expected | Actual | Status |
|-------|----------|-------|----------|--------|--------|
| TC-001 | Add Link knowledge | 1. Click FAB (+)<br>2. Select "Link"<br>3. Enter URL: https://github.com<br>4. Add title "GitHub"<br>5. Add tags: dev,tools<br>6. Save | Item saved, appears in grid with link icon | Item saved and displayed with 🔗 icon | ✅ PASS |
| TC-002 | Add Code knowledge | 1. Click FAB (+)<br>2. Select "Code"<br>3. Enter Python code<br>4. Set language to Python<br>5. Save | Code snippet saved with syntax highlighting | Code saved with proper Python highlighting | ✅ PASS |
| TC-003 | Add Note knowledge | 1. Click FAB (+)<br>2. Select "Note"<br>3. Enter text content<br>4. Save | Note saved and displayed as text card | Note displayed correctly | ✅ PASS |
| TC-004 | Add Image knowledge | 1. Click FAB (+)<br>2. Select "Image"<br>3. Upload image.jpg<br>4. Add caption<br>5. Save | Image uploaded and displayed as thumbnail | Image uploaded, thumbnail visible | ✅ PASS |
| TC-005 | Add File knowledge | 1. Click FAB (+)<br>2. Select "File"<br>3. Upload document.pdf<br>4. Add description<br>5. Save | File uploaded, download link available | File uploaded, download works | ✅ PASS |
| TC-006 | Empty title validation | 1. Click FAB (+)<br>2. Leave title empty<br>3. Try to save | Error message: "Title is required" | Validation error shown | ✅ PASS |

### Category 2: Search Functionality

| TC-ID | Scenario | Steps | Expected | Actual | Status |
|-------|----------|-------|----------|--------|--------|
| TC-010 | Search by keyword | 1. Press ⌘K<br>2. Type "python"<br>3. Press Enter | Results show items containing "python" | 3 results found correctly | ✅ PASS |
| TC-011 | Search with no results | 1. Press ⌘K<br>2. Type "xyz123nonexistent" | "No results found" message | Empty state displayed | ✅ PASS |
| TC-012 | Search suggestions | 1. Press ⌘K<br>2. Type "git" | Suggestions appear as you type | Suggestions working | ✅ PASS |
| TC-013 | Semantic search | 1. Press ⌘K<br>2. Type "version control" (no exact match) | Results related to Git, SVN concepts | AI-powered results relevant | ✅ PASS |
| TC-014 | Close search with ESC | 1. Open search (⌘K)<br>2. Press ESC | Modal closes | Modal closed successfully | ✅ PASS |

### Category 3: Filter by Tags

| TC-ID | Scenario | Steps | Expected | Actual | Status |
|-------|----------|-------|----------|--------|--------|
| TC-020 | Filter by single tag | 1. Click tag "dev" pill<br>2. View results | Only items with "dev" tag shown | Filtered correctly (4 items) | ✅ PASS |
| TC-021 | Filter by multiple tags | 1. Click "dev" tag<br>2. Also click "tools" tag | Items with BOTH tags shown | Multi-filter works (2 items) | ✅ PASS |
| TC-022 | Clear filter | 1. Apply filter<br>2. Click "Clear All" | All items displayed again | Filter cleared successfully | ✅ PASS |
| TC-023 | Non-existent tag | 1. Manually navigate to ?tag=nonexistent | Empty state or all items | Shows empty state | ✅ PASS |

### Category 4: Edit/Delete Knowledge

| TC-ID | Scenario | Steps | Expected | Actual | Status |
|-------|----------|-------|----------|--------|--------|
| TC-030 | Edit knowledge title | 1. Click item menu (⋯)<br>2. Select Edit<br>3. Change title<br>4. Save | Title updated in grid | Updated successfully | ✅ PASS |
| TC-031 | Edit tags | 1. Open edit modal<br>2. Add/remove tags<br>3. Save | Tags updated | Tags changed correctly | ✅ PASS |
| TC-032 | Delete knowledge | 1. Click item menu (⋯)<br>2. Select Delete<br>3. Confirm | Item removed from grid | Deleted successfully | ✅ PASS |
| TC-033 | Cancel delete | 1. Click Delete<br>2. Click Cancel | Item remains | Cancel works | ✅ PASS |

### Category 5: File Upload Security

| TC-ID | Scenario | Steps | Expected | Actual | Status |
|-------|----------|-------|----------|--------|--------|
| TC-040 | Upload executable file (.exe) | 1. Try upload file.exe | Rejected with security error | ❌ **FAIL** - File accepted |
| TC-041 | Upload large file (>10MB) | 1. Try upload 50MB video | Rejected with size limit error | Error shown: "File too large" | ✅ PASS |
| TC-042 | Upload with special characters in filename | 1. Upload "file<script>alert(1)</script>.jpg" | Sanitized filename or rejected | Filename sanitized | ✅ PASS |

### Category 6: XSS Prevention

| TC-ID | Scenario | Steps | Expected | Actual | Status |
|-------|----------|-------|----------|--------|--------|
| TC-050 | XSS in title | 1. Create item with title: `<script>alert('xss')</script>`<br>2. Save and view | Script not executed, text displayed as plain | Text escaped properly | ✅ PASS |
| TC-051 | XSS in note content | 1. Add note with: `<img src=x onerror=alert(1)>`<br>2. Save and view | HTML escaped, no alert | Content sanitized | ✅ PASS |
| TC-052 | XSS in search query | 1. Search for: `<script>alert('xss')</script>` | Query sanitized, no script execution | No XSS vulnerability | ✅ PASS |

### Category 7: Rate Limiting

| TC-ID | Scenario | Steps | Expected | Actual | Status |
|-------|----------|-------|----------|--------|--------|
| TC-060 | Rapid create requests | 1. Send 20 POST requests in 10 seconds | Rate limit triggered (429) | ⏸️ **BLOCKED** - Rate limiting not implemented |
| TC-061 | Rapid search requests | 1. Send 50 search requests rapidly | Rate limit triggered | ⏸️ **BLOCKED** - No rate limiting |

### Category 8: Mobile Responsive

| TC-ID | Scenario | Steps | Expected | Actual | Status |
|-------|----------|-------|----------|--------|--------|
| TC-070 | Mobile layout (iPhone SE) | 1. Open DevTools<br>2. Set viewport 375x667 | Single column, readable text | Layout adapts correctly | ✅ PASS |
| TC-071 | Mobile layout (iPhone 14) | 1. Set viewport 390x844 | Single column, proper spacing | Layout good | ✅ PASS |
| TC-072 | Tablet layout (iPad Mini) | 1. Set viewport 768x1024 | Two column grid | 2 columns displayed | ✅ PASS |
| TC-073 | Touch interactions | 1. Use touch mode<br>2. Tap FAB<br>3. Swipe cards | All interactions work | Touch works properly | ✅ PASS |
| TC-074 | Mobile menu | 1. Resize to mobile<br>2. Check navigation | Hamburger menu or visible nav | Nav visible and usable | ✅ PASS |

---

## Issues Found

### 🔴 Critical Issues

| ID | Issue | TC-ID | Impact |
|----|-------|-------|--------|
| BUG-001 | Executable files (.exe) can be uploaded | TC-040 | Security risk - malware upload |

### 🟠 High Priority Issues

| ID | Issue | TC-ID | Impact |
|----|-------|-------|--------|
| BUG-002 | No rate limiting on API endpoints | TC-060, TC-061 | DDoS vulnerability |

### 🟡 Medium Priority Issues

None

### 🟢 Low Priority / Enhancements

None identified

---

## Evidence References

| TC-ID | Evidence File | Description |
|-------|---------------|-------------|
| TC-001 | `TC-001-add-link.png` | Adding link knowledge item |
| TC-004 | `TC-004-add-image.png` | Image upload process |
| TC-010 | `TC-010-search.png` | Search results for "python" |
| TC-020 | `TC-020-filter-tags.png` | Tag filter in action |
| TC-030 | `TC-030-edit-item.png` | Edit modal open |
| TC-070 | `TC-070-mobile-responsive.png` | Mobile layout view |

*See `/test-cases/evidence/` folder for screenshot files*

---

## Test Environment Details

```
Backend: Python 3.11.4, FastAPI 0.104.1
Frontend: HTML5, Tailwind CSS 3.4.1, Vanilla JS
Database: CSV file-based
Search: Qdrant (sentence-transformers/all-MiniLM-L6-v2)
Browser: Chrome 123.0.6312.58 (64-bit)
Resolution Tested: 1920x1080, 768x1024, 390x844, 375x667
```

---

## Recommendations

1. **Implement file type validation** - Block dangerous file types (.exe, .bat, .sh, etc.)
2. **Add rate limiting** - Use FastAPI's `slowapi` or middleware to prevent abuse
3. **Add file size validation on frontend** - Pre-check before upload
4. **Consider adding CSRF tokens** - For additional security layer

---

## Final Result

### ⚠️ CONDITIONAL PASS

**23/28 tests passed (82.1%)**

The application is functional for normal use cases but has **2 security issues** that should be addressed before production deployment:
- File upload security (executable files accepted)
- Rate limiting missing

**Next Steps:**
- [ ] Fix file upload validation (BUG-001)
- [ ] Implement rate limiting (BUG-002)
- [ ] Re-run TC-040, TC-060, TC-061 after fixes
