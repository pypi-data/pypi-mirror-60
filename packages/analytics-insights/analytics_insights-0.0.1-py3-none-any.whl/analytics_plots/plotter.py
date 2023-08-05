import altair as alt
from typing import List
from py_analytics_api.py_analytics_api import PyAnalyticsApi, TSApiDef
from timeseries_etl.timeseries_etl import TimeSeriesEtl, VerticaDao
from datetime import datetime
import pandas as pd
from altair import HConcatChart
import seaborn as sns
import matplotlib.dates as mdates
from matplotlib.offsetbox import AnchoredText
from sklearn.metrics import mean_absolute_error


def build_df_from_apidef_list(ts_list: List[TSApiDef], api_wrapper: PyAnalyticsApi) -> pd.DataFrame:
    """
    Build a Pandas dataframe from a list of timeseries that we want to retrieve and an analytics endpoint.
    :param ts_list:
    :param api_wrapper:
    :return: A dataframe with the first columns as TSinfo.fields and the rest the values of the profile with a timestamp
    column with values as [0,1,...len(profile)] and a second column with the name of the measure and the value for each
    timestamp
    item_id         item_type measure data_type       day timestamp  volume
    1  measurement_site  volume      real  20180505         0    72.0
    1  measurement_site  volume      real  20180505         1    86.0
       ...               ...     ...       ...       ...       ...     ...
    4  measurement_site  volume      real  20180505       286   111.0
    """
    df_rows = []
    for ts in ts_list:
        # the information for the named tuple as values
        ts_info = list(ts._asdict().values())
        profile = api_wrapper.get_day_ts_for_item(ts.item_id, ts.item_type, ts.measure, ts.measure_period, ts.data_type,
                                                  day=ts.day.strftime("%Y%m%d%"))
        # a row is the ts_info + the profile
        row = ts_info + profile
        df_rows.append(row)
    res_df = pd.DataFrame(df_rows)
    res_df = res_df.replace('NaN', float('nan'))
    res_df.columns = list(TSApiDef._fields) + list(range(0, len(profile)))
    res_df = res_df.melt(id_vars=list(TSApiDef._fields), var_name='timestamp', value_name=ts_list[0].measure)
    return res_df


