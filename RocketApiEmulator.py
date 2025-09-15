# NOTES:
# This is very scuffed
# only works for one client
# please god rewrite this if you intend to use it for anything other than simple testing

# server.py
import asyncio
from websockets.asyncio.server import serve
import json
import time

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

nextPacketTime = telemetryPackets[0]["time"]

packetUpTo = 0
startTime = time.time()

async def sendPacket(websocket):
    global packetUpTo
    global startTime

    elapsedTime = time.time() - startTime
    
    # find the next packet (may skip some)
    for i in range(packetUpTo, len(telemetryPackets)):
        if (elapsedTime < telemetryPackets[i]["time"]):
            packetUpTo = i - 1
            break
    
    print("sending packets")
    
    packets = getRocketPacketFromTelemetryPacket(telemetryPackets[packetUpTo])
    await websocket.send(json.dumps(packets[0]))
    await websocket.send(json.dumps(packets[1]))

    return False

async def sendPackets(websocket):
    while True:
        done = await sendPacket(websocket)
        if (done):
            print("done")
            return



async def main():
    async with serve(sendPackets, "localhost", 8765) as server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())