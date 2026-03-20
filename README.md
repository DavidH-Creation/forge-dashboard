# Forge Dashboard

Unified management console for the [Forge Platform](https://github.com/DavidH-Creation/forge-platform) ecosystem. Real-time monitoring of Bulwark executions, Cartographer planning sessions, Crossfire reviews, and Crucible research pipelines.

[![CI](https://github.com/DavidH-Creation/forge-dashboard/actions/workflows/ci.yml/badge.svg)](https://github.com/DavidH-Creation/forge-dashboard/actions/workflows/ci.yml)

## Architecture

| Layer | Tech | Description |
|-------|------|-------------|
| Frontend | React 19 + TypeScript + Zustand + Vite | SPA with real-time WebSocket updates |
| Backend | FastAPI + Pydantic v2 + aiosqlite | REST API + WebSocket endpoint |
| Plugins | Plugin SDK | Modular adapters for each Forge component |

## Features

- **Plugin SDK**: Protocol-based plugin system with `ForgePlugin` interface
- **Four built-in plugins**: Bulwark, Cartographer, Crossfire, Crucible
- **Real-time updates**: WebSocket-powered live status and event streaming
- **EventBus + Aggregator**: Centralized event processing and metric aggregation
- **Platform State Store**: EventJournal, OperationLog, FlowTracker for full audit trail
- **Dynamic pipeline visualization**: Interactive flow diagram of the Forge pipeline
- **Health monitoring**: Component health cards with status indicators

## Pages

| Page | Description |
|------|-------------|
| Overview | Platform-wide stats, health cards, recent activity |
| PipelineFlow | Interactive visualization of the Crucible → Cartographer → Bulwark pipeline |
| ComponentDetail | Deep-dive into a specific component's runs and metrics |
| RunDetail | Detailed view of a single execution run with stage progress |

## Setup

### Backend

```bash
cd backend
pip install -e ".[dev]"
uvicorn forge_dashboard.app:create_app --factory --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Plugins

Each plugin is a separate package in `plugins/`:

```
plugins/
├── forge-dashboard-bulwark/
├── forge-dashboard-cartographer/
├── forge-dashboard-crossfire/
└── forge-dashboard-crucible/
```

Install a plugin:

```bash
cd plugins/forge-dashboard-bulwark
pip install -e .
```

## Testing

```bash
# Backend tests
cd backend && pytest tests/ -v

# Frontend tests
cd frontend && npm run test

# Lint
cd backend && ruff check forge_dashboard/
cd frontend && npm run lint
```

## License

MIT
