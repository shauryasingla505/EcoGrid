import pandas as pd
import joblib

model = joblib.load("models/demand_model.pkl")

new_data = pd.DataFrame({
    "Voltage": [235],
    "Global_intensity": [15],
    "Sub_metering_1": [0],
    "Sub_metering_2": [1],
    "Sub_metering_3": [17]
})

prediction = model.predict(new_data)

print("Predicted Power Consumption:")
print(prediction[0])