# Portfolio Decision Support

A Python and Streamlit application for portfolio allocation analysis, rebalancing recommendations, concentration-risk monitoring, and trade simulation.

## Live application

[Open the Streamlit application](https://portfolio-decision-support.streamlit.app)

## Features

- Upload a single portfolio CSV
- Validate portfolio structure and data quality
- Review positions and total portfolio value
- Compare actual allocation with user-defined targets
- Generate rebalancing recommendations
- Identify concentrated positions
- Simulate purchases and sales using the available cash position
- Visualize the projected allocation after a simulated trade

## CSV structure

### Required columns

| Column | Description |
| --- | --- |
| `portfolio_id` | Portfolio identifier |
| `valuation_date` | Portfolio valuation date |
| `instrument_id` | Unique instrument identifier |
| `asset_name` | Instrument name |
| `asset_class` | Asset class, such as Equity, Bond, or Cash |
| `currency` | Instrument currency |
| `quantity` | Position quantity |
| `latest_price` | Latest instrument price |
| `market_value_eur` | Position market value in euros |

### Optional columns

The sample file also contains `isin` and `ticker`. These fields can enrich the portfolio export but are not required by the application.

The file must contain one portfolio, one valuation date, unique instrument identifiers, and exactly one cash position.

A sample file is available under `data/portfolio_export_v2.csv`.

## Run locally

Install the dependencies:

```bash
pip install -r requirements.txt
```

Launch the application:

```bash
streamlit run app.py
```

## Project structure

```text
app.py          Streamlit user interface
portfolio.py    Portfolio validation, calculations, and trade simulation
monitoring.py   Allocation comparison, alerts, and concentration checks
data/           Sample portfolio export
```

## Scope

This project is a decision-support prototype created for demonstration and learning purposes. It does not provide investment advice or connect to live custody or market-data systems.