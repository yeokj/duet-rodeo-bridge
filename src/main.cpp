#include <iostream>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>

int main() {
    int client_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (client_fd < 0) {
        std::cerr << "Error: Failed to create socket\n";
        return 1;
    }

    struct sockaddr_in server_addr = {
        .sin_family = AF_INET,
        .sin_port = htons(8085)
    };

    int ip_status = inet_pton(AF_INET, "127.0.0.1", &server_addr.sin_addr);
    if (ip_status <= 0) {
        std::cerr << "Error: Invalid/Unsupported IP string\n";
        return 1;
    }

    return 0;
}