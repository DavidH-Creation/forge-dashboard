---
source_file: "C:\Users\david\dev\forge-dashboard\backend\forge_dashboard\platform\state_store.py"
type: "code"
community: "C: Users"
location: "L77"
tags:
  - graphify/code
  - graphify/INFERRED
  - community/C:_Users
---

# StateStore

## Connections
- [[.__init__()_4]] - `method` [EXTRACTED]
- [[.close()]] - `method` [EXTRACTED]
- [[.list_tables()]] - `method` [EXTRACTED]
- [[Append-only journal backed by the event_journal table.]] - `uses` [INFERRED]
- [[Append-only log of operations performed via the dashboard.]] - `uses` [INFERRED]
- [[Async SQLite state store for the platform layer.]] - `rationale_for` [EXTRACTED]
- [[Build and return a fully-wired FastAPI application. Parameters -----]] - `uses` [INFERRED]
- [[Create a new pipeline flow with the given component steps. Returns th]] - `uses` [INFERRED]
- [[Create and track cross-component pipeline flows.]] - `uses` [INFERRED]
- [[EventJournal]] - `uses` [INFERRED]
- [[EventJournal — persist and query ComponentEvents in SQLite.]] - `uses` [INFERRED]
- [[FastAPI application factory for the Forge Dashboard backend.]] - `uses` [INFERRED]
- [[FlowTracker]] - `uses` [INFERRED]
- [[FlowTracker — manage multi-component pipeline flows in SQLite.]] - `uses` [INFERRED]
- [[Get a flow with all its steps.]] - `uses` [INFERRED]
- [[List flows (without steps) ordered by creation time descending.]] - `uses` [INFERRED]
- [[Map DashboardConfig paths to per-plugin constructor kwargs.]] - `uses` [INFERRED]
- [[Mark a step and its flow as failed.]] - `uses` [INFERRED]
- [[Mark a step as completed. If all steps are done, complete the flow.]] - `uses` [INFERRED]
- [[Mark a step as running and set the flow status to running.]] - `uses` [INFERRED]
- [[OperationLog]] - `uses` [INFERRED]
- [[OperationLog — record and query dashboard operations in SQLite.]] - `uses` [INFERRED]
- [[Persist a single event.]] - `uses` [INFERRED]
- [[Query events with optional time and component filters.]] - `uses` [INFERRED]
- [[Query events, truncating to max_replay_events most recent if exceeded.]] - `uses` [INFERRED]
- [[Return the most recent operations, newest first.]] - `uses` [INFERRED]
- [[TestEventJournal]] - `uses` [INFERRED]
- [[TestFlowTracker]] - `uses` [INFERRED]
- [[TestOperationLog]] - `uses` [INFERRED]
- [[TestStateStore]] - `uses` [INFERRED]
- [[Tests for the EventJournal — persist and query events.]] - `uses` [INFERRED]
- [[Tests for the FlowTracker.]] - `uses` [INFERRED]
- [[Tests for the OperationLog.]] - `uses` [INFERRED]
- [[Tests for the SQLite StateStore — schema initialisation.]] - `uses` [INFERRED]
- [[state_store.py]] - `contains` [EXTRACTED]

#graphify/code #graphify/INFERRED #community/C:_Users