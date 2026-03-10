# Business Concept: AI Factory & Agentic Teams

*Inspired by the [Actualisation Group](https://www.actualisation.ai/) structure — adapted for our own positioning, products, and agents.*

---

## 1. Core idea (their framing, our execution)

**Their framing:**  
*"We build AI Factories & Agentic AI teams. An AI Factory is the central 'brain' of your business — people, processes, data, platforms and products. Deploy AI Agents, coach individuals, automate complex processes."*

**Our angle:**  
Build a **personal / SMB-focused AI Factory**: a central layer that orchestrates **multiple agents** (shopping, finance, and more) around **one person or one small business**, with a clear product and pricing path. We don’t sell “enterprise transformation”; we sell **time back** and **better decisions** via agents that already work.

---

## 2. Business structure (adapted from their model)

| Layer | Actualisation (enterprise) | Our version (personal / SMB) |
|-------|----------------------------|------------------------------|
| **Central “brain”** | Company-wide AI Factory | **Personal / SMB command centre**: one place to run and monitor all your agents |
| **People** | Teams across the org | **You** (or a small team); agents act on your behalf |
| **Processes** | Enterprise workflows | **Personal workflows**: meal planning → cart; income → allocation; etc. |
| **Data** | Company data lakes, CRM, ERP | **Your data**: profile, preferences, finances, carts, run logs |
| **Platforms** | Internal tools, clouds | **Our platform**: agent runner, config, sales/checkout (e.g. sales-platform) |
| **Products** | Custom AI solutions | **Shippable agent products**: Cartel (shopping), Financial Advisor, future agents |

---

## 3. What we already have (agents as products)

- **Cartel (shopping agent)**  
  Plan meals → build list → compare Woolworths/Coles → fill cart. Learn from failures; never touches payment.  
  **Product idea:** “Plan once. Shop both. Never overpay.”

- **Financial advisor agent**  
  Surplus + market snapshot → allocation (save / stocks / crypto) + rationale. Fortnightly runs.  
  **Product idea:** “One agent that keeps your surplus allocation sane.”

- **Sales platform**  
  Next.js app: checkout, session verification.  
  **Use:** Sell access to agents (licence, subscription, one-off).

Together these form a **minimal agentic team**: shopping + money advice + a way to sell them.

---

## 4. “AI Factory” we can build (central layer)

A **lightweight Factory** doesn’t need to be enterprise software. It can be:

1. **Orchestration**  
   One entry point (CLI or simple UI) that:
   - Runs the shopping agent (e.g. weekly).
   - Runs the financial advisor (e.g. fortnightly).
   - Optionally: “Talk to your data” (e.g. “What did I spend on groceries last month?” from run_logs + profile).

2. **Unified config / profile**  
   - One place for “who I am” and “what I want” (people, budget, avoid list, risk tolerance).
   - Agents read from this; the Factory doesn’t duplicate logic, it routes and schedules.

3. **Observability**  
   - Run logs, success/failures, optional simple dashboard.
   - “Last 4 runs”, “Cartel vs budget”, “Advisor recommendations history”.

4. **Extensibility**  
   - New agents (e.g. calendar, travel, inventory) plug in the same way: config, run, log.

That’s our **AI Factory**: central brain + your data + your processes + your agents + one platform to run and (optionally) sell them.

---

## 5. Business model options

- **B2C (consumers)**  
  - Sell **Cartel** and/or **Financial Advisor** as desktop/CLI tools (one-off or subscription).  
  - Sales platform = checkout + licence/API key or subscription.

- **B2B (SMB)**  
  - “Agent stack for your business”: e.g. inventory agent, booking agent, finance agent.  
  - Same Factory idea: one dashboard, multiple agents, your data.

- **White-label / partner**  
  - Offer the **structure** (or specific agents) to other brands: “Your brand’s shopping assistant powered by our agent.”

---

## 6. Differentiation from Actualisation

- **Audience:** We focus on **individuals and SMBs**, not “every company in the world” enterprise.
- **Product:** We ship **concrete agents** (shopping, finance) with clear outcomes, not only consulting or custom builds.
- **Scope:** Our “Factory” is **personal/SMB command centre**, not enterprise data lakes and org-wide workflows.
- **Message:** “More time, better decisions, one place for your agents” rather than “AI Factory at the core of your business.”

---

## 7. Next steps (practical)

1. **Name the “Factory”**  
   Product name for the central layer (e.g. “Command”, “Hub”, “Brain”) and use it in positioning.

2. **Single entry point**  
   One script or app: “Run Cartel”, “Run Advisor”, “Show last runs” — even if it’s a thin wrapper at first.

3. **Unified profile**  
   Design one config/profile schema that both Cartel and Financial Advisor can use (or a small adapter layer).

4. **Sales platform**  
   Tie checkout to “access to Cartel” or “access to Advisor” or “access to Factory (all agents)”.

5. **One-pager / landing**  
   “Your AI Factory: Plan meals, manage surplus, one place.” Link to Actualisation-style ideas without copying: we’re the **personal/SMB** version.

---

*This doc is a living outline. Update as you add agents, change pricing, or refine the central “Factory” product.*
