# AI & ML Ops Tech Challenge

### 📚 Exclusive Solution Documentation
To fully understand the engineering, architecture, and scalability decisions, please consult the following documents I have prepared:

1. 🧠 **[Expansive Project Documentation](PROJECT_DOCUMENTATION.md)** 
2. 🏛️ **[Architecture and Design](deliverables/architecture.md)**
3. ☁️ **[Production Deployment Answers](deliverables/deployment_answers.md)**

### 📚 additional challenge
Now, we present the theoretical solution to the second selected problem, which was:

🧠  **[Credit Default Prediction](Credit-Default-Prediction-Model.html)** 

---

## Challenge Summary

**Emporyum Tech** is a Colombian e-commerce platform offering installment payment plans (Buy Now, Pay Later). In this challenge, you receive a **basic functional prototype** of a conversational AI assistant for Emporyum Tech. The prototype works end-to-end: you can ask questions and it will answer. **But the quality is poor.** The architecture is minimal, the Knowledge Base is shallow, and answers are vague and generic.

Your task is to **significantly improve the quality and architecture of the assistant**. How you do it — what you build, how you structure it, what design decisions you make — is entirely up to you.

## Time Estimation

**6-8 hours** for a complete solution. You don't need to finish everything — a well-designed partial solution with clear documentation is preferred over a rushed complete solution.

## Prerequisites

