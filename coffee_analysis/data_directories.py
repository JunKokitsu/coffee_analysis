from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DataDirectories:
    root: Path
    competence: str

    def raw_file(self, *parts: str) -> Path:
        return self.root.joinpath("data", "raw", *parts)

    def raw_competence(self, source: str) -> Path:
        directory = self.root.joinpath("data", "raw", source)
        competences = sorted(path for path in directory.iterdir() if path.is_dir() and path.name[:7] <= self.competence)
        if not competences:
            raise FileNotFoundError(f"nenhuma competência de {source} até {self.competence} em {directory}")
        return competences[-1]

    def raw_competence_file(self, source: str, name: str) -> Path:
        return self.raw_competence(source) / name

    def current_raw_file(self, source: str, name: str) -> Path:
        directory = self.root.joinpath("data", "raw", source, self.competence)
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

    def quality_file(self, name: str) -> Path:
        directory = self.root.joinpath("data", "quality")
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
