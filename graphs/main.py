import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


df = pd.read_csv("walksat_results.csv")


plt.figure(figsize=(10, 4))
sns.lineplot(x=df.index, y="time_sec", data=df, color="blue")
plt.title("Execution Time per File")
plt.xlabel("File Index")
plt.ylabel("Time (seconds)")
plt.tight_layout()
plt.show()


plt.figure(figsize=(10, 4))
sns.lineplot(x=df.index, y="peak_mem_kb", data=df, color="green")
plt.title("Peak Memory Usage per File")
plt.xlabel("File Index")
plt.ylabel("Memory (kB)")
plt.tight_layout()
plt.show()


plt.figure(figsize=(8, 6))
sns.scatterplot(x="peak_mem_kb", y="time_sec", data=df, alpha=0.6, color="purple")
plt.title("Execution Time vs. Peak Memory Usage")
plt.xlabel("Peak Memory (kB)")
plt.ylabel("Time (seconds)")
plt.tight_layout()
plt.show()
