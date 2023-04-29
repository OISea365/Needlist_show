import pandas as pd
from pandas import DataFrame
import time
import os


def load_data(period: str):
    """
    读取数据并降维
    """
    # path = os.path.abspath(os.path.dirname(os.getcwd()))
    data_read = pd.read_pickle(f'data\\data_period_end_{period}.pkl')
    # multiindex降维,多层索引麻烦确实比较多
    data_read.columns = [col[0] if col[1] == 'fix' else '_'.join(col) for col in data_read.columns.values]
    return data_read


def gen_period_list(startdate, enddate: str):
    """
    生成时期列表
    """
    period_list = pd.period_range(startdate, enddate, freq='q').strftime('%Fq%q').tolist()
    # 从period中剔除q3和q1
    period_list = [period for period in period_list if 'q3' not in period and 'q1' not in period]
    return period_list


# noinspection DuplicatedCode
def yoy(
        data_name: DataFrame | None = None,
        indicators: list[str] | None = None,
        periods: list[str] | None = None,
        categories: dict | None = None,
        method: str | None = None,
) -> dict:
    """
    计算同比增长情况.

    Parameters
    ----------
    data_name: DataFrame类
    indicators : str形式的要计算的指标名称
    periods : list[str]形式的日期。表示要计算的期间列表。例如2020q4表示计算2020年相较于2019年的同比增长率
    categories : list[str]分类列表
    method : str类型的计算方法，可取'总和'、'中位数'、'均值'
    :rtype: dict
    """

    result_dict = {}
    for indicator in indicators:
        time1 = time.time()
        result_dict[indicator] = {}

        for key_1, value_1 in categories.items():
            for key_2, value_2 in categories[key_1].items():
                result_dict[indicator][key_2] = {}
                data_dataframe = pd.DataFrame()
                if '_非金融' in key_2:
                    data_sub1 = data_name[data_name['证监会行业门类'] != '金融业']
                else:
                    data_sub1 = data_name

                for key_3, value_3 in categories[key_1][key_2].items():
                    if key_1 == '切片':
                        key = key_2.split('_')[0]
                        data_sub2 = data_sub1[data_sub1[key] == value_3]
                    elif key_1 == 'query':
                        data_sub2 = data_sub1.query(value_3)
                    list_num, list_statistic, list_change = [], [], []

                    for period in periods:
                        period_pre = str(int(period[:4]) - 1) + str(period[4:])
                        data_sub = data_sub2.loc[:, [f'{indicator}_{period}', f'{indicator}_{period_pre}']].dropna()
                        data_sub_real = data_sub2.loc[:, [f'{indicator}_{period}']].dropna()
                        if data_sub.empty:
                            num_sample, statistics, growth = None, None, None
                        else:
                            # num_sample = data_sub.shape[0]  # 样本数
                            num_sample_real = data_sub_real.shape[0]  # 当年不缺失样本数
                            if method == '总和':
                                statistics = round(data_sub[f'{indicator}_{period}'].sum(), 2)
                                statistics_real = round(data_sub_real[f'{indicator}_{period}'].sum(), 2)
                                if data_sub[f'{indicator}_{period_pre}'].sum() > 0:
                                    growth = data_sub[f'{indicator}_{period}'].sum() / data_sub[f'{indicator}_{period_pre}'].sum() - 1
                                    growth = round(growth * 100, 2)
                                else:
                                    growth = None
                            elif method == '中位数':
                                # statistics = round(data_sub[f'{indicator}_{period}'].median(), 2)
                                statistics_real = round(data_sub_real[f'{indicator}_{period}'].median(), 2)
                                growth = data_sub[f'{indicator}_{period}'].median() - data_sub[f'{indicator}_{period_pre}'].median()
                                growth = round(growth, 2)
                            else:
                                # statistics = round(data_sub[f'{indicator}_{period}'].mean(), 2)
                                statistics_real = round(data_sub_real[f'{indicator}_{period}'].mean(), 2)
                                growth = data_sub[f'{indicator}_{period}'].mean() - data_sub[f'{indicator}_{period_pre}'].mean()
                                growth = round(growth, 2)
                        list_num.append(num_sample_real)
                        # list_num_real.append(num_sample_real)
                        list_statistic.append(statistics_real)
                        # list_statistic_real.append(statistics_real)
                        list_change.append(growth)

                    pd_dict = DataFrame.from_dict({'quarter': periods, 'category': [key_3] * len(list_num), 'num': list_num, 'statistic': list_statistic, 'growth': list_change})
                    data_dataframe = pd.concat([data_dataframe, pd_dict])

                result_dict[indicator][key_2]['data'] = data_dataframe
                if method == '总和':
                    result_dict[indicator][key_2]['statistic_unit'] = '总和/亿元'
                    result_dict[indicator][key_2]['growth_unit'] = '百分比'
                else:
                    result_dict[indicator][key_2]['statistic_unit'] = '比例值'
                    result_dict[indicator][key_2]['growth_unit'] = '同比变化点数'

        time2 = time.time()
        print(f'计算{indicator}：耗时{round(time2 - time1, 2)}秒')
    return result_dict


