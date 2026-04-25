import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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

# Threshold Alert
st.sidebar.subheader("⚠️ Threshold Alert")
alert_roe = st.sidebar.number_input("ROE Warning Threshold (%)", min_value=0, max_value=100, value=15) / 100
alert_debt = st.sidebar.number_input("Debt Ratio Warning Threshold (%)", min_value=0, max_value=100, value=60) / 100

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
    
    low_roe = latest_data[latest_data['roe'] < alert_roe]['conm'].tolist()
    high_debt = latest_data[latest_data['debt_ratio'] > alert_debt]['conm'].tolist()
    if low_roe or high_debt:
        st.warning("⚠️ Alert: " + (f"Low ROE: {', '.join(low_roe)}" if low_roe else "") + 
                   (f" | High Debt: {', '.join(high_debt)}" if high_debt else ""))
    else:
        st.success("✅ All companies meet your criteria")

# Dynamic Summary
st.subheader("📝 Dynamic Summary")
if len(filtered_df) > 0:
    avg_roe_cur = filtered_df['roe'].mean()
    avg_gm_cur = filtered_df['gross_margin'].mean()
    best_roe = filtered_df.loc[filtered_df['roe'].idxmax(), 'conm']
    best_gm = filtered_df.loc[filtered_df['gross_margin'].idxmax(), 'conm']
    st.info(f"""
    **{len(filtered_df['conm'].unique())} companies** from **{year_range[0]}-{year_range[1]}**:
    - Avg ROE: **{avg_roe_cur:.2%}** | Avg Gross Margin: **{avg_gm_cur:.2%}**
    - 🏆 Highest ROE: **{best_roe}** | 🏆 Highest Margin: **{best_gm}**
    """)

# Financial Ratio Trends
st.subheader("📈 Financial Ratio Trends")
for ratio_name in selected_ratios:
    col_name = ratios[ratio_name]
    fig = px.line(filtered_df, x='fyear', y=col_name, color='conm',
                  title=f"{ratio_name} Trend Comparison", markers=True, text=col_name)
    fig.update_traces(textposition='top center')
    fig.update_layout(yaxis_title=ratio_name, xaxis_title="Fiscal Year", height=450)
    st.plotly_chart(fig, use_container_width=True)

# ============================================
# NEW FEATURE 1: YoY Growth Analysis
# ============================================
st.subheader("📈 Year-over-Year Growth Analysis")
yoy_metric = st.selectbox("Select metric for YoY growth", 
                          ["roe", "gross_margin", "net_margin", "roa", "debt_ratio"],
                          format_func=lambda x: x.replace('_', ' ').title())

yoy_data = filtered_df[['conm', 'fyear', yoy_metric]].copy()
yoy_data = yoy_data.sort_values(['conm', 'fyear'])
yoy_data['pct_change'] = yoy_data.groupby('conm')[yoy_metric].pct_change()
yoy_data = yoy_data.dropna(subset=['pct_change'])

if len(yoy_data) > 0:
    fig_yoy = px.bar(yoy_data, x='conm', y='pct_change', color='fyear',
                     barmode='group', title=f"{yoy_metric.replace('_', ' ').title()} YoY Growth",
                     labels={'pct_change': 'Growth Rate', 'conm': 'Company'})
    fig_yoy.update_layout(yaxis_tickformat='.0%')
    st.plotly_chart(fig_yoy, use_container_width=True)
else:
    st.info("Not enough data for YoY comparison")

# ============================================
# NEW FEATURE 2: Company Ranking
# ============================================
st.subheader("🏆 Company Ranking")
ranking_metric = st.selectbox("Select metric for ranking",
                              ["roe", "gross_margin", "net_margin", "roa"],
                              format_func=lambda x: x.replace('_', ' ').title())
ranking_year = st.selectbox("Select year", sorted(filtered_df['fyear'].unique(), reverse=True))
rank_data = filtered_df[filtered_df['fyear'] == ranking_year].copy()
rank_data = rank_data.sort_values(ranking_metric, ascending=False)
rank_data['Rank'] = range(1, len(rank_data) + 1)
st.dataframe(rank_data[['Rank', 'conm', ranking_metric]].round(4), use_container_width=True, hide_index=True)
if len(rank_data) > 0:
    st.success(f"🥇 Top: **{rank_data.iloc[0]['conm']}** at **{rank_data.iloc[0][ranking_metric]:.2%}**")

# ============================================
# NEW FEATURE 3: Historical Comparison (Select two years)
# ============================================
st.subheader("📅 Historical Comparison")
comp_years = st.multiselect("Select two years to compare", 
                            sorted(filtered_df['fyear'].unique()), 
                            max_selections=2)
if len(comp_years) == 2:
    comp_data = filtered_df[filtered_df['fyear'].isin(comp_years)]
    comp_pivot = comp_data.pivot_table(index='conm', columns='fyear', 
                                        values=['roe', 'gross_margin', 'net_margin', 'debt_ratio'])
    st.dataframe(comp_pivot.round(4), use_container_width=True)
    
    # Show change
    for company in comp_data['conm'].unique():
        old = comp_data[(comp_data['conm'] == company) & (comp_data['fyear'] == comp_years[0])]['roe'].values
        new = comp_data[(comp_data['conm'] == company) & (comp_data['fyear'] == comp_years[1])]['roe'].values
        if len(old) > 0 and len(new) > 0:
            change = new[0] - old[0]
            st.write(f"**{company}** ROE change: {old[0]:.2%} → {new[0]:.2%} ({'+' if change > 0 else ''}{change:.2%})")

# ============================================
# NEW FEATURE 4: Export Data
# ============================================
st.subheader("📥 Export Data")
export_df = filtered_df[['conm', 'fyear', 'gross_margin', 'net_margin', 'roe', 'roa', 'debt_ratio']].round(4)
csv = export_df.to_csv(index=False).encode('utf-8')
st.download_button("📄 Download as CSV", data=csv, 
                   file_name=f"financial_data_{year_range[0]}_{year_range[1]}.csv", 
                   mime="text/csv")

# Detailed Data Table
st.subheader("📋 Detailed Data Table")
st.dataframe(export_df, use_container_width=True)

st.markdown("---")
st.caption("Data Source: WRDS Compustat | Data Access Date: April 2026")