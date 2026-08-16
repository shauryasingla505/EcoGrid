import sys
import datetime
import os
import random
import threading
from flask import Flask, jsonify, make_response, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from predict_price import MarketPriceForecaster

# Force Python to look inside its own folder for neighboring flat modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Direct local imports from the same flat directory
try:
    from predict_solar import SolarPredictor
    from predict_demand import DemandPredictor
    from predict_forecast import ForecastPredictor
except ImportError as e:
    print(f"[WARNING] Local ML modules not found: {e}. Injecting resilient mock architecture.")
    class SolarPredictor:
        def predict_generation(self, **kwargs): return round(random.uniform(5.0, 25.0), 2)
    class DemandPredictor:
        def predict_current_demand(self): return round(random.uniform(30.0, 50.0), 2)
    class ForecastPredictor:
        def predict_next_hour(self, target_hour, prev_power): return round(random.uniform(30.0, 50.0), 2)

app = Flask(__name__)

# Apply global Cross-Origin Resource Sharing configuration
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Database configuration creating a persistent SQLite file
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecogrid_audit.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Explicit thread safety primitive for protecting shared global application states
state_lock = threading.Lock()

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.String(50), nullable=False)
    agent_action = db.Column(db.String(100), nullable=False)
    cost_saved = db.Column(db.Float, nullable=False)
    carbon_saved = db.Column(db.Float, nullable=False)

# Global memory states
battery_soc = 65.0  
historical_buffer = [42.5, 45.1, 43.8, 46.2]  

# Engine instantiation (incorporating our 4th Model)
solar_engine = SolarPredictor()
demand_engine = DemandPredictor()
forecast_engine = ForecastPredictor()  
price_forecaster = MarketPriceForecaster()  # 4th MODEL ACTIVATED!

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "status": "ONLINE",
        "system": "EcoGrid AI Smart Agent Backend Machine",
        "endpoints": {
            "telemetry_data": "/api/telemetry"
        }
    })

