import pandas as pd
import numpy as np
from mpc_engine import ModelPredictiveController

def run_real_data_pipeline(data_path="datasets/household_power_consumption.txt"):
    print("⏳ Loading real household data stream...")
    # Read the dataset using the same parameters as your training script
    df = pd.read_csv(data_path, sep=';', low_memory=False, na_values=['?']).dropna()
    
    # Grab a real historical 24-hour window from the data
    # (Taking rows from index 50000 just to skip the initial setup rows)
    test_slice = df.iloc[50000:50024].copy()
    test_slice['Datetime'] = pd.to_datetime(test_slice['Date'] + ' ' + test_slice['Time'], dayfirst=True)
    
    mpc = ModelPredictiveController(battery_capacity_kwh=12.0, max_charge_rate_kw=4.0)
    current_soc = 2.0  # Start battery low
    
    print("\n🚀 Running Dynamic MPC over REAL Historical Dataset Stream\n")
    print(f"{'Time':<16} | {'Solar (kW)':<10} | {'Demand (kW)':<11} | {'Net Load':<8} | {'Price':<6} | {'MPC Action Decision':<30} | {'Battery SoC':<10}")
    print("-" * 115)
    
    for idx, row in test_slice.reset_index().iterrows():
        timestamp = row['Datetime']
        hour = timestamp.hour
        month = timestamp.month
        day_of_week = timestamp.dayofweek
        
        # Pull real live power consumption and voltage metrics from the CSV row
        real_global_power = float(row['Global_active_power'])
        real_voltage = float(row['Voltage'])
        
        # Calculate optimal action via MPC using actual real-time data inputs
        action_code, current_net_load, price = mpc.optimize_dispatch(
            current_soc=current_soc, 
            start_hour=hour, 
            month=month, 
            day_of_week=day_of_week, 
            base_power=real_global_power, 
            voltage=real_voltage
        )
        
        # State updates based on dynamic action assignment
        action_desc = "HOLD / BALANCE"
        if action_code == 1:
            action_desc = "PROACTIVE CHARGE (Grid)" if current_net_load > 0 else "CHARGE (Excess Solar)"
            current_soc = min(mpc.battery_capacity, current_soc + mpc.max_charge_rate)
        elif action_code == -1:
            action_desc = "PREEMPTIVE DISCHARGE"
            current_soc = max(0.0, current_soc - mpc.max_charge_rate)
            
        # Get real solar prediction for this specific historical timestamp row
        sol_now = mpc.solar_predictor.predict_generation(hour, month, day_of_week, real_global_power, real_voltage)
        
        print(f"{timestamp.strftime('%Y-%m-%d %H:%M')} | {sol_now:<10.2f} | {real_global_power:<11.2f} | {current_net_load:<8.2f} | ${price:<4.2f} | {action_desc:<30} | {current_soc:.2f} kWh")

if __name__ == "__main__":
    run_real_data_pipeline()