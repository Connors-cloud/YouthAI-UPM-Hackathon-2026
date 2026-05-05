#!/usr/bin/env python3
"""Browser version of YouthAI with Gemini chat."""

import os
import random
import json
from datetime import datetime, timedelta

import pymysql
import requests
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, session, url_for
from flask_mysqldb import MySQL
import MySQLdb.cursors
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask import jsonify

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = "youthai-dev-secret"

ROLE_LEVELS = {"student": 1, "staff": 2, "admin": 3}

bcrypt = Bcrypt(app)
CORS(app)

# Verify API key is loaded
api_key_status = "✅ GEMINI_API_KEY loaded" if os.getenv("GEMINI_API_KEY") else "⚠️  GEMINI_API_KEY not found"
print(f"\n{api_key_status}")

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
        
        # 2.5 USER PERSONALITY & PROBLEMS TABLE
        cursor.execute('''
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
                INSERT INTO career_paths (career_name, description, related_jobs, skills_required, related_programs) VALUES
                ('Technology', 'Tech-related careers focused on innovation and problem-solving', 
                 '["Software Engineer", "Data Scientist", "UI/UX Designer", "DevOps Engineer"]', 
                 '["Programming", "Problem Solving", "System Design"]',
                 'Python Programming Workshop, Data Analytics Crash Course, AI for Beginners'),
                ('Business', 'Business-oriented careers in management and strategy', 
                 '["Business Analyst", "Marketing Manager", "Entrepreneur", "Product Manager"]', 
                 '["Leadership", "Analysis", "Communication"]',
                 'Career Fair 2025, Mock Interview Day, LinkedIn Profile Workshop'),
                ('Creative Arts', 'Creative fields for artistic and design-focused professionals', 
                 '["Graphic Designer", "Content Creator", "Animator", "Art Director"]', 
                 '["Creativity", "Visual Design", "Communication"]',
                 'Open Mic Night, Photography Walk, Sunset Acoustic Social'),
                ('Science', 'Research and scientific discovery careers', 
                 '["Research Scientist", "Lab Technician", "Environmental Analyst", "Biotech Specialist"]', 
                 '["Research", "Analysis", "Laboratory Skills"]',
                 'Research Writing Clinic, AI for Beginners, Mindful Morning Breathing'),
                ('Social Impact', 'Careers focused on community and social good', 
                 '["Social Worker", "Community Manager", "Policy Analyst", "Non-profit Director"]', 
                 '["Empathy", "Community Engagement", "Advocacy"]',
                 'Volunteer: River Cleanup, Charity Food Drive, Peer Support Circle')
            ''')

        count_cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        count_cursor.execute("SELECT COUNT(*) as count FROM programs")
        program_count_result = count_cursor.fetchone()
        count_cursor.close()

        if program_count_result['count'] == 0:
            for program in PROGRAMS:
                cursor.execute(
                    '''
                    INSERT INTO programs (program_id, title, description, category, date, location, capacity, registration_count, is_active)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 1)
                    ''',
                    (
                        program["id"],
                        program["title"],
                        PROGRAM_DEFAULT_DESCRIPTIONS.get(program["cat"], "Campus program for students."),
                        program["cat"],
                        program["date"],
                        program["loc"],
                        program["slots"],
                        program["reg"],
                    ),
                )

        count_cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        count_cursor.execute("SELECT COUNT(*) as count FROM self_care_tips")
        tip_count_result = count_cursor.fetchone()
        count_cursor.close()

        if tip_count_result['count'] == 0:
            for tip in SELF_CARE_TIPS:
                cursor.execute(
                    '''
                    INSERT INTO self_care_tips (title, content, category, duration_minutes, difficulty_level, mood_tags)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ''',
                    (
                        tip[:60],
                        tip,
                        'wellbeing',
                        10,
                        'easy',
                        json.dumps(["stressed", "sad", "okay"]),
                    )
                )

        count_cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        count_cursor.execute("SELECT COUNT(*) as count FROM coping_strategies")
        strategy_count_result = count_cursor.fetchone()
        count_cursor.close()

        if strategy_count_result['count'] == 0:
            default_strategies = [
                ("sad", "Gentle Reset", "Give yourself a short reset with grounding and one supportive reach-out.", json.dumps(["Take 3 deep breaths", "Write one feeling down", "Text someone you trust"]), 4.5),
                ("stressed", "Pressure Release", "Break pressure into one step at a time and calm your body first.", json.dumps(["Pause for 60 seconds", "List your next task", "Work for 15 focused minutes"]), 4.7),
                ("happy", "Keep The Momentum", "Use your energy to lock in a healthy routine while motivation is high.", json.dumps(["Celebrate one win", "Plan tomorrow", "Hydrate and rest"]), 4.1),
                ("career", "Career Clarity", "Turn uncertainty into a small action toward your future direction.", json.dumps(["List 3 interests", "Pick 1 role to explore", "Join 1 relevant program"]), 4.6),
                ("study", "Study Starter", "Make studying feel smaller by reducing the first action.", json.dumps(["Open your notes", "Set a 25 minute timer", "Start the easiest section"]), 4.8),
                ("default", "Small Next Step", "When unsure, choose one tiny helpful action and do only that.", json.dumps(["Stand up and breathe", "Name one problem", "Take one small action"]), 4.2),
            ]
            for mood_trigger, strategy_title, description, steps, effectiveness in default_strategies:
                cursor.execute(
                    '''
                    INSERT INTO coping_strategies (mood_trigger, strategy_title, description, steps, effectiveness_rating)
                    VALUES (%s, %s, %s, %s, %s)
                    ''',
                    (mood_trigger, strategy_title, description, steps, effectiveness)
                )
        
        mysql.connection.commit()
        cursor.close()
        print("✅ Database initialized successfully with 17 tables!")
    except Exception as e:
        print(f"❌ Database initialization error: {e}")

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
PROGRAM_DEFAULT_DESCRIPTIONS = {
    "Workshop": "Hands-on campus learning session designed to build practical skills.",
    "Wellbeing": "Supportive wellbeing activity to help students recharge and stay balanced.",
    "Sports": "Campus sports event focused on movement, teamwork, and healthy energy.",
    "Volunteering": "Community-focused service activity that creates positive impact.",
    "Career": "Career-building session to help students prepare for future opportunities.",
    "Social": "Student social event to connect, unwind, and build friendships.",
    "Academic": "Academic support session to help students study and perform with confidence.",
}

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

