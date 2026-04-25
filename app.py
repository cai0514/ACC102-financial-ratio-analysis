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

filtered_df = df[
    (df['conm'].isin(companies)) &
    (df['fyear'].between(year_range[0], year_range[1]))
]

# Dashboard Summary
st.info(f"""
**📌 Dashboard Summary**  
Currently viewing **{len(filtered_df['conm'].unique())}** companies from **{year_range[0]}** to **{year_range[1]}**
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

# Detailed Data Table
st.subheader("📋 Detailed Data Table")
st.dataframe(
    filtered_df[['conm', 'fyear', 'gross_margin', 'net_margin', 'roe', 'roa', 'debt_ratio']].round(4),
    use_container_width=True
)

# Key Insights
st.subheader("💡 Key Insights")

if len(filtered_df) > 0:
    best_roe = filtered_df.loc[filtered_df['roe'].idxmax()]
    highest_debt = filtered_df.loc[filtered_df['debt_ratio'].idxmax()]
    
    st.markdown(f"""
    - 🏆 **Highest ROE**: {best_roe['conm']} ({best_roe['roe']:.2%}) in {best_roe['fyear']}
    - ⚠️ **Highest Debt Ratio**: {highest_debt['conm']} ({highest_debt['debt_ratio']:.2%})
    - 💡 Tech companies (Apple, Microsoft, Alphabet) show high profitability but varying debt levels
    - 📉 Walmart operates with low margins but high asset turnover
    """)

# ============================================
# NEW FEATURE: Company Comparison Tool
# ============================================
st.subheader("🔍 Company Comparison Tool")
st.markdown("Select two companies to compare their financial ratios side by side.")

available_companies = filtered_df['conm'].unique()

if len(available_companies) >= 2:
    col1, col2 = st.columns(2)
    with col1:
        company_a = st.selectbox("Select Company A", options=available_companies, key="comp_a")
    with col2:
        company_b = st.selectbox("Select Company B", options=available_companies, key="comp_b")
    
    if company_a and company_b and company_a != company_b:
        latest_year_comp = filtered_df['fyear'].max()
        data_a = filtered_df[(filtered_df['conm'] == company_a) & (filtered_df['fyear'] == latest_year_comp)]
        data_b = filtered_df[(filtered_df['conm'] == company_b) & (filtered_df['fyear'] == latest_year_comp)]
        
        if not data_a.empty and not data_b.empty:
            comparison_data = {
                "Metric": ["Gross Margin", "Net Margin", "ROE", "ROA", "Debt Ratio"],
                company_a: [
                    f"{data_a['gross_margin'].values[0]:.2%}",
                    f"{data_a['net_margin'].values[0]:.2%}",
                    f"{data_a['roe'].values[0]:.2%}",
                    f"{data_a['roa'].values[0]:.2%}",
                    f"{data_a['debt_ratio'].values[0]:.2%}"
                ],
                company_b: [
                    f"{data_b['gross_margin'].values[0]:.2%}",
                    f"{data_b['net_margin'].values[0]:.2%}",
                    f"{data_b['roe'].values[0]:.2%}",
                    f"{data_b['roa'].values[0]:.2%}",
                    f"{data_b['debt_ratio'].values[0]:.2%}"
                ]
            }
            comparison_df = pd.DataFrame(comparison_data)
            st.dataframe(comparison_df, use_container_width=True)
            
            comparison_melt = comparison_df.melt(id_vars=["Metric"], var_name="Company", value_name="Value")
            comparison_melt['Value'] = comparison_melt['Value'].str.rstrip('%').astype('float') / 100
            
            fig_comp = px.bar(
                comparison_melt,
                x="Metric",
                y="Value",
                color="Company",
                barmode="group",
                title=f"{company_a} vs {company_b} - Financial Ratio Comparison ({latest_year_comp})",
                text_auto='.2%'
            )
            st.plotly_chart(fig_comp, use_container_width=True)
        else:
            st.info("Selected companies do not have data for the latest year. Please adjust year filter.")
else:
    st.info("Please select at least two companies in the filter to enable comparison.")

# Footer
st.markdown("---")
st.caption("Data Source: WRDS Compustat | Data Access Date: April 2026")