- Python 3.10 or higher
- [Poetry](https://python-poetry.org/docs/#installation) for dependency management
- An OpenAI API key (GPT-4o-mini or Gemini Flash is sufficient and cost-effective)

## Quick Start

Run the basic solution first. Watch it work. Notice the problems.

```bash
# 1. Install dependencies
poetry install

# 2. Create your .env file and add your API key
# SECURITY EXPLANATION: The real .env file has been deliberately excluded
# from this repository (via .gitignore) to prevent private API Key leakage.
# You must generate your own local copy using this template:
cp .env.example .env

# 3. Run the interactive assistant
poetry run python tests/inline.py
```

Try these conversations and observe the responses:

| If you type | What you should notice |
|-------------|------------------------|
| `Hi!` | Generic greeting, not personalized for the user |
| `Where is my order?` | Vague response, no specific order details |
| `How much do I owe in installments?` | Vague response, no breakdown of installments |
| `I want to return a product` | Generic single-sentence response, no multi-step transactional flow |
| `What time is it?` | Tries to answer anyway -- no out-of-scope topic handling |

## Business Context

**Emporyum Tech** is a Colombian e-commerce platform that distinguishes itself by offering purchases in installments. Customers can buy products from multiple categories and split payments into monthly installments with different interest rates.

The business is organized into 4 verticals, each with its own set of rules, edge cases, and data requirements:

- **Product and Catalog** (`team_product.md`): ~290 products across 4 categories (Electronics, Home, Fashion, Beauty). Product recommendations based on user history and preferences. 5 active promotions with specific rules.

- **Payments and Installments** (`team_payments.md`): 4 payment methods (PSE, Credit Card, Efecty, Bancolombia A la Mano). Installment plans from 1 to 24 months with different interest rates. Late payment policies and amount calculations.

- **Operations and Logistics** (`team_operations.md`): Full purchase flow from browsing to delivery. Order tracking through 6 states. Delivery times by city. Return and refund policies with strict eligibility rules.

- **Platform and Account** (`team_platform.md`): Account management, password reset, two-factor authentication (2FA). App features and technical troubleshooting. Security policies.

The detailed business requirements for each area are available in the `docs/stakeholder_interviews/` folder. These interview transcripts contain the specific rules, flows, edge cases, and data fields you must consider to design the Knowledge Base and the assistant's architecture.

## Project Structure

```
ai_ml_ops_challenge/
|
|-- README.md                            # <-- YOU ARE HERE
|-- pyproject.toml                       # Native project dependencies
|-- .env.example                         # Template for your API key
|-- .env                                 # You create this (not pushed to git)
|
|-- docs/
|   |-- stakeholder_interviews/          # Your main sources: business requirements
|       |-- team_product.md              #   Product team interview
|       |-- team_payments.md             #   Payments team interview
|       |-- team_operations.md           #   Operations team interview
|       |-- team_platform.md             #   Platform team interview
|
|-- source/
|   |-- __init__.py
|   |
|   |-- application/
|   |   |-- __init__.py
|   |   |-- state.py                     # GraphState TypedDict (do not modify)
|   |   |-- graph.py                     # LangGraph Topology Definition
|   |
|   |-- domain/
|   |   |-- __init__.py
|   |   |-- router.py                    # Classifier and flow initiator
|   |   |-- handle_general.py            # General orchestrator
|   |   |-- handle_returns.py            # Dedicated synchronous flow for Returns
|   |
|   |-- adapters/
|   |   |-- __init__.py
|   |   |-- chains/
|   |   |   |-- __init__.py
|   |   |   |-- general_chain.py         # Generic LLM Prompt
|   |   |   |-- router_chain.py          # Router LLM Prompt
|   |   |   |-- returns_chain.py         # Returns LLM Prompt
|   |   |-- utils/
|   |       |-- __init__.py
|   |       |-- mock_data.py             # 8 fake user profiles (do not modify)
|   |       |-- data_filter.py           # Mitigating JSON filter for tokens
|   |       |-- knowledge_base.py        # Centralization of directives from the 4 teams
|   |
|   |-- examples/                        # Framework pattern references
|       |-- README.md
|       |-- example_kb_entry.py          #   Database entry schema
|       |-- example_chain.py             #   LLM Chain with Pydantic outputs
|       |-- example_domain_function.py   #   Async domain function pattern
|       |-- example_graph.py             #   Rudimentary executable graph
|
|-- tests/
|   |-- __init__.py
|   |-- inline.py                        # CLI to test development dynamically
|
|-- deliverables/
|   |-- architecture.md                  # Theoretical documentation of your architecture
|   |-- deployment_answers.md            # QA Deliverable for MLOps / DevOps
```

## Pre-Built Elements (Do Not Modify)

These files are provided and **should not** be modified:

| File | Description |
|------|-------------|
| `source/application/state.py` | Dictionary (`GraphState TypedDict`) defining all fields flowing through LangGraph |
| `source/adapters/utils/mock_data.py` | 8 fake user profiles with mock orders, installments, and account statements |
| `source/adapters/utils/data_filter.py` | Vital utility to filter user data and inject *only* authorized variables |
| `source/examples/*` | Framework pattern references |
| `docs/stakeholder_interviews/*` | Transcripts of the 4 leadership interviews |
| `pyproject.toml` | Native project dependencies |

## Original Problems Resolved

Upon receiving the original code, it presented numerous critical flaws, which were redesigned. Among the issues addressed are:

| Original Problem | Where to look |
|----------------|---------------|
| Every question received the same generic treatment without routing | `router.py`, `graph.py` |
| Responses were vague and impersonal | `general_chain.py` |
| The Knowledge Base was shallow and fractured | `knowledge_base.py` |
| Sensitive user data was clumsily injected | `data_filter.py`, `handle_general.py` |
| The Assistant forgot what had been said, preventing multi-turn processes | `handle_returns.py`, `inline.py` |

## Deliverables

1. **An improved assistant** -- The bot must demonstrate significantly better quality, organically covering the interview domains, evidencing routing, and using data with security barriers (guardrails).

2. **Architecture documentation** (`deliverables/architecture.md`) -- Document with diagrams, semantic context, and exhaustive explanations of what you built and why.

3. **Deployment Answers** (`deliverables/deployment_answers.md`) -- Production-oriented answers from the Infra/ML Ops side.

## Evaluation Criteria

What we value, in approximate order of importance:

- **Knowledge Base Quality** -- Effectively transcribing business rules to the application.
- **Cognitive Architecture** -- Breaking down the problem using LangGraph routers with smart topology and State management as inter-turn control variables.
- **Output Quality** -- That the bot provides correct answers using personal simulated data and handles deviations *(Out of scope)*.
- **Focus on Production and MLOps** -- Solid and reasoned answers regarding spikes and drops in `deployment_answers.md`.
- **Explanation of Solution** -- Transparency and technical accuracy when describing what was developed in `architecture.md`.

## Final Tips

1. **Read ALL 4 interview files before reviewing the code.** They are your primary source of requirements and guardrails.
2. Read `state.py` to internalize what variables circulate in the *graph* each time a step is advanced.
3. Simple and functional is better than complex and unfinished.

## Final Delivery

1. Ensure that running `poetry run python tests/inline.py` works in the terminal without throwing import errors.
2. Verify that at least one full profile flow resolves end-to-end processes.
3. Compress the entire `ai_ml_ops_challenge/` folder into a ZIP format (Changing it to your name or ensuring it is a secure folder).
4. Return it.

Congratulations and excellent development!
