from datetime import date
from pathlib import Path

import streamlit

from ponto_do_cafe.infrastructure.analytical_database import AnalyticalDatabase
from ponto_do_cafe.infrastructure.competence import Competence
from ponto_do_cafe.dashboard.chart_palette import ChartPalette
from ponto_do_cafe.dashboard.coffee_dashboard import CoffeeDashboard
from ponto_do_cafe.dashboard.dashboard_charts import DashboardCharts
from ponto_do_cafe.dashboard.dashboard_data import DashboardData
from ponto_do_cafe.infrastructure.data_directories import DataDirectories
from main import PILOT_DISTRICT_CODES

streamlit.set_page_config(page_title="Cafeterias em São Paulo", page_icon="☕", layout="wide")
directories = DataDirectories(Path(__file__).parent, Competence.of(date.today()).month)
palette = ChartPalette.for_theme(streamlit.context.theme.type)
dashboard = CoffeeDashboard(DashboardData(AnalyticalDatabase(), directories), DashboardCharts(palette), PILOT_DISTRICT_CODES)
dashboard.render()
