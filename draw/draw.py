from plotly import graph_objects as go
from plotly.subplots import make_subplots
import pickle
from pandas import DataFrame


# ----------------------图表绘制并输出-------------------------------------------------------------------------------------------------------
def draw_fig_t(
        dataname: dict,
        index: str,
        cate: str,
        value: str,
        end_qua: str,
        all_qua: bool = False
):
    """
    绘制历史图表
    :param dataname: 数据字典
    :param index: data_dict的指标
    :param cate: data_dict的分类
    :param value: 具体的分类值
    :param end_qua: 截止季度
    :param all_qua: 是否显示所有季度
    :return: fig对象
    """
    statistic_unit = dataname[index][cate]['statistic_unit']
    growth_unit = dataname[index][cate]['growth_unit']
    df = dataname[index][cate]['data']

    # 截取end_qua字符串的最后两位
    qua = end_qua[-2:]
    df0 = df[df['quarter'] <= end_qua]

    if all_qua is True:
        df_sub = df0[df0['category'] == value]
    else:
        df_sub = df0[(df0['category'] == value) & (df0['quarter'].str.contains(qua))]

    figure = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05)
    trace1 = go.Bar(x=df_sub['quarter'], y=df_sub['statistic'], name=f'{statistic_unit}')
    trace2 = go.Scatter(x=df_sub['quarter'], y=df_sub['growth'], name=f'{growth_unit}', mode='lines+markers')
    figure.add_trace(trace1, row=1, col=1)
    figure.add_trace(trace2, row=2, col=1)
    figure.update_layout(height=600, width=800,
                         title_text=f'{index}——{cate}——{value}',
                         showlegend=False,
                         hovermode='x unified',
                         yaxis=dict(tickformat=',.2f')
                         )
    return figure


def draw_fig_c(
        data_dict: dict,
        index: str,
        cate: str,
        end_qua: str,
):
    """
    绘制历史图表
    :param data_dict: 数据字典
    :param index: data_dict的指标
    :param cate: data_dict的分类
    :param end_qua: 截止季度
    :return: fig对象
    """
    statistic_unit = data_dict[index][cate]['statistic_unit']
    df = data_dict[index][cate]['data']

    df_sub = df[df['quarter'] == end_qua]
    # 根据category分组，对quarter列进行排序，提取每组中最后一个quarter的数据
    df_sub2 = df_sub.sort_values(by=['category', 'quarter'], ascending=True).groupby('category').tail(1)
    df_sub3 = df_sub2.sort_values(by=['statistic'], ascending=True)
    # 使用plotly, 以df_sub3为数据源，根据statistic列的值绘制竖版柱状图,柱状图数值值从大到小排列,横坐标为statistic,横坐标的单位是statistic_unit
    figure = go.Figure(go.Bar(x=df_sub3['statistic'], y=df_sub3['category'],
                              orientation='h', text=df_sub3['statistic']))
    figure.update_layout(title=f'{index}——{cate}——{end_qua}', xaxis_title=statistic_unit, yaxis_title=cate)
    # 在figure中显示数值
    figure.update_traces(textposition='outside', text=df_sub3['statistic'],
                         hovertemplate='<b>%{y}</b><br>数值: %{x:,}<extra></extra>')
    return figure


def show_table(
        dataname: DataFrame,
        index: str,
        cate: str,
        end_qua: str

):
    """
    显示表格
    :param dataname: 数据字典
    :param index: data_dict的指标
    :param cate: data_dict的分类
    :param end_qua: 截止季度
    :return: DataFrame
    """

    df = dataname[index][cate]['data']
    statistic_unit = dataname[index][cate]['statistic_unit']
    growth_unit = dataname[index][cate]['growth_unit']
    df_sub = df[df['quarter'] == end_qua]

    # 对df_sub的列名进行重命名
    df_result = df_sub.copy()
    df_result.sort_values(by=['statistic'], ascending=False, inplace=True)
    if growth_unit == '百分比':
        # 计算statistic列每个值占总值的百分比，生成新列,并保留两位小数
        df_result['统计值占总值的比'] = round(df_result['statistic'] / df_result['statistic'].sum() * 100, 2)
    elif growth_unit == '同比变化点数':
        df_result['统计值与统计值中位数之差'] = round(df_result['statistic'] - df_result['statistic'].median(), 2)
    df_result.rename(columns={'quarter': '季度', 'category': '分类', 'num': '样本数量',
                              'statistic': f'统计值({statistic_unit})', 'growth': f'增长率({growth_unit})'}, inplace=True)
    df_result.reset_index(drop=True, inplace=True)
    df_result.index = df_result.index + 1
    df_result.index.name = '排序'

    return df_result
