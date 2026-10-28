from datetime import date
from pathlib import Path

from ponto_do_cafe.infrastructure.data_directories import DataDirectories
from ponto_do_cafe.marts.candidate_addresses import CandidateAddresses
from ponto_do_cafe.pipeline.pilot_pipeline import PilotPipeline
from ponto_do_cafe.pipeline.pipeline_graph import STEP_LAYERS


def test_registered_steps_match_step_layers(tmp_path: Path) -> None:
    directories = DataDirectories(tmp_path, "2026-09")
    pipeline = PilotPipeline(directories, CandidateAddresses(()), (), date(2026, 9, 20))
    assert set(pipeline.step_names()) == set(STEP_LAYERS)
