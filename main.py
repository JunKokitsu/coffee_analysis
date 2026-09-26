import sys
from datetime import date
from pathlib import Path

from coffee_analysis.candidate_address import CandidateAddress
from coffee_analysis.candidate_addresses import CandidateAddresses
from coffee_analysis.data_directories import DataDirectories
from coffee_analysis.pilot_pipeline import PilotPipeline

REFERENCE_DATE = date(2026, 9, 23)
PILOT_DISTRICT_CODES = ("355030862", "355030837")
PILOT_CANDIDATES = CandidateAddresses(
    (
        CandidateAddress("Rua dos Pinheiros, 800 (Pinheiros)", "RUA DOS PINHEIROS", 800),
        CandidateAddress("Avenida Campanella, 1000 (Itaquera)", "AVENIDA CAMPANELLA", 1000),
    )
)


def main() -> None:
    directories = DataDirectories(Path(__file__).parent)
    pipeline = PilotPipeline(directories, PILOT_CANDIDATES, PILOT_DISTRICT_CODES, REFERENCE_DATE)
    pipeline.run(sys.argv[1:])


if __name__ == "__main__":
    main()
