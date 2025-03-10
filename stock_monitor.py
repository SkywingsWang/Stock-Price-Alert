import yfinance as yf
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd
import os
from datetime import datetime

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
            body {{ font-family: Arial, sans-serif; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 8px; text-align: center; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #f4f4f4; }}
            .positive {{ color: red; }}
            .negative {{ color: green; }}
        </style>
    </head>
    <body>
        <h2>📊 每日股票市场报告 - {today}</h2>
        <table>
            <tr>
                <th>名称</th>
                <th>收盘价</th>
                <th>目标价</th>
                <th>1天涨跌</th>
                <th>1周涨跌</th>
                <th>1个月涨跌</th>
                <th>3个月涨跌</th>
            </tr>
    """

    for index, row in stock_list.iterrows():
        ticker = row['Ticker']
        title = row['Title']
        target_price = row['Target Price']
        stock_type = row['Type'].strip().lower()  # 读取 "Stock" 或 "Forex"

        stock = yf.Ticker(ticker)
        stock_info = stock.info
        currency = stock_info.get("currency", "N/A")

        # 收盘价
        latest_close = stock_info.get("regularMarketPrice", 0)
        latest_close_str = f"{latest_close:.2f} {currency}"

        # 直接从 Yahoo Finance 获取数据
        one_day_change = stock_info.get("regularMarketChangePercent", 0)

        # 计算 1 周、1 个月、3 个月涨跌幅
        def calculate_change(history_data, period):
            if len(history_data) > period:
                old_price = history_data["Close"].iloc[0]
                return ((latest_close - old_price) / old_price) * 100
            return 0

        one_week_change = calculate_change(stock.history(period="7d"), 7)
        one_month_change = calculate_change(stock.history(period="1mo"), 20)  # 大约20个交易日
        if stock_type == "stock":
            three_month_change = stock_info.get("fiftyDayAverageChangePercent", 0)  # 股票指数用 Yahoo Finance 数据
        else:
            three_month_change = calculate_change(stock.history(period="3mo"), 60)  # 货币对计算 3 个月涨跌幅

        # 颜色
        def color_class(value):
            return "positive" if value > 0 else "negative"

        # HTML
        report_html += f"""
        <tr>
            <td>{title}</td>
            <td>{latest_close_str}</td>
            <td>{target_price:.2f}</td>
            <td class="{color_class(one_day_change)}">{one_day_change:.2f}%</td>
            <td class="{color_class(one_week_change)}">{one_week_change:.2f}%</td>
            <td class="{color_class(one_month_change)}">{one_month_change:.2f}%</td>
            <td class="{color_class(three_month_change)}">{three_month_change:.2f}%</td>
        </tr>
        """

    report_html += """
        </table>
    </body>
    </html>
    """

    return report_html

if __name__ == "__main__":
    print("🚀 开始收集股票数据并发送邮件...")
    stock_report_html = fetch_stock_data()
    subject = f"📈 每日股票市场报告 - {datetime.now().strftime('%Y-%m-%d')}"
    send_email(subject, "请查看 HTML 邮件", stock_report_html)
