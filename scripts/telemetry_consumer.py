import struct

frame_size = struct.calcsize("@cdddddid")

with open('/tmp/telemetry_fifo', 'rb') as fifo:
    while True:
        buffer = fifo.read(frame_size)
        if not buffer:
            break
        
        status, x, y, z, hotend, bed, feedrate, timestamp = struct.unpack("@cdddddid", buffer)
        print(f"Status: {status.decode('utf-8')} | Position: ({x}, {y}, {z}) | Hotend: {hotend}°C")
