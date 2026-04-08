# Graph Report - C:\Users\david\dev\forge-dashboard  (2026-04-08)

## Corpus Check
- Corpus is ~20,900 words - fits in a single context window. You may not need a graph.

## Summary
- 623 nodes · 1251 edges · 20 communities detected
- Extraction: 49% EXTRACTED · 51% INFERRED · 0% AMBIGUOUS · INFERRED: 642 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## God Nodes (most connected - your core abstractions)
1. `HealthStatus` - 75 edges
2. `ComponentEvent` - 71 edges
3. `PluginRegistry` - 58 edges
4. `RunSummary` - 43 edges
5. `StateStore` - 35 edges
6. `CrossfirePlugin` - 33 edges
7. `Artifact` - 32 edges
8. `RunDetail` - 32 edges
9. `ForgePlugin` - 32 edges
10. `MockPlugin` - 31 edges

## Surprising Connections (you probably didn't know these)
- `Operations router — trigger, cancel, retry actions on component runs.` --uses--> `PluginCallError`  [INFERRED]
  C:\Users\david\dev\forge-dashboard\backend\forge_dashboard\routers\operations.py → C:\Users\david\dev\forge-dashboard\backend\forge_dashboard\plugin_sdk\registry.py
- `Trigger a new run on a component.` --uses--> `PluginCallError`  [INFERRED]
  C:\Users\david\dev\forge-dashboard\backend\forge_dashboard\routers\operations.py → C:\Users\david\dev\forge-dashboard\backend\forge_dashboard\plugin_sdk\registry.py
- `Cancel a running component run.` --uses--> `PluginCallError`  [INFERRED]
  C:\Users\david\dev\forge-dashboard\backend\forge_dashboard\routers\operations.py → C:\Users\david\dev\forge-dashboard\backend\forge_dashboard\plugin_sdk\registry.py
- `Retry a failed component run.` --uses--> `PluginCallError`  [INFERRED]
  C:\Users\david\dev\forge-dashboard\backend\forge_dashboard\routers\operations.py → C:\Users\david\dev\forge-dashboard\backend\forge_dashboard\plugin_sdk\registry.py
- `FastAPI application factory for the Forge Dashboard backend.` --uses--> `DashboardConfig`  [INFERRED]
  C:\Users\david\dev\forge-dashboard\backend\forge_dashboard\main.py → C:\Users\david\dev\forge-dashboard\backend\forge_dashboard\config.py

## Communities

### Community 0 - "C: Users"
Cohesion: 0.03
Nodes (44): Aggregator, Aggregator — gathers health + recent runs from all registered plugins., Service that collects an overview snapshot from all registered plugins. C, Gather health + recent runs from all plugins., Exception, Crucible plugin for Forge Dashboard., HealthStatus, Lightweight summary of a single run (used for list views). (+36 more)

### Community 1 - "C: Users"
Cohesion: 0.04
Nodes (42): ApiKeyMiddleware, API key authentication middleware for Forge Dashboard., Require ``Authorization Bearer key `` for api and ws paths. If api_k, EventJournal, EventJournal — persist and query ComponentEvents in SQLite., Append-only journal backed by the event_journal table., Persist a single event., Query events with optional time and component filters. (+34 more)

### Community 2 - "C: Users"
Cohesion: 0.05
Nodes (35): EventBus, EventBus — central event dispatcher that polls plugins and dispatches events., Central event dispatcher. Periodically polls all healthy plugins for new, Iterate all healthy plugins, call poll_events(since), record to journal, dispatc, Send event to all listeners., Start the background poll loop., Run poll_once in a loop until cancelled., Cancel the background poll loop. (+27 more)

### Community 3 - "C: Users"
Cohesion: 0.09
Nodes (35): BaseModel, Shared fixtures for Forge Dashboard tests., A minimal in-memory plugin that satisfies the ForgePlugin protocol., Return a fresh MockPlugin instance., Artifact, FlowStep, PipelineFlow, Shared Pydantic v2 data models for the Forge Dashboard Plugin SDK. These mode (+27 more)

### Community 4 - "C: Users"
Cohesion: 0.05
Nodes (9): BulwarkPlugin, Tests for CruciblePlugin., Create a realistic Crucible manifest JSON on disk., TestBulwarkPlugin, TestCartographerPlugin, TestCruciblePlugin, _write_bulwark_manifest(), _write_carto_manifest() (+1 more)

### Community 5 - "C: Users"
Cohesion: 0.06
Nodes (11): get_overview(), Overview router — aggregated dashboard snapshot., Return a health + recent-runs overview for all registered components., authHeaders(), fetchArtifacts(), fetchEvents(), fetchFlows(), fetchOverview() (+3 more)

### Community 6 - "C: Users"
Cohesion: 0.08
Nodes (9): mock_plugin(), MockPlugin, _make_client(), Tests for REST routers — all CRUD endpoints with a MockPlugin injected., Create an app with a MockPlugin pre-registered and return an AsyncClient., TestComponentsRouter, TestOperationsRouter, TestOverviewRouter (+1 more)

