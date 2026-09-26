from datetime import date, timedelta

import geopandas
import pandas
from shapely.geometry.base import BaseGeometry

WORKPLACE_CONSUMPTION_SHARE = 0.5
RECENT_OPENING_DAYS = 730


class InfluenceAreaLayers:
    def __init__(
        self,
        sectors: geopandas.GeoDataFrame,
        establishments: geopandas.GeoDataFrame,
        jobs: geopandas.GeoDataFrame,
        city_spending_per_person: float,
        reference_date: date,
    ) -> None:
        self._sectors = sectors
        self._establishments = establishments
        self._jobs = jobs
        self._city_spending_per_person = city_spending_per_person
        self._recent_opening_limit = pandas.Timestamp(reference_date - timedelta(days=RECENT_OPENING_DAYS))

    def summarize(self, candidate: str, location: BaseGeometry, radius: int) -> dict[str, float | int | str]:
        circle = location.buffer(radius)
        demand = self._demand(circle)
        competition = self._competition(circle)
        market = demand["mercado_potencial_mensal"]
        direct_competitors = competition["cafeterias_ativas"]
        sale_points = direct_competitors + competition["lanchonetes_ativas"] + competition["padarias_ativas"]
        ratios = {
            "mercado_mensal_por_cafeteria": self._ratio(market, direct_competitors),
            "mercado_mensal_por_ponto_de_venda": self._ratio(market, sale_points),
        }
        identification: dict[str, float | int | str] = {"endereco_candidato": candidate, "raio_metros": radius}
        return {**identification, **demand, **competition, **ratios}

    def _ratio(self, numerator: float, denominator: int) -> float:
        if denominator == 0:
            return float("nan")
        return numerator / denominator

    def _demand(self, circle: BaseGeometry) -> dict[str, float]:
        intersecting = self._sectors[self._sectors.intersects(circle)]
        overlap = intersecting.intersection(circle)
        share = overlap.area / intersecting.area
        population = float((intersecting["populacao"] * share).sum())
        households = intersecting["domicilios_ocupados"] * share
        resident_spending = float((households * intersecting["gasto_cesta_cafeteria_por_domicilio_atual"]).sum())
        nearby_jobs = self._jobs[self._jobs.within(circle)]
        formal_jobs = float(nearby_jobs["vinculos_ativos"].sum())
        workplace_spending = formal_jobs * self._city_spending_per_person
        market = (1 - WORKPLACE_CONSUMPTION_SHARE) * resident_spending + WORKPLACE_CONSUMPTION_SHARE * workplace_spending
        return {
            "populacao_residente": population,
            "domicilios": float(households.sum()),
            "vinculos_formais": formal_jobs,
            "gasto_mensal_residentes": resident_spending,
            "mercado_potencial_mensal": market,
        }

    def _competition(self, circle: BaseGeometry) -> dict[str, int]:
        nearby = self._establishments[self._establishments.within(circle)]
        active = nearby[nearby["ativo"]]
        categories = active["categoria"]
        coffee_shops = nearby[nearby["categoria"] == "cafeteria"]
        opening_dates = pandas.to_datetime(coffee_shops["data_inicio_atividade"])
        return {
            "cafeterias_ativas": int((categories == "cafeteria").sum()),
            "lanchonetes_ativas": int((categories == "lanchonete").sum()),
            "padarias_ativas": int((categories == "padaria").sum()),
            "cafeterias_abertas_24_meses": int((opening_dates > self._recent_opening_limit).sum()),
        }
