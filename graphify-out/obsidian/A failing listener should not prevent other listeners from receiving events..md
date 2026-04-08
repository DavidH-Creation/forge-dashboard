---
source_file: "C:\Users\david\dev\forge-dashboard\backend\tests\test_event_bus.py"
type: "rationale"
community: "C: Users"
location: "L170"
tags:
  - graphify/rationale
  - graphify/INFERRED
  - community/C:_Users
---

# A failing listener should not prevent other listeners from receiving events.

## Connections
- [[.test_dispatch_handles_listener_errors()]] - `rationale_for` [EXTRACTED]
- [[ComponentEvent]] - `uses` [INFERRED]
- [[EventBus]] - `uses` [INFERRED]
- [[HealthStatus]] - `uses` [INFERRED]
- [[PluginRegistry]] - `uses` [INFERRED]

#graphify/rationale #graphify/INFERRED #community/C:_Users