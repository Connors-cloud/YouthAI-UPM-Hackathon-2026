# YouthAI Web Application Setup

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