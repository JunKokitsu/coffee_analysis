from datetime import datetime, timedelta

from airflow.providers.standard.operators.bash import BashOperator
from airflow.sdk import DAG, Param

from ponto_do_cafe.pipeline.pipeline_graph import DOWNLOAD_LAYER, STEP_LAYERS, step_dependencies

PROJECT_DIRECTORY = "/opt/ponto_do_cafe"
COMPETENCE_TEMPLATE = "{{ params.competencia or (dag_run.logical_date or dag_run.run_after).strftime('%Y-%m') }}"
DOWNLOAD_RETRIES = 3
DOWNLOAD_RETRY_DELAY = timedelta(minutes=30)


def download_retry_arguments() -> dict[str, int | timedelta]:
    return {"retries": DOWNLOAD_RETRIES, "retry_delay": DOWNLOAD_RETRY_DELAY}


def retry_arguments(step: str) -> dict[str, int | timedelta]:
    if STEP_LAYERS[step] == DOWNLOAD_LAYER:
        return download_retry_arguments()
    return {}


def pipeline_task(step: str) -> BashOperator:
    return BashOperator(
        task_id=step,
        bash_command=f"cd {PROJECT_DIRECTORY} && env -u VIRTUAL_ENV uv run --frozen python main.py {step} --competencia {COMPETENCE_TEMPLATE}",
        pool="ponto_do_cafe",
        **retry_arguments(step),
    )


with DAG(
    dag_id="atualizacao_mensal_cafeterias",
    description="Baixa as fontes públicas, atualiza staging e marts, valida a qualidade e gera o relatório das cafeterias de SP",
    schedule="0 6 20 * *",
    start_date=datetime(2026, 9, 1),
    catchup=False,
    max_active_runs=1,
    params={"competencia": Param("", type="string", description="Competência AAAA-MM; vazio usa o mês da execução")},
    tags=["ponto_do_cafe"],
) as dag:
    steps = {step: pipeline_task(step) for step in STEP_LAYERS}
    for step, task in steps.items():
        upstream_steps = [steps[dependency] for dependency in step_dependencies(step)]
        task.set_upstream(upstream_steps)
