import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error

print("Loading dataset...")

# 1. Hardcoded absolute path override
df = pd.read_csv(
    r"D:\ecogrid\datasets\household_power_consumption.txt",
    sep=";",
    low_memory=False,
    nrows=150000 # Read slightly more rows to account for dropping NaNs cleanly
)

df.replace("?", pd.NA, inplace=True)
df = df.dropna()

df["Global_active_power"] = pd.to_numeric(df["Global_active_power"])

# Parse timestamps sequentially
df["Datetime"] = pd.to_datetime(df["Date"] + " " + df["Time"], dayfirst=True)
df["Hour"] = df["Datetime"].dt.hour
df["Day"] = df["Datetime"].dt.day
df["Month"] = df["Datetime"].dt.month
df["Weekday"] = df["Datetime"].dt.weekday

# Lag Feature (Crucial time-series context column)
df["Prev_Power"] = df["Global_active_power"].shift(1)
df = df.dropna()

# 2. FIXED: Take a consecutive chunk of 100k rows to preserve chronological integrity
sample_df = df.head(100000)

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

# Split data (For standard hackathon presentation, 80/20 train/test holds)
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    shuffle=False # Maintain sequence chronology for a true real-world simulation!
)

print(f"Training Forecast V3 on {len(X_train)} sequential records...")

# 3. Optimized with parallel core processing
model = RandomForestRegressor(
    n_estimators=50,
    random_state=42,
    n_jobs=-1 # Speed boost for your laptop cores
)

model.fit(X_train, y_train)
predictions = model.predict(X_test)

print("\nForecast V3 True Results")
print("R2:", r2_score(y_test, predictions))
print("MAE:", mean_absolute_error(y_test, predictions))

os.makedirs("models", exist_ok=True)
joblib.dump(model, "models/forecast_model.pkl")

print("\nForecast model natively saved at models/forecast_model.pkl!")