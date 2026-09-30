from coffee_analysis.pipeline.pipeline_graph import DOWNLOAD_SOURCES, MART_DEPENDENCIES, STEP_LAYERS, STAGING_LAYER, step_dependencies


def test_every_dependency_is_a_known_step() -> None:
    dependencies = {dependency for step in STEP_LAYERS for dependency in step_dependencies(step)}
    assert dependencies <= set(STEP_LAYERS)
    assert set(MART_DEPENDENCIES) <= set(STEP_LAYERS)


def test_steps_are_listed_after_their_dependencies() -> None:
    positions = {step: position for position, step in enumerate(STEP_LAYERS)}
    late_dependencies = [(step, dependency) for step in STEP_LAYERS for dependency in step_dependencies(step) if positions[dependency] > positions[step]]
    assert late_dependencies == []


def test_downloads_only_feed_staging_steps() -> None:
    assert all(STEP_LAYERS[step] == STAGING_LAYER for step in DOWNLOAD_SOURCES)


def test_quality_waits_for_every_staging_step() -> None:
    staging = {step for step, layer in STEP_LAYERS.items() if layer == STAGING_LAYER}
    assert set(step_dependencies("qualidade")) == staging


def test_marts_never_skip_quality() -> None:
    marts_without_upstream = [step for step, layer in STEP_LAYERS.items() if layer == "marts" and not step_dependencies(step)]
    assert marts_without_upstream == []
