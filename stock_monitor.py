import yfinance as yf 
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import pandas as pd
import os
from datetime import datetime
import base64

# 邮件设置 - 从环境变量中获取邮件配置信息
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")      # 发送邮件的邮箱地址
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")    # 发送邮件邮箱的密码
SMTP_SERVER = os.getenv("SMTP_SERVER")          # SMTP服务器地址
SMTP_PORT = int(os.getenv("SMTP_PORT"))         # SMTP服务器端口
TO_EMAIL_ADDRESS = os.getenv("TO_EMAIL_ADDRESS") # 接收邮件的邮箱地址

# 读取股票信息CSV文件
stock_list = pd.read_csv('stock_list.csv')

def send_email(subject, body, body_html):
    """
    发送电子邮件函数
    
    参数:
        subject (str): 邮件主题
        body (str): 邮件纯文本内容
        body_html (str): 邮件HTML格式内容
    
    返回:
        无返回值
    """
    print(f"🔍 发送邮件 - 题目: {subject}")
    
    # 创建多部分邮件对象，支持纯文本和HTML两种格式
    msg = MIMEMultipart("alternative")
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = TO_EMAIL_ADDRESS
    msg['Subject'] = subject

    # 添加纯文本和HTML内容
    msg.attach(MIMEText(body, "plain"))  # 纯文本
    msg.attach(MIMEText(body_html, "html"))  # HTML

    try:
        # 连接SMTP服务器并发送邮件
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # 启用TLS加密
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)  # 登录邮箱
            server.sendmail(EMAIL_ADDRESS, TO_EMAIL_ADDRESS, msg.as_string())  # 发送邮件
        print("✅ 邮件发送成功")
    except Exception as e:
        # 发送失败时打印错误信息
        print(f"❌ 邮件发送失败: {e}")
        raise

