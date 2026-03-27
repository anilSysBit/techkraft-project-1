# Real Estate Buyer Portal – Backend

## Overview

This is the Django backend for a Buyer Portal application built as part of a full-stack take-home assessment.

It provides:
- User authentication (register, login, logout)
- Property listing APIs
- User-specific favourites management
- Secure access control (users only see their own data)

The frontend is implemented separately and connects to this API.

---

## Tech Stack

- Django
- Django REST Framework
- SQLite
- Token-based Authentication

---

## API Endpoints

### Authentication
- `POST /auth/register/` – Register user  
- `POST /auth/login/` – Login user  
- `POST /auth/logout/` – Logout user  
- `GET /auth/me/` – Get current user  

### Properties
- `GET /properties/` – List properties  
- `GET /properties/<id>/` – Property detail  

### Favourites
- `GET /favourites/` – Get user favourites  
- `POST /favourites/add/` – Add favourite  
- `DELETE /favourites/remove/<property_id>/` – Remove favourite  
- `POST /favourites/toggle/<property_id>/` – Toggle favourite  

---

## How to Run the Application

This project consists of **two repositories**:

- Backend (Django API):  
  https://github.com/anilSysBit/techkraft-project-1.git  

- Frontend (React Buyer Portal):  
  https://github.com/anilSysBit/property.git  

---

## 1. Setup and Run Backend

### Clone backend repo

```bash
git clone https://github.com/anilSysBit/techkraft-project-1.git
cd techkraft-project-1


# Create virtual environment
python -m venv techkraftenv
Activate:

# Windows

techkraftenv\Scripts\activate

macOS / Linux

source techkraftenv/bin/activate
# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py makemigrations
python manage.py migrate
# Start server
python manage.py runserver

# Backend runs at:

http://127.0.0.1:8000/