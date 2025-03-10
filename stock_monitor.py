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
            .hidden-data {{ display: none; font-size: 10px; color: gray; }}
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

    hidden_data = "<div class='hidden-data'><h3>📊 数据调试信息（隐藏）</h3>"

    for index, row in stock_list.iterrows():
        ticker = row['Ticker']
        title = row['Title']
        target_price = row['Target Price']
        stock_type = row['Type'].strip().lower()

        stock = yf.Ticker(ticker)
        stock_info = stock.info
        currency = stock_info.get("currency", "N/A")

        # 收盘价
        latest_close = stock_info.get("regularMarketPrice", 0)
        latest_close_str = f"{latest_close:.2f} {currency}"

        # 直接从 Yahoo Finance 获取 1 天涨跌幅
        one_day_change = stock_info.get("regularMarketChangePercent", 0)

        # 计算 1 周、1 个月、3 个月涨跌幅
        def calculate_change(hist, period_name):
            if not hist.empty:
                first_valid_date = hist.first_valid_index()
                if first_valid_date is not None:
                    first_close = hist.loc[first_valid_date, "Close"]
                    return ((latest_close - first_close) / first_close) * 100
            return 0

        # 获取历史数据
        hist_7d = stock.history(period="7d").asfreq('B')
        hist_1mo = stock.history(period="1mo").asfreq('B')
        hist_3mo = stock.history(period="3mo").asfreq('B')

        one_week_change = calculate_change(hist_7d, "7d")
        one_month_change = calculate_change(hist_1mo, "1mo")

        if stock_type == "stock":
            three_month_change = stock_info.get("fiftyDayAverageChangePercent", 0)  # 股票指数用 Yahoo Finance 数据
        else:
            three_month_change = calculate_change(hist_3mo, "3mo")  # 货币对计算 3 个月涨跌幅

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

        # **隐藏调试数据**
        hidden_data += f"""
        <p><b>{title} ({ticker})</b></p>
        <ul>
            <li>最新收盘价: {latest_close_str}</li>
            <li>1 天前收盘价: {hist_7d["Close"].iloc[-2] if len(hist_7d) > 1 else "N/A"}</li>
            <li>7 天前收盘价: {hist_7d["Close"].iloc[0] if len(hist_7d) > 1 else "N/A"}</li>
            <li>1 个月前收盘价: {hist_1mo["Close"].iloc[0] if len(hist_1mo) > 1 else "N/A"}</li>
            <li>3 个月前收盘价: {hist_3mo["Close"].iloc[0] if len(hist_3mo) > 1 else "N/A"}</li>
        </ul>
        """

    report_html += """
        </table>
    """

    # **隐藏数据部分**
    report_html += hidden_data + "</div>"

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
