from pathlib import Path

import geopandas
import pyogrio

from coffee_analysis.data_directories import DataDirectories

SAO_PAULO_MUNICIPALITY_CODE = "3550308"
METRIC_PROJECTION = "EPSG:31983"


class CensusDistricts:
    def __init__(self, directories: DataDirectories) -> None:
        self._directories = directories

    def build(self) -> Path:
        sectors = self._read_sectors()
        sectors.to_parquet(self._directories.processed_file("setores_censo_2022.parquet"))
        districts = self._read_districts()
        districts.to_parquet(self._directories.processed_file("distritos_censo_2022_geometria.parquet"))
        return self._directories.processed_file("setores_censo_2022.parquet")

    def _read_sectors(self) -> geopandas.GeoDataFrame:
        source = self._directories.raw_file("ibge", "SP_setores_CD2022.gpkg")
        sectors = pyogrio.read_dataframe(
            source,
            columns=["CD_SETOR", "CD_DIST", "NM_DIST", "v0001", "v0007"],
            where=f"CD_MUN = '{SAO_PAULO_MUNICIPALITY_CODE}'",
        )
        renamed = sectors.rename(
            columns={
                "CD_SETOR": "codigo_setor",
                "CD_DIST": "codigo_distrito",
                "NM_DIST": "nome_distrito",
                "v0001": "populacao",
                "v0007": "domicilios_ocupados",
            }
        )
        typed = renamed.astype({"populacao": "int64", "domicilios_ocupados": "int64"})
        return typed.to_crs(METRIC_PROJECTION)

    def _read_districts(self) -> geopandas.GeoDataFrame:
        source = self._directories.raw_file("ibge", "SP_distritos_CD2022.gpkg")
        districts = pyogrio.read_dataframe(
            source,
            columns=["CD_DIST", "NM_DIST", "AREA_KM2", "v0001", "v0007"],
            where=f"CD_MUN = '{SAO_PAULO_MUNICIPALITY_CODE}'",
        )
        renamed = districts.rename(
            columns={
                "CD_DIST": "codigo_distrito",
                "NM_DIST": "nome_distrito",
                "AREA_KM2": "area_km2",
                "v0001": "populacao_2022",
                "v0007": "domicilios_2022",
            }
        )
        typed = renamed.astype({"area_km2": "float64", "populacao_2022": "int64", "domicilios_2022": "int64"})
        return typed.to_crs(METRIC_PROJECTION)
