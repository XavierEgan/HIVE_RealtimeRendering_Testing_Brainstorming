# NOTES:
# This is very scuffed
# only works for one client
# please god rewrite this if you intend to use it for anything other than simple testing

# server.py
import asyncio
from websockets.asyncio.server import serve
import json
import time
import random

# constants
TARGET_PACKET_HZ = 10
TARGET_PACKET_S = 1/TARGET_PACKET_HZ
PACKET_INNACURACY = .05 # 1 corresponds to: x += x, .5 corresponds to x += .5x


def getRocketPacketFromTelemetryPacket(telemetry):
    packet1 = {
        "id": 3,
        "data": {
            "meta": {
                "rssi": -15.454711,
                "snr": 0.37879905,
                "timestampS": telemetry["time"],
                "totalPacketCountAv": f"{telemetry['packetCountAv']}",
                "totalPacketCountGse": "946",
            },
            "flightState": "PRE_FLIGHT_NO_FLIGHT_READY",
            "stateFlags": {
                "dualBoardConnectivityStateFlag": False,
                "recoveryChecksCompleteAndFlightReady": False,
                "GPSFixFlag": False,
                "payloadConnectionFlag": True,
                "cameraControllerConnectionFlag": True,
            },
            "accelLowX": telemetry["accelLowX"],
            "accelLowY": telemetry["accelLowY"],
            "accelLowZ": telemetry["accelLowZ"],
            "accelHighX": telemetry["accelHighX"],
            "accelHighY": telemetry["accelHighY"],
            "accelHighZ": telemetry["accelHighZ"],
            "gyroX": telemetry["gyroX"],
            "gyroY": telemetry["gyroY"],
            "gyroZ": telemetry["gyroZ"],
            "altitude": telemetry["altitude"],
            "velocity": telemetry["velocity"],
            "apogeePrimaryTestComplete": False,
            "apogeeSecondaryTestComplete": False,
            "apogeePrimaryTestResults": False,
            "apogeeSecondaryTestResults": False,
            "mainPrimaryTestComplete": False,
            "mainSecondaryTestComplete": False,
            "mainPrimaryTestResults": False,
            "mainSecondaryTestResults": False,
            "broadcastFlag": False,
            "mach_number": telemetry["mach_number"],
        }
    }
    packet2 = {
        "id": 4,
        "data": {
            "meta": {
                "rssi": -14.7131,
                "snr": 0.442897,
                "timestampS": telemetry["time"],
                "totalPacketCountAv": telemetry['packetCountAv'],
                "totalPacketCountGse": "944",
            },
            "flightState": "PRE_FLIGHT_NO_FLIGHT_READY",
            "stateFlags": {
                "dualBoardConnectivityStateFlag": False,
                "recoveryChecksCompleteAndFlightReady": False,
                "GPSFixFlag": False,
                "payloadConnectionFlag": True,
                "cameraControllerConnectionFlag": True,
            },
            "GPSLatitude": telemetry["GPSLatitude"],
            "GPSLongitude": telemetry["GPSLongitude"],
            "navigationStatus": "NA",
            "qw": telemetry["qw"],
            "qx": telemetry["qx"],
            "qy": telemetry["qy"],
            "qz": telemetry["qz"],
        }
    }

    return packet1, packet2

fileLocation = input("Which file would you like to emulate? > ")
fileLocation = "testdata/" + fileLocation + ".json"
telemetryPackets = []
try:
    with open(fileLocation, "r") as file:
        telemetryPackets = json.load(file)
except:
    print(f"could not open file {fileLocation}")
    quit()

if len(telemetryPackets) == 0:
    print("json file empty")

class RocketEmulator:
    previousSentPacket = 0
    previousSentPacketTime = 0
    startTime = 0

    def __init__(self):
        self.startTime = time.time()

    def findNextPacket(self, elapsedTime):
        for i in range(len(telemetryPackets)):
            if (elapsedTime < telemetryPackets[i]["time"]):
                return i
        return 0
    
    async def sendPacket(self, websocket, elapsedTime):
        
    
        packetUpTo = self.findNextPacket(elapsedTime)
        
        print(f"sending packets t={elapsedTime} p={packetUpTo}")
        
        packets = getRocketPacketFromTelemetryPacket(telemetryPackets[packetUpTo])
        await websocket.send(json.dumps(packets[0]))
        await websocket.send(json.dumps(packets[1]))

        self.previousSentPacket = packetUpTo
        self.previousSentPacketTime = time.time()

        return False
    
    async def sendPackets(self, websocket):
        while True:
            elapsedTime = time.time() - self.startTime

            if (time.time() - self.previousSentPacketTime < TARGET_PACKET_S):
                continue

            done = await self.sendPacket(websocket, elapsedTime)
            if (done):
                print("done")
                return

async def handle(websocket):
    rocketEmulator = RocketEmulator()
    await rocketEmulator.sendPackets(websocket)

async def main():
    async with serve(handle, "localhost", 8765) as server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())