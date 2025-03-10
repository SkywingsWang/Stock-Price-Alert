import yfinance as yf
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd
import os

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
    report = "📊 **每日股票市场报告**\n\n"
    report += "Ticker | 收盘价 | 1天涨跌幅 | 1周涨跌幅 | 1个月涨跌幅\n"
    report += "------------------------------------------------\n"

    try:
        for index, row in stock_list.iterrows():
            ticker = row['Ticker']
            
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1mo")  # 获取过去1个月的数据
            
            if hist.empty or len(hist) < 2:
                print(f"⚠️ 无法获取 {ticker} 的数据")
                continue
            
            # 获取收盘价
            latest_close = hist['Close'].iloc[-1]
            one_day_change = ((latest_close - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100 if len(hist) > 1 else 0
            one_week_change = ((latest_close - hist['Close'].iloc[-6]) / hist['Close'].iloc[-6]) * 100 if len(hist) > 6 else 0
            one_month_change = ((latest_close - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100 if len(hist) > 20 else 0
            
            report += f"{ticker} | {latest_close:.2f} | {one_day_change:.2f}% | {one_week_change:.2f}% | {one_month_change:.2f}%\n"

    except Exception as e:
        report += f"\n❌ 数据获取出错: {e}"

    return report

if __name__ == "__main__":
    print("🚀 开始收集股票数据并发送邮件...")
    stock_report = fetch_stock_data()
    send_email("📈 每日股票市场报告", stock_report)
