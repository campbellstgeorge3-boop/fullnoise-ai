# How to Build Their Business (Actualisation-Style)

A practical playbook for building an **enterprise AI Factory & Agentic teams** business like [Actualisation Group](https://www.actualisation.ai/): sell to companies, not just to individuals.

---

## 1. What “their” business is

- **Offer:** Design and build the central “brain” of a company (AI Factory) that connects people, processes, data, platforms and products.
- **Deliverables:** Deploy AI agents, coach teams, automate complex processes.
- **Buyers:** Enterprises and mid-market companies that want “AI at the core.”
- **Revenue:** Likely consulting + build (projects, retainers, licences).

So we’re building: **a company that sells and delivers AI Factories and agentic teams to other companies.**

---

## 2. How to build it — six pillars

### Pillar 1: Offer design (what you sell)

| Offering | What it is | How to price (examples) |
|----------|------------|--------------------------|
| **Discovery / assessment** | Map their people, processes, data, platforms; identify agent opportunities | Fixed fee (e.g. 1–2 weeks) |
| **AI Factory design** | Architecture for central “brain”: orchestration, data access, agent roster | Design fee + optional build |
| **Agent build** | Custom agents (e.g. internal support, ops, data query, workflow) | Per-agent project or retainer |
| **Agentic team rollout** | Deploy multiple agents + coaching so teams use them | Project + change / training |
| **Ongoing run / improve** | Operate and iterate the Factory and agents | Monthly retainer or SLA |

Start with **one clear offer** (e.g. “AI Factory discovery + first agent”) so you can sell and deliver repeatably.

---

### Pillar 2: Who sells (go-to-market)

- **Direct:** You (or a co-founder) sell to decision-makers (COO, Head of Ops, CTO, “Head of AI”).
- **Partners:** System integrators, consultancies, agencies that already serve those companies — you deliver the AI Factory / agents; they bring the relationship.
- **Inbound:** Content that ranks for “AI agents for business”, “AI Factory”, “agentic AI teams”; demos and case studies (even anonymised) to convert.

Your existing agents (Cartel, Financial Advisor) are **proof you can build**: use them as demos (“we already run agentic workflows”) and as templates for “we’ll build agents like this, but for your data and processes”).

---

### Pillar 3: Delivery (how you build for clients)

- **Factory layer:** Central orchestration + config + logging. Can start as a thin wrapper (like we outlined in BUSINESS_CONCEPT_AI_FACTORY.md) and scale to multi-tenant or on-prem.
- **Agents:** Each client gets agents tailored to their workflows (support, scheduling, data lookup, approvals, etc.). Reuse patterns from Cartel and Financial Advisor (config → plan → act → observe → learn).
- **Data:** Connect to their systems (APIs, DBs, spreadsheets, CRMs). The “Factory” is the layer that agents call, not the client’s core systems.
- **People:** Workshops to define use cases; training so their teams use and trust the agents; clear handover and runbooks.

Keep delivery modular: **same Factory concept, different agents and data per client.**

---

### Pillar 4: IP and reuse

- **Framework:** One “AI Factory” architecture (orchestrator, agent interface, config, logs) that every engagement uses. Improves over time.
- **Agent templates:** Shopping (Cartel), finance (Advisor), and future ones (e.g. calendar, inventory, booking) become **templates** you adapt for clients (e.g. “inventory agent” for a retailer, “allocation agent” for a fund).
- **This repo:** Cartel + Financial Advisor + planner + tools = proof and reusable patterns. You don’t ship grocery shopping to a bank; you ship “we’ve built agents that plan, act, and learn — here’s how we’ll do it for you.”

So: **build their business by reusing and generalising what we already have.**

---

### Pillar 5: Company structure (minimal)

- **Core team (early):**  
  - Sales / positioning (you or a partner).  
  - Delivery (you or a technical co-founder): design Factory, build agents, integrate data.  
  - Optional: one person for marketing/content and one for operations as you scale.

- **Legal:** Company entity, contracts (MSA, SOW, IP ownership), privacy/DPA for client data. Get templates from a lawyer used to tech/consulting.

- **Brand:** Name, one-pager, website that explains “We build AI Factories and agentic teams for your business” and points to outcomes (speed, automation, “talk to your data”), not just tech.

---

### Pillar 6: First 12 months (tactical)

| Phase | Focus |
|-------|--------|
| **Months 1–2** | Lock offer: e.g. “AI Factory discovery + first agent”. One-pager + simple site. List 50 target companies (industry, size, role to contact). |
| **Months 2–4** | First 2–3 conversations (warm intros or outbound). Run one **paid discovery** (even at a discount) and deliver a clear “AI Factory design + agent roadmap” for that client. |
| **Months 4–6** | First **full build**: one client, one Factory + 1–2 agents. Reuse our orchestration and agent patterns. Document everything for reuse. |
| **Months 6–9** | Second client (different industry or use case). Refine framework and sales story. Optional: one partner (SI or consultancy) to co-sell. |
| **Months 9–12** | Package “AI Factory in a box” (design + deploy template). Aim for 2–3 live clients and a repeatable sales and delivery motion. |

---

## 3. How this repo fits

- **Cartel / Financial Advisor:** Demos and templates. “We run agentic workflows ourselves; we’ll build the same kind of thing for your processes.”
- **Planner, tools, config, run_logs:** Patterns for “plan → act → observe → learn” and config-driven agents. Reuse in client agents.
- **Sales platform:** Can later sell **productised** offerings (e.g. “Factory starter pack”) or training, not only custom build.
- **docs/BUSINESS_CONCEPT_AI_FACTORY.md, AI_FACTORY_STRUCTURE.md:** Internal reference for what the “Factory” is; adapt the diagram and language for client proposals.

---

## 4. One-line summary

**To build their business:** Define one enterprise offer (e.g. AI Factory discovery + first agent), sell it to 1–2 paying clients, deliver using a reusable Factory + agent framework, and use this repo as your proof and template. Scale with more clients and partners, then productise (e.g. “Factory in a box”) once the motion works.

If you say which part you want to do first (offer, sales, or delivery), we can break it into concrete next steps (e.g. one-pager copy, first outreach list, or a minimal “Factory” orchestrator for a demo client).
