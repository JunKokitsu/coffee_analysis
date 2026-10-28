import argparse
from datetime import date
from pathlib import Path

from ponto_do_cafe.marts.candidate_address import CandidateAddress
from ponto_do_cafe.marts.candidate_addresses import CandidateAddresses
from ponto_do_cafe.infrastructure.competence import Competence
from ponto_do_cafe.infrastructure.data_directories import DataDirectories
from ponto_do_cafe.pipeline.pilot_pipeline import PilotPipeline
from ponto_do_cafe.pipeline.pipeline_graph import STEP_LAYERS

PILOT_DISTRICT_CODES = ("355030862", "355030837")
PILOT_CANDIDATES = CandidateAddresses(
    (
        CandidateAddress("Rua dos Pinheiros, 800 (Pinheiros)", "RUA DOS PINHEIROS", 800),
        CandidateAddress("Avenida Campanella, 1000 (Itaquera)", "AVENIDA CAMPANELLA", 1000),
    )
)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Pipeline de métricas para novas cafeterias em São Paulo")
    parser.add_argument("etapas", nargs="*", choices=list(STEP_LAYERS), help="etapas a executar, na ordem; vazio executa todas")
    parser.add_argument("--competencia", default=Competence.of(date.today()).month, help="competência no formato AAAA-MM")
    parser.add_argument("--data-referencia", type=date.fromisoformat, default=None, help="data de referência AAAA-MM-DD")
    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()
    competence = Competence(arguments.competencia)
    reference_date = arguments.data_referencia or competence.reference_date(date.today())
    directories = DataDirectories(Path(__file__).parent, competence.month)
    pipeline = PilotPipeline(directories, PILOT_CANDIDATES, PILOT_DISTRICT_CODES, reference_date)
    pipeline.run(arguments.etapas)


if __name__ == "__main__":
    main()
