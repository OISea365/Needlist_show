import streamlit as st
from draw.draw import draw_fig_t, draw_fig_c, show_table
from calculate.calculate import gen_period_list
import pickle


# 设置网页信息
st.set_page_config(
    page_title="挂牌公司财报分析玩具",  # 页面标题
    page_icon=":rainbow:",  # icon
    layout="wide",  # 页面布局
    initial_sidebar_state="auto"  # 侧边栏
)


# 从data文件夹载入data_dict.pkl数据
with open('data_dict.pkl', 'rb') as pkl:
    data = pickle.load(pkl)

# 设置截至日期
end_data = '2022q4'

# 生成时期列表
period_list = gen_period_list('2017q2', end_data)
period_list.sort(reverse=True)

# 设置step1
with st.sidebar:
    step1 = st.radio('Step1：选择分析维度', ('市场概况', '盈利情况', '成本和收益情况', '债务和偿债情况', '投资和融资情况', '其他'), index=1)
    if step1 == '市场概况':
        st.stop()
    elif step1 == '盈利情况':
        step2 = st.radio('Step2：选择指标', ('营业总收入', '归母净利润', '净资产收益率TTM', '销售净利率TTM', '总资产周转率TTM', '权益乘数'), index=0)
    elif step1 == '成本和收益情况':
        step2 = st.radio('Step2：选择指标', ('营业总成本', '成本收入比', '销售毛利率TTM'), index=0)
    elif step1 == '债务和偿债情况':
        step2 = st.radio('Step2：选择指标', ('总体资产负债率', '债务成本'), index=0)
    elif step1 == '投资和融资情况':
        step2 = st.radio('Step2：选择指标', ('购建付现', '筹资现金流入', '现金占资产比重'), index=0)
    elif step1 == '其他':
        step2 = st.radio('Step2：选择指标', ('研发强度', '支付的各项税费和收入比'), index=0)
    step3 = st.radio('Step3：选择一级分类', list(data['营业总收入'].keys()))

col1, col2 = st.columns([3, 7])
with col1:
    option1 = st.selectbox('请选择细分类', data['营业总收入'][step3]['data']['category'].unique().tolist())
    option2 = st.selectbox('请选择季度', period_list)

with col2:
    st.write(f'{step2}——{step3}——{option2}')
    df = show_table(data, step2, step3, option2)
    df_formatted = df.applymap(lambda x: '{:.2f}'.format(x))
    st.dataframe(df_formatted, use_container_width=True)

st.markdown("---")
col3, col4 = st.columns([5, 5])
with col3:
    st.markdown(f'#### {step2}历史走势图（上图为统计值，下图为变化量）')
    check = st.checkbox('显示所有季度')
    if check:
        fig1 = draw_fig_t(data, step2, step3, option1, option2, all_qua=True)
    else:
        fig1 = draw_fig_t(data, step2, step3, option1, option2)
    st.plotly_chart(fig1)
with col4:
    st.markdown(f'#### {step3}各部分对比图')
    fig2 = draw_fig_c(data, step2, step3, end_qua=option2)
    st.plotly_chart(fig2)