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

    report_html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; font-size: 18px; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 15px; text-align: center; border-bottom: 1px solid #ddd; font-size: 22px; }}
            th {{ background-color: #f4f4f4; font-size: 24px; }}
            .positive {{ color: red; font-weight: bold; }}
            .negative {{ color: green; font-weight: bold; }}
            .highlight {{ font-size: 28px; font-weight: bold; }}
            .index-container {{ display: flex; align-items: center; margin-bottom: 30px; }}
            .index-image {{ flex: 1; text-align: center; }}
            .index-data {{ flex: 1; }}
            .index-data table {{ width: 100%; border: none; }}
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
    
    stock_data = []
    
    for index, row in stock_list.iterrows():
        ticker = row['Ticker']
        title = row['Title']
        stockcharts_ticker = row['StockCharts Ticker']

        stock = yf.Ticker(ticker)
        stock_info = stock.info
        currency = stock_info.get("currency", "N/A")

        latest_close = stock_info.get("regularMarketPrice", 0)
        latest_close_str = f"{latest_close:.2f} {currency}"
        one_day_change = stock_info.get("regularMarketChangePercent", 0)

        def color_class(value):
            return "positive" if value > 0 else "negative"

        report_html += f"""
        <tr>
            <td>{title}</td>
            <td>{latest_close_str}</td>
            <td>{row['Target Price']}</td>
            <td class="{color_class(one_day_change)} highlight">{one_day_change:.2f}%</td>
        </tr>
        """
        
        stock_data.append((title, stockcharts_ticker, latest_close_str, one_day_change))
    
    report_html += "</table>"
    report_html += "<h3>📈 市场趋势</h3>"
    
    headers = {"User-Agent": "Mozilla/5.0"}

    for title, stockcharts_ticker, latest_close_str, one_day_change in stock_data:
        if stockcharts_ticker and stockcharts_ticker != "N/A":
            chart_url = f"https://stockcharts.com/c-sc/sc?s={stockcharts_ticker}&p=D&b=40&g=0&i=0"
            try:
                response = requests.get(chart_url, headers=headers)
                if response.status_code == 200:
                    img_base64 = base64.b64encode(response.content).decode("utf-8")
                    report_html += f"""
                    <div class="index-container">
                        <div class="index-image">
                            <img src="data:image/png;base64,{img_base64}" alt="{title} Chart" style="width: 90%; max-width: 800px;">
                        </div>
                        <div class="index-data">
                            <h4>{title} ({stockcharts_ticker})</h4>
                            <p>收盘价: {latest_close_str}</p>
                            <p class="{color_class(one_day_change)} highlight">1天涨跌: {one_day_change:.2f}%</p>
                        </div>
                    </div>
                    """
            except Exception as e:
                print(f"❌ 图片下载失败: {stockcharts_ticker}, 错误: {e}")
    
    report_html += "</body></html>"
    return report_html


if __name__ == "__main__":
    print("🚀 开始收集股票数据并发送邮件...")
    stock_report_html = fetch_stock_data()
    subject = f"📈 每日股票市场报告 - {datetime.now().strftime('%Y-%m-%d')}"
    send_email(subject, "请查看 HTML 邮件", stock_report_html)
