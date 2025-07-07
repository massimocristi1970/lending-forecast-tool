import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import numpy as np

# Page configuration
st.set_page_config(page_title="Lending Forecast Tool", layout="wide")
st.title("📊 Lending Forecast and Unit Economics")

# Initialize session state
if "saved_scenarios" not in st.session_state:
    st.session_state.saved_scenarios = {}

# Sidebar inputs
st.sidebar.header("🔧 Adjustable Inputs")
scenario_name = st.sidebar.text_input("Scenario Name", value="Default Scenario")

# Core lending parameters
initial_lending = st.sidebar.number_input(
    "Initial Monthly Lending Volume (£)", 
    value=2_000_000, 
    step=100_000,
    help="Starting monthly lending amount"
)

loan_growth_rate = st.sidebar.slider(
    "Monthly Loan Growth Rate (%)", 
    min_value=-50.0, 
    max_value=100.0, 
    value=0.0,
    help="Monthly compound growth rate in lending volume"
) / 100

# Loan size parameters with validation
min_loan_size = st.sidebar.number_input(
    "Minimum Loan Amount (£)", 
    value=300, 
    step=50,
    min_value=50
)

max_loan_size = st.sidebar.number_input(
    "Maximum Loan Amount (£)", 
    value=1500, 
    step=50,
    min_value=min_loan_size + 50
)

# Validation check
if min_loan_size >= max_loan_size:
    st.error("⚠️ Minimum loan size must be less than maximum loan size")
    st.stop()

avg_loan_size = (min_loan_size + max_loan_size) / 2

loan_term = st.sidebar.selectbox(
    "Loan Term (Months)", 
    options=[1, 2, 3, 4, 5, 6, 12], 
    index=2,
    help="Duration of loans in months"
)

# Cost and revenue parameters
cost_per_funded = st.sidebar.number_input(
    "Cost per Funded Loan (£)", 
    value=40, 
    step=5,
    min_value=0,
    help="Direct cost to fund each loan (origination, processing, etc.)"
)

bad_debt_rate = st.sidebar.slider(
    "Bad Debt Rate (%)", 
    min_value=0.0, 
    max_value=100.0, 
    value=20.0,
    help="Expected percentage of loans that will default"
) / 100

recovery_rate = st.sidebar.slider(
    "Recovery Rate (%)", 
    min_value=0.0, 
    max_value=100.0, 
    value=0.0,
    help="Percentage of defaulted amount that can be recovered"
) / 100

revenue_per_loan_base = st.sidebar.number_input(
    "Base Revenue per Loan (£300 loan for 3 months)", 
    value=150, 
    step=10,
    min_value=0,
    help="Revenue from baseline £300 loan over 3 months"
)

months = st.sidebar.slider(
    "Forecast Horizon (Months)", 
    min_value=1, 
    max_value=60, 
    value=12,
    help="Number of months to forecast"
)

# Operating expenditure assumptions
st.sidebar.header("🏢 Operating Expenditure")
fixed_costs = st.sidebar.number_input(
    "Monthly Fixed Overheads (£)", 
    value=25_000, 
    step=1_000,
    min_value=0,
    help="Monthly fixed costs (salaries, rent, etc.)"
)

variable_cost_pct = st.sidebar.slider(
    "Variable Cost (% of Revenue)", 
    min_value=0.0, 
    max_value=100.0, 
    value=5.0,
    help="Variable costs as percentage of revenue"
) / 100

# Business logic validations with warnings
if bad_debt_rate > 0.5:
    st.sidebar.warning("⚠️ Bad debt rate above 50% - please verify")

if cost_per_funded > revenue_per_loan_base * 0.5:
    st.sidebar.warning("⚠️ Cost per funded loan is >50% of base revenue - check unit economics")

# Calculate derived values
loan_size_factor = avg_loan_size / 300
loan_term_factor = loan_term / 3
revenue_per_loan = revenue_per_loan_base * loan_size_factor * loan_term_factor
bad_debt_per_loan = avg_loan_size * bad_debt_rate * (1 - recovery_rate)
net_contribution_per_loan = revenue_per_loan - cost_per_funded - bad_debt_per_loan

