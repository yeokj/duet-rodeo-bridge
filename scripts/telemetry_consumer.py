import struct
import json
import asyncio
import os
import websockets

frame_size = struct.calcsize("@cdddddid")
connected_clients = set()

async def handle_client_connection(websocket, path):
    print("Connection in progress...")
    connected_clients.add(websocket)

    try:
        async for message in websocket:
            pass
    finally:
        connected_clients.remove(websocket)
        await websocket.close()

async def read_fifo_and_broadcast():
    fd = os.open('/tmp/telemetry_fifo', os.O_RDONLY | os.O_NONBLOCK)
    loop = asyncio.get_event_loop()
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)

    await loop.connect_read_pipe(lambda: protocol, os.fdopen(fd, 'rb'))
    while True:
        buffer = await reader.readexactly(frame_size)
        if not buffer:
            break
        try:
            status, x, y, z, hotend, bed, feedrate, timestamp = struct.unpack("@cdddddid", buffer)

            data = {
                'metadata': {
                    'timestamp': timestamp
                },
                'status': { 
                    'operating_mode': status.decode('utf-8')
                },
                'telemetry': {
                    'kinematics': {
                        'position': {
                            'x': x,
                            'y': y,
                            'z': z
                        },
                        'feedrate': feedrate
                    },
                    'thermals': {
                        'hotend': hotend,
                        'bed': bed
                    }
                }
            }
            buffer_data = json.dumps(data)
            
            for client in connected_clients.copy():
                try:
                    await client.send(buffer_data)
                except Exception:
                    connected_clients.remove(client)
        
        except (struct.error, UnicodeDecodeError) as e:
            print("Error: Failed decoding POSIX FIFO")
            continue
    
async def main():
    fifo_task = asyncio.create_task(read_fifo_and_broadcast())

    async with websockets.serve(handle_client_connection, "localhost", 8765):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
        
