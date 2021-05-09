import numpy as np
import matplotlib.pyplot as plt



print("Read data")
data = np.fromfile('lrc_data.bin', dtype=np.double)
print("Data Read finished.")


dt = data[0]
total_time = data[1]

print(dt, total_time)

data = data[2:]

data = data.reshape(-1, 3)

x0 = data[:,0]
x1 = data[:,1]
x2 = data[:,2]


t = np.linspace(0, total_time, len(x0))*1e3

plt.plot(t, x0, label="Node 1 Voltage")
plt.plot(t, x1, label="L1 Current")
plt.plot(t, x2, label="C1 Current")

plt.legend()
plt.show()


