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
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")
        raise  # Re-raise the exception to terminate the workflow

def monitor_stocks():
    try:
        for index, row in stock_list.iterrows():
            ticker = row['Ticker']
            threshold = row['Threshold']
            
            stock = yf.Ticker(ticker)
            hist = stock.history(period="2d")
            
            if not hist.empty and len(hist) >= 2:
                prev_close = hist['Close'].iloc[0]
                current_close = hist['Close'].iloc[1]
                change = ((current_close - prev_close) / prev_close) * 100
                
                if abs(change) >= abs(threshold):
                    subject = f"Stock Alert: {ticker}"
                    body = f"The stock {ticker} has changed by {change:.2f}% today."
                    send_email(subject, body)
                    
    except Exception as e:
        # If there's an exception during the monitoring, send an error email
        subject = "Stock Monitor Error"
        body = f"An error occurred while monitoring stocks: {e}"
        send_email(subject, body)
        raise  # Re-raise the exception to terminate the workflow

if __name__ == "__main__":
    monitor_stocks()
