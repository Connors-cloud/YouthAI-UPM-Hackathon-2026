-- ===== YOUTHAI DATABASE INITIALIZATION SCRIPT =====
-- Database: youthai_db
-- Created: April 23, 2026
-- Purpose: Complete database schema for YouthAI system

-- ===== 1. USERS TABLE =====
-- Stores user account information
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('student', 'staff', 'admin') DEFAULT 'student',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active TINYINT(1) DEFAULT 1,
    INDEX idx_email (email),
    INDEX idx_role (role)
);

-- ===== 2. USER PROFILE TABLE =====
-- Stores detailed user profile information
CREATE TABLE IF NOT EXISTS user_profiles (
    profile_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    interests JSON,
    goals JSON,
    preferences JSON,
    bio TEXT,
    avatar_url VARCHAR(255),
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id)
);

-- ===== 2.5 USER PERSONALITY & PROBLEMS TABLE =====
-- Stores user personality traits and personal problems for AI personalization
CREATE TABLE IF NOT EXISTS user_personality (
    personality_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    personality_traits JSON,
    communication_style VARCHAR(100),
    preferred_language_tone VARCHAR(100),
    main_problems TEXT,
    problem_categories JSON,
    learning_style VARCHAR(100),
    stress_triggers JSON,
    coping_mechanisms JSON,
    goals_and_aspirations TEXT,
    family_background TEXT,
    current_challenges TEXT,
    support_system TEXT,
    ai_engagement_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id)
);

-- ===== 3. CHAT HISTORY TABLE =====
-- Stores conversation messages between users and AI
CREATE TABLE IF NOT EXISTS chat_history (
    chat_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    message TEXT NOT NULL,
    ai_response TEXT,
    message_type ENUM('text', 'mood_check', 'career_question', 'program_inquiry') DEFAULT 'text',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_timestamp (timestamp)
);

-- ===== 4. BEHAVIOUR TRACKING TABLE =====
-- Tracks user emotional patterns and engagement
CREATE TABLE IF NOT EXISTS behaviour_tracking (
    tracking_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    mood VARCHAR(50),
    emotion_score INT,
    engagement_level INT,
    detected_pattern VARCHAR(100),
    note TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_timestamp (timestamp),
    INDEX idx_mood (mood)
);

-- ===== 5. MOOD TRACKING TABLE =====
-- Detailed mood tracking with daily check-ins
CREATE TABLE IF NOT EXISTS mood_tracking (
    mood_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    mood_value VARCHAR(50) NOT NULL,
    mood_score INT,
    note TEXT,
    date DATE NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_date (date),
    UNIQUE KEY unique_user_date (user_id, date)
);

-- ===== 6. RECOMMENDATIONS TABLE =====
-- AI-generated recommendations for users
CREATE TABLE IF NOT EXISTS recommendations (
    rec_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    recommendation_type ENUM('career', 'skill', 'activity', 'coping_strategy') NOT NULL,
    content TEXT NOT NULL,
    relevance_score DECIMAL(3, 2),
    reason TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_viewed TINYINT(1) DEFAULT 0,
    viewed_at TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_type (recommendation_type)
);

-- ===== 7. PROGRAMS / EVENTS TABLE =====
-- University programs and campus activities
CREATE TABLE IF NOT EXISTS programs (
    program_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL,
    date DATE NOT NULL,
    start_time TIME,
    end_time TIME,
    location VARCHAR(200),
    capacity INT,
    registration_count INT DEFAULT 0,
    created_by INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active TINYINT(1) DEFAULT 1,
    FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL,
    INDEX idx_category (category),
    INDEX idx_date (date),
    INDEX idx_created_by (created_by)
);

