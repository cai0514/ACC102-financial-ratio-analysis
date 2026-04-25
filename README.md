# Financial Ratio Analysis Dashboard

## 1. Problem & User
This project helps accounting students and individual investors quickly compare key financial ratios (Gross Margin, Net Margin, ROE, ROA, Debt Ratio) across multiple companies without manually calculating from financial statements.

## 2. Data
- **Source**: WRDS Compustat (Fundamentals Annual table)
- **Access date**: April 24, 2026
- **Key fields**: revenue, cost of goods sold, net income, total assets, total liabilities, common equity

## 3. Methods
- Connected to WRDS Compustat using PyWRDS and executed SQL queries to retrieve financial data for 6 companies (Apple, Microsoft, Alphabet, Tesla, Johnson & Johnson, Walmart) from 2023-2025
- Calculated 5 financial ratios using Pandas
- Built an interactive Streamlit dashboard with Plotly visualizations
- Added company comparison feature for side-by-side analysis

## 4. Key Findings
- Apple and Microsoft show consistently high profitability with gross margins above 43%
- Tesla's profitability declined significantly from 2023 to 2025 (ROE dropped from 24% to 4.6%)
- Walmart operates with very low margins (2-3% net margin) but maintains stable profitability through high volume
- Alphabet (Google) achieved the highest ROE (32%) among all companies in 2025
- Apple has the highest debt ratio (over 80%), indicating a more leveraged capital structure

## 5. How to Run
```bash
pip install streamlit pandas plotly
streamlit run app.py

## 6. Product Link / Demo
Run the code locally to access the full interactive demo.

## 7. Limitations & Next Steps

Limited to 6 large-cap companies and 3 years of data
No real-time data refresh (manual update required)
Future improvements: add more companies, include industry benchmarks, implement automatic data refresh from WRDS