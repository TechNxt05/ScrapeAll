"""
Database models for ScrapeAll
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class ScrapeStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    url = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    tags = Column(JSON, default=list)  # List of tags
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="projects")
    scrapes = relationship("Scrape", back_populates="project", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="project", cascade="all, delete-orphan")
    form_submissions = relationship("FormSubmission", back_populates="project", cascade="all, delete-orphan")

class Scrape(Base):
    __tablename__ = "scrapes"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    url = Column(Text, nullable=False)
    raw_html = Column(Text, nullable=True)
    extracted_content = Column(JSON, nullable=True)  # Structured content
    summary = Column(Text, nullable=True)
    key_points = Column(JSON, default=list)  # List of key points
    entities = Column(JSON, default=dict)  # Extracted entities
    status = Column(Enum(ScrapeStatus), default=ScrapeStatus.PENDING)
    error_message = Column(Text, nullable=True)
    scrape_method = Column(String(50), nullable=True)  # static, selenium, playwright
    ai_provider = Column(String(50), nullable=True)  # groq, gemini, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="scrapes")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    role = Column(String(20), nullable=False)  # user or assistant
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="chat_messages")

class FormSubmission(Base):
    __tablename__ = "form_submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    form_url = Column(Text, nullable=False)
    form_fields = Column(JSON, nullable=True)  # Detected form fields
    form_data = Column(JSON, nullable=True)  # User-provided data
    status = Column(String(50), nullable=True)  # success, failed, partial
    result = Column(Text, nullable=True)  # Result message
    screenshot_path = Column(String(500), nullable=True)  # Path to screenshot
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="form_submissions")
