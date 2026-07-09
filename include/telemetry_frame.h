#ifndef TELEMETRY_FRAME_H
#define TELEMETRY_FRAME_H

struct Coordinates {
    double x = 0.0;
    double y = 0.0;
    double z = 0.0;
};

struct Temperatures {
    double hotend = 0.0;
    double bed = 0.0;
};

struct TelemetryFrame {
    char status = 'I';
    Coordinates coord;
    Temperatures temp;
    int feedrate = 0;
    double timestamp = 0.0;
};

#endif