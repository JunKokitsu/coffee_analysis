from datetime import datetime, timedelta

from airflow.providers.standard.operators.bash import BashOperator
from airflow.sdk import DAG, Param

from coffee_analysis.pipeline_graph import DOWNLOAD_SOURCES, STEP_LAYERS, step_dependencies

PROJECT_DIRECTORY = "/opt/coffee_analysis"
COMPETENCE_TEMPLATE = "{{ params.competencia or (dag_run.logical_date or dag_run.run_after).strftime('%Y-%m') }}"
DOWNLOAD_RETRIES = 3


def download_task(source: str) -> BashOperator:
    return BashOperator(
        task_id=f"baixar_{source}",
        bash_command=f"COMPETENCIA={COMPETENCE_TEMPLATE} {PROJECT_DIRECTORY}/scripts/baixar_fontes.sh {source}",
        retries=DOWNLOAD_RETRIES,
        retry_delay=timedelta(minutes=30),
    )


def pipeline_task(step: str) -> BashOperator:
    return BashOperator(
        task_id=step,
        bash_command=f"cd {PROJECT_DIRECTORY} && env -u VIRTUAL_ENV uv run --frozen python main.py {step} --competencia {COMPETENCE_TEMPLATE}",
        pool="coffee_analysis",
    )


with DAG(
    dag_id="atualizacao_mensal_cafeterias",
    description="Baixa as fontes públicas, atualiza staging e marts, valida a qualidade e gera o relatório das cafeterias de SP",
    schedule="0 6 20 * *",
    start_date=datetime(2026, 9, 1),
    catchup=False,
    max_active_runs=1,
    params={"competencia": Param("", type="string", description="Competência AAAA-MM; vazio usa o mês da execução")},
    tags=["coffee_analysis"],
) as dag:
    downloads = {source: download_task(source) for source in sorted(set(DOWNLOAD_SOURCES.values()))}
    steps = {step: pipeline_task(step) for step in STEP_LAYERS}
    for step, task in steps.items():
        upstream_steps = [steps[dependency] for dependency in step_dependencies(step)]
        upstream_downloads = [downloads[DOWNLOAD_SOURCES[step]]] if step in DOWNLOAD_SOURCES else []
        task.set_upstream([*upstream_steps, *upstream_downloads])