# Initialize database on app startup after defaults are defined
with app.app_context():
    init_db()

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


def current_role():
    return session.get("role", "student")


def role_allows(required_role):
    return ROLE_LEVELS.get(current_role(), 0) >= ROLE_LEVELS.get(required_role, 0)


def require_role(required_role):
    needs_login = require_login()
    if needs_login:
        return needs_login
    if not role_allows(required_role):
        return redirect(url_for("dashboard"))
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


def get_all_users():
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("""
            SELECT user_id, name, email, role, is_active, created_at, updated_at
            FROM users
            ORDER BY created_at DESC
        """)
        users = cursor.fetchall()
        cursor.close()
        return users
    except Exception as e:
        print(f"Error getting users: {e}")
        return []


def get_programs_from_db():
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("""
            SELECT
                program_id,
                title,
                description,
                category,
                date,
                start_time,
                end_time,
                location,
                capacity,
                registration_count,
                created_by,
                is_active
            FROM programs
            WHERE is_active = 1
            ORDER BY date ASC, created_at ASC
        """)
        rows = cursor.fetchall()
        cursor.close()
        return [
            {
                "id": row["program_id"],
                "title": row["title"],
                "desc": row.get("description") or PROGRAM_DEFAULT_DESCRIPTIONS.get(row["category"], "Campus program for students."),
                "cat": row["category"],
                "date": row["date"].strftime("%Y-%m-%d") if hasattr(row["date"], "strftime") else str(row["date"]),
                "start_time": row["start_time"].strftime("%H:%M") if row.get("start_time") and hasattr(row["start_time"], "strftime") else "",
                "end_time": row["end_time"].strftime("%H:%M") if row.get("end_time") and hasattr(row["end_time"], "strftime") else "",
                "loc": row.get("location") or "TBA",
                "slots": row.get("capacity") or 0,
                "reg": row.get("registration_count") or 0,
                "created_by": row.get("created_by"),
            }
            for row in rows
        ]
    except Exception as e:
        print(f"Error getting programs: {e}")
        return []


def create_program(title, description, category, date_value, location, capacity, created_by, start_time=None, end_time=None):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            """
            INSERT INTO programs (title, description, category, date, start_time, end_time, location, capacity, registration_count, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 0, %s)
            """,
            (title, description, category, date_value, start_time, end_time, location, capacity, created_by),
        )
        mysql.connection.commit()
        program_id = cursor.lastrowid
        cursor.close()
        return program_id
    except Exception as e:
        print(f"Error creating program: {e}")
        return None