-- ===== 8. USER-PROGRAM MAPPING TABLE =====
-- Join table for user program registrations
CREATE TABLE IF NOT EXISTS user_programs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    program_id INT NOT NULL,
    status ENUM('joined', 'saved', 'interested', 'attended') DEFAULT 'interested',
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    attended_at TIMESTAMP NULL,
    rating INT,
    feedback TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (program_id) REFERENCES programs(program_id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_program (user_id, program_id),
    INDEX idx_user_id (user_id),
    INDEX idx_program_id (program_id),
    INDEX idx_status (status)
);

-- ===== 9. NOTIFICATIONS TABLE =====
-- System notifications for users
CREATE TABLE IF NOT EXISTS notifications (
    notification_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    notification_type ENUM('mood_insight', 'program_update', 'career_suggestion', 'reminder', 'achievement') DEFAULT 'reminder',
    related_id INT,
    is_read TINYINT(1) DEFAULT 0,
    read_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_is_read (is_read),
    INDEX idx_created_at (created_at)
);

-- ===== 10. ADMIN LOGS TABLE =====
-- System activity and admin action logging
CREATE TABLE IF NOT EXISTS admin_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    admin_id INT NOT NULL,
    action_type VARCHAR(100) NOT NULL,
    action_description TEXT,
    affected_user_id INT,
    affected_entity_type VARCHAR(50),
    affected_entity_id INT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (admin_id) REFERENCES users(user_id) ON DELETE SET NULL,
    FOREIGN KEY (affected_user_id) REFERENCES users(user_id) ON DELETE SET NULL,
    INDEX idx_admin_id (admin_id),
    INDEX idx_action_type (action_type),
    INDEX idx_timestamp (timestamp)
);

