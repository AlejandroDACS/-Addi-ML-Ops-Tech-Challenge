# LangGraph Architecture - Step-by-Step Flow

This document explains the step-by-step logic of each node and edge present in the `langgraph_architecture.png` diagram. The system behaves as a directed acyclic graph (with memory) to process every message sent by the user.

## 1. Start / Entry Point: `fetch_user_data`

* **What it does:** Every time the user sends a message, the graph starts executing at this node.
* **Logic:** 
  1. It reads the current `user_id` from the connection or the active state.
  2. It accesses the system's mock database (`source/adapters/utils/mock_data.py`).
  3. It extracts the complete raw JSON profile of that specific user (name, orders, available credit, active balance) and saves it directly into the graph's State (`state["user_data"]`).
* **Why it is here:** To guarantee that the rest of the downstream agents don't have to worry about querying databases. They just read the state.

---

## 2. Unconditional Edge: `fetch_user_data` ➔ `router`

After successfully downloading the user's data into the State, the graph automatically pushes execution forward to the Router node.

---

## 3. Node: `router`

* **What it does:** It acts as the "Traffic Cop" or the intelligent front-door receptionist.
* **Logic:** 
  1. **Memory Check (Bypass):** First, it checks if `state["is_return_in_progress"]` is `True`. If the user is currently engaged in a multi-step complaint/return from a previous message, it skips all AI analysis, immediately assigns `selected_agent = "handle_returns"`, and finishes.
  2. **Inference Flow:** If there is no previous return in progress, it invokes `router_chain` (powered by Google Gemini at Temperature 0).
  3. The LLM evaluates the user's intent exclusively among a list of allowed topics (Product, Payments, Operations, Platform).
  4. Once categorized, it sets `state["selected_agent"]` to either `"handle_returns"` (if the topic is return-related) or `"handle_general"` (for anything else).
* **Why it is here:** To avoid stuffing the final conversational AI with conflicting business rules.

---

## 4. Conditional Edge/Gate: `route_to_agent`

This logic block reads the decision made by the router node and physically moves the graph's execution to the correct path. It evaluates the string parameter stored in `state.get("selected_agent")`.

* **Path A:** `If "handle_returns" ➔ Route to handle_returns node`
* **Path B:** `If "handle_general" ➔ Route to handle_general node`

---

## 5. Branch A - Node: `handle_general`

* **What it does:** Conversational worker assigned to answer typical inquiries, catalogs, shipping times, or accounting balances.
* **Logic:** 
  1. Uses the topic string defined by the router to query the `SCENARIO_KNOWLEDGE_BASE`.
  2. Pulls only the specific instructions relevant to that topic.
  3. Triggers the `data_filter.py` utility to clean up the `user_data` JSON, deleting unnecessary fields (like credit card hashes if the user is just asking for a product recommendation).
  4. Prompts the generative AI model via `general_chain` with a local Colombian tone to generate the final response (`state["response"]`).

---

## 6. Branch B - Node: `handle_returns`

* **What it does:** A specialized, strict agent that manages the Returns transactional machinery.
* **Logic:** 
  1. Uses finite-state machine steps to not get lost.
  2. If the user initiates a return, the LLM sets `is_return_in_progress = True` inside the State.
  3. Before actually responding, it strictly verifies via `returns_chain` if the user provided enough context (Reason for the return, which exact item order).
  4. If the info is incomplete, it returns a question and halts. In the next turn, because `is_return_in_progress` is still True, the router will bypass and drop the user right back here to continue the process seamlessly.
  5. Once all conditions are met, it sets `is_return_in_progress = False` and issues the logistical pickup confirmation.

---

## 7. The Final Edge: ➔ `__end__`

Regardless of whether the graph took the `handle_general` route or the `handle_returns` route, both nodes lead directly to `END`.
At this stage, the LangGraph traversal is terminated. The orchestrator returns the populated `GraphState` object back to the main application (the CLI terminal or the Web API), and the user finally gets to read the string printed in `state["response"]`.
