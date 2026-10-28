import re
from ftplib import FTP

DEFAULT_RAIS_HOST = "ftp.mtps.gov.br"
DEFAULT_RAIS_DIRECTORY = "/pdet/microdados/RAIS/"
YEAR_PATTERN = re.compile(r"^\d{4}$")
FTP_TIMEOUT_SECONDS = 120


class RaisReleases:
    def __init__(self, host: str = DEFAULT_RAIS_HOST, directory: str = DEFAULT_RAIS_DIRECTORY) -> None:
        self._host = host
        self._directory = directory

    def latest_year(self) -> str:
        with FTP(self._host, timeout=FTP_TIMEOUT_SECONDS) as connection:
            connection.login()
            names = connection.nlst(self._directory)
        return self.latest_year_among(names)

    def latest_year_among(self, names: list[str]) -> str:
        years = [name for name in (self._last_segment(name) for name in names) if YEAR_PATTERN.fullmatch(name)]
        return self._require_latest(years)

    def _last_segment(self, name: str) -> str:
        return name.rsplit("/", 1)[-1]

    def _require_latest(self, years: list[str]) -> str:
        if years:
            return sorted(years)[-1]
        raise ValueError("nenhum ano de publicação da RAIS encontrado")
