FROM apache/airflow:3.3.2-python3.14

USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends 7zip \
    && rm -rf /var/lib/apt/lists/*

USER airflow
RUN pip install --no-cache-dir uv \
    && mkdir -p /home/airflow/.venvs /home/airflow/.pythons /home/airflow/.cache/uv \
    && chmod -R g+rwX /home/airflow/.venvs /home/airflow/.pythons /home/airflow/.cache
ENV UV_PROJECT_ENVIRONMENT=/home/airflow/.venvs/coffee_analysis \
    UV_PYTHON_INSTALL_DIR=/home/airflow/.pythons \
    UV_LINK_MODE=copy
