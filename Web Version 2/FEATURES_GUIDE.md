# YouthAI - New Features & Implementation Guide

## ✨ Features Added

### Data Persistence
All user interactions are now automatically saved to the database:
- ✅ Chat messages stored in `chat_history` table
- ✅ Mood check-ins stored in `mood_tracking` table
- ✅ Career assessments stored in `recommendations` table
- ✅ Program registrations stored in `user_programs` table

### Comprehensive Mood Tracking
- **Table:** `mood_tracking`
- Records daily mood check-ins with optional notes
- Automatic timestamp recording
- One entry per user per day (prevents duplicates)
- Mood scores range from 1-6

### AI Conversation History
- **Table:** `chat_history`
- Stores every message between user and AI
- Categorizes messages by type (text, mood_check, career_question, program_inquiry)
- Enables conversation analysis and pattern detection

### Career Path Guidance
- **Table:** `career_paths` + `user_career_interests`
- 5 default career paths: Technology, Business, Creative Arts, Science, Social Impact
- Tracks user interest scores for each career
- Links careers to related jobs and skills

### Behaviour & Pattern Recognition
- **Table:** `behaviour_tracking`
- Tracks emotional patterns over time
- Records engagement levels
- Detects recurring patterns in mood and behavior
- Enables proactive AI suggestions

### Program Management & Registration
- **Table:** `programs` + `user_programs`
- Staff can create campus programs/events
- Students can join, save, or mark interested in programs
- Tracks attendance and feedback
- Program categories and filtering

### Self-Care & Coping Resources
- **Table:** `self_care_tips` + `coping_strategies`
- 5 pre-loaded self-care tips
- 5 evidence-based coping strategies
- Tagged by mood trigger and difficulty level
- User can track which strategies work best

### Gamification
- **Table:** `achievements`
- Award badges for milestones
- Track user engagement through achievements
- Motivate continued app usage

### User Notifications
- **Table:** `notifications`
- Send mood insights, program updates, career suggestions
- Read status tracking
- Notification expiration
- Multiple notification types

### System Admin Logging
- **Table:** `admin_logs`
- Track all administrative actions
- IP address and user agent logging
- Audit trail for compliance

### User Feedback Collection
- **Table:** `feedback`
- Collect ratings and feedback on programs
- Track issues and suggestions
- Admin response system
- Status tracking (new, reviewed, resolved)

---

## 🔄 How New Features Work

### Mood Check-in Flow

```
User selects mood emoji on Dashboard
         ↓
Mood saved to mood_tracking table
         ↓
Chat message added to chat_history
         ↓
AI responds with counseling-style question
         ↓
Redirects to AI Chat page
         ↓
Conversation continues with DB persistence
```

### Career Assessment Flow

```
User answers 3 career preference questions
         ↓
Scores calculated for each career path
         ↓
Recommendation created in recommendations table
         ↓
Career interest score saved/updated
         ↓
AI message added to chat_history
         ↓
Redirects to AI Chat with program suggestions
         ↓
Conversation continues with program recommendations
```

### Program Registration Flow

```
User clicks "Join" on program
         ↓
Status saved to user_programs table
         ↓
User can later rate and provide feedback
         ↓
Data available for program analytics
```

---

## 📊 Database Functions Added

### `get_user_id(email)`
**Purpose:** Retrieve user_id from email address  
**Usage:** Used by all database save functions to get the current user's ID  
**Returns:** Integer user_id or None

### `save_chat_to_db(user_id, user_message, ai_response, message_type)`
**Purpose:** Save chat messages to database  
**Parameters:**
- `user_id`: Integer user ID
- `user_message`: User's message text
- `ai_response`: AI's response text
- `message_type`: 'text', 'mood_check', 'career_question', 'program_inquiry'

### `save_mood_to_db(user_id, mood_value, note)`
**Purpose:** Save mood check-in to database  
**Parameters:**
- `user_id`: Integer user ID
- `mood_value`: One of (Terrible, Bad, Okay, Good, Great, Amazing)
- `note`: Optional user note

### `save_recommendation_to_db(user_id, rec_type, content, reason)`
**Purpose:** Save AI recommendations  
**Parameters:**
- `user_id`: Integer user ID
- `rec_type`: 'career', 'skill', 'activity', 'coping_strategy'
- `content`: Recommendation text
- `reason`: Why it's recommended

### `save_program_registration(user_id, program_id, status)`
**Purpose:** Save program registration/updates  
**Parameters:**
- `user_id`: Integer user ID
- `program_id`: Integer program ID
- `status`: 'joined', 'saved', 'interested', 'attended'

---

## 🚀 Routes Updated for Database

### `/chat/send` (POST)
- Saves chat messages to `chat_history` table
- Records both user message and AI response
- Categorizes as 'text' type