def delete_program(program_id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE programs SET is_active = 0 WHERE program_id = %s", (program_id,))
        mysql.connection.commit()
        cursor.close()
        return True
    except Exception as e:
        print(f"Error deleting program: {e}")
        return False


def update_user_role(target_user_id, role):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE users SET role = %s WHERE user_id = %s", (role, target_user_id))
        mysql.connection.commit()
        cursor.close()
        return True
    except Exception as e:
        print(f"Error updating user role: {e}")
        return False


def set_user_active(target_user_id, is_active):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE users SET is_active = %s WHERE user_id = %s", (1 if is_active else 0, target_user_id))
        mysql.connection.commit()
        cursor.close()
        return True
    except Exception as e:
        print(f"Error updating user active state: {e}")
        return False


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


def save_recommendation_to_db(user_id, rec_type, content, reason='', relevance_score=None):
    """Save AI recommendation to database."""
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('''
            INSERT INTO recommendations (user_id, recommendation_type, content, reason, relevance_score)
            VALUES (%s, %s, %s, %s, %s)
        ''', (user_id, rec_type, content, reason, relevance_score))
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


def parse_csv_list(value):
    return [item.strip() for item in value.split(",") if item.strip()]


def ensure_user_profile(user_id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            '''
            INSERT INTO user_profiles (user_id, interests, goals, preferences)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE user_id = VALUES(user_id)
            ''',
            (user_id, json.dumps([]), json.dumps([]), json.dumps({}))
        )
        mysql.connection.commit()
        cursor.close()
    except Exception as e:
        print(f"Error ensuring user profile: {e}")


def get_user_profile(user_id):
    try:
        ensure_user_profile(user_id)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user_profiles WHERE user_id = %s', (user_id,))
        profile = cursor.fetchone()
        cursor.close()
        if not profile:
            return {}
        for field in ["interests", "goals", "preferences"]:
            raw = profile.get(field)
            if not raw:
                profile[field] = [] if field != "preferences" else {}
            else:
                try:
                    profile[field] = json.loads(raw)
                except Exception:
                    profile[field] = [] if field != "preferences" else {}
        return profile
    except Exception as e:
        print(f"Error getting user profile: {e}")
        return {}


def save_user_profile(user_id, interests, goals, preferences, bio, avatar_url, phone):
    try:
        ensure_user_profile(user_id)
        cursor = mysql.connection.cursor()
        cursor.execute(
            '''
            UPDATE user_profiles
            SET interests = %s,
                goals = %s,
                preferences = %s,
                bio = %s,
                avatar_url = %s,
                phone = %s
            WHERE user_id = %s
            ''',
            (
                json.dumps(interests),
                json.dumps(goals),
                json.dumps(preferences),
                bio,
                avatar_url,
                phone,
                user_id,
            )
        )
        mysql.connection.commit()
        cursor.close()
        return True
    except Exception as e:
        print(f"Error saving user profile: {e}")
        return False


def save_user_personality(user_id, personality_traits, communication_style, preferred_language_tone, 
                         main_problems, problem_categories, learning_style, stress_triggers,
                         coping_mechanisms, goals_and_aspirations, family_background, 
                         current_challenges, support_system, ai_engagement_notes):
    """Save user personality and problems to database."""
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('''
            INSERT INTO user_personality (
                user_id, personality_traits, communication_style, preferred_language_tone,
                main_problems, problem_categories, learning_style, stress_triggers,
                coping_mechanisms, goals_and_aspirations, family_background,
                current_challenges, support_system, ai_engagement_notes
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                personality_traits = VALUES(personality_traits),
                communication_style = VALUES(communication_style),
                preferred_language_tone = VALUES(preferred_language_tone),
                main_problems = VALUES(main_problems),
                problem_categories = VALUES(problem_categories),
                learning_style = VALUES(learning_style),
                stress_triggers = VALUES(stress_triggers),
                coping_mechanisms = VALUES(coping_mechanisms),
                goals_and_aspirations = VALUES(goals_and_aspirations),
                family_background = VALUES(family_background),
                current_challenges = VALUES(current_challenges),
                support_system = VALUES(support_system),
                ai_engagement_notes = VALUES(ai_engagement_notes),
                updated_at = CURRENT_TIMESTAMP
        ''', (
            user_id,
            json.dumps(personality_traits) if personality_traits else None,
            communication_style,
            preferred_language_tone,
            main_problems,
            json.dumps(problem_categories) if problem_categories else None,
            learning_style,
            json.dumps(stress_triggers) if stress_triggers else None,
            json.dumps(coping_mechanisms) if coping_mechanisms else None,
            goals_and_aspirations,
            family_background,
            current_challenges,
            support_system,
            ai_engagement_notes
        ))
        mysql.connection.commit()
        cursor.close()
        return True
    except Exception as e:
        print(f"Error saving user personality: {e}")
        return False


def get_user_personality(user_id):
    """Retrieve user personality and problems from database."""
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('''
            SELECT * FROM user_personality WHERE user_id = %s
        ''', (user_id,))
        personality = cursor.fetchone()
        cursor.close()
        
        if not personality:
            return None
            
        # Parse JSON fields
        json_fields = ['personality_traits', 'problem_categories', 'stress_triggers', 'coping_mechanisms']
        for field in json_fields:
            if personality.get(field):
                try:
                    personality[field] = json.loads(personality[field])
                except Exception:
                    personality[field] = []
        
        return personality
    except Exception as e:
        print(f"Error getting user personality: {e}")
        return None


def build_personality_context(user_id):
    """Build a context string for AI based on user personality and problems."""
    personality = get_user_personality(user_id)
    if not personality:
        return ""
    
    context_parts = []
    
    if personality.get('personality_traits'):
        traits = ", ".join(personality['personality_traits']) if isinstance(personality['personality_traits'], list) else str(personality['personality_traits'])
        context_parts.append(f"User personality: {traits}")
    
    if personality.get('communication_style'):
        context_parts.append(f"Prefers {personality['communication_style']} communication style")
    
    if personality.get('preferred_language_tone'):
        context_parts.append(f"Prefers a {personality['preferred_language_tone']} tone")
    
    if personality.get('main_problems'):
        context_parts.append(f"Main concerns: {personality['main_problems']}")
    
    if personality.get('problem_categories'):
        categories = ", ".join(personality['problem_categories']) if isinstance(personality['problem_categories'], list) else str(personality['problem_categories'])
        context_parts.append(f"Problem areas: {categories}")
    
    if personality.get('learning_style'):
        context_parts.append(f"Learning style: {personality['learning_style']}")
    
    if personality.get('stress_triggers'):
        triggers = ", ".join(personality['stress_triggers']) if isinstance(personality['stress_triggers'], list) else str(personality['stress_triggers'])
        context_parts.append(f"Stress triggers: {triggers}")
    
    if personality.get('coping_mechanisms'):
        mechanisms = ", ".join(personality['coping_mechanisms']) if isinstance(personality['coping_mechanisms'], list) else str(personality['coping_mechanisms'])
        context_parts.append(f"Prefers these coping methods: {mechanisms}")
    
    if personality.get('goals_and_aspirations'):
        context_parts.append(f"Goals: {personality['goals_and_aspirations']}")
    
    if personality.get('current_challenges'):
        context_parts.append(f"Current challenges: {personality['current_challenges']}")
    
    if personality.get('support_system'):
        context_parts.append(f"Support system: {personality['support_system']}")
    
    return "\n".join(context_parts)


def save_behaviour_tracking(user_id, mood, emotion_score, engagement_level, detected_pattern, note):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            '''
            INSERT INTO behaviour_tracking (user_id, mood, emotion_score, engagement_level, detected_pattern, note)
            VALUES (%s, %s, %s, %s, %s, %s)
            ''',
            (user_id, mood, emotion_score, engagement_level, detected_pattern, note)
        )
        mysql.connection.commit()
        cursor.close()
    except Exception as e:
        print(f"Error saving behaviour tracking: {e}")


def save_notification(user_id, title, message, notification_type='reminder', related_id=None, expires_days=7):
    try:
        cursor = mysql.connection.cursor()
        expires_at = datetime.now() + timedelta(days=expires_days) if expires_days else None
        cursor.execute(
            '''
            INSERT INTO notifications (user_id, title, message, notification_type, related_id, expires_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            ''',
            (user_id, title, message, notification_type, related_id, expires_at)
        )
        mysql.connection.commit()
        cursor.close()
    except Exception as e:
        print(f"Error saving notification: {e}")


def get_notifications(user_id):
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            '''
            SELECT * FROM notifications
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT 10
            ''',
            (user_id,)
        )
        rows = cursor.fetchall()
        cursor.close()
        return rows
    except Exception as e:
        print(f"Error getting notifications: {e}")
        return []


def mark_notification_read(notification_id, user_id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            '''
            UPDATE notifications
            SET is_read = 1, read_at = CURRENT_TIMESTAMP
            WHERE notification_id = %s AND user_id = %s
            ''',
            (notification_id, user_id)
        )
        mysql.connection.commit()
        cursor.close()
    except Exception as e:
        print(f"Error marking notification read: {e}")