# Function to calculate monthly metrics
def calculate_monthly_metrics(month, initial_lending, loan_growth_rate, avg_loan_size, 
                            revenue_per_loan, cost_per_funded, bad_debt_per_loan, 
                            fixed_costs, variable_cost_pct):
    monthly_lending = initial_lending * ((1 + loan_growth_rate) ** (month - 1))
    loans_this_month = int(monthly_lending / avg_loan_size)
    revenue = loans_this_month * revenue_per_loan
    cost = loans_this_month * cost_per_funded
    provision = loans_this_month * bad_debt_per_loan
    variable_cost = revenue * variable_cost_pct
    net_contribution = revenue - cost - provision - variable_cost
    total_expenditure = cost + provision + variable_cost + fixed_costs
    net_cashflow = revenue - total_expenditure
    
    return {
        'monthly_lending': monthly_lending,
        'loans_this_month': loans_this_month,
        'revenue': revenue,
        'cost': cost,
        'provision': provision,
        'variable_cost': variable_cost,
        'net_contribution': net_contribution,
        'total_expenditure': total_expenditure,
        'net_cashflow': net_cashflow
    }

# Generate forecast data
data = []
# Extended arrays to handle repayment periods
forecast_horizon = months + loan_term
cashflow_data = [0] * forecast_horizon
net_cashflow_data = [0] * forecast_horizon

for month in range(1, months + 1):
    metrics = calculate_monthly_metrics(
        month, initial_lending, loan_growth_rate, avg_loan_size,
        revenue_per_loan, cost_per_funded, bad_debt_per_loan,
        fixed_costs, variable_cost_pct
    )
    
    data.append([
        month,
        metrics['monthly_lending'],
        metrics['loans_this_month'],
        metrics['revenue'],
        metrics['cost'],
        metrics['provision'],
        metrics['variable_cost'],
        fixed_costs,
        metrics['net_contribution'],
        metrics['net_cashflow']
    ])
    
    # Calculate repayment cashflow - starts after loan term
    if loan_term > 0:
        monthly_repayment = metrics['revenue'] / loan_term
        monthly_net_expense = metrics['total_expenditure'] / loan_term
        
        for i in range(loan_term):
            repayment_month = month - 1 + i  # Array index (0-based)
            if repayment_month < len(cashflow_data):
                cashflow_data[repayment_month] += monthly_repayment
                net_cashflow_data[repayment_month] += monthly_repayment - monthly_net_expense

# Create DataFrame
df = pd.DataFrame(data, columns=[
    "Month", "Lending Volume (£)", "Loans Funded", "Revenue (£)", 
    "Cost (£)", "Provision (£)", "Variable Costs (£)", "Fixed Costs (£)", 
    "Net Contribution (£)", "Net Cashflow (£)"
])

# Create total row
total_row = pd.DataFrame({
    "Month": ["TOTAL"],
    "Lending Volume (£)": [df["Lending Volume (£)"].sum()],
    "Loans Funded": [df["Loans Funded"].sum()],
    "Revenue (£)": [df["Revenue (£)"].sum()],
    "Cost (£)": [df["Cost (£)"].sum()],
    "Provision (£)": [df["Provision (£)"].sum()],
    "Variable Costs (£)": [df["Variable Costs (£)"].sum()],
    "Fixed Costs (£)": [df["Fixed Costs (£)"].sum()],
    "Net Contribution (£)": [df["Net Contribution (£)"].sum()],
    "Net Cashflow (£)": [df["Net Cashflow (£)"].sum()]
})

# Save scenario functionality
if st.sidebar.button("💾 Save Scenario"):
    if scenario_name.strip():
        st.session_state.saved_scenarios[scenario_name] = {
            "df": df.copy(),
            "total": total_row.copy(),
            "cashflow": cashflow_data.copy(),
            "net_cashflow": net_cashflow_data.copy(),
            "parameters": {
                "initial_lending": initial_lending,
                "loan_growth_rate": loan_growth_rate,
                "avg_loan_size": avg_loan_size,
                "loan_term": loan_term,
                "revenue_per_loan": revenue_per_loan,
                "bad_debt_rate": bad_debt_rate,
                "months": months
            }
        }
        st.sidebar.success(f"✅ Saved '{scenario_name}'")
    else:
        st.sidebar.error("Please enter a scenario name")

# Display key metrics at the top
st.subheader("📋 Key Metrics Summary")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Revenue", 
        f"£{df['Revenue (£)'].sum():,.0f}",
        help="Total revenue across all months"
    )

with col2:
    st.metric(
        "Total Loans", 
        f"{df['Loans Funded'].sum():,.0f}",
        help="Total number of loans funded"
    )

