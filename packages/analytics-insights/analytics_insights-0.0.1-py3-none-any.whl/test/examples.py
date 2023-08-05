# These examples work with the LAB DB and the aforos data. There is no api_Wrapper

from timeseries_etl.timeseries_etl import TimeSeriesEtl
from analytics_plots.plotter import AnalyticsPlotter


db_type = 'vertica'
host = '172.24.9.121'
port = 5433
user = 'dbadmin'
password = 'default'
dbname = 'pems'
schema = 'public'

table = 'measure_link_aforos_inrix_15min'
measure = 'speed'

timeseries_etl = TimeSeriesEtl(db_type, host, port, user, password, dbname, schema)
api_wrapper = None
plotter = AnalyticsPlotter(api_wrapper, timeseries_etl, 190, 100)
ax, df = plotter.bar_plot_data_distribution_by_month(table, measure)

ax, df = plotter.bar_plot_item_distribution_by_month(table, measure)
ax, df = plotter.density_plot_items_with_ndatapoints(table)
ax, df = plotter.density_plot_measure(table, measure)
ax, df = plotter.item_profile(466778840, measure, table)
ax, df = plotter.bar_plot_holes_by_month(table, measure, 15, [466778840, 337618483, 466817933, 466979359])