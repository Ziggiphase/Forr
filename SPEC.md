# Forr — Project Specification

## Stack Decision (Phase 0.3)

| Layer | Technology | Rationale |
|---|---|---|
| **Backend** | FastAPI (Python) | Closest to ML background; handles AI-agent calls naturally |
| **Frontend** | Next.js (React + TypeScript) | Most common modern choice; deepest AI tooling training exposure |
| **Database** | PostgreSQL | Reliable, battle-tested relational DB |
| **Local DB** | Docker Compose (Postgres 16) | Consistent dev environment |

---

## Project Structure

```
Forr/
├── frontend/        → Next.js app (port 3000)
├── backend/         → FastAPI app (port 8000)
├── docker-compose.yml → Postgres (port 5432)
├── .env.example     → Environment variable template
├── SPEC.md          → This file
└── README.md        → Quick-start guide
```

---

## Conventions

- **API prefix**: All backend API routes live under `/api/v1/`
- **Frontend proxy**: Next.js rewrites `/api/*` → `http://localhost:8000/api/*` in development
- **Database migrations**: Managed via Alembic (in `backend/alembic/`)
- **Environment variables**: Stored in `.env` (never committed); template in `.env.example`
- **Git workflow**: One phase = one clean, reviewable increment; confirm before moving on

---

## Build Roadmap

**How this works:** Each phase has a goal, concrete steps, and a "confirm before moving on" checklist. Don't start the next phase until the current one is fully checked off. That's the whole point of working this way with an AI coding assistant — small, verified increments instead of one giant prompt that quietly breaks something in the middle.

