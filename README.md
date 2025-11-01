<div id="top"></div>

<br />
<div align="center">
  <a href="">
    <img src="docs/images/chookhub-logo.svg" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">🐔 C H O O K H U B</h3>

  <p align="center">
    A modern recipe management and cooking platform built with Django and React.
    <br />
    <a href="#getting-started"><strong>Get Started »</strong></a>
    <br />
    <br />
    <a href="https://github.com/LauraMalinaBenchea/CookHub">GitHub</a>
    ·
    <a href="#features">Features</a>
    ·
    <a href="#development">Development</a>
  </p>
</div>

---

<details>
  <summary><strong>Contents</strong></summary>
  <ol>
    <li><a href="#overview">Overview</a></li>
    <li><a href="#features">Features</a></li>
    <li><a href="#getting-started">Getting Started</a></li>
    <li><a href="#development">Development</a></li>
    <li><a href="#common-issues">Common Issues</a></li>
    <li><a href="#credits">Credits</a></li>
  </ol>
</details>

---

## 🧠 Overview

**Chookhub** is a full-stack web app for managing, generating, and sharing cooking recipes.
It combines a **Django backend** for data management and APIs with a **React + Tailwind CSS** frontend for an interactive user experience.

---

## ✨ Features

- 🥘 Create and edit recipes with ingredient management
- ⚖️ Metric / Imperial unit switching and conversion
- 🤖 Automatic recipe generation (AI-assisted, optional)
- 🔍 Filter and search recipes by ingredients or tags
- 👤 User accounts and admin dashboard

---

## 🚀 Getting Started

### 1️⃣ Clone the repository

```bash
    git clone https://github.com/yourusername/chookhub.git
    cd chookhub
```

### 2️⃣ Set up the virtual environment
```bash
    python -m venv .venv
    source .venv/bin/activate
```

### 3️⃣ Install dependencies
```bash
  pip install -r requirements.txt
```

### 4️⃣ Apply migrations & create superuser
```bash
    python manage.py migrate
    python manage.py createsuperuser
```

### 5️⃣ Populate the database with some demo units, ingredients, and recipes
```bash
    python manage.py populate_ingredients
    python manage.py populate_measuring_units
    python manage.py generate_recipes_with_openai
```

### 6️⃣ Start the backend server
```bash
python manage.py runserver
```

### 7️⃣ Start the frontend (from /frontend folder)
```bash
cd frontend
npm install
npm start
```

Then open http://localhost:3000
 (frontend)
and http://localhost:8000
 (backend API).

---

<h2 id="tech-stack">🏗️ Tech Stack</h2>

<ul>
  <li><strong>Backend:</strong> Django + Django REST Framework</li>
  <li><strong>Frontend:</strong> React + Tailwind CSS</li>
  <li><strong>Database:</strong> SQLite (dev) / PostgreSQL (prod)</li>
  <li><strong>Other:</strong> NPM, Virtualenv, Git</li>
</ul>

---
