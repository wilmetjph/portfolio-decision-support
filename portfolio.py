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
            "instrument_id",
            "asset_name",
            "asset_class",
            "currency",
            "quantity",
            "latest_price",
            "market_value_eur",
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

    def calculate_asset_class_allocation(
            self,
            positions=None
        ):
            if positions is None:
                positions = self.positions

            allocation = (
                positions
                .groupby("asset_class")["market_value_eur"]
                .sum()
            )

            allocation = (
                allocation
                / allocation.sum()
                * 100
            )

            return allocation.round(2)

    def get_portfolio_id(self):
        return self.positions[
            "portfolio_id"
        ].iloc[0]

    def get_valuation_date(self):
        return self.positions[
            "valuation_date"
        ].iloc[0]

    def simulate_trade(
        self,
        instrument_id,
        action,
        quantity
    ):
        projected_positions = self.positions.copy()

        action = action.upper()
        if action not in ["BUY", "SELL"]:
            raise ValueError("Action must be BUY or SELL")
        if quantity<=0:
            raise ValueError("Trade quantity must be positive.")

        instrument_exists = (
            projected_positions["instrument_id"] == instrument_id
        ).any()
        if not instrument_exists:
            raise ValueError("Instrument not found.")

        instrument_mask = (
            projected_positions["instrument_id"] == instrument_id
        )
        instrument_index = projected_positions[instrument_mask].index[0]
        selected_position = projected_positions.loc[instrument_index]

        if selected_position["asset_class"] == "Cash":
            raise ValueError("Cash cannot be selected as the traded instrument.")
        cash_positions = projected_positions[projected_positions["asset_class"] == "Cash"]
        if len(cash_positions) != 1:
            raise ValueError("The portfolio must contain exactly one cash position.")
        cash_index = cash_positions.index[0]
        current_quantity = selected_position["quantity"]
        unit_value_eur = (
            selected_position["market_value_eur"]/current_quantity
        )
        trade_value_eur = quantity * unit_value_eur

        if action=="SELL" and quantity>current_quantity:
            raise ValueError("Sell quantity exceeds the current position.")
        available_cash = projected_positions.loc[
            cash_index,
            "market_value_eur"
        ]

        if action=="BUY" and trade_value_eur>available_cash:
            raise ValueError("Insufficient cash for this purchase.")

        direction = 1 if action == "BUY" else -1

        projected_positions.loc[
            instrument_index,
            "quantity"
        ] += direction*quantity

        projected_positions.loc[
            instrument_index,
            "market_value_eur"
        ] += direction*trade_value_eur

        projected_positions.loc[
            cash_index,
            "quantity"
        ] -= direction*trade_value_eur

        projected_positions.loc[
            cash_index,
            "market_value_eur"
        ] -= direction*trade_value_eur

        return projected_positions

def main():
    portfolio = Portfolio(
        portfolio_path="data/portfolio_export_v2.csv"
    )

    projected_positions = portfolio.simulate_trade(
        instrument_id="MSFT",
        action="BUY",
        quantity=5
    )

    display_columns = [
        "instrument_id",
        "quantity",
        "market_value_eur"
    ]

    print("Initial allocation:")
    print(portfolio.calculate_asset_class_allocation())
    print("Projected allocation:")
    print(portfolio.calculate_asset_class_allocation(projected_positions))

if __name__ == "__main__":
    main()