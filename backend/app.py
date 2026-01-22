"""
Main FastAPI application
"""
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from backend.config import settings
from backend.database.db import get_db, init_db
from backend.database.models import User, Project, Scrape, ChatMessage, FormSubmission, ScrapeStatus
from backend.schemas import (
    UserCreate, UserLogin, UserResponse,
    ProjectCreate, ProjectResponse,
    ScrapeRequest, ScrapeResponse,
    ChatRequest, ChatResponse,
    FormDetectRequest, FormFillRequest, FormResponse
)
from backend.auth import get_password_hash, verify_password, create_access_token, get_current_user, get_optional_user
from backend.scrapers.smart_scraper import smart_scraper
from backend.ai.content_extractor import content_extractor
from backend.ai.chat_engine import chat_engine
from backend.ai.form_analyzer import form_analyzer
from backend.ai.ai_provider import ai_provider

# Create FastAPI app
app = FastAPI(
    title="ScrapeAll API",
    description="Advanced web scraping platform with AI-powered content extraction",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL, 
        "https://scrape-all.vercel.app",
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()
    print("🚀 ScrapeAll API started on Port 8001")
    print(f"🤖 Active AI provider: {ai_provider.get_active_provider()}")
    
    # DEBUG: Print all registered routes
    print("🛣️  Registered Routes:")
    for route in app.routes:
        print(f"   - {route.path} [{','.join(route.methods)}]")

    # Seed default user if not exists
    db = next(get_db())
    try:
        if not db.query(User).filter(User.id == 1).first():
            print("👤 Creating default user (id=1)...")
            default_user = User(
                email="user@example.com",
                password_hash=get_password_hash("password")
            )
            db.add(default_user)
            db.commit()
            print("✅ Default user created: user@example.com / password")
    except Exception as e:
        print(f"⚠️ Failed to seed default user: {e}")
    finally:
        db.close()

# Health check
@app.get("/")
async def root():
    return {
        "message": "ScrapeAll API",
        "version": "1.0.0",
        "ai_provider": ai_provider.get_active_provider(),
        "status": "running"
    }

# ==================== AUTH ROUTES ====================

@app.post("/api/auth/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    user = User(email=user_data.email, password_hash=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user

@app.post("/api/auth/login")
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Login user"""
    user = db.query(User).filter(User.email == user_data.email).first()
    
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create access token
    access_token = create_access_token(data={"sub": user.email, "user_id": user.id})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.from_orm(user)
    }

# ==================== PROJECT ROUTES ====================

@app.post("/api/projects", response_model=ProjectResponse)
async def create_project(
    project_data: ProjectCreate, 
    user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Create a new project"""
    project = Project(**project_data.dict())
    project.user_id = user.id
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

@app.get("/api/projects", response_model=List[ProjectResponse])
async def get_projects(
    user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Get all projects for current user"""
    projects = db.query(Project).filter(Project.user_id == user.id).order_by(Project.updated_at.desc()).all()
    return projects

@app.get("/api/projects/{project_id}/latest-scrape")
async def get_latest_scrape(
    project_id: int, 
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the latest scrape for a project"""
    # Verify project ownership
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    scrape = db.query(Scrape).filter(Scrape.project_id == project_id).order_by(Scrape.created_at.desc()).first()
    if not scrape:
        return None
        
    return {
        "id": scrape.id,
        "project_id": scrape.project_id,
        "url": scrape.url,
        "status": scrape.status,
        "summary": scrape.summary,
        "key_points": scrape.key_points,
        "entities": scrape.extracted_content.get('entities') if scrape.extracted_content else None,
        "topics": scrape.extracted_content.get('topics') if scrape.extracted_content else None,
        "scrape_method": scrape.scrape_method,
        "ai_provider": scrape.ai_provider,
        "error_message": scrape.error_message,
        "created_at": scrape.created_at
    }

@app.get("/api/projects/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int, 
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific project"""
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@app.delete("/api/projects/{project_id}")
async def delete_project(
    project_id: int, 
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a project"""
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Clear chat data
    chat_engine.clear_project_data(project_id)
    
    # Delete project (cascades to scrapes, messages, etc.)
    db.delete(project)
    db.commit()
    
    return {"message": "Project deleted successfully"}

# ==================== SCRAPE ROUTES ====================

@app.post("/api/scrape")
async def scrape_url(
    scrape_data: ScrapeRequest, 
    user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Scrape a URL and extract content"""
    
    # Determine user ID (1 for anonymous/guest, actual ID for logged in)
    user_id = user.id if user else 1
    
    project = None
    
    # 1. Add to existing project (Multi-Source RAG)
    if scrape_data.project_id:
        # Verify ownership
        project = db.query(Project).filter(Project.id == scrape_data.project_id, Project.user_id == user_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found or access denied")
        print(f"➕ Adding source to existing project: {project.name} (ID: {project.id})")
        
    # 2. Create new project
    else:
        project_name = scrape_data.project_name or f"Scrape {scrape_data.url[:50]}"
        project = Project(
            name=project_name,
            url=scrape_data.url,
            user_id=user_id
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        print(f"🆕 Created new project: {project.name} (ID: {project.id})")
    
    # Create scrape record
    scrape = Scrape(
        project_id=project.id,
        url=scrape_data.url,
        status=ScrapeStatus.IN_PROGRESS
    )
    db.add(scrape)
    db.commit()
    db.refresh(scrape)
    
    try:
        # Scrape the URL
        print(f"🔍 Scraping: {scrape_data.url} {f'[Selector: {scrape_data.selector}]' if scrape_data.selector else ''}")
        result = smart_scraper.scrape(scrape_data.url, scrape_data.selector)
        
        if not result.success:
            # Scraping failed
            scrape.status = ScrapeStatus.FAILED
            scrape.error_message = result.error
            scrape.scrape_method = result.method
            db.commit()
            
            return {
                "success": False,
                "project_id": project.id,
                "scrape_id": scrape.id,
                "error": result.error
            }
        
        # Scraping succeeded - extract content with AI
        print(f"✅ Scraped successfully with {result.method}")
        print(f"🤖 Extracting content with AI...")
        
        extracted = content_extractor.extract_content(
            text=result.text,
            url=scrape_data.url,
            title=result.title
        )
        
        # Update scrape record
        scrape.raw_html = result.html
        scrape.extracted_content = extracted
        scrape.summary = extracted['summary']
        scrape.key_points = extracted['key_points']
        scrape.status = ScrapeStatus.COMPLETED
        scrape.scrape_method = result.method
        scrape.ai_provider = ai_provider.get_active_provider()
        
        db.commit()
        db.refresh(scrape)
        
        # Add content to chat engine for RAG
        print(f"💾 Adding content to vector database...")
        chat_engine.add_content(
            project_id=project.id,
            content=result.text,
            metadata={
                'url': scrape_data.url,
                'title': result.title,
                'scrape_id': scrape.id
            }
        )
        
        print(f"✅ Scrape completed successfully!")
        
        return {
            "success": True,
            "project_id": project.id,
            "scrape_id": scrape.id,
            "summary": extracted['summary'],
            "key_points": extracted['key_points'],
            "entities": extracted['entities'],
            "topics": extracted['topics'],
            "scrape_method": result.method,
            "ai_provider": ai_provider.get_active_provider()
        }
        
    except Exception as e:
        scrape.status = ScrapeStatus.FAILED
        scrape.error_message = str(e)
        db.commit()
        
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

@app.get("/api/scrapes/{scrape_id}")
async def get_scrape(scrape_id: int, db: Session = Depends(get_db)):
    """Get scrape details"""
    scrape = db.query(Scrape).filter(Scrape.id == scrape_id).first()
    if not scrape:
        raise HTTPException(status_code=404, detail="Scrape not found")
    
    return {
        "id": scrape.id,
        "project_id": scrape.project_id,
        "url": scrape.url,
        "status": scrape.status,
        "summary": scrape.summary,
        "key_points": scrape.key_points,
        "entities": scrape.extracted_content.get('entities') if scrape.extracted_content else None,
        "topics": scrape.extracted_content.get('topics') if scrape.extracted_content else None,
        "scrape_method": scrape.scrape_method,
        "ai_provider": scrape.ai_provider,
        "error_message": scrape.error_message,
        "created_at": scrape.created_at
    }

# ==================== CHAT ROUTES ====================

@app.post("/api/chat", response_model=ChatResponse)
async def chat(chat_data: ChatRequest, db: Session = Depends(get_db)):
    """Chat with scraped content"""
    
    # Verify project exists
    project = db.query(Project).filter(Project.id == chat_data.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get conversation history
    messages = db.query(ChatMessage).filter(
        ChatMessage.project_id == chat_data.project_id
    ).order_by(ChatMessage.created_at.desc()).limit(10).all()
    
    conversation_history = [
        {"role": msg.role, "content": msg.content}
        for msg in reversed(messages)
    ]
    
    # Save user message
    user_message = ChatMessage(
        project_id=chat_data.project_id,
        role="user",
        content=chat_data.message
    )
    db.add(user_message)
    db.commit()
    
    # Get AI response
    response = chat_engine.chat(
        project_id=chat_data.project_id,
        question=chat_data.message,
        conversation_history=conversation_history
    )
    
    # Save assistant message
    assistant_message = ChatMessage(
        project_id=chat_data.project_id,
        role="assistant",
        content=response
    )
    db.add(assistant_message)
    db.commit()
    
    return ChatResponse(
        response=response,
        timestamp=datetime.utcnow()
    )

@app.get("/api/chat/{project_id}/history")
async def get_chat_history(project_id: int, db: Session = Depends(get_db)):
    """Get chat history for a project"""
    messages = db.query(ChatMessage).filter(
        ChatMessage.project_id == project_id
    ).order_by(ChatMessage.created_at.asc()).all()
    
    return [
        {
            "id": msg.id,
            "role": msg.role,
            "content": msg.content,
            "created_at": msg.created_at
        }
        for msg in messages
    ]

# ==================== FORM ROUTES ====================

@app.post("/api/forms/detect", response_model=FormResponse)
async def detect_forms(form_data: FormDetectRequest):
    """Detect forms on a webpage"""
    result = form_analyzer.detect_forms(form_data.url)
    
    if result['success']:
        return FormResponse(
            success=True,
            message=f"Found {result['total_forms']} form(s)",
            details=result
        )
    else:
        return FormResponse(
            success=False,
            message=result['error'],
            details=result
        )

@app.post("/api/forms/fill", response_model=FormResponse)
async def fill_form(
    form_data: FormFillRequest,
    db: Session = Depends(get_db)
):
    """Fill a form on a webpage"""
    
    result = form_analyzer.fill_form(
        url=form_data.url,
        form_data=form_data.form_data,
        form_index=form_data.form_index,
        submit=form_data.submit
    )
    
    # Save to database
    # TODO: Link to project
    submission = FormSubmission(
        project_id=1,  # TODO: Get from context
        form_url=form_data.url,
        form_data=form_data.form_data,
        status="success" if result['success'] else "failed",
        result=str(result)
    )
    db.add(submission)
    db.commit()
    
    if result['success']:
        return FormResponse(
            success=True,
            message=result['message'],
            details=result
        )
    else:
        return FormResponse(
            success=False,
            message=result['error'],
            details=result
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
