import pandas as pd
import joblib
import os

class EcoGridOptimizer:
    def __init__(self, model_path="models/forecast_model.pkl"):
        """Initializes and loads the trained ML model safely."""
        if os.path.exists(model_path):
            self.model = joblib.load(model_path)
            print(f" EcoGrid ML Model successfully loaded from {model_path}")
        else:
            self.model = None
            print(f" Warning: {model_path} not found. Running in fallback simulation mode.")

    def run_pipeline(self, features: dict, grid_context: dict) -> dict:
        """
        Executes the entire pipeline:
        1. Predicts demand using the ML model.
        2. Runs the smart optimization matrix against active grid variables.
        """
        # 1. ML Inference Stage
        predicted_demand = self._predict_demand(features)
        
        # 2. Extract Contextual Variables
        solar = grid_context.get("solar_generation", 0.0)
        battery = grid_context.get("battery_soc", 50)  # State of charge %
        tariff = grid_context.get("tariff_period", "standard").lower() # peak, standard, off-peak

        # 3. Compute Net Grid Load and Score
        net_grid_load = max(0, predicted_demand - solar)
        stress_score = self._calculate_stress(net_grid_load, tariff, battery)
        
        # 4. Generate Dynamic Decisions Matrix
        status, recommendations = self._generate_matrix(predicted_demand, solar, battery, tariff, net_grid_load, stress_score)

        # 5. Financial & Carbon Analytics
        base_rate = 8  # ₹ per kWh
        estimated_savings = round(predicted_demand * base_rate * (stress_score * 0.02), 2)
        co2_reduction_kg = round(solar * 0.82, 2)

        return {
            "predicted_demand_kw": round(predicted_demand, 2),
            "net_grid_load_kw": round(net_grid_load, 2),
            "grid_status": status,
            "stress_score": stress_score,
            "financials": {
                "estimated_savings_inr": estimated_savings,
                "co2_reduction_kg": co2_reduction_kg
            },
            "actions": recommendations
        }

    def _predict_demand(self, features: dict) -> float:
        """Handles ML inference or triggers an algorithmic fallback."""
        if self.model:
            try:
                sample_df = pd.DataFrame([{
                    "Hour": features.get("hour", 12),
                    "Day": features.get("day", 15),
                    "Month": features.get("month", 6),
                    "Weekday": features.get("weekday", 2),
                    "Prev_Power": features.get("prev_power", 3.5)
                }])
                return float(self.model.predict(sample_df)[0])
            except Exception as e:
                print(f"Inference error: {e}. Defaulting to fallback calculation.")
        
        # Fallback math proxy if model pipeline fails/is missing during testing
        return float(features.get("prev_power", 3.5) * 1.1)

    def _calculate_stress(self, net_load, tariff, battery) -> int:
        score = 0
        if net_load > 4: score += 4
        elif net_load > 2: score += 2
        
        if tariff == "peak": score += 4
        elif tariff == "standard": score += 1
        
        if battery < 30: score += 2
        return score

    def _generate_matrix(self, demand, solar, battery, tariff, net_load, score) -> tuple:
        recommendations = []
        
        if score >= 7: status = "CRITICAL / HIGH STRESS"
        elif score >= 4: status = "MODERATE STRESS"
        else: status = "OPTIMAL / LOW STRESS"

        if tariff == 'peak' and battery > 40:
            recommendations.append("Grid prices are PEAK. Discharging battery to power local loads and save costs.")
        
        if solar > demand and battery < 95:
            recommendations.append(f"Surplus solar detected (+{round(solar - demand, 2)} kW). Routing excess power to top up battery storage.")
        elif solar > demand and battery >= 95:
            recommendations.append("Renewable surplus available and battery full. Initiating net-metering grid export for credit.")

        if net_load > 4 and tariff == 'peak':
            recommendations.append("Heavy demand spike projected during peak pricing. Automating demand-response: postponing EV charging and heavy appliances.")
            
        if tariff == 'off-peak' and battery < 80:
            recommendations.append("Grid electricity is cheap (Off-Peak). Fast-charging battery reserves from the grid for upcoming peak hours.")

        if not recommendations:
            recommendations.append("System stable. Running on balanced grid-solar-battery mix.")

        return status, recommendations