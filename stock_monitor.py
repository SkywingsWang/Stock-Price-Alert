import yfinance as yf
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd
import time
import os

# 邮件配置
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))

# 读取股票清单
stock_list = pd.read_csv('stock_list.csv')  # 假设csv文件中有两列: 'Ticker', 'Threshold'

def send_email(subject, body):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = EMAIL_ADDRESS
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, text)

def monitor_stocks():
    for index, row in stock_list.iterrows():
        ticker = row['Ticker']
        threshold = row['Threshold']
        
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1d")
        
        if not hist.empty:
            open_price = hist['Open'].iloc[0]
            current_price = hist['Close'].iloc[0]
            change = ((current_price - open_price) / open_price) * 100
            
            if abs(change) >= abs(threshold):
                subject = f"Stock Alert: {ticker}"
                body = f"The stock {ticker} has changed by {change:.2f}% today."
                send_email(subject, body)

if __name__ == "__main__":
    while True:
        monitor_stocks()
        time.sleep(3600)  # 每小时运行一次
