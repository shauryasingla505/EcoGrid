import pandas as pd
import matplotlib.pyplot as plt

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

sample = df["Global_active_power"].head(1000)

plt.plot(sample)
plt.title("Power Consumption Trend")
plt.xlabel("Time")
plt.ylabel("Power")
plt.show()