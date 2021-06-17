import numpy as np
import matplotlib.pyplot as plt





def read_spice_plot(filename):

    t = []
    columns = {}

    with open(filename) as f:
        for line in f:
            line = line.strip()
            cols = line.split("\t")
            try:
                cols = list(map(float, cols))
            except:
                print("Can't convert: ", line)

            t.append(cols[0])
            for i, col in enumerate(cols[1:]):
                if i not in columns:
                    columns[i] = []

                columns[i].append(col)


    print(columns)
    return t, columns


print("Read data")
data = np.fromfile('diode_data.bin', dtype=np.double)
print("Data Read finished.")


dt = data[0]
total_time = data[1]

print(dt, total_time)

data = data[2:]

data = data.reshape(-1, 3)

t = data[:,0]
x0 = data[:,1]
x1 = data[:,2]


lt_t, lt_cols = read_spice_plot("Diode_LTSpice.txt")

plt.plot(t, x0, label="Node 2 Voltage")
plt.plot(t, x1, label="Node 2 Voltage")


plt.plot(lt_t, lt_cols[0], label="LT Voltage")
plt.plot(lt_t, lt_cols[1], label="LT Voltage")


plt.legend()
plt.show()


