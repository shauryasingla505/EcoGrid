import pandas as pd
import joblib

model = joblib.load("models/demand_model.pkl")

features = [
    "Voltage",
    "Global_intensity",
    "Sub_metering_1",
    "Sub_metering_2",
    "Sub_metering_3"
]

importance = model.feature_importances_

for feature, score in zip(features, importance):
    print(f"{feature}: {score:.4f}")