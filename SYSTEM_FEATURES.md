# YouthAI System Features & Architecture

## 🔹 1. SYSTEM FEATURES (FULL LIST)

### 🧠 Core AI Features
- Conversational AI chat (NLP-based)
- Sentiment/emotion detection (stress, motivation)
- Personalized recommendations:
  - Career paths
  - Skills & courses
  - Campus activities
- Behaviour tracking (long-term patterns)
- Proactive suggestions (not just reactive)

### 👤 User Features (Student)
- Register / Login account
- Create & edit profile (interests, goals, preferences)
- Chat with AI assistant
- View recommendations
- Track mood / emotional input
- Browse programs/events
- Search & filter activities
- Receive notifications

### 🏫 Staff Features
- Login (staff role)
- Upload programs/events
- Edit/delete programs
- Categorize programs (academic, sports, volunteering)

### ⚙️ Admin Features
- Manage users (create/remove)
- Manage roles (student/staff)
- Monitor system usage
- Ensure system integrity

### 🔍 System Features
- Search & filtering engine
- Recommendation engine
- Centralized database
- Role-based access control
- Real-time AI responses
- Notification system

---

## 🔹 2. APP REDIRECTION (BUTTON FLOW)

### 🧑‍🎓 Student Flow

#### 1. Authentication
- Login button → Dashboard
- Register button → Registration Page → Dashboard

#### 2. Dashboard
Main hub with buttons:
- "Chat with AI" → AI Chat Page
- "View Recommendations" → Recommendation Page
- "Explore Programs" → Program List Page
- "Profile" → Profile Page
- "Notifications" → Notification Page

#### 3. AI Chat Page
- Input message → AI response displayed
- "View Suggestions" → Recommendation Page
- "Save Insight" → Stored in profile/history

#### 4. Recommendation Page
- Career suggestion click → Career Details Page
- Skill/course click → Learning Resource Page
- Activity click → Program Details Page

#### 5. Program Page
- Program list → click → Program Details
- "Join/Register" → Confirmation / Saved events
- Filter button → Filter panel

#### 6. Profile Page
- Edit profile → Save changes → Update DB
- View history → Interaction history page

### 🏫 Staff Flow
- Login → Staff Dashboard
- "Add Program" → Create Program Page
- "Edit Program" → Update Page
- "Delete Program" → Remove from DB

### ⚙️ Admin Flow
- Login → Admin Panel
- Manage Users → User List Page
- Manage Roles → Role Settings
- System Logs → Monitoring Page

---

## 🔹 3. USER INTERACTION (HOW USERS USE SYSTEM)

### 👤 Student Interaction
1. Registers account
2. Inputs:
   - Interests
   - Goals
   - Feelings (via chat)
3. Chats with AI:
   - "I feel stressed"
   - "I don't know my career path"
4. System:
   - Analyzes emotion
   - Tracks patterns
   - Responds with advice
5. Gets:
   - Career suggestions
   - Activities
   - Coping strategies
6. Browses events & joins programs
7. Receives notifications

### 🏫 Staff Interaction
1. Logs in
2. Uploads event:
   - Title
   - Date
   - Category
   - Description
3. Updates/removes events

### ⚙️ Admin Interaction
1. Oversees system
2. Manages users
3. Ensures data security

---

## 🔹 4. DATABASE DESIGN (WHAT IS STORED)

### 🧑‍💻 1. Users Table
- `user_id` (PK)
- `name`
- `email`
- `password` (hashed)
- `role` (student/staff/admin)
- `created_at`

### 👤 2. User Profile Table
- `profile_id` (PK)
- `user_id` (FK)
- `interests`
- `goals`
- `preferences`

### 💬 3. Interaction / Chat History
- `chat_id` (PK)
- `user_id` (FK)
- `message`
- `ai_response`
- `timestamp`

### 📊 4. Behaviour Tracking
- `tracking_id` (PK)
- `user_id` (FK)
- `mood/emotion`
- `engagement_level`
- `detected_pattern`
- `timestamp`

### 🎯 5. Recommendations
- `rec_id` (PK)
- `user_id` (FK)
- `type` (career/skill/activity)
- `content`
- `relevance_score`
- `timestamp`

### 📅 6. Programs / Events
- `program_id` (PK)
- `title`
- `description`
- `category`
- `date`
- `created_by` (staff_id)

### 📌 7. User-Program Mapping (Join Table)
- `id` (PK)
- `user_id` (FK)
- `program_id` (FK)
- `status` (joined/saved)

### 🔔 8. Notifications
- `notification_id` (PK)
- `user_id` (FK)
- `message`
- `type`
- `is_read`
- `timestamp`

### 🔐 9. Admin Logs (Optional)
- `log_id`
- `action`
- `performed_by`
- `timestamp`

---

## 🔹 5. SYSTEM LOGIC (IMPORTANT INSIGHT)

### What makes this system different:

- **Not just chatbot** → tracks long-term behaviour
- **Not just job platform** → guides emotionally + career
- **Not just event system** → AI matches activities to users

---

## 🔹 6. KEY WORKFLOWS

### Mood Check → AI Chat Counseling Flow
1. Student does quick mood check (select mood emoji)
2. System records mood
3. Auto-redirects to AI Chat
4. AI asks counseling-style questions about the reason
5. Conversation proceeds with emotional support and guidance

### Career Guide → Program Recommendation Flow
1. Student answers career preference questions
2. System calculates career match scores
3. Auto-redirects to AI Chat
4. AI helps student choose from staff/admin-added programs
5. Programs are recommended based on:
   - Career path match
   - Mood/emotional state
   - Available campus activities
   - User interests

---

**Last Updated:** April 23, 2026  
**Version:** 1.0  
**Status:** Active Development
