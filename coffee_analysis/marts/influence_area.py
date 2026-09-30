from datetime import date
from itertools import product
from pathlib import Path

import geopandas
import pandas

from coffee_analysis.infrastructure.analytical_database import AnalyticalDatabase
from coffee_analysis.marts.candidate_addresses import CandidateAddresses
from coffee_analysis.infrastructure.data_directories import DataDirectories
from coffee_analysis.marts.influence_area_layers import InfluenceAreaLayers

RADII_IN_METERS = (300, 500, 1000)
GEOGRAPHIC_PROJECTION = "EPSG:4674"
SURVEY_GEOGRAPHIC_PROJECTION = "EPSG:4326"
METRIC_PROJECTION = "EPSG:31983"


class InfluenceArea:
    def __init__(
        self,
        database: AnalyticalDatabase,
        directories: DataDirectories,
        candidates: CandidateAddresses,
        reference_date: date,
    ) -> None:
        self._database = database
        self._directories = directories
        self._candidates = candidates
        self._reference_date = reference_date

    def build(self) -> Path:
        located = self._located_candidates()
        layers = self._layers()
        combinations = product(zip(located["endereco_candidato"], located.geometry), RADII_IN_METERS)
        rows = [layers.summarize(candidate, location, radius) for (candidate, location), radius in combinations]
        summary = pandas.DataFrame(rows)
        with_location = summary.merge(pandas.DataFrame(located.drop(columns="geometry")), on="endereco_candidato")
        destination = self._directories.marts_file("areas_influencia.parquet")
        with_location.to_parquet(destination)
        return destination

    def _located_candidates(self) -> geopandas.GeoDataFrame:
        addresses_file = self._directories.staging_file("cnefe", "enderecos.parquet")
        located = self._database.frame(self._candidates.locate_query(addresses_file))
        return self._as_points(located.to_pandas(), GEOGRAPHIC_PROJECTION)

    def _as_points(self, frame: pandas.DataFrame, projection: str) -> geopandas.GeoDataFrame:
        located_rows = frame[frame["latitude"].notna()]
        geometry = geopandas.points_from_xy(located_rows["longitude"], located_rows["latitude"])
        points = geopandas.GeoDataFrame(located_rows, geometry=geometry, crs=projection)
        return points.to_crs(METRIC_PROJECTION)

    def _trip_destinations(self) -> geopandas.GeoDataFrame:
        trips = pandas.read_parquet(self._directories.marts_file("viagens_destino.parquet"))
        renamed = trips.rename(columns={"latitude_destino": "latitude", "longitude_destino": "longitude"})
        return self._as_points(renamed, SURVEY_GEOGRAPHIC_PROJECTION)

    def _layers(self) -> InfluenceAreaLayers:
        metrics = pandas.read_parquet(self._directories.marts_file("distritos_metricas_rais.parquet"))
        establishments = pandas.read_parquet(self._directories.marts_file("estabelecimentos_cafe.parquet"))
        jobs = pandas.read_parquet(self._directories.marts_file("empregos_formais_cep.parquet"))
        stations = pandas.read_parquet(self._directories.marts_file("estacoes_demanda.parquet"))
        survey_metrics = pandas.read_parquet(self._directories.marts_file("distritos_metricas.parquet"))
        return InfluenceAreaLayers(
            sectors=self._sectors_with_spending(metrics),
            establishments=self._as_points(establishments, GEOGRAPHIC_PROJECTION),
            jobs=self._as_points(jobs, GEOGRAPHIC_PROJECTION),
            trips=self._trip_destinations(),
            stations=self._as_points(stations, SURVEY_GEOGRAPHIC_PROJECTION),
            city_spending_per_person=float(metrics["gasto_per_capita_cidade"].iloc[0]),
            city_spending_per_attracted_trip=float(survey_metrics["gasto_por_viagem_atraida_cidade"].iloc[0]),
            reference_date=self._reference_date,
        )

    def _sectors_with_spending(self, metrics: pandas.DataFrame) -> geopandas.GeoDataFrame:
        sectors = geopandas.read_parquet(self._directories.staging_file("censo_2022", "setores.parquet")).to_crs(METRIC_PROJECTION)
        spending = metrics[["codigo_distrito", "gasto_cesta_cafeteria_por_domicilio_atual"]]
        return sectors.merge(spending, on="codigo_distrito", how="left")
