import numpy as np
import matplotlib.pyplot as plt



print("Read data")
data = np.fromfile('lrc_data.bin', dtype=np.double)
print("Data Read finished.")


dt = data[0]
total_time = data[1]

print(dt, total_time)

data = data[2:]

data = data.reshape(-1, 2)

x0 = data[:,0]
x1 = data[:,1]

t = np.linspace(0, total_time, len(x0))*1e3

plt.plot(t, x0)
plt.plot(t, x1)

plt.show()


