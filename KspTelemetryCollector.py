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

if space_center == None:
    raise RuntimeError("space_center is none")

vessel = space_center.active_vessel
flight = vessel.flight(vessel.surface_reference_frame)
flightRelativeToKerbin = vessel.flight(vessel.orbit.body.reference_frame)

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

def main():
    packets = []

    previousVelocity = [0.0, 0.0, 0.0]
    previousRotation = [0.0, 0.0, 0.0, 0.0]

    startTime = time.time()
    prevTime = time.time()

    packetCountAv = 0

    vessel.control.activate_next_stage()
    vessel.control.throttle = 1
    while True:
        try:
            # should error when we finish the launch because there is no longer a vehicle to talk to
            delta = time.time() - prevTime
            if (delta == 0.0):
                delta = 1.0e-6

            time.sleep(.01)

            prevTime = time.time()

            packet = {}

            packet["time"] = time.time() - startTime
            packet["packetCountAv"] = packetCountAv
            packetCountAv += 1

            # krpc doesnt seem to expose acceleration so i gotta calc it myself.
            acceleration = acclerationFromVelocity(flightRelativeToKerbin.velocity, previousVelocity, delta)
            previousVelocity = flightRelativeToKerbin.velocity

            packet["accelLowX"] = clamp(acceleration[0], 16)
            packet["accelLowY"] = clamp(acceleration[1], 16)
            packet["accelLowZ"] = clamp(acceleration[2], 16)
            packet["accelHighX"] = clamp(acceleration[0], 32)
            packet["accelHighY"] = clamp(acceleration[1], 32)
            packet["accelHighZ"] = clamp(acceleration[2], 32)

            angularVelocity = angularVelocityFromQuanterniun(previousRotation, flight.rotation, delta)
            previousRotation = flight.rotation

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

            packets.append(packet)
        except Exception as e:
            print(e)
            break


    with open("testdata/launch1.json", mode="x", encoding="utf-8") as file:
        file.write(json.dumps(packets, indent=4))

if __name__ == "__main__":
    main()