# How to Start Building the Canopy

A step-by-step plan to start building your **large company** (the “canopy”) in the AI Factory / agentic space — from where you are now to a real business.

---

## What “the canopy” is

The **canopy** = the big structure: your company that designs, builds and runs **AI Factories and agentic teams** for other companies. You don’t build it in one go. You build it by doing **one thing, then the next**, and letting each step support the next.

---

## Phase 0: Lock the foundation (Week 1–2)

**Goal:** One clear offer, one name, one way to describe what you do.

### 1. Name the company

- Pick a **company name** (can change later; you need something to put on a one-pager and in emails).
- Optional: name your core product (e.g. “Factory”, “Command”, “Core”) so you can say “We build [Product] and agentic teams for your business.”

### 2. Write your one offer

- **One sentence:** “We help [who] to [outcome] by [what you do].”
  - Example: “We help mid-market companies get from ‘AI experiments’ to running AI agents in production by designing and building their AI Factory and first agents.”
- **One offer** to sell first (so you’re not selling “everything”):
  - Example: **“AI Factory discovery + first agent”** = 1–2 week discovery (map data, processes, use cases) + design + build one agent (e.g. internal Q&A, scheduling, or data lookup). Fixed price or capped scope.
- **One price band** (even rough): e.g. “Discovery: $X–Y”, “First agent: $Z”. You can refine after first conversations.

### 3. Write your one-pager (1 page PDF or web page)

- Headline: what you do (AI Factory + agentic teams).
- Problem you solve: “Companies want AI/agents but can’t get them into production.”
- What you deliver: your one offer (discovery + first agent).
- Proof: “We already run agentic workflows” + point to Cartel & Financial Advisor as demos (no need to name them; “we run planning, automation and decision agents”).
- Call to action: “Book a 30‑min call” or “Reply to this email.”
- Contact.

**Output:** Company name, one offer, one sentence, one-pager. No code yet — this is how you’ll talk to people.

---

## Phase 1: First conversations (Week 3–6)

**Goal:** Talk to real buyers. Learn what they care about. Get one “yes” to a paid discovery or pilot.

### 4. List 30–50 targets

- **Who:** Companies that could buy (mid-market or enterprise in one industry you know: e.g. field services, retail, logistics, professional services).
- **Role to contact:** COO, Head of Ops, CTO, or “Head of AI / Digital” — whoever owns “how we get work done” or “how we use AI.”
- Put them in a simple list (spreadsheet or doc): company, name, role, LinkedIn or email, source (intro / cold).

### 5. Get in front of them

- **Warm:** Ask for one intro per week from your network (“I’m starting X; who do you know who’s thinking about AI agents / automation?”).
- **Cold:** Short email (3–4 lines): who you are, what you do (one sentence), one outcome, ask for 20–30 min to see if it’s a fit. Attach or link your one-pager.
- **Outcome:** 5–10 conversations. In each, ask: “Where are you with AI/agents? What’s blocking you? What would ‘success’ look like in 6 months?”

### 6. Propose your first paid engagement

- For 1–2 people who said “we’re stuck” or “we want to move beyond experiments”: propose **your one offer** (discovery + first agent).
- Send a short proposal (1–2 pages): scope, what they get, timeline, price. Offer a call to discuss.
- **Goal:** One signed discovery or pilot. Even at a discount, the aim is **deliver something real and get a reference.**

**Output:** 5–10 conversations, 1 signed discovery/pilot. You’re now “building the canopy” by having a real client.

---

## Phase 2: Deliver the first engagement (Week 7–14)

**Goal:** Deliver the discovery and (if in scope) the first agent. Reuse your repo as the “engine”; the client gets something that works.

### 7. Run discovery

- Map: their key processes, data sources (CRMs, spreadsheets, APIs), pain points, and “first agent” use case (e.g. “answer internal questions from our docs”, “schedule X”, “summarise Y”).
- Produce: a short **AI Factory design** (1–3 pages): central layer (data + orchestration), where the first agent fits, what you’ll build.
- Get their sign-off before build.

