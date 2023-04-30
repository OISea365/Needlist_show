# 本脚本尝试通过pickle格式保存的dataframe将数据持久化
import pandas as pd
import os


def merge_data(end_date: str):
    """
    合并各个季度的数据，最后再与行业、省份等属性数据合并，最后生成截止于某季度末的数据
    """
    name_list = ['2016q2.xlsx', '2016q4.xlsx',
                 '2017q2.xlsx', '2017q4.xlsx',
                 '2018q2.xlsx', '2018q4.xlsx',
                 '2019q2.xlsx', '2019q4.xlsx',
                 '2020q2.xlsx', '2020q4.xlsx',
                 '2021q2.xlsx', '2021q4.xlsx',
                 '2022q2.xlsx', '2022q4.xlsx']

    data = pd.DataFrame()
    path = os.path.abspath(os.path.dirname(os.getcwd()))
    for name in name_list:
        period = name.split('.')[0]
        # 通过一个列表循环把所有文件都读出来，然后修改所有列名，不要读取首行，wind命名格式不规范
        # noinspection PyArgumentList
        data_tmp = pd.read_excel(f'{path}\\data\\oridata\\{name}', header=None, skiprows=[0], index_col=0)

        base_list = ['股票简称', '披露日期', '营业总收入', '归母净利润', '营业总成本',
                     '总资产报酬率TTM', '销售净利率TTM', '销售毛利率TTM', '研发费用', '净资产收益率TTM', '总资产周转率TTM', '权益乘数',
                     '支付的各项税费', '购建付现', '经营现金流净额', '筹资现金流入',
                     '经营现金流入', '投资现金流出', '应收账款', '预付款项', '应付账款', '预收账款', '资产总计', '带息债务',
                     '负债合计', '现金及等价物', '货币资金', '利息支出TTM']
        # 构建multiindex并修改列名
        data_tmp.columns = tuple([(base_list[i], period) for i in range(len(base_list))])  # 生成多层索引，注意一定是tuple

        # 删除多余的列
        data_tmp.drop(columns=[('股票简称', period)], inplace=True)
        # 合并dataframe
        data = pd.concat([data, data_tmp], axis=1)
        print(f'{period} is done.')

    # 把单独的属性变量读取并合并
    # noinspection PyArgumentList
    data_fix = pd.read_excel(f'{path}\\data\\oridata\\attribute.xlsx', header=None, skiprows=[0])
    data_fix.index = data_fix[0]
    data_fix.drop(columns=[0], inplace=True)
    base_list = ['股票简称', '所属分层', '公司属性', '企业规模', '是否专精特新', '证监会行业门类', '证监会行业大类', 'wind一级行业',
                 'wind二级行业', 'wind三级行业', 'wind四级行业', '省份', '挂牌日期', '城市']
    data_fix.columns = tuple([(base_list[i], 'fix') for i in range(len(base_list))])
    data_final = pd.concat([data_fix, data], axis=1, join='inner')
    print('attribute.xlsx is done.')
    # data_date = datetime.now().strftime('%Y-%m-%d')
    data_final.to_pickle(f'{path}\\data\\data_period_end_{end_date}.pkl')
    print(f'data_period_end_{end_date}.pkl is done.')
    return data_final


if __name__ == '__main__':
    data_new = merge_data('2022q4')
