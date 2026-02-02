import requests
import json
import numpy as np
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from tkcalendar import Calendar

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
        
        # 分析日期 (原结束日期)
        ttk.Label(time_frame, text="分析日期:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.analysis_date = ttk.Entry(time_frame, width=12)
        self.analysis_date.grid(row=0, column=3, padx=5, pady=5)
        self.analysis_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # 日期选择按钮
        ttk.Button(time_frame, text="选择日期", command=self.select_date).grid(row=0, column=4, padx=5, pady=5)
        
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
        version_label = ttk.Label(main_frame, text="MACD Analyzer v1.2 | A股日线分析工具 (1年时间窗口)", font=("Arial", 8))
        version_label.pack(side=tk.BOTTOM, pady=5)
    
    def select_date(self):
        """打开日期选择器 - 仅选择分析日期"""
        try:
            # 创建一个临时窗口用于日期选择
            date_window = tk.Toplevel(self.root)
            date_window.title("选择分析日期")
            date_window.geometry("300x200")
            
            # 日期选择器
            ttk.Label(date_window, text="选择分析日期:").pack(pady=5)
            cal = Calendar(date_window, selectmode='day', date_pattern='yyyy-mm-dd')
            cal.pack(padx=10, pady=5)
            
            # 设置默认日期
            cal.set_date(self.analysis_date.get())
            
            def ok():
                self.analysis_date.delete(0, tk.END)
                self.analysis_date.insert(0, cal.get_date())
                date_window.destroy()
            
            ttk.Button(date_window, text="确定", command=ok).pack(pady=10)
        except Exception as e:
            messagebox.showerror("错误", f"日期选择器无法加载: {str(e)}")
    
    def analyze(self):
        """执行MACD分析"""
        stock_code = self.stock_code.get().strip()
        analysis_date = self.analysis_date.get()
        
        # 验证股票代码格式
        if not stock_code or len(stock_code) < 1:
            messagebox.showerror("错误", "请输入股票代码")
            return
        
        # 验证日期格式
        try:
            analysis_date_obj = datetime.strptime(analysis_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("日期错误", "请输入正确的日期格式 (YYYY-MM-DD)")
            return
        
        # 计算开始日期 (分析日期前1年)
        start_date_obj = analysis_date_obj - relativedelta(years=1)
        start_date = start_date_obj.strftime("%Y-%m-%d")
        
        # 构造API URL
        api_url = f"https://api.mairuiapi.com/hsstock/history/macd/{stock_code}/d/f/B61FAD11-CE87-44C0-9C2A-6ABA4877CA11"
        
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
            if start_date <= date <= analysis_date:
                filtered_data.append(item)
        
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
        self.result_text.insert(tk.END, f"分析时间范围: {start_date} 到 {analysis_date} (1年窗口)\n")
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
        self.result_te