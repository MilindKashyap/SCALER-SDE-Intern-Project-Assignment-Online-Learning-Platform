# SCALER-SDE-Intern-Project-Assignment-Online-Learning-Platform
Mini LMS is a simple learning platform where teachers upload lectures &amp; quizzes, and students learn, attempt, and track progress.

🎓 Mini LMS - Online Learning Platform 

learning-management-system/
├── README.md                 # Comprehensive documentation
├── requirements.txt          # Python dependencies
├── .gitignore               # Git ignore rules
└── lms_backend/             # Django project
    ├── manage.py
    ├── lms_project/         # Django settings
    ├── users/              # User management
    ├── courses/            # Course management
    ├── lectures/           # Lecture content
    ├── quizzes/            # Quiz system
    ├── enrollments/        # Student enrollments
    ├── progress/           # Progress tracking
    ├── templates/          # HTML templates
    ├── static/             # CSS, JS files
    └── media/              # Uploaded files

📌 Overview

A full-stack web application designed as part of an SDE Intern Assignment.

Supports two main roles:

Instructor → Can create/manage courses, lectures, and quizzes.

Student → Can browse courses, complete lectures, attempt quizzes, and track progress.

Built with a focus on security, scalability, and user experience.

👩‍🏫 Instructor Features

Course Management

Create, update, and delete courses.

Assign course descriptions and titles.

Lecture Management

Upload lecture materials in PDF format.

Secure storage in the database.

Delete lectures when needed.

Quiz Management

Create quizzes with multiple-choice questions (MCQs).

Quizzes are time-bound (with start and end dates).

Delete quizzes if required.

Student Assessment

View student quiz submissions.

Assign marks and track performance.

👨‍🎓 Student Features

User Access

Sign up and log in with role-based permissions.

Course Access

Browse all available courses with a search feature.

View uploaded lecture PDFs.

Learning Flow

Mark lectures as completed.

Sequential navigation → move to the next lecture after completing the previous one.

Quizzes & Scores

Attempt quizzes within the time frame.

Get instant scores after submission.

Progress Tracking

Track personal course completion (e.g., 5/10 lectures completed).

📊 System Features

Authentication & Authorization

Role-based access control for Students & Instructors.

Secure login using JWT authentication.

Security

CSRF protection for forms.

File validation for secure uploads (lectures, images).

Real-Time Features

Live progress tracking.

Time-bound quizzes.

UI/UX

Responsive design (mobile, tablet, desktop).

Light/Dark mode supported.

🛠️ Technology Stack

Backend → Python 3.9+, Django 5.2.5 (scalable, secure).

API → Django REST Framework (serialization, auth, permissions).

Authentication → DRF Simple JWT (stateless, secure token-based).

Database → SQLite (lightweight, portable for dev).

Frontend → Bootstrap 5 (responsive, modern UI).

Styling → CSS Variables (dark/light mode).

Forms → Django Crispy Forms (Bootstrap integration).

Media → Pillow (image/file validation & processing).

Icons → Bootstrap Icons.

Fonts → Google Fonts (Inter for readability).

📂 Project Architecture

backend/ → Django backend (API, ORM, Auth, Business logic).

frontend/ → Templates, Bootstrap, CSS.

media/ → Uploaded files (PDFs, profile images).

static/ → Static assets (CSS, JS, images).

manage.py → Project runner.

requirements.txt → Python dependencies.

README.md → Documentation.

🚀 Setup & Installation

Clone repo → git clone ...

Create virtual environment → python -m venv venv

Install dependencies → pip install -r requirements.txt

Run migrations → python manage.py migrate

Create superuser → python manage.py createsuperuser

Start server → python manage.py runserver

Access at → http://127.0.0.1:8000/

🔒 Security Features

CSRF protection.

JWT Authentication (secure APIs).

Role-based access control.

File validation & safe uploads.

📱 Responsive Design

Mobile-first using Bootstrap 5.

Dark/Light mode toggle with CSS variables.

Scales for tablets & desktops seamlessly.

✨ Bonus Features

Search for courses.

Instructor file uploads.

Real-time tracking of progress.

Time-bound quizzes.