with col3:
    avg_growth = ((df['Lending Volume (£)'].iloc[-1] / df['Lending Volume (£)'].iloc[0]) ** (1/months) - 1) * 100 if months > 1 else 0
    st.metric(
        "Avg Monthly Growth", 
        f"{avg_growth:.1f}%",
        help="Average monthly growth rate achieved"
    )

with col4:
    margin = (net_contribution_per_loan / revenue_per_loan * 100) if revenue_per_loan > 0 else 0
    st.metric(
        "Net Contribution Margin", 
        f"{margin:.1f}%",
        help="Net contribution as percentage of revenue per loan"
    )

# Display forecast table
st.subheader("📅 Forecast Table")
df_display = pd.concat([df, total_row], ignore_index=True)

# Format the display DataFrame
formatted_df = df_display.style.format({
    'Lending Volume (£)': '£{:,.0f}',
    'Revenue (£)': '£{:,.0f}',
    'Cost (£)': '£{:,.0f}',
    'Provision (£)': '£{:,.0f}',
    'Variable Costs (£)': '£{:,.0f}',
    'Fixed Costs (£)': '£{:,.0f}',
    'Net Contribution (£)': '£{:,.0f}',
    'Net Cashflow (£)': '£{:,.0f}'
}).apply(lambda x: ['font-weight: bold' if x.name == len(df_display) - 1 else '' for i in x], axis=1)

st.dataframe(formatted_df, use_container_width=True)

# Unit economics display
st.subheader("📌 Per-Loan Unit Economics")
unit_economics_col1, unit_economics_col2 = st.columns(2)

with unit_economics_col1:
    st.markdown(f"""
    **Scenario:** {scenario_name}
    
    **Loan Parameters:**
    - Loan amount range: £{min_loan_size:,.0f} – £{max_loan_size:,.0f}
    - Average loan size: £{avg_loan_size:,.0f}
    - Loan term: {loan_term} months
    """)

with unit_economics_col2:
    st.markdown(f"""
    **Unit Economics:**
    - Revenue per loan: £{revenue_per_loan:.2f}
    - Cost per funded loan: £{cost_per_funded:.2f}
    - Bad debt provision: £{bad_debt_per_loan:.2f}
    - **Net contribution per loan: £{net_contribution_per_loan:.2f}**
    """)

# Charts section
st.subheader("📈 Trend Charts")

# Main trends chart
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(df['Month'], df['Revenue (£)'], label='Revenue', marker='o', linewidth=2)
ax.plot(df['Month'], df['Provision (£)'], label='Bad Debt Provision', marker='x', linewidth=2)
ax.plot(df['Month'], df['Net Contribution (£)'], label='Net Contribution', marker='s', linewidth=2)
ax.plot(df['Month'], df['Net Cashflow (£)'], label='Net Cashflow', marker='^', linewidth=2)

ax.set_xlabel("Month")
ax.set_ylabel("Amount (£)")
ax.set_title("Revenue, Provision, and Net Results Over Time")
ax.legend(loc='upper left')
ax.grid(True, alpha=0.3)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'£{x:,.0f}'))

plt.tight_layout()
st.pyplot(fig)

# Cashflow projection chart
st.subheader("💵 Cashflow Projection (Repayment Flow)")
cashflow_df = pd.DataFrame({
    "Month": list(range(1, len(cashflow_data) + 1)),
    "Cashflow (£)": cashflow_data,
    "Net Cashflow (£)": net_cashflow_data
})

fig2, ax2 = plt.subplots(figsize=(12, 6))
ax2.bar(cashflow_df['Month'], cashflow_df['Cashflow (£)'], 
        label='Repayment Cashflow', alpha=0.6, color='lightblue')
ax2.plot(cashflow_df['Month'], cashflow_df['Net Cashflow (£)'], 
         label='Net Cashflow', color='red', marker='o', linewidth=2)

ax2.set_title("Repayment-Based Revenue and Net Cashflow")
ax2.set_xlabel("Month")
ax2.set_ylabel("Cash Flow (£)")
ax2.legend()
ax2.grid(True, alpha=0.3)
ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'£{x:,.0f}'))

plt.tight_layout()
st.pyplot(fig2)

