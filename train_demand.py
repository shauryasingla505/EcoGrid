import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error

# Load Dataset - Optimized with nrows to save RAM and time
print("Loading data...")
df = pd.read_csv(
    r"D:\ecogrid\datasets\household_power_consumption.txt",
    sep=";",
    low_memory=False,
    nrows=100000  # <--- CRITICAL: Prevents your laptop from crashing/freezing
)

# Clean Dataset
df.replace("?", pd.NA, inplace=True)
df = df.dropna()

# Convert columns to numbers
cols = [
    "Global_active_power",
    "Voltage",
    "Global_intensity",
    "Sub_metering_1",
    "Sub_metering_2",
    "Sub_metering_3"
]

for col in cols:
    df[col] = pd.to_numeric(df[col])

# Features (Inputs)
X = df[
    [
        "Voltage",
        "Global_intensity",
        "Sub_metering_1",
        "Sub_metering_2",
        "Sub_metering_3"
    ]
]

# Target (Output)
y = df["Global_active_power"]

# Train-Test Split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

print(f"Training model on {len(X_train)} rows...")

# Model - Optimized with parallel processing cores
model = RandomForestRegressor(
    n_estimators=50,
    random_state=42,
    n_jobs=-1  # <--- CRITICAL: Uses all CPU cores to speed up training dramatically
)

model.fit(X_train, y_train)

# Predictions
predictions = model.predict(X_test)

# Metrics
r2 = r2_score(y_test, predictions)
mae = mean_absolute_error(y_test, predictions)

print("\nResults")
print("R2 Score:", r2)
print("MAE:", mae)

os.makedirs("models", exist_ok=True)
joblib.dump(model, "models/demand_model.pkl")

print("\nModel saved successfully at models/demand_model.pkl!")