def save_user_career_interest(user_id, career_name, interest_score):
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT career_id FROM career_paths WHERE career_name = %s', (career_name,))
        row = cursor.fetchone()
        if row:
            cursor.execute(
                '''
                INSERT INTO user_career_interests (user_id, career_id, interest_score)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE interest_score = VALUES(interest_score)
                ''',
                (user_id, row['career_id'], interest_score)
            )
            mysql.connection.commit()
        cursor.close()
    except Exception as e:
        print(f"Error saving career interest: {e}")


def get_user_career_interests(user_id):
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            '''
            SELECT cp.career_name, uci.interest_score, uci.last_updated
            FROM user_career_interests uci
            JOIN career_paths cp ON cp.career_id = uci.career_id
            WHERE uci.user_id = %s
            ORDER BY uci.interest_score DESC, cp.career_name ASC
            ''',
            (user_id,)
        )
        rows = cursor.fetchall()
        cursor.close()
        return rows
    except Exception as e:
        print(f"Error getting career interests: {e}")
        return []


def log_admin_action(admin_id, action_type, description, affected_user_id=None, entity_type=None, entity_id=None):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            '''
            INSERT INTO admin_logs (
                admin_id, action_type, action_description, affected_user_id,
                affected_entity_type, affected_entity_id, ip_address, user_agent
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''',
            (
                admin_id,
                action_type,
                description,
                affected_user_id,
                entity_type,
                entity_id,
                request.remote_addr if request else None,
                request.headers.get("User-Agent") if request else None,
            )
        )
        mysql.connection.commit()
        cursor.close()
    except Exception as e:
        print(f"Error logging admin action: {e}")


def get_admin_logs(limit=20):
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            '''
            SELECT al.*, u.name AS admin_name
            FROM admin_logs al
            LEFT JOIN users u ON u.user_id = al.admin_id
            ORDER BY al.timestamp DESC
            LIMIT %s
            ''',
            (limit,)
        )
        rows = cursor.fetchall()
        cursor.close()
        return rows
    except Exception as e:
        print(f"Error getting admin logs: {e}")
        return []


def award_achievement(user_id, badge_name, description, icon_url=None):
    try:
        icon_url = icon_url or "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='48' height='48'><rect width='48' height='48' rx='12' fill='%23059669'/><text x='50%25' y='58%25' text-anchor='middle' font-size='24' fill='white'>★</text></svg>"
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT achievement_id FROM achievements WHERE user_id = %s AND badge_name = %s',
            (user_id, badge_name)
        )
        existing = cursor.fetchone()
        if existing:
            cursor.close()
            return
        cursor.execute(
            '''
            INSERT INTO achievements (user_id, badge_name, description, icon_url)
            VALUES (%s, %s, %s, %s)
            ''',
            (user_id, badge_name, description, icon_url)
        )
        mysql.connection.commit()
        cursor.close()
        save_notification(user_id, "New Achievement", f"You earned the '{badge_name}' badge.", "achievement")
    except Exception as e:
        print(f"Error awarding achievement: {e}")


def get_achievements(user_id):
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT * FROM achievements WHERE user_id = %s ORDER BY earned_at DESC',
            (user_id,)
        )
        rows = cursor.fetchall()
        cursor.close()
        return rows
    except Exception as e:
        print(f"Error getting achievements: {e}")
        return []


def save_feedback_entry(user_id, feedback_type, subject, message, rating, related_entity_type=None, related_entity_id=None):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            '''
            INSERT INTO feedback (
                user_id, feedback_type, subject, message, rating,
                related_entity_type, related_entity_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''',
            (user_id, feedback_type, subject, message, rating, related_entity_type, related_entity_id)
        )
        mysql.connection.commit()
        cursor.close()
        award_achievement(user_id, "Voice Matters", "Submitted feedback to help improve YouthAI.")
        return True
    except Exception as e:
        print(f"Error saving feedback: {e}")
        return False


def get_feedback_for_user(user_id):
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT * FROM feedback WHERE user_id = %s ORDER BY created_at DESC',
            (user_id,)
        )
        rows = cursor.fetchall()
        cursor.close()
        return rows
    except Exception as e:
        print(f"Error getting user feedback: {e}")
        return []


def get_all_feedback():
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            '''
            SELECT f.*, u.name AS user_name, u.email
            FROM feedback f
            JOIN users u ON u.user_id = f.user_id
            ORDER BY f.created_at DESC
            '''
        )
        rows = cursor.fetchall()
        cursor.close()
        return rows
    except Exception as e:
        print(f"Error getting all feedback: {e}")
        return []


def update_feedback_admin(feedback_id, status, admin_response):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            '''
            UPDATE feedback
            SET status = %s, admin_response = %s
            WHERE feedback_id = %s
            ''',
            (status, admin_response, feedback_id)
        )
        mysql.connection.commit()
        cursor.close()
        return True
    except Exception as e:
        print(f"Error updating feedback: {e}")
        return False


def save_strategy_usage(user_id, strategy_id, feedback_score=None, notes=''):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            '''
            INSERT INTO user_strategy_usage (user_id, strategy_id, effectiveness_feedback, notes)
            VALUES (%s, %s, %s, %s)
            ''',
            (user_id, strategy_id, feedback_score, notes)
        )
        mysql.connection.commit()
        cursor.close()
    except Exception as e:
        print(f"Error saving strategy usage: {e}")


def get_strategy_usage(user_id):
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            '''
            SELECT usu.*, cs.strategy_title
            FROM user_strategy_usage usu
            JOIN coping_strategies cs ON cs.strategy_id = usu.strategy_id
            WHERE usu.user_id = %s
            ORDER BY usu.used_at DESC
            LIMIT 10
            ''',
            (user_id,)
        )
        rows = cursor.fetchall()
        cursor.close()
        return rows
    except Exception as e:
        print(f"Error getting strategy usage: {e}")
        return []


def get_recommendations(user_id):
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            '''
            SELECT * FROM recommendations
            WHERE user_id = %s
            ORDER BY timestamp DESC
            LIMIT 10
            ''',
            (user_id,)
        )
        rows = cursor.fetchall()
        cursor.close()
        return rows
    except Exception as e:
        print(f"Error getting recommendations: {e}")
        return []


