# Forr — Build Roadmap

**How this works:** Each phase has a goal, concrete steps, and a "confirm before moving on" checklist. Don't start the next phase until the current one is fully checked off. That's the whole point of working this way with an AI coding assistant — small, verified increments instead of one giant prompt that quietly breaks something in the middle.

**Design system note:** once you have a locked design system (`DESIGN.md` + a reference implementation like `code.html`), attach both to *every* UI-related task you give Antigravity — Phase 8's Inbox, Phase 9's analytics dashboard, Phase 11's shell polish, any restyle. The roadmap's checklist items describe *what* to build, not the actual colors/tokens/components — those live only in the design files, and starting a task from the roadmap text alone (without re-attaching them) is what caused the styling regression once already.

**Assumptions I made** (say so if any are wrong, and I'll adjust the map):
- You're building a web app (dashboard + business pages), since your notes describe a "webpage" and "dashboard."
- You'll build this mostly yourself with an AI coding assistant (Claude Code, Cursor, etc.), given the "AI slop" concern — each phase is sized to be one clean, reviewable session with a tool like that.
- Where your notes list several integration channels or file formats at once, I'm recommending you get ONE working end-to-end before adding the rest. Trying to build all four channels or all six file types simultaneously is a common way projects like this stall.
- Phases 0 and 11 aren't in your notes — I added them because nothing else works reliably without Phase 0, and nothing is really "done" without Phase 11. Every other phase follows your notes' own order.

---

## Using This Map With Google Antigravity

Same phase-by-phase, confirm-before-moving-on structure — only *how* you drive each phase changes if you use Antigravity (Google's agent-first IDE, built around Gemini models) instead of a chat-based coding assistant:

- **One phase = one task.** Antigravity's Manager view lets you <cite index="1-1">run several agents at once, each working asynchronously in its own workspace</cite> — give it one phase at a time as its own task, the same discipline as one phase per chat session, just enforced through separate tasks instead.
- **Use Planning Mode as your scope check.** Before it touches code, <cite index="7-1">the agent first produces a to-do list and a plan for you to review</cite>. Check that plan against the phase's steps in this map before letting it run — if it's quietly added scope you didn't ask for, that's exactly where slop creeps back in even with a strong tool.
- **Let its Artifacts be your confirmation evidence.** Antigravity <cite index="1-1">leaves behind an inspectable record of what an agent did — plans, task lists, screenshots, and browser recordings — rather than just low-level logs</cite>. Ask it to demonstrate each "✅ Confirm before moving on" line inside the browser rather than just reporting "done"; the recording is your proof, not its word.
- **Keep permission gates tight early on.** You can <cite index="5-1">restrict, per task, what an agent may run on its own versus what needs your approval first</cite>. Start conservative — ask-before-running — especially around Phase 1's auth, Phase 4's database writes, and Phase 10's payments; loosen only once you trust what it's producing.
- **Still paste in your Phase 0 spec doc** at the start of every task so context doesn't drift between phases — the same reason it mattered with a chat assistant.

---

## Phase 0 — Foundation (before any feature work) *[added]*

**Goal:** By the end of this phase, Antigravity has a real empty project to build on and a real spec to read — not a blank chat with no context.

**0.1 — Install Google Antigravity**
- [ ] Download it for your OS from Google's Antigravity site and install it (it's VS Code–based, so it'll feel familiar).
- [ ] Sign in with a Google account so it can use Gemini.

**0.2 — Create a GitHub account and one empty repo**
- [ ] Sign up at github.com if you don't already have an account.
- [ ] Create a single new, empty repository (e.g. `forr`). This is where everything Antigravity builds will live, and gives you a rollback point after every confirmed phase.

**0.3 — Lock your stack (recommended default, so you're not stuck deciding)**
- [ ] Backend: **FastAPI** (Python) — closest to your existing ML background, and it'll handle the AI-agent calls in Phase 6 naturally.
- [ ] Frontend: **Next.js** (React) — the most common modern choice, and the one AI coding tools have the deepest training exposure to, which shows up in output quality.
- [ ] Database: **Postgres**.
- [ ] Write these three down — this is the first line of your spec doc in 0.5.

**0.4 — Pick one hosting account (don't compare — just pick)**
- [ ] Sign up for **Railway** or **Render**. Either can host your frontend, backend, and Postgres database under one dashboard, which matters a lot when you're solo.

**0.5 — Write your spec doc**
- [ ] Copy this roadmap into a doc — a `SPEC.md` in your new repo, or a Google Doc — and add your 0.3 stack decision to the top. This is what you paste into every Antigravity task from now on so it isn't guessing conventions each session.

**0.6 — Give Antigravity its first task**
- [ ] Point it at your empty repo and ask for exactly one thing: scaffold the empty project — Next.js frontend, FastAPI backend, connected to Postgres. Nothing else yet.
- [ ] Read the plan it proposes (Planning Mode) before letting it run — it should match this one task, no more.
- [ ] Let it run, then check its Artifacts (recording/screenshots) to see what it actually did.

**✅ Confirm before moving on:** the scaffolded project runs (locally or in Antigravity's preview), it's pushed to your GitHub repo, and your spec doc exists with the stack decision written down. Only then open a new task for Phase 1.

---

## Phase 1 — User Accounts *(from your notes)*

**Goal:** A business owner can create an account and log in.

- [ ] Data model with the fields from your notes: Name, Email, NIN, Password, Date of Birth, Nationality, Gender, State, Address, Phone Number.
  - Hash passwords (bcrypt or argon2) — never store them plain.
  - Real NIN verification against NIMC needs a third-party KYC provider. I'd store it unverified for now and treat verification as a separate later task, not a signup blocker.
- [ ] Signup and login screens wired to that model.
- [ ] Decide whether email verification gates an active account (recommended).

**✅ Confirm before moving on:** sign up, log out, log back in, and see every stored field in your database exactly as entered.

---

## Phase 2 — Dashboard Shell *(from your notes)*

**Goal:** The logged-in home page exists with all the navigation your notes call for, even if most sections are placeholders.

- [ ] Build the dashboard with nav for: Businesses, Profile, FAQs, Settings, Notifications, Search, AI (status indicator), and Total Token Used.
- [ ] Every nav item routes to a real (even if empty) page.

**✅ Confirm before moving on:** every nav item works, and the logged-in user's info is visible somewhere.

---

## Phase 3 — Business Registration *(from your notes)*

**Goal:** An owner can register a business.

- [ ] "Businesses" page: list of registered businesses (empty state at first) + "Create your business" button.
- [ ] "Create your business" form, per your notes: Business Name, Type, Description, Integration Type — a **multi-select** of Facebook, WhatsApp, Instagram, Telegram (an owner can pick more than one channel at once), Business Address, Size, and Service Mode (physical-only / online-remote-only / both).
- [ ] On submit, save and route to that business's own page.

**✅ Confirm before moving on:** create a business, see it in the list, and reopen its page.

---

## Phase 4 — Catalogue / Products *(from your notes, refined)*

**Goal:** One editable product table that a business can fill manually, via upload, or both — nothing goes live until the owner reviews and confirms it.

**4a — Manual table only**
- [ ] Build the catalogue as an editable table: columns like product name, price, description, quantity/stock, category (adjust to what your businesses actually sell — lock this down now, since the upload parsers in 4b need to match it). Manual add/edit/delete, row by row. This table is the single source of truth no matter how a row gets into it.
- [ ] Confirm before moving to 4b: add, edit, and delete a product manually, refresh, and see it persist.

**4b — CSV/Excel upload into the same table**
- [ ] Add file upload for CSV/Excel (via pandas) — these map onto rows and columns most cleanly.
- [ ] Parsed rows land in that SAME table as drafts, never auto-published. The owner reviews, edits, and explicitly confirms before a row counts as a live catalogue entry.
- [ ] Confirm before moving to 4c: upload one CSV, see the parsed rows appear as editable drafts, edit one, confirm it, and check it now looks identical to a manually-added row.

**4c — Remaining formats, one at a time**
- [ ] Once CSV/Excel are reliable, add PDF (pdfplumber or PyMuPDF), Word/docx (python-docx), and images (OCR via pytesseract, or a vision-capable model) — one format per task, not all at once.

**✅ Confirm before moving on to Phase 5:** every format you've added produces rows that land as editable drafts in the same table, and nothing is live until you've explicitly confirmed it.

---

## Phase 5 — Messaging Integrations *(from your notes, refined)*

**Goal:** The business is actually reachable on the channel(s) it registered for. Not every channel connects the same way, so this splits into three tasks instead of one.

**5a — Telegram (done)**
- [ ] Each business stores its *own* bot token (from that business's own `@BotFather` bot) — not one shared token for the whole platform.
- [ ] Use polling, not a webhook, for now — a webhook needs a public HTTPS URL, which doesn't exist until Phase 0's deferred hosting decision is actually acted on. Switch to a webhook after deploying.
- [ ] Store the bot token as a secret (env var for now, encrypted column later) — never committed to git, never logged in plain text.
- [ ] Build "modify integration / add more integrations," and its reverse — disconnect/cancel a connected channel — in Settings.

**✅ Confirm 5a before moving on:** message your test bot yourself as a real customer would, confirm it lands in the backend tied to the correct business, then disconnect it and confirm messages stop arriving.

**5b — WhatsApp (build this now, via Twilio's free Sandbox)**
- [ ] Testing uses Twilio's WhatsApp Sandbox — no WhatsApp Business Account needed at this stage. Store the Account SID and Auth Token as secrets (env vars), same rule as the Telegram bot token: never hardcoded, never committed to git. Also add a `twilio_phone_number` field to the Business model — populate it with the sandbox number for every business for now, but have the send logic read from this field rather than a hardcoded constant, so moving a business to its own dedicated number later is a data change, not a code change.
- [ ] Unlike Telegram, WhatsApp has no polling option — Twilio only delivers incoming messages via a webhook, so a public URL is required even just to test. Use ngrok for this: claim your free static/dev domain in the ngrok dashboard once, and always start ngrok pointed at *that* domain (not the default random one) so the URL doesn't change between sessions.
- [ ] Set that ngrok URL (plus your webhook route) as the Sandbox's "When a message comes in" address in the Twilio Console.
- [ ] Reuse the same "modify integration / add more integrations" and disconnect/cancel pattern built for Telegram, so this lives in the same Settings screen.

**✅ Confirm 5b before moving on:** message the Twilio sandbox number from your own (joined) WhatsApp, confirm it lands in the backend tied to the correct business, then disconnect and confirm messages stop arriving. Note: a real business's own WhatsApp number (not the shared sandbox) is a separate, later step — through Meta's Embedded Signup or a BSP — not needed until you're onboarding real businesses.

**5c — Instagram, Facebook (later — not this session)**
- [ ] These two go through Meta with the same OAuth-style "log in and grant access" pattern as WhatsApp's Embedded Signup — the owner authenticates and authorizes, they don't hand you a token to type in.
- [ ] The Business record will need to store this OAuth-granted access token + account IDs, a different shape of credential than Telegram's plain bot token or WhatsApp's Account SID/Auth Token pair — worth keeping in mind for the schema now, even though you're not building this part yet.

**✅ Confirm before moving on to Phase 6:** 5a and 5b together are enough to proceed — 5c doesn't block anything downstream and can be picked up whenever you're ready to onboard Instagram/Facebook businesses.

---

## Phase 6 — Knowledge Base & Agent Behavior *(from your notes, refined)*

**Goal:** The AI agent has the business-specific facts and tone it needs to respond well. Split into two tasks — the first is plain data, the second is where real AI behavior starts.

**6a — Knowledge base + tone config (build first, no AI involved yet)**
- [ ] Structured key-value fields per your notes: delivery fee, plus whatever else an owner wants to set (return policy, business hours, etc.).
- [ ] A separate free-text "how to respond / general chat tone" field.

**✅ Confirm 6a before moving on:** save some values, reload the page, and see them persist correctly. Nothing agent-related yet — this is just data.

**6b — Wire it into the actual agent**
- [ ] **Model confirmed:** `openai/gpt-oss-120b` on GroqCloud (Llama models were deprecated by Groq mid-2026; this is the replacement). Open-weight (Apache 2.0), supports tool/function calling natively — Phase 8c's `escalate_to_human` design is workable as-is.
- [ ] Wire the catalogue (Phase 4) and knowledge base (6a) into the agent's context. Direct prompt injection is fine while catalogues are small; flag to Antigravity that this should be swappable for retrieval (embeddings + a vector store) later, not hardcoded assuming everything always fits in context.
- [ ] Explicitly require the agent to say it doesn't know rather than invent a product, price, or policy that isn't in the data — state this in the plan, don't assume it happens on its own.
- [ ] Check Groq's current free-tier rate limits (requests/tokens per minute and per day) on your own console.groq.com dashboard once signed up — these numbers shift between models and over time, so treat any number you read elsewhere as approximate and verify live.

**✅ Confirm 6b before moving on:** chat with it as a test customer. Ask about a real product (should be accurate), ask the delivery fee (should match what you set), and ask about something *not* in your catalogue (should say it doesn't know, not make something up).

---

## Phase 7 — Token Usage Tracking *(from your notes)*

**Goal:** Visibility into how much AI usage a business is consuming.

- [ ] Log token usage (prompt + completion) on every agent call — Groq returns this in a `usage` object on the response for standard calls. If responses are streamed, usage has historically appeared under `x_groq.usage` on the final chunk instead of the standard location — check which applies to your actual implementation rather than assuming.
- [ ] Surface "Total token used" on the dashboard (the Phase 2 placeholder) with the real number.

**✅ Confirm before moving on:** send a few test messages and confirm the count matches your LLM provider's own usage dashboard.

---

## Phase 8 — AI Agent Mode & Inbox *(from your notes, expanded)*

**Goal:** "AI Agent mode" turns out to need a real interface, not just a toggle — an Inbox where the owner can see conversations and take over when needed. Split into three tasks.

**8a — Inbox UI (view only, no handoff logic yet)**
- [ ] One unified conversation list, not separate tabs per channel — every conversation from every connected channel sorted together by most recent activity, with a small channel icon (WhatsApp/Telegram) on each row so the channel is still obvious at a glance. A channel filter on top is fine as a secondary option, but unified is the default view.
- [ ] Customer identification differs by channel — show whatever's actually available rather than forcing one consistent field: Telegram gives you the customer's real name/username automatically; WhatsApp (via the Twilio sandbox) only gives a phone number unless the customer states their name in conversation. Don't fake a "name" field for WhatsApp customers who haven't given one.
- [ ] No cross-channel customer merging — a WhatsApp number and a Telegram user ID have no shared identifier, so there's no reliable way to know if they're the same real person. Every (channel + customer identifier) combination is its own separate conversation thread. A unified customer profile across channels is a deliberate later feature, not something to build here.
- [ ] Each conversation row needs a clear status, not just a channel icon — e.g. AI handling it / needs you / you're handling it manually. This is what actually makes the Inbox useful day to day, since 8c introduces AI-handled and handed-off conversations and the owner needs to know where their attention is needed without opening every thread.
- [ ] Click into a conversation to see the full message history. The open conversation should poll for new messages on a short interval (~5s) and append them automatically, no manual refresh. Every other conversation in the list polls on a longer interval (~10–15s); when a new message arrives for one that isn't open, mark it unread (bold name + dot/count) and bump it to the top by recency. Flag to Antigravity that this should be swappable for WebSockets later — don't hardcode assuming polling is permanent.
- [ ] Unread activity is a separate signal from the handling-status badge, not the same thing — a fully AI-handled conversation can still have unread activity you haven't glanced at. Don't conflate the two.
- [ ] Channel badge gets its own visual identity, distinct from the status badge — bold text with a soft channel-tinted background (e.g. muted green for WhatsApp, muted blue for Telegram), not the same neutral grey pill as the status badge.
- [ ] Confirm the list-and-thread layout stacks on mobile (list only, or thread only — never both side by side) rather than assuming responsiveness happens automatically from a restyle.

**✅ Confirm 8a before moving on:** your real Phase 5 test conversations (Telegram and WhatsApp) show up together in one list, sorted by recency, each with the correct channel icon, correct customer identifier (name for Telegram, number for WhatsApp), and correct status — not just the right messages in the right order.

**8b — Manual reply from the Inbox**
- [ ] Owner can type and send a reply directly from the Inbox for a conversation, and it actually delivers on the right channel (WhatsApp or Telegram) tied to that business — reusing Phase 5's send logic, not a separate path.
- [ ] Watch for duplicates against 8a's polling: if a sent reply is added to the thread immediately and the next poll re-fetches the full history, the same message can appear twice unless the code explicitly avoids re-adding something it already has locally.
- [ ] Label manual replies as sent by the owner, not the AI — the thread already shows "AI Assistant" under bot replies; a human reply needs the equivalent (e.g. "You" or the owner's name), not blank or mislabeled. This matters for the Inbox's supervision purpose — being able to tell afterward whether the AI or a human actually answered.

**✅ Confirm 8b before moving on:** send a manual reply from the Inbox and see it arrive on your own test phone/Telegram, exactly like a normal message from that business. Watch the thread through the next poll cycle to confirm it doesn't duplicate, and confirm it's labeled as sent by you, not the AI.

**8c — Handoff trigger**
- [ ] Two triggers, as decided: the owner manually turns Agent Mode off, or the agent itself can't answer.
- [ ] For "agent can't answer": don't try to detect this by scanning the AI's own reply text for uncertainty afterward — give the model a structured way to signal it directly instead. Define an `escalate_to_human`-style tool/function the model can call in place of a normal reply, and instruct it explicitly (in the system prompt from Phase 6b) to call that tool rather than guess when the catalogue and knowledge base don't cover the question. This depends on the Phase 6b model choice supporting tool/function calling — worth checking that's settled.
- [ ] Either trigger must flip that conversation's status badge (from 8a) to "Needs You" — not just silently stop the AI from responding. Without a visible status change, a customer is left hanging with no signal to the owner that anyone needs to step in.
- [ ] A business owner should also be able to manually take over an AI-handled conversation from the Inbox at any time, not just have handoff be AI-triggered.

**✅ Confirm 8c before moving on:** turn Agent Mode off and confirm the conversation goes to the Inbox for manual handling with a visible status change. Then, with Agent Mode on, ask it several questions *outside* your catalogue/knowledge base — deliberately adversarial (e.g. return policy, a product you don't carry, payment plans, something plainly off-topic) — and confirm it escalates every time instead of inventing an answer, and updates the status badge each time. Also check it doesn't over-escalate on easy, clearly-answerable questions. Then test manually taking over a live AI conversation yourself and confirm the AI stops replying to it.

---

## Phase 9 — Analytics Dashboard *(from your notes, refined)*

**Goal:** An owner can see how their AI agent and business are performing in aggregate — distinct from the Inbox's raw conversation view. Split into two tasks: some of what you want depends on Phase 10 (payments), which doesn't exist yet.

**9a — build now**
- [ ] Headline row: two standalone single-number cards side by side — Total Conversations, Escalation Rate.
- [ ] Activity chart: Unique Customers vs. Total Chats, both lines on one chart, bucketed by day — meaningful next to each other, not as separate widgets (a high chat count with few unique customers means repeat questions, not growing reach).
- [ ] Response Time card: AI average next to Manual average in the same card, since the comparison is the actual insight.
- [ ] Token Spend Over Time chart, bucketed by day.
- [ ] Satisfaction card: good feedback vs. complaints, shown as a simple split. Requires a small new feature first — add an explicit "Was this helpful? 👍 👎" prompt the AI sends when a conversation seems resolved. Don't infer sentiment from message text; get a direct signal, same lesson as 8c's escalation design.
- [ ] One date-range selector (Today / 7 days / 30 days) above everything, controlling every widget at once.
- [ ] Attach `DESIGN.md` and `code.html` to this task, same as every UI phase — don't let this be another styling regression.

**✅ Confirm 9a before moving on:** numbers update after a real test conversation and reflect actual data, not placeholders. Also test the feedback prompt itself — tap both thumbs up and down and confirm the satisfaction card reflects it.

**9b — once the B2C checkout flow (Phase 10b) exists**
- [ ] Add Conversion Rate to the headline row: unique paying customers ÷ unique chatting customers.
- [ ] Sales Over Time chart with a day/week/month toggle on the *same* chart, not three separate charts.
- [ ] Drill-down list (not a dashboard tile): customers who enquired repeatedly without paying, with their count — reachable by clicking into the Conversion Rate card, not sitting on the main dashboard face.

**✅ Confirm 9b before moving on:** make a real test purchase through the B2C checkout flow, confirm it shows up correctly in both the conversion rate and the sales chart, and confirm the drill-down list only shows customers who genuinely didn't pay.

---

## Phase 10 — Payments & Billing *(from your notes)*

**Goal:** Forr can charge businesses for using the platform. This is B2B only — Forr charging businesses their subscription, using Forr's own Paystack keys. End-customers paying businesses for products is a separate flow, out of scope here (see Phase 10b).

- [ ] Build Paystack now, not Stripe — Nigeria isn't a Stripe-supported country for opening a merchant account, so Stripe isn't actually usable until Forr has a foreign entity in a supported country (US/UK, etc.), which is a "when we go global" step, not a "now" one. Paystack already covers Ghana, Kenya, South Africa, and Côte d'Ivoire too, so this isn't purely Nigeria-only reach in the meantime.
- [ ] Revisit Stripe once a foreign entity actually exists as part of scaling — add it alongside Paystack at that point, not instead of it.
- [ ] Billing model decided: standard monthly subscription per tier, with an automatic upgrade to the next tier when a business crosses its plan's conversation limit — not smooth per-token metering. "One conversation" = one distinct (channel + customer identifier) thread, reusing Phase 8a's existing conversation definition, not a new counting mechanism.
- [ ] When a business crosses its limit: pause the AI agent for that business (don't auto-upgrade or auto-charge), and send the owner a notification explaining why. The owner must actively opt in to upgrade before service resumes — no silent charges.
- [ ] This is a third reason Agent Mode can go quiet, alongside Phase 8c's owner-off and agent-escalation triggers — and it needs to look different in the Inbox, not reuse the "Needs You" badge, since the owner's required action is completely different ("upgrade your plan" vs. "answer this customer"). This touches Phase 8's already-built status logic, not just new Phase 10 code.
- [ ] The notification itself needs to exist before this can work, and "Notifications" is currently unbuilt (sitting in Phase 11). Build a minimal version now — a transactional email to the owner's Phase 1 address is enough — rather than pulling all of Phase 11 forward early.
- [ ] API access for businesses is a planned future tier, not part of this build — don't let it creep into scope now.
- [ ] Build a dedicated Billing page, linked from a new top-level "Billing" item in the main sidebar nav (not nested under Settings): a current-plan section (tier, price, usage this cycle as a progress indicator); all available tiers with price, conversation limit, and a switch button — upgrade and downgrade both handled through Paystack from this page; and a prominent banner state for when the business is paused for exceeding its limit, with the upgrade action front and center. The Inbox's "Paused — Limit Reached" status badge should link directly to this page.

**✅ Confirm before moving on:** subscribe a test business through Paystack's test mode and confirm it's active in your own database, not just Paystack's dashboard. Push that business to its conversation limit and confirm the AI actually pauses, with a distinct "Paused — Limit Reached" status in the Inbox (not the same badge as "Needs You") that links to the Billing page. Confirm the notification email genuinely arrives. Confirm opting in on the Billing page calls Paystack's plan-change API, moves the business to the next tier, and resumes AI service. Then confirm the reverse: if you don't opt in, the pause stays in effect rather than silently auto-resuming. Also confirm downgrading works, not just upgrading.

---

## Phase 10b — B2C Checkout Flow *[new scope, deferred]*

**Goal:** End-customers paying businesses for products directly through a chat conversation. This surfaced during the Phase 9 dashboard discussion (conversion tracking, sales metrics) but isn't part of your original notes and is a real architecture decision, not a small add-on — don't build this until it's been deliberately scoped on its own.

- [ ] Open decision: **marketplace model** (Forr collects payment through its own Paystack account via Subaccounts/split payments, then pays out to the business minus a platform fee — carries real compliance weight since Forr would be holding other people's money) vs. **per-business keys** (each business connects their own Paystack account, same credential-storage pattern as Telegram's bot token or WhatsApp's Account SID — simpler for Forr, but every business needs their own working Paystack account before they can sell anything). Decide deliberately when you actually get here.
- [ ] Whichever model is chosen, tag every payment record with the customer and conversation it came from — Phase 9b's conversion tracking (enquired vs. paid) can't be computed later if this link isn't captured at the time the payment happens.

**✅ Confirm before moving on:** a real test purchase completes end-to-end through a chat conversation, the money lands in the right place under whichever model was chosen, and the payment record is correctly linked to its customer and conversation.

---

## Phase 11 — Finish the Shell *[added]*

**Goal:** The placeholders from Phase 2 become real before you call this launch-ready.

- [ ] Build out FAQs, Settings, Notifications, and Search properly — easy to leave stubbed once the AI features feel "done," but owners will notice.

**✅ Confirm before moving on:** every nav item from Phase 2 is fully functional, not a stub.

---

*Work top to bottom. If a phase turns out to need its own sub-map (Phase 6's agent wiring is the most likely candidate), just ask and we'll break that one down further.*
