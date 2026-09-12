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

portfolio_file = st.file_uploader(
    "Upload portfolio export",
    type="csv"
)

if portfolio_file is None:
    st.info(
        "Upload a portfolio CSV file to start the analysis."
    )
    st.stop()

try:
    portfolio = Portfolio(
        portfolio_path=portfolio_file
    )

except ValueError as error:
    st.error(str(error))
    st.stop()

st.metric(
    "Total portfolio value",
    f"€{portfolio.get_total_value():,.2f}"
)

st.subheader("Portfolio overview")
positions_display=(
    portfolio
    .calculate_position_values()
    [
        [
            "instrument_id",
            "asset_name",
            "asset_class",
            "currency",
            "quantity",
            "latest_price",
            "market_value_eur",
            "weight"
        ]
    ]
    .copy()
)
positions_display["weight"] = (
    positions_display["weight"]/100
)
st.dataframe(
    positions_display,
    hide_index=True,
    width="stretch",
    column_config={
        "instrument_id": "Instrument ID",
        "asset_name": "Asset",
        "asset_class": "Asset class",
        "currency": "Currency",
        "quantity": st.column_config.NumberColumn(
            "Quantity",
            format="localized"
        ),
        "latest_price": st.column_config.NumberColumn(
            "Latest price",
            format="%.2f"
        ),
        "market_value_eur": st.column_config.NumberColumn(
            "Market value",
            format="euro"
        ),
        "weight": st.column_config.NumberColumn(
            "Weight",
            format="percent",
            step=0.0001
        )
    }
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
allocation_display = allocation_comparison.astype(float) / 100

st.dataframe(
    allocation_display,
    width="stretch",
    column_config={
        "actual": st.column_config.NumberColumn(
            "Actual",
            format="percent",
            step=0.0001
        ),
        "target": st.column_config.NumberColumn(
            "Target",
            format="percent",
            step=0.0001
        ),
        "deviation": st.column_config.NumberColumn(
            "Deviation",
            format="percent",
            step=0.0001
        )
    }
)
chart_data = allocation_comparison[
    ["actual", "target"]
]
st.bar_chart(
    chart_data,
    width="stretch"
)

st.subheader("Rebalancing recommendations")
alerts = monitor.generate_alerts()
alerts_df = pd.DataFrame(alerts)
if not alerts_df.empty:
    alerts_display = alerts_df.copy()
    alerts_display["deviation"] = pd.to_numeric(
    alerts_display["deviation"]
)/100
    alerts_display["amount"] = pd.to_numeric(
    alerts_display["amount"]
)
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
concentrations_display["market_value_eur"] = pd.to_numeric(
    concentrations_display["market_value_eur"]
)
if not concentrations_display.empty:
    st.dataframe(
        concentrations_display,
        hide_index=True,
        width="stretch",
        column_config={
            "instrument_id": "Instrument ID",
            "asset_name" : "Asset",
            "asset_class": "Asset class",
            "weight": st.column_config.NumberColumn(
                "Weight",
                format="percent",
                step=0.0001
            ),
            "market_value_eur": st.column_config.NumberColumn(
                "Market value",
                format="euro"
            )
        }
    )
else:
    st.success(
        "No position exceeds the concentration limit."
    )

st.subheader("Rebalancing simulator")
tradable_positions = portfolio.positions[
    portfolio.positions["asset_class"] != "Cash"
]
tradable_instruments = (
    tradable_positions["instrument_id"]
    .tolist()
)
selected_instrument = st.selectbox(
    "Select an instrument",
    tradable_instruments
)

selected_action = st.selectbox(
    "Select an action",
    ["BUY", "SELL"]
)

trade_quantity = st.number_input(
    "Trade quantity",
    min_value=0.01,
    value=1.0,
    step=1.0
)

if st.button("Simulate trade"):
    try:
        projected_positions = portfolio.simulate_trade(
            selected_instrument,
            selected_action,
            trade_quantity
        )

        current_allocation = portfolio.calculate_asset_class_allocation()
        project_allocation = portfolio.calculate_asset_class_allocation(projected_positions)
        allocation_comparison = pd.DataFrame({
            "Before": current_allocation,
            "After": project_allocation
        }).fillna(0)

        st.subheader("Projected allocation")
        st.dataframe(
            allocation_comparison.round(2),
            use_container_width=True
        )
        st.bar_chart(
            allocation_comparison,
            stack=False,
            use_container_width=True
        )
    except ValueError as error:
        st.error(str(error))