# Excel export function
def to_excel(df_main, df_total, df_cashflow, scenario_params):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Main forecast
        df_main.to_excel(writer, index=False, sheet_name='Forecast')
        
        # Totals
        df_total.to_excel(writer, index=False, sheet_name='Totals')
        
        # Cashflow
        df_cashflow.to_excel(writer, index=False, sheet_name='Cashflow')
        
        # Parameters
        params_df = pd.DataFrame(list(scenario_params.items()), columns=['Parameter', 'Value'])
        params_df.to_excel(writer, index=False, sheet_name='Parameters')
        
    return output.getvalue()

# Download button
excel_data = to_excel(df, total_row, cashflow_df, {
    'Scenario Name': scenario_name,
    'Initial Lending': initial_lending,
    'Growth Rate': loan_growth_rate,
    'Average Loan Size': avg_loan_size,
    'Loan Term': loan_term,
    'Revenue per Loan': revenue_per_loan,
    'Bad Debt Rate': bad_debt_rate,
    'Recovery Rate': recovery_rate,
    'Fixed Costs': fixed_costs,
    'Variable Cost %': variable_cost_pct,
    'Forecast Months': months
})

st.download_button(
    label="📥 Download Excel Report",
    data=excel_data,
    file_name=f"{scenario_name.replace(' ', '_')}_forecast.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    help="Download complete forecast data as Excel file"
)

# Scenario comparison
if st.session_state.saved_scenarios:
    st.subheader("📊 Saved Scenario Comparison")
    
    available_scenarios = list(st.session_state.saved_scenarios.keys())
    compare_names = st.multiselect(
        "Select Scenarios to Compare", 
        available_scenarios,
        default=available_scenarios[:min(2, len(available_scenarios))],
        help="Choose 2 or more scenarios to compare"
    )
    
    if len(compare_names) >= 2:
        # Comparison table
        comparison_data = []
        for name in compare_names:
            scenario = st.session_state.saved_scenarios[name]
            total_revenue = scenario["total"]["Revenue (£)"].iloc[0]
            total_loans = scenario["total"]["Loans Funded"].iloc[0]
            total_contribution = scenario["total"]["Net Contribution (£)"].iloc[0]
            
            comparison_data.append({
                'Scenario': name,
                'Total Revenue': f"£{total_revenue:,.0f}",
                'Total Loans': f"{total_loans:,.0f}",
                'Total Net Contribution': f"£{total_contribution:,.0f}",
                'Avg Revenue per Loan': f"£{total_revenue/total_loans:.2f}" if total_loans > 0 else "£0.00"
            })
        
        comparison_df = pd.DataFrame(comparison_data)
        st.dataframe(comparison_df, use_container_width=True)
        
        # Comparison charts
        col1, col2 = st.columns(2)
        
        with col1:
            fig3, ax3 = plt.subplots(figsize=(10, 5))
            for name in compare_names:
                cashflow_series = st.session_state.saved_scenarios[name]["cashflow"]
                ax3.plot(range(1, len(cashflow_series) + 1), cashflow_series, 
                        label=name, marker='o', linewidth=2)
            ax3.set_title("Repayment Cashflow Comparison")
            ax3.set_xlabel("Month")
            ax3.set_ylabel("Cash In (£)")
            ax3.legend()
            ax3.grid(True, alpha=0.3)
            ax3.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'£{x:,.0f}'))
            plt.tight_layout()
            st.pyplot(fig3)
        
        with col2:
            fig4, ax4 = plt.subplots(figsize=(10, 5))
            for name in compare_names:
                net_cf = st.session_state.saved_scenarios[name]["net_cashflow"]
                ax4.plot(range(1, len(net_cf) + 1), net_cf, 
                        label=name, marker='s', linewidth=2)
            ax4.set_title("Net Cashflow Comparison")
            ax4.set_xlabel("Month")
            ax4.set_ylabel("Net Cash (£)")
            ax4.legend()
            ax4.grid(True, alpha=0.3)
            ax4.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'£{x:,.0f}'))
            plt.tight_layout()
            st.pyplot(fig4)
    
    # Option to delete scenarios
    if st.sidebar.button("🗑️ Clear All Scenarios"):
        st.session_state.saved_scenarios = {}
        st.sidebar.success("All scenarios cleared")

# Footer with explanation
st.markdown("---")
st.caption("""
**Model Assumptions:** Revenue calculations adjust for loan amount and term relative to a £300/3-month baseline. 
Repayment flow assumes straight-line amortization across the loan term. Net cashflow includes all fixed and variable costs. 
Growth rate applies as monthly compound increase to lending volume. Bad debt provision is calculated upfront but actual 
losses may occur over time.
""")