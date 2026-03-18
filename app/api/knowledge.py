"""
Knowledge API Routes - CRUD Operations
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Request
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Literal
from datetime import datetime
from pathlib import Path
from slowapi.util import get_remote_address
from slowapi import Limiter
import csv
import os
import json
import uuid
import mimetypes
import fcntl

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")
CSV_PATH = os.path.join(DATA_DIR, "knowledge.csv")
ATTACHMENTS_DIR = os.path.join(DATA_DIR, "attachments")
INDEX_PATH = os.path.join(DATA_DIR, "index.json")

# File upload security settings
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.pdf', '.txt', '.md', '.py', '.js', '.html', '.json', '.csv', '.zip'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Ensure directories exist
os.makedirs(ATTACHMENTS_DIR, exist_ok=True)


class KnowledgeItem(BaseModel):
    id: str
    title: str
    content: str
    type: str  # link, code, note, image, file
    tags: str
    source: str
    created_at: str
    updated_at: str
    vector_id: Optional[str] = None


class KnowledgeCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Title of the knowledge item")
    content: str = Field(..., min_length=1, max_length=50000, description="Main content")
    type: Literal["link", "code", "note", "image", "file", "idea"] = Field(..., description="Type of knowledge item")
    tags: str = Field(default="", max_length=500, description="Comma-separated tags")
    source: str = Field(default="", max_length=1000, description="Source URL or reference")

    @validator('tags')
    def validate_tags(cls, v):
        if v:
            tags = [t.strip() for t in v.split(',') if t.strip()]
            if len(tags) > 20:
                raise ValueError('Maximum 20 tags allowed')
            if any(len(t) > 50 for t in tags):
                raise ValueError('Each tag must be less than 50 characters')
        return v


class KnowledgeUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1, max_length=50000)
    type: Optional[Literal["link", "code", "note", "image", "file", "idea"]] = None
    tags: Optional[str] = Field(None, max_length=500)
    source: Optional[str] = Field(None, max_length=1000)

    @validator('tags')
    def validate_tags(cls, v):
        if v:
            tags = [t.strip() for t in v.split(',') if t.strip()]
            if len(tags) > 20:
                raise ValueError('Maximum 20 tags allowed')
            if any(len(t) > 50 for t in tags):
                raise ValueError('Each tag must be less than 50 characters')
        return v


def read_csv():
    """Read all knowledge items from CSV with file locking"""
    if not os.path.exists(CSV_PATH):
        return []
    
    items = []
    with open(CSV_PATH, 'r', newline='', encoding='utf-8') as f:
        # Acquire shared lock for reading
        try:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
        except (AttributeError, ImportError):
            pass  # fcntl not available on Windows
        
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('id'):  # Skip empty rows
                items.append(dict(row))
        
        # Release lock
        try:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        except (AttributeError, ImportError):
            pass
    
    return items


def write_csv(items):
    """Write all knowledge items to CSV with file locking (atomic)"""
    fieldnames = ['id', 'title', 'content', 'type', 'tags', 'source', 'created_at', 'updated_at', 'vector_id']
    
    # Write to a temporary file first for atomic operation
    temp_path = CSV_PATH + '.tmp'
    
    with open(temp_path, 'w', newline='', encoding='utf-8') as f:
        # Acquire exclusive lock for writing
        try:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        except (AttributeError, ImportError):
            pass
        
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(items)
        
        # Release lock
        try:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        except (AttributeError, ImportError):
            pass
    
    # Atomic rename
    os.replace(temp_path, CSV_PATH)
    
    # Update stats
    update_stats(len(items))


def update_stats(count):
    """Update index.json stats"""
    if os.path.exists(INDEX_PATH):
        with open(INDEX_PATH, 'r') as f:
            data = json.load(f)
        data['stats']['total_items'] = count
        data['stats']['last_updated'] = datetime.now().isoformat()
        with open(INDEX_PATH, 'w') as f:
            json.dump(data, f, indent=2)


@router.get("/", response_model=List[KnowledgeItem])
async def get_all_knowledge(tag: Optional[str] = None, type: Optional[str] = None):
    """Get all knowledge items with optional filtering"""
    items = read_csv()
    
    if tag:
        items = [item for item in items if tag.lower() in item.get('tags', '').lower()]
    
    if type:
        items = [item for item in items if item.get('type') == type]
    
    # Sort by updated_at descending
    items.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
    
    return items


@router.get("/tags")
async def get_all_tags():
    """Get all unique tags"""
    items = read_csv()
    tags = set()
    for item in items:
        item_tags = item.get('tags', '').split(',')
        for tag in item_tags:
            tag = tag.strip()
            if tag:
                tags.add(tag)
    return sorted(list(tags))


@router.get("/stats")
async def get_stats():
    """Get knowledge base statistics"""
    items = read_csv()
    tags = set()
    for item in items:
        item_tags = item.get('tags', '').split(',')
        for tag in item_tags:
            if tag.strip():
                tags.add(tag.strip())
    
    return {
        "total_items": len(items),
        "total_tags": len(tags),
        "types": {
            "link": len([i for i in items if i.get('type') == 'link']),
            "code": len([i for i in items if i.get('type') == 'code']),
            "note": len([i for i in items if i.get('type') == 'note']),
            "image": len([i for i in items if i.get('type') == 'image']),
            "file": len([i for i in items if i.get('type') == 'file']),
        }
    }


@router.get("/{item_id}")
async def get_knowledge(item_id: str):
    """Get a single knowledge item by ID"""
    items = read_csv()
    for item in items:
        if item.get('id') == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")


@router.post("/")
@limiter.limit("30/minute")
async def create_knowledge(request: Request, item: KnowledgeCreate):
    """Create a new knowledge item"""
    items = read_csv()
    
    now = datetime.now().isoformat()
    new_item = {
        "id": str(uuid.uuid4())[:8],
        "title": item.title,
        "content": item.content,
        "type": item.type,
        "tags": item.tags,
        "source": item.source,
        "created_at": now,
        "updated_at": now,
        "vector_id": ""
    }
    
    items.append(new_item)
    write_csv(items)
    
    return new_item


@router.put("/{item_id}")
@limiter.limit("30/minute")
async def update_knowledge(request: Request, item_id: str, update: KnowledgeUpdate):
    """Update an existing knowledge item"""
    items = read_csv()
    
    for item in items:
        if item.get('id') == item_id:
            if update.title is not None:
                item['title'] = update.title
            if update.content is not None:
                item['content'] = update.content
            if update.type is not None:
                item['type'] = update.type
            if update.tags is not None:
                item['tags'] = update.tags
            if update.source is not None:
                item['source'] = update.source
            
            item['updated_at'] = datetime.now().isoformat()
            write_csv(items)
            return item
    
    raise HTTPException(status_code=404, detail="Item not found")


@router.delete("/{item_id}")
@limiter.limit("20/minute")
async def delete_knowledge(request: Request, item_id: str):
    """Delete a knowledge item"""
    items = read_csv()
    initial_count = len(items)
    
    items = [item for item in items if item.get('id') != item_id]
    
    if len(items) == initial_count:
        raise HTTPException(status_code=404, detail="Item not found")
    
    write_csv(items)
    return {"message": "Item deleted successfully", "id": item_id}


@router.post("/{item_id}/upload")
@limiter.limit("10/minute")
async def upload_attachment(request: Request, item_id: str, file: UploadFile = File(...)):
    """Upload a file attachment for a knowledge item with security validation"""
    items = read_csv()
    
    item = None
    for i in items:
        if i.get('id') == item_id:
            item = i
            break
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Validate file exists
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Read file content
    content = await file.read()
    
    # Validate file size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail=f"File too large. Maximum size is {MAX_FILE_SIZE / (1024*1024)}MB")
    
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"File type '{file_ext}' not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}")
    
    # Validate MIME type matches extension
    mime_type, _ = mimetypes.guess_type(file.filename)
    dangerous_mimes = {'application/x-msdownload', 'application/x-executable', 'application/x-sh'}
    if mime_type in dangerous_mimes:
        raise HTTPException(status_code=400, detail="Dangerous file type not allowed")
    
    # Generate safe filename (no original filename components)
    safe_filename = f"{item_id}_{uuid.uuid4().hex[:16]}{file_ext}"
    file_path = os.path.join(ATTACHMENTS_DIR, safe_filename)
    
    # Ensure path is within attachments directory (prevent path traversal)
    real_attachments_dir = os.path.realpath(ATTACHMENTS_DIR)
    real_file_path = os.path.realpath(file_path)
    if not real_file_path.startswith(real_attachments_dir):
        raise HTTPException(status_code=400, detail="Invalid file path")
    
    # Write file
    with open(file_path, "wb") as buffer:
        buffer.write(content)
    
    # Update item source to point to file
    item['source'] = f"/data/attachments/{safe_filename}"
    item['updated_at'] = datetime.now().isoformat()
    write_csv(items)
    
    return {
        "message": "File uploaded successfully",
        "filename": safe_filename,
        "path": f"/data/attachments/{safe_filename}",
        "size": len(content)
    }