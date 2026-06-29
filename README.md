# BISMILLAHIRRAHMANIRRAHIIM


# 🌊 FLASHFLOOD - HTTP Load Testing Tool

[![Python](https://img.shields.io/badge/Python-3.7%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![GitHub stars](https://img.shields.io/github/stars/yourusername/flashflood)](https://github.com/yourusername/flashflood/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/yourusername/flashflood)](https://github.com/yourusername/flashflood/issues)

🚀 **FLASHFLOOD** adalah alat load testing HTTP yang powerful, ringan, dan mudah digunakan. Dirancang untuk menguji performa website dengan simulasi request HTTP secara paralel.

## ✨ Features

- 🚀 **High Performance** - Mendukung hingga 500 thread concurrent
- 🔄 **Auto Proxy** - Download proxy otomatis dari berbagai sumber
- 🎯 **Multi Method** - Support GET, POST, PUT, DELETE, HEAD, OPTIONS, PATCH
- ⚡ **Jitter & Delay** - Simulasi traffic realistis dengan random delay
- 📊 **Real-time Statistics** - Monitor RPS, success rate, status codes
- 📝 **Logging** - Save hasil testing ke file JSON
- 🔒 **SSL Support** - Support HTTPS dengan custom SSL verification
- 🌐 **Multi Platform** - Bekerja di Windows, Linux, MacOS
- 🔄 **Auto-retry** - Retry mechanism untuk request yang gagal
- 🎨 **Colorful Output** - Tampilan terminal yang informatif

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/CPA0711/flashflood.git
cd flashflood

# Install dependencies
pip install -r requirements.txt

# Or install with pip
pip install flashflood
```

Basic Usage

```bash
# Simple GET request
python flash.py --url https://example.com --no-proxy

# With auto-proxy (download proxies automatically)
python flash.py --url https://example.com --auto-proxy --threads 30

# High performance testing
python flash.py --url https://example.com --no-proxy --threads 50 --delay 0.01

# With logging
python flash.py --url https://example.com --no-proxy --threads 30 --log
```

📚 Documentation

Command Line Options

Option Description Default
--url Target URL (required) -
-t, --timeout Request timeout in seconds 10
--threads Number of concurrent threads 20
--delay Delay between requests 1.0
--no-proxy Disable proxy False
-X, --method HTTP method (GET, POST, etc.) GET
-H, --header Custom headers -
-j, --jitter Random delay (min,max) -
-l, --log Save results to log False
--auto-proxy Auto-download proxies False
--no-verify Disable SSL verification False
--retry Retry count 0
--retry-delay Retry delay 1.0

Examples

```bash
# 1. Basic testing
python flash.py --url https://httpbin.org/get --no-proxy

# 2. High load testing
python flash.py --url https://example.com --no-proxy --threads 100 --delay 0.01

# 3. With auto-proxy
python flash.py --url https://example.com --auto-proxy --threads 30 --delay 0.05

# 4. POST request with headers
python flash.py --url https://api.example.com --method POST -H "Content-Type: application/json" --no-proxy

# 5. With jitter (random delay)
python flash.py --url https://example.com --no-proxy --jitter 0.5,1.5 --threads 30

# 6. Full featured
python flash.py --url https://example.com --auto-proxy --jitter 0.3,0.8 --threads 50 --delay 0.05 --log
```

📊 Performance

Mode Threads RPS Success Rate
Direct Connection 30 27.7 100%
With Proxy 30 2.2 59.5%
High Load 100 50+ 95%+

🛠️ Development

Setup Development Environment

```bash
# Clone repository
git clone https://github.com/CPA0711/flashflood.git
cd flashflood

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/
```

Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=flashflood tests/

# Run specific test
pytest tests/test_flash.py
```

🤝 Contributing

How to Contribute

1. Fork repository
2. Buat branch baru (git checkout -b feature/amazing-feature)
3. Commit perubahan (git commit -m 'Add some amazing feature')
4. Push ke branch (git push origin feature/amazing-feature)
5. Open Pull Request

📄 License

Distributed under MIT License. See LICENSE for more information.

⚠️ Disclaimer

FLASHFLOOD hanya untuk tujuan edukasi dan testing. Gunakan hanya pada website yang Anda miliki atau memiliki izin eksplisit. Penggunaan tanpa izin untuk serangan DDoS atau aktivitas ilegal lainnya adalah melanggar hukum.



