---
source_file: "C:\Users\david\dev\forge-dashboard\backend\forge_dashboard\services\event_bus.py"
type: "code"
community: "C: Users"
location: "L19"
tags:
  - graphify/code
  - graphify/INFERRED
  - community/C:_Users
---

# EventBus

## Connections
- [[.__init__()_9]] - `method` [EXTRACTED]
- [[._dispatch()]] - `method` [EXTRACTED]
- [[._poll_loop()]] - `method` [EXTRACTED]
- [[.add_listener()]] - `method` [EXTRACTED]
- [[.poll_once()]] - `method` [EXTRACTED]
- [[.remove_listener()]] - `method` [EXTRACTED]
- [[.start()]] - `method` [EXTRACTED]
- [[.stop()]] - `method` [EXTRACTED]
- [[A failing listener should not prevent other listeners from receiving events.]] - `uses` [INFERRED]
- [[Build and return a fully-wired FastAPI application. Parameters -----]] - `uses` [INFERRED]
- [[Central event dispatcher. Periodically polls all healthy plugins for new]] - `rationale_for` [EXTRACTED]
- [[ComponentEvent]] - `uses` [INFERRED]
- [[EventJournal]] - `uses` [INFERRED]
- [[FakePollPlugin]] - `uses` [INFERRED]
- [[FastAPI application factory for the Forge Dashboard backend.]] - `uses` [INFERRED]
- [[Listeners can be added and removed.]] - `uses` [INFERRED]
- [[Map DashboardConfig paths to per-plugin constructor kwargs.]] - `uses` [INFERRED]
- [[Minimal plugin that yields pre-loaded events from poll_events.]] - `uses` [INFERRED]
- [[PluginRegistry]] - `uses` [INFERRED]
- [[TestEventBus]] - `uses` [INFERRED]
- [[Tests for EventBus — central event dispatcher.]] - `uses` [INFERRED]
- [[event_bus.py]] - `contains` [EXTRACTED]
- [[poll_once should collect events from healthy plugins, record them, and dispatch.]] - `uses` [INFERRED]
- [[poll_once should dispatch all events from a plugin.]] - `uses` [INFERRED]
- [[poll_once should not call poll_events on degraded plugins.]] - `uses` [INFERRED]
- [[poll_once should poll events from all healthy plugins.]] - `uses` [INFERRED]
- [[poll_once should update _last_poll_time after each poll.]] - `uses` [INFERRED]
- [[start() should create a background task, stop() should cancel it.]] - `uses` [INFERRED]

#graphify/code #graphify/INFERRED #community/C:_Users