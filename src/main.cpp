#include "telemetry_frame.h"
#include <iostream>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <string>

TelemetryFrame parse_telemetry(const std::string &packet) {
    TelemetryFrame frame;

    size_t pos = packet.find("\"status\": \"");
    frame.status = packet[pos + 11];

    pos = packet.find("\"X\": ");
    size_t end_pos = packet.find(",", pos + 5);
    size_t length = end_pos - (pos + 5);
    std::string x_str = packet.substr(pos + 5, length);
    frame.coord.x = std::stod(x_str);

    return frame;
}

int main() {
    int client_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (client_fd < 0) {
        std::cerr << "Error: Failed to create socket.\n";
        return 1;
    }

    struct sockaddr_in server_addr = {
        .sin_family = AF_INET,
        .sin_port = htons(8085)
    };

    int ip_status = inet_pton(AF_INET, "127.0.0.1", &server_addr.sin_addr);
    if (ip_status <= 0) {
        std::cerr << "Error: Invalid/Unsupported IP string.\n";
        return 1;
    }

    int connection_status = connect(client_fd, (struct sockaddr*)&server_addr, sizeof(server_addr));
    if (connection_status < 0) {
        std::cerr << "Error: Connection to simulator failed\n";
        return 1;
    }

    std::cout << "Successfully connected to Duet Simulator!\n";

    std::string stream_accumulator;
    while (true) {
        char buffer[1024];

        ssize_t bytes_received = recv(client_fd, buffer, sizeof(buffer) - 1, 0);
        if (bytes_received == 0) {
            std::cerr << "Error: Connection to server closed.\n";
            break;
        }
        if (bytes_received < 0) {
            std::cerr << "Error: Read failure occurred.\n";
            return 1;
        }
        if (bytes_received > 0) {
            buffer[bytes_received] = '\0';
            stream_accumulator += buffer;

            size_t newline_pos;
            while ((newline_pos = stream_accumulator.find('\n')) != std::string::npos) {
                std::string packet = stream_accumulator.substr(0, newline_pos);
                TelemetryFrame frame = parse_telemetry(packet);
                std::cout << "Packet->Status: " << frame.status << " | X: " << frame.coord.x << std::endl;
                stream_accumulator.erase(0, newline_pos + 1);
            }
        }
    }

    return 0;
}