def mark_recommendation_viewed(rec_id, user_id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            '''
            UPDATE recommendations
            SET is_viewed = 1, viewed_at = CURRENT_TIMESTAMP
            WHERE rec_id = %s AND user_id = %s
            ''',
            (rec_id, user_id)
        )
        mysql.connection.commit()
        cursor.close()
    except Exception as e:
        print(f"Error marking recommendation viewed: {e}")


def get_behaviour_tracking(user_id):
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            '''
            SELECT * FROM behaviour_tracking
            WHERE user_id = %s
            ORDER BY timestamp DESC
            LIMIT 10
            ''',
            (user_id,)
        )
        rows = cursor.fetchall()
        cursor.close()
        return rows
    except Exception as e:
        print(f"Error getting behaviour tracking: {e}")
        return []


def get_career_paths_details():
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM career_paths ORDER BY career_name ASC')
        rows = cursor.fetchall()
        cursor.close()
        for row in rows:
            try:
                row['related_jobs'] = json.loads(row['related_jobs']) if row.get('related_jobs') else []
            except Exception:
                row['related_jobs'] = []
            try:
                row['skills_required'] = json.loads(row['skills_required']) if row.get('skills_required') else []
            except Exception:
                row['skills_required'] = []
        return rows
    except Exception as e:
        print(f"Error getting career paths: {e}")
        return []


def get_coping_strategies(mood_trigger=None):
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if mood_trigger:
            cursor.execute(
                'SELECT * FROM coping_strategies WHERE mood_trigger = %s ORDER BY effectiveness_rating DESC',
                (mood_trigger,)
            )
        else:
            cursor.execute('SELECT * FROM coping_strategies ORDER BY effectiveness_rating DESC')
        rows = cursor.fetchall()
        cursor.close()
        for row in rows:
            try:
                row['steps'] = json.loads(row['steps']) if row.get('steps') else []
            except Exception:
                row['steps'] = []
        return rows
    except Exception as e:
        print(f"Error getting coping strategies: {e}")
        return []


def get_db_self_care_tips():
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM self_care_tips ORDER BY created_at DESC')
        rows = cursor.fetchall()
        cursor.close()
        for row in rows:
            try:
                row['mood_tags'] = json.loads(row['mood_tags']) if row.get('mood_tags') else []
            except Exception:
                row['mood_tags'] = []
        return rows
    except Exception as e:
        print(f"Error getting self care tips: {e}")
        return []


def get_user_program_details(user_id):
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            '''
            SELECT up.*, p.title, p.category, p.date, p.location
            FROM user_programs up
            JOIN programs p ON p.program_id = up.program_id
            WHERE up.user_id = %s
            ORDER BY up.registered_at DESC
            ''',
            (user_id,)
        )
        rows = cursor.fetchall()
        cursor.close()
        return rows
    except Exception as e:
        print(f"Error getting user program details: {e}")
        return []


def update_user_program_status(user_id, program_id, status, rating=None, feedback=None):
    try:
        cursor = mysql.connection.cursor()
        if status == 'attended':
            cursor.execute(
                '''
                UPDATE user_programs
                SET status = %s, attended_at = CURRENT_TIMESTAMP, rating = %s, feedback = %s
                WHERE user_id = %s AND program_id = %s
                ''',
                (status, rating, feedback, user_id, program_id)
            )
        else:
            cursor.execute(
                '''
                INSERT INTO user_programs (user_id, program_id, status, rating, feedback)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE status = VALUES(status), rating = VALUES(rating), feedback = VALUES(feedback)
                ''',
                (user_id, program_id, status, rating, feedback)
            )
        mysql.connection.commit()
        cursor.close()
        return True
    except Exception as e:
        print(f"Error updating user program status: {e}")
        return False


