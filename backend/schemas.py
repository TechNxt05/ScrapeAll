"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict
from datetime import datetime

# User schemas
class UserCreate(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Project schemas
class ProjectCreate(BaseModel):
    name: str
    url: str
    description: Optional[str] = None
    tags: Optional[List[str]] = []

class ProjectResponse(BaseModel):
    id: int
    name: str
    url: str
    description: Optional[str]
    tags: List[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Scrape schemas
class ScrapeRequest(BaseModel):
    url: str
    project_name: Optional[str] = None
    project_id: Optional[int] = None
    selector: Optional[str] = None

class ScrapeResponse(BaseModel):
    id: int
    project_id: int
    url: str
    status: str
    summary: Optional[str]
    key_points: Optional[List[str]]
    scrape_method: Optional[str]
    ai_provider: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Chat schemas
class ChatRequest(BaseModel):
    project_id: int
    message: str

class ChatResponse(BaseModel):
    response: str
    timestamp: datetime

# Form schemas
class FormDetectRequest(BaseModel):
    url: str

class FormFillRequest(BaseModel):
    url: str
    form_data: Dict[str, str]
    form_index: int = 0
    submit: bool = False

class FormResponse(BaseModel):
    success: bool
    message: str
    details: Optional[Dict] = None
