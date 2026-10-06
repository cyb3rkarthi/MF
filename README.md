# Madras Foodies Consultancy — Full Stack Web Application

A professional hospitality consultancy website built with **Flask + MongoDB Atlas**.

---

## Project Structure

```
madras_foodies_fullstack/
│
├── app/                        # Application package
│   ├── __init__.py             # App factory (Flask + DB init)
│   ├── db.py                   # Database layer (MongoDB Atlas + SQLite fallback)
│   ├── routes.py               # All page routes and API endpoints
│   ├── email_service.py        # SMTP email notifications (async)
│   │
│   ├── templates/              # Jinja2 HTML templates
│   │   ├── base.html           # Base layout (nav, footer, WhatsApp button)
│   │   ├── home.html           # Home page (hero, services, projects, reviews)
│   │   ├── services.html       # Services page
│   │   ├── projects.html       # Projects portfolio page
│   │   ├── about.html          # About us page
│   │   └── contact.html        # Contact page (3 form tabs)
│   │
│   └── static/
│       ├── css/style.css       # All styles
│       └── js/main.js          # AJAX form handling, carousel, tabs
│
├── data/                       # SQLite fallback database (auto-created)
│   └── madras_foodies.db
│
├── run.py                      # Entry point — starts Flask server
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (never commit)
├── .env.example                # Template for .env
└── .gitignore
```

---

## Collections (MongoDB Atlas — `madras_foodies`)

| Collection    | Populated by              |
|---------------|---------------------------|
| `contacts`    | Contact Us form           |
| `clients`     | Client Details form       |
| `restaurants` | Restaurant Onboarding form|
| `reviews`     | Member Review form        |
| `projects`    | Auto-seeded on startup    |

---

## API Endpoints

| Method | Endpoint           | Action                        |
|--------|--------------------|-------------------------------|
| GET    | `/`                | Home page                     |
| GET    | `/services`        | Services page                 |
| GET    | `/projects`        | Projects page                 |
| GET    | `/about`           | About page                    |
| GET    | `/contact`         | Contact page                  |
| POST   | `/api/contacts`    | Save contact enquiry + email  |
| POST   | `/api/clients`     | Save client details + email   |
| POST   | `/api/restaurants` | Save restaurant details + email|
| POST   | `/api/reviews`     | Save member review            |
| GET    | `/api/projects`    | List projects (JSON)          |
| GET    | `/api/status`      | Health check (JSON)           |

---

## Setup & Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
copy .env.example .env
# Edit .env with your MongoDB URI and Gmail App Password

# 3. Start the server
python run.py
# → http://127.0.0.1:5000/
```

---

## Environment Variables (`.env`)

```
MONGO_URI=mongodb+srv://<user>:<password>@<cluster>.mongodb.net/
MONGO_DB=madras_foodies
SECRET_KEY=your-secret-key

SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=madrasfoodiesconsultancy@gmail.com
SMTP_PASSWORD=your-gmail-app-password
NOTIFICATION_RECIPIENT=madrasfoodiesconsultancy@gmail.com
```

---

## Tech Stack

- **Backend** — Python 3, Flask
- **Database** — MongoDB Atlas (primary), SQLite (auto-fallback)
- **Email** — Gmail SMTP via App Password (async background thread)
- **Frontend** — HTML5, CSS3, Vanilla JavaScript (no frameworks)