def delete_user(target_user_id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('DELETE FROM users WHERE user_id = %s', (target_user_id,))
        mysql.connection.commit()
        cursor.close()
        return True
    except Exception as e:
        print(f"Error deleting user: {e}")
        return False


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


def gemini_reply(user_msg, history, user_id=None):
    api_key = os.getenv("GEMINI_API_KEY", "").strip()

    if not api_key:
        print("⚠️ GEMINI_API_KEY not found. Using fallback.")
        return random.choice(AI_RESP[detect_mood(user_msg)])

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-3.1-flash-lite-preview:generateContent?key={api_key}"
    )
    
    convo = "\n".join([f"{m['sender']}: {m['msg']}" for m in history[-10:]])
    
    # Build personalized system prompt with user's personality and problems
    personalized_prompt = SYSTEM_PROMPT
    if user_id:
        personality_context = build_personality_context(user_id)
        if personality_context:
            personalized_prompt = f"{SYSTEM_PROMPT}\n\nAbout this user:\n{personality_context}\n\nBased on this, provide personalized and empathetic support."

    payload = {
        "contents": [{
            "parts": [{
                "text": f"{personalized_prompt}\n\nConversation:\n{convo}\n\nUser: {user_msg}"
            }]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 220
        },
    }

    # Retry logic
    for attempt in range(3):
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()

            # Safe parsing
            text = (
                data.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text")
            )

            if text:
                return text.strip()

            print(f"⚠️ Empty Gemini response: {data}")
            return random.choice(AI_RESP[detect_mood(user_msg)])

        except requests.exceptions.Timeout:
            print(f"⏳ Timeout (attempt {attempt+1})...")
        except Exception as e:
            print(f"❌ Gemini error: {e}")
            break

    print("⚠️ All retries failed. Using fallback.")
    return random.choice(AI_RESP[detect_mood(user_msg)])

def render_app(page, **kwargs):
    state = get_state()
    user_id = session.get("user_id") or get_user_id(session.get("email"))
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
    db_programs = get_programs_from_db() or PROGRAMS
    notifications = get_notifications(user_id) if user_id else []
    profile_data = get_user_profile(user_id) if user_id else {}
    achievements = get_achievements(user_id) if user_id else []
    user_feedback = get_feedback_for_user(user_id) if user_id else []
    user_program_details = get_user_program_details(user_id) if user_id else []
    user_career_interests = get_user_career_interests(user_id) if user_id else []
    recommendations = get_recommendations(user_id) if user_id else []
    behaviour_tracking = get_behaviour_tracking(user_id) if user_id else []
    strategy_usage = get_strategy_usage(user_id) if user_id else []
    db_self_care_tips = get_db_self_care_tips()
    coping_strategies = get_coping_strategies()
    career_paths = get_career_paths_details()
    filtered_programs = [
        p
        for p in db_programs
        if (selected_cat == "All" or p["cat"] == selected_cat)
        and (
            not search
            or search in p["title"].lower()
            or search in p["loc"].lower()
            or search in p.get("desc", "").lower()
        )
    ]
    return render_template(
        "app.html",
        page=page,
        username=session.get("username", "Student"),
        email=session.get("email", ""),
        role=current_role(),
        user_id=user_id,
        now=datetime.now().strftime("%d %b %Y, %I:%M %p"),
        mood_avg=round(avg, 2),
        mood_history=mood_history[-7:],
        full_mood_history=mood_history,
        mood_labels=mood_labels,
        mood_values=mood_values,
        mood_emojis=mood_emojis,
        chat_msgs=state["chat_msgs"],
        programs=filtered_programs,
        all_programs=db_programs,
        selected_cat=selected_cat,
        search=search,
        categories=["All"] + sorted(list({p["cat"] for p in db_programs})),
        cat_col=CAT_COL,
        registered=set(state["registered"]),
        careers=CAREERS,
        career_q=CAREER_Q,
        career_scores=state["career_scores"],
        self_care_tip=random.choice([tip["content"] for tip in db_self_care_tips]) if db_self_care_tips else random.choice(SELF_CARE_TIPS),
        daily_tip=random.choice(TIPS),
        admin_users=get_all_users() if current_role() == "admin" else [],
        admin_logs=get_admin_logs() if current_role() == "admin" else [],
        admin_feedback=get_all_feedback() if current_role() == "admin" else [],
        notifications=notifications,
        user_profile=profile_data,
        achievements=achievements,
        user_feedback=user_feedback,
        user_program_details=user_program_details,
        user_career_interests=user_career_interests,
        recommendations=recommendations,
        behaviour_tracking=behaviour_tracking,
        strategy_usage=strategy_usage,
        coping_strategies=coping_strategies,
        db_self_care_tips=db_self_care_tips,
        career_paths=career_paths,
        **kwargs,
    )


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/login")
def login():
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "").strip()
    if not email or "@" not in email or not password:
        return render_template("login.html", error="Please enter a valid email and password.")
    
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        user = cursor.fetchone()
        cursor.close()
        
        if user and not user.get("is_active", 1):
            return render_template("login.html", error="This account has been deactivated. Please contact an admin.")

        if user and bcrypt.check_password_hash(user['password'], password):
            session["user_id"] = user["user_id"]
            session["username"] = user["name"]
            session["email"] = user["email"]
            session["role"] = user.get("role", "student")
            session.pop("state", None)
            ensure_user_profile(user["user_id"])
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="Invalid email or password.")
    except Exception as e:
        print(f"Login error: {e}")
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
    if not name or not email or "@" not in email or not password or len(password) < 6:
        return render_template("signup.html", error="Please fill in all fields. Password min 6 chars.")
    
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Check if email already exists
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            cursor.close()
            return render_template("signup.html", error="Email already registered.")
        
        # Hash password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # Insert new user
        cursor.execute('INSERT INTO users (name, email, password) VALUES (%s, %s, %s)', 
                      (name, email, hashed_password))
        mysql.connection.commit()
        new_user_id = cursor.lastrowid
        cursor.close()
        
        session["user_id"] = new_user_id
        session["username"] = name
        session["email"] = email
        session["role"] = "student"
        session.pop("state", None)
        ensure_user_profile(new_user_id)
        save_notification(new_user_id, "Welcome to YouthAI", "Your student wellbeing workspace is ready.", "achievement", new_user_id, 30)
        return redirect(url_for("dashboard"))
    except Exception as e:
        print(f"Signup error: {e}")
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
    
    # Get user_id
    user_id = session.get("user_id") or get_user_id(session.get("email"))
    
    state = get_state()
    state["chat_msgs"].append({"sender": "user", "msg": user_msg})
    # Pass user_id to gemini_reply for personalized responses
    ai_msg = gemini_reply(user_msg, state["chat_msgs"], user_id)
    state["chat_msgs"].append({"sender": "ai", "msg": ai_msg})
    save_state(state)
    
    # Save to database
    if user_id:
        save_chat_to_db(user_id, user_msg, ai_msg, 'text')
        if len([msg for msg in state["chat_msgs"] if msg["sender"] == "user"]) == 1:
            award_achievement(user_id, "First Conversation", "Started your first AI conversation in YouthAI.")
    
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
        save_behaviour_tracking(
            user_id,
            mood_value,
            MOODS[mood_value]["v"],
            max(1, 7 - MOODS[mood_value]["v"]),
            detect_mood(note or mood_value),
            note,
        )
        strategy_matches = get_coping_strategies(detect_mood(note or mood_value))
        if strategy_matches:
            save_notification(
                user_id,
                "Coping Strategy Available",
                f"Suggested strategy: {strategy_matches[0]['strategy_title']}",
                "mood_insight",
                strategy_matches[0]["strategy_id"],
            )
            save_strategy_usage(user_id, strategy_matches[0]["strategy_id"], None, f"Suggested after mood '{mood_value}'")
        if len(state["mood_history"]) == 1:
            award_achievement(user_id, "Mood Tracker", "Logged your first mood check-in.")
    
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
        save_behaviour_tracking(
            user_id,
            mood_value,
            MOODS[mood_value]["v"],
            max(1, 7 - MOODS[mood_value]["v"]),
            "mood_check",
            "",
        )
    
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
        save_recommendation_to_db(user_id, 'career', top_career, f"Career match score: {scores[top_career]}/3", round(scores[top_career] / 3, 2))
        for career_name, score in scores.items():
            save_user_career_interest(user_id, career_name, score)
        save_notification(user_id, "Career Insight Ready", f"Your strongest match is {top_career}.", "career_suggestion")
    
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
        try:
            cursor = mysql.connection.cursor()
            cursor.execute(
                """
                UPDATE programs
                SET registration_count = (
                    SELECT COUNT(*) FROM user_programs
                    WHERE program_id = %s AND status = 'joined'
                )
                WHERE program_id = %s
                """,
                (pid, pid),
            )
            mysql.connection.commit()
            cursor.close()
        except Exception as e:
            print(f"Error updating registration count: {e}")
        save_notification(user_id, "Program Joined", "You successfully joined a campus program.", "program_update", pid)
        award_achievement(user_id, "Campus Explorer", "Joined your first campus program.")
    
    return redirect(url_for("programs"))


