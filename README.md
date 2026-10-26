# Mi Mundo

Mi Mundo is a personal productivity web application developed as the final project for Harvard's CS50x: Introduction to Computer Science.

The application brings together personal finance management, task organization, and learning progress tracking in a single, intuitive dashboard, helping users stay organized and monitor their daily activities.

---

## Features

### Dashboard
- Financial balance overview
- Pending tasks summary
- Active courses overview
- Average learning progress
- Daily motivational quote
- Interactive financial charts

### Budget Manager
- Add income and expenses
- Automatic balance calculation
- Expense categorization
- Export financial records to CSV

### Agenda
- Create and manage personal activities
- Organize tasks by category (Study, Exercise, Personal)
- Track pending activities

### Kanban Board
- Organize tasks visually
- Update task status (Pending, In Progress, Completed)

### Education Tracker
- Add courses with total modules or lessons
- Track learning progress
- Visual progress bars
- Edit and delete courses
- Automatic completion badge for finished courses

### Multi-language Support
- English and Spanish
- Dynamic language switching

### User Interface
- Responsive design with Tailwind CSS
- Dark mode support
- Clean and modern dashboard

---

## Technologies Used

### Backend
- Python
- Flask
- SQLite
- Jinja2

### Frontend
- HTML5
- Tailwind CSS
- JavaScript

### Libraries
- Chart.js

---

## Database

The application uses SQLite with the following main tables:

- users
- finances
- activities
- education

---

## Authentication

- User registration and login
- Secure password hashing
- Session-based authentication

---

## Installation

Clone the repository:

```bash
git clone https://github.com/DanielaM1293/MiMundo.git
cd MiMundo
```

Create and activate a virtual environment:

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Create a file named `.env` in the project folder with a secret key (the app will not start without it):

```
SECRET_KEY=put-a-long-random-text-here
```

You can generate a random key with:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Run the application:

```bash
flask run
```

---

## Environment Variables

| Variable | Required | Description |
| --- | --- | --- |
| `SECRET_KEY` | Yes | Secret key used to sign user sessions. Never commit it to GitHub. |
| `DATABASE_PATH` | No | Path of the SQLite file. Defaults to `mi_mundo.db` inside the project folder. |

---

## Deployment (Render)

The app is deployed on [Render](https://render.com) as a Web Service:

1. Create a new **Web Service** and connect this GitHub repository.
2. Build Command: `pip install -r requirements.txt`
3. Start Command: `gunicorn app:app`
4. In the **Environment** tab, add the variable `SECRET_KEY` with your own random value.
5. Save and deploy.

Live app: https://mimundo-y5rd.onrender.com

> Note: on Render's free plan the app goes to sleep when it is not used (the first visit can take about a minute) and the SQLite database is erased on every restart or new deploy. For permanent data, use a persistent disk or an external database.

---

## Project Objectives

This project demonstrates knowledge of:

- Full-stack web development
- Database design and management
- User authentication
- Frontend and backend integration
- Dynamic user interfaces
- CRUD operations
- Data visualization
- Responsive web design

---

## Demo

A video demonstration of the project will be submitted as part of the CS50 final project requirements.
https://youtu.be/z6laESd-FJg?si=0LP4tYCd17-YsaBA

---

## Author

**Daniela Martínez**

Final Project for **Harvard CS50x – Introduction to Computer Science**
