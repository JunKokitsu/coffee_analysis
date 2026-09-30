from collections.abc import Callable
from datetime import date
from pathlib import Path

from coffee_analysis.staging.ibge.address_directory import AddressDirectory
from coffee_analysis.infrastructure.analytical_database import AnalyticalDatabase
from coffee_analysis.staging.cepea.arabica_prices import ArabicaPrices
from coffee_analysis.marts.candidate_addresses import CandidateAddresses
from coffee_analysis.staging.ibge.census_districts import CensusDistricts
from coffee_analysis.staging.ibge.census_sector_income import CensusSectorIncome
from coffee_analysis.marts.coffee_shop_classification import CoffeeShopClassification
from coffee_analysis.marts.commercial_property_prices import CommercialPropertyPrices
from coffee_analysis.staging.cnpj.company_registry import CompanyRegistry
from coffee_analysis.staging.ibge.consumer_price_index import ConsumerPriceIndex
from coffee_analysis.infrastructure.data_directories import DataDirectories
from coffee_analysis.quality.data_quality_check import DataQualityCheck
from coffee_analysis.marts.district_income import DistrictIncome
from coffee_analysis.marts.district_metrics import DistrictMetrics
from coffee_analysis.marts.district_mobility import DistrictMobility
from coffee_analysis.staging.ibge.household_coffee_spending import HouseholdCoffeeSpending
from coffee_analysis.marts.influence_area import InfluenceArea
from coffee_analysis.staging.mobility.metro_station_demand import MetroStationDemand
from coffee_analysis.staging.mobility.motiva_station_demand import MotivaStationDemand
from coffee_analysis.marts.opportunity_index import OpportunityIndex
from coffee_analysis.marts.origin_destination_market import OriginDestinationMarket
from coffee_analysis.staging.mobility.origin_destination_survey import OriginDestinationSurvey
from coffee_analysis.reporting.pilot_report import PilotReport
from coffee_analysis.pipeline.download_steps import DownloadSteps
from coffee_analysis.pipeline.pipeline_graph import STEP_LAYERS
from coffee_analysis.staging.itbi.property_transactions import PropertyTransactions
from coffee_analysis.staging.mobility.rail_stations import RailStations
from coffee_analysis.staging.rais.rais_registry import RaisRegistry
from coffee_analysis.marts.formal_employment import FormalEmployment
from coffee_analysis.marts.ranking_comparison import RankingComparison
from coffee_analysis.marts.station_flow import StationFlow
from coffee_analysis.marts.survival_analysis import SurvivalAnalysis


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