@app.post("/programs/create")
def create_program_post():
    blocked = require_role("staff")
    if blocked:
        return blocked

    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    category = request.form.get("category", "").strip()
    date_value = request.form.get("date", "").strip()
    start_time = request.form.get("start_time", "").strip() or None
    end_time = request.form.get("end_time", "").strip() or None
    location = request.form.get("location", "").strip()
    capacity = request.form.get("capacity", "").strip()

    valid_categories = {p["cat"] for p in PROGRAMS}
    if (
        not title
        or category not in valid_categories
        or not date_value
        or not location
        or not capacity.isdigit()
        or int(capacity) <= 0
    ):
        return redirect(url_for("programs"))

    new_program_id = create_program(
        title=title,
        description=description or PROGRAM_DEFAULT_DESCRIPTIONS.get(category, "Campus program for students."),
        category=category,
        date_value=date_value,
        location=location,
        capacity=int(capacity),
        created_by=session.get("user_id"),
        start_time=start_time,
        end_time=end_time,
    )
    if new_program_id:
        log_admin_action(
            session.get("user_id"),
            "program_create",
            f"Created program '{title}'",
            entity_type="program",
            entity_id=new_program_id,
        )
    return redirect(url_for("programs"))


@app.post("/programs/delete/<int:pid>")
def delete_program_post(pid):
    blocked = require_role("admin")
    if blocked:
        return blocked
    delete_program(pid)
    log_admin_action(
        session.get("user_id"),
        "program_delete",
        f"Deleted program id {pid}",
        entity_type="program",
        entity_id=pid,
    )
    return redirect(url_for("programs"))


@app.post("/programs/status/<int:pid>")
def update_program_status_post(pid):
    needs_login = require_login()
    if needs_login:
        return needs_login

    user_id = session.get("user_id") or get_user_id(session.get("email"))
    status = request.form.get("status", "interested").strip()
    rating_raw = request.form.get("rating", "").strip()
    feedback = request.form.get("feedback", "").strip()
    rating = int(rating_raw) if rating_raw.isdigit() else None

    if status not in {"joined", "saved", "interested", "attended"}:
        return redirect(url_for("profile"))

    update_user_program_status(user_id, pid, status, rating=rating, feedback=feedback)
    save_notification(user_id, "Program Updated", f"Program status changed to {status}.", "program_update", pid)
    if status == "attended":
        award_achievement(user_id, "Showed Up", "Marked a program as attended and reflected on it.")
    return redirect(url_for("profile"))


@app.post("/notifications/read/<int:notification_id>")
def notification_read(notification_id):
    needs_login = require_login()
    if needs_login:
        return needs_login
    user_id = session.get("user_id") or get_user_id(session.get("email"))
    mark_notification_read(notification_id, user_id)
    return redirect(request.referrer or url_for("dashboard"))


@app.post("/recommendations/view/<int:rec_id>")
def recommendation_view(rec_id):
    needs_login = require_login()
    if needs_login:
        return needs_login
    user_id = session.get("user_id") or get_user_id(session.get("email"))
    mark_recommendation_viewed(rec_id, user_id)
    return redirect(request.referrer or url_for("dashboard"))


@app.post("/profile/update")
def profile_update():
    needs_login = require_login()
    if needs_login:
        return needs_login

    user_id = session.get("user_id") or get_user_id(session.get("email"))
    interests = parse_csv_list(request.form.get("interests", ""))
    goals = parse_csv_list(request.form.get("goals", ""))
    preferences = {
        "communication_style": request.form.get("communication_style", "supportive").strip(),
        "study_focus": request.form.get("study_focus", "balanced").strip(),
        "reminder_pref": request.form.get("reminder_pref", "gentle").strip(),
    }
    bio = request.form.get("bio", "").strip()
    avatar_url = request.form.get("avatar_url", "").strip()
    phone = request.form.get("phone", "").strip()
    save_user_profile(user_id, interests, goals, preferences, bio, avatar_url, phone)
    save_notification(user_id, "Profile Updated", "Your profile details were saved.", "reminder")
    return redirect(url_for("profile"))


@app.post("/personality/save")
def personality_save():
    """Save user personality and problems for AI personalization."""
    needs_login = require_login()
    if needs_login:
        return needs_login

    user_id = session.get("user_id") or get_user_id(session.get("email"))
    
    # Parse form data
    personality_traits = parse_csv_list(request.form.get("personality_traits", ""))
    communication_style = request.form.get("communication_style", "").strip()
    preferred_language_tone = request.form.get("preferred_language_tone", "").strip()
    main_problems = request.form.get("main_problems", "").strip()
    problem_categories = parse_csv_list(request.form.get("problem_categories", ""))
    learning_style = request.form.get("learning_style", "").strip()
    stress_triggers = parse_csv_list(request.form.get("stress_triggers", ""))
    coping_mechanisms = parse_csv_list(request.form.get("coping_mechanisms", ""))
    goals_and_aspirations = request.form.get("goals_and_aspirations", "").strip()
    family_background = request.form.get("family_background", "").strip()
    current_challenges = request.form.get("current_challenges", "").strip()
    support_system = request.form.get("support_system", "").strip()
    ai_engagement_notes = request.form.get("ai_engagement_notes", "").strip()
    
    # Save to database
    success = save_user_personality(
        user_id,
        personality_traits,
        communication_style,
        preferred_language_tone,
        main_problems,
        problem_categories,
        learning_style,
        stress_triggers,
        coping_mechanisms,
        goals_and_aspirations,
        family_background,
        current_challenges,
        support_system,
        ai_engagement_notes
    )
    
    if success:
        save_notification(user_id, "Personality Profile Saved", "Your personality and problem information has been saved. AI will now provide more personalized support.", "reminder")
        award_achievement(user_id, "Personal Connection", "Shared your personality profile for personalized AI support.")
    
    return redirect(url_for("profile"))


