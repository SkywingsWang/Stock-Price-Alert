import yfinance as yf
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd
import os
import datetime
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
    print(f"🔍 发送邮件 - 主题: {subject}")
    print(f"📧 发件人: {EMAIL_ADDRESS}")
    print(f"📧 收件人: {TO_EMAIL_ADDRESS}")
    print(f"📡 SMTP 服务器: {SMTP_SERVER}:{SMTP_PORT}")

    msg = MIMEMultipart("alternative")
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = TO_EMAIL_ADDRESS
    msg['Subject'] = subject

    # 添加纯文本格式（备用）
    text_part = MIMEText(body, "plain")
    msg.attach(text_part)

    # 添加 HTML 格式
    html_part = MIMEText(body_html, "html")
    msg.attach(html_part)

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, TO_EMAIL_ADDRESS, msg.as_string())
        print("✅ 邮件发送成功")
    except Exception as e:
        print(f"❌ 邮件发送失败: {e}")
        raise  # 终止任务

from datetime import datetime, timedelta  # ✅ 直接导入 timedelta

def fetch_stock_data():
    today = datetime.now().strftime("%Y-%m-%d")  # 获取今天的日期

    # 获取 30 天前的日期
    one_month_ago = datetime.today() - timedelta(days=30)  # ✅ 正确使用 timedelta

    # HTML 邮件表头
    report_html = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
            }}
            th, td {{
                padding: 8px;
                text-align: center;
                border-bottom: 1px solid #ddd;
            }}
            th {{
                background-color: #f4f4f4;
            }}
            .positive {{
                color: red;
            }}
            .negative {{
                color: green;
            }}
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
            </tr>
    """

    try:
        for index, row in stock_list.iterrows():
            ticker = row['Ticker']
            title = row['Title']
            target_price = row['Target Price']
            
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1mo")  # 获取过去1个月的数据
            
            if hist.empty or len(hist) < 2:
                print(f"⚠️ 无法获取 {ticker} 的数据")
                continue
            
            # 获取货币单位
            stock_info = stock.info
            currency = stock_info.get("currency", "N/A")  # 获取货币单位
            
            # 获取收盘价
            latest_close = hist['Close'].iloc[-1]
            latest_close_str = f"{latest_close:.2f} {currency}"  # 让收盘价包含货币单位

            one_day_change = ((latest_close - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100 if len(hist) > 1 else 0
            one_week_change = ((latest_close - hist['Close'].iloc[-6]) / hist['Close'].iloc[-6]) * 100 if len(hist) > 6 else 0
            
            # 修正1个月涨跌幅的计算方式
            hist_one_month = hist[hist.index <= one_month_ago]  # ✅ 取 30 天前的最近交易日
            if not hist_one_month.empty:
                first_close = hist_one_month['Close'].iloc[-1]  # 取 30 天前最近的交易日收盘价
                one_month_change = ((latest_close - first_close) / first_close) * 100
            else:
                one_month_change = 0  # 如果没有数据，默认为 0
            
            # 颜色处理（上涨为红色，下降为绿色）
            one_day_color = "positive" if one_day_change > 0 else "negative"
            one_week_color = "positive" if one_week_change > 0 else "negative"
            one_month_color = "positive" if one_month_change > 0 else "negative"

            # HTML 表格格式
            report_html += f"""
            <tr>
                <td>{title}</td>
                <td>{latest_close_str}</td>
                <td>{target_price:.2f}</td>
                <td class="{one_day_color}">{one_day_change:.2f}%</td>
                <td class="{one_week_color}">{one_week_change:.2f}%</td>
                <td class="{one_month_color}">{one_month_change:.2f}%</td>
            </tr>
            """

    except Exception as e:
        report_html += f"<tr><td colspan='6'>❌ 数据获取出错: {e}</td></tr>"

    report_html += """
        </table>
    </body>
    </html>
    """

    return report_html


if __name__ == "__main__":
    print("🚀 开始收集股票数据并发送邮件...")
    stock_report_text, stock_report_html = fetch_stock_data()
    subject = f"📈 每日股票市场报告 - {datetime.now().strftime('%Y-%m-%d')}"
    send_email(subject, stock_report_text, stock_report_html)
