from collections.abc import Callable
from datetime import date
from pathlib import Path

from coffee_analysis.address_directory import AddressDirectory
from coffee_analysis.analytical_database import AnalyticalDatabase
from coffee_analysis.arabica_prices import ArabicaPrices
from coffee_analysis.candidate_addresses import CandidateAddresses
from coffee_analysis.census_districts import CensusDistricts
from coffee_analysis.coffee_shop_registry import CoffeeShopRegistry
from coffee_analysis.commercial_property_prices import CommercialPropertyPrices
from coffee_analysis.consumer_price_index import ConsumerPriceIndex
from coffee_analysis.data_directories import DataDirectories
from coffee_analysis.district_income import DistrictIncome
from coffee_analysis.district_metrics import DistrictMetrics
from coffee_analysis.household_coffee_spending import HouseholdCoffeeSpending
from coffee_analysis.influence_area import InfluenceArea
from coffee_analysis.opportunity_index import OpportunityIndex
from coffee_analysis.pilot_report import PilotReport
from coffee_analysis.rais_workforce import RaisWorkforce
from coffee_analysis.survival_analysis import SurvivalAnalysis


class PilotPipeline:
    def __init__(
        self,
        directories: DataDirectories,
        candidates: CandidateAddresses,
        pilot_district_codes: tuple[str, ...],
        reference_date: date,
    ) -> None:
        database = AnalyticalDatabase()
        self._steps: dict[str, Callable[[], Path]] = {
            "enderecos": AddressDirectory(database, directories).build,
            "censo": CensusDistricts(directories).build,
            "ipca": ConsumerPriceIndex(database, directories).build,
            "pof": HouseholdCoffeeSpending(database, directories).build,
            "renda": DistrictIncome(database, directories).build,
            "cepea": ArabicaPrices(directories, reference_date).build,
            "rais": RaisWorkforce(database, directories).build,
            "itbi": CommercialPropertyPrices(database, directories).build,
            "cnpj": CoffeeShopRegistry(database, directories).build,
            "sobrevivencia": SurvivalAnalysis(database, directories, reference_date).build,
            "metricas": DistrictMetrics(database, directories, reference_date).build,
            "indice": OpportunityIndex(database, directories).build,
            "area_influencia": InfluenceArea(database, directories, candidates, reference_date).build,
            "relatorio": PilotReport(database, directories, pilot_district_codes, reference_date).build,
        }

    def run(self, selected_steps: list[str]) -> list[Path]:
        step_names = selected_steps or list(self._steps)
        return [self._run_step(step_name) for step_name in step_names]

    def _run_step(self, step_name: str) -> Path:
        print(f"executando etapa: {step_name}", flush=True)
        output = self._steps[step_name]()
        print(f"  gerado: {output}", flush=True)
        return output
