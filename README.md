# AI Career Recommendation System

An AI-powered career recommendation web application developed as a final-year BCA project. The system helps students and early-career users explore suitable career paths by analyzing their skills, experience level, industry preference, and uploaded resume content.

The project combines a React frontend, Flask backend, machine learning based recommendation logic, resume parsing, authentication, saved careers, analytics, and cybersecurity awareness features for safer online job searching.

## Project Overview

Career planning can be difficult for students because career information is often scattered, generic, or not personalized to an individual's skills. This project solves that problem by providing a web-based platform that recommends career paths based on user input and resume data.

The application also includes cybersecurity features such as URL safety checking and job posting fraud analysis, helping users identify suspicious links and potentially fake job opportunities.

## Key Features

- Personalized career recommendations based on skills, industry, and experience level
- Hybrid recommendation approach using content-based logic and collaborative filtering concepts
- Resume upload and parsing for PDF, DOCX, and TXT files
- Skill extraction and skill-gap analysis
- User registration and login with JWT authentication
- Saved career recommendations for logged-in users
- Analytics dashboard for recommendation and engagement insights
- Cybersecurity tips for job seekers
- URL safety checker for suspicious job links
- Job posting fraud indicator analysis
- REST API backend with Flask
- Responsive React frontend

## Tech Stack

### Frontend

- React
- React Router
- Axios / Fetch API
- Tailwind CSS
- Chart.js
- React Hot Toast

### Backend

- Python
- Flask
- Flask-CORS
- Flask-JWT-Extended
- Flask-SQLAlchemy
- SQLite for local development
- PostgreSQL-ready configuration

### Machine Learning and NLP

- scikit-learn
- NumPy
- spaCy
- PyPDF2
- python-docx

### Testing and Tools

- pytest
- pytest-flask
- VS Code task configuration
- Git and GitHub

## System Architecture

```text
React Frontend
    |
    | HTTP requests
    v
Flask REST API
    |
    |-- Authentication and user management
    |-- Career recommendation engine
    |-- Resume parser
    |-- Cybersecurity services
    |-- Evaluation and analytics endpoints
    |
    v
SQLite / PostgreSQL Database
```

## Project Structure

```text
ai-career-recommender-main/
  backend/
    app.py
    requirements.txt
    database/
    services/
    ml_system/
    evaluation/
    tests/
  frontend/
    package.json
    src/
      api/
      components/
      context/
      pages/
  .vscode/
    tasks.json
    settings.json
  README.md
```

## Backend Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
flask --app app run --host 0.0.0.0 --port 5000
```

The backend will run at:

```text
http://localhost:5000
```

Health check endpoint:

```text
http://localhost:5000/health
```

## Frontend Setup

```bash
cd frontend
npm install
npm start
```

The frontend will run at:

```text
http://localhost:3000
```

## Running in VS Code

Open the project folder in VS Code:

```text
ai-career-recommender-main
```

Then run:

```text
Terminal > Run Task...
```

Available tasks:

- Backend: Flask API
- Frontend: React

## Environment Variables

Create a `backend/.env` file for local development:

```env
FLASK_ENV=development
FLASK_DEBUG=1
JWT_SECRET_KEY=change-this-secret-key-min-32-chars
DATABASE_URL=sqlite:///ai_career.db
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
MAX_UPLOAD_SIZE_MB=16
UPLOAD_FOLDER=uploads
```

Do not commit real secrets, API keys, or production database credentials.

## Main API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/health` | Backend health check |
| POST | `/auth/register` | Register a new user |
| POST | `/auth/login` | Login and receive JWT token |
| GET | `/auth/me` | Get current authenticated user |
| POST | `/ai/recommend` | Generate career recommendations |
| POST | `/ai/skills/analyze` | Analyze skill gaps |
| POST | `/resume/parse` | Parse resume and extract skills |
| GET | `/cybersecurity/tips` | Get cybersecurity tips |
| POST | `/cybersecurity/check-url` | Check URL safety |
| POST | `/cybersecurity/analyze-job` | Analyze job posting risk |
| GET | `/ai/favorites` | Get saved careers |
| POST | `/ai/favorites` | Save a career |

## Academic Relevance

This project demonstrates practical knowledge in:

- Full-stack web application development
- REST API design
- Authentication and authorization
- Database modeling
- Machine learning based recommendation systems
- Natural language processing for resume parsing
- Cybersecurity awareness in job search platforms
- Software testing and project documentation

## Future Enhancements

- Add a production deployment pipeline
- Improve recommendation accuracy with larger datasets
- Add admin dashboard for career dataset management
- Integrate external job market APIs
- Add email verification and password reset
- Improve resume parsing accuracy with advanced NLP models
- Add more detailed career roadmap visualization

## Author

Developed by a final-year BCA student as an academic full-stack AI project.

## License

This project is intended for academic and educational use.
