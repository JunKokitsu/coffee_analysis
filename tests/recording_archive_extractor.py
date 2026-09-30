from pathlib import Path

from coffee_analysis.infrastructure.archive_extractor import ArchiveExtractor


class RecordingArchiveExtractor(ArchiveExtractor):
    def __init__(self) -> None:
        self.unzip_calls: list[tuple[Path, Path, tuple[str, ...], bool]] = []

    def unzip(
        self,
        archive: Path,
        destination: Path,
        member_patterns: tuple[str, ...] = (),
        flatten: bool = False,
    ) -> Path:
        self.unzip_calls.append((archive, destination, member_patterns, flatten))
        destination.mkdir(parents=True, exist_ok=True)
        return destination
