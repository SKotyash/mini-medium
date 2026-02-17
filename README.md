# Mini Medium (Flask)

Mini Medium is a full-featured blogging platform inspired by Medium.
The project was built as a backend-focused pet project to practice Flask,
application architecture, and real-world backend patterns.

---
# Live-Demo

https://mini-medium-remki.onrender.com/
---

## 🚀 Features

### Authentication & Roles
- User registration and login
- Role-based access control:
  - User
  - Moderator
  - Admin
- Custom decorators for permissions
- User ban & mute system

### Posts
- Create, edit, delete posts
- Post lifecycle:
  - Draft
  - On review
  - Published
  - Rejected
- Post moderation by moderators/admins
- Pagination for posts
- Search by post title

### Social Features
- Follow / unfollow users
- Personalized feed based on followed authors
- Likes with unique constraint
- Comments system

### Notifications System
- Notifications for:
  - New posts from followed users
  - Likes
  - Comments
  - Mute / unmute events
- Mark all notifications as read
- Mark single notification as read
- Notification links to related content

### Moderation & Security
- Admin panel for moderation
- User banning
- Temporary mute with automatic unmute
- Background scheduler to remove expired mutes
- CSRF protection
- Access checks on all sensitive actions

---

## 🧱 Tech Stack

- **Python 3**
- **Flask**
- **Flask-SQLAlchemy**
- **Flask-Migrate**
- **Flask-WTF (CSRF protection)**
- **Flask-APScheduler**
- **SQLite**(development)
- **PostgreSQL**(production ready)
- **Jinja2**
- **Werkzeug security (password hashing)**

---

## 🏗 Project Architecture

The project follows a modular architecture:

- **Blueprints** — route separation by domain
- **Service layer** — business logic (notifications, moderation, follows)
- **Decorators** — access control and permissions
- **Models** — ORM models with domain methods
- **Background jobs** — scheduled tasks for system maintenance


---

## ⚙️ Installation & Run



### 1. Clone repository
````
git clone https://github.com/SKotyash/mini-medium.git
cd mini-medium
````
### 2. Create virtual environment

Windows:
````
python -m venv venv
venv\Scripts\activate
````

Linux/MacOS

````
python3 -m venv venv
source venv/bin/activate
````

### 3. Install dependencies
````
pip install -r requirements.txt
````

### 4. Set environment variables
Create a .env file in the root directory:
````
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///app.db
````


If you are not using python-dotenv, you can set variables manually:

Windows (PowerShell):
````
$env:SECRET_KEY="your-secret-key"
$env:DATABASE_URL="sqlite:///app.db"
````
Linux/MacOS:
````
export SECRET_KEY="your-secret-key"
export DATABASE_URL="sqlite:///app.db"
````

### 5. Initialize database (first run)
````
flask db upgrade
````

If migrations are not initialized yet:

````
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
````

### 6. Run the application
````
flask run
````

Application will be available at:
````
http://127.0.0.1:5000
````
### 7. Creating the First Admin
**Note:** On the first launch, the very first registered user is automatically assigned the `admin` role. 

If you need to create an admin manually via Flask Shell 
```bash
flask shell
```
Run these commands inside the shell:
```python
from app import db
from models import User
from werkzeug.security import generate_password_hash

# Create admin user with 'admin' role string
admin = User(
    username="admin",
    email="admin@example.com",
    password_hash=generate_password_hash("admin123"),
    role="admin",  
    is_banned=False,
    is_muted=False
)

db.session.add(admin)
db.session.commit()
exit()

```

## 🧠 Key Backend Concepts Demonstrated
Role-based access control
- Service layer separation
- Background jobs with APScheduler
- Notification system design
- Pagination & filtering
- Secure authentication
- SQLAlchemy relationships and constraints
- Production-oriented project structure

## 📈 Future Improvements
- REST API + frontend separation
- Email notifications
- Real-time notifications (WebSockets)
- Full-text search
- Dockerization
- Test coverage (pytest)

## 🙌 Credits & Acknowledgments

- **Inspiration**: [Medium](https://medium.com) for the clean UI and social blogging concept.
- **UI/UX**: HTML templates and Bootstrap 5 layouts were prototyped and polished with the help of **AI (ChatGPT/Claude)**.
- **Background Processing**: Logic for automated unmuting is powered by **Flask-APScheduler**.
- **Avatars**: Default user avatars are provided by [DiceBear API](https://www.dicebear.com).
