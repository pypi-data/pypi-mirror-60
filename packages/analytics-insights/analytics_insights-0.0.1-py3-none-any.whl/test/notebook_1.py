# An example of how to use the analytics_insights tool

from analytics_plots.plotter import AnalyticsPlotter


# we are going to use the DGT environment. Currently we only have detectors for 1 min ( raw data )
# and speed as measure for this environment but things might change

host = '172.24.76.225'
endpoint = 'tdfana'
datasource = 'etx'
measure_period = 1
width = 600
height = 500

# First of all we create the plotter.
plotter = AnalyticsPlotter(host, endpoint, datasource, measure_period, width, height)
# The plotter has different types of plots. A useful one is to get a line plot for several items to see if they are correlated
res = plotter.get_line_plot_for_several_items([100, 101, 102, 105], 'detector', 'speed', 'real', '20181010')
