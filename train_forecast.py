import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error

print("Loading dataset...")

df = pd.read_csv(
    "datasets/household_power_consumption.txt",
    sep=";",
    low_memory=False
)

df.replace("?", pd.NA, inplace=True)
df = df.dropna()

df["Global_active_power"] = pd.to_numeric(
    df["Global_active_power"]
)

df["Datetime"] = pd.to_datetime(
    df["Date"] + " " + df["Time"],
    dayfirst=True
)

df["Hour"] = df["Datetime"].dt.hour
df["Day"] = df["Datetime"].dt.day
df["Month"] = df["Datetime"].dt.month
df["Weekday"] = df["Datetime"].dt.weekday

# Lag Feature
df["Prev_Power"] = df["Global_active_power"].shift(1)

df = df.dropna()

sample_df = df.sample(
    n=100000,
    random_state=42
)

X = sample_df[
    [
        "Hour",
        "Day",
        "Month",
        "Weekday",
        "Prev_Power"
    ]
]

y = sample_df["Global_active_power"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

print("Training Forecast V3...")

model = RandomForestRegressor(
    n_estimators=50,
    random_state=42
)

model.fit(X_train, y_train)

predictions = model.predict(X_test)

print("\nForecast V3 Results")
print("R2:", r2_score(y_test, predictions))
print("MAE:", mean_absolute_error(y_test, predictions))
import joblib
import os

os.makedirs("models", exist_ok=True)

joblib.dump(model, "models/forecast_model.pkl")

print("\nForecast model saved!")