# 🎓 EduClip AI

## AI-Enhanced Video Editing and Summarization for Educational Content Creators

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

EduClip AI is an intelligent video processing platform that transforms lengthy educational videos into concise, searchable, and accessible learning materials using cutting-edge AI technologies.

## 🌟 Features

### Core Functionality
- **Automated Speech-to-Text**: High-accuracy transcription using OpenAI Whisper
- **Intelligent Summarization**: AI-powered content analysis using Gemini/GPT
- **Smart Highlight Detection**: Automatic identification of key educational moments
- **Clip Generation**: Creates short, focused video segments automatically
- **Learning Analytics**: Comprehensive tracking of student engagement and progress
- **Topic Segmentation**: Breaks down lectures into logical sections

### Technical Features
- RESTful API with FastAPI
- Asynchronous video processing
- SQL database for structured data
- JWT-based authentication
- Role-based access control (Educator/Student/Admin)
- Responsive web interface
- Scalable architecture

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend Layer                          │
│         HTML5 + CSS3 + JavaScript (Vanilla/React)           │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                      API Layer                               │
│              FastAPI RESTful Endpoints                       │
│         Authentication │ Validation │ Rate Limiting          │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                  AI Processing Layer                         │
│   ┌─────────────┐  ┌──────────────┐  ┌─────────────┐       │
│   │   Whisper   │  │  Gemini/GPT  │  │   Custom    │       │
│   │     ASR     │  │     LLM      │  │     NLP     │       │
│   └─────────────┘  └──────────────┘  └─────────────┘       │
│   ┌──────────────────────────────────────────────────┐      │
│   │          FFmpeg Video Processing                 │      │
│   └──────────────────────────────────────────────────┘      │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                     Data Layer                               │
│    SQL Database    │    File Storage    │    Analytics      │
└──────────────────────────────────────────────────────────────┘
```

## 📋 Prerequisites

### Software Requirements
- Python 3.8 or higher
- FFmpeg 4.0 or higher
- PostgreSQL 12+ or MySQL 8+ (for production)
- Node.js 14+ (optional, for frontend build tools)

### API Keys Required
- OpenAI API key (for Whisper - optional, can run locally)
- Google Gemini API key or OpenAI GPT API key

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/educlip-ai.git
cd educlip-ai
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r code/requirements.txt
```

### 4. Install FFmpeg
**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html)

### 5. Setup Database
```bash
# Create database
createdb educlip_db

# Run schema
psql -d educlip_db -f code/database/schema.sql
```

### 6. Configure Environment Variables
Create `.env` file:
```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:password@localhost/educlip_db
GEMINI_API_KEY=your-gemini-api-key
OPENAI_API_KEY=your-openai-api-key (optional)
ENVIRONMENT=development
```

### 7. Run the Application

**Backend:**
```bash
cd code/backend
python main.py
```

**Frontend:**
Open `code/frontend/index.html` in a web browser or serve with:
```bash
python -m http.server 8080
```

The API will be available at `http://localhost:8000`

## 📖 Usage

### For Educators

1. **Upload Video**
   - Navigate to Upload section
   - Select or drag-and-drop your lecture video
   - Enter title and description
   - Click "Start Processing"

2. **View Results**
   - Wait for processing to complete (progress bar shows status)
   - Access transcript, summary, and generated clips
   - Download clips for social media or LMS

3. **Analyze Engagement**
   - View analytics dashboard
   - Track student engagement
   - Identify popular topics
   - Export reports

### For Students

1. **Browse Videos**
   - Access video library
   - Search by topic or keyword
   - Filter by difficulty level

2. **Watch Clips**
   - View topic-specific short clips
   - Access full lectures
   - Review summaries
   - Take notes

3. **Track Progress**
   - View learning dashboard
   - See completed topics
   - Get personalized recommendations

## 🔧 API Documentation

### Authentication Endpoints

**Register User**
```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "secure_password",
  "role": "educator"
}
```

