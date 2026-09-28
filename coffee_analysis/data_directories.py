from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DataDirectories:
    root: Path

    def raw_file(self, *parts: str) -> Path:
        return self.root.joinpath("data", "raw", *parts)

    def raw_files(self, folder: str, pattern: str) -> list[Path]:
        directory = self.root.joinpath("data", "raw", folder)
        return sorted(directory.glob(pattern))

    def latest_raw_competence(self, source: str) -> Path:
        directory = self.root.joinpath("data", "raw", source)
        competences = sorted(path for path in directory.iterdir() if path.is_dir())
        return competences[-1]

    def processed_file(self, name: str) -> Path:
        directory = self.root.joinpath("data", "processed")
        directory.mkdir(parents=True, exist_ok=True)
        return directory / name

    def staging_file(self, source: str, name: str) -> Path:
        directory = self.root.joinpath("data", "staging", source)
        directory.mkdir(parents=True, exist_ok=True)
        return directory / name

    def marts_file(self, name: str) -> Path:
        directory = self.root.joinpath("data", "marts")
        directory.mkdir(parents=True, exist_ok=True)
        return directory / name

    def temporary_directory(self) -> Path:
        directory = self.root.joinpath("data", "temporary")
        directory.mkdir(parents=True, exist_ok=True)
        return directory

    def report_file(self, name: str) -> Path:
        directory = self.root.joinpath("reports")
        directory.mkdir(parents=True, exist_ok=True)
        return directory / name
