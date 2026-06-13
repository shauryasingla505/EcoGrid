import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score

def train_solar_model(data_path="datasets/household_power_consumption.txt", model_output_path="models/solar_model.pkl"):
    print("⏳ Loading Household Power Consumption dataset...")
    
    # Read UCI dataset (semicolon-separated, handles '?' as NaN)
    df = pd.read_csv(data_path, sep=';', low_memory=False, na_values=['?'])
    
    print("🧹 Cleaning data and engineering solar features...")
    # Drop rows with missing values
    df = df.dropna()
    
    # Create a proper datetime column
    df['Datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], dayfirst=True)
    
    # Extract time features
    df['Hour'] = df['Datetime'].dt.hour
    df['Month'] = df['Datetime'].dt.month
    df['DayOfWeek'] = df['Datetime'].dt.dayofweek
    
    # Convert technical columns to float
    df['Global_active_power'] = df['Global_active_power'].astype(float)
    df['Voltage'] = df['Voltage'].astype(float)
    
    # HACK: Synthesize a realistic solar generation target based on time of day
    # Solar peaks at 12 PM to 1 PM, depends roughly on seasonal changes (Month), and is 0 at night.
    # We add a bit of random variance to simulate cloud cover.
    np.random.seed(42)
    solar_profile = np.sin((df['Hour'] - 6) / 12 * np.pi)  # Bell curve between 6 AM and 6 PM
    solar_profile = np.clip(solar_profile, 0, None)       # Zero out night hours
    
    # Scale it to look like a standard 3kW to 5kW home solar array with some noise
    df['solar_output'] = solar_profile * 4.0 * np.random.uniform(0.7, 1.0, len(df))
    
    # Define features and target
    features = ['Hour', 'Month', 'DayOfWeek', 'Global_active_power', 'Voltage']
    X = df[features]
    y = df['solar_output']
    
    # Take a subset if the dataset is too massive to train quickly during the hackathon
    if len(X) > 100000:
        X, _, y, _ = train_test_split(X, y, train_size=100000, random_state=42)
    
    # Train/Test Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("🚀 Training Solar Regressor...")
    model = RandomForestRegressor(n_estimators=50, max_depth=12, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    
    # Evaluate
    predictions = model.predict(X_test)
    print("✅ Training Complete!")
    print(f"📊 Mean Absolute Error: {mean_absolute_error(y_test, predictions):.3f} kW")
    print(f"📊 R² Score: {r2_score(y_test, predictions):.4f}")
    
    # Save model
    joblib.dump(model, model_output_path)
    print(f"💾 Solar model saved to '{model_output_path}'")

if __name__ == "__main__":
    train_solar_model()