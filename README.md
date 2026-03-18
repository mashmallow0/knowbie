# 🧠 Knowbie

Personal Knowledge Manager - ระบบจัดการความรู้ส่วนตัว ที่ใช้งานง่าย ทันสมัย ไม่ต้องใช้ Database (file-based CSV)

## 🚀 Features

- **Card-based Layout** - แสดง knowledge แบบ cards (เหมือน Pinterest)
- **Quick Capture** - Floating Action Button (FAB) เพิ่ม knowledge เร็ว
- **Tag System** - แท็ก/หมวดหมู่แบบ pill buttons
- **Semantic Search** - ⌘K shortcut, ค้นหาผ่าน Qdrant (AI-powered)
- **Type Support** - Link, Code, Note, Image
- **Responsive** - ใช้บนมือถือได้

## 🎨 Color Palette

- 🟣 Primary: #A78BFA (ม่วงอ่อน)
- 🩷 Accent: #F9A8D4 (ชมพูพาสเทล)
- 🟢 Mint: #6EE7B7 (เขียวอมฟ้า)
- 🟠 Orange: #FDBA74 (ส้มอ่อน)
- ⬜ Background: #FEFCE8 (ครีม)

## 🛠️ Tech Stack

- **Frontend:** HTML + Tailwind CSS + Vanilla JS (SPA)
- **Backend:** Python FastAPI
- **Storage:** CSV file + local folder for attachments
- **Search:** Qdrant (semantic search with sentence-transformers)

## 📁 Project Structure

```
knowbie/
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── static/
│   │   ├── css/style.css    # Custom styles
│   │   └── js/app.js        # Frontend logic
│   ├── templates/
│   │   └── index.html       # Main HTML template
│   └── api/
│       ├── knowledge.py     # CRUD endpoints
│       └── search.py        # Search endpoints
├── data/
│   ├── knowledge.csv        # Main data file
│   ├── attachments/         # File uploads
│   └── index.json           # Config & stats
├── designs/                 # UI/UX designs (SVG, PNG)
├── docs/
│   ├── flowchart.svg        # Architecture diagram
│   └── knowbie-code-docs.md # Code documentation
├── reviews/
│   └── knowbie-review-round-1.md  # Code review reports
├── test-cases/
│   ├── knowbie-test-report.md     # QA test reports
│   └── evidence/            # Test screenshots
└── requirements.txt
```

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Qdrant (optional, for semantic search)

### Installation

```bash
# Clone the repository
git clone https://github.com/mashmallow0/knowbie.git
cd knowbie

# Install dependencies
pip install -r requirements.txt

# Run the application
python app/main.py

# Access at http://localhost:8000
```

### Qdrant Setup (for semantic search)

```bash
# Using Docker
docker run -p 6333:6333 qdrant/qdrant

# Or use cloud version at https://qdrant.io
```

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `⌘K` / `Ctrl+K` | Open search modal |
| `ESC` | Close modals |
| `N` | Add new item |

## 📚 API Documentation

### Knowledge Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/knowledge/` | Get all items |
| GET | `/api/knowledge/tags` | Get all tags |
| GET | `/api/knowledge/stats` | Get statistics |
| GET | `/api/knowledge/{id}` | Get single item |
| POST | `/api/knowledge/` | Create item |
| PUT | `/api/knowledge/{id}` | Update item |
| DELETE | `/api/knowledge/{id}` | Delete item |

### Search Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/search/` | Semantic search |
| GET | `/api/search/suggest` | Search suggestions |

## 📄 License

MIT License

---
*Built with ❤️ by Knowbie Team*