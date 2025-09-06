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
fig, axes = plt.subplots(3, 3, figsize=(12, 4))

axes[0][0].plot(x, getPacketDataInList("accelHighX"))
axes[0][0].plot(x, getPacketDataInList("accelHighY"))
axes[0][0].plot(x, getPacketDataInList("accelHighZ"))
axes[0][0].set_title("Acceleration High")

axes[0][1].plot(x, getPacketDataInList("accelLowX"))
axes[0][1].plot(x, getPacketDataInList("accelLowY"))
axes[0][1].plot(x, getPacketDataInList("accelLowZ"))
axes[0][1].set_title("Acceleration Low")

axes[0][2].plot(x, getPacketDataInList("gyroX"))
axes[0][2].plot(x, getPacketDataInList("gyroY"))
axes[0][2].plot(x, getPacketDataInList("gyroZ"))
axes[0][2].set_title("Gyro")

axes[1][0].plot(x, getPacketDataInList("altitude"))
axes[1][0].set_title("Altitude")

axes[1][1].plot(x, getPacketDataInList("velocity"))
axes[1][1].set_title("Velocity")

axes[1][2].plot(x, getPacketDataInList("mach_number"))
axes[1][2].set_title("Mach Number")

axes[2][0].plot(x, getPacketDataInList("GPSLatitude"))
axes[2][0].plot(x, getPacketDataInList("GPSLongitude"))
axes[2][0].set_title("GPS Position")

axes[2][1].plot(x, getPacketDataInList("qw"))
axes[2][1].plot(x, getPacketDataInList("qx"))
axes[2][1].plot(x, getPacketDataInList("qy"))
axes[2][1].plot(x, getPacketDataInList("qz"))
axes[2][1].set_title("Rotation")

axes[2][2].plot(x, getPacketDataInList("packetCountAv"))
axes[2][2].set_title("Packet Count")

plt.tight_layout()
plt.show()