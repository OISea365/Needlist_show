from calculate.calculate import load_data, gen_period_list, yoy, yoy2
from calculate.categories import get_categories
import pickle

# ----------------------导入常量----------------------
startdate, enddate = '2017q2', '2022q4'  # 起始日期和结束日期
period_list = gen_period_list(startdate, enddate)  # 生成时期列表
data = load_data(enddate)  # 读取数据
category_dict = get_categories(data)  # 获取分类方法

input_yoy_list_sum = ['营业总收入', '归母净利润', '营业总成本', '资产总计',
                      '货币资金', '支付的各项税费', '研发费用', '经营现金流入', '经营现金流净额',
                      '购建付现', '筹资现金流入']  # yoy函数中，用总和法计算的指标

input_yoy_list_median = ['销售毛利率TTM', '净资产收益率TTM', '总资产周转率TTM', '销售净利率TTM',
                         '权益乘数']  # yoy函数中，用中位数法计算的指标

input_yoy2_dict = {'债务成本': ['利息支出TTM', '带息债务'], '经营现金流入占总收入比': ['经营现金流入', '营业总收入'],
                   '研发强度': ['研发费用', '营业总收入'], '支付的各项税费和收入比': ['支付的各项税费', '营业总收入'],
                   '现金占资产比重': ['货币资金', '资产总计'], '总体资产负债率': ['负债合计', '资产总计'],
                   '成本收入比': ['营业总成本', '营业总收入']
                   }    # yoy2函数计算的指标

# ----------------------数据运算----------------------
data_dict = {}
# yoy函数中，用总和法计算的指标
data_dict_sum = yoy(data, indicators=input_yoy_list_sum, periods=period_list, categories=category_dict, method='总和')
# yoy函数中，用中位数法计算的指标
data_dict_median = yoy(data, indicators=input_yoy_list_median, periods=period_list, categories=category_dict, method='中位数')
# yoy2函数计算的指标
data_dict_calcu = yoy2(data, indicator_dict=input_yoy2_dict, periods=period_list, categories=category_dict)

# 合并并保存数据
data_dict.update(data_dict_sum)
data_dict.update(data_dict_median)
data_dict.update(data_dict_calcu)
with open('data_dict.pkl', 'wb') as f:
    pickle.dump(data_dict, f)
