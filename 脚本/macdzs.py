import requests
import json
import numpy as np
from datetime import datetime, timedelta

STOCK_LIST = [
{
"code": "000001.SH",
"name": "上证指数"
},
{
"code": "000006.SH",
"name": "地产指数"
},
{
"code": "000025.SH",
"name": "180基建"
},
{
"code": "000036.SH",
"name": "上证消费"
},
{
"code": "000037.SH",
"name": "上证医药"
},
{
"code": "000038.SH",
"name": "上证金融"
},
{
"code": "000158.SH",
"name": "上证环保"
},
{
"code": "000680.SH",
"name": "科创综指"
},
{
"code": "000685.SH",
"name": "科创芯片"
},
{
"code": "000688.SH",
"name": "科创50"
},
{
"code": "000913.SH",
"name": "300医药"
},
{
"code": "399006.SZ",
"name": "创业板指"
},
{
"code": "399275.SZ",
"name": "创医药"
},
{
"code": "399283.SZ",
"name": "机器人50"
},
{
"code": "399395.SZ",
"name": "国证有色"
},
{
"code": "399959.SZ",
"name": "军工指数"
},
{
"code": "399437.SZ",
"name": "证券龙头"
},
{
"code": "399971.SZ",
"name": "中证传媒"
},
{
"code": "399284.SZ",
"name": "AI 50"
}
]

# 固定API许可证
LICENSE = "98BA60DF-D2DB-47CB-A454-2AC16CF968F5"
# 5BEBFBE4-BE54-4525-91DA-5EC474A35191
# 877AC725-4D2C-4107-9537-5B1EB5A56E74
# CBD5265D-3CF4-4AFB-AA07-97A761D0E5AF
# 98BA60DF-D2DB-47CB-A454-2AC16CF968F5

def analyze_stock(stock):
    """分析单支股票的MACD DIF值（过去两年数据）"""
    # 构造API URL（不使用st和et参数）
    # api_url = f"https://api.mairuiapi.com/hszbl/macd/{stock['code']}/d/{LICENSE}"
    api_url = f"https://api.mairuiapi.com/hsindex/history/macd/{stock['code']}/d/{LICENSE}"
    # api_url = f"https://api.mairuiapi.com/hsindex/history/macd/000001.SZ/d/CBD5265D-3CF4-4AFB-AA07-97A761D0E5AF?st=20240109&et=20260119"
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
    two_years_ago = current_date - timedelta(days=365*2)
    # 过滤过去两年的数据
    filtered_data = []
    for item in data:
        try:
            date_str = item["t"]
            
            # date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            date_obj = datetime.strptime(item["t"], "%Y-%m-%d %H:%M:%S")
            if date_obj >= two_years_ago:
                filtered_data.append(item)
        except (ValueError, TypeError):
            print("error")
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
    print("MACD DIF值分析报告 (过去两年数据)")
    print(f"分析日期: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"分析时间范围: {datetime.now().strftime('%Y-%m-%d')} - {(datetime.now() - timedelta(days=365*2)).strftime('%Y-%m-%d')}")
    print("="*80)
    # 使用固定宽度格式化确保对齐
    header = f"{'股票代码'}\t {'股票名称'} \t {'当前DIF'} \t {'Z-score'} \t {'推荐买入'} \t {'推荐卖出'}"
    print(header)
    print("-" * len(header))
    for stock in STOCK_LIST:
        result, error = analyze_stock(stock)
        
        if error:
            # 错误行也使用相同宽度对齐
            print(f"{stock['code']}\t | {stock['name']}\t | {'N/A'}\t\t | {'N/A'}\t\t | {'N/A'}\t\t | {'N/A'}\t\t | {error}")
        else:
            print(f"{result['code']}\t | {result['name']}\t {result['current_diff']:.2f}\t\t|{result['z_score']:.1f}\t\t | {result['buy_diff']:.1f}\t\t | {result['sell_diff']:.1f}") 
    print("="*80)
    print("分析完成！")

if __name__ == "__main__":
    main()