# import pandas as pd
# import matplotlib.pyplot as plt
# import seaborn as sns

# # Load data
# df = pd.read_csv("sat_results.csv")

# # Plot 1: Time vs Filename
# plt.figure(figsize=(10, 5))
# sns.barplot(x="filename", y="time_sec", data=df)
# plt.xticks(rotation=45, ha='right')
# plt.title("Execution Time by Filename")
# plt.ylabel("Time (sec)")
# plt.tight_layout()
# plt.show()

# # Plot 2: Peak Memory vs Filename
# plt.figure(figsize=(10, 5))
# sns.barplot(x="filename", y="peak_mem_kb", data=df)
# plt.xticks(rotation=45, ha='right')
# plt.title("Peak Memory Usage by Filename")
# plt.ylabel("Memory (kB)")
# plt.tight_layout()
# plt.show()

# # Plot 3: Scatter Plot - Time vs Memory
# plt.figure(figsize=(6, 6))
# sns.scatterplot(x="peak_mem_kb", y="time_sec", hue="result", data=df)
# plt.title("Time vs. Memory Usage")
# plt.xlabel("Peak Memory (kB)")
# plt.ylabel("Time (sec)")
# plt.tight_layout()
# plt.show()



import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the CSV file
df = pd.read_csv("walksat_results.csv")

# --- Plot 1: Execution Time per File ---
plt.figure(figsize=(10, 4))
sns.lineplot(x=df.index, y="time_sec", data=df, color="blue")
plt.title("Execution Time per File")
plt.xlabel("File Index")
plt.ylabel("Time (seconds)")
plt.tight_layout()
plt.show()

# --- Plot 2: Peak Memory per File ---
plt.figure(figsize=(10, 4))
sns.lineplot(x=df.index, y="peak_mem_kb", data=df, color="green")
plt.title("Peak Memory Usage per File")
plt.xlabel("File Index")
plt.ylabel("Memory (kB)")
plt.tight_layout()
plt.show()

# --- Plot 3: Time vs Memory Scatter Plot ---
plt.figure(figsize=(8, 6))
sns.scatterplot(x="peak_mem_kb", y="time_sec", data=df, alpha=0.6, color="purple")
plt.title("Execution Time vs. Peak Memory Usage")
plt.xlabel("Peak Memory (kB)")
plt.ylabel("Time (seconds)")
plt.tight_layout()
plt.show()
