# server.py
import asyncio
from websockets.asyncio.server import serve
import json

class TestPacket:
    def __init__(self):
        self.time = 0
        self.packetCountAv = 0
        
        self.accelLowX = 0
        self.accelLowY = 0
        self.accelLowZ = 0
        self.accelHighX = 0
        self.accelHighY = 0
        self.accelHighZ = 0

        self.gyroX = 0
        self.gyroY = 0
        self.gyroZ = 0

        self.altitude = 0
        self.velocity = 0

        self.latitude = 0
        self.longitude = 0

        self.qw = 0
        self.qx = 0
        self.qy = 0
        self.qz = 0

        self.mach = 0
    
    def getPacket(self, id) -> str:
        packet = {}
        if (id == 3):
            packet["id"] = 3
            packet["data"] = {
                "meta": {
                    "rssi": -15.454711,
                    "snr": 0.37879905,
                    "timestampS": self.time,
                    "totalPacketCountAv": f"{self.packetCountAv}",
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
                "accelLowX": self.accelLowX,
                "accelLowY": self.accelLowY,
                "accelLowZ": self.accelLowZ,
                "accelHighX": self.accelHighX,
                "accelHighY": self.accelHighY,
                "accelHighZ": self.accelHighZ,
                "gyroX": self.gyroX,
                "gyroY": self.gyroY,
                "gyroZ": self.gyroZ,
                "altitude": self.altitude,
                "velocity": self.velocity,
                "apogeePrimaryTestComplete": False,
                "apogeeSecondaryTestComplete": False,
                "apogeePrimaryTestResults": False,
                "apogeeSecondaryTestResults": False,
                "mainPrimaryTestComplete": False,
                "mainSecondaryTestComplete": False,
                "mainPrimaryTestResults": False,
                "mainSecondaryTestResults": False,
                "broadcastFlag": False,
                "mach_number": self.mach,
            }
        elif (id == 4):
            packet["id"] = 4
            packet["data"] = {
                "meta": {
                    "rssi": -14.7131,
                    "snr": 0.442897,
                    "timestampS": self.time,
                    "totalPacketCountAv": f"{self.packetCountAv}",
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
                "GPSLatitude": self.longitude,
                "GPSLongitude": self.latitude,
                "navigationStatus": "NA",
                "qw": self.qw,
                "qx": self.qx,
                "qy": self.qy,
                "qz": self.qz,
            }

        return json.dumps(packet)

    def readJsonObj(jsonObj):
        pass

async def send(websocket):
    await websocket.send("hi")


async def main():
    async with serve(send, "localhost", 8765) as server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())