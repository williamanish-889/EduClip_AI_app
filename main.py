"""
EduClip AI - FastAPI Backend Implementation
Complete backend API for video processing and AI analysis
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict
import os
import uuid
import logging
from datetime import datetime, timedelta
import jwt
import bcrypt
from pathlib import Path
import json
import asyncio
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="EduClip AI API",
    description="AI-Enhanced Video Editing and Summarization for Educational Content",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="."), name="static")

# Security
security = HTTPBearer()
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# File storage paths
UPLOAD_DIR = Path("./storage/uploads")
CLIPS_DIR = Path("./storage/clips")
THUMBNAILS_DIR = Path("./storage/thumbnails")

# Create directories
for directory in [UPLOAD_DIR, CLIPS_DIR, THUMBNAILS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# ============= Models =============

class UserRole(str, Enum):
    EDUCATOR = "educator"
    STUDENT = "student"
    ADMIN = "admin"

class VideoStatus(str, Enum):
    UPLOADING = "uploading"
    PROCESSING = "processing"
    TRANSCRIBING = "transcribing"
    ANALYZING = "analyzing"
    GENERATING_CLIPS = "generating_clips"
    COMPLETE = "complete"
    FAILED = "failed"

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.STUDENT

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class VideoMetadata(BaseModel):
    title: str
    description: Optional[str] = None
    tags: Optional[List[str]] = []

class VideoResponse(BaseModel):
    video_id: str
    title: str
    status: VideoStatus
    progress: int
    uploaded_at: str
    duration: Optional[float] = None

class TranscriptSegment(BaseModel):
    id: int
    start: float
    end: float
    text: str
    confidence: float

class TranscriptResponse(BaseModel):
    video_id: str
    full_text: str
    segments: List[TranscriptSegment]
    duration: float
    language: str

class Summary(BaseModel):
    executive_summary: str
    key_concepts: List[Dict]
    learning_objectives: List[str]
    topics: List[Dict]
    difficulty_level: str

class ClipInfo(BaseModel):
    clip_id: str
    title: str
    start_time: float
    end_time: float
    duration: float
    importance_score: float
    thumbnail_url: str
    download_url: str

class AnalyticsResponse(BaseModel):
    user_id: str
    total_videos_watched: int
    total_watch_time: int
    topics_covered: List[str]
    average_completion_rate: float
    recent_activity: List[Dict]

# ============= Database Simulation (Replace with actual DB) =============

# In production, use proper database (PostgreSQL, MySQL)
users_db = {}
videos_db = {}
transcripts_db = {}
summaries_db = {}
clips_db = {}
analytics_db = {}

# ============= Authentication =============

def create_access_token(data: dict):
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ============= Authentication Endpoints =============

@app.post("/api/auth/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserRegister):
    """Register new user"""
    
    # Check if email already exists
    if user.email in [u["email"] for u in users_db.values()]:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    password_hash = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    
    # Create user
    user_id = str(uuid.uuid4())
    users_db[user_id] = {
        "user_id": user_id,
        "username": user.username,
        "email": user.email,
        "password_hash": password_hash,
        "role": user.role,
        "created_at": datetime.utcnow().isoformat()
    }
    
    # Generate token
    token = create_access_token({"sub": user_id})
    
    return {
        "success": True,
        "message": "User registered successfully",
        "data": {
            "user_id": user_id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "token": token
        }
    }

@app.post("/api/auth/login")
async def login(credentials: UserLogin):
    """User login"""
    
    # Find user by email
    user = next((u for u in users_db.values() if u["email"] == credentials.email), None)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Verify password
    if not bcrypt.checkpw(credentials.password.encode('utf-8'), user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Generate token
    token = create_access_token({"sub": user["user_id"]})
    
    return {
        "success": True,
        "message": "Login successful",
        "data": {
            "user_id": user["user_id"],
            "username": user["username"],
            "email": user["email"],
            "role": user["role"],
            "token": token
        }
    }

# ============= Video Endpoints =============

@app.post("/api/videos/upload")
async def upload_video(
    file: UploadFile = File(...),
    title: str = None,
    description: str = None,
    user_id: str = Depends(verify_token)
):
    """Upload video file"""
    
    # Validate file type
    if not file.content_type.startswith('video/'):
        raise HTTPException(status_code=400, detail="File must be a video")
    
    # Generate unique video ID
    video_id = str(uuid.uuid4())
    
    # Save file
    file_extension = os.path.splitext(file.filename)[1]
    file_path = UPLOAD_DIR / f"{video_id}{file_extension}"
    
    try:
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Create video record
        videos_db[video_id] = {
            "video_id": video_id,
            "user_id": user_id,
            "title": title or file.filename,
            "description": description,
            "file_path": str(file_path),
            "status": VideoStatus.PROCESSING,
            "progress": 0,
            "uploaded_at": datetime.utcnow().isoformat(),
            "file_size": len(content)
        }
        
        # Start processing in background (in production, use Celery or similar)
        asyncio.create_task(process_video(video_id))
        
        logger.info(f"Video uploaded: {video_id}")
        
        return {
            "success": True,
            "message": "Video uploaded successfully",
            "data": {
                "video_id": video_id,
                "status": VideoStatus.PROCESSING,
                "title": title or file.filename
            }
        }
        
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail="Upload failed")

@app.get("/api/videos/{video_id}/status")
async def get_video_status(video_id: str, user_id: str = Depends(verify_token)):
    """Get video processing status"""
    
    if video_id not in videos_db:
        raise HTTPException(status_code=404, detail="Video not found")
    
    video = videos_db[video_id]
    
    return {
        "success": True,
        "data": {
            "video_id": video_id,
            "status": video["status"],
            "progress": video["progress"],
            "title": video["title"]
        }
    }

@app.get("/api/videos/{video_id}/transcript")
async def get_transcript(video_id: str, user_id: str = Depends(verify_token)):
    """Get video transcript"""
    
    if video_id not in transcripts_db:
        raise HTTPException(status_code=404, detail="Transcript not available")
    
    transcript = transcripts_db[video_id]
    
    return {
        "success": True,
        "data": transcript
    }

@app.get("/api/videos/{video_id}/summary")
async def get_summary(video_id: str, user_id: str = Depends(verify_token)):
    """Get video summary"""
    
    if video_id not in summaries_db:
        raise HTTPException(status_code=404, detail="Summary not available")
    
    summary = summaries_db[video_id]
    
    return {
        "success": True,
        "data": summary
    }

@app.get("/api/videos/{video_id}/clips")
async def get_clips(video_id: str, user_id: str = Depends(verify_token)):
    """Get generated clips"""
    
    clips = [clip for clip in clips_db.values() if clip["video_id"] == video_id]
    
    return {
        "success": True,
        "data": {
            "video_id": video_id,
            "clips": clips,
            "count": len(clips)
        }
    }

@app.get("/api/videos")
async def list_videos(user_id: str = Depends(verify_token)):
    """List user's videos"""
    
    user_videos = [v for v in videos_db.values() if v["user_id"] == user_id]
    
    return {
        "success": True,
        "data": {
            "videos": user_videos,
            "count": len(user_videos)
        }
    }

