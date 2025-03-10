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

# Email Settings
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
TO_EMAIL_ADDRESS = os.getenv("TO_EMAIL_ADDRESS")

# Read Stock Information CSV
stock_list = pd.read_csv('stock_list.csv')

def send_email(subject, body, body_html):
    print(f"🔍 发送邮件 - 题目: {subject}")
    
    msg = MIMEMultipart("alternative")
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = TO_EMAIL_ADDRESS
    msg['Subject'] = subject

    msg.attach(MIMEText(body, "plain"))  # 纯文本
    msg.attach(MIMEText(body_html, "html"))  # HTML

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, TO_EMAIL_ADDRESS, msg.as_string())
        print("✅ 邮件发送成功")
    except Exception as e:
        print(f"❌ 邮件发送失败: {e}")
        raise

def fetch_stock_data():
    today = datetime.now().strftime("%Y-%m-%d")

    # HTML 头部
    report_html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; font-size: 18px; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 12px; text-align: center; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #f4f4f4; font-size: 20px; }}
            .positive {{ color: red; font-weight: bold; }}
            .negative {{ color: green; font-weight: bold; }}
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
    
    for index, row in stock_list.iterrows():
        ticker = row['Ticker']
        title = row['Title']
        stockcharts_ticker = row['StockCharts Ticker']

        # 处理 `target_price` 为空的情况
        target_price = row['Target Price']
        try:
            target_price = float(target_price) if target_price not in ["N/A", ""] else None
        except ValueError:
            target_price = None

        stock = yf.Ticker(ticker)
        stock_info = stock.info
        currency = stock_info.get("currency", "N/A")

        # 收盘价
        latest_close = stock_info.get("regularMarketPrice", 0)
        latest_close_str = f"{latest_close:.2f} {currency}"

        # 直接从 Yahoo Finance 获取 1 天涨跌幅
        one_day_change = stock_info.get("regularMarketChangePercent", 0)

        # 计算 1 周、1 个月、3 个月涨跌幅
        def calculate_change(hist):
            if not hist.empty:
                first_valid_date = hist.first_valid_index()
                if first_valid_date is not None:
                    first_close = hist.loc[first_valid_date, "Close"]
                    return ((latest_close - first_close) / first_close) * 100
            return 0

        hist_7d = stock.history(period="7d").asfreq('B')
        hist_1mo = stock.history(period="1mo").asfreq('B')
        hist_3mo = stock.history(period="3mo").asfreq('B')

        one_week_change = calculate_change(hist_7d)
        one_month_change = calculate_change(hist_1mo)
        three_month_change = calculate_change(hist_3mo)

        def color_class(value):
            return "positive" if value > 0 else "negative"

        # 处理 `target_price` 为空的情况
        target_price_str = f"{target_price:.2f}" if target_price is not None else "N/A"

        report_html += f"""
        <tr>
            <td>{title}</td>
            <td>{latest_close_str}</td>
            <td>{target_price_str}</td>
            <td class="{color_class(one_day_change)}"><b>{one_day_change:.2f}%</b></td>
            <td class="{color_class(one_week_change)}">{one_week_change:.2f}%</td>
            <td class="{color_class(one_month_change)}">{one_month_change:.2f}%</td>
            <td class="{color_class(three_month_change)}">{three_month_change:.2f}%</td>
        </tr>
        """
    
    report_html += """
        </table>
        <h3>📈 市场趋势图</h3>
    """

    # 使用 Base64 嵌入图片
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    for index, row in stock_list.iterrows():
        stockcharts_ticker = row['StockCharts Ticker']
        title = row['Title']
        
        if stockcharts_ticker and stockcharts_ticker != "N/A":
            chart_url = f"https://stockcharts.com/c-sc/sc?s={stockcharts_ticker}&p=D&b=40&g=0&i=0"
            try:
                response = requests.get(chart_url, headers=headers)
                if response.status_code == 200:
                    # 将图片转换为 Base64
                    img_base64 = base64.b64encode(response.content).decode("utf-8")
                    report_html += f"""
                    <div style="text-align: center; margin: 20px 0;">
                        <h4>{title} ({stockcharts_ticker})</h4>
                        <img src="data:image/png;base64,{img_base64}" alt="{title} Chart" style="width: 80%; max-width: 800px; display: block; margin: auto;">
                    </div>
                    """
                    print(f"✅ 图片嵌入成功: {stockcharts_ticker}")
                else:
                    print(f"❌ 图片下载失败: {stockcharts_ticker}, 状态码: {response.status_code}")
            except Exception as e:
                print(f"❌ 图片下载时出错: {stockcharts_ticker}, 错误: {e}")

    report_html += """
    </body>
    </html>
    """
    
    return report_html

if __name__ == "__main__":
    print("🚀 开始收集股票数据并发送邮件...")
    stock_report_html = fetch_stock_data()
    subject = f"📈 每日股票市场报告 - {datetime.now().strftime('%Y-%m-%d')}"
    send_email(subject, "请查看 HTML 邮件", stock_report_html)
