# import math

# pixel = 0.248  # Pixel size in mm

# groups = [18, 10, 9, 8, 7, 6, 5, 4, 3]
# line_spacing = [i * pixel for i in groups]  # Compute line spacing directly

# obj_distance = 770  # Object distance in mm

# # Compute angular resolutions in radians and degrees
# angular_resolutions_rad = [math.atan(i / obj_distance) for i in line_spacing]
# angular_resolutions_deg = [math.degrees(res) for res in angular_resolutions_rad]

# # Print formatted results
# print("Angular Resolutions (Radians):", [f"{res:.2f}" for res in angular_resolutions_rad])
# print("Angular Resolutions (Degrees):", [f"{res:.2f}" for res in angular_resolutions_deg])


import math
import numpy as np
import matplotlib.pyplot as plt

# Given constants
a = -5.802 * 10**-7
b = 3.90802 * 10**-3
c = -0.1

discriminant = b**2 - 4*a*c
T1 = (-b + math.sqrt(discriminant)) / (2*a)
T2 = (-b - math.sqrt(discriminant)) / (2*a)

print(T1, T2)

# Temperature range from 0°C to 200°C
temperatures = np.linspace(0, 200, 100)

# Calculate resistance for each temperature
resistances = 100 * (1 + b * temperatures - a * temperatures**2)

# Plotting the characteristic curve
plt.plot(temperatures, resistances, label="Resistance vs Temperature", color='r')
plt.title("Resistance vs Temperature for Platinum Resistor")
plt.xlabel("Temperature (°C)")
plt.ylabel("Resistance (Ω)")
plt.grid(True)
plt.legend()
plt.show()

