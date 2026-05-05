# YouthAI Database Quick Reference

## 🚀 Quick Start (3 Steps)

1. **Start XAMPP**
   - Apache: Start
   - MySQL: Start

2. **Run Flask App**
   ```bash
   python app_web.py
   ```

3. **Verify Database**
   - phpMyAdmin: `http://localhost/phpmyadmin`
   - Database: `youthai_db`
   - Should see 17 tables

---

## 📊 17 Database Tables at a Glance

| # | Table Name | Purpose | Key Field |
|---|------------|---------|-----------|
| 1 | users | User accounts | user_id |
| 2 | user_profiles | Profile details | profile_id → user_id |
| 3 | chat_history | AI conversations | chat_id → user_id |
| 4 | mood_tracking | Daily mood check-ins | mood_id → user_id |
| 5 | behaviour_tracking | Emotional patterns | tracking_id → user_id |
| 6 | recommendations | AI suggestions | rec_id → user_id |
| 7 | programs | Campus events | program_id |
| 8 | user_programs | Event registrations | id → (user_id, program_id) |
| 9 | notifications | System alerts | notification_id → user_id |
| 10 | admin_logs | Audit trail | log_id → admin_id |
| 11 | career_paths | Career options | career_id |
| 12 | user_career_interests | Career scores | interest_id → (user_id, career_id) |
| 13 | self_care_tips | Wellness tips | tip_id |
| 14 | coping_strategies | Mental health techniques | strategy_id |
| 15 | user_strategy_usage | Strategy history | usage_id → (user_id, strategy_id) |
| 16 | achievements | Gamification badges | achievement_id → user_id |
| 17 | feedback | User feedback | feedback_id → user_id |

---

## 🔄 Data Flow Diagrams

### Mood Check
```
Dashboard → mood emoji → /mood/quick/<mood> → 
  mood_tracking table ↓
  chat_history table ↓
  → AI Chat page
```

### Career Assessment
```
Career page → answers → /career/submit → 
  recommendations table ↓
  career_interests table ↓
  chat_history table ↓
  → AI Chat with suggestions
```

### Chat Message
```
Chat input → /chat/send →
  chat_history (user message) ↓
  chat_history (AI response) ↓
  → Display in UI
```

### Program Join
```
Programs page → Join button → /programs/join/<id> →
  user_programs table (status='joined') ↓
  → Updated programs page
```

---

## 🔧 Database Functions (Quick Reference)

```python
# Get user ID
user_id = get_user_id(session.get("email"))

# Save chat
save_chat_to_db(user_id, "my message", "ai response", "text")

# Save mood
save_mood_to_db(user_id, "Great", "optional note")

# Save recommendation
save_recommendation_to_db(user_id, "career", "Technology", "matched your answers")

# Save program registration
save_program_registration(user_id, program_id, "joined")
```

---

## 📈 Useful SQL Queries

### Get user's recent mood
```sql
SELECT mood_value, date FROM mood_tracking 
WHERE user_id = 1 
ORDER BY date DESC LIMIT 7;
```

### Get user's chat history
```sql
SELECT message, ai_response, timestamp FROM chat_history
WHERE user_id = 1 
ORDER BY timestamp DESC LIMIT 50;
```

### Get popular programs
```sql
SELECT program_id, title, COUNT(*) as registrations
FROM user_programs
GROUP BY program_id
ORDER BY registrations DESC;
```

### Get user's career interests
```sql
SELECT cp.career_name, uci.interest_score
FROM user_career_interests uci
JOIN career_paths cp ON uci.career_id = cp.career_id
WHERE uci.user_id = 1;
```

### Get user engagement
```sql
SELECT 
    COUNT(DISTINCT DATE(timestamp)) as chat_days,
    COUNT(*) as total_messages
FROM chat_history
WHERE user_id = 1;
```

---

## 🎯 Common Tasks

### How to backup database
1. phpMyAdmin → Export
2. Select `youthai_db`
3. Format: SQL
4. Download `.sql` file

### How to view user data
1. phpMyAdmin → users table
2. Click user → pencil icon
3. View all related data

### How to check mood trend
```sql
SELECT date, mood_value, mood_score 
FROM mood_tracking 
WHERE user_id = ? 
ORDER BY date DESC;
```

### How to reset a user
```sql
DELETE FROM users WHERE email = 'user@example.com';
```
(Cascades delete all related data)

---

## ✅ Features Checklist

- [x] User registration & login
- [x] Mood tracking (daily)
- [x] AI chat history
- [x] Career assessment
- [x] Program registration
- [x] Behavior tracking
- [x] Notifications
- [x] Admin logging
- [x] User feedback
- [x] Coping strategies
- [x] Self-care tips
- [x] Achievements
- [x] Career paths

---

## 📝 Default Data

**Career Paths (5)**
- Technology
- Business
- Creative Arts
- Science
- Social Impact

**Self-Care Tips (5)**
- 5-Minute Breathing Break
- Drink Water & Stretch
- Gratitude Journal
- 15-Minute Walk
- Peer Check-In

**Coping Strategies (5)**
- Box Breathing (stress)
- Grounding Technique (anxiety)
- Positive Activity Scheduling (sadness)
- Task Breakdown (overwhelm)
- Social Connection (loneliness)

---

## 🔐 Security Notes

- Passwords stored (should be hashed - TODO)
- User_id used as primary key
- Foreign keys enforce data integrity
- Admin_logs track all actions
- Role-based access control implemented

---

## 📞 Troubleshooting

| Problem | Solution |
|---------|----------|
| Database not created | Run Flask app, check console logs |
| No tables visible | Refresh phpMyAdmin, verify `youthai_db` |
| Data not saving | Check `get_user_id()` returns value |
| Slow queries | Check indexes are present |
| Duplicate moods | Normal - ON DUPLICATE KEY UPDATE prevents |

---

## 🚀 What's Ready

✅ Core database system  
✅ Data persistence for all main features  
✅ User account management  
✅ Mood & behavior tracking  
✅ Chat history logging  
✅ Career path guidance  
✅ Program management  
✅ Notification system  
✅ Admin audit trail  

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `database_init.sql` | SQL schema (run once) |
| `DATABASE_MANAGEMENT.md` | Complete management guide |
| `FEATURES_GUIDE.md` | Feature implementation details |
| `IMPLEMENTATION_REPORT.md` | Summary of all changes |
| `SYSTEM_FEATURES.md` | System architecture |
| `QUICK_REFERENCE.md` | This file |

---

**YouthAI | Database System v1.0**  
**Status: Production Ready** ✅  
**Last Updated: April 23, 2026**
