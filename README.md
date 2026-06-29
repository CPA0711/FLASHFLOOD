# 🌊 FLASHFLOOD - HTTP Load Testing Tool

[![Python](https://img.shields.io/badge/Python-3.7%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![GitHub stars](https://img.shields.io/github/stars/yourusername/flashflood)](https://github.com/yourusername/flashflood/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/yourusername/flashflood)](https://github.com/yourusername/flashflood/network)
[![GitHub issues](https://img.shields.io/github/issues/yourusername/flashflood)](https://github.com/yourusername/flashflood/issues)
[![GitHub pull requests](https://img.shields.io/github/issues-pr/yourusername/flashflood)](https://github.com/yourusername/flashflood/pulls)
[![GitHub contributors](https://img.shields.io/github/contributors/yourusername/flashflood)](https://github.com/yourusername/flashflood/graphs/contributors)
[![GitHub last commit](https://img.shields.io/github/last-commit/yourusername/flashflood)](https://github.com/yourusername/flashflood/commits/main)
[![GitHub release](https://img.shields.io/github/release/yourusername/flashflood)](https://github.com/yourusername/flashflood/releases)
[![GitHub repo size](https://img.shields.io/github/repo-size/yourusername/flashflood)](https://github.com/yourusername/flashflood)
[![Downloads](https://img.shields.io/github/downloads/yourusername/flashflood/total)](https://github.com/yourusername/flashflood/releases)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PyPI version](https://badge.fury.io/py/flashflood.svg)](https://badge.fury.io/py/flashflood)
[![Test](https://github.com/yourusername/flashflood/actions/workflows/python-package.yml/badge.svg)](https://github.com/yourusername/flashflood/actions/workflows/python-package.yml)

<p align="center">
  <img src="https://img.shields.io/badge/⭐-Star%20this%20repo-brightgreen?style=for-the-badge" alt="Star">
  <img src="https://img.shields.io/badge/🐛-Report%20Issue-red?style=for-the-badge" alt="Issue">
  <img src="https://img.shields.io/badge/💡-Feature%20Request-blue?style=for-the-badge" alt="Feature">
</p>

🚀 **FLASHFLOOD** adalah alat load testing HTTP yang powerful, ringan, dan mudah digunakan. Dirancang untuk menguji performa website dengan simulasi request HTTP secara paralel.

## ⭐ **Support this Project**

If you find FLASHFLOOD useful, please consider:

- ⭐ **Star** this repository on GitHub
- 🐛 **Report** issues you find
- 💡 **Suggest** new features
- 🔧 **Submit** pull requests

[![Star on GitHub](https://img.shields.io/github/stars/yourusername/flashflood?style=social)](https://github.com/yourusername/flashflood/stargazers)
[![Watch on GitHub](https://img.shields.io/github/watchers/yourusername/flashflood?style=social)](https://github.com/yourusername/flashflood/watchers)
[![Fork on GitHub](https://img.shields.io/github/forks/yourusername/flashflood?style=social)](https://github.com/yourusername/flashflood/network/members)

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

## 📊 Project Statistics

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/flashflood&type=Date)](https://star-history.com/#yourusername/flashflood&Date)

| Metric | Value |
|--------|-------|
| ⭐ Stars | [![GitHub stars](https://img.shields.io/github/stars/yourusername/flashflood)](https://github.com/yourusername/flashflood/stargazers) |
| 🍴 Forks | [![GitHub forks](https://img.shields.io/github/forks/yourusername/flashflood)](https://github.com/yourusername/flashflood/network) |
| 🐛 Issues | [![GitHub issues](https://img.shields.io/github/issues/yourusername/flashflood)](https://github.com/yourusername/flashflood/issues) |
| 🔀 PRs | [![GitHub pull requests](https://img.shields.io/github/issues-pr/yourusername/flashflood)](https://github.com/yourusername/flashflood/pulls) |
| 👥 Contributors | [![GitHub contributors](https://img.shields.io/github/contributors/yourusername/flashflood)](https://github.com/yourusername/flashflood/graphs/contributors) |
| 📦 Downloads | [![Downloads](https://img.shields.io/github/downloads/yourusername/flashflood/total)](https://github.com/yourusername/flashflood/releases) |

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/flashflood.git
cd flashflood

# Install dependencies
pip install -r requirements.txt

# Or install with pip
pip install flashflood

# Simple GET request
python flash.py --url https://example.com --no-proxy

# With auto-proxy (download proxies automatically)
python flash.py --url https://example.com --auto-proxy --threads 30

# High performance testing
python flash.py --url https://example.com --no-proxy --threads 50 --delay 0.01

# With logging
python flash.py --url https://example.com --no-proxy --threads 30 --log

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
🐛 Issues & Bug Reports

Found a bug? Please report it:

· 📌 Report Bug
· 💡 Request Feature
· ❓ Ask Question

🤝 Contributing

Kami sangat menghargai kontribusi! Silahkan baca CONTRIBUTING.md untuk panduan berkontribusi.

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

🙏 Acknowledgments

· requests - HTTP library
· TheSpeedX/SOCKS-List - Proxy list
· proxifly/free-proxy-list - Free proxy list

 GitHub Stats

<p align="center">
  <img src="https://github-readme-stats.vercel.app/api?username=yourusername&show_icons=true&count_private=true&hide_title=true&hide=prs&theme=radical" alt="GitHub Stats">
</p>

<p align="center">
  <img src="https://github-readme-stats.vercel.app/api/pin/?username=yourusername&repo=flashflood&theme=radical" alt="Repo Card">
</p>

---

⭐ Jika Anda menyukai project ini, berikan star! ⭐

https://img.shields.io/github/stars/yourusername/flashflood?style=for-the-badge&logo=github
https://img.shields.io/github/forks/yourusername/flashflood?style=for-the-badge&logo=github
https://img.shields.io/github/watchers/yourusername/flashflood?style=for-the-badge&logo=github

### **.github/ISSUE_TEMPLATE/bug_report.md**

```markdown
---
name: Bug Report
about: Create a report to help us improve
title: '[BUG] '
labels: bug
assignees: ''

---

## 🐛 Bug Description
A clear and concise description of what the bug is.

## 🔄 Steps to Reproduce
Steps to reproduce the behavior:
1. Run command '...'
2. See error '...'
3. ...

## ✅ Expected Behavior
A clear and concise description of what you expected to happen.

## 📸 Screenshots
If applicable, add screenshots to help explain your problem.

## 💻 Environment
- OS: [e.g., Windows 10, Ubuntu 22.04]
- Python Version: [e.g., 3.9.7]
- FLASHFLOOD Version: [e.g., 0.4.3]
- Command used: [e.g., python flash.py --url https://example.com]

## 📋 Additional Context
Add any other context about the problem here.

## 🔍 Logs
```

Paste any relevant logs here

```
```

.github/ISSUE_TEMPLATE/feature_request.md

```markdown
---
name: Feature Request
about: Suggest an idea for this project
title: '[FEATURE] '
labels: enhancement
assignees: ''

---

## 💡 Feature Description
A clear and concise description of what you want to happen.

## 🤔 Why is this needed?
Explain why this feature would be useful.

## 🔄 Alternative Solutions
Describe any alternative solutions or features you've considered.

## 📋 Additional Context
Add any other context or screenshots about the feature request here.
```

.github/ISSUE_TEMPLATE/question.md

```markdown
---
name: Question
about: Ask a question about FLASHFLOOD
title: '[QUESTION] '
labels: question
assignees: ''

---

## ❓ Question
Ask your question here.

## 💻 Environment
- OS: [e.g., Windows 10, Ubuntu 22.04]
- Python Version: [e.g., 3.9.7]
- FLASHFLOOD Version: [e.g., 0.4.3]
- Command used: [e.g., python flash.py --url https://example.com]

## 📋 Additional Context
Add any other context here.
```

---

📄 Tambahkan GitHub Profile README Badge

Link untuk Badge yang Bisa Dicopy:

```markdown
[![GitHub stars](https://img.shields.io/github/stars/yourusername/flashflood)](https://github.com/yourusername/flashflood/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/yourusername/flashflood)](https://github.com/yourusername/flashflood/issues)
[![GitHub forks](https://img.shields.io/github/forks/yourusername/flashflood)](https://github.com/yourusername/flashflood/network)
[![GitHub pull requests](https://img.shields.io/github/issues-pr/yourusername/flashflood)](https://github.com/yourusername/flashflood/pulls)
```

---
