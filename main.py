"""
EduClip AI - FastAPI Backend Implementation - FIXED FOR RENDER
Complete backend API with proper CORS, error handling, and logging
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
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

# Configure logging with more detail
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="EduClip AI API",
    description="AI-Enhanced Video Editing and Summarization for Educational Content",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ✅ FIXED: Proper CORS configuration for Render
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Security
security = HTTPBearer(auto_error=False)
SECRET_KEY = os.getenv("SECRET_KEY", "educlip-secret-key-" + str(uuid.uuid4()))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# ✅ FIXED: Use /tmp for Render (ephemeral storage)
BASE_DIR = Path("/tmp") if os.getenv("RENDER") else Path("./storage")
UPLOAD_DIR = BASE_DIR / "uploads"
CLIPS_DIR = BASE_DIR / "clips"
THUMBNAILS_DIR = BASE_DIR / "thumbnails"

# Create directories
for directory in [UPLOAD_DIR, CLIPS_DIR, THUMBNAILS_DIR]:
    try:
        directory.mkdir(parents=True, exist_ok=True)
        logger.info(f"✓ Directory created: {directory}")
    except Exception as e:
        logger.warning(f"Directory creation warning: {e}")

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

# ============= In-Memory Database =============
users_db = {}
videos_db = {}
transcripts_db = {}
summaries_db = {}
clips_db = {}
analytics_db = {}

# ============= Helper Functions =============

def create_access_token(data: dict):
    """Create JWT access token"""
    try:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        logger.error(f"Token creation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create authentication token")

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token"""
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError as e:
        logger.error(f"JWT verification error: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        raise HTTPException(status_code=401, detail="Authentication failed")

# ============= Root & Health Endpoints =============

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "EduClip AI API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
        "health": "/health",
        "message": "Welcome to EduClip AI - AI-Enhanced Educational Video Platform"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": "render" if os.getenv("RENDER") else "local",
        "users_count": len(users_db),
        "videos_count": len(videos_db),
        "python_version": "3.9+"
    }

# ============= Authentication Endpoints =============