class AnalyticsPlotter:
    def __init__(self, api_wrapper: PyAnalyticsApi, timeseries_etl: TimeSeriesEtl, width: int, height: int):
        self.api_wrapper = api_wrapper
        self.timeseries_etl = timeseries_etl
        self.plot_width = width
        self.plot_height = height

    def line_plot_for_several_items(self, item_ids: List[int], item_type: str, measure_name: str, measure_period: int,
                                    data_type: str,
                                    day: str) -> HConcatChart:
        """
        Plots the values for a list of item ids for a given item type, measure and data type during a given day
        :param item_ids:
        :param item_type:
        :param measure_name:
        :param measure_period:
        :param data_type:
        :param day: a day in the format YYYY-mm-dd
        :return:
        """
        day_dt = datetime.strptime(day, "%Y-%m-%d")
        list_of_ts = PyAnalyticsApi.create_list_of_ts_api_defs(item_ids=item_ids, item_type=item_type,
                                                               measure_name=measure_name, measure_period=measure_period,
                                                               data_type=data_type, day=day_dt)
        df = build_df_from_apidef_list(list_of_ts, self.api_wrapper)
        selection = alt.selection_multi(fields=['item_id'])
        color = alt.condition(selection,
                              alt.Color('item_id:N', legend=None),
                              alt.value('lightgray'))
        plot = alt.Chart(df).mark_line().encode(
            x='timestamp:Q',
            y=measure_name + ':Q',
            color=color
        ).properties(width=self.plot_width, height=self.plot_height)
        legend = alt.Chart(df).mark_point().encode(
            y=alt.Y('item_id:N', axis=alt.Axis(orient='right')),
            color=color
        ).add_selection(selection)
        return plot | legend

    def line_plot_item_data_with_df(self, day: str, predictors: pd.DataFrame, truth_values: pd.Series,
                                    prediction_model: object, measure_period: int, horizon: int, data_types: List):
        """
        A line plot of different types of data for one item during a given day.
        This one should be use when we do not have a valid PyAnalyticsApi because we have not trained models
        in any Predictive Analytics Instance. This is typical when we are experimenting with
        new data in a notebook. In this case we will need the DataFrame with the predictors, the truth values
        and the trained sklearn prediction model to be able to calculate patterns, predictions and the real values.
        The method is static since it can be used without creating any AnalyticsPlotter instance at all
        :param day: a day in the format of YYYY-mm-dd
        :param predictors:
        :param truth_values:
        :param prediction_model: An sklearn model that has a predict method
        :param measure_period: The measure period used. It should be the same as in the truth_values and the predictors
        :param data_types: The different data types that we want to use. Options are ['real', 'forecast', 'normal']
        :return:
        """
        date_rng = pd.date_range(start=day + ' 00:00:00', end=day + ' 23:59:00',
                                 freq=str(measure_period) + 'min')
        data = []
        if 'real' in data_types:
            real_values = truth_values[day]
            data.append(pd.DataFrame({'real_values': real_values.reindex(date_rng)}))
        if 'normal' in data_types:
            only_hours = truth_values.index.to_series().apply(lambda x: x.strftime("%H:%M")).apply(
                lambda x: datetime.strptime(x, "%H:%M"))
            average_df = pd.DataFrame(truth_values)
            average_df['only_hours'] = only_hours.dt.round('15min')
            # group only by the hours and take the second column through iloc which is the mean value across the groups
            normal_values = average_df.groupby('only_hours').describe().iloc[:, 1]
            data.append(
                pd.DataFrame({'normal_values': normal_values}).set_index(truth_values[day].index).reindex(date_rng))
        if 'forecast' in data_types:
            pred_values = prediction_model.predict(predictors[day])
            data.append(pd.DataFrame({'forecast_values': pred_values}).set_index(
                predictors[day].index).reindex(date_rng.shift(horizon, str(measure_period) + 'min')))
        plot_df = pd.concat(data, axis=1)
        plot_df = pd.melt(plot_df.reset_index(), value_vars=['normal_values', 'forecast_values', 'real_values'],
                          id_vars='index')
        palette = {'normal_values': 'g', 'forecast_values': 'r', 'real_values': 'b'}
        ax = sns.lineplot(x="index", y="value", hue="variable", palette=palette, data=plot_df, marker="o")
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        ax.tick_params(labelrotation=45)
        ax.minorticks_on()
        ax.grid(which='major', linestyle='-', color='red')
        ax.grid(which='minor', linestyle=':', color='black')
        if 'forecast' and 'real' in data_types:
            at = AnchoredText('MAE: ' + str(round(mean_absolute_error(real_values, pred_values), 3)),
                              loc='upper left', prop=dict(size=8), frameon=True,
                              )
            ax.add_artist(at)
        return ax, plot_df

    def line_plot_item_data_with_analytics(self, day: str, item_id: int, item_type: str, measure: str,
                                           measure_period: int, horizon: int, data_types: List):
        """
        A line plot of different types of data for one item during a given day.
        This one should be use when we have a valid PyAnalyticsApi because it's connected to a Predictive Analytics
        Instance. This is typical when we want to quickly generate plots with the results of a trained Analytics
        instance. As parameters we only need the data needed by the Analytics API (itemID, itemType, measure, etc..)
        :param day: a day in the format of YYYY-mm-dd
        :param item_id:
        :param item_type:
        :param measure:
        :param measure_period:
        :param horizon:
        :param data_types:
        :return:
        """
        date_rng = pd.date_range(start=day + ' 00:00:00', end=day + ' 23:59:00',
                                 freq=str(measure_period) + 'min')
        day_str_api = datetime.strptime(day, "%Y-%m-%d").strftime("%Y%m%d%")
        data = []
        # These three ifs could be done through a loop in the list data_types. We leave it like this for readability
        if 'real' in data_types:
            real_values = self.api_wrapper.get_day_ts_for_item(item_id, item_type, measure, measure_period, 'real',
                                                               day=day_str_api)
            data.append(pd.DataFrame({'real_values': real_values}).set_index(
                date_rng))  # I guess that if the real data is missing it returns NaN
        if 'normal' in data_types:
            normal_values = self.api_wrapper.get_day_ts_for_item(item_id, item_type, measure, measure_period, 'normal',
                                                                 day=day_str_api)
            data.append(pd.DataFrame({'normal_values': normal_values}).set_index(date_rng))
        if 'forecast' in data_types:
            forecast_values = self.api_wrapper.get_day_ts_for_item(item_id, item_type, measure, measure_period,
                                                                   'forecasth', horizon=horizon, day=day_str_api)
            data.append(pd.DataFrame({'forecast_values': forecast_values}).set_index(date_rng))
        plot_df = pd.concat(data, axis=1)
        plot_df = pd.melt(plot_df.reset_index(), value_vars=['normal_values', 'forecast_values', 'real_values'],
                          id_vars='index')
        ax = sns.lineplot(x="index", y="value", hue="variable", style="variable", data=plot_df), plot_df
        return ax, plot_df

    # Some of these plots are going to be similar but we will keep them together in case their implementations and
    # aestethics differ in the future
    def bar_plot_data_distribution_by_month(self, table: str, measure: str):
        query = "select DATE_PART(\'MONTH\', start_date) as month, DATE_PART(\'YEAR\', start_date) as year, count(*) from public.{0} where {1} is not null group by month, year".format(
            table, measure)
        year_and_month_count_links = self.timeseries_etl.dao.execute_query(query)
        ax = sns.catplot(x='month', y='count', hue='year', data=year_and_month_count_links, kind='bar', palette='muted')
        if ax.axes[0][0].get_yticks()[-1] > 20000:
            new_axes = ['{:,.0f}'.format(x) + 'K' for x in ax.axes[0][0].get_yticks() / 1000]
            ax.set_yticklabels(new_axes)
        return ax, year_and_month_count_links

    def bar_plot_item_distribution_by_month(self, table: str, measure: str):
        query = "select DATE_PART(\'MONTH\', start_date) as month, DATE_PART(\'YEAR\', start_date) as year, count(distinct item_id) from public.{0} where {1} is not null group by month, year".format(
            table, measure)
        year_and_month_distinct_items = self.timeseries_etl.dao.execute_query(query)
        ax = sns.catplot(x='month', y='count', hue='year', data=year_and_month_distinct_items, kind='bar',
                         palette='muted')
        if ax.axes[0][0].get_yticks()[-1] > 20000:
            new_axes = ['{:,.0f}'.format(x) + 'K' for x in ax.axes[0][0].get_yticks() / 1000]
            ax.set_yticklabels(new_axes)
        return ax, year_and_month_distinct_items

    def density_plot_items_with_ndatapoints(self, table: str):
        query = "select count(*), item_id from  public.{0} group by item_id order by count".format(table)
        item_by_ndata = self.timeseries_etl.dao.execute_query(query)
        ax = sns.distplot(item_by_ndata['count'], kde=False, rug=True)
        return ax, item_by_ndata

    def density_plot_measure(self, table: str, measure: str):
        # We have to use a barplot instead of a density plot because the density calculation is done in the DB side with
        # the following query. It would be too expensive to bring all the data and calculate the density in Python
        query = "select count(*), {1} from public.{0} group by {1}".format(table, measure)
        measure_distribution = self.timeseries_etl.dao.execute_query(query)
        ax = sns.barplot(x=measure_distribution[measure], y=measure_distribution['count'], palette="Blues_d")
        i = 0
        # show ticks every nsteps. The number of steps is going to be calculated in a way that there will always be 30 ticks
        nticks = 30
        nsteps = round(len(ax.xaxis.get_ticklabels())/nticks)
        for label in ax.xaxis.get_ticklabels():
            if i % nsteps == 0:
                label.set_visible(True)
                label.set_rotation(45)
            else:
                label.set_visible(False)
            i += 1
        return ax, measure_distribution

    def item_profile(self, item_id : int, measure: str, table: str):
        query = "select DATE_TRUNC('minute', start_date) as ts, {1}, item_id from public.{2} where item_id={0}".format(
            item_id, measure, table)
        values_by_ts = self.timeseries_etl.dao.execute_query(query)
        values_by_ts['truncated_ts'] = values_by_ts['ts'].apply(lambda x: x.strftime("%H:%M")).apply(
            lambda x: datetime.strptime(x, "%H:%M"))
        values_by_ts['truncated_ts'] = values_by_ts['truncated_ts'].dt.round('15min').apply(lambda x: x.strftime("%H:%M"))
        ax = sns.boxplot(x="truncated_ts", y=measure, data=values_by_ts)
        i = 0
        # show ticks every nsteps. The number of steps is going to be calculated in a way that there will always be 30 ticks
        nticks = 30
        nsteps = round(len(ax.xaxis.get_ticklabels())/nticks)
        for label in ax.xaxis.get_ticklabels():
            if (i % nsteps) == 0:
                label.set_visible(True)
                label.set_rotation(45)
            else:
                label.set_visible(False)
            i += 1
        return ax, values_by_ts

    def bar_plot_holes_by_month(self, table: str, measure: str, measure_period: int, items : List = None):
        query = "select min(start_date) as minimum_date, max(start_date) as maximum_date from public.{0} ".format(table)
        if items is not None:
            str_items = [str(i) for i in items]
            query += "where item_id in ({0})".format(', '.join(str_items))
        min_max_df = self.timeseries_etl.dao.execute_query(query)
        minimum_d = str(min_max_df['minimum_date'][0])
        maximum_d = str(min_max_df['maximum_date'][0])
        x_part = "select DATE_PART(\'MONTH\', start_date) as month, DATE_PART(\'YEAR\', start_date) as year, count(*) as cuenta, item_id " \
                 "from public.{0} where {1} is not null " \
                 "and start_date > \'{2}\' and start_date < \'{3}\' ".format(table, measure, minimum_d, maximum_d)
        if items is not None:
            x_part += "and item_id in ({0}) ".format(', '.join(str_items))
        x_part += "group by month, year, item_id"
        query = "select z.month_y, z.year_y, sum(z.dif) from \
        (select x.item_id, x.year as year_x, y.year as year_y, x.month as month_x, y.month as month_y, x.cuenta, y.cuenta_cal, y.cuenta_cal - x.cuenta as dif from \
        ({3}) as x right join \
        (select count(*) as cuenta_cal, DATE_PART(\'MONTH\', ts) as month, DATE_PART(\'YEAR\', ts) as year from \
        (select ts from \
        ( \
        SELECT \'{0}\'::TIMESTAMP as tm \
        UNION \
        SELECT \'{1}\'::TIMESTAMP as tm \
        ) as t \
        TIMESERIES ts as \'{2} minutes\' OVER (ORDER BY tm)) as cal group by month, year) as y \
        on y.month = x.month and x.year = y.year) as z \
        group by z.month_y, z.year_y".format(minimum_d, maximum_d, measure_period, x_part)
        holes_by_month = self.timeseries_etl.dao.execute_query(query)
        ax = sns.catplot(x='month_y', y='sum', hue='year_y', data=holes_by_month, kind='bar', palette='muted')
        if ax.axes[0][0].get_yticks()[-1] > 20000:
            new_axes = ['{:,.0f}'.format(x) + 'K' for x in ax.axes[0][0].get_yticks() / 1000]
            ax.set_yticklabels(new_axes)
        return ax, holes_by_month


