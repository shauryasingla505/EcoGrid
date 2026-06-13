import pandas as pd
import joblib

model = joblib.load(
    "models/forecast_model.pkl"
)

sample = pd.DataFrame({
    "Hour": [18],
    "Day": [13],
    "Month": [6],
    "Weekday": [5],
    "Prev_Power": [4.8]
})

prediction = model.predict(sample)

predicted_demand = prediction[0]

print(
    "\nForecasted Demand:",
    round(predicted_demand, 2),
    "kW"
)

recommendations = []

if predicted_demand > 5:
    recommendations.append(
        "Shift EV charging to off-peak hours"
    )

    recommendations.append(
        "Use battery storage during peak load"
    )

if predicted_demand > 4:
    recommendations.append(
        "Schedule irrigation at night"
    )

print("\nRecommendations:")

for r in recommendations:
    print("-", r)