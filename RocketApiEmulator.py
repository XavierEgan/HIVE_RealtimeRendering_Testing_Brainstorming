# NOTES:
# This is very scuffed
# only works for one client
# please god rewrite this if you intend to use it for anything other than simple testing

# server.py
import asyncio
from websockets.asyncio.server import serve
from websockets import ServerConnection
import json
import time
import random

from Logging import Logging

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
                "totalPacketCountAv": telemetry['packetCountAv'],
                "totalPacketCountGse": telemetry['packetCountAv'],
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
                "totalPacketCountGse": telemetry['packetCountAv'],
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

print("\033[H\033[2J")

while True:
    fileLocation = input("Which file would you like to emulate? > ")
    fileLocation = "testdata/" + fileLocation + ".json"
    telemetryPackets = []
    try:
        with open(fileLocation, "r") as file:
            telemetryPackets = json.load(file)

        Logging.printInfo(f"Opened File '{fileLocation}'")
    except:
        Logging.printWarn(f"Could Not Open File '{fileLocation}'")
        continue
    break

if len(telemetryPackets) == 0:
    Logging.printWarn("json file empty")

class RocketEmulator:
    def __init__(self) -> None:
        self.startTime = time.monotonic()
        self.packetIndex = 0
    
    async def sendPackets(self, websocket):
        try:
            while True:
                now = time.monotonic()
                elapsed = now - self.startTime

                # keep going till we find a packet with an elapsed time greater than the actual elapsed time
                while elapsed >= telemetryPackets[self.packetIndex]["time"]:
                    self.packetIndex += 1

                    # replay if we get to the end
                    if self.packetIndex >= len(telemetryPackets):
                        self.packetIndex = 0
                        self.startTime = time.monotonic()
                        Logging.printInfo("Reached end of playback, replaying")
                        break
                
                self.packetIndex = self.packetIndex - 1 if self.packetIndex != 0 else self.packetIndex

                rocketPackets = getRocketPacketFromTelemetryPacket(telemetryPackets[self.packetIndex])
                
                Logging.printInfo(f"Sending Packet - t={telemetryPackets[self.packetIndex]['time']} p={self.packetIndex}")

                await websocket.send(json.dumps(rocketPackets[0]))
                await websocket.send(json.dumps(rocketPackets[1]))

                frameTime = time.monotonic() - now
                waitTime = TARGET_PACKET_S - frameTime
                await asyncio.sleep(waitTime)
        except Exception as e:
            Logging.printWarn(f"Client Disconnected or Error: {e}")

async def handle(websocket: ServerConnection):
    Logging.printInfo(f"New Connection")
    rocketEmulator = RocketEmulator()
    await rocketEmulator.sendPackets(websocket)

async def main():
    Logging.printInfo(f"Waiting for Connection...")
    async with serve(handle, "localhost", 8765) as server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())