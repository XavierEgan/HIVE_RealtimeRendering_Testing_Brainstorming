"""
Launch a rocket in the game KSP and record where it is for example data
"""

import krpc
import json
import time
import math

import krpc
conn = krpc.connect(name="fwer")
space_center = conn.space_center
assert space_center is not None

vessel = space_center.active_vessel
flight = vessel.flight(vessel.surface_reference_frame)
flightRelativeToKerbin = vessel.flight(vessel.orbit.body.orbital_reference_frame)

def fixQuanterniun(q):
    #because unity is weird and has w last
    return [q[3], q[0], q[1], q[2]]

#https://mariogc.com/post/angular-velocity-quaternions/
def angularVelocityFromQuanterniun(previous, now, dt):
    q1 = fixQuanterniun(previous)
    q2 = fixQuanterniun(now)
    ret = [
        q1[0]*q2[1] - q1[1]*q2[0] - q1[2]*q2[3] + q1[3]*q2[2],
        q1[0]*q2[2] + q1[1]*q2[3] - q1[2]*q2[0] - q1[3]*q2[1],
        q1[0]*q2[3] - q1[1]*q2[2] + q1[2]*q2[1] - q1[3]*q2[0]
    ]
    ret[0] *= (2 / dt)
    ret[1] *= (2 / dt)
    ret[2] *= (2 / dt)
    return ret

def acclerationFromVelocity(vf, vi, dt):
    return [
        (vf[0] - vi[0]) / dt,
        (vf[1] - vi[1]) / dt,
        (vf[2] - vi[2]) / dt
    ]

def clamp(x, limit):
    return max(-limit, min(limit, x))

class Collector:
    def __init__(self):
        self.packets = []

        self.previousVelocity = flightRelativeToKerbin.velocity
        self.previousRotation = flight.rotation

        assert space_center is not None
        self.startTime = space_center.ut

        self.packetCountAv = 0

    def collectData(self, delta):
        packet = {}

        assert space_center is not None
        packet["time"] = space_center.ut - self.startTime
        packet["packetCountAv"] = self.packetCountAv
        self.packetCountAv += 1

        # krpc doesnt seem to expose acceleration so i gotta calc it myself.
        acceleration = acclerationFromVelocity(flightRelativeToKerbin.velocity, self.previousVelocity, delta)
        self.previousVelocity = flightRelativeToKerbin.velocity

        packet["accelLowX"] = clamp(acceleration[0], 16)
        packet["accelLowY"] = clamp(acceleration[1], 16)
        packet["accelLowZ"] = clamp(acceleration[2], 16)
        packet["accelHighX"] = clamp(acceleration[0], 32)
        packet["accelHighY"] = clamp(acceleration[1], 32)
        packet["accelHighZ"] = clamp(acceleration[2], 32)

        angularVelocity = angularVelocityFromQuanterniun(self.previousRotation, flight.rotation, delta)
        self.previousRotation = flight.rotation

        packet["gyroX"] = angularVelocity[0]
        packet["gyroY"] = angularVelocity[1]
        packet["gyroZ"] = angularVelocity[2]

        packet["altitude"] = flight.surface_altitude
        packet["velocity"] = flightRelativeToKerbin.speed
        packet["mach_number"] = flight.mach

        packet["GPSLatitude"] = flight.latitude
        packet["GPSLongitude"] = flight.longitude

        packet["qw"] = flight.rotation[3]
        packet["qx"] = flight.rotation[0]
        packet["qy"] = flight.rotation[1]
        packet["qz"] = flight.rotation[2]

        self.packets.append(packet)

def main():
    targetFPS = 120
    targetSPF = 1.0 / targetFPS

    vessel.control.activate_next_stage()
    vessel.control.throttle = 1

    collector = Collector()

    assert space_center is not None
    previousFrameStartTime = space_center.ut
    time.sleep(targetSPF)
    while True:
        try:
            # should error when i close the server

            # delta = the time the last frame took (including sleep)
            delta = space_center.ut - previousFrameStartTime
            previousFrameStartTime = space_center.ut

            collector.collectData(delta)

            frameTime = space_center.ut - previousFrameStartTime
            timeToSleep = targetSPF - frameTime
            time.sleep(0 if timeToSleep < 0 else timeToSleep)

        except Exception as e:
            print(e)
            break


    with open("testdata/launch2.json", mode="x", encoding="utf-8") as file:
        file.write(json.dumps(collector.packets, indent=4))

if __name__ == "__main__":
    main()