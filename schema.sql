-- EduClip AI Database Schema
-- PostgreSQL/MySQL Compatible

-- ============================================
-- Users Table
-- ============================================
CREATE TABLE users (
    user_id VARCHAR(36) PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('educator', 'student', 'admin') DEFAULT 'student',
    profile_picture VARCHAR(500),
    bio TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    INDEX idx_email (email),
    INDEX idx_username (username)
);

-- ============================================
-- Videos Table
-- ============================================
CREATE TABLE videos (
    video_id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    file_path VARCHAR(500) NOT NULL,
    thumbnail_path VARCHAR(500),
    duration DECIMAL(10, 2),
    file_size BIGINT,
    resolution VARCHAR(20),
    format VARCHAR(10),
    status ENUM('uploading', 'processing', 'transcribing', 'analyzing', 'generating_clips', 'complete', 'failed') DEFAULT 'uploading',
    progress INT DEFAULT 0,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    views INT DEFAULT 0,
    is_public BOOLEAN DEFAULT FALSE,
    tags JSON,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_uploaded_at (uploaded_at)
);

-- ============================================
-- Transcripts Table
-- ============================================
CREATE TABLE transcripts (
    transcript_id VARCHAR(36) PRIMARY KEY,
    video_id VARCHAR(36) NOT NULL UNIQUE,
    full_text LONGTEXT NOT NULL,
    language VARCHAR(10) DEFAULT 'en',
    segments JSON NOT NULL,
    word_count INT,
    confidence_score DECIMAL(5, 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (video_id) REFERENCES videos(video_id) ON DELETE CASCADE,
    INDEX idx_video_id (video_id),
    FULLTEXT idx_full_text (full_text)
);

-- ============================================
-- Summaries Table
-- ============================================
CREATE TABLE summaries (
    summary_id VARCHAR(36) PRIMARY KEY,
    video_id VARCHAR(36) NOT NULL UNIQUE,
    executive_summary TEXT NOT NULL,
    key_concepts JSON,
    learning_objectives JSON,
    topics JSON,
    prerequisites JSON,
    difficulty_level ENUM('beginner', 'intermediate', 'advanced') DEFAULT 'intermediate',
    key_takeaways JSON,
    suggested_applications JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (video_id) REFERENCES videos(video_id) ON DELETE CASCADE,
    INDEX idx_video_id (video_id),
    INDEX idx_difficulty (difficulty_level)
);

-- ============================================
-- Clips Table
-- ============================================
CREATE TABLE clips (
    clip_id VARCHAR(36) PRIMARY KEY,
    video_id VARCHAR(36) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    start_time DECIMAL(10, 2) NOT NULL,
    end_time DECIMAL(10, 2) NOT NULL,
    duration DECIMAL(10, 2) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    thumbnail_path VARCHAR(500),
    importance_score DECIMAL(5, 2),
    topic VARCHAR(255),
    concepts JSON,
    views INT DEFAULT 0,
    shares INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (video_id) REFERENCES videos(video_id) ON DELETE CASCADE,
    INDEX idx_video_id (video_id),
    INDEX idx_importance (importance_score DESC),
    INDEX idx_topic (topic)
);

-- ============================================
-- Learning Analytics Table
-- ============================================
CREATE TABLE learning_analytics (
    analytics_id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    video_id VARCHAR(36),
    clip_id VARCHAR(36),
    watch_duration DECIMAL(10, 2) NOT NULL,
    completion_rate DECIMAL(5, 2),
    interaction_type ENUM('view', 'pause', 'rewind', 'complete', 'bookmark', 'note') NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_id VARCHAR(36),
    device_type VARCHAR(50),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (video_id) REFERENCES videos(video_id) ON DELETE CASCADE,
    FOREIGN KEY (clip_id) REFERENCES clips(clip_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_video_id (video_id),
    INDEX idx_timestamp (timestamp)
);

-- ============================================
-- User Progress Table
-- ============================================
CREATE TABLE user_progress (
    progress_id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    video_id VARCHAR(36) NOT NULL,
    topics_completed JSON,
    concepts_mastered JSON,
    quiz_scores JSON,
    last_position DECIMAL(10, 2),
    total_watch_time INT DEFAULT 0,
    completion_percentage DECIMAL(5, 2) DEFAULT 0,
    first_watched TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_watched TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (video_id) REFERENCES videos(video_id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_video (user_id, video_id),
    INDEX idx_user_id (user_id),
    INDEX idx_video_id (video_id)
);

-- ============================================
-- Highlights Table
-- ============================================
CREATE TABLE highlights (
    highlight_id VARCHAR(36) PRIMARY KEY,
    video_id VARCHAR(36) NOT NULL,
    start_time DECIMAL(10, 2) NOT NULL,
    end_time DECIMAL(10, 2) NOT NULL,
    highlight_text TEXT NOT NULL,
    importance_score DECIMAL(5, 2),
    highlight_type ENUM('concept', 'definition', 'example', 'summary', 'emphasis') NOT NULL,
    detected_by VARCHAR(50) DEFAULT 'ai',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (video_id) REFERENCES videos(video_id) ON DELETE CASCADE,
    INDEX idx_video_id (video_id),
    INDEX idx_importance (importance_score DESC)
);

-- ============================================
-- Topics Table
-- ============================================
CREATE TABLE topics (
    topic_id VARCHAR(36) PRIMARY KEY,
    topic_name VARCHAR(255) NOT NULL UNIQUE,
    category VARCHAR(100),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_category (category)
);

-- ============================================
-- Video Topics Junction Table
-- ============================================
CREATE TABLE video_topics (
    video_id VARCHAR(36) NOT NULL,
    topic_id VARCHAR(36) NOT NULL,
    relevance_score DECIMAL(5, 2),
    PRIMARY KEY (video_id, topic_id),
    FOREIGN KEY (video_id) REFERENCES videos(video_id) ON DELETE CASCADE,
    FOREIGN KEY (topic_id) REFERENCES topics(topic_id) ON DELETE CASCADE,
    INDEX idx_video_id (video_id),
    INDEX idx_topic_id (topic_id)
);

-- ============================================
-- Comments Table
-- ============================================
CREATE TABLE comments (
    comment_id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    video_id VARCHAR(36),
    clip_id VARCHAR(36),
    parent_comment_id VARCHAR(36),
    comment_text TEXT NOT NULL,
    timestamp_reference DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    likes INT DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (video_id) REFERENCES videos(video_id) ON DELETE CASCADE,
    FOREIGN KEY (clip_id) REFERENCES clips(clip_id) ON DELETE CASCADE,
    FOREIGN KEY (parent_comment_id) REFERENCES comments(comment_id) ON DELETE CASCADE,
    INDEX idx_video_id (video_id),
    INDEX idx_clip_id (clip_id),
    INDEX idx_user_id (user_id)
);

-- ============================================
-- Bookmarks Table
-- ============================================
CREATE TABLE bookmarks (
    bookmark_id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    video_id VARCHAR(36),
    clip_id VARCHAR(36),
    timestamp_position DECIMAL(10, 2),
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (video_id) REFERENCES videos(video_id) ON DELETE CASCADE,
    FOREIGN KEY (clip_id) REFERENCES clips(clip_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_video_id (video_id)
);

-- ============================================
-- API Keys Table (for external integrations)
-- ============================================
CREATE TABLE api_keys (
    key_id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    api_key VARCHAR(64) NOT NULL UNIQUE,
    key_name VARCHAR(100),
    permissions JSON,
    is_active BOOLEAN DEFAULT TRUE,
    last_used TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_api_key (api_key)
);

-- ============================================
-- System Logs Table
-- ============================================
CREATE TABLE system_logs (
    log_id VARCHAR(36) PRIMARY KEY,
    log_type ENUM('info', 'warning', 'error', 'critical') NOT NULL,
    message TEXT NOT NULL,
    user_id VARCHAR(36),
    video_id VARCHAR(36),
    additional_data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_log_type (log_type),
    INDEX idx_created_at (created_at),
    INDEX idx_user_id (user_id)
);

-- ============================================
-- Sample Data Insertion
-- ============================================

-- Insert sample user
INSERT INTO users (user_id, username, email, password_hash, role) VALUES
('user-001', 'john_educator', 'john@example.com', '$2b$12$sample_hash_here', 'educator'),
('user-002', 'jane_student', 'jane@example.com', '$2b$12$sample_hash_here', 'student');

-- Insert sample topics
INSERT INTO topics (topic_id, topic_name, category, description) VALUES
('topic-001', 'Machine Learning Basics', 'Computer Science', 'Introduction to machine learning concepts'),
('topic-002', 'Neural Networks', 'Computer Science', 'Deep learning and neural network architectures'),
('topic-003', 'Data Structures', 'Computer Science', 'Fundamental data structures and algorithms');

-- ============================================
-- Useful Queries
-- ============================================

-- Get user's video statistics
-- SELECT 
--     u.username,
--     COUNT(v.video_id) as total_videos,
--     SUM(v.duration) as total_duration,
--     AVG(v.views) as avg_views
-- FROM users u
-- LEFT JOIN videos v ON u.user_id = v.user_id
-- WHERE u.user_id = 'user-001'
-- GROUP BY u.username;

-- Get most engaging clips
-- SELECT 
--     c.title,
--     c.importance_score,
--     c.views,
--     v.title as video_title
-- FROM clips c
-- JOIN videos v ON c.video_id = v.video_id
-- ORDER BY c.views DESC, c.importance_score DESC
-- LIMIT 10;

-- Get user learning progress
-- SELECT 
--     u.username,
--     COUNT(DISTINCT up.video_id) as videos_watched,
--     AVG(up.completion_percentage) as avg_completion,
--     SUM(up.total_watch_time) as total_time
-- FROM users u
-- JOIN user_progress up ON u.user_id = up.user_id
-- WHERE u.user_id = 'user-002'
-- GROUP BY u.username;

-- ============================================
-- Indexes for Performance Optimization
-- ============================================

-- Additional composite indexes for common queries
CREATE INDEX idx_videos_user_status ON videos(user_id, status);
CREATE INDEX idx_analytics_user_timestamp ON learning_analytics(user_id, timestamp);
CREATE INDEX idx_clips_video_importance ON clips(video_id, importance_score DESC);
CREATE INDEX idx_progress_user_completion ON user_progress(user_id, completion_percentage);

-- ============================================
-- Views for Common Analytics Queries
-- ============================================

-- User engagement summary view
CREATE VIEW v_user_engagement AS
SELECT 
    u.user_id,
    u.username,
    u.email,
    COUNT(DISTINCT la.video_id) as videos_watched,
    COUNT(DISTINCT la.clip_id) as clips_watched,
    SUM(la.watch_duration) as total_watch_time,
    AVG(la.completion_rate) as avg_completion_rate
FROM users u
LEFT JOIN learning_analytics la ON u.user_id = la.user_id
GROUP BY u.user_id, u.username, u.email;

-- Video performance view
CREATE VIEW v_video_performance AS
SELECT 
    v.video_id,
    v.title,
    v.user_id,
    v.duration,
    v.views,
    COUNT(DISTINCT c.clip_id) as total_clips,
    AVG(c.importance_score) as avg_clip_importance,
    COUNT(DISTINCT la.user_id) as unique_viewers,
    AVG(la.completion_rate) as avg_completion_rate
FROM videos v
LEFT JOIN clips c ON v.video_id = c.video_id
LEFT JOIN learning_analytics la ON v.video_id = la.video_id
GROUP BY v.video_id, v.title, v.user_id, v.duration, v.views;

-- ============================================
-- Triggers
-- ============================================

-- Update video view count trigger
DELIMITER //
CREATE TRIGGER update_video_views
AFTER INSERT ON learning_analytics
FOR EACH ROW
BEGIN
    IF NEW.interaction_type = 'view' THEN
        UPDATE videos 
        SET views = views + 1 
        WHERE video_id = NEW.video_id;
    END IF;
END//
DELIMITER ;

-- Update clip view count trigger
DELIMITER //
CREATE TRIGGER update_clip_views
AFTER INSERT ON learning_analytics
FOR EACH ROW
BEGIN
    IF NEW.clip_id IS NOT NULL AND NEW.interaction_type = 'view' THEN
        UPDATE clips 
        SET views = views + 1 
        WHERE clip_id = NEW.clip_id;
    END IF;
END//
DELIMITER ;
