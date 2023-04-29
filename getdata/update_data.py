import os
import pandas as pd
from WindPy import w
from datetime import datetime
import openpyxl


def update_data(
    new_db_period: str,
    base_db_period: str
):
    """
    更新数据集
    ----------
    Parameters
    ----------
    new_db_period: '2012q4'类似格式
    base_db_period: '2012q3'类似格式
    """

    # 0.检查输入
    if new_db_period != base_db_period:
        print('现在将进行以下步骤\n'
              f'1.读取{new_db_period}.xlsx的数据--\033[0;31;40m添加\033[0m\n'
              f'2.读取attribute.xlsx的数据--\033[0;31;40m更新\033[0m\n'
              f'3.从wind获取最新股票列表并更新数据--\033[0;31;40m添加\033[0m\n'
              f'4.以上数据都将汇总到data_period_end_{base_db_period}.pkl中')
    else:
        print('现在将进行以下步骤\n'
              f'1.读取{new_db_period}.xlsx的数据--\033[0;31;40m更新\033[0m\n'
              f'2.读取attribute.xlsx的数据--\033[0;31;40m更新\033[0m\n'
              f'3.从wind获取最新股票列表并更新数据--\033[0;31;40m添加\033[0m\n'
              f'4.以上数据都将汇总到data_period_end_{new_db_period}.pkl中')
    while True:
        check = input(f'请至少确保{new_db_period}.xlsx已经下载好，确保excel尾部的\033[0;31;40m数据来源\033[0m已删除，然后输入y：')
        if check == 'y':
            break
        else:
            print('输入错误！')
            continue
    path = os.path.abspath(os.path.dirname(os.getcwd()))
    # 1.预加载所需要的数据
    # 1.1.预加载基础文件和信息
    data_base = pd.read_pickle(f'{path}\\data\\data_period_end_{base_db_period}.pkl')
    data_date = datetime.now().strftime('%Y-%m-%d')  # 当前日期

    # 1.2.预加载指标模板
    # noinspection PyArgumentList
    data_indicator = pd.read_excel(f'{path}\\data\\指标模板.xlsx', header=0)
    list_period = data_indicator[data_indicator['指标类别'] == 'period']['指标中文缩写'].to_list()  # 已有-period指标
    list_fix = data_indicator[data_indicator['指标类别'] == 'fix']['指标中文缩写'].to_list()[1:]  # 已有-fix指标, stkcd要作为index,所以去掉

    # 2.加载新的数据
    # 2.1.读取新一期的period数据——手工下载
    # noinspection PyArgumentList
    data_tmp_1 = pd.read_excel(f'{path}\\data\\oridata\\{new_db_period}.xlsx', header=None, skiprows=[0], index_col=0)
    data_tmp_1.drop(columns=[1], inplace=True)
    data_tmp_1.columns = tuple([(list_period[i], new_db_period) for i in range(len(list_period))])

    # 2.2.读取新一期的fix数据——手工下载
    # noinspection PyArgumentList
    data_tmp_2 = pd.read_excel(f'{path}\\data\\oridata\\attribute.xlsx', header=None, skiprows=[0], index_col=0)
    data_tmp_2.columns = tuple([(list_period[i], 'fix') for i in range(len(list_fix))])

    # 2.3.读取新公司的数据——自动生成、手动更新
    # 2.3.1.获取待更新的的stkcd，同时也生成了待删除的stkcd
    base_stkcd_list = data_base.index.to_list()  # 基础数据集中的stkcd
    w.start()
    new_stkcd_list = w.wset("sectorconstituent", f"date={data_date};sectorid=1000007748000000;field=wind_code", usedf=True)[1]['wind_code'].to_list()
    w.stop()  # 从wind中获取最新的stkcd

    de_list = [x for x in base_stkcd_list if x not in new_stkcd_list]  # 待删除的stkcd，这些公司已经退市
    add_list = [x for x in new_stkcd_list if x not in base_stkcd_list]  # 待更新的stkcd，这些公司是新上市的

    # 2.3.2.自动生成新公司的excel文件
    data_indicator['提数指令'] = data_indicator['提数指令'].apply(lambda x: x.replace('f=', '='))
    dict_fix = data_indicator[data_indicator['指标类别'] == 'fix'].set_index('指标中文缩写').to_dict()['提数指令']
    dict_period = data_indicator[data_indicator['指标类别'] == 'period'].set_index('指标中文缩写').to_dict()['提数指令']

    data_tmp_3 = pd.DataFrame()
    if len(add_list) == 0:
        print('没有新增上市公司')
    else:
        # 调取数据常量
        name_list = os.listdir(f'{path}\\data\\oridata')
        list_period_0 = list_period = [s.replace('.xlsx', '') for s in name_list if '20' in s]  # 同时保留2012q4这种格式和2012-12-31这种格式
        list_period = [s.replace('q1', '-03-31') for s in list_period]
        list_period = [s.replace('q2', '-06-30') for s in list_period]
        list_period = [s.replace('q3', '-09-30') for s in list_period]
        list_period = [s.replace('q4', '-12-31') for s in list_period]

        # 写入excel
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(list(dict_fix.keys()) + [i for i in list(dict_period.keys()) for _ in range(len(list_period))])  # 写入首行
        ws.append(['fix'] * len(dict_fix) + list_period_0 * len(dict_period))  # 写入次行

        for stkcd in add_list:  # 写入数据行
            dict_fix_trans = {key: value.format(stkcd=stkcd, end_date=data_date) for key, value in dict_fix.items()}
            list2 = []
            for period in list_period:
                dict_period_trans = {key: value.format(stkcd=stkcd, period=period) for key, value in dict_period.items()}
                list2.append(list(dict_period_trans.values()))
            list3 = [j[i] for i in range(len(list2[0])) for j in list2]
            row = list(dict_fix_trans.values()) + list3
            ws.append(row)
        wb.save(f'{path}\\data\\new_company_{data_date}.xlsx')
        print('------------------------------------')
        print(f'new_company_{data_date}.xlsx数据完成写入！请打开文件和wind进行数据刷新！')
        while True:
            check = input('数据刷新完成后，请输入y：')
            if check == 'y':
                break
            else:
                continue
        # noinspection PyArgumentList
        data_tmp_3 = pd.read_excel(f'{path}\\data\\new_company_{data_date}.xlsx', header=[0, 1], index_col=0)

    # 合并dataframe
    """
    两步走：
    1.调整样本数量：剔除del_list公司，增补add_list公司，调整后的样本应该是new_stkcd_list。
    2.更新最新数据
        2.1 如果new_db_date == base_db_period，用update方法
        2.2 如果new_db_date != base_db_period，用concat方法
    """

    # step1
    if len(de_list) == 0 and len(add_list) == 0:
        data = data_base
    elif len(de_list) == 0 and len(add_list) != 0:
        data = pd.concat([data_base, data_tmp_3], axis=0, join='outer')
    elif len(de_list) != 0 and len(add_list) == 0:
        data = data_base.drop(de_list, axis=0)
    else:
        data = data_base.drop(index=de_list, axis=0)
        data = pd.concat([data, data_tmp_3], axis=0, join='inner')

    # step2
    if new_db_period == base_db_period:
        data.update(data_tmp_1)
        data.update(data_tmp_2)
    else:
        data = pd.concat([data, data_tmp_1], axis=1, join='inner')
        data.update(data_tmp_2)

    # 保存数据
    data.to_pickle(f'{path}\\data\\data_period_end_{new_db_period}.pkl')
    print(f'{path}\\data_period_end_{new_db_period}.pkl saved!')
    return data


if __name__ == '__main__':
    data_new = update_data(new_db_period='2022q4', base_db_period='2022q2')
