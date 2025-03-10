import yfinance as yf
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd
import os
from datetime import datetime, timedelta  # ✅ 正确导入

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

def fetch_stock_data():
    today = datetime.now().strftime("%Y-%m-%d")  # 获取今天的日期

    # 纯文本格式
    report_text = f"📊 每日市场报告 - {today}\n\n"
    report_text += f"{'名称':<10} {'收盘价':<12} {'目标价':<8} {'1周涨跌':<10} {'1个月涨跌':<10} {'3个月涨跌':<10}\n"
    report_text += "-" * 80 + "\n"

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
                <th>1周涨跌</th>
                <th>1个月涨跌</th>
                <th>3个月涨跌</th>
            </tr>
    """

    try:
        for index, row in stock_list.iterrows():
            ticker = row['Ticker']
            title = row['Title']
            target_price = row['Target Price']
            
            stock = yf.Ticker(ticker)
            stock_info = stock.info  # 获取完整的股票信息

            # 获取收盘价
            latest_close = stock_info.get("regularMarketPreviousClose", None)  # 最新收盘价
            currency = stock_info.get("currency", "N/A")  # 货币单位

            # 获取 Yahoo Finance 提供的涨跌幅
            one_week_change = stock_info.get("52WeekChange", 0) * 100  # 1 周涨跌幅
            one_month_change = stock_info.get("52WeekChange", 0) * 100  # 1 个月涨跌幅
            three_month_change = stock_info.get("threeMonthChangePercent", 0) * 100  # 3 个月涨跌幅

            # 处理数据格式
            latest_close_str = f"{latest_close:.2f} {currency}" if latest_close else "N/A"
            target_price_str = f"{target_price:.2f}" if pd.notna(target_price) else "N/A"

            # 颜色处理（涨红跌绿）
            one_week_color = "positive" if one_week_change > 0 else "negative"
            one_month_color = "positive" if one_month_change > 0 else "negative"
            three_month_color = "positive" if three_month_change > 0 else "negative"

            # 纯文本格式
            report_text += f"{title:<10} {latest_close_str:<12} {target_price_str:<8} {one_week_change:>8.2f}% {one_month_change:>8.2f}% {three_month_change:>8.2f}%\n"

            # HTML 格式
            report_html += f"""
            <tr>
                <td>{title}</td>
                <td>{latest_close_str}</td>
                <td>{target_price_str}</td>
                <td class="{one_week_color}">{one_week_change:.2f}%</td>
                <td class="{one_month_color}">{one_month_change:.2f}%</td>
                <td class="{three_month_color}">{three_month_change:.2f}%</td>
            </tr>
            """

    except Exception as e:
        report_text += f"\n❌ 数据获取出错: {e}"
        report_html += f"<tr><td colspan='6'>❌ 数据获取出错: {e}</td></tr>"

    report_html += """
        </table>
    </body>
    </html>
    """

    return report_text, report_html



if __name__ == "__main__":
    print("🚀 开始收集股票数据并发送邮件...")
    stock_report_text, stock_report_html = fetch_stock_data()
    subject = f"📈 每日股票市场报告 - {datetime.now().strftime('%Y-%m-%d')}"
    send_email(subject, stock_report_text, stock_report_html)
