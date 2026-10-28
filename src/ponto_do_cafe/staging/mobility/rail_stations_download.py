from pathlib import Path

from ponto_do_cafe.infrastructure.data_directories import DataDirectories
from ponto_do_cafe.infrastructure.http_client import HttpClient


class RailStationsDownload:
    def __init__(
        self,
        http_client: HttpClient,
        directories: DataDirectories,
    ) -> None:
        self._http_client = http_client
        self._directories = directories

    def build(self) -> Path:
        geosampa_directory = self._directories.raw_file("geosampa", self._directories.competence)
        wfs_base = "https://wfs.geosampa.prefeitura.sp.gov.br/geoserver/ows?service=WFS&version=2.0.0&request=GetFeature&outputFormat=application/json&srsName=EPSG:4326"

        self._download_layer(geosampa_directory, wfs_base, "estacao_metro")
        self._download_layer(geosampa_directory, wfs_base, "estacao_trem")
        return geosampa_directory

    def _download_layer(self, geosampa_directory: Path, wfs_base: str, layer_name: str) -> None:
        destination = geosampa_directory / f"{layer_name}.json"
        url = f"{wfs_base}&typeNames=geoportal:{layer_name}"
        self._http_client.download(url, destination)
