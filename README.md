# TCP Titans

**Computer Networks — Phase 1: Private Network Service Platform**
Distributed Network Infrastructure, DNS, Secure HTTPS, Reverse Proxy, Load Balancing and Network Analysis

Newton School of Technology · Submitted 4 October 2026

A private network service platform built on three Macs on one LAN. A client resolves service names through a private DNS server (dnsmasq), connects over HTTPS to an Nginx reverse proxy, and Nginx forwards each request to one of two Flask backends. The project also demonstrates HTTP cache validation (`Cache-Control` / `ETag` / `304`), a backend-failure scenario, and packet-level analysis in Wireshark.

The full report (`TCP_TITANS_Phase1_Final_Report.pdf`) contains the analysis, figures, requirements matrix, troubleshooting notes and appendices. This README is a short guide to the repository.

---

## Team

| Member | Roll number | Machine and role |
|---|---|---|
| Bulbul Agarwalla | 2401010131 | Mac 1 — Backend A, Client, Wireshark, Caching |
| Kanishka Dubey | 2401010208 | Mac 2 — Backend B, Client Testing, HTTPS Trust |
| Shourya Pratap | 2401010445 | Mac 3 — Private DNS, Nginx, HTTPS/TLS, Load Balancer |

## Architecture

```
            Client (curl / dig / Wireshark)
               |                       |
         DNS query :53             HTTPS :443
               v                       v
      +--------------------------------------+
      |  Mac 3   10.7.9.131                  |
      |  dnsmasq :53     Nginx :80 / :443    |
      |                  TLS termination     |
      |                  reverse proxy       |
      |                  upstream backend_pool|
      +------------------+-------------------+
                         |  plain HTTP
              +----------+-----------+
              v                      v
      Mac 1  10.7.9.129       Mac 2  10.7.16.21
      Backend A  :3001        Backend B  :3002
```

| Machine | IP address | Service | Port |
|---|---|---|---|
| Mac 1 | `10.7.9.129` | Backend A (Flask) | 3001 |
| Mac 2 | `10.7.16.21` | Backend B (Flask) | 3002 |
| Mac 3 | `10.7.9.131` | dnsmasq | 53 |
| Mac 3 | `10.7.9.131` | Nginx (HTTP redirect / HTTPS) | 80 / 443 |

Domain names: `app.tcp-titans.test` and `api.tcp-titans.test`, both resolving to `10.7.9.131`.

> The addresses are the DHCP assignments used during Phase 1 and may change. If they do, update `config/dnsmasq.conf` and `config/nginx.conf`.

## Technologies

dnsmasq · Nginx (`nginx/1.31.6` in the captured responses) · mkcert · Python / Flask 3.1.3 · curl · dig · Wireshark

## Components

### Private DNS — `config/dnsmasq.conf`

```
listen-address=127.0.0.1,10.7.9.131

address=/app.tcp-titans.test/10.7.9.131
address=/api.tcp-titans.test/10.7.9.131
```

Clients are pointed at `10.7.9.131`. On Mac 2 this was done with:

```bash
sudo networksetup -setdnsservers "Wi-Fi" 10.7.9.131
```

### Backend A — `backend-a/app.py` (Mac 1, port 3001)

- `GET /` → `{"backend":"A","status":"ok"}` with `X-Backend: A`
- `GET /api/status` → same body plus `Cache-Control: max-age=60` and `ETag: "backend-a-v1"`; returns an empty-body `304` when `If-None-Match` equals the ETag

### Backend B — `backend-b/app.py` (Mac 2, port 3002)

- `GET /` and `GET /api/status` → `{"backend":"B","status":"ok"}` with `X-Backend: B` (no caching headers)

### Nginx — `config/nginx.conf` (Mac 3)

- `upstream backend_pool` with `10.7.9.129:3001` and `10.7.16.21:3002`
- Port 80: `return 301 https://$host$request_uri;`
- Port 443: TLS, `proxy_pass http://backend_pool;`, forwarding `Host` and `X-Real-IP`
- `app` and `api` share one server block and one pool (no separate API routing)
- Not configured: `proxy_cache`, `max_fails` / `fail_timeout`, `proxy_next_upstream`, `ssl_protocols`, `ssl_ciphers`, an explicit balancing method

The certificate paths in the repository copy are placeholders. Set them to the real paths on Mac 3.

### HTTPS / TLS

A certificate for `app.tcp-titans.test` and `api.tcp-titans.test` was generated with mkcert, and clients verify it with the mkcert root CA:

```bash
curl --cacert ~/Downloads/rootCA.pem -i https://app.tcp-titans.test/
curl --cacert ~/Downloads/rootCA.pem -i https://api.tcp-titans.test/api/status
```

Without the root CA, curl reports `(60) SSL certificate problem: unable to get local issuer certificate`. The packet capture shows a TLS 1.3 session with cipher suite `TLS_AES_256_GCM_SHA384` (read from the Server Hello). Traffic from Nginx to the backends is plain HTTP.

