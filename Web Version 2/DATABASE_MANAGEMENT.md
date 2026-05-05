# YouthAI Database Management Guide

## 📊 Database Overview

The YouthAI system uses **MySQL** with **17 tables** to manage all user data, interactions, and system information.

**Database Name:** `youthai_db`  
**Total Tables:** 17  
**Primary Key System:** All tables use INT AUTO_INCREMENT for unique IDs

---

## 🔧 Setup Instructions

### Step 1: Start XAMPP
1. Open XAMPP Control Panel
2. Click **Start** for Apache and MySQL
3. Click **Admin** button next to MySQL to open phpMyAdmin

### Step 2: Create Database (Automatic)
- When the Flask app starts, it automatically creates the `youthai_db` database
- All 17 tables are created automatically on first run
- Default data (career paths, self-care tips, coping strategies) are inserted

### Step 3: Manual Setup (If Needed)
If you need to manually set up the database:
1. In phpMyAdmin, go to **SQL** tab
2. Copy and paste the contents of `database_init.sql`
3. Click **Go** to execute all SQL commands

---

## 📋 Complete Table Schema

### 1. **users** - User Accounts
| Column | Type | Purpose |
|--------|------|---------|
| user_id | INT (PK, Auto) | Unique user identifier |
| name | VARCHAR(100) | Student/Staff name |
| email | VARCHAR(120) UNIQUE | Login email |
| password | VARCHAR(255) | Encrypted password |
| role | ENUM('student','staff','admin') | User type |
| created_at | TIMESTAMP | Account creation date |
| updated_at | TIMESTAMP | Last update |
| is_active | TINYINT | Account status (1=active) |

**Use Case:** Authentication and user management

---

### 2. **user_profiles** - Detailed User Info
| Column | Type | Purpose |
|--------|------|---------|
| profile_id | INT (PK) | Profile ID |
| user_id | INT (FK) | Links to users table |
| interests | JSON | User interests (array) |
| goals | JSON | Career/personal goals (array) |
| preferences | JSON | App preferences (array) |
| bio | TEXT | User biography |
| avatar_url | VARCHAR(255) | Profile picture |
| phone | VARCHAR(20) | Contact number |

**Use Case:** Store comprehensive user profile information

---

### 3. **chat_history** - Conversation Logs
| Column | Type | Purpose |
|--------|------|---------|
| chat_id | INT (PK) | Message ID |
| user_id | INT (FK) | Links to user |
| message | TEXT | User message |
| ai_response | TEXT | AI response |
| message_type | ENUM | 'text', 'mood_check', 'career_question', 'program_inquiry' |
| timestamp | TIMESTAMP | When message was sent |

**Use Case:** Track all conversations with AI for history and analysis

---

### 4. **behaviour_tracking** - Emotional Patterns
| Column | Type | Purpose |
|--------|------|---------|
| tracking_id | INT (PK) | Tracking ID |
| user_id | INT (FK) | Links to user |
| mood | VARCHAR(50) | Detected mood |
| emotion_score | INT | Score (1-10) |
| engagement_level | INT | Activity level |
| detected_pattern | VARCHAR(100) | Pattern identified |
| note | TEXT | Additional notes |
| timestamp | TIMESTAMP | Recording time |

**Use Case:** Identify emotional patterns over time

---

### 5. **mood_tracking** - Daily Mood Check-ins
| Column | Type | Purpose |
|--------|------|---------|
| mood_id | INT (PK) | Mood entry ID |
| user_id | INT (FK) | Links to user |
| mood_value | VARCHAR(50) | Mood selected (Terrible, Bad, Okay, Good, Great, Amazing) |
| mood_score | INT | Numeric score (1-6) |
| note | TEXT | Optional user note |
| date | DATE | Date of check-in |
| timestamp | TIMESTAMP | Exact time |

**Unique Constraint:** One mood entry per user per day  
**Use Case:** Track daily mood trends

---

### 6. **recommendations** - AI Suggestions
| Column | Type | Purpose |
|--------|------|---------|
| rec_id | INT (PK) | Recommendation ID |
| user_id | INT (FK) | Links to user |
| recommendation_type | ENUM | 'career', 'skill', 'activity', 'coping_strategy' |
| content | TEXT | Recommendation text |
| relevance_score | DECIMAL | 0.00-1.00 confidence |
| reason | TEXT | Why recommended |
| is_viewed | TINYINT | Whether user viewed it |
| viewed_at | TIMESTAMP | When viewed |

**Use Case:** Store and track AI recommendations

---