### 8. Build the first agent (and a minimal “Factory”)

- **Factory:** Even a minimal version: one place that loads config, runs one (or more) agents, and logs runs. Can be a thin wrapper around your existing patterns (see `docs/AI_FACTORY_STRUCTURE.md`). Host it where the client is comfortable (their cloud, or yours with a contract).
- **Agent:** Build one agent that does the agreed job (e.g. “query our docs”, “suggest schedule”). Reuse the **plan → act → observe → learn** pattern from Cartel/Advisor; swap their data and tools for yours.
- **Handover:** Short doc: what it does, how to run it, how to change config. One training call.

### 9. Capture for reuse

- Note what you’d do the same vs different next time (discovery questions, Factory layout, agent interface).
- Turn the engagement into a **case study** (anonymised if needed): “We designed their AI Factory and built their first agent; they now [outcome].”
- Update your one-pager with “We’ve delivered for [industry/size]” and the case study.

**Output:** First delivered client, one case study, a reusable “Factory + one agent” pattern. The canopy is one real project old.

---

## Phase 3: Repeat and systemise (Month 4+)

**Goal:** Second client, clearer process, and the start of a “productised” offer.

### 10. Second client

- Use the case study and one-pager to get 5–10 more conversations.
- Propose the same offer (discovery + first agent) or a variant (e.g. “second agent”, “coaching rollout”).
- Deliver using the same discovery + Factory + agent pattern. Each time you’ll be faster.

### 11. Systemise

- **Sales:** Same one-pager, same email template, same proposal template; refine based on what works.
- **Delivery:** Checklist for discovery, standard Factory layout, agent template (config, run, log). Your repo becomes the **template**; each client gets a copy or instance tailored to them.
- **Legal:** Simple MSA + SOW (get a lawyer to draft or adapt). Use them for every new client.

### 12. Decide how to grow the canopy

- **More clients same offer:** Keep selling “discovery + first agent” until you have 3–5 delivered and a waitlist.
- **Wider offer:** Add “second agent”, “ongoing run”, or “team coaching” as upsells.
- **Productise:** “Factory in a box” — fixed-scope design + deploy for a segment (e.g. “Field services AI Factory”).
- **Partner:** One SI or consultancy that refers you; you deliver, they own the relationship.
- **Team:** First hire when you’re consistently selling and delivering (e.g. delivery so you can focus on sales, or sales so you can focus on delivery).

**Output:** Second (and third) client, repeatable process, and a clear next move (more clients, wider offer, product, partner, or hire).

---

## What you already have (use it)

| Asset | How to use it |
|-------|----------------|
| **Cartel (shopping agent)** | Demo: “We run agents that plan, act and learn. Here’s one that does grocery planning and cart build.” Proves you can build agents. |
| **Financial Advisor** | Demo: “We run decision agents on data (market + surplus → allocation).” Proves you can build logic + data agents. |
| **planner.py, config, run_logs** | Pattern for config-driven workflows and observability. Reuse in client agents. |
| **sales-platform** | Later: sell productised offers (e.g. “Factory starter”) or training. Not needed for first B2B clients. |
| **docs/** | BUSINESS_CONCEPT_AI_FACTORY, BUILD_THEIR_BUSINESS_PLAYBOOK, AI_FACTORY_STRUCTURE, MARKET note = your internal playbook. Use them; don’t wait to perfect them. |

---

## Summary: start here

1. **Week 1–2:** Name, one offer, one sentence, one-pager.  
2. **Week 3–6:** 30–50 targets, 5–10 conversations, 1 signed discovery/pilot.  
3. **Week 7–14:** Deliver discovery + first agent; minimal Factory; case study.  
4. **Month 4+:** Second client, systemise, then choose: more clients, wider offer, productise, partner, or hire.

The **canopy** gets built by doing these steps over and over: offer → conversations → deliver → reuse → repeat. Start with Phase 0; everything else follows from that.
