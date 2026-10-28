import fnmatch
import shutil
import subprocess
import zipfile
from pathlib import Path

SEVEN_ZIP_BINARY_NAMES = ("7z", "7zz")


class ArchiveExtractor:
    def unzip(
        self,
        archive: Path,
        destination: Path,
        member_patterns: tuple[str, ...] = (),
        flatten: bool = False,
    ) -> Path:
        destination.mkdir(parents=True, exist_ok=True)
        self._unzip_into_destination(archive, destination, member_patterns, flatten)
        return destination

    def _unzip_into_destination(
        self,
        archive: Path,
        destination: Path,
        member_patterns: tuple[str, ...],
        flatten: bool,
    ) -> None:
        with zipfile.ZipFile(archive) as zip_file:
            self._extract_members(zip_file, destination, member_patterns, flatten)

    def _extract_members(
        self,
        zip_file: zipfile.ZipFile,
        destination: Path,
        member_patterns: tuple[str, ...],
        flatten: bool,
    ) -> None:
        member_names = self._select_member_names(zip_file, member_patterns)
        for member_name in member_names:
            self._extract_member(zip_file, member_name, destination, flatten)

    def _select_member_names(self, zip_file: zipfile.ZipFile, member_patterns: tuple[str, ...]) -> list[str]:
        if not member_patterns:
            return zip_file.namelist()
        return [name for name in zip_file.namelist() if self._matches_any_pattern(name, member_patterns)]

    def _matches_any_pattern(self, name: str, member_patterns: tuple[str, ...]) -> bool:
        return any(fnmatch.fnmatch(name, pattern) for pattern in member_patterns)

    def _extract_member(self, zip_file: zipfile.ZipFile, member_name: str, destination: Path, flatten: bool) -> None:
        if flatten:
            self._extract_member_flattened(zip_file, member_name, destination)
            return
        zip_file.extract(member_name, destination)

    def _extract_member_flattened(self, zip_file: zipfile.ZipFile, member_name: str, destination: Path) -> None:
        target_path = destination / Path(member_name).name
        self._write_member_bytes(zip_file, member_name, target_path)

    def _write_member_bytes(self, zip_file: zipfile.ZipFile, member_name: str, target_path: Path) -> None:
        with zip_file.open(member_name) as source_file:
            target_path.write_bytes(source_file.read())

    def extract_seven_zip(self, archive: Path, destination: Path) -> Path:
        destination.mkdir(parents=True, exist_ok=True)
        binary_path = self._find_seven_zip_binary()
        subprocess.run([binary_path, "e", "-y", f"-o{destination}", str(archive)], check=True, capture_output=True)
        return destination

    def _find_seven_zip_binary(self) -> str:
        candidate_paths = (shutil.which(name) for name in SEVEN_ZIP_BINARY_NAMES)
        binary_path = next((path for path in candidate_paths if path is not None), None)
        return self._require_seven_zip_binary(binary_path)

    def _require_seven_zip_binary(self, binary_path: str | None) -> str:
        if binary_path is not None:
            return binary_path
        raise FileNotFoundError("nenhum binário 7z ou 7zz encontrado no PATH")
