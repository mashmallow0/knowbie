# Knowbie - Code Documentation

## Overview
Knowbie is a personal knowledge manager built with FastAPI backend and vanilla JavaScript SPA frontend. It uses CSV for storage and Qdrant for semantic search.

## Project Structure
```
knowbie/
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── api/
│   │   ├── __init__.py
│   │   ├── knowledge.py     # CRUD endpoints + Export
│   │   └── search.py        # Semantic search endpoints
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css    # Custom styles + Dark mode
│   │   └── js/
│   │       └── app.js       # Frontend SPA logic
│   └── templates/
│       └── index.html       # Main template
├── data/
│   ├── knowledge.csv        # Main data storage
│   ├── attachments/         # File uploads
│   └── index.json           # Config & stats
├── docs/
│   ├── flowchart.svg        # Architecture diagram
│   └── knowbie-code-docs.md # This file
└── extension/               # 🆕 Browser Extension
    ├── manifest.json        # Extension config
    ├── background.js        # Context menus
    ├── popup.html/js        # Popup interface
    ├── options.html         # Settings
    ├── icons/               # Extension icons
    └── README.md
```

## 🆕 New Features (v1.1.0)

### 1. 🌙 Dark Mode
- Toggle button in navigation (sun/moon icon)
- CSS variables for theme switching
- Preference saved in localStorage
- Instant switch without page reload

**Implementation:**
- CSS variables in `:root` and `[data-theme="dark"]`
- JavaScript `toggleTheme()` function
- `loadTheme()` on app initialization

### 2. 📤 Export Markdown/PDF
- Export dropdown in navigation
- Export All Items or Current Item
- Markdown export: generates `.md` file
- PDF export: generates printable HTML or PDF (if weasyprint available)

**API Endpoints:**
- `POST /api/knowledge/export/pdf` - Export to PDF

**Frontend Functions:**
- `exportMarkdown(scope)` - Client-side markdown generation
- `exportPDF(scope)` - PDF generation with fallback

### 3. 📋 Templates
- Template selector in Add Knowledge modal
- 4 preset templates:
  - 📅 **Meeting Notes**: Attendees, Agenda, Notes, Action Items
  - 💻 **Code Snippet**: Function template with placeholder
  - 📚 **Book Summary**: Key takeaways, quotes, rating
  - ⚡ **Quick Note**: Simple note template

**Frontend:**
- `templates` object with structure + placeholders
- `applyTemplate(key)` function

### 4. 🔌 Browser Extension
Manifest V3 extension for Chrome/Firefox.

**Features:**
- Context menu: "Save Link", "Save Selection", "Save Page"
- Popup: Quick add knowledge with type selection
- Options: Configure API URL
- Notifications for save status

**Permissions:**
- `activeTab` - Access current tab
- `contextMenus` - Right-click menus
- `storage` - Save settings

**Installation:**
1. Chrome: `chrome://extensions/` → Developer mode → Load unpacked
2. Firefox: `about:debugging` → Load Temporary Add-on

## API Endpoints

### Knowledge API (`/api/knowledge`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Get all items (optional: `?tag=xxx&type=xxx`) |
| GET | `/tags` | Get all unique tags |
| GET | `/stats` | Get statistics |
| GET | `/{item_id}` | Get single item |
| POST | `/` | Create new item |
| PUT | `/{item_id}` | Update item |
| DELETE | `/{item_id}` | Delete item |
| POST | `/{item_id}/upload` | Upload attachment |
| 🆕 POST | `/export/pdf` | Export items to PDF |

### Search API (`/api/search`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/` | Semantic search |
| GET | `/suggest` | Search suggestions |
| POST | `/index/{item_id}` | Index item for search |
| DELETE | `/index/{vector_id}` | Remove from index |
| GET | `/health` | Search service health |

## Data Models

### KnowledgeItem
```python
{
    "id": str,              # 8-char UUID
    "title": str,
    "content": str,
    "type": str,            # link|code|note|image|file|idea
    "tags": str,            # comma-separated
    "source": str,
    "created_at": str,      # ISO format
    "updated_at": str,      # ISO format
    "vector_id": str|null   # Qdrant point ID
}
```

