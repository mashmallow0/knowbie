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
│   │   ├── knowledge.py     # CRUD endpoints
│   │   └── search.py        # Semantic search endpoints
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css    # Custom styles
│   │   └── js/
│   │       └── app.js       # Frontend SPA logic
│   └── templates/
│       └── index.html       # Main template
├── data/
│   ├── knowledge.csv        # Main data storage
│   ├── attachments/         # File uploads
│   └── index.json           # Config & stats
└── docs/
    ├── flowchart.svg        # Architecture diagram
    └── knowbie-code-docs.md # This file
```

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
    "type": str,            # link|code|note|image|file
    "tags": str,            # comma-separated
    "source": str,
    "created_at": str,      # ISO format
    "updated_at": str,      # ISO format
    "vector_id": str|null   # Qdrant point ID
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

### Keyboard Shortcuts
- `⌘K` / `Ctrl+K` - Open search
- `ESC` - Close modals
- `N` - New item

## Dependencies

### Backend
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `python-multipart` - File uploads
- `jinja2` - Templates
- `qdrant-client` - Vector search
- `sentence-transformers` - Embeddings

### Frontend
- Tailwind CSS (CDN)
- Highlight.js - Code syntax
- Vanilla JavaScript (no framework)

## Environment Variables
```bash
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

## Running the App
```bash
# Install dependencies
pip install -r requirements.txt

# Run server
python app/main.py

# Access at http://localhost:8000
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

## Future Enhancements
- [ ] Edit item functionality
- [ ] Tags management page
- [ ] Statistics dashboard
- [ ] Import/Export
- [ ] Markdown support
- [ ] Image preview optimization