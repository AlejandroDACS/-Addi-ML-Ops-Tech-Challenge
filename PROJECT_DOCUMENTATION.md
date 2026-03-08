# Addi ML Ops Tech Challenge 
This document exhaustively details the methodological transformation applied to solve the "AI & ML Ops Tech Challenge." It is designed to act as the master scroll for understanding the systemic logic, analyzing the chronological development order, the interacting files in each phase, and the chosen algorithms.

---

## 1. Architectural Patterns and Chosen Algorithms

The original flawed architecture used the *"God Object"* Anti-Pattern, sending the entire cognitive load to a single generic node (`handle_general.py`). The refactoring opted for the **Stateful Multi-Agent Workflow** paradigm, supported by **Semantic Routing** in a central machine governed by **LangGraph** and **Zero-Shot Classifier** Models under **Gemini 2.5 Flash**.

1. **Deterministic Routing (Structured Semantic Classifier):** Before conversing with the user, a masked prompt forces the LLM to read the array of stipulated "Valid Topics" and apply `Pydantic Structured Output` to return a strict JSON classifying the user's intent. 
   - *Why?* It avoids using slow conversational LLMs and mitigates the heavy need for RAG/Embeddings for a limited categorical knowledge base like this one.
2. **Conditional Edging (Conditional Graphs):** The network evaluates the Router's outputs and mathematically directs the flow ("If X is said -> Go to node Y"). It solves the problem of *"Context Stuffing"* (Lack of attention) since it isolates instructions that do not concern that query.
3. **Multi-turn Finite-State Machine (Persistent GraphState Variables):** Exploiting the mutable properties of `state.py`, we coupled booleans like `is_return_in_progress` that allow the bot to remember past interactions and break the HTTP limitation of "Stateless Amnesia".

---

## 2. Chronological Development: Modification Flow, File Relationships, and Responsibilities

The solution was approached from the inside out: first cementing the Database or Knowledge Engineering ("Data"), to later build the Inferential Nervous System ("Chains"), the Operational Nodes ("Handlers"), and finishing at the Central Orchestrator ("Graph").

### PHASE 1: Data Engineering and Extraction (The Static Brain)
*   **Problem:** The original base was precarious. The bot had no precise operational guidelines (like 15-day limits, or 1.5% rates) and did not apply commercial language for Emporyum Tech App suggestions.
*   **Modified Files:** 
    *   `source/adapters/utils/knowledge_base.py` **(Extreme Refactoring)**
*   **Systemic Detail:** The 4 stakeholder interviews in `docs/stakeholder_interviews/*` (Product, Operations, Payments, Platform) were carefully evaluated. Loose narratives were translated into a hyper-structured Python super-dictionary (`SCENARIO_KNOWLEDGE_BASE`). Each dictionary key encrypts a "Domain", its *mandatory instructions*, its base cases, and crosses explicit variables that the node in turn will later seek to hydrate. 
*   **Subsequent Relationship:** This dictionary is the "Oracle" from which the Phase 3 `handlers` will dynamically feed.

### PHASE 2: Traffic Classification (The Smart Router)
*   **Problem:** To divide responsibilities, an initial gatekeeper agent was needed to decide where to travel.
*   **Created/Modified Files:**
    *   `source/adapters/chains/router_chain.py` **(Created)**
    *   `source/domain/router.py` **(Created)**
*   **Systemic Detail:**
    *   **In Chain (`router_chain.py`):** Configures a syntactic analysis (AST) schema through the `RouterResponse` model. The system passes the parametric order to the LLM using cold probabilistic inference (Temperature 0) and receives the corresponding Topic back (`selected_topic`).
    *   **In Node (`router.py`):** Transfers the execution. The initial subroutine in the tree manually checks if the local flag `state["is_return_in_progress"]` is true. If so, it **nullifies and ignores** the inferential chain (bypass), forcefully marking it to continue towards the returns agent, keeping the memory alive. If false, it continues inferring from the `router_chain` and marks where to direct the pass in `state["selected_agent"]`.
