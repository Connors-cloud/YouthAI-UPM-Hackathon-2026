# YouthAI Web Application Setup

## 👥 Team (UPM Hackathon 2026)

- Adam A. Tay – Project Manager  
- Muhammad Alif Azamrin – Developer  
- Nabhan Hakimi – QA & Database  
- Muhammad Aziem Asriel – System Design & UI/UX  

## Prerequisites

1. **XAMPP** (includes Apache, MySQL, and phpMyAdmin)
   - Download from: https://www.apachefriends.org/
   - Install and start XAMPP Control Panel

2. **Python 3.8+** with required packages
   - Install packages: `pip install -r requirements.txt`

## Database Setup

1. **Start MySQL and Apache in XAMPP**
   - Open XAMPP Control Panel
   - Start "MySQL" and "Apache" modules

2. **Access phpMyAdmin**
   - Open browser and go to: http://localhost/phpmyadmin
   - Default login: username `root`, password is empty (leave blank)

3. **Create Database (Optional)**
   - The application will automatically create the `youthai_db` database and `users` table on first run
   - You can verify this in phpMyAdmin after running the app

## Running the Application

```bash
cd "Web Version"
python app_web.py
```

Then open http://localhost:5000 in your browser.

## Database Configuration

The app is configured to connect to MySQL with these default settings:
- Host: localhost
- User: root
- Password: (empty)
- Database: youthai_db

To change these settings, modify the MySQL configuration in `app_web.py`:

```python
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''  # Your MySQL password
app.config['MYSQL_DB'] = 'youthai_db'
```

## Features

- User registration and login with MySQL database storage
- AI chat functionality with Gemini API
- Mood tracking and career assessment
- Program registration system

## Security Note

This is a development setup. For production:
- Use environment variables for database credentials
- Implement password hashing (bcrypt)
- Use HTTPS
- Add input validation and sanitization

## Gemini API key configuration

The desktop Gemini app (`TestAppHackathonGEMINI.py`) reads `GEMINI_API_KEY` from the process environment. If it is unset, the app uses local fallback responses; you can also enter a key in the Profile API Settings for the current session.

Set the variable locally before starting the app. Do not put a real key in Python, HTML, documentation, or Git history. The existing `.gitignore` excludes `.env` files; the desktop app does not load them automatically.

```bash
read -rsp "Gemini API key: " GEMINI_API_KEY; echo
export GEMINI_API_KEY
python TestAppHackathonGEMINI.py
unset GEMINI_API_KEY
```

If a key has been exposed, revoke it in its Google Cloud project (or Google AI Studio) and replace it in the environments that use it. Removing it from the latest source does not remove it from old commits or revoke it.
