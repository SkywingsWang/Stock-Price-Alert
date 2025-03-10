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

def send_email(subject, body):
    print(f"🔍 发送邮件 - 主题: {subject}")
    print(f"📧 发件人: {EMAIL_ADDRESS}")
    print(f"📧 收件人: {TO_EMAIL_ADDRESS}")
    print(f"📡 SMTP 服务器: {SMTP_SERVER}:{SMTP_PORT}")

    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = TO_EMAIL_ADDRESS
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            text = msg.as_string()
            server.sendmail(EMAIL_ADDRESS, TO_EMAIL_ADDRESS, text)
        print("✅ 邮件发送成功")
    except Exception as e:
        print(f"❌ 邮件发送失败: {e}")
        raise  # 终止任务

def fetch_stock_data():
    today = datetime.now().strftime("%Y-%m-%d")  # 获取今天的日期
    report = f"📊 **每日股票市场报告 - {today}**\n\n"
    
    # 表头
    report += f"{'Ticker':<8} {'名称':<10} {'收盘价':<10} {'目标价':<10} {'货币':<5} {'1天涨跌':<10} {'1周涨跌':<10} {'1个月涨跌':<10}\n"
    report += "-" * 90 + "\n"

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
            one_day_change = ((latest_close - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100 if len(hist) > 1 else 0
            one_week_change = ((latest_close - hist['Close'].iloc[-6]) / hist['Close'].iloc[-6]) * 100 if len(hist) > 6 else 0
            
            # 修正1个月涨跌幅的计算方式
            first_day_of_month = hist.index[0]  # 获取数据的第一个交易日
            first_close = hist.loc[first_day_of_month, "Close"]
            one_month_change = ((latest_close - first_close) / first_close) * 100 if first_close else 0
            
            # 格式化数据，确保对齐
            report += f"{ticker:<8} {title:<10} {latest_close:>8.2f} {currency:<5} {target_price:>8.2f} {currency:<5} {one_day_change:>8.2f}% {one_week_change:>8.2f}% {one_month_change:>8.2f}%\n"

    except Exception as e:
        report += f"\n❌ 数据获取出错: {e}"

    return report

if __name__ == "__main__":
    print("🚀 开始收集股票数据并发送邮件...")
    stock_report = fetch_stock_data()
    subject = f"📈 每日股票市场报告 - {datetime.now().strftime('%Y-%m-%d')}"
    send_email(subject, stock_report)
