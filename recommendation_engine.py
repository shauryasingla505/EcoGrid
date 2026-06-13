def generate_recommendations(
    predicted_demand,
    solar_generation,
    battery_level,
    tariff
):
    recommendations = []

    if predicted_demand > 5:
        recommendations.append(
            "High demand expected. Shift non-critical loads."
        )

    if solar_generation > predicted_demand:
        recommendations.append(
            "Use available solar energy before grid power."
        )

    if battery_level > 70:
        recommendations.append(
            "Use stored battery energy during peak hours."
        )

    if tariff == "peak":
        recommendations.append(
            "Delay heavy appliances until off-peak pricing."
        )

    return recommendations


recs = generate_recommendations(
    predicted_demand=5.4,
    solar_generation=3.2,
    battery_level=85,
    tariff="peak"
)

for r in recs:
    print("-", r)