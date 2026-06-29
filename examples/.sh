```bash
#!/bin/bash

# FLASHFLOOD Example Usage Scripts

echo "=== FLASHFLOOD Example Usage ==="

# 1. Basic GET request
echo -e "\n1. Basic GET request"
python flash.py --url https://httpbin.org/get --no-proxy

# 2. High load testing
echo -e "\n2. High load testing (30 threads, minimal delay)"
python flash.py --url https://httpbin.org/get --no-proxy --threads 30 --delay 0.05

# 3. With auto-proxy
echo -e "\n3. With auto-proxy"
python flash.py --url https://httpbin.org/get --auto-proxy --threads 20 --delay 0.1

# 4. POST request
echo -e "\n4. POST request with headers"
python flash.py --url https://httpbin.org/post --method POST -H "Content-Type: application/json" --no-proxy

# 5. With jitter
echo -e "\n5. With jitter (random delay)"
python flash.py --url https://httpbin.org/get --no-proxy --jitter 0.1,0.5 --threads 20

# 6. With logging
echo -e "\n6. With logging"
python flash.py --url https://httpbin.org/get --no-proxy --threads 20 --log

# 7. Full featured
echo -e "\n7. Full featured testing"
python flash.py --url https://httpbin.org/get --auto-proxy --jitter 0.3,0.8 --threads 30 --delay 0.05 --log

echo -e "\n=== All examples completed ==="
```

---
