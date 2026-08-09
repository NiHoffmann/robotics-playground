import subprocess
import matplotlib.pyplot as plt

try:
    result = subprocess.run(["./amplitude_sweep"], capture_output=True, text=True, check=True)
except subprocess.CalledProcessError as e:
    print("Error running ./amplitude_sweep:", e)
    exit(1)

x_vals = []
y_vals = []

for line in result.stdout.strip().split('\n'):
    if line.strip():
        try:
            x_str, y_str = line.strip().split(',')
            x = float(x_str)
            y = float(y_str)
            x_vals.append(x)
            y_vals.append(y)
        except ValueError:
            print(f"Skipping malformed line: {line}")

plt.figure(figsize=(8, 5))
plt.plot(x_vals, y_vals, marker='o')
plt.title("Synchronization Amplitude vs. Coupling Radius")
plt.xlabel("Distance (r)")
plt.ylabel("Amplitude")
plt.grid(True)
plt.tight_layout()
plt.savefig("amplitude_sweep.png")