@app.get("/personality/view")
def personality_view():
    """View current personality profile."""
    needs_login = require_login()
    if needs_login:
        return needs_login
    
    user_id = session.get("user_id") or get_user_id(session.get("email"))
    personality = get_user_personality(user_id)
    
    if personality:
        return jsonify(personality)
    else:
        return jsonify({"message": "No personality profile found"}), 404


@app.post("/feedback/submit")
def feedback_submit():
    needs_login = require_login()
    if needs_login:
        return needs_login
    user_id = session.get("user_id") or get_user_id(session.get("email"))
    feedback_type = request.form.get("feedback_type", "general").strip()
    subject = request.form.get("subject", "").strip()
    message = request.form.get("message", "").strip()
    rating_raw = request.form.get("rating", "").strip()
    related_entity_type = request.form.get("related_entity_type", "").strip() or None
    related_entity_id_raw = request.form.get("related_entity_id", "").strip()
    related_entity_id = int(related_entity_id_raw) if related_entity_id_raw.isdigit() else None
    rating = int(rating_raw) if rating_raw.isdigit() else None
    if not subject or not message:
        return redirect(url_for("profile"))
    save_feedback_entry(user_id, feedback_type, subject, message, rating, related_entity_type, related_entity_id)
    save_notification(user_id, "Feedback Submitted", "Thanks for helping improve YouthAI.", "reminder")
    return redirect(url_for("profile"))


@app.post("/strategies/use/<int:strategy_id>")
def strategy_use(strategy_id):
    needs_login = require_login()
    if needs_login:
        return needs_login
    user_id = session.get("user_id") or get_user_id(session.get("email"))
    effectiveness_raw = request.form.get("effectiveness_feedback", "").strip()
    notes = request.form.get("notes", "").strip()
    effectiveness = int(effectiveness_raw) if effectiveness_raw.isdigit() else None
    save_strategy_usage(user_id, strategy_id, effectiveness, notes)
    return redirect(url_for("dashboard"))


@app.get("/profile")
def profile():
    needs_login = require_login()
    if needs_login:
        return needs_login
    return render_app("profile")


@app.post("/admin/users/<int:target_user_id>/role")
def admin_update_user_role(target_user_id):
    blocked = require_role("admin")
    if blocked:
        return blocked

    if target_user_id == session.get("user_id"):
        return redirect(url_for("profile"))

    new_role = request.form.get("role", "student").strip()
    if new_role not in ROLE_LEVELS:
        return redirect(url_for("profile"))

    update_user_role(target_user_id, new_role)
    save_notification(target_user_id, "Account Role Updated", f"Your account role is now {new_role}.", "reminder")
    log_admin_action(
        session.get("user_id"),
        "user_role_update",
        f"Changed user {target_user_id} role to {new_role}",
        affected_user_id=target_user_id,
        entity_type="user",
        entity_id=target_user_id,
    )
    return redirect(url_for("profile"))


@app.post("/admin/users/<int:target_user_id>/status")
def admin_update_user_status(target_user_id):
    blocked = require_role("admin")
    if blocked:
        return blocked

    if target_user_id == session.get("user_id"):
        return redirect(url_for("profile"))

    new_status = request.form.get("is_active", "1")
    set_user_active(target_user_id, new_status == "1")
    save_notification(
        target_user_id,
        "Account Status Changed",
        f"Your account is now {'active' if new_status == '1' else 'inactive'}.",
        "reminder",
    )
    log_admin_action(
        session.get("user_id"),
        "user_status_update",
        f"Set user {target_user_id} active status to {new_status}",
        affected_user_id=target_user_id,
        entity_type="user",
        entity_id=target_user_id,
    )
    return redirect(url_for("profile"))


@app.post("/admin/users/<int:target_user_id>/delete")
def admin_delete_user(target_user_id):
    blocked = require_role("admin")
    if blocked:
        return blocked
    if target_user_id == session.get("user_id"):
        return redirect(url_for("profile"))
    delete_user(target_user_id)
    log_admin_action(
        session.get("user_id"),
        "user_delete",
        f"Deleted user {target_user_id}",
        affected_user_id=target_user_id,
        entity_type="user",
        entity_id=target_user_id,
    )
    return redirect(url_for("profile"))


@app.post("/admin/feedback/<int:feedback_id>")
def admin_feedback_update(feedback_id):
    blocked = require_role("admin")
    if blocked:
        return blocked
    status = request.form.get("status", "reviewed").strip()
    admin_response = request.form.get("admin_response", "").strip()
    if status not in {"new", "reviewed", "resolved"}:
        return redirect(url_for("profile"))
    update_feedback_admin(feedback_id, status, admin_response)
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT user_id FROM feedback WHERE feedback_id = %s', (feedback_id,))
        row = cursor.fetchone()
        cursor.close()
        if row:
            save_notification(row["user_id"], "Feedback Updated", f"Your feedback status is now {status}.", "reminder", feedback_id)
    except Exception as e:
        print(f"Error notifying feedback update: {e}")
    log_admin_action(
        session.get("user_id"),
        "feedback_update",
        f"Updated feedback {feedback_id} to {status}",
        entity_type="feedback",
        entity_id=feedback_id,
    )
    return redirect(url_for("profile"))


@app.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
