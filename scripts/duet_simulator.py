import asyncio
import json
import random
import time

HOST = '127.0.0.1'
PORT = 8085 

async def handle_client(reader, writer):
    print(f"[{current_time()}] C++ Telemetry Bridge connected!")
    
    # Initial mock printing state
    x, y, z = 0.0, 0.0, 0.0
    hotend_temp = 210.0
    bed_temp = 60.0
    
    try:
        while True:
            # Simulate slight physical movements and thermal fluctuations
            x = round(x + random.uniform(-0.5, 0.5) % 220, 3)
            y = round(y + random.uniform(-0.5, 0.5) % 220, 3)
            z = round(z + 0.001, 4)
            hotend_temp = round(210.0 + random.uniform(-0.8, 0.8), 2)
            bed_temp = round(60.0 + random.uniform(-0.2, 0.2), 2)
            
            # Construct a Duet-style status packet
            telemetry_packet = {
                "status": "P",
                "coords": {"X": x, "Y": y, "Z": z},
                "temps": {"tools": [hotend_temp], "bed": bed_temp},
                "feedrate": random.randint(1200, 1500),
                "timestamp": time.time()
            }
            
            # Serialize to JSON and append a newline delimiter for the network stream
            payload = json.dumps(telemetry_packet) + "\n"
            writer.write(payload.encode('utf-8'))
            await writer.drain()
            
            # Stream at 10Hz (10 packets per second) to simulate a high-frequency system
            await asyncio.sleep(0.1)
            
    except (asyncio.CancelledError, ConnectionResetError):
        print(f"[{current_time()}] Client disconnected.")
    finally:
        writer.close()
        await writer.wait_closed()

def current_time():
    return time.strftime("%H:%M:%S", time.localtime())

async def main():
    server = await asyncio.start_server(handle_client, HOST, PORT)
    print(f"[*] Duet Board Simulator running on {HOST}:{PORT}")
    print("[*] Awaiting connection from C++ Bridge...")
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[*] Shutting down Duet Simulator.")