### Community 7 - "C: Users"
Cohesion: 0.09
Nodes (4): CrossfirePlugin, Create realistic Crossfire spec and review artifact files., TestCrossfirePlugin, _write_crossfire_artifacts()

### Community 8 - "C: Users"
Cohesion: 0.11
Nodes (18): BaseSettings, DashboardConfig, DashboardConfig — centralised settings for the Forge Dashboard backend., Configuration loaded from environment variables prefixed with FORGE_DASHBOARD_., _init_app(), Tests for API key authentication middleware., CORS should reflect the cors_origins config instead of hardcoded ., Without api_key configured, all requests pass through. (+10 more)

### Community 9 - "C: Users"
Cohesion: 0.14
Nodes (2): CartographerPlugin, _stage_index()

### Community 10 - "C: Users"
Cohesion: 0.16
Nodes (1): CruciblePlugin

### Community 11 - "C: Users"
Cohesion: 0.18
Nodes (9): _init_app(), Tests for FastAPI app factory — create_app lifecycle and basic routing., Create app and manually init the store (ASGITransport skips lifespan)., App should initialise, serve api overview, and return 200., GET api components should return an empty list when no plugins are registered., CORS middleware should allow any origin., GET api events should return an empty list when no events exist., GET api pipeline flows should return an empty list when no flows exist. (+1 more)

### Community 12 - "C: Users"
Cohesion: 0.14
Nodes (13): get_artifacts(), get_config(), get_run(), list_components(), list_runs(), Components router — per-component runs, artifacts, and config., List all registered component plugins with their health status., List runs for a given component with optional pagination and status filter. (+5 more)

### Community 13 - "C: Users"
Cohesion: 0.25
Nodes (7): cancel(), Operations router — trigger, cancel, retry actions on component runs., Trigger a new run on a component., Cancel a running component run., Retry a failed component run., retry(), trigger()

### Community 14 - "C: Users"
Cohesion: 0.25
Nodes (7): get_events(), get_flow(), list_flows(), Pipeline router — cross-component flows and event journal queries., List pipeline flows, ordered by creation time descending., Get a specific pipeline flow with all its steps., Query the event journal with optional time, component, and limit filters.

### Community 15 - "C: Users"
Cohesion: 0.54
Nodes (3): _event(), _make_store(), TestEventJournal

### Community 16 - "Community 16"
Cohesion: 1.0
Nodes (0): 

### Community 17 - "C: Users"
Cohesion: 1.0
Nodes (1): Return the active database connection (raises if not initialised).

### Community 18 - "Community 18"
Cohesion: 1.0
Nodes (0): 

### Community 19 - "Community 19"
Cohesion: 1.0
Nodes (0): 

## Knowledge Gaps
- **40 isolated node(s):** `API key authentication middleware for Forge Dashboard.`, `Require ``Authorization Bearer key `` for api and ws paths. If api_k`, `DashboardConfig — centralised settings for the Forge Dashboard backend.`, `Configuration loaded from environment variables prefixed with FORGE_DASHBOARD_.`, `SQLite-backed state store for the Forge Dashboard platform layer. Provides pe` (+35 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 16`** (2 nodes): `useApi.test.ts`, `importApi()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `C: Users`** (1 nodes): `Return the active database connection (raises if not initialised).`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 18`** (1 nodes): `test-setup.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 19`** (1 nodes): `vite.config.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ComponentEvent` connect `C: Users` to `C: Users`, `C: Users`, `C: Users`, `C: Users`, `C: Users`, `C: Users`, `C: Users`, `C: Users`, `C: Users`?**
  _High betweenness centrality (0.234) - this node is a cross-community bridge._
- **Why does `HealthStatus` connect `C: Users` to `C: Users`, `C: Users`, `C: Users`, `C: Users`, `C: Users`, `C: Users`, `C: Users`?**
  _High betweenness centrality (0.177) - this node is a cross-community bridge._
- **Why does `PluginRegistry` connect `C: Users` to `C: Users`, `C: Users`?**
  _High betweenness centrality (0.131) - this node is a cross-community bridge._
- **Are the 72 inferred relationships involving `HealthStatus` (e.g. with `ForgePlugin` and `ForgePlugin Protocol — the contract every component plugin must satisfy.`) actually correct?**
  _`HealthStatus` has 72 INFERRED edges - model-reasoned connections that need verification._
- **Are the 68 inferred relationships involving `ComponentEvent` (e.g. with `EventJournal` and `EventJournal — persist and query ComponentEvents in SQLite.`) actually correct?**
  _`ComponentEvent` has 68 INFERRED edges - model-reasoned connections that need verification._
- **Are the 46 inferred relationships involving `PluginRegistry` (e.g. with `FastAPI application factory for the Forge Dashboard backend.` and `Map DashboardConfig paths to per-plugin constructor kwargs.`) actually correct?**
  _`PluginRegistry` has 46 INFERRED edges - model-reasoned connections that need verification._
- **Are the 39 inferred relationships involving `RunSummary` (e.g. with `ForgePlugin` and `ForgePlugin Protocol — the contract every component plugin must satisfy.`) actually correct?**
  _`RunSummary` has 39 INFERRED edges - model-reasoned connections that need verification._