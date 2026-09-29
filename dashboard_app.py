from datetime import date
from pathlib import Path

import streamlit

from coffee_analysis.analytical_database import AnalyticalDatabase
from coffee_analysis.competence import Competence
from coffee_analysis.dashboard.chart_palette import ChartPalette
from coffee_analysis.dashboard.coffee_dashboard import CoffeeDashboard
from coffee_analysis.dashboard.dashboard_charts import DashboardCharts
from coffee_analysis.dashboard.dashboard_data import DashboardData
from coffee_analysis.data_directories import DataDirectories
from main import PILOT_DISTRICT_CODES

streamlit.set_page_config(page_title="Cafeterias em São Paulo", page_icon="☕", layout="wide")
directories = DataDirectories(Path(__file__).parent, Competence.of(date.today()).month)
palette = ChartPalette.for_theme(streamlit.context.theme.type)
dashboard = CoffeeDashboard(DashboardData(AnalyticalDatabase(), directories), DashboardCharts(palette), PILOT_DISTRICT_CODES)
dashboard.render()