### Load balancing

```bash
for i in {1..6}; do curl --cacert ~/Downloads/rootCA.pem -s https://app.tcp-titans.test/; echo; done
```

Observed order: **A, B, A, B, A, B**. Requests alternate between the two backends in this test. The config declares no balancing method, so this is Nginx's default behaviour.

### HTTP caching

```bash
curl -i http://10.7.9.129:3001/api/status
curl -i -H 'If-None-Match: "backend-a-v1"' http://10.7.9.129:3001/api/status
```

The first request returns `200 OK` with `Cache-Control: max-age=60` and the `ETag`. The second returns `304 NOT MODIFIED` with no body. This was tested directly against Backend A; Nginx does not cache.

### Failure test

With Backend A unavailable, four HTTPS requests through Nginx were all answered by Backend B (`{"backend":"B","status":"ok"}`). This shows service continuing through Backend B in that scenario. The report does not claim zero downtime or production-grade high availability.

## Evidence

All files are under `evidence/`. Screenshots are JPEG images with a `.png.jpeg` double extension.

| Feature | File |
|---|---|
| LAN addresses | `lan/01_mac2_ip`, `lan/02_mac3_ip`, `lan/03_mac1_ip` |
| LAN connectivity (ping) | `lan/04_lan_connectivity` |
| DNS from Mac 1 | `dns/01_private_dns_resolution` |
| DNS from Mac 2 | `dns/02_mac2_private_dns_resolution` |
| Backend A / B direct | `backends/01_backend_a`, `backends/02_backend_b` |
| HTTPS (app / API) | `https/01_https_app`, `https/02_https_app` |
| Nginx config test | `https/03_nginx_config_test` |
| Nginx listening on 80/443 | `https/04_nginx_ports_80_443` |
| Load balancing | `load-balancing/01_round_robin` |
| Cache 200 / 304 | `caching/01_cache_headers`, `caching/02_conditional_304` |
| Failure test | `failure/01_backend_a_failure_failover` |
| Wireshark DNS / TCP / TLS | `wireshark/01_dns_query`, `wireshark/02_tcp_tls` |
| Full packet capture | `wireshark/phase1-complete-flow.pcapng` |

`phase1-complete-flow.pcapng` was captured on Mac 1 over the whole interface (4,873 frames, about 59.6 s), so it also contains unrelated background traffic. The project flow is TCP `10.7.9.129:56367 → 10.7.9.131:443` plus the DNS exchange for `app.tcp-titans.test` (query ID `0xd497`, answer in frame 1938).

## Repository structure

```
.
├── README.md
├── .gitignore
├── backend-a/    app.py, requirements.txt
├── backend-b/    app.py, requirements.txt
├── config/       dnsmasq.conf, nginx.conf
└── evidence/
    ├── backends/  caching/  dns/  failure/  https/
    ├── lan/  load-balancing/  wireshark/
```

## How to run

1. Put all three Macs on the same LAN.
2. **Mac 1 (Backend A):**
   ```bash
   cd backend-a
   pip install -r requirements.txt
   python3 app.py
   ```
3. **Mac 2 (Backend B):**
   ```bash
   cd backend-b
   pip install -r requirements.txt
   python3 app.py
   ```
4. **Mac 3:**
   - Install dnsmasq and apply `config/dnsmasq.conf`.
   - Install Nginx and generate the mkcert certificate for both names (the file names `app.tcp-titans.test+1.pem` and `app.tcp-titans.test+1-key.pem` match mkcert's naming for a two-name certificate).
   - Set the certificate paths in `config/nginx.conf`, load it from Nginx's `servers/` directory (the main `nginx.conf` needs `include servers/*;`), then validate:
     ```bash
     sudo nginx -t
     sudo lsof -nP -iTCP:80 -iTCP:443
     ```
5. Point each client's DNS server at `10.7.9.131` and copy the mkcert `rootCA.pem` to each client.
6. Verify:
   ```bash
   dig app.tcp-titans.test
   dig api.tcp-titans.test
   curl -i http://10.7.9.129:3001/
   curl -i http://10.7.16.21:3002/
   ```
   then run the HTTPS, load-balancing and caching commands above.

dnsmasq install/start commands and the Nginx start/reload command are not recorded in the project materials, so they are not listed here.

## Security notes

- Never commit private keys. `.gitignore` excludes `*.key`, `*-key.pem` and `rootCA-key.pem`.
- Keep the mkcert CA private key private; anyone holding it can issue certificates your machines will trust.
- Both Flask apps bind to `0.0.0.0` and run on the Werkzeug development server, so they are reachable directly on the LAN without going through Nginx.
- The Nginx-to-backend hop is unencrypted HTTP.
- The packet capture and the listener screenshot (`https/04_nginx_ports_80_443`) contain unrelated traffic and connections from the capturing machines.
- This is a LAN prototype, not a production-security design.
