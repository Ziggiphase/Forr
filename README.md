# Forr

AI-powered business communication platform.

## Stack

- **Frontend**: Next.js (React + TypeScript) — port 3000
- **Backend**: FastAPI (Python) — port 8000
- **Database**: PostgreSQL 16 (via Docker) — port 5432

## Prerequisites

- [Node.js](https://nodejs.org/) 18+
- [Python](https://python.org/) 3.11+
- [Docker](https://docker.com/) (for Postgres)

## Quick Start

### 1. Start the database

```bash
docker compose up -d
```

Wait for the health check to pass:

```bash
docker compose ps
```

### 2. Set up the backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API will be available at [http://localhost:8000](http://localhost:8000).
Health check: [http://localhost:8000/health](http://localhost:8000/health)

### 3. Set up the frontend

```bash
cd frontend
npm install
npm run dev
```

The app will be available at [http://localhost:3000](http://localhost:3000).

## Environment Variables

Copy `.env.example` to `.env` and adjust if needed:

```bash
cp .env.example .env
```

## Project Structure

```
├── frontend/          # Next.js app
├── backend/           # FastAPI app
│   ├── app/           # Application code
│   │   ├── main.py    # FastAPI entry point
│   │   ├── config.py  # Settings
│   │   ├── database.py # DB connection
│   │   └── models/    # SQLAlchemy models
│   └── alembic/       # Database migrations
├── docker-compose.yml # Postgres
├── SPEC.md            # Project specification & roadmap
└── README.md          # This file
```
