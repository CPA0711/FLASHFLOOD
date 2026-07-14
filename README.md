## BISMILLAH

# 🌊 FLASHFLOOD - HTTP Load Testing Tool

## 🚀 Quick Start

git clone https://github.com/CPA0711/flashflood.git

cd flashflood

pip install -r requirements.txt

python flash.py --url https://example.com --no-proxy

Or install with pip

pip install flashflood

## Usage

Simple GET request
python flash.py --url https://example.com --no-proxy

With auto-proxy (download proxies automatically)
python flash.py --url https://example.com --auto-proxy --threads 30

High performance testing
python flash.py --url https://example.com --no-proxy --threads 50 --delay 0.01

With logging
python flash.py --url https://example.com --no-proxy --threads 30 --log

## Examples

1. Basic testing
python flash.py --url https://httpbin.org/get --no-proxy

2. High load testing
python flash.py --url https://example.com --no-proxy --threads 100 --delay 0.01

3. With auto-proxy
python flash.py --url https://example.com --auto-proxy --threads 30 --delay 0.05

4. POST request with headers
python flash.py --url https://api.example.com --method POST -H "Content-Type: application/json" --no-proxy

5. With jitter (random delay)
python flash.py --url https://example.com --no-proxy --jitter 0.5,1.5 --threads 30

6. Full featured
python flash.py --url https://example.com --auto-proxy --jitter 0.3,0.8 --threads 50 --delay 0.05 --log

