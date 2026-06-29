```markdown
# Detailed Usage Guide

## Installation

### From PyPI
```bash
pip install flashflood
```

From Source

```bash
git clone https://github.com/yourusername/flashflood.git
cd flashflood
pip install -e .
```

Command Line Interface

Basic Usage

```bash
flashflood --url https://example.com
```

Options Explained

URL Options

· --url <URL>: Target URL (required)

Performance Options

· --threads <NUM>: Number of concurrent threads (1-500)
· --delay <SEC>: Delay between requests
· -t, --timeout <SEC>: Request timeout

Proxy Options

· --no-proxy: Disable proxy
· --auto-proxy: Auto-download proxies
· --proxy-interval <M>: Update interval in minutes

Request Options

· -X, --method <M>: HTTP method (GET, POST, etc.)
· -H, --header <H>: Custom headers
· --no-verify: Disable SSL verification
· --no-redirect: Disable redirects

Advanced Options

· -j, --jitter <V>: Random delay
· --retry <NUM>: Retry count
· --retry-delay <SEC>: Retry delay
· -l, --log: Save to log file

Examples

Basic GET Request

```bash
flashflood --url https://httpbin.org/get --no-proxy
```

High Load Testing

```bash
flashflood --url https://example.com --no-proxy --threads 100 --delay 0.01
```

With Auto-Proxy

```bash
flashflood --url https://example.com --auto-proxy --threads 30 --delay 0.05
```

POST Request with Headers

```bash
flashflood --url https://api.example.com --method POST -H "Content-Type: application/json" --no-proxy
```

With Jitter

```bash
flashflood --url https://example.com --no-proxy --jitter 0.5,1.5 --threads 30
```

Full Featured

```bash
flashflood --url https://example.com --auto-proxy --jitter 0.3,0.8 --threads 50 --delay 0.05 --log
```

Understanding Statistics

Real-time Statistics

· Time: Elapsed time
· Requests: Total requests sent
· Success: Successful requests (2xx, 3xx)
· Failed: Failed requests
· Success Rate: Percentage of successful requests
· RPS: Requests per second
· Status Codes: Distribution of HTTP status codes

Response Times

· Fast: < 100ms - Excellent
· Good: 100-500ms - Acceptable
· Slow: 500ms-2s - Needs optimization
· Very Slow: > 2s - Problematic

Best Practices

1. Start Small: Begin with low threads and increase gradually
2. Monitor Results: Watch success rate and response times
3. Use Direct Connection: For baseline performance testing
4. Use Proxy: For testing from different locations
5. Log Results: Save logs for analysis
6. Respect Rate Limits: Don't overload servers
7. Get Permission: Only test websites you own or have permission

Troubleshooting

Common Issues

1. Connection Errors
   · Check URL format
   · Verify internet connection
   · Check firewall settings
2. Proxy Errors
   · Use --no-proxy to test without proxies
   · Use --auto-proxy to get fresh proxies
3. SSL Errors
   · Use --no-verify to disable SSL verification
   · Check certificate validity
4. Timeout Errors
   · Increase timeout with --timeout
   · Reduce thread count
   · Check server response time

Performance Tips

1. For Maximum Speed:
   ```bash
   flashflood --url https://example.com --no-proxy --threads 50 --delay 0.01
   ```
2. For Realistic Testing:
   ```bash
   flashflood --url https://example.com --no-proxy --jitter 0.1,0.5 --threads 30
   ```
3. For Load Testing:
   ```bash
   flashflood --url https://example.com --auto-proxy --threads 30 --delay 0.05
   ```

```

---