def fetch_stock_data():
    """
    获取股票数据并生成HTML格式的报告
    
    该函数从Yahoo Finance获取股票数据，包括价格和涨跌幅信息，
    并从StockCharts获取股票走势图，最后生成一个美观的HTML格式报告。
    
    返回:
        str: 包含股票数据的HTML格式报告
    """
    today = datetime.now().strftime("%Y-%m-%d")  # 获取当前日期

    # 创建HTML报告的头部，包含CSS样式
    report_html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; font-size: 18px; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 14px; text-align: center; border-bottom: 1px solid #ddd; font-size: 22px; }}
            th {{ background-color: #f4f4f4; font-size: 24px; font-weight: bold; }}
            .positive {{ color: red; font-weight: bold; }}  /* 正涨幅显示为红色（中国市场习惯） */
            .negative {{ color: green; font-weight: bold; }}  /* 负涨幅显示为绿色 */
            .highlight {{ font-size: 28px; font-weight: bold; }} /* 强调 1 天涨幅 */
            .index-container {{ display: flex; align-items: center; margin: 20px 0; }}
            .index-image {{ flex: 1; text-align: center; }}
            .index-data {{ flex: 1; padding-left: 20px; font-size: 22px; }}
            img {{ width: 90%; max-width: 600px; border: 1px solid #ccc; }}
        </style>
    </head>
    <body>
        <h2>📊 每日股票市场报告 - {today}</h2>
        <table>
            <tr>
                <th>名称</th>
                <th>收盘价</th>
                <th>目标价</th>
                <th><b>1天涨跌</b></th>
                <th>1周涨跌</th>
                <th>1个月涨跌</th>
                <th>3个月涨跌</th>
            </tr>
    """

    # 遍历股票列表，获取每只股票的数据
    for index, row in stock_list.iterrows():
        ticker = row['Ticker']           # Yahoo Finance股票代码
        title = row['Title']             # 股票显示名称
        stockcharts_ticker = row['StockCharts Ticker']  # StockCharts网站的股票代码

        # 处理目标价格为空的情况
        target_price = row['Target Price']
        try:
            target_price = float(target_price) if target_price not in ["N/A", ""] else None
        except ValueError:
            target_price = None

        # 使用yfinance获取股票信息
        stock = yf.Ticker(ticker)
        stock_info = stock.info
        currency = stock_info.get("currency", "N/A")  # 获取货币单位

        # 获取最新收盘价
        latest_close = stock_info.get("regularMarketPrice", 0)
        latest_close_str = f"{latest_close:.2f} {currency}"

        # 直接从Yahoo Finance获取1天涨跌幅
        one_day_change = stock_info.get("regularMarketChangePercent", 0)

        # 定义计算涨跌幅的辅助函数
        def calculate_change(hist):
            """
            计算历史数据的涨跌幅
            
            参数:
                hist (DataFrame): 包含历史价格数据的DataFrame
            
            返回:
                float: 涨跌幅百分比
            """
            if not hist.empty:
                first_valid_date = hist.first_valid_index()
                if first_valid_date is not None:
                    first_close = hist.loc[first_valid_date, "Close"]
                    return ((latest_close - first_close) / first_close) * 100
            return 0

        # 获取不同时间段的历史数据
        hist_7d = stock.history(period="7d").asfreq('B')    # 1周数据，只保留工作日
        hist_1mo = stock.history(period="1mo").asfreq('B')  # 1个月数据
        hist_3mo = stock.history(period="3mo").asfreq('B')  # 3个月数据

        # 计算各时间段的涨跌幅
        one_week_change = calculate_change(hist_7d)
        one_month_change = calculate_change(hist_1mo)
        three_month_change = calculate_change(hist_3mo)

        # 根据涨跌幅确定显示颜色的辅助函数
        def color_class(value):
            """
            根据涨跌幅确定CSS类名
            
            参数:
                value (float): 涨跌幅值
            
            返回:
                str: CSS类名，正值为'positive'，负值为'negative'
            """
            return "positive" if value > 0 else "negative"

        # 处理目标价格为空的情况
        target_price_str = f"{target_price:.2f}" if target_price is not None else "N/A"

        # 将股票数据添加到HTML表格中
        report_html += f"""
        <tr>
            <td>{title}</td>
            <td>{latest_close_str}</td>
            <td>{target_price_str}</td>
            <td class="{color_class(one_day_change)} highlight">{one_day_change:.2f}%</td>
            <td class="{color_class(one_week_change)}">{one_week_change:.2f}%</td>
            <td class="{color_class(one_month_change)}">{one_month_change:.2f}%</td>
            <td class="{color_class(three_month_change)}">{three_month_change:.2f}%</td>
        </tr>
        """

    # 添加市场趋势图部分
    report_html += """
        </table>
        <h3>📈 市场趋势图</h3>
    """

    # 设置请求头，模拟浏览器访问
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    # 遍历股票列表，获取每只股票的走势图
    for index, row in stock_list.iterrows():
        stockcharts_ticker = row['StockCharts Ticker']
        title = row['Title']
        
        # 只处理有StockCharts代码的股票
        if stockcharts_ticker and stockcharts_ticker != "N/A":
            # 构建StockCharts图表URL
            chart_url = f"https://stockcharts.com/c-sc/sc?s={stockcharts_ticker}&p=D&b=40&g=0&i=0"
            try:
                # 获取图表图片
                response = requests.get(chart_url, headers=headers)
                if response.status_code == 200:
                    # 将图片转换为Base64编码，以便嵌入HTML
                    img_base64 = base64.b64encode(response.content).decode("utf-8")
                    # 添加图表和股票详细信息到HTML
                    report_html += f"""
                    <div class="index-container">
                        <div class="index-image">
                            <h4>{title} ({stockcharts_ticker})</h4>
                            <img src="data:image/png;base64,{img_base64}" alt="{title} Chart">
                        </div>
                        <div class="index-data">
                            <p><b>收盘价：</b> {latest_close_str}</p>
                            <p><b>目标价：</b> {target_price_str}</p>
                            <p><b>1天涨跌：</b> <span class="{color_class(one_day_change)} highlight">{one_day_change:.2f}%</span></p>
                            <p><b>1周涨跌：</b> <span class="{color_class(one_week_change)}">{one_week_change:.2f}%</span></p>
                            <p><b>1个月涨跌：</b> <span class="{color_class(one_month_change)}">{one_month_change:.2f}%</span></p>
                            <p><b>3个月涨跌：</b> <span class="{color_class(three_month_change)}">{three_month_change:.2f}%</span></p>
                        </div>
                    </div>
                    """
                    print(f"✅ 图片嵌入成功: {stockcharts_ticker}")
                else:
                    print(f"❌ 图片下载失败: {stockcharts_ticker}, 状态码: {response.status_code}")
            except Exception as e:
                print(f"❌ 图片下载时出错: {stockcharts_ticker}, 错误: {e}")

    # 完成HTML报告
    report_html += """
    </body>
    </html>
    """

    return report_html


if __name__ == "__main__":
    """
    主程序入口
    
    当脚本直接运行时，执行以下步骤：
    1. 收集股票数据
    2. 生成HTML格式报告
    3. 发送邮件
    """
    print("🚀 开始收集股票数据并发送邮件...")
    stock_report_html = fetch_stock_data()  # 获取股票数据并生成HTML报告
    subject = f"📈 每日股票市场报告 - {datetime.now().strftime('%Y-%m-%d')}"  # 设置邮件主题
    send_email(subject, "请查看 HTML 邮件", stock_report_html)  # 发送邮件
