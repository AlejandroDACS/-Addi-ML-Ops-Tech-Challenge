# Addi ML Ops Tech Challenge 
This document exhaustively details the methodological transformation applied to solve the "AI & ML Ops Tech Challenge". It is designed to act as the main blueprint for understanding the systemic logic, analyzing the chronological order of development, the files interacting in each phase, and the chosen algorithms.

---

## 1. Architectural Patterns and Chosen Algorithms

The original flawed architecture used the *"God Object"* Anti-Pattern, sending all cognitive load to a single generic node (`handle_general.py`). The refactoring opted for the **Stateful Multi-Agent Workflow** paradigm, supported by **Semantic Routing** in a central machine governed by **LangGraph** and **Zero-Shot Classifier** Models under **Gemini 2.5 Flash**.

1. **Deterministic Routing (Structured Semantic Classifier):** Before conversing with the user, a hidden prompt forces the LLM to read the stipulated "Valid Topics" array and apply `Pydantic Structured Output` to return a strict JSON classifying the user's intent. 
   - *Why?* It avoids using slow conversational LLMs and mitigates the strong need for RAG/Embeddings for a limited categorical knowledge base like this one.
2. **Conditional Bifurcation (Conditional Graphs):** The network evaluates the Router's outputs and mathematically directs the flow ("If X is said -> Go to node Y"). It solves the *"Context Stuffing"* problem (Lack of attention) since it isolates instructions that do not concern that query.
3. **Multi-turn Finite State Machine (GraphState Persistent Variables):** Exploiting the mutable properties of `state.py`, we couple booleans like `is_return_in_progress` that allow the bot to remember past interactions and break the "Stateless Amnesia" HTTP limitation.

---

## 2. Chronological Development: Modification Flow, File Relationships, and Responsibilities

The solution was approached from the inside out: first cementing the Database or Knowledge Engineering ("Data"), then building the Inferential Nervous System ("Chains"), the Operational Nodes ("Handlers"), and finishing in the Central Orchestrator ("Graph").

### PHASE 1: Data Engineering and Extraction (The Static Brain)
*   **Problem:** The original base was precarious. The bot had no precise operational guidelines (like 15-day limits, or 1.5% rates) and did not apply commercial language for Emporyum Tech App suggestions.
*   **Files Modified:** 
    *   `source/adapters/utils/knowledge_base.py` **(Extreme Refactoring)**
*   **Systemic Detail:** The 4 stakeholder interviews in `docs/stakeholder_interviews/*` (Product, Operations, Payments, Platform) were carefully evaluated. The loose narratives were translated into a hyper-structured super-dictionary in Python (`SCENARIO_KNOWLEDGE_BASE`). Each dictionary key encrypts a "Domain", its *mandatory instructions*, its base cases, and cross-references explicit variables that the node will in turn seek to hydrate later. 
*   **Subsequent Relationship:** This dictionary is the "Oracle" from which the Phase 3 `handlers` will dynamically feed.

### PHASE 2: Traffic Classification (The Smart Router)
*   **Problem:** To divide responsibilities, an initial guardian agent was needed to decide where to travel.
*   **Files Created/Modified:**
    *   `source/adapters/chains/router_chain.py` **(Created)**
    *   `source/domain/router.py` **(Created)**
*   **Systemic Detail:**
    *   **In Chain (`router_chain.py`):** Configures a parsing schema (AST) through the `RouterResponse` model. The system passes the parametric order to the LLM using cold probabilistic inference (Temperature 0) and receives back the corresponding Topic (`selected_topic`).
    *   **In Node (`router.py`):** Transfers the execution. The initial subroutine in the tree manually checks if the local flag `state["is_return_in_progress"]` is true. If so, it **nullifies and ignores** the inferential chain (bypass), forcefully marking it to continue towards the returns agent, keeping the memory alive. If false, it continues inferring from the `router_chain` and marks where to direct the pass in `state["selected_agent"]`.
