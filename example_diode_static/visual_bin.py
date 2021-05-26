import numpy as np
import matplotlib.pyplot as plt

# V_2 = 0
# V_3 = -10

# b = 1e-15*(np.exp((V_2-V_3)/0.025875))

# print(b)

# exit()

print("Read data")
data = np.fromfile('diode_data.bin', dtype=np.double)
print("Data Read finished.")


dt = data[0]
total_time = data[1]

print(dt, total_time)

data = data[2:]

data = data.reshape(-1, 4)

t = data[:,0]
x0 = data[:,1]
x1 = data[:,2]
x2 = data[:,3]


plt.plot(t, x0, label="Node 2 Voltage")
plt.plot(t, x1, label="Node 2 Voltage")
plt.plot(t, x2, label="Node 2 Voltage")


plt.legend()
plt.show()


