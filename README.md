# Portfolio Decision Support

A Python and Streamlit application that analyzes a portfolio, compares its
current asset allocation with user-defined targets, and generates rebalancing
recommendations and concentration-risk alerts.

## Features

- Dynamic CSV file upload
- Portfolio valuation using the latest available prices
- Actual versus target allocation comparison
- Rebalancing recommendations
- Position concentration-risk detection
- Benchmark selection
- Interactive Streamlit interface

## Required CSV structure

### Holdings file

Required columns:

- `asset`
- `asset_class`
- `quantity`

### Price history file

- A `date` column
- One column for every asset in the holdings file
- At least one benchmark column

## Run locally

Install the dependencies:

```bash
pip install -r requirements.txt
```

Launch the application:

```bash
streamlit run app.py
```
