import pandas as pd

class Portfolio:
    def __init__(self, portfolio_path):
        self.portfolio_path = portfolio_path
        self.positions = self.load_positions()

    def load_positions(self):
        positions = pd.read_csv(
            self.portfolio_path
        )
        
        required_columns = [
            "portfolio_id",
            "valuation_date",
            "isin",
            "ticker",
            "asset_name",
            "asset_class",
            "currency",
            "quantity",
            "latest_price",
            "market_value_eur",
            "instrument_id"
        ]
        missing_columns = [
            column
            for column in required_columns
            if column not in positions.columns
        ]
        if missing_columns:
            raise ValueError(
                f"Missing columns: {', '.join(missing_columns)}"
            )
        
        if positions.empty:
            raise ValueError(
                "The portfolio is empty."
            )
        
        mandatory_columns = [
            "portfolio_id",
            "valuation_date",
            "instrument_id",
            "asset_name",
            "asset_class",
            "currency",
            "quantity",
            "latest_price",
            "market_value_eur"
        ]
        
        if positions[mandatory_columns].isna().any().any():
            raise ValueError("Missing values found in mandatory fields.")
        
        positions["valuation_date"] = pd.to_datetime(
            positions["valuation_date"],
            errors="coerce"
        )
        if positions["valuation_date"].isna().any():
            raise ValueError("Invalid valuation date.")
        
        numeric_columns = [
            "quantity",
            "latest_price",
            "market_value_eur"
        ]
        for column in numeric_columns:
            positions[column] = pd.to_numeric(
                positions[column],
                errors="coerce"
            )
            
            if positions[column].isna().any():
                raise ValueError(
                    f"{column} must contain numeric values."
                )
        if (positions["quantity"]<=0).any():
            raise ValueError("Quantities must be positive.")
        if (positions["latest_price"]<=0).any():
            raise ValueError("Prices must be positive.")
        if (positions["market_value_eur"]<=0).any():
            raise ValueError("Market values must be positive.")
        
        if positions["portfolio_id"].nunique() != 1:
            raise ValueError("The file must contain exactly one portfolio.")
        if positions["valuation_date"].nunique() != 1:
            raise ValueError("The file must contain exactly one valuation date.")
        if positions["instrument_id"].duplicated().any():
            raise ValueError("Duplicate instruments found.")
          
        return positions
        
    def calculate_position_values(self):
        positions = self.positions.copy()
        total_value = positions["market_value_eur"].sum()
        
        positions["weight"] = (
            positions["market_value_eur"] / total_value*100
        )
        
        return positions
    
    def get_total_value(self):
        return self.positions["market_value_eur"].sum()
    
    def calculate_asset_class_allocation(self):
        allocation = (
            self.positions
            .groupby("asset_class")["market_value_eur"]
            .sum()
        )
        allocation = allocation / allocation.sum()*100
        return allocation.round(2)

def main():
    portfolio = Portfolio(
        portfolio_path="data/portfolio_export_v2.csv"
    )

    print(portfolio.calculate_position_values())
    print(f"Total value: {portfolio.get_total_value():,.2f}")
    print(portfolio.calculate_asset_class_allocation())

if __name__ == "__main__":
    main()