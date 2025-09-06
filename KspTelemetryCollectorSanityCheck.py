import matplotlib.pyplot as plt
import json

# read in the json
fileName = input("FileName: ")
fileName = "testdata/" + fileName + ".json"

packets = []

with open(fileName, "r") as file:
    packets = json.load(file)

def getPacketDataInList(name):
    return [packet[name] for packet in packets]

x = []
for packet in packets:
    x.append(packet["time"])

# Create a row of three different graphs (subplots)
fig, axes = plt.subplots(1, 3, figsize=(12, 4))

axes[0].plot(x, getPacketDataInList("altitude"))
axes[0].set_title("Altitude")

axes[1].plot(x, getPacketDataInList("accelHighX"))
axes[1].plot(x, getPacketDataInList("accelHighY"))
axes[1].plot(x, getPacketDataInList("accelHighZ"))
axes[1].set_title("Acceleration")

axes[2].plot(x, getPacketDataInList("velocity"))
axes[2].set_title("Velocity")

plt.tight_layout()
plt.show()