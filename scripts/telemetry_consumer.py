import struct
import json

frame_size = struct.calcsize("@cdddddid")

with open('/tmp/telemetry_fifo', 'rb') as fifo:
    while True:
        buffer = fifo.read(frame_size)
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
            print(buffer_data)

        except (struct.error, UnicodeDecodeError) as e:
            print("Error: Failed decoding POSIX FIFO")
            continue