@app.post("/api/auth/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserRegister):
    """Register new user - FIXED VERSION"""
    try:
        logger.info(f"📝 Registration attempt - Email: {user.email}, Username: {user.username}")
        
        # ✅ FIXED: Better validation
        if not user.username or len(user.username) < 3:
            logger.warning(f"Invalid username length: {len(user.username) if user.username else 0}")
            raise HTTPException(status_code=400, detail="Username must be at least 3 characters long")
        
        if not user.email:
            raise HTTPException(status_code=400, detail="Email address is required")
        
        if not user.password or len(user.password) < 6:
            logger.warning("Invalid password length")
            raise HTTPException(status_code=400, detail="Password must be at least 6 characters long")
        
        # Check if email already exists
        existing_user = next((u for u in users_db.values() if u["email"] == user.email), None)
        if existing_user:
            logger.warning(f"Email already registered: {user.email}")
            raise HTTPException(status_code=400, detail="This email is already registered")
        
        # Check if username already exists
        existing_username = next((u for u in users_db.values() if u["username"] == user.username), None)
        if existing_username:
            logger.warning(f"Username already taken: {user.username}")
            raise HTTPException(status_code=400, detail="This username is already taken")
        
        # Hash password
        password_hash = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
        
        # Create user
        user_id = str(uuid.uuid4())
        users_db[user_id] = {
            "user_id": user_id,
            "username": user.username,
            "email": user.email,
            "password_hash": password_hash,
            "role": user.role.value if isinstance(user.role, Enum) else user.role,
            "created_at": datetime.utcnow().isoformat(),
            "last_login": None
        }
        
        logger.info(f"✅ User registered successfully - ID: {user_id}, Email: {user.email}")
        
        # Generate token
        token = create_access_token({"sub": user_id})
        
        return {
            "success": True,
            "message": "Registration successful! Welcome to EduClip AI",
            "data": {
                "user_id": user_id,
                "username": user.username,
                "email": user.email,
                "role": user.role.value if isinstance(user.role, Enum) else user.role,
                "token": token
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Registration error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Registration failed: {str(e)}"
        )

@app.post("/api/auth/login")
async def login(credentials: UserLogin):
    """User login - FIXED VERSION"""
    try:
        logger.info(f"🔐 Login attempt - Email: {credentials.email}")
        
        # Validate input
        if not credentials.email:
            raise HTTPException(status_code=400, detail="Email is required")
        
        if not credentials.password:
            raise HTTPException(status_code=400, detail="Password is required")
        
        # Find user by email
        user = next((u for u in users_db.values() if u["email"] == credentials.email), None)
        
        if not user:
            logger.warning(f"❌ User not found: {credentials.email}")
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Verify password
        if not bcrypt.checkpw(credentials.password.encode('utf-8'), user["password_hash"]):
            logger.warning(f"❌ Invalid password for: {credentials.email}")
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Update last login
        user["last_login"] = datetime.utcnow().isoformat()
        
        logger.info(f"✅ Login successful - Email: {credentials.email}")
        
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
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Login error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Login failed: {str(e)}"
        )

# ============= Video Endpoints =============

@app.post("/api/videos/upload")
async def upload_video(
    file: UploadFile = File(...),
    title: str = None,
    description: str = None,
    user_id: str = Depends(verify_token)
):
    """Upload video file"""
    try:
        logger.info(f"📤 Video upload started - User: {user_id}, File: {file.filename}")
        
        # Validate file type
        if not file.content_type or not file.content_type.startswith('video/'):
            raise HTTPException(status_code=400, detail="File must be a video")
        
        if not title:
            title = file.filename
        
        # Generate unique video ID
        video_id = str(uuid.uuid4())
        
        # Save file
        file_extension = os.path.splitext(file.filename)[1]
        file_path = UPLOAD_DIR / f"{video_id}{file_extension}"
        
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        logger.info(f"✅ Video saved: {file_path} ({len(content)} bytes)")
        
        # Create video record
        videos_db[video_id] = {
            "video_id": video_id,
            "user_id": user_id,
            "title": title,
            "description": description or "",
            "file_path": str(file_path),
            "status": VideoStatus.PROCESSING.value,
            "progress": 0,
            "uploaded_at": datetime.utcnow().isoformat(),
            "file_size": len(content)
        }
        
        # Start processing in background
        asyncio.create_task(process_video(video_id))
        
        return {
            "success": True,
            "message": "Video uploaded successfully",
            "data": {
                "video_id": video_id,
                "status": VideoStatus.PROCESSING.value,
                "title": title
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Upload error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/api/videos/{video_id}/status")
async def get_video_status(video_id: str, user_id: str = Depends(verify_token)):
    """Get video processing status"""
    try:
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
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Status check error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get video status")

@app.get("/api/videos/{video_id}/transcript")
async def get_transcript(video_id: str, user_id: str = Depends(verify_token)):
    """Get video transcript"""
    if video_id not in transcripts_db:
        raise HTTPException(status_code=404, detail="Transcript not available yet")
    
    return {"success": True, "data": transcripts_db[video_id]}

@app.get("/api/videos/{video_id}/summary")
async def get_summary(video_id: str, user_id: str = Depends(verify_token)):
    """Get video summary"""
    if video_id not in summaries_db:
        raise HTTPException(status_code=404, detail="Summary not available yet")
    
    return {"success": True, "data": summaries_db[video_id]}

@app.get("/api/videos/{video_id}/clips")
async def get_clips(video_id: str, user_id: str = Depends(verify_token)):
    """Get generated clips"""
    clips = [clip for clip in clips_db.values() if clip["video_id"] == video_id]
    return {"success": True, "data": {"video_id": video_id, "clips": clips, "count": len(clips)}}

@app.get("/api/videos")
async def list_videos(user_id: str = Depends(verify_token)):
    """List user's videos"""
    user_videos = [v for v in videos_db.values() if v["user_id"] == user_id]
    return {"success": True, "data": {"videos": user_videos, "count": len(user_videos)}}

# ============= Analytics Endpoints =============

@app.get("/api/analytics/user/{target_user_id}")
async def get_user_analytics(target_user_id: str, user_id: str = Depends(verify_token)):
    """Get user analytics"""
    if user_id != target_user_id and users_db.get(user_id, {}).get("role") != "admin":
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    analytics = analytics_db.get(target_user_id, {
        "user_id": target_user_id,
        "total_videos_watched": 0,
        "total_watch_time": 0,
        "topics_covered": [],
        "average_completion_rate": 0.0,
        "recent_activity": []
    })
    
    return {"success": True, "data": analytics}

@app.get("/api/analytics/video/{video_id}")
async def get_video_analytics(video_id: str, user_id: str = Depends(verify_token)):
    """Get video analytics"""
    if video_id not in videos_db:
        raise HTTPException(status_code=404, detail="Video not found")
    
    return {
        "success": True,
        "data": {
            "video_id": video_id,
            "total_views": 0,
            "unique_viewers": 0,
            "average_watch_time": 0,
            "completion_rate": 0.0
        }
    }

# ============= Background Processing =============

async def process_video(video_id: str):
    """Background video processing"""
    try:
        video = videos_db.get(video_id)
        if not video:
            return
        
        logger.info(f"🔄 Processing started: {video_id}")
        
        stages = [
            ("transcribing", 30, "Transcribing audio..."),
            ("analyzing", 60, "Analyzing content..."),
            ("generating_clips", 80, "Generating clips..."),
            ("complete", 100, "Processing complete!")
        ]
        
        for stage, progress, message in stages:
            await asyncio.sleep(2)
            video["status"] = stage
            video["progress"] = progress
            logger.info(f"📊 {video_id}: {message} ({progress}%)")
        
        # Create dummy data
        transcripts_db[video_id] = {
            "video_id": video_id,
            "full_text": "Sample educational transcript...",
            "segments": [],
            "duration": 600.0,
            "language": "en"
        }
        
        summaries_db[video_id] = {
            "video_id": video_id,
            "executive_summary": "Educational content summary...",
            "key_concepts": [],
            "learning_objectives": [],
            "topics": [],
            "difficulty_level": "intermediate"
        }
        
        logger.info(f"✅ Processing complete: {video_id}")
        
    except Exception as e:
        logger.error(f"❌ Processing error {video_id}: {str(e)}")
        if video_id in videos_db:
            videos_db[video_id]["status"] = "failed"

# ============= Error Handlers =============

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    logger.warning(f"HTTP {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle all other exceptions"""
    logger.error(f"❌ Unhandled error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "error": str(exc)
        }
    )

# ============= Startup Event =============

@app.on_event("startup")
async def startup_event():
    """Log startup information"""
    logger.info("=" * 60)
    logger.info("🚀 EduClip AI Backend Starting...")
    logger.info(f"📍 Environment: {os.getenv('RENDER', 'local')}")
    logger.info(f"📁 Storage: {BASE_DIR}")
    logger.info(f"🔒 CORS: Enabled (all origins)")
    logger.info(f"📚 Docs: /docs")
    logger.info("=" * 60)

# For local development
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
