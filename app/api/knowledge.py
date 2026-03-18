"""
Knowledge API Routes - CRUD Operations
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import csv
import os
import json
import uuid
import shutil

router = APIRouter()

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")
CSV_PATH = os.path.join(DATA_DIR, "knowledge.csv")
ATTACHMENTS_DIR = os.path.join(DATA_DIR, "attachments")
INDEX_PATH = os.path.join(DATA_DIR, "index.json")

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
    title: str
    content: str
    type: str
    tags: str = ""
    source: str = ""


class KnowledgeUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    type: Optional[str] = None
    tags: Optional[str] = None
    source: Optional[str] = None


def read_csv():
    """Read all knowledge items from CSV"""
    if not os.path.exists(CSV_PATH):
        return []
    
    items = []
    with open(CSV_PATH, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('id'):  # Skip empty rows
                items.append(dict(row))
    return items


def write_csv(items):
    """Write all knowledge items to CSV"""
    fieldnames = ['id', 'title', 'content', 'type', 'tags', 'source', 'created_at', 'updated_at', 'vector_id']
    
    with open(CSV_PATH, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(items)
    
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
async def create_knowledge(item: KnowledgeCreate):
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
async def update_knowledge(item_id: str, update: KnowledgeUpdate):
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
async def delete_knowledge(item_id: str):
    """Delete a knowledge item"""
    items = read_csv()
    initial_count = len(items)
    
    items = [item for item in items if item.get('id') != item_id]
    
    if len(items) == initial_count:
        raise HTTPException(status_code=404, detail="Item not found")
    
    write_csv(items)
    return {"message": "Item deleted successfully", "id": item_id}


@router.post("/{item_id}/upload")
async def upload_attachment(item_id: str, file: UploadFile = File(...)):
    """Upload a file attachment for a knowledge item"""
    items = read_csv()
    
    item = None
    for i in items:
        if i.get('id') == item_id:
            item = i
            break
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Save file
    file_ext = os.path.splitext(file.filename)[1]
    safe_filename = f"{item_id}_{uuid.uuid4().hex[:8]}{file_ext}"
    file_path = os.path.join(ATTACHMENTS_DIR, safe_filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Update item source to point to file
    item['source'] = f"/data/attachments/{safe_filename}"
    item['updated_at'] = datetime.now().isoformat()
    write_csv(items)
    
    return {
        "message": "File uploaded successfully",
        "filename": safe_filename,
        "path": f"/data/attachments/{safe_filename}"
    }