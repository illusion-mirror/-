import requests
import json
import numpy as np
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from tkcalendar import Calendar  # 确保已安装tkcalendar

class MACDAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MACD DIF Z-score分析工具 - A股日线")
        self.root.geometry("850x650")
        
        # 创建主框架
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建时间选择区域
        time_frame = ttk.LabelFrame(main_frame, text="时间范围选择", padding="10")
        time_frame.pack(fill=tk.X, pady=5)
        
        # 股票代码输入
        ttk.Label(time_frame, text="股票代码:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.stock_code = ttk.Entry(time_frame, width=12)
        self.stock_code.grid(row=0, column=1, padx=5, pady=5)
        self.stock_code.insert(0, "000001")  # 默认上证指数代码
        
        # 开始日期
        ttk.Label(time_frame, text="开始日期:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.start_date = ttk.Entry(time_frame, width=12)
        self.start_date.grid(row=0, column=3, padx=5, pady=5)
        self.start_date.insert(0, (datetime.now() - relativedelta(years=1)).strftime("%Y-%m-%d"))
        
        # 结束日期
        ttk.Label(time_frame, text="结束日期:").grid(row=0, column=4, sticky=tk.W, padx=5, pady=5)
        self.end_date = ttk.Entry(time_frame, width=12)
        self.end_date.grid(row=0, column=5, padx=5, pady=5)
        self.end_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # 日期选择按钮
        ttk.Button(time_frame, text="选择日期", command=self.select_date).grid(row=0, column=6, padx=5, pady=5)
        
        # 分析按钮
        self.analyze_btn = ttk.Button(main_frame, text="分析MACD DIF值", command=self.analyze)
        self.analyze_btn.pack(pady=10)
        
        # 结果显示区域
        result_frame = ttk.LabelFrame(main_frame, text="分析结果", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.result_text = scrolledtext.ScrolledText(result_frame, wrap=tk.WORD, font=("Consolas", 10))
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.result_text.config(state=tk.DISABLED)
        
        # 添加版本信息
        version_label = ttk.Label(main_frame, text="MACD Analyzer v1.1 | A股日线分析工具", font=("Arial", 8))
        version_label.pack(side=tk.BOTTOM, pady=5)
    
    def select_date(self):
        """打开日期选择器"""
        try:
            # 创建一个临时窗口用于日期选择
            date_window = tk.Toplevel(self.root)
            date_window.title("选择日期")
            date_window.geometry("300x250")
            
            # 日期选择器
            ttk.Label(date_window, text="选择开始日期:").pack(pady=5)
            start_cal = Calendar(date_window, selectmode='day', date_pattern='yyyy-mm-dd')
            start_cal.pack(padx=10, pady=5)
            
            ttk.Label(date_window, text="选择结束日期:").pack(pady=5)
            end_cal = Calendar(date_window, selectmode='day', date_pattern='yyyy-mm-dd')
            end_cal.pack(padx=10, pady=5)
            
            # 设置默认日期
            start_cal.set_date(self.start_date.get())
            end_cal.set_date(self.end_date.get())
            
            def ok():
                self.start_date.delete(0, tk.END)
                self.start_date.insert(0, start_cal.get_date())
                self.end_date.delete(0, tk.END)
                self.end_date.insert(0, end_cal.get_date())
                date_window.destroy()
            
            ttk.Button(date_window, text="确定", command=ok).pack(pady=10)
        except Exception as e:
            messagebox.showerror("错误", f"日期选择器无法加载: {str(e)}")
    
    def analyze(self):
        """执行MACD分析"""
        stock_code = self.stock_code.get().strip()
        start_date = self.start_date.get()
        end_date = self.end_date.get()
        
        # 验证股票代码格式
        if not stock_code or len(stock_code) < 1:
            messagebox.showerror("错误", "请输入股票代码")
            return
        
        # 验证日期格式
        try:
            datetime.strptime(start_date, "%Y-%m-%d")
            datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("日期错误", "请输入正确的日期格式 (YYYY-MM-DD)")
            return
        # B61FAD11-CE87-44C0-9C2A-6ABA4877CA11
        #98BA60DF-D2DB-47CB-A454-2AC16CF968F5
        # 构造API URL
        api_url = f"https://api.mairuiapi.com/hsstock/history/macd/{stock_code}/d/n/B61FAD11-CE87-44C0-9C2A-6ABA4877CA11"
        
        try:
            response = requests.get(api_url)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            messagebox.showerror("API错误", f"请求API失败: {e}")
            return
        except json.JSONDecodeError:
            messagebox.showerror("API错误", "API返回数据格式错误")
            return
        
        # 过滤数据在指定时间范围内的
        filtered_data = []
        for item in data:
            date = item["t"]
        
            if start_date <= date <= end_date:
                if date == end_date:
                    self.result_text.insert(tk.END, f"{data}\n")
                print(f"filter {date}\n")
                filtered_data.append(item)
        print(f"{end_date}\n")
        if not filtered_data:
            messagebox.showinfo("无数据", "在指定时间范围内没有找到数据")
            return
        
        # 提取diff值
        diff_values = [item["diff"] for item in filtered_data]
        
        # 计算统计值
        mean_diff = np.mean(diff_values)
        std_diff = np.std(diff_values)
        
        # 获取当前diff值
        current_diff = diff_values[-1]
        
        # 计算Z-score (a值)
        a_value = (current_diff - mean_diff) / std_diff
        comdiff = mean_diff + std_diff  # 推荐买入值
        sealdiff = mean_diff - std_diff  # 推荐卖出值
        
        # 清除结果文本
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        
        # 格式化输出
        self.result_text.insert(tk.END, "===== MACD DIF Z-score分析报告 =====\n")
        self.result_text.insert(tk.END, f"股票代码: {stock_code}\n")
        self.result_text.insert(tk.END, f"分析时间范围: {start_date} 到 {end_date}\n")
        self.result_text.insert(tk.END, f"数据点数: {len(filtered_data)}\n")
        self.result_text.insert(tk.END, f"DIF均值: {mean_diff:.4f}\n")
        self.result_text.insert(tk.END, f"DIF标准差: {std_diff:.4f}\n")
        self.result_text.insert(tk.END, f"当前DIF值: {current_diff:.4f}\n")
        self.result_text.insert(tk.END, f"当前Z-score (a): {a_value:.4f}\n")
        self.result_text.insert(tk.END, f"推荐买入值: {comdiff:.4f}\n")
        self.result_text.insert(tk.END, f"推荐卖出值: {sealdiff:.4f}\n\n")
        
        # 买入信号判断
        if a_value > 1.0:
            self.result_text.insert(tk.END, "✅ 当前Z-score (a) > 1.0，建议买入\n")
        elif a_value > 0.5:
            self.result_text.insert(tk.END, "⚠️ 当前Z-score (a) > 0.5，可关注\n")
        else:
            self.result_text.insert(tk.END, "❌ 当前Z-score (a) < 0.5，暂不建议买入\n")
        
        # 添加其他参考信号
        self.result_text.insert(tk.END, "\n其他买入参考信号:\n")
        self.result_text.insert(tk.END, "- DIF上穿DEA线（金叉）\n")
        self.result_text.insert(tk.END, "- DIF值从负转正（上穿0轴）\n")
        self.result_text.insert(tk.END, "- MACD柱状图由负转正\n")
        
        # 添加卖出参考信号
        self.result_text.insert(tk.END, "\n卖出参考信号:\n")
        self.result_text.insert(tk.END, "- DIF下穿DEA线（死叉）\n")
        self.result_text.insert(tk.END, "- DIF值从正转负（下穿0轴）\n")
        self.result_text.insert(tk.END, "- MACD柱状图由正转负\n")
        
        self.result_text.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = MACDAnalyzerGUI(root)
    root.mainloop()