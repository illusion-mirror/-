import requests
import json
import numpy as np
from datetime import datetime, timedelta

STOCK_LIST = [
    {"code": "601888", "name": "中国中免"},
    {"code": "002230", "name": "科大讯飞"},
    {"code": "600363", "name": "联创光电"},
    {"code": "601919", "name": "中远海控"},
    {"code": "000858", "name": "五粮液"},
    {"code": "002027", "name": "分众传媒"},
    {"code": "002223", "name": "鱼跃医疗"},
    {"code": "600329", "name": "达仁堂"},
    {"code": "000538", "name": "云南白药"},
    {"code": "600436", "name": "片仔癀"},
    {"code": "603087", "name": "甘李药业"},
    {"code": "600276", "name": "恒瑞药业"},
    {"code": "603259", "name": "药明康德"},
    {"code": "603171", "name": "税友股份"},
    {"code": "002648", "name": "卫星化学"},
    {"code": "002050", "name": "三花智控"},
    {"code": "002603", "name": "以岭药业"},
    {"code": "600048", "name": "保利地产"},
    {"code": "000099", "name": "中信海直"},
    {"code": "600036", "name": "招商银行"},
    {"code": "002465", "name": "海格通信"},
    {"code": "002371", "name": "北方华创"},
    {"code": "603993", "name": "洛阳钼业"},
    {"code": "002074", "name": "国轩高科"},
    {"code": "002594", "name": "比亚迪  "},
    {"code": "600030", "name": "中信证券"},
    {"code": "603605", "name": "珀莱雅  "},
    {"code": "002920", "name": "德赛西威"},
    {"code": "601012", "name": "隆基绿能"},
    {"code": "001696", "name": "宗申动力"},
    {"code": "002085", "name": "万丰奥威"}
]

# 固定API许可证
LICENSE = "CBD5265D-3CF4-4AFB-AA07-97A761D0E5AF"
# LICENSE = "5BEBFBE4-BE54-4525-91DA-5EC474A35191"
# LICENSE = "877AC725-4D2C-4107-9537-5B1EB5A56E74"
# LICENSE = "98BA60DF-D2DB-47CB-A454-2AC16CF968F5"

def analyze_stock(stock):
    """分析单支股票的MACD DIF值（过去两年数据）"""
    # 构造API URL（不使用st和et参数）
    api_url = f"https://api.mairuiapi.com/hszbl/macd/{stock['code']}/d/{LICENSE}"
    # api_url = f"https://api.mairuiapi.com/hsindex/history/macd/{stock['code']}/d/{LICENSE}"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        return None, f"API请求失败: {str(e)}"
    
    # 检查API返回数据是否有效
    if not data or not isinstance(data, list):
        return None, "API返回数据格式错误"
    
    # 获取当前日期并计算过去两年的起始日期
    current_date = datetime.now()
    two_years_ago = current_date - timedelta(days=365)
    
    # 过滤过去两年的数据
    filtered_data = []
    for item in data:
        try:
            date_str = item["t"]
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            if date_obj >= two_years_ago:
                filtered_data.append(item)
        except (ValueError, TypeError):
            continue
    
    # 检查过滤后的数据是否有效
    if len(filtered_data) < 2:
        return None, f"数据不足（需要至少2个数据点，当前有{len(filtered_data)}个）"
    
    # 提取diff值
    diff_values = [item["diff"] for item in filtered_data]
    
    # 计算统计值
    mean_diff = np.mean(diff_values)
    std_diff = np.std(diff_values)
    
    # 获取当前diff值
    current_diff = diff_values[-1]
    
    # 计算Z-score
    z_score = (current_diff - mean_diff) / std_diff
    
    # 计算推荐值
    buy_diff = mean_diff + std_diff
    sell_diff = mean_diff - std_diff
    
    return {
        "code": stock["code"],
        "name": stock["name"],
        "current_diff": current_diff,
        "z_score": z_score,
        "buy_diff": buy_diff,
        "sell_diff": sell_diff
    }, None

def main():
    print("="*80)
    print("MACD DIF值分析报告 (过去一年数据)")
    print(f"分析日期: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"分析时间范围:{(datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')} - {{datetime.now().strftime('%Y-%m-%d')}}")
    print("="*80)
    # 使用固定宽度格式化确保对齐
    header = f"{'股票代码'}\t {'股票名称'} \t {'当前DIF'} \t {'Z-score'} \t {'推荐买入'} \t {'推荐卖出'}"
    print(header)
    print("-" * len(header))
    for stock in STOCK_LIST:
        result, error = analyze_stock(stock)
        
        if error:
            # 错误行也使用相同宽度对齐
            print(f"{stock['code']}\t\t | {stock['name']}\t | {'N/A'}\t\t | {'N/A'}\t\t | {'N/A'}\t\t | {'N/A'}\t\t | {error}")
        else:
            print(f"{result['code']}\t\t | {result['name']}\t | {result['current_diff']:.2f}\t\t | {result['z_score']:.2f}\t\t | {result['buy_diff']:.2f}\t\t | {result['sell_diff']:.2f}") 
    print("="*80)
    print("分析完成！")

if __name__ == "__main__":
    main()