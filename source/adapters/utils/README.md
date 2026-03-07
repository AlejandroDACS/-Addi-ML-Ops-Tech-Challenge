# Module: Adapters / Utils

This directory maintains miscellaneous classes and constant in-house layers, abstract cleaners, or pre-built objects shared locally by the LLM chains or Nodes.

## Development Files

### `knowledge_base.py`
- **Description:** Hardcoded contextual database of the system (Main Dictionary).
- **System Role:** Groups all the business infrastructure that the chat must know. Instead of blindly embedding directives, it exposes fields for catalog recommendations, returns, or bank quotas within a strict framework that iterative agents punctually absorb to shape authorized responses.

### `data_filter.py`
- **Description:** Strict perimeter JSON filter.
- **System Role:** Requires cross-referencing fields pre-identified by rules (e.g., excluding the credit card from transactions involving warranty queries). It allows the orchestrator to safely maintain its wrapper and aggressively minimizes token usage.
