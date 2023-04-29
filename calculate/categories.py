from pandas import DataFrame


def get_categories(
        data_name: DataFrame,
) -> dict:
    """
    根据给定的分类，生成分类字典。
    对于wind行业等固定分类，value值为列表格式。
    对于公司属性(外资等分类归为其他)以及自定义分类，采用query方法，value值为字符串格式。

    Parameters
    ----------
    data_name : DataFrame类，原始数据集
    Returns
    -------
    dict
    """

    result_dict = {'切片': {}, 'query': {}}
    # 类别一：切片法运算的公司
    col_name1 = ['所属分层', '证监会行业门类', 'wind一级行业']
    for col in col_name1:
        list_unique = data_name[col].unique().tolist()
        list_unique_nn = list(filter(None, list_unique))  # 去除空值
        result_dict['切片'][col] = {nn: nn for nn in list_unique_nn}  # 这种字典嵌套的方法虽然啰嗦，但是可以保持字典结构一致
        if col == '所属分层':
            result_dict['切片'][col + '_非金融'] = {nn: nn for nn in list_unique_nn}
        else:
            pass

    # 类别二：query方法运算的公司
    size_dict = {'大型': '企业规模 == "大型"',
                 '中型': '企业规模 == "中型"',
                 '小型': '企业规模 == "小型"',
                 '微型': '企业规模 == "微型"',
                 '中小型': '企业规模 == "中型" | 企业规模 == "小型"'
                 }
    size_dict_not_fin = {'大型_非金融': '企业规模 == "大型"',
                         '中型_非金融': '企业规模 == "中型"',
                         '小型_非金融': '企业规模 == "小型"',
                         '微型_非金融': '企业规模 == "微型"',
                         '中小型_非金融': '企业规模 == "中型" | 企业规模 == "小型"'
                         }
    soe_dict = {'民营企业': '公司属性 == "民营企业"',
                '国有企业': '公司属性 == "中央国有企业" | 公司属性 == "地方国有企业"',
                '中央国有企业': '公司属性 == "中央国有企业"',
                '地方国有企业': '公司属性 == "地方国有企业"',
                '公众企业': '公司属性 == "公众企业"'
                }
    soe_dict_not_fin = {'民营企业_非金融': '公司属性 == "民营企业"',
                        '国有企业_非金融': '公司属性 == "中央国有企业" | 公司属性 == "地方国有企业"',
                        '中央国有企业_非金融': '公司属性 == "中央国有企业"',
                        '地方国有企业_非金融': '公司属性 == "地方国有企业"',
                        '公众企业_非金融': '公司属性 == "公众企业"'
                        }
    custom_dict_not_fin = {'大型民营企业_非金融': '企业规模 == "大型" & 公司属性 == "民营企业"',
                           '中小微民营企业_非金融': f'企业规模 != "大型" & 公司属性 == "民营企业"'
                           }

    result_dict['query']['企业规模'] = size_dict
    result_dict['query']['企业规模_非金融'] = size_dict_not_fin
    result_dict['query']['公司属性'] = soe_dict
    result_dict['query']['公司属性_非金融'] = soe_dict_not_fin
    result_dict['query']['自定义_非金融'] = custom_dict_not_fin

    result_dict['query']['全部挂牌公司'] = {'全部挂牌公司': '股票简称 != ""'}
    result_dict['query']['非金融挂牌公司'] = {'非金融挂牌公司': '证监会行业门类 != "金融业"'}
    return result_dict
