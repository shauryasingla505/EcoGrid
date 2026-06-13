import pandas as pd
import joblib

model = joblib.load("models/forecast_model.pkl")

sample = pd.DataFrame({
    "Hour": [18],
    "Day": [13],
    "Month": [6],
    "Weekday": [5],
    "Prev_Power": [4.8]
})

prediction = model.predict(sample)

print("Forecasted Demand:", prediction[0])