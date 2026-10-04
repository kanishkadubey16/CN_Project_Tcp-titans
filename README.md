# CN Project - TCP Titans

## Phase 1: Private Network Service Platform

A fully local private network service platform demonstrating:

- LAN-based communication
- Private DNS using dnsmasq
- Two Flask backend services
- Nginx reverse proxy
- Round-robin load balancing
- HTTPS/TLS
- HTTP caching using Cache-Control and ETag
- Wireshark-based network observation
- Backend failure and failover handling

## Team Members

| Member | Role |
|---|---|
| Name 1 | Backend A, Client, Wireshark, Caching |
| Name 2 | Backend B, Client Testing, HTTPS Trust |
| Name 3 | DNS, Nginx, HTTPS/TLS, Load Balancer |

## Infrastructure

| Machine | Role | IP Address |
|---|---|---|
| Mac 1 | Backend A, Client, Wireshark, Caching | 10.7.9.129 |
| Mac 2 | Backend B, Client Testing, HTTPS Trust | 10.7.16.21 |
| Mac 3 | Private DNS, Nginx, HTTPS/TLS, Load Balancer | 10.7.9.131 |

> Note: The IP addresses shown above correspond to the current Phase 1 LAN setup and may change if DHCP assigns different addresses.

## Architecture

```text
                         Private LAN
                              |
                           Client
                              |
                              v
                       Private DNS
                         dnsmasq
                              |
                              | app.tcp-titans.test
                              | api.tcp-titans.test
                              v
                    Nginx Reverse Proxy
                       HTTPS / TLS
                              |
                       Round-Robin
                       Load Balancer
                        /           \
                       /             \
                      v               v
              Backend A            Backend B
              Port 3001            Port 3002
              Mac 1                Mac 2