# ============= Analytics Endpoints =============

@app.get("/api/analytics/user/{target_user_id}")
async def get_user_analytics(
    target_user_id: str,
    user_id: str = Depends(verify_token)
):
    """Get user analytics"""
    
    # In production, check permissions
    if user_id != target_user_id and users_db[user_id]["role"] != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    # Calculate analytics
    user_analytics = analytics_db.get(target_user_id, {
        "user_id": target_user_id,
        "total_videos_watched": 0,
        "total_watch_time": 0,
        "topics_covered": [],
        "average_completion_rate": 0.0,
        "recent_activity": []
    })
    
    return {
        "success": True,
        "data": user_analytics
    }

@app.get("/api/analytics/video/{video_id}")
async def get_video_analytics(video_id: str, user_id: str = Depends(verify_token)):
    """Get video-specific analytics"""
    
    if video_id not in videos_db:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Calculate video analytics
    analytics = {
        "video_id": video_id,
        "total_views": 0,
        "unique_viewers": 0,
        "average_watch_time": 0,
        "completion_rate": 0.0,
        "clip_engagement": {},
        "peak_engagement_times": []
    }
    
    return {
        "success": True,
        "data": analytics
    }

# ============= Background Processing =============

async def process_video(video_id: str):
    """Background video processing pipeline"""
    
    try:
        video = videos_db[video_id]
        
        # Step 1: Update status
        video["status"] = VideoStatus.TRANSCRIBING
        video["progress"] = 10
        
        # Simulate processing (replace with actual processing)
        await asyncio.sleep(2)
        
        # Step 2: Transcription (call Whisper module)
        logger.info(f"Transcribing video: {video_id}")
        video["progress"] = 30
        
        # Create dummy transcript
        transcripts_db[video_id] = {
            "video_id": video_id,
            "full_text": "Sample transcript...",
            "segments": [],
            "duration": 600.0,
            "language": "en"
        }
        
        await asyncio.sleep(2)
        
        # Step 3: Analyzing
        video["status"] = VideoStatus.ANALYZING
        video["progress"] = 60
        logger.info(f"Analyzing video: {video_id}")
        
        # Create dummy summary
        summaries_db[video_id] = {
            "video_id": video_id,
            "executive_summary": "This lecture covers...",
            "key_concepts": [],
            "learning_objectives": [],
            "topics": [],
            "difficulty_level": "intermediate"
        }
        
        await asyncio.sleep(2)
        
        # Step 4: Generate clips
        video["status"] = VideoStatus.GENERATING_CLIPS
        video["progress"] = 80
        logger.info(f"Generating clips: {video_id}")
        
        await asyncio.sleep(2)
        
        # Step 5: Complete
        video["status"] = VideoStatus.COMPLETE
        video["progress"] = 100
        logger.info(f"Processing complete: {video_id}")
        
    except Exception as e:
        logger.error(f"Processing error for {video_id}: {str(e)}")
        video["status"] = VideoStatus.FAILED
        video["progress"] = 0

# ============= Health Check =============


@app.get("/")
async def serve_index():
    """Serve the index.html frontend application"""
    return FileResponse("index.html")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

# ============= Error Handlers =============

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "error": str(exc)
        }
    )

