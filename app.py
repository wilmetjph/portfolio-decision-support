import streamlit as st
import pandas as pd

from portfolio import Portfolio
from monitoring import PortfolioMonitor

st.set_page_config(
    page_title="Portfolio Decision Support",
    page_icon="📊",
    layout="wide"
)

st.title("Portfolio Decision Support")
st.write(
    "Upload your portfolio data to identify allocation gaps "
    "and concentration risks."
)

holdings_file = st.file_uploader(
    "Upload holdings",
    type="csv"
)

prices_file = st.file_uploader(
    "Upload price history",
    type="csv"
)

if holdings_file is None or prices_file is None:
    st.info("Upload both CSV files to start the analysis.")
    st.stop()

prices_file.seek(0)

price_columns = pd.read_csv(
    prices_file,
    nrows=0
).columns.tolist()

available_benchmark = [
    column
    for column in price_columns
    if column != "date"
]

benchmark = st.selectbox(
    "Select the benchmark",
    available_benchmark
)

holdings_file.seek(0)
prices_file.seek(0)

try:
    portfolio = Portfolio(
        holdings_path=holdings_file,
        prices_path=prices_file,
        benchmark=benchmark
    )

except ValueError as error:
    st.error(str(error))
    st.stop()

st.metric(
    "Total portfolio value",
    f"€{portfolio.get_total_value():,.2f}"
)

st.sidebar.header("Target allocation")

actual_allocation = (
    portfolio.calculate_asset_class_allocation()
)

default_targets = {
    "Equity": 50.0,
    "Bond": 40.0,
    "Cash": 10.0
}

targets = {}

for asset_class in actual_allocation.index:
    targets[asset_class] = st.sidebar.number_input(
        asset_class,
        min_value=0.0,
        max_value=100.0,
        value=default_targets.get(asset_class, 0.0),
        step=1.0
    )

if abs(sum(targets.values()) - 100) > 0.01:
    st.error("Target allocations must sum to 100%.")
    st.stop()

monitor = PortfolioMonitor(
    portfolio=portfolio,
    target_allocation=targets,
    tolerance=5
)

st.subheader("Allocation analysis")
allocation_comparison = monitor.compare_allocation()
allocation_display = allocation_comparison.astype(float)

st.dataframe(
    allocation_display,
    width="stretch",
    column_config={
        "actual": st.column_config.NumberColumn(
            "Actual",
            format="%.2f"
        ),
        "target": st.column_config.NumberColumn(
            "Target",
            format="%.2f"
        ),
        "deviation": st.column_config.NumberColumn(
            "Deviation",
            format="%.2f"
        )
    }
)
chart_data = allocation_comparison[
    ["actual", "target"]
]
st.bar_chart(
    chart_data,
    stack=False,
    width="stretch"
)

st.subheader("Rebalancing recommandations")
alerts = monitor.generate_alerts()
alerts_df = pd.DataFrame(alerts)
if not alerts_df.empty:
    alerts_display = alerts_df.copy()
    alerts_display["deviation"] = pd.to_numeric(
    alerts_display["deviation"]
)/100
    alerts_display["amount"] = pd.to_numeric(
    alerts_display["amount"]
)/100
    alerts_display["status"] = alerts_display["status"].str.capitalize()
    st.dataframe(
        alerts_display,
        hide_index=True,
        width="stretch",
        column_config={
            "asset_class": "Asset class",
            "status": "Status",
            "deviation": st.column_config.NumberColumn(
                "Deviation",
                format="percent"
            ),
            "action": "Action",
            "amount": st.column_config.NumberColumn(
                "Amount",
                format="euro"
            )
        }
    )
else:
    st.success(
        "The portfolio is within the allocation tolerance."
    )

st.subheader("Concentration risks")
concentrations = monitor.check_concentration()
concentrations_display = concentrations.copy()
concentrations_display["weight"] = pd.to_numeric(
    concentrations_display["weight"]
)/100
concentrations_display["market_value"] = pd.to_numeric(
    concentrations_display["market_value"]
)/100
if not concentrations_display.empty:
    st.dataframe(
        concentrations_display,
        hide_index=True,
        width="stretch",
        column_config={
            "asset": "Asset",
            "weight": st.column_config.NumberColumn(
                "Weight",
                format="percent"
            ),
            "market_value": st.column_config.NumberColumn(
                "Market value",
                format="euro"
            )
        }
    )
else:
    st.success(
        "No position exceeds the concentration limit."
    )