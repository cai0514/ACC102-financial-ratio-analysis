import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Financial Ratio Analysis Dashboard", layout="wide")

st.title("📊 Financial Ratio Analysis Dashboard")
st.markdown("Interactive financial ratio comparison tool based on WRDS Compustat data")

@st.cache_data
def load_data():
    df = pd.read_csv('financial_ratios.csv')
    return df

df = load_data()

st.sidebar.header("Filter Settings")

companies = st.sidebar.multiselect(
    "Select Companies",
    options=df['conm'].unique(),
    default=df['conm'].unique().tolist()
)

years = sorted(df['fyear'].unique())
year_range = st.sidebar.select_slider(
    "Select Year Range",
    options=years,
    value=(min(years), max(years))
)

ratios = {
    "Gross Margin": "gross_margin",
    "Net Margin": "net_margin",
    "ROE (Return on Equity)": "roe",
    "ROA (Return on Assets)": "roa",
    "Debt Ratio": "debt_ratio"
}

selected_ratios = st.sidebar.multiselect(
    "Select Financial Ratios",
    options=list(ratios.keys()),
    default=["Gross Margin", "Net Margin", "ROE (Return on Equity)"]
)

# ============================================
# FEATURE 3: Threshold Alert (Sidebar)
# ============================================
st.sidebar.subheader("⚠️ Threshold Alert")

alert_roe = st.sidebar.number_input(
    "ROE Warning Threshold (%)", 
    min_value=0, 
    max_value=100, 
    value=15
) / 100

alert_debt = st.sidebar.number_input(
    "Debt Ratio Warning Threshold (%)", 
    min_value=0, 
    max_value=100, 
    value=60
) / 100

filtered_df = df[
    (df['conm'].isin(companies)) &
    (df['fyear'].between(year_range[0], year_range[1]))
]

# Dashboard Summary
st.markdown(f"""
<b>📌 Dashboard Summary</b><br>
Currently viewing <b>{len(filtered_df['conm'].unique())}</b> companies 
from <b>{year_range[0]}</b> to <b>{year_range[1]}</b>
""")

# Key Metrics Summary
st.subheader("🎯 Key Metrics Summary (Latest Year)")

latest_year = filtered_df['fyear'].max()
latest_data = filtered_df[filtered_df['fyear'] == latest_year]

if len(latest_data) > 0:
    avg_roe = latest_data['roe'].mean()
    avg_net_margin = latest_data['net_margin'].mean()
    avg_debt = latest_data['debt_ratio'].mean()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Average ROE", f"{avg_roe:.2%}")
    with col2:
        st.metric("Average Net Margin", f"{avg_net_margin:.2%}")
    with col3:
        st.metric("Average Debt Ratio", f"{avg_debt:.2%}")
    
    # ============================================
    # FEATURE 3: Threshold Alert Results (Sidebar already has inputs, show results here)
    # ============================================
    low_roe_companies = latest_data[latest_data['roe'] < alert_roe]['conm'].tolist()
    high_debt_companies = latest_data[latest_data['debt_ratio'] > alert_debt]['conm'].tolist()
    
    if low_roe_companies or high_debt_companies:
        st.warning("⚠️ Companies below your threshold:")
        if low_roe_companies:
            st.write(f"Low ROE (< {alert_roe:.0%}): {', '.join(low_roe_companies)}")
        if high_debt_companies:
            st.write(f"High Debt (> {alert_debt:.0%}): {', '.join(high_debt_companies)}")
    else:
        st.success("✅ All companies meet your criteria")

# ============================================
# FEATURE 1: Dynamic Summary
# ============================================
st.subheader("📝 Dynamic Summary")

if len(filtered_df) > 0:
    avg_roe_current = filtered_df['roe'].mean()
    avg_gm_current = filtered_df['gross_margin'].mean()
    best_company_roe = filtered_df.loc[filtered_df['roe'].idxmax(), 'conm']
    best_company_gm = filtered_df.loc[filtered_df['gross_margin'].idxmax(), 'conm']
    
    summary_text = f"""
Based on your selection of **{len(filtered_df['conm'].unique())} companies** 
from **{year_range[0]}** to **{year_range[1]}**:

- Average ROE: **{avg_roe_current:.2%}**
- Average Gross Margin: **{avg_gm_current:.2%}**

🏆 **{best_company_roe}** has the highest ROE
🏆 **{best_company_gm}** has the highest Gross Margin
"""
    st.info(summary_text)
else:
    st.info("Please select at least one company and year range to see the dynamic summary.")

# Financial Ratio Trends
st.subheader("📈 Financial Ratio Trends")

for ratio_name in selected_ratios:
    col_name = ratios[ratio_name]
    
    fig = px.line(
        filtered_df,
        x='fyear',
        y=col_name,
        color='conm',
        title=f"{ratio_name} Trend Comparison",
        markers=True,
        text=col_name
    )
    fig.update_traces(textposition='top center')
    fig.update_layout(
        yaxis_title=ratio_name,
        xaxis_title="Fiscal Year",
        legend_title="Company",
        height=450
    )
    st.plotly_chart(fig, use_container_width=True)

# ============================================
# FEATURE 6: Company Ranking
# ============================================
st.subheader("🏆 Company Ranking")

ranking_metric = st.selectbox(
    "Select metric for ranking",
    ["roe", "gross_margin", "net_margin", "roa"],
    format_func=lambda x: {
        "roe": "ROE (Return on Equity)",
        "gross_margin": "Gross Margin",
        "net_margin": "Net Margin",
        "roa": "ROA (Return on Assets)"
    }[x]
)

ranking_year = st.selectbox(
    "Select year for ranking", 
    sorted(filtered_df['fyear'].unique(), reverse=True)
)

ranking_data = filtered_df[filtered_df['fyear'] == ranking_year].copy()
ranking_data = ranking_data.sort_values(ranking_metric, ascending=False)
ranking_data['Rank'] = range(1, len(ranking_data) + 1)

st.dataframe(
    ranking_data[['Rank', 'conm', ranking_metric]].round(4),
    use_container_width=True,
    hide_index=True
)

if len(ranking_data) > 0:
    top_company = ranking_data.iloc[0]
    st.success(f"🥇 **{top_company['conm']}** has the highest {ranking_metric.replace('_', ' ').title()} at **{top_company[ranking_metric]:.2%}**")

# Detailed Data Table
st.subheader("📋 Detailed Data Table")
st.dataframe(
    filtered_df[['conm', 'fyear', 'gross_margin', 'net_margin', 'roe', 'roa', 'debt_ratio']].round(4),
    use_container_width=True
)

st.markdown("---")
st.caption("Data Source: WRDS Compustat | Data Access Date: April 2026")