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
vec_size = int(data[2])

print(dt, total_time, vec_size)

data = data[3:]

data = data.reshape(-1, vec_size+2)

t = data[:,0]
source = data[:,1]

xs = [data[:,i+2] for i in range(vec_size)]


plt.plot(t, source, label="Source Voltage")

for i, x in enumerate(xs):
    plt.plot(t, x, label=f"Node {i} Voltage")



plt.legend()
plt.show()