-- ===== 11. CAREER PATHS TABLE =====
-- Available career paths in the system
CREATE TABLE IF NOT EXISTS career_paths (
    career_id INT AUTO_INCREMENT PRIMARY KEY,
    career_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    related_jobs JSON,
    skills_required JSON,
    related_programs TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ===== 12. USER CAREER INTEREST TABLE =====
-- Tracks user career interests and scores
CREATE TABLE IF NOT EXISTS user_career_interests (
    interest_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    career_id INT NOT NULL,
    interest_score INT DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (career_id) REFERENCES career_paths(career_id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_career (user_id, career_id),
    INDEX idx_user_id (user_id)
);

-- ===== 13. SELF-CARE TIPS TABLE =====
-- Library of self-care and wellness tips
CREATE TABLE IF NOT EXISTS self_care_tips (
    tip_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(50),
    duration_minutes INT,
    difficulty_level ENUM('easy', 'moderate', 'challenging') DEFAULT 'easy',
    mood_tags JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_category (category)
);

-- ===== 14. COPING STRATEGIES TABLE =====
-- Evidence-based coping strategies for different moods
CREATE TABLE IF NOT EXISTS coping_strategies (
    strategy_id INT AUTO_INCREMENT PRIMARY KEY,
    mood_trigger VARCHAR(100) NOT NULL,
    strategy_title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    steps JSON,
    effectiveness_rating DECIMAL(3, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_mood_trigger (mood_trigger)
);

-- ===== 15. USER-STRATEGY USAGE TABLE =====
-- Tracks which coping strategies users have tried
CREATE TABLE IF NOT EXISTS user_strategy_usage (
    usage_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    strategy_id INT NOT NULL,
    used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    effectiveness_feedback INT,
    notes TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (strategy_id) REFERENCES coping_strategies(strategy_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_used_at (used_at)
);

-- ===== 16. ACHIEVEMENT / BADGES TABLE =====
-- Gamification: user achievements and badges
CREATE TABLE IF NOT EXISTS achievements (
    achievement_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    badge_name VARCHAR(100) NOT NULL,
    description TEXT,
    icon_url VARCHAR(255),
    earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_earned_at (earned_at)
);

-- ===== 17. FEEDBACK TABLE =====
-- Collect user feedback on app and programs
CREATE TABLE IF NOT EXISTS feedback (
    feedback_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    feedback_type VARCHAR(50),
    subject VARCHAR(200),
    message TEXT NOT NULL,
    rating INT,
    related_entity_type VARCHAR(50),
    related_entity_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('new', 'reviewed', 'resolved') DEFAULT 'new',
    admin_response TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status)
);

-- ===== INSERT DEFAULT DATA =====

-- Insert default career paths
INSERT IGNORE INTO career_paths (career_name, description, related_jobs, skills_required)
VALUES
('Technology', 'Tech-related careers focused on innovation and problem-solving', '["Software Engineer", "Data Scientist", "UI/UX Designer", "DevOps Engineer"]', '["Programming", "Problem Solving", "System Design"]'),
('Business', 'Business-oriented careers in management and strategy', '["Business Analyst", "Marketing Manager", "Entrepreneur", "Product Manager"]', '["Leadership", "Analysis", "Communication"]'),
('Creative Arts', 'Creative fields for artistic and design-focused professionals', '["Graphic Designer", "Content Creator", "Animator", "Art Director"]', '["Creativity", "Visual Design", "Communication"]'),
('Science', 'Research and scientific discovery careers', '["Research Scientist", "Lab Technician", "Environmental Analyst", "Biotech Specialist"]', '["Research", "Analysis", "Laboratory Skills"]'),
('Social Impact', 'Careers focused on community and social good', '["Social Worker", "Community Manager", "Policy Analyst", "Non-profit Director"]', '["Empathy", "Community Engagement", "Advocacy"]');

-- Insert default self-care tips
INSERT IGNORE INTO self_care_tips (title, content, category, duration_minutes, difficulty_level, mood_tags)
VALUES
('5-Minute Breathing Break', 'Take slow, deep breaths for 5 minutes between study sessions to reset your mind.', 'mindfulness', 5, 'easy', '["stressed", "anxious"]'),
('Drink Water & Stretch', 'Drink a glass of water and stretch your shoulders for 30 seconds to refresh.', 'physical', 2, 'easy', '["tired", "overwhelmed"]'),
('Gratitude Journal', 'Write down 3 things you are grateful for today.', 'reflection', 10, 'easy', '["sad", "down"]'),
('15-Minute Walk', 'Go for a short walk to boost mood and creativity.', 'physical', 15, 'easy', '["stressed", "sad"]'),
('Peer Check-In', 'Text a friend and check in with them for mutual support.', 'social', 10, 'moderate', '["lonely", "isolated"]');

-- Insert default coping strategies
INSERT IGNORE INTO coping_strategies (mood_trigger, strategy_title, description, steps, effectiveness_rating)
VALUES
('stressed', 'Box Breathing Technique', 'Reduce stress through structured breathing', '["Breathe in for 4 counts", "Hold for 4 counts", "Exhale for 4 counts", "Hold for 4 counts", "Repeat 5 times"]', 4.5),
('anxious', 'Grounding Technique (5-4-3-2-1)', 'Use senses to ground yourself in the present', '["Notice 5 things you see", "4 things you can touch", "3 things you hear", "2 things you smell", "1 thing you taste"]', 4.3),
('sad', 'Positive Activity Scheduling', 'Plan and engage in activities you enjoy', '["List 3 activities that bring joy", "Schedule one for today", "Complete the activity"]', 4.1),
('overwhelmed', 'Task Breakdown Method', 'Break large tasks into manageable steps', '["List all tasks", "Prioritize 3 main tasks", "Break each into smaller steps", "Complete one step at a time"]', 4.4),
('lonely', 'Social Connection Prompt', 'Reach out to friends or community', '["Think of 3 people you care about", "Send a message to one", "Suggest a virtual or in-person meetup"]', 4.2);

-- ===== SUMMARY =====
-- Created 17 tables covering:
-- - User management & profiles
-- - AI chat & interaction history
-- - Mood & behaviour tracking
-- - Career guidance & paths
-- - Programs & event management
-- - Notifications & logging
-- - Self-care & coping strategies
-- - Gamification (achievements)
-- - Feedback collection
-- Total tables: 17
-- Total initial data rows: 10
