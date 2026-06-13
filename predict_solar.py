import joblib
import pandas as pd
import numpy as np
import os

class SolarPredictor:
    def __init__(self, model_path="models/solar_model.pkl"):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"❌ Model file not found at {model_path}. Run train_solar.py first!")
        self.model = joblib.load(model_path)
        self.features = ['Hour', 'Month', 'DayOfWeek', 'Global_active_power', 'Voltage']

    def predict_generation(self, hour, month, day_of_week, global_active_power, voltage):
        """
        Predicts solar power generation based on temporal parameters and house consumption metrics.
        """
        input_data = pd.DataFrame([{
            'Hour': hour,
            'Month': month,
            'DayOfWeek': day_of_week,
            'Global_active_power': global_active_power,
            'Voltage': voltage
        }])
        
        # Hard constraint: No solar generation possible at night
        if hour < 6 or hour > 19:
            return 0.0
            
        prediction = self.model.predict(input_data[self.features])[0]
        return max(0.0, float(prediction))

if __name__ == "__main__":
    try:
        predictor = SolarPredictor()
        # Test case: Sunny afternoon, medium house load, normal voltage
        sample_pred = predictor.predict_generation(
            hour=13, 
            month=7, 
            day_of_week=2, 
            global_active_power=1.5, 
            voltage=240.0
        )
        print(f"☀️ Predicted Solar Output: {sample_pred:.2f} kW")
    except Exception as e:
        print(str(e))