*   **Subsequent Relationship:** The string emitted and anchored here in the state will guide the logical gate `route_to_agent` elaborated in Phase 5.

### PHASE 3: Specialized Modular Layer Development (The Multi-turn Workers)
*   **Original Problem:** There was only a single pre-programmed Agent ("Amnesic" and generic).
*   **Created/Modified Files:**
    *   `source/adapters/chains/returns_chain.py` **(Created)**
    *   `source/domain/handle_returns.py` **(Created)**
    *   `source/adapters/chains/general_chain.py` **(Refactored)**
    *   `source/domain/handle_general.py` **(Refactored)**
*   **Systemic Detail:**
    *   **The Expert (`handle_returns.py` and its chain `returns_chain.py`):** This Agent was intrinsically designed as a Finite State Machine to solve "amnesia" during a multi-step interactive complaint. The *Knowledge Base* warned that payments should not be refunded instantly without asking for details. Then the Pydantic chain (`ReturnsResponse`) engages `next_step` properties and iterations of the `is_return_in_progress` flag. By cyclically modifying these flags, the bot does not release the flow and continues asking questions ("What caused the damage?") until culminating in logistics without the `Router` (Phase 2) interfering.
    *   **The General (`handle_general.py` and its chain `general_chain.py`):** Now de-saturated of the weight of Returns, it was rewritten to absorb *only* from the `SCENARIO_KNOWLEDGE_BASE` the specific directive indicated for its assigned Topic (`state["selected_topic"]`). At the `general_chain.py` level, a strict system (`GeneralResponse`) was injected forcing a reasoning native to Colombian human speech and without deviating from the *instruction_set*.
*   **Subsequent Relationship:** Both agents become the endpoint of the system. They are conditionally called by Phase 5 and introduce the final "Response" payload from which the user receives a string.

### PHASE 4: Protection and Vulnerability Mitigation Layer (The Sanitizer)
*   **Original Problem:** A user's mocked in-line data ("Their email, cellphone number, medical history, associated cards, addresses") passed indiscriminately into the massive JSON of the *System Prompt*. If someone asked about generic promotions, they still exposed tokens with sensitive private data, a severe "Data Leakage" factor in MLOps architectures.
*   **Modified Files:**
    *   `source/adapters/utils/data_filter.py` **(Refactored)**
*   **Systemic Detail:** To resolve it, the filter was reprogrammed. Now, every Node in "Phase 3", before building its prompt, communicates with this parametric utility. They temporarily dynamically extract into volatile memory a secure `dict` that retains the mandatory *base properties* but adjusts to the `relevant_fields` listed in the `knowledge_base` (`topic`). Ex: If it's profile questions, orders are removed; If it's shipping, payment balance is removed.
*   **Subsequent Relationship:** The drastic minimization cuts tokens down to 80%, accelerating graph latency without sacrificing asynchronous database validations.

### PHASE 5: Topographical Re-Construction of the Orchestrator (The Graph Wiring)
*   **Original Problem:** The system was wired in a straight line assuming a single existing agent between `fetch_data` and `END`.
*   **Modified Files:**
    *   `source/application/graph.py` **(Radically Refactored)**
*   **Systemic Detail:** 
    1. The start of the graph `fetch_user_data` was connected to the newly formulated blind initial node: `router_node`.
    2. In the remaining freed space, a **Boolean Path Gate** (`add_conditional_edges`) was introduced.
    3. The decision logic `route_to_agent` was programmed, which passively reads the mutation record written by the Node-Router Function in Phase 2 (`state.get("selected_agent")`), and raises the appropriate bridge by invoking either the dependencies of `handle_returns` or `handle_general` internally.
    4. Both Nodes now dictate a direct route to the execution terminator `END`.
*   **Final Relationship:** This closed the LangGraph ecosystem cycle. A clean architecture without tight coupling, allowing for the addition of unlimited Specialist Nodes in weeks by a large team, simply adding gates to the central router without affecting cross-generative performance.
