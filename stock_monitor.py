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

    # 添加纯文本格式（备用）
    msg.attach(MIMEText(body, "plain"))
    # 添加 HTML 格式
    msg.attach(MIMEText(body_html, "html"))

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
    today = datetime.now().strftime("%Y-%m-%d")  # 获取今天的日期

    # 纯文本格式
    report_text = f"📊 每日市场报告 - {today}\n\n"
    report_text += f"{'名称':<12} {'收盘价':<12} {'目标价':<8} {'1天涨跌':<10} {'1周涨跌':<10} {'1个月涨跌':<10} {'3个月涨跌':<10}\n"
    report_text += "-" * 100 + "\n"

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
                <th>3个月涨跌</th>
            </tr>
    """

    try:
        for index, row in stock_list.iterrows():
            ticker = row['Ticker']
            title = row['Title']
            target_price = row['Target Price']
            stock_type = row['Type'].strip().lower()  # 读取 "Stock" 或 "Forex"

            stock = yf.Ticker(ticker)
            stock_info = stock.info
            currency = stock_info.get("currency", "N/A")

            # 获取收盘价
            latest_close = stock.history(period="1d")["Close"].iloc[-1]
            latest_close_str = f"{latest_close:.2f} {currency}"

            if stock_type == "stock":
                # 直接获取 Yahoo Finance 提供的涨跌幅
                one_day_change = stock_info.get("regularMarketChangePercent", 0)
                one_week_change = stock_info.get("52WeekChange", 0)  # Yahoo 没有 7 天的涨跌幅，这里暂时用 52 周变化
                one_month_change = stock_info.get("fiftyDayAverageChangePercent", 0)
                three_month_change = stock_info.get("twoHundredDayAverageChangePercent", 0)
            else:
                # 仍然手动计算 Forex（货币对）
                hist = stock.history(period="3mo")  
                if len(hist) < 2:
                    print(f"⚠️ 无法获取 {ticker} 的数据")
                    continue

                hist.index = hist.index.tz_localize(None)  # 移除时区
                one_day_change = ((latest_close - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100 if len(hist) > 1 else 0
                one_week_change = ((latest_close - hist['Close'].iloc[-6]) / hist['Close'].iloc[-6]) * 100 if len(hist) > 6 else 0
                one_month_change = ((latest_close - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100 if len(hist) > 20 else 0
                three_month_change = ((latest_close - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100 if len(hist) > 60 else 0

            # 颜色处理
            def color_class(value):
                return "positive" if value > 0 else "negative"

            # 纯文本格式
            report_text += f"{title:<12} {latest_close_str:<12} {target_price:>8.2f} {one_day_change:>8.2f}% {one_week_change:>8.2f}% {one_month_change:>8.2f}% {three_month_change:>8.2f}%\n"

            # HTML 格式
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

    except Exception as e:
        report_text += f"\n❌ 数据获取出错: {e}"
        report_html += f"<tr><td colspan='7'>❌ 数据获取出错: {e}</td></tr>"

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
