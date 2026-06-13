def carbon_reduction(predicted_demand):

    carbon_factor = 0.82

    reduction = predicted_demand * carbon_factor * 0.10

    return round(reduction, 2)


print(
    "Estimated CO2 Reduction:",
    carbon_reduction(5.4),
    "kg"
)