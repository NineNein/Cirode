import numpy as np
import matplotlib.pyplot as plt



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


