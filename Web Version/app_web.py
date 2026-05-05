#!/usr/bin/env python3
"""Browser version of YouthAI with Gemini chat."""

import os
import random
from datetime import datetime

import pymysql
import requests
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, session, url_for
from flask_mysqldb import MySQL
import MySQLdb.cursors

# Load environment variables from .env file
load_dotenv()

# Verify API key is loaded
api_key_status = "✅ GEMINI_API_KEY loaded" if os.getenv("GEMINI_API_KEY") else "⚠️  GEMINI_API_KEY not found"
print(f"\n{api_key_status}")

app = Flask(__name__)
app.secret_key = "youthai-dev-secret"

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''  # Default XAMPP password is empty
app.config['MYSQL_DB'] = 'youthai_db'

mysql = MySQL(app)

def init_db():
    """Initialize database and create all required tables for YouthAI system."""
    try:
        # First create database if it doesn't exist
        temp_conn = pymysql.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD']
        )
        temp_cursor = temp_conn.cursor()
        temp_cursor.execute('CREATE DATABASE IF NOT EXISTS youthai_db')
        temp_conn.commit()
        temp_cursor.close()
        temp_conn.close()
        
        cursor = mysql.connection.cursor()
        
        # 1. USERS TABLE
        cursor.execute('''
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
            )
        ''')
        
        # 2. USER PROFILES TABLE
        cursor.execute('''
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
            )
        ''')
        
        # 3. CHAT HISTORY TABLE
        cursor.execute('''
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
            )
        ''')
        
        # 4. BEHAVIOUR TRACKING TABLE
        cursor.execute('''
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
            )
        ''')
        
        # 5. MOOD TRACKING TABLE
        cursor.execute('''
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
            )
        ''')
        
        # 6. RECOMMENDATIONS TABLE
        cursor.execute('''
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
            )
        ''')
        
        # 7. PROGRAMS / EVENTS TABLE
        cursor.execute('''
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
                created_by INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                is_active TINYINT(1) DEFAULT 1,
                FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL,
                INDEX idx_category (category),
                INDEX idx_date (date),
                INDEX idx_created_by (created_by)
            )
        ''')
        
        # 8. USER-PROGRAM MAPPING TABLE
        cursor.execute('''
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
            )
        ''')
        
        # 9. NOTIFICATIONS TABLE
        cursor.execute('''
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
            )
        ''')
        
        # 10. ADMIN LOGS TABLE
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin_logs (
                log_id INT AUTO_INCREMENT PRIMARY KEY,
                admin_id INT,
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
            )
        ''')
        
        # 11. CAREER PATHS TABLE
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS career_paths (
                career_id INT AUTO_INCREMENT PRIMARY KEY,
                career_name VARCHAR(100) NOT NULL UNIQUE,
                description TEXT,
                related_jobs JSON,
                skills_required JSON,
                related_programs TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        ''')
        
        # 12. USER CAREER INTERESTS TABLE
        cursor.execute('''
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
            )
        ''')
        
        # 13. SELF-CARE TIPS TABLE
        cursor.execute('''
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
            )
        ''')
        
        # 14. COPING STRATEGIES TABLE
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS coping_strategies (
                strategy_id INT AUTO_INCREMENT PRIMARY KEY,
                mood_trigger VARCHAR(100) NOT NULL,
                strategy_title VARCHAR(200) NOT NULL,
                description TEXT NOT NULL,
                steps JSON,
                effectiveness_rating DECIMAL(3, 2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_mood_trigger (mood_trigger)
            )
        ''')
        
        # 15. USER-STRATEGY USAGE TABLE
        cursor.execute('''
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
            )
        ''')
        
        # 16. ACHIEVEMENTS / BADGES TABLE
        cursor.execute('''
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
            )
        ''')
        
        # 17. FEEDBACK TABLE
        cursor.execute('''
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
            )
        ''')
        
        # Insert default career paths if not exist
        count_cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        count_cursor.execute("SELECT COUNT(*) as count FROM career_paths")
        count_result = count_cursor.fetchone()
        count_cursor.close()
        
        if count_result['count'] == 0:
            cursor.execute('''
                INSERT INTO career_paths (career_name, description, related_jobs, skills_required) VALUES
                ('Technology', 'Tech-related careers focused on innovation and problem-solving', 
                 '["Software Engineer", "Data Scientist", "UI/UX Designer", "DevOps Engineer"]', 
                 '["Programming", "Problem Solving", "System Design"]'),
                ('Business', 'Business-oriented careers in management and strategy', 
                 '["Business Analyst", "Marketing Manager", "Entrepreneur", "Product Manager"]', 
                 '["Leadership", "Analysis", "Communication"]'),
                ('Creative Arts', 'Creative fields for artistic and design-focused professionals', 
                 '["Graphic Designer", "Content Creator", "Animator", "Art Director"]', 
                 '["Creativity", "Visual Design", "Communication"]'),
                ('Science', 'Research and scientific discovery careers', 
                 '["Research Scientist", "Lab Technician", "Environmental Analyst", "Biotech Specialist"]', 
                 '["Research", "Analysis", "Laboratory Skills"]'),
                ('Social Impact', 'Careers focused on community and social good', 
                 '["Social Worker", "Community Manager", "Policy Analyst", "Non-profit Director"]', 
                 '["Empathy", "Community Engagement", "Advocacy"]')
            ''')
        
        mysql.connection.commit()
        cursor.close()
        print("✅ Database initialized successfully with 17 tables!")
    except Exception as e:
        print(f"❌ Database initialization error: {e}")

# Initialize database on app startup
with app.app_context():
    init_db()

SYSTEM_PROMPT = (
    "You are YouthAI, a warm and supportive AI wellbeing buddy for UKM students. "
    "Be empathetic, concise (2-4 sentences), practical, and friendly."
)

MOODS = {
    "Terrible": {"emoji": "😢", "v": 1},
    "Bad": {"emoji": "😟", "v": 2},
    "Okay": {"emoji": "😐", "v": 3},
    "Good": {"emoji": "🙂", "v": 4},
    "Great": {"emoji": "😊", "v": 5},
    "Amazing": {"emoji": "😄", "v": 6},
}

PROGRAMS = [
    {"id": 1, "title": "Python Programming Workshop", "cat": "Workshop", "date": "2025-02-15", "loc": "Lab FSKTM 1", "slots": 30, "reg": 18},
    {"id": 2, "title": "Mental Health Awareness Talk", "cat": "Wellbeing", "date": "2025-02-18", "loc": "Dewan Seminar", "slots": 100, "reg": 65},
    {"id": 3, "title": "Campus Run 5K", "cat": "Sports", "date": "2025-02-20", "loc": "Padang UKM", "slots": 200, "reg": 142},
    {"id": 4, "title": "Volunteer: River Cleanup", "cat": "Volunteering", "date": "2025-02-22", "loc": "Sungai Langat", "slots": 50, "reg": 32},
    {"id": 5, "title": "Career Fair 2025", "cat": "Career", "date": "2025-02-25", "loc": "Dewan Canselori", "slots": 500, "reg": 280},
    {"id": 6, "title": "UI/UX Design Bootcamp", "cat": "Workshop", "date": "2025-02-28", "loc": "Lab FSKTM 2", "slots": 25, "reg": 25},
    {"id": 7, "title": "Open Mic Night", "cat": "Social", "date": "2025-03-01", "loc": "Cafe Kampus", "slots": 80, "reg": 45},
    {"id": 8, "title": "Study Skills Seminar", "cat": "Academic", "date": "2025-03-03", "loc": "Dewan Kuliah A", "slots": 60, "reg": 38},
    {"id": 9, "title": "Yoga & Mindfulness Session", "cat": "Wellbeing", "date": "2025-03-05", "loc": "Gym UKM", "slots": 20, "reg": 12},
    {"id": 10, "title": "Hackathon: Solve for SDG", "cat": "Workshop", "date": "2025-03-08", "loc": "FSKTM", "slots": 100, "reg": 78},
    {"id": 11, "title": "Resume Clinic", "cat": "Career", "date": "2025-03-10", "loc": "Career Center", "slots": 40, "reg": 16},
    {"id": 12, "title": "Beach Cleanup Day", "cat": "Volunteering", "date": "2025-03-12", "loc": "Pantai Morib", "slots": 70, "reg": 29},
    {"id": 13, "title": "Badminton Friendly Tournament", "cat": "Sports", "date": "2025-03-15", "loc": "Kompleks Sukan", "slots": 64, "reg": 40},
    {"id": 14, "title": "Financial Literacy for Students", "cat": "Academic", "date": "2025-03-18", "loc": "Bilik Seminar Pusanika", "slots": 90, "reg": 57},
    {"id": 15, "title": "Sunset Acoustic Social", "cat": "Social", "date": "2025-03-20", "loc": "Tasik Varsiti", "slots": 120, "reg": 84},
    {"id": 16, "title": "Data Analytics Crash Course", "cat": "Workshop", "date": "2025-03-22", "loc": "Lab Data Sains", "slots": 45, "reg": 33},
    {"id": 17, "title": "Peer Support Circle", "cat": "Wellbeing", "date": "2025-03-24", "loc": "Pusat Kaunseling UKM", "slots": 25, "reg": 14},
    {"id": 18, "title": "Futsal League Kickoff", "cat": "Sports", "date": "2025-03-26", "loc": "Gelanggang Futsal UKM", "slots": 100, "reg": 72},
    {"id": 19, "title": "Library Volunteer Day", "cat": "Volunteering", "date": "2025-03-27", "loc": "Perpustakaan Tun Seri Lanang", "slots": 35, "reg": 19},
    {"id": 20, "title": "LinkedIn Profile Workshop", "cat": "Career", "date": "2025-03-29", "loc": "Career Hub", "slots": 50, "reg": 34},
    {"id": 21, "title": "Board Game Chill Night", "cat": "Social", "date": "2025-04-01", "loc": "Student Lounge", "slots": 70, "reg": 46},
    {"id": 22, "title": "Exam Strategy Masterclass", "cat": "Academic", "date": "2025-04-03", "loc": "Dewan Kuliah B", "slots": 110, "reg": 61},
    {"id": 23, "title": "Mobile App Build Sprint", "cat": "Workshop", "date": "2025-04-05", "loc": "Innovation Lab", "slots": 32, "reg": 24},
    {"id": 24, "title": "Mindful Morning Breathing", "cat": "Wellbeing", "date": "2025-04-07", "loc": "Taman Ilmu", "slots": 40, "reg": 21},
    {"id": 25, "title": "Charity Food Drive", "cat": "Volunteering", "date": "2025-04-09", "loc": "Dataran Pusanika", "slots": 150, "reg": 93},
    {"id": 26, "title": "Mock Interview Day", "cat": "Career", "date": "2025-04-11", "loc": "Bilik Temuduga FEP", "slots": 60, "reg": 42},
    {"id": 27, "title": "Table Tennis Open", "cat": "Sports", "date": "2025-04-12", "loc": "Kompleks Sukan Indoor", "slots": 48, "reg": 28},
    {"id": 28, "title": "Photography Walk", "cat": "Social", "date": "2025-04-14", "loc": "Sekitar Kampus Bangi", "slots": 55, "reg": 31},
    {"id": 29, "title": "Research Writing Clinic", "cat": "Academic", "date": "2025-04-16", "loc": "Pusat Siswazah", "slots": 65, "reg": 41},
    {"id": 30, "title": "AI for Beginners", "cat": "Workshop", "date": "2025-04-18", "loc": "Makmal AI FSKTM", "slots": 80, "reg": 80},
]
CAT_COL = {"Workshop": "#7EC8C8", "Wellbeing": "#FF8A9E", "Sports": "#98D8AA", "Volunteering": "#B8B5FF", "Career": "#FFD166", "Social": "#FFB7A5", "Academic": "#5AA8A8"}

CAREER_Q = [
    {"q": "What excites you the most?", "opts": [("Building with technology", "Technology"), ("Business strategy", "Business"), ("Creative expression", "Creative Arts"), ("Scientific discovery", "Science"), ("Helping people", "Social Impact")]},
    {"q": "How do you prefer to work?", "opts": [("Solving tech problems", "Technology"), ("Leading teams", "Business"), ("Designing visually", "Creative Arts"), ("Experimenting and analyzing", "Science"), ("Collaborating with communities", "Social Impact")]},
    {"q": "What matters most to you?", "opts": [("Innovation", "Technology"), ("Growth", "Business"), ("Creativity", "Creative Arts"), ("Knowledge", "Science"), ("Social impact", "Social Impact")]},
]

CAREERS = {
    "Technology": ["Software Engineer", "Data Scientist", "UI/UX Designer"],
    "Business": ["Business Analyst", "Marketing Manager", "Entrepreneur"],
    "Creative Arts": ["Graphic Designer", "Content Creator", "Animator"],
    "Science": ["Research Scientist", "Lab Technician", "Environmental Analyst"],
    "Social Impact": ["Social Worker", "Community Manager", "Policy Analyst"],
}

SELF_CARE_TIPS = [
    "Take a 5-minute breathing break between study blocks.",
    "Drink water now and stretch your shoulders for 30 seconds.",
    "Write down one small win from today.",
    "Go for a 10-minute walk to reset your mind.",
    "Text a friend and check in with them.",
]
TIPS = [
    "Take a 5-minute break every hour to stretch and breathe.",
    "Write down 3 things you're grateful for today.",
    "Growth happens outside your comfort zone.",
    "A 15-minute walk boosts mood and creativity.",
]

AI_RESP = {
    "sad": ["I hear you. That sounds heavy right now, and you are not alone. Want to share what happened today?"],
    "stressed": ["That pressure can feel intense. Try one small next step and one short breathing break, then we can plan the rest together."],
    "happy": ["That is awesome. Keep the momentum going and celebrate this win a little."],
    "career": ["Great question. Tell me your top interests and strengths, and I will suggest realistic paths."],
    "study": ["You can do this. Try 25 minutes focus + 5 minutes break and start from the easiest task."],
    "default": ["I am here with you. Tell me a bit more and I will help you work through it."],
}


def get_state():
    if "state" not in session:
        session["state"] = {
            "chat_msgs": [{"sender": "ai", "msg": "Hey there! I am YouthAI. How are you feeling today? 😊"}],
            "mood_history": [],
            "registered": [],
            "career_scores": {},
        }
    return session["state"]


def save_state(state):
    session["state"] = state
    session.modified = True


def require_login():
    if not session.get("username"):
        return redirect(url_for("index"))
    return None


def get_user_id(email):
    """Get user_id from email."""
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT user_id FROM users WHERE email = %s', (email,))
        result = cursor.fetchone()
        cursor.close()
        return result['user_id'] if result else None
    except Exception as e:
        print(f"Error getting user_id: {e}")
        return None


def save_chat_to_db(user_id, user_message, ai_response, message_type='text'):
    """Save chat message to database."""
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('''
            INSERT INTO chat_history (user_id, message, ai_response, message_type)
            VALUES (%s, %s, %s, %s)
        ''', (user_id, user_message, ai_response, message_type))
        mysql.connection.commit()
        cursor.close()
    except Exception as e:
        print(f"Error saving chat to DB: {e}")


def save_mood_to_db(user_id, mood_value, note=''):
    """Save mood tracking to database."""
    try:
        cursor = mysql.connection.cursor()
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute('''
            INSERT INTO mood_tracking (user_id, mood_value, mood_score, note, date)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            mood_value = VALUES(mood_value),
            mood_score = VALUES(mood_score),
            note = VALUES(note),
            timestamp = CURRENT_TIMESTAMP
        ''', (user_id, mood_value, MOODS[mood_value]["v"] if mood_value in MOODS else 3, note, today))
        mysql.connection.commit()
        cursor.close()
    except Exception as e:
        print(f"Error saving mood to DB: {e}")


def save_recommendation_to_db(user_id, rec_type, content, reason=''):
    """Save AI recommendation to database."""
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('''
            INSERT INTO recommendations (user_id, recommendation_type, content, reason)
            VALUES (%s, %s, %s, %s)
        ''', (user_id, rec_type, content, reason))
        mysql.connection.commit()
        cursor.close()
    except Exception as e:
        print(f"Error saving recommendation to DB: {e}")


def save_program_registration(user_id, program_id, status='interested'):
    """Save or update user program registration."""
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('''
            INSERT INTO user_programs (user_id, program_id, status)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE status = VALUES(status)
        ''', (user_id, program_id, status))
        mysql.connection.commit()
        cursor.close()
    except Exception as e:
        print(f"Error saving program registration: {e}")



def detect_mood(text):
    t = text.lower()
    if any(w in t for w in ["sad", "down", "lonely", "hurt"]):
        return "sad"
    if any(w in t for w in ["stress", "anxious", "overwhelm", "tired"]):
        return "stressed"
    if any(w in t for w in ["happy", "great", "amazing", "good"]):
        return "happy"
    if any(w in t for w in ["career", "job", "future"]):
        return "career"
    if any(w in t for w in ["study", "exam", "assignment"]):
        return "study"
    return "default"


def gemini_reply(user_msg, history):
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    
    # Debug: Check if API key is loaded
    if not api_key:
        print("⚠️  WARNING: GEMINI_API_KEY not found. Using local fallback.")
        return random.choice(AI_RESP[detect_mood(user_msg)])
    
    print("✅ Using Gemini API for response")
    try:
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"gemini-3-flash-preview:generateContent?key={api_key}"
        )
        convo = "\n".join([f"{m['sender']}: {m['msg']}" for m in history[-10:]])
        payload = {
            "contents": [{"parts": [{"text": f"{SYSTEM_PROMPT}\n\nConversation:\n{convo}\n\nUser: {user_msg}"}]}],
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 220},
        }
        response = requests.post(url, json=payload, timeout=12)
        response.raise_for_status()
        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as e:
        print(f"❌ Gemini API error: {e}. Falling back to local response.")
        return random.choice(AI_RESP[detect_mood(user_msg)])


def render_app(page, **kwargs):
    state = get_state()
    mood_history = state["mood_history"]
    mood_chart_data = mood_history[-7:]
    mood_labels = [item["date"][-5:] for item in mood_chart_data]
    mood_values = [MOODS[item["mood"]]["v"] for item in mood_chart_data]
    mood_emojis = [MOODS[item["mood"]]["emoji"] for item in mood_chart_data]
    avg = (
        sum(MOODS[m["mood"]]["v"] for m in mood_history) / len(mood_history)
        if mood_history
        else 0
    )
    search = request.args.get("q", "").strip().lower()
    selected_cat = request.args.get("cat", "All")
    filtered_programs = [
        p
        for p in PROGRAMS
        if (selected_cat == "All" or p["cat"] == selected_cat)
        and (not search or search in p["title"].lower() or search in p["loc"].lower())
    ]
    return render_template(
        "app.html",
        page=page,
        username=session.get("username", "Student"),
        email=session.get("email", ""),
        now=datetime.now().strftime("%d %b %Y, %I:%M %p"),
        mood_avg=round(avg, 2),
        mood_history=mood_history[-7:],
        full_mood_history=mood_history,
        mood_labels=mood_labels,
        mood_values=mood_values,
        mood_emojis=mood_emojis,
        chat_msgs=state["chat_msgs"],
        programs=filtered_programs,
        all_programs=PROGRAMS,
        selected_cat=selected_cat,
        search=search,
        categories=["All"] + sorted(list({p["cat"] for p in PROGRAMS})),
        cat_col=CAT_COL,
        registered=set(state["registered"]),
        careers=CAREERS,
        career_q=CAREER_Q,
        career_scores=state["career_scores"],
        self_care_tip=random.choice(SELF_CARE_TIPS),
        daily_tip=random.choice(TIPS),
        **kwargs,
    )


@app.get("/")
def index():
    if session.get("username"):
        return redirect(url_for("dashboard"))
    return render_template("login.html")


@app.post("/login")
def login():
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "").strip()
    if not email or "@" not in email or not password:
        return render_template("login.html", error="Please enter a valid email and password.")
    
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = %s AND password = %s', (email, password))
        user = cursor.fetchone()
        cursor.close()
        
        if user:
            session["username"] = user["name"]
            session["email"] = user["email"]
            session.pop("state", None)
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="Invalid email or password.")
    except Exception as e:
        return render_template("login.html", error="Database error. Please try again.")


@app.get("/signup")
def signup():
    if session.get("username"):
        return redirect(url_for("dashboard"))
    return render_template("signup.html")


@app.post("/signup")
def signup_post():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "").strip()
    if not name or not email or "@" not in email or not password:
        return render_template("signup.html", error="Please fill in all fields with valid information.")
    
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Check if email already exists
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            cursor.close()
            return render_template("signup.html", error="Email already registered.")
        
        # Insert new user
        cursor.execute('INSERT INTO users (name, email, password) VALUES (%s, %s, %s)', 
                      (name, email, password))
        mysql.connection.commit()
        cursor.close()
        
        session["username"] = name
        session["email"] = email
        session.pop("state", None)
        return redirect(url_for("dashboard"))
    except Exception as e:
        return render_template("signup.html", error="Database error. Please try again.")


@app.get("/dashboard")
def dashboard():
    needs_login = require_login()
    if needs_login:
        return needs_login
    return render_app("dashboard")


@app.get("/chat")
def chat():
    needs_login = require_login()
    if needs_login:
        return needs_login
    return render_app("chat")


@app.post("/chat/send")
def chat_send():
    needs_login = require_login()
    if needs_login:
        return needs_login
    user_msg = request.form.get("message", "").strip()
    if not user_msg:
        return redirect(url_for("chat"))
    state = get_state()
    state["chat_msgs"].append({"sender": "user", "msg": user_msg})
    ai_msg = gemini_reply(user_msg, state["chat_msgs"])
    state["chat_msgs"].append({"sender": "ai", "msg": ai_msg})
    save_state(state)
    
    # Save to database
    user_id = get_user_id(session.get("email"))
    if user_id:
        save_chat_to_db(user_id, user_msg, ai_msg, 'text')
    
    return redirect(url_for("chat"))


@app.post("/chat/clear")
def chat_clear():
    needs_login = require_login()
    if needs_login:
        return needs_login
    state = get_state()
    state["chat_msgs"] = [{"sender": "ai", "msg": "Hey there! I am YouthAI. How are you feeling today? 😊"}]
    save_state(state)
    return redirect(url_for("chat"))


@app.get("/mood")
def mood():
    needs_login = require_login()
    if needs_login:
        return needs_login
    return render_app("mood")


@app.post("/mood/save")
def mood_save():
    needs_login = require_login()
    if needs_login:
        return needs_login
    mood_value = request.form.get("mood", "Okay")
    note = request.form.get("note", "").strip()
    if mood_value not in MOODS:
        mood_value = "Okay"
    state = get_state()
    state["mood_history"].append(
        {"date": datetime.now().strftime("%Y-%m-%d"), "mood": mood_value, "note": note}
    )
    state["mood_history"] = state["mood_history"][-30:]
    save_state(state)
    
    # Save to database
    user_id = get_user_id(session.get("email"))
    if user_id:
        save_mood_to_db(user_id, mood_value, note)
    
    return redirect(url_for("mood"))


@app.post("/mood/quick/<mood_value>")
def mood_quick(mood_value):
    needs_login = require_login()
    if needs_login:
        return needs_login
    if mood_value not in MOODS:
        mood_value = "Okay"
    state = get_state()
    state["mood_history"].append({"date": datetime.now().strftime("%Y-%m-%d"), "mood": mood_value, "note": ""})
    state["mood_history"] = state["mood_history"][-30:]
    # Add mood context message to chat for counseling flow
    mood_emoji = MOODS[mood_value]["emoji"]
    state["chat_msgs"].append({"sender": "user", "msg": f"I'm feeling {mood_value} {mood_emoji}"})
    ai_counsel_msg = f"I hear you're feeling {mood_value} {mood_emoji}. Tell me, what's been on your mind? I'd like to understand what's causing this feeling so I can better support you."
    state["chat_msgs"].append({"sender": "ai", "msg": ai_counsel_msg})
    save_state(state)
    
    # Save to database
    user_id = get_user_id(session.get("email"))
    if user_id:
        save_mood_to_db(user_id, mood_value, "")
        save_chat_to_db(user_id, f"I'm feeling {mood_value} {mood_emoji}", ai_counsel_msg, 'mood_check')
    
    return redirect(url_for("chat"))


@app.get("/career")
def career():
    needs_login = require_login()
    if needs_login:
        return needs_login
    return render_app("career")


@app.post("/career/submit")
def career_submit():
    needs_login = require_login()
    if needs_login:
        return needs_login
    scores = {k: 0 for k in CAREERS}
    for idx in range(len(CAREER_Q)):
        selected = request.form.get(f"q{idx}")
        if selected in scores:
            scores[selected] += 1
    state = get_state()
    state["career_scores"] = scores
    # Add career context to chat for AI-guided program matching
    top_matches = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_career = top_matches[0][0] if top_matches else "your profile"
    career_msg = f"Based on your answers, I see you're interested in {top_career}. Here are some campus programs and activities that align with your path. Which of these interests you?"
    state["chat_msgs"].append({"sender": "ai", "msg": career_msg})
    save_state(state)
    
    # Save to database
    user_id = get_user_id(session.get("email"))
    if user_id:
        save_chat_to_db(user_id, "Career Assessment Complete", career_msg, 'career_question')
        # Save career recommendation
        save_recommendation_to_db(user_id, 'career', top_career, f"Career match score: {scores[top_career]}/3")
    
    return redirect(url_for("chat"))


@app.get("/programs")
def programs():
    needs_login = require_login()
    if needs_login:
        return needs_login
    return render_app("programs")


@app.post("/programs/join/<int:pid>")
def join_program(pid):
    needs_login = require_login()
    if needs_login:
        return needs_login
    state = get_state()
    if pid not in state["registered"]:
        state["registered"].append(pid)
    save_state(state)
    
    # Save to database
    user_id = get_user_id(session.get("email"))
    if user_id:
        save_program_registration(user_id, pid, 'joined')
    
    return redirect(url_for("programs"))


@app.get("/profile")
def profile():
    needs_login = require_login()
    if needs_login:
        return needs_login
    return render_app("profile")


@app.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
