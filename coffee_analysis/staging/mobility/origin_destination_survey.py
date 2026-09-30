from pathlib import Path

import numpy
import pandas
import pyogrio
from pyproj import Transformer

from coffee_analysis.infrastructure.data_directories import DataDirectories

SURVEY_PROJECTION = "EPSG:22523"
GEOGRAPHIC_PROJECTION = "EPSG:4326"
SURVEY_FOLDER = ("pesquisa_od", "2023", "Site_190225")
SURVEY_DATABASE = "Banco2023_divulgacao_190225.dbf"
TRIP_PURPOSES = {
    1: "Trabalho indústria",
    2: "Trabalho comércio",
    3: "Trabalho serviços",
    4: "Escola/educação",
    5: "Compras",
    6: "Saúde",
    7: "Recreação/visitas/lazer",
    8: "Residência",
    9: "Procurar emprego",
    10: "Assuntos pessoais",
    11: "Refeição",
}


class OriginDestinationSurvey:
    def __init__(self, directories: DataDirectories) -> None:
        self._directories = directories
        self._transformer = Transformer.from_crs(SURVEY_PROJECTION, GEOGRAPHIC_PROJECTION, always_xy=True)

    def build(self) -> Path:
        records = self._read_records()
        people = self._people(records)
        people.to_parquet(self._directories.staging_file("pesquisa_od", "pessoas.parquet"), index=False)
        trips = self._trips(records)
        destination = self._directories.staging_file("pesquisa_od", "viagens.parquet")
        trips.to_parquet(destination, index=False)
        return destination

    def _read_records(self) -> pandas.DataFrame:
        source = self._directories.raw_file(*SURVEY_FOLDER, SURVEY_DATABASE)
        columns = ["ID_PESS", "F_PESS", "FE_PESS", "ZONATRA1", "CO_TR1_X", "CO_TR1_Y", "N_VIAG", "FE_VIA", "ZONA_D", "CO_D_X", "CO_D_Y", "MOTIVO_D", "H_CHEG"]
        return pyogrio.read_dataframe(source, read_geometry=False, columns=columns)

    def _people(self, records: pandas.DataFrame) -> pandas.DataFrame:
        first_records = records[records["F_PESS"] == 1]
        longitude, latitude = self._geographic(first_records["CO_TR1_X"], first_records["CO_TR1_Y"])
        return pandas.DataFrame(
            {
                "id_pessoa": first_records["ID_PESS"].astype("int64").to_numpy(),
                "fator_expansao_pessoa": first_records["FE_PESS"].to_numpy(),
                "codigo_zona_trabalho": first_records["ZONATRA1"].replace(0, pandas.NA).astype("Int32").to_numpy(),
                "latitude_trabalho": latitude,
                "longitude_trabalho": longitude,
            }
        )

    def _trips(self, records: pandas.DataFrame) -> pandas.DataFrame:
        trips = records[records["N_VIAG"] > 0]
        longitude, latitude = self._geographic(trips["CO_D_X"], trips["CO_D_Y"])
        purposes = trips["MOTIVO_D"].astype("int32")
        return pandas.DataFrame(
            {
                "id_pessoa": trips["ID_PESS"].astype("int64").to_numpy(),
                "numero_viagem": trips["N_VIAG"].astype("int32").to_numpy(),
                "fator_expansao_viagem": trips["FE_VIA"].to_numpy(),
                "codigo_zona_destino": trips["ZONA_D"].astype("int32").to_numpy(),
                "codigo_motivo_destino": purposes.to_numpy(),
                "motivo_destino": purposes.map(TRIP_PURPOSES).to_numpy(),
                "hora_chegada": trips["H_CHEG"].astype("int32").to_numpy(),
                "latitude_destino": latitude,
                "longitude_destino": longitude,
            }
        )

    def _geographic(self, easting: pandas.Series, northing: pandas.Series) -> tuple[numpy.ndarray, numpy.ndarray]:
        known = (easting > 0) & (northing > 0)
        valid_easting = easting.where(known).to_numpy(dtype="float64")
        valid_northing = northing.where(known).to_numpy(dtype="float64")
        longitude, latitude = self._transformer.transform(valid_easting, valid_northing)
        return numpy.asarray(longitude), numpy.asarray(latitude)