### ExportRequest
```python
{
    "items": List[KnowledgeItem]
}
```

## CSV Schema
```csv
id,title,content,type,tags,source,created_at,updated_at,vector_id
```

## Frontend Components

### Type Configurations
- **link**: Purple theme, 🔗 icon
- **code**: Mint theme, 💻 icon
- **note**: Orange theme, 📝 icon
- **image**: Pink theme, 🖼️ icon
- **file**: Rose theme, 📎 icon
- **idea**: Indigo theme, 💡 icon

### Keyboard Shortcuts
- `⌘K` / `Ctrl+K` - Open search
- `ESC` - Close modals
- `N` - New item

### 🆕 New UI Elements

**Dark Mode Toggle:**
```html
<button class="theme-toggle" onclick="app.toggleTheme()">
  <svg class="sun-icon">...</svg>
  <svg class="moon-icon">...</svg>
</button>
```

**Export Dropdown:**
```html
<div class="relative" id="export-dropdown">
  <button onclick="app.toggleExportMenu()">Export</button>
  <div id="export-menu" class="dropdown-menu">
    <button onclick="app.exportMarkdown('all')">Export All (Markdown)</button>
    <button onclick="app.exportMarkdown('current')">Export Current (Markdown)</button>
    <button onclick="app.exportPDF('all')">Export All (PDF)</button>
    <button onclick="app.exportPDF('current')">Export Current (PDF)</button>
  </div>
</div>
```

**Template Selector:**
```html
<select id="template-select" onchange="app.applyTemplate(this.value)">
  <option value="">-- No template --</option>
  <option value="meeting">📅 Meeting Notes</option>
  <option value="code">💻 Code Snippet</option>
  <option value="book">📚 Book Summary</option>
  <option value="quick">⚡ Quick Note</option>
</select>
```

## Dependencies

### Backend
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `python-multipart` - File uploads
- `jinja2` - Templates
- `qdrant-client` - Vector search
- `sentence-transformers` - Embeddings
- `weasyprint` (optional) - PDF generation

### Frontend
- Tailwind CSS (CDN)
- Highlight.js - Code syntax
- Vanilla JavaScript (no framework)

### Extension
- Manifest V3
- Chrome 88+ / Firefox 109+

## Environment Variables
```bash
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

## Running the App

### Main App
```bash
# Install dependencies
pip install -r requirements.txt

# Run server
python app/main.py

# Access at http://localhost:8000
```

### Browser Extension
```bash
# Chrome
1. Go to chrome://extensions/
2. Enable Developer mode
3. Click "Load unpacked"
4. Select the extension/ folder

# Firefox
1. Go to about:debugging
2. Click "This Firefox"
3. Click "Load Temporary Add-on"
4. Select extension/manifest.json
```

## Semantic Search Flow
1. User enters query
2. Frontend sends to `/api/search/`
3. Backend encodes query using `all-MiniLM-L6-v2`
4. Qdrant performs cosine similarity search
5. Results returned with relevance scores
6. Frontend displays with highlighting

## File Storage
- Attachments stored in `data/attachments/`
- Filename format: `{item_id}_{hash}{ext}`
- Accessible via `/data/attachments/{filename}`

## Export Flow
### Markdown Export
1. User selects scope (all/current)
2. Frontend generates markdown string
3. Creates Blob and triggers download
4. File saved as `knowbie-export-{date}.md`

### PDF Export
1. User selects scope
2. Backend receives items list
3. Tries weasyprint for PDF generation
4. Falls back to printable HTML
5. File downloaded or print dialog opened

## Dark Mode CSS Variables
```css
:root {
  --bg-primary: #FEFCE8;
  --bg-secondary: #ffffff;
  --text-primary: #1f2937;
  --border-color: #e5e7eb;
}

[data-theme="dark"] {
  --bg-primary: #0f172a;
  --bg-secondary: #1e293b;
  --text-primary: #f1f5f9;
  --border-color: #334155;
}
```

## Future Enhancements
- [ ] Edit item functionality (in progress)
- [ ] Tags management page
- [ ] Statistics dashboard
- [ ] Import from Markdown/CSV
- [ ] Real-time sync
- [ ] Mobile app
