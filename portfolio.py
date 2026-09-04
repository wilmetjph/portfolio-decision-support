import pandas as pd

class Portfolio:
    def __init__(self, holdings_path, prices_path, benchmark):
        self.holdings_path = holdings_path
        self.prices_path = prices_path
        self.benchmark = benchmark

        self.holdings = self.load_holdings()
        self.prices = self.load_prices()

    def load_holdings(self):
        holdings = pd.read_csv (
            self.holdings_path
        )
        
        required_columns = ["asset", "asset_class", "quantity"]
        missing_columns = [
            column
            for column in required_columns
            if column not in holdings.columns
        ]
        if missing_columns:
            raise ValueError("Missing columns")
              
        if holdings["asset"].duplicated().any():
            raise ValueError("Duplicate values found.")

        if holdings.isna().any().any():
            raise ValueError("Missing values found.")
        
        quantities = pd.to_numeric(holdings["quantity"], errors="coerce")
        if quantities.isna().any():
            raise ValueError("Quantities must be numeric.")
        holdings["quantity"] = quantities
        
        if (holdings["quantity"]<=0).any():
            raise ValueError("Quantities must be positive.")
        
        return holdings
    
    def load_prices(self):
        prices = pd.read_csv(
            self.prices_path,
            parse_dates=["date"],
            index_col="date"
        )
        
        if prices.empty:
            raise ValueError("Prices file is empty.")
            
        if prices.isna().any().any():
            raise ValueError("Missing prices found.")
        
        held_assets = set(self.holdings["asset"])
        available_assets = set(prices.columns)
        missing_assets = held_assets - available_assets
        
        if missing_assets:
            raise ValueError(f"Missing price data for: {missing_assets}")
        if self.benchmark not in prices.columns:
            raise ValueError("No data for benchmark")
        
        prices = prices.sort_index()
        
        return prices
    
    def get_latest_prices(self):
        return self.prices.iloc[-1]
    
    def calculate_position_values(self):
        holdings = self.holdings.copy()
        latest_prices = self.get_latest_prices()
        
        holdings["latest_price"] = holdings["asset"].map(latest_prices)
        holdings["market_value"] = (
            holdings["quantity"] * holdings["latest_price"]
        )
        
        total_value = holdings["market_value"].sum()
        holdings["weight"] = (
            holdings["market_value"] / total_value * 100
        )
        
        return holdings
    
    def get_total_value(self):
        positions = self.calculate_position_values()
        return positions["market_value"].sum()
    
    def calculate_asset_class_allocation(self):
        positions = self.calculate_position_values()
        allocation = (
            positions.groupby("asset_class")["market_value"].sum()
        )
        allocation = allocation / allocation.sum()*100
        return allocation.round(2)

def main():
    portfolio = Portfolio(
        holdings_path="data/holdings.csv",
        prices_path="data/prices.csv",
        benchmark="Benchmark"
    )

    print(portfolio.calculate_position_values())
    print(f"Total value: {portfolio.get_total_value():,.2f}")
    print(portfolio.calculate_asset_class_allocation())


if __name__ == "__main__":
    main()