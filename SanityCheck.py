# client_test.py
import asyncio
import websockets

async def test():
    async with websockets.connect("ws://localhost:8765") as ws:
        while True:
            await ws.send("test")
            reply = await ws.recv()
            print("server sent:", reply)

asyncio.run(test())
