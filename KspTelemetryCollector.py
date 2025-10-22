"""
Launch a rocket in the game KSP and record where it is for example data
"""

import krpc
import json
import math

import krpc
conn = krpc.connect(name="fwer")
space_center = conn.space_center
assert space_center is not None

vessel = space_center.active_vessel
flight = vessel.flight(vessel.surface_reference_frame)
flightRelativeToKerbin = vessel.flight(vessel.orbit.body.orbital_reference_frame)

targetFPS = 240
targetSPF = 1.0 / targetFPS
GRAVITY = 9.81

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
    return (
        (vf[0] - vi[0]) / dt / GRAVITY,
        (vf[1] - vi[1]) / dt / GRAVITY,
        (vf[2] - vi[2]) / dt / GRAVITY
    )

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

    def collectData(self, current_time, delta):
        packet = {}

        assert space_center is not None
        packet["time"] = current_time - self.startTime
        packet["packetCountAv"] = self.packetCountAv
        self.packetCountAv += 1

        current_velocity = flightRelativeToKerbin.velocity
        current_rotation = flight.rotation

        # krpc doesnt seem to expose acceleration so i gotta calc it myself.
        acceleration = acclerationFromVelocity(current_velocity, self.previousVelocity, delta)
        self.previousVelocity = current_velocity

        packet["accelLowX"] = clamp(acceleration[0], 16)
        packet["accelLowY"] = clamp(acceleration[1], 16)
        packet["accelLowZ"] = clamp(acceleration[2], 16)
        packet["accelHighX"] = clamp(acceleration[0], 32)
        packet["accelHighY"] = clamp(acceleration[1], 32)
        packet["accelHighZ"] = clamp(acceleration[2], 32)

        angularVelocity = angularVelocityFromQuanterniun(self.previousRotation, current_rotation, delta)
        self.previousRotation = current_rotation

        packet["gyroX"] = angularVelocity[0]
        packet["gyroY"] = angularVelocity[1]
        packet["gyroZ"] = angularVelocity[2]

        packet["altitude"] = flight.surface_altitude
        packet["velocity"] = flightRelativeToKerbin.speed
        packet["mach_number"] = flight.mach

        packet["GPSLatitude"] = flight.latitude
        packet["GPSLongitude"] = flight.longitude

        packet["qw"] = current_rotation[3]
        packet["qx"] = current_rotation[0]
        packet["qy"] = current_rotation[1]
        packet["qz"] = current_rotation[2]

        self.packets.append(packet)

def main():
    vessel.control.activate_next_stage()
    vessel.control.throttle = 1

    collector = Collector()

    assert space_center is not None

    time_at_last_collection = space_center.ut
    try:
        while True:
            current_time = space_center.ut
            time_since_last_collection = current_time - time_at_last_collection

            if (time_since_last_collection <= targetSPF):
                continue

            time_at_last_collection = current_time

            collector.collectData(current_time, time_since_last_collection)
            
    except Exception as e:
        print(e)


    with open("testdata/temp.json", mode="x", encoding="utf-8") as file:
        file.write(json.dumps(collector.packets, indent=4))

if __name__ == "__main__":
    main()