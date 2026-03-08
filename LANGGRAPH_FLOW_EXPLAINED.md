# LangGraph Architecture - Step-by-Step Flow

This document explains the step-by-step logic of the system, strictly aligned with the flow diagram and design decisions outlined in `deliverables/architecture.md`. The assistant operates as a **Stateful Multi-Agent Workflow** using LangGraph.

---

## Node A: `[Start]`
Everything begins when the user sends a new message (`user_input`). LangGraph initializes the state and prepares to flow through the machine.

## Node B: `fetch_user_data`
* **Action:** The system accesses `source/adapters/utils/mock_data.py` to extract the complete raw JSON profile for the current user (orders, credit, balances).
* **State Update:** It saves this massive database payload directly into the graph's memory (`state["user_data"]`).
* **Architectural Reason:** Guarantees that downstream generative agents just read the state instead of worrying about database connections or missing context.

## Node C: `{Semantic Router}`
* **Action:** Acts as an independent "Traffic Cop" to decide where the user should go *before* generating a response.
* **Architectural Decision A (Independent Router):** Added to provide the final LLM with only relevant context, severely limiting hallucinations caused by "context overload".
* **Logic Edge 1 (Bypass):** If `state["is_return_in_progress"] == True`, it forcefully skips intent classification and routes directly to Node D (`handle_returns`). 
* **Logic Edge 2 (Inference):** If no return is in progress, the Router uses a zero-shot LLM prompt (`router_chain.py`) with strict structured outputs to classify the user's intent into an allowed topic.
* **Routing:** 
  * Classifies as RETURNS ➔ Triggers Node D (`handle_returns`)
  * Classifies as another topic ➔ Triggers Node E (`handle_general`)

## Node D: `handle_returns` (Multi-Step Flow)
* **Action:** A dedicated, strict agent that manages the Returns transactional machinery.
* **Architectural Decision B (Dedicated Handling):** Separated from the general flow because operations dictate strict, uninterrupted validation sequences (e.g., verifying a 15-day timeframe before asking the return reason). A generic agent often forgets to collect mandatory data before escalating.
* **State Mutation:** It toggles `is_return_in_progress = True` inside the State. This ensures that in the next user interaction (Node F), the Semantic Router (Node C) will be bypassed automatically, dropping the user right back here to continue their multi-turn complaint without amnesia.

## Node E: `handle_general` (Standard Inquiries)
* **Action:** The conversational worker assigned to catalog, shipping times, account balances, and general chatting.
* **Architectural Decision C (Data Filter System):** Before prompting the LLM, this node triggers `data_filter.py` to strip out unnecessary sensitive fields from the JSON (e.g., removing credit card hashes if the user is just asking for a product). This reduces token costs and prevents Data Leakage vulnerabilities.
* **Architectural Decision D (Knowledge Base Centralization):** This node queries `SCENARIO_KNOWLEDGE_BASE` using the topic defined by the router. It pulls *only* the specific instructions for that domain, decoupling the functional LangGraph logic from the business policies.

## Node Z: `[END]`
Regardless of whether the graph took Node D or Node E, both paths lead directly to `END`. The LangGraph traversal terminates, returning the populated `GraphState` object back to the main application. The final generated string inside `state["response"]` is then printed back to the user on the screen.
