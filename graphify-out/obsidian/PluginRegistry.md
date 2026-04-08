---
source_file: "C:\Users\david\dev\forge-dashboard\backend\forge_dashboard\plugin_sdk\registry.py"
type: "code"
community: "C: Users"
location: "L38"
tags:
  - graphify/code
  - graphify/INFERRED
  - community/C:_Users
---

# PluginRegistry

## Connections
- [[.__init__()_7]] - `method` [EXTRACTED]
- [[._mark_degraded()]] - `method` [EXTRACTED]
- [[._mark_healthy()]] - `method` [EXTRACTED]
- [[.check_health()]] - `method` [EXTRACTED]
- [[.discover_plugins()]] - `method` [EXTRACTED]
- [[.get()]] - `method` [EXTRACTED]
- [[.get_status()]] - `method` [EXTRACTED]
- [[.list_plugins()]] - `method` [EXTRACTED]
- [[.register()]] - `method` [EXTRACTED]
- [[.safe_call()]] - `method` [EXTRACTED]
- [[A failing listener should not prevent other listeners from receiving events.]] - `uses` [INFERRED]
- [[Aggregator]] - `uses` [INFERRED]
- [[Aggregator — gathers health + recent runs from all registered plugins.]] - `uses` [INFERRED]
- [[Build and return a fully-wired FastAPI application. Parameters -----]] - `uses` [INFERRED]
- [[Cancel the background poll loop.]] - `uses` [INFERRED]
- [[Central event dispatcher. Periodically polls all healthy plugins for new]] - `uses` [INFERRED]
- [[Central registry for Forge component plugins. Provides - Registrati]] - `rationale_for` [EXTRACTED]
- [[Crucible plugin for Forge Dashboard.]] - `uses` [INFERRED]
- [[EventBus]] - `uses` [INFERRED]
- [[EventBus — central event dispatcher that polls plugins and dispatches events.]] - `uses` [INFERRED]
- [[FakeOverviewPlugin]] - `uses` [INFERRED]
- [[FakePlugin]] - `uses` [INFERRED]
- [[FakePollPlugin]] - `uses` [INFERRED]
- [[FastAPI application factory for the Forge Dashboard backend.]] - `uses` [INFERRED]
- [[Gather health + recent runs from all plugins.]] - `uses` [INFERRED]
- [[HealthStatus]] - `uses` [INFERRED]
- [[Iterate all healthy plugins, call poll_events(since), record to journal, dispatc]] - `uses` [INFERRED]
- [[Listeners can be added and removed.]] - `uses` [INFERRED]
- [[Map DashboardConfig paths to per-plugin constructor kwargs.]] - `uses` [INFERRED]
- [[Minimal plugin that yields pre-loaded events from poll_events.]] - `uses` [INFERRED]
- [[Plugin that provides health and list_runs for aggregator tests.]] - `uses` [INFERRED]
- [[Register a callback to receive dispatched events.]] - `uses` [INFERRED]
- [[Run poll_once in a loop until cancelled.]] - `uses` [INFERRED]
- [[Send event to all listeners.]] - `uses` [INFERRED]
- [[Service that collects an overview snapshot from all registered plugins. C]] - `uses` [INFERRED]
- [[Start the background poll loop.]] - `uses` [INFERRED]
- [[Test that FakePlugin satisfies the ForgePlugin protocol.]] - `uses` [INFERRED]
- [[TestAggregator]] - `uses` [INFERRED]
- [[TestEventBus]] - `uses` [INFERRED]
- [[TestForgePluginProtocol]] - `uses` [INFERRED]
- [[TestPluginCallError]] - `uses` [INFERRED]
- [[TestPluginRegistry]] - `uses` [INFERRED]
- [[Tests for Aggregator — overview service that collects health + runs from all plu]] - `uses` [INFERRED]
- [[Tests for EventBus — central event dispatcher.]] - `uses` [INFERRED]
- [[Unregister a previously registered callback.]] - `uses` [INFERRED]
- [[get_overview should aggregate data from all registered plugins.]] - `uses` [INFERRED]
- [[get_overview should handle plugins whose health() raises.]] - `uses` [INFERRED]
- [[get_overview should handle plugins whose list_runs() raises.]] - `uses` [INFERRED]
- [[get_overview should include the registry status for each plugin.]] - `uses` [INFERRED]
- [[get_overview should return health and recent runs for all plugins.]] - `uses` [INFERRED]
- [[get_overview with no plugins returns empty components list.]] - `uses` [INFERRED]
- [[poll_once should collect events from healthy plugins, record them, and dispatch.]] - `uses` [INFERRED]
- [[poll_once should dispatch all events from a plugin.]] - `uses` [INFERRED]
- [[poll_once should not call poll_events on degraded plugins.]] - `uses` [INFERRED]
- [[poll_once should poll events from all healthy plugins.]] - `uses` [INFERRED]
- [[poll_once should update _last_poll_time after each poll.]] - `uses` [INFERRED]
- [[registry.py]] - `contains` [EXTRACTED]
- [[start() should create a background task, stop() should cancel it.]] - `uses` [INFERRED]

#graphify/code #graphify/INFERRED #community/C:_Users