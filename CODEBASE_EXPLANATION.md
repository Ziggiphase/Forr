# Forr - Codebase Explanation

This document provides a comprehensive, file-by-file explanation of the Forr codebase. Forr is an AI-powered conversational commerce platform that allows businesses to manage automated customer interactions across WhatsApp and Telegram, manage product inventories, and receive payments securely.

---

## 1. Project Root

- **docker-compose.yml**: Defines the local development infrastructure. Currently, it spins up a postgres:16-alpine Docker container which serves as the primary relational database for the application. It maps port 5432 to the host and mounts a volume (orr_pgdata) so database data persists across restarts.
- **.env / .env.example**: Environment variables file. Contains critical secrets like API keys (Groq, Paystack, Telegram, Twilio), database URLs, and encryption keys.
- **.gitignore**: Tells Git which files and directories to ignore (e.g., 
ode_modules, __pycache__, .env, and virtual environments).

---

## 2. Backend (FastAPI + Python)

The backend is a high-performance asynchronous REST API built with FastAPI, SQLAlchemy (ORM), and PostgreSQL.

### Core Configuration
- **ackend/run.py**: The entry point script that uses Uvicorn to run the FastAPI application on port 8000.
- **ackend/app/main.py**: The FastAPI application factory. It initializes the app, configures CORS middleware (allowing the frontend to communicate with it), registers all API routers (auth, businesses, products, webhooks, etc.), and launches background tasks like the Telegram long-poller.
- **ackend/app/config.py**: Uses Pydantic BaseSettings to load environment variables and expose them as strongly typed Python attributes.
- **ackend/app/database.py**: Configures the asynchronous SQLAlchemy engine and session maker (sync_session). Provides a get_db dependency injection function used by endpoints to interact with the database.

### API Endpoints (ackend/app/api/)
- **uth.py**: Handles user registration and login. Exposes /signup (hashes passwords and creates users) and /login (verifies credentials and returns JWT access tokens).
- **usinesses.py**: Manages business accounts. Contains logic for creating businesses, fetching analytics, and configuring third-party integrations (WhatsApp and Telegram tokens).
- **products.py**: Manages the e-commerce catalogue. Supports adding products manually and parsing bulk textual lists using an LLM to automatically generate structured products.
- **inbox.py**: Exposes the conversational data. Allows the frontend dashboard to fetch message histories, mark conversations as read, and manually intervene in AI conversations.
- **webhooks.py**: The Twilio WhatsApp entry point. Exposes a public endpoint that Twilio hits whenever a customer sends a WhatsApp message. It parses the payload and forwards it to the Inbox service.
- **illing.py**: Manages subscription tiers (Free, Pro, Premium). Includes the Paystack webhook listener to verify when a business successfully pays for a subscription upgrade.

### Core Services (ackend/app/services/)
- **gent.py**: The "brain" of the platform. When a customer messages, this file fetches the business's product catalogue, formats a strict system prompt, and calls the Groq LLM API. It handles token tracking, tool calling (like generate_payment_link), and fallback logic.
- **inbox.py**: (Service Layer) Orchestrates incoming messages. When a message arrives, it finds or creates a Conversation record, logs the message, triggers the gent.py to get an AI reply, saves the AI reply, and updates conversation unread statuses.
- **	elegram_poller.py**: A background loop that continuously reaches out to the Telegram API to fetch new messages for all connected businesses. It acts as the Telegram equivalent of webhooks.py.
- **paystack.py**: A wrapper around the Paystack API. It handles creating subaccounts for businesses (so businesses can receive splits of customer payments) and initializing B2C transactions.
- **messaging.py**: Helper functions to dispatch outgoing text messages asynchronously via the Twilio (WhatsApp) and Telegram APIs.
- **email.py**: A lightweight SMTP email dispatcher used for sending platform alerts, like when a business exceeds their AI conversation limit.

### Database Models (ackend/app/models/)
These files define the SQLAlchemy relational tables mapped to PostgreSQL:
- **user.py**: Stores business owners and encrypted passwords.
- **usiness.py**: The core entity. Stores business profiles, encrypted API keys for messaging platforms, Paystack subaccount codes, and customized AI knowledge/tones.
- **product.py**: Stores items for sale, their prices, and stock statuses.
- **conversation.py**: Tracks a unique chat session between a customer (identified by phone number or chat ID) and a business. Tracks whether the AI is currently handling it or if a human took over.
- **message.py**: Individual chat bubbles within a conversation. Tracks tokens used and response times.
- **payment.py**: Tracks customer checkout sessions generated by the AI.
- **subscription.py**: Tracks B2B SaaS subscriptions for businesses.

---

## 3. Frontend (Next.js + React + Tailwind)

The frontend is a React application utilizing the Next.js App Router, structured for a B2B SaaS dashboard experience.

### Configuration
- **rontend/next.config.ts**: Next.js configuration.
- **rontend/tailwind.config.ts**: Defines the design system, colors, and fonts (using Material Design 3 principles).
- **rontend/src/app/globals.css**: Global stylesheet enforcing basic resets and Tailwind imports.
- **rontend/src/app/layout.tsx**: The root HTML wrapper. Enforces a full-screen layout.

### Authentication (rontend/src/app/(auth)/)
- **login/page.tsx & signup/page.tsx**: React forms for user onboarding. They POST data to the backend auth endpoints and store the returned JWT token securely in js-cookie.

### Dashboard (rontend/src/app/dashboard/)
The primary authenticated workspace.
- **layout.tsx**: The persistent shell. Contains the sidebar navigation and a global debounced search bar. It verifies the user's JWT token on load.
- **page.tsx**: The business selector. Lists all businesses owned by the logged-in user.
- **usinesses/[id]/layout.tsx**: A sub-navigation shell specific to a single business (Inbox, Products, AI Settings, Integrations).
- **usinesses/[id]/inbox/page.tsx**: The real-time chat interface. It polls the backend for new messages, displays chat histories, and allows human agents to seamlessly take over conversations from the AI.
- **usinesses/[id]/products/page.tsx**: A table displaying inventory. Includes a bulk upload modal that utilizes the backend's AI parsing capabilities.
- **usinesses/[id]/integrations/page.tsx**: Forms for entering Telegram Bot tokens and Twilio credentials. It securely encrypts and stores them.
- **usinesses/[id]/page.tsx (Payments)**: An onboarding flow for Paystack. Allows the business to enter their bank details so Forr can automatically generate a subaccount and enable AI checkout links.
- **illing/page.tsx**: Displays the user's current subscription tier, usage progress bars, and allows upgrading/downgrading via Paystack integration.
