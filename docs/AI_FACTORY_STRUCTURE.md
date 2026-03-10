# AI Factory — One-Page Structure

How our business maps to the “AI Factory & Agentic teams” idea.

```
┌─────────────────────────────────────────────────────────────────────────┐
│  CENTRAL LAYER ("AI Factory" / Command centre)                           │
│  • One entry: run agents, schedule, view logs                            │
│  • Unified config + profile (people, budget, preferences, risk)           │
│  • Optional: "Talk to your data" (e.g. spend summary, run history)        │
└─────────────────────────────────────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   CARTEL     │ │  FINANCIAL   │ │  (Future     │
│   (Shopping) │ │  ADVISOR     │ │   agents)    │
│ Plan → Cart  │ │ Surplus →    │ │ Calendar,    │
│ Woolies/Coles│ │ Allocation   │ │ Travel, etc. │
└──────────────┘ └──────────────┘ └──────────────┘
        │           │           │
        └───────────┼───────────┘
                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  YOUR DATA & PLATFORMS                                                  │
│  profile.json, config.json, run_logs, cart.json, finances, market data   │
└─────────────────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  SALES PLATFORM (Next.js)                                               │
│  Checkout, verify session → sell access to Cartel / Advisor / Factory   │
└─────────────────────────────────────────────────────────────────────────┘
```

**In one line:**  
*Central layer (Factory) runs and observes your agents; agents use your data; sales platform monetises access.*

**Current repo mapping:**

| Concept        | In this repo                          |
|----------------|----------------------------------------|
| Central layer  | To build (orchestrator script / app)   |
| Cartel         | `agent.py`, `planner.py`, woolies/coles|
| Financial Advisor | `financial-advisor/`               |
| Your data      | `profile.json`, `config.json`, `run_logs/`, `cart.json` |
| Sales          | `sales-platform/`                     |

See **BUSINESS_CONCEPT_AI_FACTORY.md** for full business model and next steps.
