from collections.abc import Callable
from datetime import date
from pathlib import Path

from ponto_do_cafe.staging.ibge.address_directory import AddressDirectory
from ponto_do_cafe.infrastructure.analytical_database import AnalyticalDatabase
from ponto_do_cafe.staging.cepea.arabica_prices import ArabicaPrices
from ponto_do_cafe.marts.candidate_addresses import CandidateAddresses
from ponto_do_cafe.staging.ibge.census_districts import CensusDistricts
from ponto_do_cafe.staging.ibge.census_sector_income import CensusSectorIncome
from ponto_do_cafe.marts.coffee_shop_classification import CoffeeShopClassification
from ponto_do_cafe.marts.commercial_property_prices import CommercialPropertyPrices
from ponto_do_cafe.staging.cnpj.company_registry import CompanyRegistry
from ponto_do_cafe.staging.ibge.consumer_price_index import ConsumerPriceIndex
from ponto_do_cafe.infrastructure.data_directories import DataDirectories
from ponto_do_cafe.quality.data_quality_check import DataQualityCheck
from ponto_do_cafe.marts.district_income import DistrictIncome
from ponto_do_cafe.marts.district_metrics import DistrictMetrics
from ponto_do_cafe.marts.district_mobility import DistrictMobility
from ponto_do_cafe.staging.ibge.household_coffee_spending import HouseholdCoffeeSpending
from ponto_do_cafe.marts.influence_area import InfluenceArea
from ponto_do_cafe.staging.mobility.metro_station_demand import MetroStationDemand
from ponto_do_cafe.staging.mobility.motiva_station_demand import MotivaStationDemand
from ponto_do_cafe.marts.opportunity_index import OpportunityIndex
from ponto_do_cafe.marts.origin_destination_market import OriginDestinationMarket
from ponto_do_cafe.staging.mobility.origin_destination_survey import OriginDestinationSurvey
from ponto_do_cafe.reporting.pilot_report import PilotReport
from ponto_do_cafe.pipeline.download_steps import DownloadSteps
from ponto_do_cafe.pipeline.pipeline_graph import STEP_LAYERS
from ponto_do_cafe.staging.itbi.property_transactions import PropertyTransactions
from ponto_do_cafe.staging.mobility.rail_stations import RailStations
from ponto_do_cafe.staging.rais.rais_registry import RaisRegistry
from ponto_do_cafe.marts.formal_employment import FormalEmployment
from ponto_do_cafe.marts.ranking_comparison import RankingComparison
from ponto_do_cafe.marts.station_flow import StationFlow
from ponto_do_cafe.marts.survival_analysis import SurvivalAnalysis


class PilotPipeline:
    def __init__(
        self,
        directories: DataDirectories,
        candidates: CandidateAddresses,
        pilot_district_codes: tuple[str, ...],
        reference_date: date,
    ) -> None:
        database = AnalyticalDatabase()
        download_steps = DownloadSteps(directories).build()
        self._steps: dict[str, Callable[[], Path]] = {
            **download_steps,
            "enderecos": AddressDirectory(database, directories).build,
            "censo": CensusDistricts(directories).build,
            "renda_2010": CensusSectorIncome(database, directories).build,
            "ipca": ConsumerPriceIndex(database, directories).build,
            "pof": HouseholdCoffeeSpending(database, directories).build,
            "cepea": ArabicaPrices(directories, reference_date).build,
            "rais": RaisRegistry(database, directories).build,
            "itbi": PropertyTransactions(database, directories).build,
            "cnpj": CompanyRegistry(database, directories).build,
            "pesquisa_od": OriginDestinationSurvey(directories).build,
            "demanda_metro": MetroStationDemand(database, directories).build,
            "demanda_motiva": MotivaStationDemand(database, directories).build,
            "estacoes": RailStations(database, directories).build,
            "qualidade": DataQualityCheck(database, directories).build,
            "renda": DistrictIncome(database, directories).build,
            "empregos": FormalEmployment(database, directories).build,
            "preco_m2": CommercialPropertyPrices(database, directories).build,
            "cafeterias": CoffeeShopClassification(database, directories).build,
            "sobrevivencia": SurvivalAnalysis(database, directories, reference_date).build,
            "metricas_rais": DistrictMetrics(database, directories, reference_date).build,
            "indice_rais": OpportunityIndex(
                database,
                directories.marts_file("distritos_metricas_rais.parquet"),
                directories.marts_file("distritos_indice_oportunidade_rais.parquet"),
            ).build,
            "fluxo_estacoes": StationFlow(database, directories).build,
            "mobilidade": DistrictMobility(database, directories).build,
            "metricas": OriginDestinationMarket(database, directories).build,
            "indice": OpportunityIndex(
                database,
                directories.marts_file("distritos_metricas.parquet"),
                directories.marts_file("distritos_indice_oportunidade.parquet"),
            ).build,
            "comparacao_ranking": RankingComparison(database, directories).build,
            "area_influencia": InfluenceArea(database, directories, candidates, reference_date).build,
            "relatorio": PilotReport(database, directories, pilot_district_codes, reference_date).build,
        }

    def step_names(self) -> list[str]:
        return list(self._steps)

    def run(self, selected_steps: list[str]) -> list[Path]:
        step_names = selected_steps or list(STEP_LAYERS)
        return [self._run_step(step_name) for step_name in step_names]

    def _run_step(self, step_name: str) -> Path:
        print(f"executando etapa: {step_name}", flush=True)
        output = self._steps[step_name]()
        print(f"  gerado: {output}", flush=True)
        return output
