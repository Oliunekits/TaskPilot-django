# TaskPilot — Django 
Task Manager

Fullstack pet-project built with **Django + HTML/CSS (Bootstrap) + HTMX**.
Includes authentication, per-user data isolation, CRUD, Kanban board, and Dockerized setup.

## Features
- Auth: register / login / logout
- Projects & tasks CRUD
- Kanban board: To Do / In Progress / Done
- Task labels (M2M), priorities, due dates
- Comments (HTMX partial updates)
- Search & filters
- Admin panel
- Docker (Gunicorn + WhiteNoise)

## Tech Stack
- Python, Django
- SQLite
- Bootstrap 5, HTMX
- Docker, Gunicorn, WhiteNoise

## Local run
- bash
- python -m venv .venv

Windows
- .venv\Scripts\activate
- pip install -r requirements.txt
- python manage.py migrate
- python manage.py runserver

# Docker run
- docker compose up --build
- docker compose exec web python manage.py migrate
- docker compose exec web python manage.py createsuperuser

## open project
- Open: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/
