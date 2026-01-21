import requests
import json
import numpy as np
from datetime import datetime, timedelta

STOCK_LIST = [
    {"code": "603993.SZ", "name": "科大讯飞"}
]

# 固定API许可证
# LICENSE = "CBD5265D-3CF4-4AFB-AA07-97A761D0E5AF"
# LICENSE = "5BEBFBE4-BE54-4525-91DA-5EC474A35191"
# LICENSE = "877AC725-4D2C-4107-9537-5B1EB5A56E74"
LICENSE = "98BA60DF-D2DB-47CB-A454-2AC16CF968F5"

def analyze_stock(stock):
    """分析单支股票的MACD DIF值（过去两年数据）"""
    api_stock_url = f"https://api.mairuiapi.com/hsstock/history/{stock["code"]}/d/n/{LICENSE}?st=20200101&et=20260120"
    api_macd_url = f"https://api.mairuiapi.com/hsstock/history/macd/{stock["code"]}/d/n/{LICENSE}?st=20200101&et=20260120"
    try:
        resMacd = requests.get(api_macd_url)
        resMacd.raise_for_status()
        macdData = resMacd.json()

        resStock = requests.get(api_stock_url)
        resStock.raise_for_status()
        stockData = resStock.json()
    except Exception as e:
        return None, f"API请求失败: {str(e)}"
    
    # 检查API返回数据是否有效
    if not macdData or not isinstance(macdData, list):
        return None, "macdData API返回数据格式错误"
    

    if not stockData or not isinstance(stockData, list):
        return None, "stockData API返回数据格式错误"
    
    # 检查过滤后的数据是否有效
    if len(stockData) < 2:
        return None, f"数据不足（需要至少2个数据点，当前有{len(stockData)}个）"
    
    # 提取diff值
    diff_values = [item["diff"] for item in macdData]
    stock_values = [item["c"] for item in stockData]
    
    if(len(diff_values) != len(stock_values)):
        return None, f"长度不一致，{len(diff_values)} {len(stock_values)}"
    
    cash = 1000000.0  # 初始本金100万
    position = 0.0     # 持仓数量（股）
    last_buy_price = None  # 记录上一次买入价格
    total_profit = 0.0   # 总收益
      # 模拟交易
     # 打印表头
    print("="*80)
    print(f"{'日期':<10} {'操作':<6} {'价格':<10} {'diff':<10} {'ZScore':<10} {'本次收益':<12} {'总收益':<12}")
    print("-"*80)
    position = 0
    # 逐日计算并执行交易（从索引2开始，即第3个数据点）
    for i in range(200, len(diff_values)):
        # 计算当前zScore（使用前i个历史数据）
        hist_diff = diff_values[:i]  # 历史diff值（0到i-1）
        if len(hist_diff) < 2:
            continue  # 跳过不足2个历史数据的点
        
        mean_diff = np.mean(hist_diff)
        std_diff = np.std(hist_diff)
        if std_diff == 0:  # 避免除以0错误
            continue
            
        current_diff = diff_values[i]
        z_score = (current_diff - mean_diff) / std_diff
        
        # 当前日期和价格
        current_date = stockData[i]['t']
        current_price = stock_values[i]
        
        # 策略执行
        if z_score > 1 and position == 0:  # 买入条件
            # 计算买入股数
            position = cash / current_price
            cash = cash - position * current_price
            last_buy_price = current_price
            
            # 计算总收益（买入后总价值=100万，总收益=0）
            total_profit = cash + position * current_price - 1000000
            
            # 打印买入日志
            print(f"{current_date}  买入   {current_price:<10.2f} {current_diff:<10.4f} {z_score:<10.4f} {0:<12.2f} {total_profit:<12.2f}")
        
        elif z_score < -1 and position > 0:  # 卖出条件
            # 计算本次卖出收益
            if last_buy_price is not None:
                profit_this_trade = (current_price - last_buy_price) * position
            else:
                profit_this_trade = 0
                
            # 卖出操作
            cash += position * current_price
            position = 0.0
            last_buy_price = None
            
            # 计算总收益
            total_profit = cash + position * current_price - 1000000
            
            # 打印卖出日志
            print(f"{current_date}  卖出   {current_price:<10.2f} {current_diff:<10.4f} {z_score:<10.4f} {profit_this_trade:<12.2f} {total_profit:<12.2f}")
    
    # 计算最终收益
    if position != 0:
        # 计算本次卖出收益
        if last_buy_price is not None:
            profit_this_trade = (current_price - last_buy_price) * position
        else:
            profit_this_trade = 0
            
        # 卖出操作
        cash += position * current_price
        position = 0.0
        last_buy_price = None
        
        # 计算总收益
        total_profit = cash + position * current_price - 1000000
        
        # 打印卖出日志
        print(f"{current_date}  卖出   {current_price:<10.2f} {current_diff:<10.4f} {z_score:<10.4f} {profit_this_trade:<12.2f} {total_profit:<12.2f}")
    final_value = cash + position * stock_values[-1]  # 按最后一天收盘价计算
    profit = final_value - 1000000.0
    
    # 打印最终结果
    print("-"*80)
    print(f"最终收益: {profit:.2f} 元")
    print(f"总收益: {total_profit:.2f} 元")
    print("="*80)
    
    return profit, None  # 返回收益和无错误信息
def main():
    for stock in STOCK_LIST:
        result, error = analyze_stock(stock)
        print(f"{result} {error}")

if __name__ == "__main__":
    main()