### 7. **programs** - Campus Events/Activities
| Column | Type | Purpose |
|--------|------|---------|
| program_id | INT (PK) | Program ID |
| title | VARCHAR(200) | Event name |
| description | TEXT | Full description |
| category | VARCHAR(50) | Workshop, Wellbeing, Sports, etc. |
| date | DATE | Event date |
| start_time | TIME | Start time |
| end_time | TIME | End time |
| location | VARCHAR(200) | Venue |
| capacity | INT | Max attendees |
| registration_count | INT | Current registrations |
| created_by | INT (FK) | Staff who created it |
| is_active | TINYINT | Event is active |

**Use Case:** Manage all campus programs and events

---

### 8. **user_programs** - Event Registrations
| Column | Type | Purpose |
|--------|------|---------|
| id | INT (PK) | Entry ID |
| user_id | INT (FK) | Links to user |
| program_id | INT (FK) | Links to program |
| status | ENUM | 'joined', 'saved', 'interested', 'attended' |
| registered_at | TIMESTAMP | Registration time |
| attended_at | TIMESTAMP | When attended |
| rating | INT | 1-5 star rating |
| feedback | TEXT | User feedback |

**Unique Constraint:** One status per user per program  
**Use Case:** Track user program participation

---

### 9. **notifications** - System Alerts
| Column | Type | Purpose |
|--------|------|---------|
| notification_id | INT (PK) | Notification ID |
| user_id | INT (FK) | Links to user |
| title | VARCHAR(200) | Notification title |
| message | TEXT | Full message |
| notification_type | ENUM | 'mood_insight', 'program_update', 'career_suggestion', 'reminder', 'achievement' |
| related_id | INT | Related entity ID |
| is_read | TINYINT | Read status |
| read_at | TIMESTAMP | When read |
| expires_at | TIMESTAMP | Expiration time |

**Use Case:** Send and manage user notifications

---

### 10. **admin_logs** - System Activity Tracking
| Column | Type | Purpose |
|--------|------|---------|
| log_id | INT (PK) | Log ID |
| admin_id | INT (FK) | Which admin did action |
| action_type | VARCHAR(100) | Type of action |
| action_description | TEXT | Details |
| affected_user_id | INT (FK) | User affected |
| affected_entity_type | VARCHAR(50) | What was modified |
| affected_entity_id | INT | ID of modified entity |
| ip_address | VARCHAR(45) | Admin IP |
| timestamp | TIMESTAMP | When action occurred |

**Use Case:** Audit trail for compliance and troubleshooting

---

### 11. **career_paths** - Career Options
| Column | Type | Purpose |
|--------|------|---------|
| career_id | INT (PK) | Career ID |
| career_name | VARCHAR(100) UNIQUE | Career name |
| description | TEXT | Career overview |
| related_jobs | JSON | Job titles (array) |
| skills_required | JSON | Required skills (array) |
| related_programs | TEXT | Recommended campus programs |

**Default Entries:**
- Technology
- Business
- Creative Arts
- Science
- Social Impact

---

### 12. **user_career_interests** - Career Match Tracking
| Column | Type | Purpose |
|--------|------|---------|
| interest_id | INT (PK) | Entry ID |
| user_id | INT (FK) | Links to user |
| career_id | INT (FK) | Links to career path |
| interest_score | INT | Matching score |
| last_updated | TIMESTAMP | Last update |

**Unique Constraint:** One interest per user per career  
**Use Case:** Track user career interest scores

---

### 13. **self_care_tips** - Wellness Resources
| Column | Type | Purpose |
|--------|------|---------|
| tip_id | INT (PK) | Tip ID |
| title | VARCHAR(200) | Tip title |
| content | TEXT | Full tip content |
| category | VARCHAR(50) | 'mindfulness', 'physical', 'social', 'reflection' |
| duration_minutes | INT | Time to complete |
| difficulty_level | ENUM | 'easy', 'moderate', 'challenging' |
| mood_tags | JSON | Applicable moods (array) |

**Default Entries:** 5 pre-loaded self-care tips

---

### 14. **coping_strategies** - Mental Health Techniques
| Column | Type | Purpose |
|--------|------|---------|
| strategy_id | INT (PK) | Strategy ID |
| mood_trigger | VARCHAR(100) | Triggered mood (stressed, anxious, sad) |
| strategy_title | VARCHAR(200) | Strategy name |
| description | TEXT | How it works |
| steps | JSON | Step-by-step instructions (array) |
| effectiveness_rating | DECIMAL | Effectiveness score (0.0-5.0) |

**Default Entries:** 5 evidence-based coping strategies

---

### 15. **user_strategy_usage** - Strategy History
| Column | Type | Purpose |
|--------|------|---------|
| usage_id | INT (PK) | Usage ID |
| user_id | INT (FK) | Links to user |
| strategy_id | INT (FK) | Links to strategy |
| used_at | TIMESTAMP | When used |
| effectiveness_feedback | INT | 1-5 effectiveness rating |
| notes | TEXT | User notes |

