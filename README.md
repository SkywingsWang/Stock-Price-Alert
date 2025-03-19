# Stock-Price-Alert

Stock Price Alert 是一个用于监控股票价格变化并通过电子邮件发送每日报告的 Python 脚本。该项目使用 GitHub Actions 自动运行，适用于任何想要零成本定期监控股票价格的人。
 
## 功能特性
 
- 使用 yfinance 获取股票数据
- 监控多种股票、指数和加密货币的价格变化
- 生成美观的HTML格式邮件报告，包含：
  - 股票当前价格和目标价格
  - 1天、1周、1个月和3个月的涨跌幅
  - 股票走势图（从StockCharts获取）
- 通过 SMTP 发送电子邮件通知
- GitHub Actions 自动定时运行（每周二至周六的北京时间早上7点）
- 可定制的股票清单和监控策略
 
## 快速开始
 
### 克隆仓库
 
```bash
git clone https://github.com/SkywingsWang/Stock-Price-Alert.git
cd Stock-Price-Alert
```
 
### 配置 GitHub Secrets
 
在你的 GitHub 仓库中添加以下 Action Secrets：
 
- `EMAIL_ADDRESS`：发送邮件的邮箱地址
- `EMAIL_PASSWORD`：发送邮件邮箱的密码（建议使用应用专用密码）
- `SMTP_SERVER`：SMTP 服务器地址（例如 `smtp.gmail.com`）
- `SMTP_PORT`：SMTP 服务器端口（例如 `587`）
- `TO_EMAIL_ADDRESS`：接收邮件的邮箱地址
 
### 配置股票清单
 
根据需要修改 `stock_list.csv` 文件，文件格式如下：

```
Ticker,Title,Target Price,Type,StockCharts Ticker
^IXIC,纳斯达克,17000,Stock,$COMPQ
GC=F,现货黄金,2800,Stock,$GOLD
```

各字段说明：
- `Ticker`: Yahoo Finance的股票代码
- `Title`: 显示名称
- `Target Price`: 目标价格（可以是N/A）
- `Type`: 类型（Stock、Forex等）
- `StockCharts Ticker`: StockCharts网站的股票代码（用于获取图表，可以是N/A）

### 本地运行
 
1. 安装依赖：
```bash
pip install yfinance pandas requests
```

2. 设置环境变量：
```bash
# Windows
set EMAIL_ADDRESS=your_email@example.com
set EMAIL_PASSWORD=your_password
set SMTP_SERVER=smtp.example.com
set SMTP_PORT=587
set TO_EMAIL_ADDRESS=recipient@example.com

# Linux/Mac
export EMAIL_ADDRESS=your_email@example.com
export EMAIL_PASSWORD=your_password
export SMTP_SERVER=smtp.example.com
export SMTP_PORT=587
export TO_EMAIL_ADDRESS=recipient@example.com
```

3. 运行脚本：
```bash
python stock_monitor.py
```
 
### 自定义报告
 
你可以修改 `stock_monitor.py` 文件中的 `fetch_stock_data` 函数，以自定义报告的内容和样式。

### 配置 GitHub Actions
 
仓库中已包含 `.github/workflows/monitor.yml` 文件。你可以根据需要修改此文件以更改运行频率或其他参数。默认的 GitHub Actions workflow 每周二至周六的北京时间早上7点运行一次。

```yaml
schedule:
  - cron: "0 23 * * 2-6"  # 每周二至周六（UTC 23:00，对应北京时间 07:00 AM）运行
```
 
## 邮件报告示例

邮件报告包含以下内容：
1. 所有监控股票的汇总表格（名称、收盘价、目标价、各时间段涨跌幅）
2. 每只股票的详细信息和走势图

## 常见问题

1. **邮件发送失败**：请检查SMTP服务器设置和邮箱密码是否正确。如果使用Gmail，请确保已开启"不够安全的应用访问权限"或使用应用专用密码。

2. **股票数据获取失败**：请确认Yahoo Finance的股票代码是否正确。某些特殊市场的股票可能需要特殊格式的代码。

3. **图表显示问题**：如果StockCharts的图表无法显示，请检查StockCharts Ticker是否正确，或者网络连接是否正常。

## 贡献
 
欢迎贡献代码！请 fork 本仓库并提交 Pull Request。

## 未来计划

- 添加更多数据源支持
- 实现自定义报告模板
- 添加价格预警功能
- 支持更多类型的金融产品监控
 
## 许可证
 
此项目基于 MIT 许可证发布。详情请参阅 [LICENSE](./LICENSE) 文件