@app.route('/api/telemetry', methods=['GET', 'OPTIONS'])
def get_telemetry():
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        response.headers.add("Access-Control-Allow-Methods", "GET,OPTIONS")
        return response

    global battery_soc, historical_buffer
    
    now = datetime.datetime.now()
    current_hour = now.hour
    time_string = now.strftime("%H:%M:%S")
    
    with state_lock:
        # 1. PERCEIVE: Collect environmental signals via underlying ML wrappers
        predicted_solar = solar_engine.predict_generation(temperature=34.2, humidity=55, cloud_cover=15, hour=current_hour)
        predicted_demand = demand_engine.predict_current_demand()
        
        future_forecast = forecast_engine.predict_next_hour(
            target_hour=(current_hour + 1) % 24, 
            prev_power=predicted_demand
        )
        
        # 2. RUNNING 4th ML MODEL PRICE CALCULATIONS
        mock_grid_load = round(random.uniform(70.0, 88.0), 1)
        current_tariff = price_forecaster.forecast_next_hour_price(current_hour, mock_grid_load)
        future_price_trend = price_forecaster.get_price_trend_curve(current_hour)
        
        agent_logs = []
        agent_action = "GRID_ROUTING"
        
        is_peak_hour = current_tariff >= 8.5  
        saved_cost = 0.0
        carbon_deflected = 0.0
        
        agent_logs.append(f"[{time_string}] [PERCEIVE] Load forecast: {predicted_demand} kWh. Expected Solar: {predicted_solar} kWh.")
        agent_logs.append(f"[{time_string}] [MARKET FORECAST ENGINE] Current ML predicted grid tariff is ₹{current_tariff}/kWh (Grid Load: {mock_grid_load} MVA).")
        
        # 3. REASON, PLAN & ACT: Closed-loop autonomous execution logic
        if is_peak_hour and battery_soc > 20.0:
            agent_action = "DISCHARGING_BATTERY_RESERVE"
            energy_drawn = min(15.0, predicted_demand)  
            battery_soc = max(20.0, battery_soc - (energy_drawn / 10.0))  
            
            saved_cost = round(energy_drawn * (current_tariff - 2.5), 2) 
            carbon_deflected = round(energy_drawn * 0.85, 2) 
            
            agent_logs.append(f"[{time_string}] [ACT] Firing micro-relay. Battery reserve deployed to dodge peak market pricing.")
            
            try:
                new_log = AuditLog(
                    timestamp=time_string,
                    agent_action=agent_action,
                    cost_saved=saved_cost,
                    carbon_saved=carbon_deflected
                )
                db.session.add(new_log)
                db.session.commit()
            except Exception as db_err:
                db.session.rollback()
                agent_logs.append(f"[{time_string}] [DATABASE ERROR] Log rollback initiated: {str(db_err)}")
                
        elif predicted_solar > predicted_demand and battery_soc < 95.0:
            agent_action = "CHARGING_BATTERY_SOLAR"
            excess_solar = predicted_solar - predicted_demand
            battery_soc = min(100.0, battery_soc + (excess_solar / 10.0))
            agent_logs.append(f"[{time_string}] [ACT] Solar inverter switching topology to battery storage mode.")
        else:
            agent_logs.append(f"[{time_string}] [ACT] System loads balanced. Maintaining default utility grid bypass.")

        if random.random() > 0.80:
            historical_buffer.append(predicted_demand)
            if len(historical_buffer) > 4:
                historical_buffer.pop(0)

    # 4. AUDITING: Database aggregation execution optimized via native SQL functions
    try:
        total_savings = db.session.query(func.sum(AuditLog.cost_saved)).scalar() or 0.0
        total_carbon = db.session.query(func.sum(AuditLog.carbon_saved)).scalar() or 0.0
        total_savings = round(total_savings, 2)
        total_carbon = round(total_carbon, 2)
    except Exception as query_err:
        total_savings = 0.0
        total_carbon = 0.0
        print(f"Error querying aggregations: {query_err}")

    badge_unlocked = total_savings > 150.0
    current_score = 4.4 if total_savings > 100.0 else 3.2

    # 5. UI ADAPTER MAP: Build specific payload structures for the pricing engine
    pricing_strategy = "ARBITRAGE_DISCHARGE" if is_peak_hour and battery_soc > 20.0 else "STANDBY_GRID_BYPASS"
    pricing_tier = "PEAK_HIGH" if is_peak_hour else "NORMAL_OFF_PEAK"

    upcoming_blocks = []
    try:
        curve = future_price_trend if future_price_trend else [current_tariff] * 24
        upcoming_blocks = [
            { "time_slot": f"{(current_hour + 1) % 24:02d}:00 - {(current_hour + 2) % 24:02d}:00", "rate": round(curve[(current_hour + 1) % 24], 2), "type": "FORECAST_T1" },
            { "time_slot": f"{(current_hour + 2) % 24:02d}:00 - {(current_hour + 3) % 24:02d}:00", "rate": round(curve[(current_hour + 2) % 24], 2), "type": "FORECAST_T2" },
            { "time_slot": f"{(current_hour + 3) % 24:02d}:00 - {(current_hour + 4) % 24:02d}:00", "rate": round(curve[(current_hour + 3) % 24], 2), "type": "FORECAST_T3" }
        ]
    except Exception:
        upcoming_blocks = [
            { "time_slot": "Next Hour Block", "rate": round(current_tariff, 2), "type": "STABLE" }
        ]

    return jsonify({
        "current_time": now.strftime("%H:%M"),
        "metrics": {
            "grid_tariff": current_tariff,
            "is_peak_hour": is_peak_hour,
            "facility_demand": predicted_demand,
            "future_macro_forecast": future_forecast,  
            "solar_generation": predicted_solar,
            "battery_reserve": round(battery_soc, 2),
            "predicted_next_hour_tariff_inr": current_tariff
        },
        "dynamic_pricing": {
            "current_grid_rate_inr": current_tariff,
            "pricing_tier": pricing_tier,
            "market_strategy": pricing_strategy,
            "upcoming_tariffs": upcoming_blocks
        },
        "price_trend_graph": future_price_trend,  
        "agent": {
            "action": agent_action,
            "logs": agent_logs
        },
        "launchpad_status": {
            "current_score": current_score,
            "badge_unlocked": badge_unlocked,
            "total_savings_inr": total_savings,
            "carbon_saved_kg": total_carbon
        }
    })

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(port=5000, debug=True, threaded=True)