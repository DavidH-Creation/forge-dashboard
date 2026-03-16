"""Shared Pydantic v2 data models for the Forge Dashboard Plugin SDK.

These models define the contract between forge-dashboard and all component
plugins (Bulwark, Cartographer, Crucible, Crossfire, etc.).
"""

from __future__ import annotations

from pydantic import BaseModel, Field


# ── Stage ────────────────────────────────────────────────────────────────────

class StageDefinition(BaseModel):
    """Declarative definition of a single pipeline stage."""

    name: str
    order: int
    description: str = ""


class StageRecord(BaseModel):
    """Runtime record for a stage within a run."""

    name: str
    status: str
    started_at: str = ""
    finished_at: str = ""
    duration_seconds: float | None = None
    input_refs: list[str] = Field(default_factory=list)
    output_refs: list[str] = Field(default_factory=list)


# ── Artifact ─────────────────────────────────────────────────────────────────

class Artifact(BaseModel):
    """A build/run artifact produced by a component."""

    name: str
    artifact_type: str
    content_or_path: str
    size: int | None = None


# ── Run ──────────────────────────────────────────────────────────────────────

class RunSummary(BaseModel):
    """Lightweight summary of a single run (used for list views)."""

    component: str
    run_id: str
    status: str
    current_stage: str = ""
    progress: float = Field(default=0.0, ge=0.0, le=1.0)
    started_at: str = ""
    finished_at: str = ""


class RunDetail(RunSummary):
    """Full detail for a single run (used for detail views)."""

    stages: list[StageRecord] = Field(default_factory=list)
    artifacts: list[Artifact] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
    error: str | None = None


# ── Events ───────────────────────────────────────────────────────────────────

class ComponentEvent(BaseModel):
    """An event emitted by (or on behalf of) a component."""

    component: str
    event_type: str
    run_id: str
    timestamp: str
    data: dict = Field(default_factory=dict)
    is_retroactive: bool = False


# ── Health ───────────────────────────────────────────────────────────────────

class HealthStatus(BaseModel):
    """Health-check response from a component plugin."""

    component: str
    status: str
    version: str = ""
    details: dict = Field(default_factory=dict)


# ── Pipeline / Flow ─────────────────────────────────────────────────────────

class FlowStep(BaseModel):
    """One step in a cross-component pipeline flow."""

    component: str
    run_id: str | None = None
    step_order: int
    status: str = "pending"
    started_at: str | None = None
    finished_at: str | None = None


class PipelineFlow(BaseModel):
    """A multi-component pipeline flow (e.g. Cartographer -> Bulwark)."""

    flow_id: str
    name: str
    status: str
    created_at: str
    finished_at: str | None = None
    steps: list[FlowStep] = Field(default_factory=list)
