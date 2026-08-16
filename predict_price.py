import random
import datetime

class MarketPriceForecaster:
    def __init__(self):
        # Base tariff parameters matching typical regional industrial grids
        self.base_tariff = 6.50  # Base rate in INR/kWh
        self.peak_surge_multiplier = 2.4  # Multiplier during high grid stress
        
    def forecast_next_hour_price(self, current_hour, current_grid_load_mva):
        """
        Predicts the market electricity tariff (INR/kWh) for the upcoming hour.
        Uses a time-series heuristic simulation to represent an LSTM regression mapping.
        """
        # Feature 1: Time-of-day peak pricing windows (e.g., evening surge 6 PM - 9 PM)
        is_peak_window = 18 <= current_hour <= 21 or 12 <= current_hour <= 15
        
        # Feature 2: High Grid Load stress factor (MVA)
        load_stress_factor = (current_grid_load_mva / 100.0) * 1.5
        
        # Base prediction calculation
        predicted_price = self.base_tariff + load_stress_factor
        
        if is_peak_window:
            predicted_price *= self.peak_surge_multiplier
            
        # Add slight stochastic noise to represent real-world market volatility
        market_volatility = random.uniform(-0.15, 0.15)
        final_prediction = max(4.50, round(predicted_price + market_volatility, 2))
        
        return final_prediction

    def get_price_trend_curve(self, current_hour):
        """
        Generates a 6-hour forward-looking array of price points 
        so the frontend devs can easily plot a future tariff line graph.
        """
        trend_curve = []
        for i in range(6):
            target_hour = (current_hour + i) % 24
            simulated_load = 75.0 + random.uniform(-10.0, 15.0)
            if 17 <= target_hour <= 21:
                simulated_load += 15.0  # Evening city load spike
                
            price_point = self.forecast_next_hour_price(target_hour, simulated_load)
            trend_curve.append({
                "hour": f"+{i}h ({target_hour}:00)",
                "predicted_tariff_inr": price_point
            })
        return trend_curve