# Module: Application

This directory contains the topological definition and state management of the application based on LangGraph. It is designed to orchestrate the execution of specialist customer service agents.

## Development Files

### `graph.py`
- **Description:** Contains the topological definition (the "Graph") of LangGraph.
- **Functionality:** Configures the main flow and its conditional branches. It adds the early routing node (`router_node`) which, based on the evaluation of the user's intent, dynamically transfers control towards the specialist operational nodes (like `handle_general` or `handle_returns`).

### `state.py`
- **Description:** Defines the data structure that is transferred between the Nodes (TypedDict).
- **Functionality:** It is actively used throughout the graph to transport `user_data`, `question`, or web history. Specifically, this project leverages variables such as `current_step` and `is_return_in_progress` to provide multi-turn memory to the returns flow, and safeguards the classification given by the initial LLM (`selected_topic`).
