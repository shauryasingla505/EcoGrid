def calculate_savings(predicted_demand):

    base_cost_per_kwh = 8  # ₹

    if predicted_demand > 5:
        savings = predicted_demand * base_cost_per_kwh * 0.15

    elif predicted_demand > 3:
        savings = predicted_demand * base_cost_per_kwh * 0.08

    else:
        savings = predicted_demand * base_cost_per_kwh * 0.03

    return round(savings, 2)


predicted_demand = 5.4

print(
    "Estimated Daily Savings: ₹",
    calculate_savings(predicted_demand)
)