def yoy2(
        data_name: DataFrame | None = None,
        indicator_dict: dict | None = None,
        periods: list[str] | None = None,
        categories: dict | None = None
) -> dict:

    """
    计算同比增长情况.

    Parameters
    ----------
    data_name: DataFrame类
    indicator : str形式的要计算的指标名称
    base_indicator : list[str]形式的指标名称，用于计算indicator的基础指标（相除关系），最大元素个数为2，分子在前，分母在后
    periods : list[str]形式的日期。表示要计算的期间列表。例如2020q4表示计算2020年相较于2019年的同比增长率
    categories : list[str]分类列表，表示某些特定类别的公司，应以0-1标识。例如 classification='专精特新'，是专精特新为1，否则为0
    :rtype: DataFrame
    """

    result_dict = {}
    for indicator, base_indicators in indicator_dict.items():
        time1 = time.time()
        result_dict[indicator] = {}

        for key_1, value_1 in categories.items():
            for key_2, value_2 in categories[key_1].items():
                result_dict[indicator][key_2] = {}
                data_dataframe = pd.DataFrame()
                if '_非金融' in key_2:
                    data_sub1 = data_name[data_name['证监会行业门类'] != '金融业']
                else:
                    data_sub1 = data_name

                for key_3, value_3 in categories[key_1][key_2].items():
                    if key_1 == '切片':
                        key = key_2.split('_')[0]
                        data_sub2 = data_sub1[data_sub1[key] == value_3]
                    elif key_1 == 'query':
                        data_sub2 = data_sub1.query(value_3)
                    list_num, list_statistic, list_change = [], [], []

                    for period in periods:
                        period_pre = str(int(period[:4]) - 1) + str(period[4:])
                        check_list0 = [f'{base_indicators[0]}_{period}', f'{base_indicators[1]}_{period}']
                        check_list1 = [f'{base_indicators[0]}_{period_pre}', f'{base_indicators[1]}_{period_pre}']
                        data_sub3 = data_sub2.loc[:, check_list0].dropna()
                        data_sub4 = data_sub2.loc[:, check_list1].dropna()
                        if data_sub3.empty or data_sub4.empty:
                            num_sample, statistics, growth = None, None, None
                        else:
                            data_sub00 = data_sub3[check_list0]
                            data_sub11 = data_sub4[check_list1]
                            num_sample = data_sub00.shape[0]  # 样本数
                            if data_sub00[f'{base_indicators[1]}_{period}'].sum() == 0 or data_sub11[f'{base_indicators[1]}_{period_pre}'].sum() == 0:
                                statistics, growth = None, None
                            else:
                                statistics0 = data_sub00[f'{base_indicators[0]}_{period}'].sum() / data_sub00[f'{base_indicators[1]}_{period}'].sum()
                                statistics1 = data_sub11[f'{base_indicators[0]}_{period_pre}'].sum() / data_sub11[
                                    f'{base_indicators[1]}_{period_pre}'].sum()
                                statistics = round(statistics0 * 100, 2)
                                growth = round((statistics0 - statistics1) * 100, 2)
                        list_num.append(num_sample)
                        list_statistic.append(statistics)
                        list_change.append(growth)
                    pd_dict = DataFrame.from_dict({'quarter': periods, 'category': [key_3] * len(list_num), 'num': list_num, 'statistic': list_statistic, 'growth': list_change})
                    data_dataframe = pd.concat([data_dataframe, pd_dict])
                result_dict[indicator][key_2]['data'] = data_dataframe
                result_dict[indicator][key_2]['statistic_unit'] = '比例值'
                result_dict[indicator][key_2]['growth_unit'] = '同比变化点数'
        time2 = time.time()
        print(f'计算{indicator}：耗时{round(time2 - time1, 2)}秒')
    return result_dict