**Assumptions I made** (say so if any are wrong, and I'll adjust the map):
- You're building a web app (dashboard + business pages), since your notes describe a "webpage" and "dashboard."
- You'll build this mostly yourself with an AI coding assistant (Claude Code, Cursor, etc.), given the "AI slop" concern — each phase is sized to be one clean, reviewable session with a tool like that.
- Where your notes list several integration channels or file formats at once, I'm recommending you get ONE working end-to-end before adding the rest. Trying to build all four channels or all six file types simultaneously is a common way projects like this stall.
- Phases 0 and 11 aren't in your notes — I added them because nothing else works reliably without Phase 0, and nothing is really "done" without Phase 11. Every other phase follows your notes' own order.

---

### Phase 0 — Foundation (before any feature work) *[added]*

**Goal:** By the end of this phase, Antigravity has a real empty project to build on and a real spec to read — not a blank chat with no context.

**0.1 — Install Google Antigravity**
- [x] Download it for your OS from Google's Antigravity site and install it (it's VS Code–based, so it'll feel familiar).
- [x] Sign in with a Google account so it can use Gemini.

**0.2 — Create a GitHub account and one empty repo**
- [x] Sign up at github.com if you don't already have an account.
- [x] Create a single new, empty repository (e.g. `forr`). This is where everything Antigravity builds will live, and gives you a rollback point after every confirmed phase.

**0.3 — Lock your stack (recommended default, so you're not stuck deciding)**
- [x] Backend: **FastAPI** (Python) — closest to your existing ML background, and it'll handle the AI-agent calls in Phase 6 naturally.
- [x] Frontend: **Next.js** (React) — the most common modern choice, and the one AI coding tools have the deepest training exposure to, which shows up in output quality.
- [x] Database: **Postgres**.
- [x] Write these three down — this is the first line of your spec doc in 0.5.

**0.4 — Pick one hosting account (don't compare — just pick)**
- [ ] Sign up for **Railway** or **Render**. Either can host your frontend, backend, and Postgres database under one dashboard, which matters a lot when you're solo.

**0.5 — Write your spec doc**
- [x] Copy this roadmap into a doc — a `SPEC.md` in your new repo, or a Google Doc — and add your 0.3 stack decision to the top. This is what you paste into every Antigravity task from now on so it isn't guessing conventions each session.

**0.6 — Give Antigravity its first task**
- [x] Point it at your empty repo and ask for exactly one thing: scaffold the empty project — Next.js frontend, FastAPI backend, connected to Postgres. Nothing else yet.
- [x] Read the plan it proposes (Planning Mode) before letting it run — it should match this one task, no more.
- [ ] Let it run, then check its Artifacts (recording/screenshots) to see what it actually did.

**✅ Confirm before moving on:** the scaffolded project runs (locally or in Antigravity's preview), it's pushed to your GitHub repo, and your spec doc exists with the stack decision written down. Only then open a new task for Phase 1.

---

### Phase 1 — User Accounts *(from your notes)*

**Goal:** A business owner can create an account and log in.

- [ ] Data model with the fields from your notes: Name, Email, NIN, Password, Date of Birth, Nationality, Gender, State, Address, Phone Number.
  - Hash passwords (bcrypt or argon2) — never store them plain.
  - Real NIN verification against NIMC needs a third-party KYC provider. I'd store it unverified for now and treat verification as a separate later task, not a signup blocker.
- [ ] Signup and login screens wired to that model.
- [ ] Decide whether email verification gates an active account (recommended).

**✅ Confirm before moving on:** sign up, log out, log back in, and see every stored field in your database exactly as entered.

---

### Phase 2 — Dashboard Shell *(from your notes)*

**Goal:** The logged-in home page exists with all the navigation your notes call for, even if most sections are placeholders.

- [ ] Build the dashboard with nav for: Businesses, Profile, FAQs, Settings, Notifications, Search, AI (status indicator), and Total Token Used.
- [ ] Every nav item routes to a real (even if empty) page.

**✅ Confirm before moving on:** every nav item works, and the logged-in user's info is visible somewhere.

---

### Phase 3 — Business Registration *(from your notes)*

**Goal:** An owner can register a business.

- [ ] "Businesses" page: list of registered businesses (empty state at first) + "Create your business" button.
- [ ] "Create your business" form, per your notes: Business Name, Type, Description, Integration Type (Facebook, WhatsApp, Instagram, Telegram), Business Address, Size, and Service Mode (physical-only / online-remote-only / both).
- [ ] On submit, save and route to that business's own page.

**✅ Confirm before moving on:** create a business, see it in the list, and reopen its page.

---

### Phase 4 — Catalogue / Products *(from your notes, refined)*

**Goal:** One editable product table that a business can fill manually, via upload, or both — nothing goes live until the owner reviews and confirms it.

- [ ] Build the catalogue as an editable table first: columns like product name, price, description, quantity/stock, category (adjust to what your businesses actually sell). Manual add/edit/delete, row by row. This table is the single source of truth no matter how a row gets into it.
- [ ] Confirm the manual table alone works as a usable v1 before touching upload at all.
- [ ] Add file upload starting with CSV/Excel (via pandas) — these map onto rows and columns most cleanly.
- [ ] Parsed rows land in that SAME table as drafts, never auto-published. The owner reviews, edits, and explicitly confirms before a row counts as a live catalogue entry.
- [ ] Once CSV/Excel are reliable, add PDF (pdfplumber or PyMuPDF), Word/docx (python-docx), and images (OCR via pytesseract, or a vision-capable model) one at a time — these need more parsing judgment, so they're safer to add once the table + review flow is already solid.

**✅ Confirm before moving on:** create a few products manually in the table, then upload one CSV and confirm the parsed rows show up as editable drafts in that same table before you "confirm" them live.

---

### Phase 5 — Messaging Integrations *(from your notes)*

**Goal:** The business is actually reachable on the channel(s) it registered for.

- [ ] Pick ONE channel from Phase 3 and connect it fully first — WhatsApp Business API, Instagram/Facebook via Meta's Graph API, or Telegram Bot API (Telegram is usually fastest since it skips Meta business verification).
- [ ] Build "modify integration / add more integrations" in Settings so an owner can add the remaining channels later without re-registering the business.

**✅ Confirm before moving on:** send a real test message on the connected channel and see it land in your backend.

---

### Phase 6 — Knowledge Base & Agent Behavior *(from your notes)*

**Goal:** The AI agent has the business-specific facts and tone it needs to respond well.

- [ ] Knowledge base fields from your notes: delivery fee, plus other structured facts as key-value pairs.
- [ ] "How to respond / general chat tone" configuration — this feeds the agent's system prompt.
- [ ] Wire the catalogue (Phase 4) and knowledge base into the agent's context. For a small catalogue, injecting it directly into the prompt is fine; if it grows large, move to retrieval (embeddings + a vector store) instead of always injecting everything.

**✅ Confirm before moving on:** chat with the agent as a test customer and confirm it uses the catalogue, respects the delivery fee, and matches the configured tone.

---

### Phase 7 — Token Usage Tracking *(from your notes)*

**Goal:** Visibility into how much AI usage a business is consuming.

- [ ] Log token usage (prompt + completion) on every agent call — most LLM provider SDKs return this in the response, so it's mainly about saving it against the right business/account.
- [ ] Surface "Total token used" on the dashboard (the Phase 2 placeholder) with the real number.

**✅ Confirm before moving on:** send a few test messages and confirm the count matches your LLM provider's own usage dashboard.

---

### Phase 8 — AI Agent Mode *(from your notes)*

**Goal:** Decide and build what "AI Agent mode" toggles between — most likely fully-autonomous replies vs. AI drafts a reply for the owner to approve (human-in-the-loop).

- [ ] Build the toggle and both behaviors.

**✅ Confirm before moving on:** flip the toggle in a live test conversation and confirm the behavior actually changes.

---

### Phase 9 — Analytics Dashboard *(from your notes)*

**Goal:** An owner can see how their AI agent is performing.

- [ ] Pick a small set of concrete metrics to start (e.g. conversations handled, response time, token spend over time) rather than trying to show everything at once.

**✅ Confirm before moving on:** the numbers update after a real test conversation and reflect actual data, not placeholders.

---

### Phase 10 — Payments & Billing *(from your notes)*

**Goal:** Forr can charge businesses for using the platform.

- [ ] Integrate Paystack (best fit for Naira/Nigerian cards) and/or Stripe (if you'll serve international customers too).
- [ ] Build both billing modes from your notes: Subscription (recurring tiers) and Pay-as-you-go (likely metered against the token usage from Phase 7).
- [ ] Decide what happens on failed payment or an exceeded free tier — gate the AI agent's responses, or just notify?

**✅ Confirm before moving on:** run one real transaction through each provider's test mode end-to-end, and confirm the account's billing status updates correctly.

---

### Phase 11 — Finish the Shell *[added]*

**Goal:** The placeholders from Phase 2 become real before you call this launch-ready.

- [ ] Build out FAQs, Settings, Notifications, and Search properly — easy to leave stubbed once the AI features feel "done," but owners will notice.

**✅ Confirm before moving on:** every nav item from Phase 2 is fully functional, not a stub.

---

*Work top to bottom. If a phase turns out to need its own sub-map (Phase 6's agent wiring is the most likely candidate), just ask and we'll break that one down further.*