**Login**
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "secure_password"
}
```

### Video Endpoints

**Upload Video**
```http
POST /api/videos/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <video_file>
title: "Introduction to Machine Learning"
description: "Basics of ML algorithms"
```

**Get Video Status**
```http
GET /api/videos/{video_id}/status
Authorization: Bearer <token>
```

**Get Transcript**
```http
GET /api/videos/{video_id}/transcript
Authorization: Bearer <token>
```

**Get Summary**
```http
GET /api/videos/{video_id}/summary
Authorization: Bearer <token>
```

**Get Clips**
```http
GET /api/videos/{video_id}/clips
Authorization: Bearer <token>
```

### Analytics Endpoints

**Get User Analytics**
```http
GET /api/analytics/user/{user_id}
Authorization: Bearer <token>
```

**Get Video Analytics**
```http
GET /api/analytics/video/{video_id}
Authorization: Bearer <token>
```

## 🧪 Testing

Run tests:
```bash
pytest tests/
```

Run with coverage:
```bash
pytest --cov=code tests/
```

## 📊 Database Schema

### Key Tables

- **users**: User accounts and authentication
- **videos**: Video metadata and processing status
- **transcripts**: Speech-to-text results with timestamps
- **summaries**: AI-generated summaries and topics
- **clips**: Generated video clips with metadata
- **learning_analytics**: User engagement tracking
- **user_progress**: Learning progress tracking

See `code/database/schema.sql` for complete schema.

## 🔐 Security

- Password hashing with bcrypt
- JWT token authentication
- HTTPS recommended for production
- SQL injection prevention via parameterized queries
- Input validation with Pydantic
- Rate limiting on API endpoints
- CORS configuration

## 🎯 Performance Optimization

- Asynchronous video processing
- Database indexing on frequently queried fields
- Caching for common queries
- CDN for video delivery (production)
- Connection pooling
- Background task queues

## 📈 Scaling Considerations

For production deployment:

1. **Load Balancing**: Use nginx or AWS ELB
2. **Database**: PostgreSQL with read replicas
3. **File Storage**: AWS S3 or Azure Blob Storage
4. **Task Queue**: Celery with Redis
5. **Monitoring**: Prometheus + Grafana
6. **Logging**: ELK Stack or CloudWatch

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

## 👥 Authors

- **Your Name** - *Initial work* - Final Year Capstone Project

## 🙏 Acknowledgments

- OpenAI Whisper team for ASR technology
- Google for Gemini API
- FastAPI community
- All educators making knowledge accessible

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Email: support@educlip.ai (example)

## 🗺️ Roadmap

### Version 1.0 (Current)
- ✅ Video upload and processing
- ✅ Speech-to-text transcription
- ✅ AI-powered summarization
- ✅ Clip generation
- ✅ Basic analytics

### Version 1.1 (Planned)
- ⏳ Multilingual support (10+ languages)
- ⏳ Real-time transcription
- ⏳ Question-answer generation
- ⏳ Quiz creation from content
- ⏳ LMS integration (Moodle, Canvas)

### Version 2.0 (Future)
- ⏳ Mobile applications (iOS/Android)
- ⏳ Live lecture processing
- ⏳ AR/VR integration
- ⏳ Voice cloning for narration
- ⏳ Advanced predictive analytics

## 📚 Documentation

Full documentation available at:
- [API Documentation](docs/api.md)
- [User Guide](docs/user-guide.md)
- [Developer Guide](docs/developer-guide.md)
- [Deployment Guide](docs/deployment.md)

## 🎓 Academic Use

This project is designed as a final year capstone project for B.E/B.Tech Computer Science Engineering. It demonstrates:

- Full-stack web development
- AI/ML integration
- System architecture design
- Database design and optimization
- API development
- Cloud deployment readiness

Perfect for academic presentations and viva voce examinations.

---

**Built with ❤️ for Education**
