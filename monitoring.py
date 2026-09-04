import pandas as pd
from portfolio import Portfolio

class PortfolioMonitor:
    def __init__(self, portfolio, target_allocation, tolerance=5):
        self.portfolio = portfolio
        self.target_allocation = target_allocation
        self.tolerance = tolerance
    
    def compare_allocation(self):
        actual = self.portfolio.calculate_asset_class_allocation()
        
        target = pd.Series(
            self.target_allocation,
            name="target",
            dtype=float
        )
        
        comparison = pd.concat(
            [actual.rename("actual"), target],
            axis=1
        ).fillna(0)
        
        comparison["deviation"] = (
            comparison["actual"] - comparison["target"]
        )
        
        return comparison
    
    def generate_alerts(self):
        total_value = self.portfolio.get_total_value()
        comparison = self.compare_allocation()
        alerts = []
        
        for asset_class, row in comparison.iterrows():
            deviation = row["deviation"]
            
            if abs(deviation) > self.tolerance:
                if deviation > 0:
                    status = "overweight"
                    action = "SELL"
                else:
                    status = "underweight"
                    action = "BUY"
                
                trade_amount = abs(deviation) / 100 * total_value
                
                alerts.append({
                    "asset_class" : asset_class,
                    "status" : status,
                    "deviation" : deviation,
                    "action" : action,
                    "amount" : trade_amount.round(2)
                })
        return alerts
    
    def check_concentration(self, max_weight=20):
        positions = self.portfolio.calculate_position_values()
        
        concentrated = positions[
            positions["weight"] > max_weight
        ]
        
        return concentrated[
            ["asset", "weight", "market_value"]
        ].round(2)

def main():
    portfolio = Portfolio(
        holdings_path="data/holdings.csv",
        prices_path="data/prices.csv",
        benchmark="Benchmark"
    )

    targets = {
        "Equity": 50,
        "Bond": 40,
        "Cash": 10
    }

    monitor = PortfolioMonitor(
        portfolio=portfolio,
        target_allocation=targets,
        tolerance=5
    )

    print(monitor.compare_allocation().round(2))
    print(monitor.generate_alerts())
    print(monitor.check_concentration())

if __name__ == "__main__":
    main()