**Use Case:** Track which strategies work best for each user

---

### 16. **achievements** - Gamification
| Column | Type | Purpose |
|--------|------|---------|
| achievement_id | INT (PK) | Achievement ID |
| user_id | INT (FK) | Links to user |
| badge_name | VARCHAR(100) | Badge name |
| description | TEXT | What was achieved |
| icon_url | VARCHAR(255) | Badge icon image |
| earned_at | TIMESTAMP | When earned |

**Use Case:** Gamify user engagement with achievements

---

### 17. **feedback** - User Feedback
| Column | Type | Purpose |
|--------|------|---------|
| feedback_id | INT (PK) | Feedback ID |
| user_id | INT (FK) | Links to user |
| feedback_type | VARCHAR(50) | Type of feedback |
| subject | VARCHAR(200) | Feedback subject |
| message | TEXT | Feedback message |
| rating | INT | 1-5 star rating |
| related_entity_type | VARCHAR(50) | What feedback is about |
| related_entity_id | INT | ID of entity |
| status | ENUM | 'new', 'reviewed', 'resolved' |
| admin_response | TEXT | Admin response |

**Use Case:** Collect and manage user feedback

---

## 🔍 Common phpMyAdmin Operations

### View a Table
1. In phpMyAdmin, click on the table name in the left menu
2. Scroll through data or use search bar
3. Click pencil icon to edit rows

### Add New Data
1. Go to **Insert** tab
2. Fill in the form fields
3. Click **Go** to save

### Query Data with SQL
1. Go to **SQL** tab
2. Enter your query (e.g., `SELECT * FROM users WHERE role = 'student'`)
3. Click **Go** to execute

### Example Queries

**Find all students:**
```sql
SELECT * FROM users WHERE role = 'student';
```

**Get user mood history (last 7 days):**
```sql
SELECT user_id, mood_value, date FROM mood_tracking 
WHERE user_id = 1 AND date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
ORDER BY date DESC;
```

**Find all unread notifications:**
```sql
SELECT * FROM notifications WHERE is_read = 0 ORDER BY created_at DESC;
```

**Get most popular programs:**
```sql
SELECT program_id, title, COUNT(*) as registrations 
FROM user_programs 
GROUP BY program_id 
ORDER BY registrations DESC 
LIMIT 10;
```

**Find user career interests:**
```sql
SELECT u.name, cp.career_name, uci.interest_score
FROM user_career_interests uci
JOIN users u ON uci.user_id = u.user_id
JOIN career_paths cp ON uci.career_id = cp.career_id
WHERE uci.user_id = 1;
```

---

## 🛡️ Data Security & Maintenance

### Regular Backups
1. In phpMyAdmin, click **Export**
2. Select all tables
3. Choose **SQL** format
4. Click **Go** to download backup

### Regular Cleanup
1. Delete old notifications: `DELETE FROM notifications WHERE expires_at < CURDATE();`
2. Archive old chat history (optional): `SELECT * FROM chat_history WHERE timestamp < DATE_SUB(CURDATE(), INTERVAL 1 YEAR);`

### Monitor Database Size
1. Click on **youthai_db** in left menu
2. Check **Information** tab for space usage

---

## 📝 Initial Data Setup

When the app starts, these defaults are inserted:

### Career Paths (5 total)
- Technology
- Business
- Creative Arts
- Science
- Social Impact

### Self-Care Tips (5 total)
- 5-Minute Breathing Break
- Drink Water & Stretch
- Gratitude Journal
- 15-Minute Walk
- Peer Check-In

### Coping Strategies (5 total)
- Box Breathing (for stress)
- Grounding Technique (for anxiety)
- Positive Activity Scheduling (for sadness)
- Task Breakdown (for overwhelm)
- Social Connection (for loneliness)

---

## ✅ Checklist for Initial Setup

- [ ] XAMPP running with MySQL active
- [ ] Flask app started (runs `init_db()`)
- [ ] phpMyAdmin accessible at `http://localhost/phpmyadmin`
- [ ] Database `youthai_db` created
- [ ] All 17 tables created
- [ ] Default data inserted
- [ ] App stores data on chat/mood interactions
- [ ] Database backups scheduled

---

## 🚀 Next Steps

1. **Import existing data** - If migrating from another system
2. **Create staff accounts** - Add staff users for program management
3. **Upload programs** - Add campus programs through the app
4. **Monitor usage** - Check analytics through phpMyAdmin queries
5. **Backup regularly** - Export database weekly

---

**Last Updated:** April 23, 2026  
**Version:** 1.0  
**Status:** Production Ready