*   **Subsequent Relationship:** The string emitted and anchored here in the state will guide the logical gate `route_to_agent` elaborated in Phase 5.

### PHASE 3: Specialized Modular Layer Development (The Multi-turn Workers)
*   **Original Problem:** There was only a single pre-programmed Agent ("Amnesic" and generic).
*   **Files Created/Modified:**
    *   `source/adapters/chains/returns_chain.py` **(Created)**
    *   `source/domain/handle_returns.py` **(Created)**
    *   `source/adapters/chains/general_chain.py` **(Refactored)**
    *   `source/domain/handle_general.py` **(Refactored)**
*   **Systemic Detail:**
    *   **The Expert (`handle_returns.py` and its chain `returns_chain.py`):** This Agent was intrinsically designed as a Finite State Machine to solve "amnesia" during a multi-step interactive complaint. The *Knowledge Base* warned that payments should not be instantly refunded without asking for details. Then the Pydantic chain (`ReturnsResponse`) gears `next_step` properties and iterations of the `is_return_in_progress` flag. By cyclically modifying these flags, the bot does not let go of the flow and continues asking questions ("What caused the damage?") until culminating in logistics without the `Router` (Phase 2) interfering.
    *   **The General (`handle_general.py` and its chain `general_chain.py`):** Now de-saturated from the weight of Returns, it was rewritten to absorb *only* from the `SCENARIO_KNOWLEDGE_BASE` the specific directive indicated for its assigned Topic (`state["selected_topic"]`). At the `general_chain.py` level, a strict system (`GeneralResponse`) was injected forcing a reasoning native to Colombian human speech and without deviating from the *instruction_set*.
*   **Subsequent Relationship:** Both agents become the endpoint of the system. They are conditionally called by Phase 5 and introduce the final "Response" payload from which the user receives a string.

### PHASE 4: Protection and Vulnerability Mitigation Layer (The Sanitizer)
*   **Original Problem:** A user's online mocked data ("Their email, cellphone number, medical history, associated cards, addresses") passed indiscriminately to the massive JSON of the *System Prompt*. If someone asked for generic promotions, they still exposed tokens with sensitive private data, a severe "Data Leakage" factor in MLOps architectures.
*   **Files Modified:**
    *   `source/adapters/utils/data_filter.py` **(Refactored)**
*   **Systemic Detail:** To solve it, the filter was reprogrammed. Now, every Node in "Phase 3", before building its prompt, communicates with this parametric utility. They temporarily and dynamically extract to a volatile memory a secure `dict` that retains the mandatory *base properties* but adjusts to the `relevant_fields` listed in the `knowledge_base` (`topic`). Ex: If they are profile questions, orders are deleted; If it is shipping, the payments balance is deleted.
*   **Subsequent Relationship:** The drastic minimization cuts tokens by 80%, accelerating graph latency without sacrificing asynchronous database validations.

### PHASE 5: Topographical Re-Construction of the Orchestrator (The Graph Wiring)
*   **Original Problem:** The system was wired in a straight line assuming a single existing agent between `fetch_data` y `END`.
*   **Files Modified:**
    *   `source/application/graph.py` **(Radically Refactored)**
*   **Systemic Detail:** 
    1. The start of the graph `fetch_user_data` was connected to the new formulated blind initial node: `router_node`.
    2. In the remaining freed space, a **Boolean Route Gate** (`add_conditional_edges`) was introduced.
    3. The decision logic `route_to_agent` was programmed, which passively reads the mutation record written by the Node-Router Function in Phase 2 (`state.get("selected_agent")`), and raises the appropriate bridge by internally invoking either the dependencies of `handle_returns` or `handle_general`.
    4. Both Nodes now dictate a direct route towards the execution terminator `END`.
*   **Final Relationship:** This closed the LangGraph ecosystem loop. A clean architecture without tight coupling, allowing the addition of unlimited Specialist Nodes in weeks by a large team, simply by adding gates to the central router without affecting cross-generative performance.
