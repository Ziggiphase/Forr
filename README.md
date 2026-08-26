# Forr

**Forr** is a comprehensive, AI-powered conversational commerce platform designed for small-to-medium businesses (B2B SaaS). It enables business owners to completely automate customer support and sales through WhatsApp and Telegram using intelligent AI agents. The AI has direct access to the business's product catalogue, can answer questions, securely generate Paystack checkout links in-chat, and intelligently escalate complex queries to human staff.

---

## ??? Tech Stack

- **Frontend:** Next.js (React 18), Tailwind CSS, TypeScript
- **Backend:** FastAPI, Python 3.11+, SQLAlchemy (Async), Pydantic
- **Database:** PostgreSQL 16 (via Docker Compose)
- **AI/LLM:** Groq API (Llama3/GPT OSS via HTTPX)
- **Integrations:** Twilio (WhatsApp), Telegram Bot API, Paystack (Payments)

---

## ?? Docker & Database Architecture

The platform relies on a **PostgreSQL 16** database. Instead of installing PostgreSQL natively on your machine, the project uses **Docker Compose** to spin up the database in an isolated container. 

- **Docker Image Used:** postgres:16-alpine (A lightweight version of the official Postgres image).
- **Volumes:** The data is persisted locally via a Docker Volume named orr_pgdata. Even if you destroy the container, your database records remain intact on your host machine.
- **Do we push the images to GitHub?** No. The docker-compose.yml file pulls the official public image from Docker Hub automatically. We do not build or push custom Docker images for this project.

### Starting the Database

1. Ensure Docker Desktop is running.
2. Run the following command from the project root:
   \\\ash
   docker-compose up -d
   \\\

---

## ?? Running the Platform Locally

### 1. Backend Setup
The backend requires a Python virtual environment and valid environment variables.

\\\ash
cd backend
python -m venv venv
.\venv\Scripts\activate   # Windows
# source venv/bin/activate # Mac/Linux

pip install -r requirements.txt
python run.py
\\\
The backend will boot up at http://localhost:8000.

### 2. Frontend Setup
The frontend requires Node.js (18+).

\\\ash
cd frontend
npm install
npm run dev
\\\
The frontend will boot up at http://localhost:3000.

---

## ?? Environment Variables
Ensure you copy .env.example to .env in the root of the ackend folder. You will need:
- \GROQ_API_KEY\: To power the AI Agent.
- \PAYSTACK_SECRET_KEY\: For generating checkout links.
- \ENCRYPTION_KEY\: A base64 32-byte key used to securely encrypt business integrations in the database.

---

## ?? Codebase Explanation
For a comprehensive line-by-line breakdown of every file, directory, and architectural decision, please refer to the [CODEBASE_EXPLANATION.md](./CODEBASE_EXPLANATION.md) file included in this repository.