### `/mood/save` (POST)
- Saves mood with optional note to `mood_tracking` table
- One entry per day (duplicate key update)

### `/mood/quick/<mood_value>` (POST)
- Saves mood to `mood_tracking` table
- Creates counseling-style AI message
- Saves message to `chat_history` with type 'mood_check'
- Redirects to chat page

### `/career/submit` (POST)
- Calculates career scores
- Saves career recommendation to `recommendations` table
- Creates AI message with program suggestions
- Saves to `chat_history` with type 'career_question'
- Redirects to chat page

### `/programs/join/<pid>` (POST)
- Saves user program registration to `user_programs` table
- Status set to 'joined'

---

## 📈 Analytics Queries

### Get User's Mood Trend
```sql
SELECT date, mood_value, mood_score FROM mood_tracking 
WHERE user_id = ? 
ORDER BY date DESC 
LIMIT 30;
```

### Find Most Popular Programs
```sql
SELECT p.program_id, p.title, COUNT(up.id) as registrations
FROM programs p
LEFT JOIN user_programs up ON p.program_id = up.program_id
GROUP BY p.program_id
ORDER BY registrations DESC;
```

### Get User's Career Interests
```sql
SELECT cp.career_name, uci.interest_score
FROM user_career_interests uci
JOIN career_paths cp ON uci.career_id = cp.career_id
WHERE uci.user_id = ?
ORDER BY uci.interest_score DESC;
```

### Track User Engagement
```sql
SELECT 
    u.name,
    COUNT(DISTINCT DATE(ch.timestamp)) as chat_days,
    COUNT(DISTINCT mt.date) as mood_check_days,
    COUNT(up.id) as programs_joined
FROM users u
LEFT JOIN chat_history ch ON u.user_id = ch.user_id
LEFT JOIN mood_tracking mt ON u.user_id = mt.user_id
LEFT JOIN user_programs up ON u.user_id = up.user_id
GROUP BY u.user_id
ORDER BY chat_days DESC;
```

---

## 🔌 Integration Points

### Session Management
- User email stored in session
- `get_user_id()` retrieves user_id from email
- All database operations use user_id as reference

### Automatic Data Flow
1. User interacts with app (chat, mood, career)
2. Session-state updated (existing behavior)
3. Database saved (new behavior)
4. Data persists across sessions

### Default Data Insertion
On app startup (`init_db()`):
- Career paths inserted if table empty
- Self-care tips loaded once
- Coping strategies loaded once

---

## ✅ Testing Checklist

- [ ] Create new user account
- [ ] Submit mood check - verify in DB
- [ ] Send chat message - verify in DB
- [ ] Complete career assessment - verify recommendations in DB
- [ ] Join program - verify in user_programs table
- [ ] Check mood_tracking table has entries
- [ ] Check chat_history table has all messages
- [ ] Verify user_id correctly linked to all data
- [ ] Run backup and verify SQL dump
- [ ] Check all timestamps are correct

---

## 🔮 Future Features (Recommendations)

1. **Notification System**
   - Auto-generate mood insights: "Your mood has improved 20%"
   - Program reminders: "Event starts in 2 hours"
   - Achievement badges: "Completed 10 chat sessions!"

2. **Advanced Analytics**
   - Mood improvement trends
   - Program attendance statistics
   - Career path recommendations based on behavior
   - Peer comparison analytics (anonymized)

3. **Staff Dashboard**
   - Program attendance tracking
   - Student engagement metrics
   - Program effectiveness scoring
   - Student well-being reports

4. **Admin Panel**
   - User management (create, deactivate accounts)
   - System health monitoring
   - Database maintenance tools
   - Audit log viewer

5. **AI Enhancements**
   - Personalized recommendations based on historical data
   - Predictive alerts (detect concerning mood patterns)
   - Career path analysis with success rates
   - Sentiment analysis on feedback

6. **Mobile App**
   - Native iOS/Android apps
   - Push notifications
   - Offline mode
   - Biometric authentication

---

## 📞 Support & Troubleshooting

### Issue: Data not saving to database
**Solution:** 
- Verify XAMPP MySQL is running
- Check app logs for database connection errors
- Verify user_id is retrieved correctly with `get_user_id()`

### Issue: Duplicate mood entries
**Solution:**
- Unique constraint on (user_id, date) prevents duplicates
- DUPLICATE KEY UPDATE handles updates automatically

### Issue: Slow database queries
**Solution:**
- Verify indexes are created (they are by default)
- Check phpMyAdmin explain plan
- Consider archiving old chat history

### Issue: Out of disk space
**Solution:**
- Archive old data to external storage
- Use `OPTIMIZE TABLE` command to reclaim space
- Consider partitioning large tables

---

**Last Updated:** April 23, 2026  
**Version:** 1.0  
**Compatibility:** Flask + MySQL + XAMPP
