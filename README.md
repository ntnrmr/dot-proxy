# dot-proxy

Simple DNS to DNS over TLS proxy. Supports TCP connections only.

```mermaid
flowchart LR
    A[Client] -->|tcp:53| B(dot-proxy) -->|tcp:853| C[DoT server]
```

## Run locally

To run the application locally, use the following command:

```shell
# Install prereqs and run
pip install -r requirements.txt
python3 main.py
# Test DNS response
dig example.com @127.0.0.1 +tcp +short
```

> Python version tested was 3.9

## Run in Docker

For running the application in a Docker container, use the following Docker run command:

```shell
docker build -t dot-proxy:0.0.1 .
docker run -p 53:53 dot-proxy:0.0.1
```
