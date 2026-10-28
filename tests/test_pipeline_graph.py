from ponto_do_cafe.pipeline.pipeline_graph import (
    DOWNLOAD_LAYER,
    MART_DEPENDENCIES,
    STAGING_DOWNLOADS,
    STAGING_LAYER,
    STEP_LAYERS,
    step_dependencies,
)


def test_every_dependency_is_a_known_step() -> None:
    dependencies = {dependency for step in STEP_LAYERS for dependency in step_dependencies(step)}
    assert dependencies <= set(STEP_LAYERS)
    assert set(MART_DEPENDENCIES) <= set(STEP_LAYERS)


def test_steps_are_listed_after_their_dependencies() -> None:
    positions = {step: position for position, step in enumerate(STEP_LAYERS)}
    late_dependencies = [(step, dependency) for step in STEP_LAYERS for dependency in step_dependencies(step) if positions[dependency] > positions[step]]
    assert late_dependencies == []


def test_staging_downloads_only_point_to_download_steps() -> None:
    assert all(STEP_LAYERS[download_step] == DOWNLOAD_LAYER for download_step in STAGING_DOWNLOADS.values())


def test_staging_downloads_only_map_staging_steps() -> None:
    assert all(STEP_LAYERS[step] == STAGING_LAYER for step in STAGING_DOWNLOADS)


def test_staging_steps_with_download_depend_on_it() -> None:
    for step, download_step in STAGING_DOWNLOADS.items():
        assert step_dependencies(step) == (download_step,)


def test_download_steps_have_no_dependencies() -> None:
    download_steps = [step for step, layer in STEP_LAYERS.items() if layer == DOWNLOAD_LAYER]
    assert all(step_dependencies(download_step) == () for download_step in download_steps)


def test_quality_waits_for_every_staging_step() -> None:
    staging = {step for step, layer in STEP_LAYERS.items() if layer == STAGING_LAYER}
    assert set(step_dependencies("qualidade")) == staging


def test_marts_never_skip_quality() -> None:
    marts_without_upstream = [step for step, layer in STEP_LAYERS.items() if layer == "marts" and not step_dependencies(step)]
    assert marts_without_upstream == []
