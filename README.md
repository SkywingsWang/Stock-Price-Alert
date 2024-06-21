# Stock-Price-Alert

Stock Price Alert 是一个用于监控股票价格变化并通过电子邮件发送通知的 Python 脚本。该项目使用 GitHub Actions 自动运行，适用于任何想要零成本定期监控股票价格的人。
 
## 特性
 
- 使用 yfinance 获取股票数据
- 监控指定幅度的价格变化
- 通过 SMTP 发送电子邮件通知
- GitHub Actions 自动定时运行
- 可定制的策略和触发机制
 
## 快速开始
 
### 克隆仓库
 
```bash
git clone https://github.com/SkywingsWang/Stock-Price-Alert.git
cd stock-price-alert
```
 
### 配置 GitHub Secrets
 
在你的 GitHub 仓库中添加以下 Action Secrets：
 
- `EMAIL_ADDRESS`：发送邮件的邮箱地址
- `EMAIL_PASSWORD`：发送邮件邮箱的密码（建议使用应用专用密码）
- `SMTP_SERVER`：SMTP 服务器地址（例如 `smtp.gmail.com`）
- `SMTP_PORT`：SMTP 服务器端口（例如 `587`）
 
### 配置股票清单
 
根据需要修改 `stock_list.csv` 文件，包括股票代码和变化幅度。如果程序报错，请检查这部分数据是否存在问题。
 
### 自定义策略
 
你可以修改 `stock_monitor.py` 文件中的 `monitor_stocks` 函数，以实现自定义的监控策略。默认为使用前一天的收盘价作为基准计算价格变化。
 
### 配置 GitHub Actions
 
仓库中已包含 `.github/workflows/monitor.yml` 文件。你可以根据需要修改此文件以更改运行频率或其他参数。默认的 GitHub Actions workflow 每小时运行一次。
 
## 贡献
 
欢迎贡献代码！请 fork 本仓库并提交 Pull Request
 
## 许可证
 
此项目基于 MIT 许可证发布。详情请参阅 [LICENSE](./LICENSE) 文件
