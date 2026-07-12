import struct
import json
import asyncio
import os

frame_size = struct.calcsize("@cdddddid")
connected_clients = set()

async def read_fifo_and_broadcast():
    fd = os.open('/tmp/telemetry_fifo', os.O_RDONLY | os.O_NONBLOCK)

    loop = asyncio.get_event_loop()
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await loop.connect_read_pipe(lambda: protocol, os.fdopen(fd, 'rb'))
    # with open('/tmp/telemetry_fifo', 'rb') as fifo:
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
