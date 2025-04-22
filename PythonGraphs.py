import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import random

# Load your CSV file
df = pd.read_csv(r"C:\Users\lucas\Documents\Transposed_WAR_Data.csv")

# Transpose the data so that players are rows and dates are columns
df_transposed = df.set_index("Date").T
df_transposed.index.name = "Name"
df_transposed.reset_index(inplace=True)

# Melt the DataFrame to long format
df_melted = df_transposed.melt(id_vars="Name", var_name="Date", value_name="WAR")
df_melted["Date"] = pd.to_datetime(df_melted["Date"])
latest_date = df_melted["Date"].max()

# Set up color palette
colors = cm.get_cmap('tab20', df_melted["Name"].nunique())

# Manual Y-offset adjustments to prevent label overlap
manual_adjustments = {
    "Alonso": 0.0,
    "Lindor": 0.0,
    "Soto": 0.1,
    "Acuna": -0.01,
    "Baty": .05,
    "Torrens": -0.04,
    "Senger": -0.06,
    "Marte": -0.01,
    "Winker": 0.02,
    "Nimmo": -0.12,
    'Winker': .02,
    "Taylor": -0.14,
    "Vientos": -0.1
}

# Set up plot
plt.style.use("dark_background")
plt.figure(figsize=(14, 8))
random.seed(42)
jitter_options = [0.0, 0.005, -0.005, 0.01, -0.01, 0.015, -0.015, 0.02, -0.02, 0.025, -0.025, 0.03, -0.03]

# Plot WAR lines
for i, (name, group) in enumerate(df_melted.groupby("Name")):
    jitter = random.choice(jitter_options)
    jittered_war = group["WAR"].values + jitter

    plt.plot(group["Date"].values, jittered_war, color=colors(i), linewidth=4)

    # Label at latest point
    latest_point = group[group["Date"] == latest_date]
    if not latest_point.empty:
        y_val = latest_point["WAR"].values[0] + jitter
        adjusted_y = y_val + manual_adjustments.get(name, 0.0)

        plt.text(
            latest_point["Date"].values[0] + np.timedelta64(2, 'D'),
            adjusted_y,
            name,
            fontsize=16,
            color=colors(i),
            verticalalignment='center'
        )

# Add baseline and labels
plt.axhline(0, color='white', linestyle='--', linewidth=1)
plt.title("Mets WAR Over Time", fontsize=18)
plt.xlabel("Date", fontsize=18)
plt.ylabel("WAR", fontsize=18)
plt.grid(True, color='gray', linestyle='--', linewidth=0.5)
plt.xticks(rotation=45)
plt.subplots_adjust(right=0.85)
plt.text(
    0.01, 0.03,
    "Source: Fangraphs",
    transform=plt.gcf().transFigure,
    fontsize=7,
    color='white',
    ha='left',
    va='bottom'
)

plt.text(
    0.01, 0.01,
    "@LinkofSunshine",
    transform=plt.gcf().transFigure,
    fontsize=7,
    color='white',
    ha='left',
    va='bottom'
)

plt.show()
