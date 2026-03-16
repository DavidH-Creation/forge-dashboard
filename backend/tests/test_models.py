import pytest
from forge_dashboard.plugin_sdk.models import (
    RunSummary, RunDetail, StageRecord, StageDefinition,
    ComponentEvent, Artifact, HealthStatus, PipelineFlow, FlowStep,
)


class TestStageDefinition:
    def test_create(self):
        sd = StageDefinition(name="EXECUTE", order=3, description="Execute the plan")
        assert sd.name == "EXECUTE"
        assert sd.order == 3
        assert sd.description == "Execute the plan"

    def test_default_description(self):
        sd = StageDefinition(name="VALIDATE", order=0)
        assert sd.description == ""


class TestStageRecord:
    def test_create_minimal(self):
        sr = StageRecord(name="EXECUTE", status="running")
        assert sr.name == "EXECUTE"
        assert sr.status == "running"
        assert sr.started_at == ""
        assert sr.finished_at == ""
        assert sr.duration_seconds is None
        assert sr.input_refs == []
        assert sr.output_refs == []

    def test_create_full(self):
        sr = StageRecord(
            name="EXECUTE", status="completed",
            started_at="2026-03-16T10:00:00Z",
            finished_at="2026-03-16T10:05:00Z",
            duration_seconds=300.0,
            input_refs=["task.yaml"],
            output_refs=["result.json"],
        )
        assert sr.duration_seconds == 300.0
        assert sr.input_refs == ["task.yaml"]
        assert sr.output_refs == ["result.json"]


class TestArtifact:
    def test_create(self):
        a = Artifact(name="output.json", artifact_type="json", content_or_path="/tmp/output.json")
        assert a.name == "output.json"
        assert a.artifact_type == "json"
        assert a.size is None

    def test_with_size(self):
        a = Artifact(name="report.md", artifact_type="markdown",
                     content_or_path="# Report", size=1024)
        assert a.size == 1024


class TestRunSummary:
    def test_create_minimal(self):
        rs = RunSummary(component="bulwark", run_id="run-1",
                        status="running", current_stage="EXECUTE", progress=0.5)
        assert rs.component == "bulwark"
        assert rs.progress == 0.5

    def test_progress_clamped(self):
        with pytest.raises(Exception):
            # progress > 1.0 should be rejected by ge/le validators
            RunSummary(component="bulwark", run_id="run-1",
                       status="running", current_stage="EXECUTE", progress=1.5)

    def test_progress_lower_bound(self):
        with pytest.raises(Exception):
            RunSummary(component="bulwark", run_id="run-1",
                       status="running", current_stage="EXECUTE", progress=-0.1)

    def test_defaults(self):
        rs = RunSummary(component="bulwark", run_id="run-1", status="pending")
        assert rs.current_stage == ""
        assert rs.progress == 0.0
        assert rs.started_at == ""
        assert rs.finished_at == ""


class TestRunDetail:
    def test_inherits_run_summary(self):
        rd = RunDetail(component="bulwark", run_id="run-1", status="completed",
                       current_stage="COMPLETE", progress=1.0)
        assert isinstance(rd, RunSummary)
        assert rd.stages == []
        assert rd.artifacts == []
        assert rd.metadata == {}
        assert rd.error is None

    def test_with_stages_and_artifacts(self):
        rd = RunDetail(
            component="cartographer", run_id="run-2", status="running",
            current_stage="DISCOVER", progress=0.3,
            stages=[StageRecord(name="INTAKE", status="completed")],
            artifacts=[Artifact(name="spec.yaml", artifact_type="yaml",
                                content_or_path="/tmp/spec.yaml")],
            metadata={"goal": "build feature"},
            error=None,
        )
        assert len(rd.stages) == 1
        assert len(rd.artifacts) == 1
        assert rd.metadata["goal"] == "build feature"


class TestComponentEvent:
    def test_retroactive_default_false(self):
        e = ComponentEvent(component="bulwark", event_type="phase_completed",
                           run_id="run-1", timestamp="2026-03-16T10:00:00Z", data={})
        assert e.is_retroactive is False

    def test_retroactive_can_be_true(self):
        e = ComponentEvent(component="bulwark", event_type="phase_completed",
                           run_id="run-1", timestamp="2026-03-16T10:00:00Z",
                           data={"phase": "EXECUTE"}, is_retroactive=True)
        assert e.is_retroactive is True
        assert e.data["phase"] == "EXECUTE"


class TestHealthStatus:
    def test_valid_statuses(self):
        for s in ("healthy", "degraded", "down"):
            h = HealthStatus(component="test", status=s, version="1.0")
            assert h.status == s

    def test_default_details(self):
        h = HealthStatus(component="test", status="healthy")
        assert h.version == ""
        assert h.details == {}


class TestFlowStep:
    def test_create_minimal(self):
        fs = FlowStep(component="crucible", step_order=0)
        assert fs.run_id is None
        assert fs.status == "pending"
        assert fs.started_at is None
        assert fs.finished_at is None

    def test_create_full(self):
        fs = FlowStep(component="cartographer", run_id="run-5", step_order=1,
                       status="running", started_at="2026-03-16T10:00:00Z")
        assert fs.run_id == "run-5"
        assert fs.status == "running"


class TestPipelineFlow:
    def test_create_with_steps(self):
        flow = PipelineFlow(
            flow_id="flow-1", name="test", status="running",
            created_at="2026-03-16T10:00:00Z",
            steps=[
                FlowStep(component="crucible", step_order=0, status="completed"),
                FlowStep(component="cartographer", step_order=1, status="running"),
            ],
        )
        assert len(flow.steps) == 2
        assert flow.finished_at is None

    def test_create_minimal(self):
        flow = PipelineFlow(flow_id="flow-2", name="deploy", status="pending",
                            created_at="2026-03-16T10:00:00Z")
        assert flow.steps == []
        assert flow.finished_at is None
