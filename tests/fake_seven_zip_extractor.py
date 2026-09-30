from pathlib import Path

from coffee_analysis.infrastructure.archive_extractor import ArchiveExtractor


class FakeSevenZipExtractor(ArchiveExtractor):
    def __init__(self) -> None:
        self.extract_seven_zip_calls: list[tuple[Path, Path]] = []

    def extract_seven_zip(self, archive: Path, destination: Path) -> Path:
        self.extract_seven_zip_calls.append((archive, destination))
        return destination
