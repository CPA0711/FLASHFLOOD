# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
CPA FLASHFLOOD V2 - HTTP Load 
"""

import sys
import os
import threading
import random
import requests
import time
import getopt
import urllib.parse
import json
import datetime
import re
from urllib.parse import urlparse
from threading import Thread, Event
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

# Warna untuk terminal
class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    END = '\033[0m'

VERSION = (1, 0, 0)
__version__ = '%d.%d.%d' % VERSION[0:3]

if sys.version_info[0:2] < (3, 5):
    raise RuntimeError('Python 3.5 or higher is required!')

# Banner
BANNER = f"""
{Colors.CYAN}
██████╗ ██████╗  █████╗ ███████╗██╗     ███████╗██╗  ██╗██╗     ██████╗  ██████╗ 
██╔══██╗██╔══██╗██╔══██╗██╔════╝██║     ██╔════╝██║  ██║██║     ██╔══██╗██╔═══██╗
██████╔╝██████╔╝███████║█████╗  ██║     █████╗  ███████║██║     ██║  ██║██║   ██║
██╔═══╝ ██╔══██╗██╔══██║██╔══╝  ██║     ██╔══╝  ██╔══██║██║     ██║  ██║██║   ██║
██║     ██║  ██║██║  ██║███████╗███████╗██║     ██║  ██║███████╗██████╔╝╚██████╔╝
╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝╚═╝     ╚═╝  ╚═╝╚══════╝╚═════╝  ╚═════╝ 
                     CPA TOOLS DEVELOPMENT - V2
{Colors.END}"""

# File konfigurasi
proxy_file = 'proxy.txt'
proxy_filtered_file = 'proxy_filtered.txt'
ua_file = 'user-agents.txt'
ref_file = 'referers.txt'
log_file = 'flashflood_v2.log'

# URL untuk auto-download proxy (lebih banyak sumber)
PROXY_SOURCES = [
    'https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/protocols/http/data.txt',
    'https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt',
    'https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt',
    'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt',
    'https://raw.githubusercontent.com/almightyuncle/Proxy-List/master/http.txt',
    'https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt',
    'https://raw.githubusercontent.com/maherabd/proxy-list/main/proxies/http.txt',
    'https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt',
    'https://raw.githubusercontent.com/zevtyardt/proxy-list/main/http.txt',
    'https://raw.githubusercontent.com/mmpx12/proxy-list/master/http.txt',
    'https://raw.githubusercontent.com/opsxcq/proxy-list/master/list.txt',
    'https://raw.githubusercontent.com/fate0/proxylist/master/proxy.list',
]

ex = Event()
rps_limit = 0
post_data = None
rps_tokens = 20
last_refill = time.time()
ips = []
filtered_ips = []
ref = []
ua = []
cookies = {}
timeout = 10
url = ''
max_threads = 20
request_delay = 1
total_requests = 0
success_requests = 0
failed_requests = 0
status_codes = defaultdict(int)
lock = threading.Lock()
start_time = 0
use_proxy = True
method = 'GET'
custom_headers = {}
use_jitter = False
jitter_min = 0.5
jitter_max = 1.5
save_log = False
log_data = []
verify_ssl = True
follow_redirects = True
retry_count = 0
retry_delay = 1
auto_update_proxy = False
proxy_update_interval = 600
last_proxy_update = 0
proxy_filter_enabled = True
proxy_test_timeout = 5
bad_proxies = set()
proxy_stats = defaultdict(lambda: {'success': 0, 'fail': 0, 'last_used': 0})

DEFAULT_UA = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPad; CPU OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
]

DEFAULT_REF = [
    'https://www.google.com/',
    'https://www.bing.com/',
    'https://www.yahoo.com/',
    'https://duckduckgo.com/',
    'https://www.facebook.com/',
    'https://www.twitter.com/',
    'https://www.instagram.com/',
    'https://www.linkedin.com/',
    'https://www.youtube.com/',
    'https://www.reddit.com/',
]

def wait_for_rps_token():
    """Token bucket algorithm for rate limiting"""
    global rps_tokens, last_refill, rps_limit
    
    if rps_limit <= 0:
        return
    
    with lock:
        now = time.time()
        elapsed = now - last_refill
        rps_tokens = min(rps_tokens + elapsed * rps_limit, rps_limit)
        last_refill = now
        
        if rps_tokens < 1:
            wait_time = (1 - rps_tokens) / rps_limit
            lock.release()
            time.sleep(wait_time)
            lock.acquire()
            now = time.time()
            elapsed = now - last_refill
            rps_tokens = min(rps_tokens + elapsed * rps_limit, rps_limit)
            last_refill = now
        
        rps_tokens -= 1

def test_proxy(proxy):
    """Test if a proxy is working"""
    try:
        test_url = 'http://httpbin.org/ip'
        proxies = {
            'http': f'http://{proxy}',
            'https': f'http://{proxy}'
        }
        response = requests.get(test_url, proxies=proxies, timeout=proxy_test_timeout)
        return response.status_code == 200
    except:
        return False

def filter_proxies(proxy_list):
    """Filter working proxies with multithreading"""
    global filtered_ips, bad_proxies
    
    if not proxy_list:
        return []
    
    print(f"{Colors.CYAN}🔍 Testing {len(proxy_list)} proxies...{Colors.END}")
    
    working = []
    total = len(proxy_list)
    
    with ThreadPoolExecutor(max_workers=50) as executor:
        future_to_proxy = {executor.submit(test_proxy, proxy): proxy for proxy in proxy_list}
        
        for i, future in enumerate(as_completed(future_to_proxy)):
            proxy = future_to_proxy[future]
            try:
                if future.result():
                    working.append(proxy)
                    print(f"{Colors.GREEN}✓ [{i+1}/{total}] {proxy} - Working{Colors.END}")
                else:
                    bad_proxies.add(proxy)
                    print(f"{Colors.RED}✗ [{i+1}/{total}] {proxy} - Failed{Colors.END}")
            except:
                bad_proxies.add(proxy)
                print(f"{Colors.RED}✗ [{i+1}/{total}] {proxy} - Error{Colors.END}")
    
    filtered_ips = working
    
    # Save filtered proxies
    try:
        with open(proxy_filtered_file, 'w') as f:
            f.write(f'# Filtered proxies - {len(working)} working\n')
            f.write(f'# Total tested: {total}\n')
            f.write(f'# Updated: {datetime.datetime.now().isoformat()}\n\n')
            f.write('\n'.join(working))
        print(f"{Colors.GREEN}✅ Saved {len(working)} working proxies to {proxy_filtered_file}{Colors.END}")
    except:
        pass
    
    return working

def download_proxies():
    """Download proxy list from online sources"""
    global ips, last_proxy_update
    all_proxies = []
    
    print(f"{Colors.CYAN}🌐 Downloading proxies from online sources...{Colors.END}")
    
    for source in PROXY_SOURCES:
        try:
            print(f"{Colors.DIM}  ↳ Fetching: {source[:60]}...{Colors.END}")
            response = requests.get(source, timeout=30)
            if response.status_code == 200:
                proxies = [line.strip() for line in response.text.split('\n') 
                          if line.strip() and not line.startswith('#')]
                proxies = [p.replace('http://', '').replace('https://', '').replace('socks5://', '') for p in proxies]
                proxies = [p for p in proxies if ':' in p and len(p.split(':')) == 2]
                proxies = [p for p in proxies if re.match(r'^\d+\.\d+\.\d+\.\d+:\d+$', p)]
                
                if proxies:
                    all_proxies.extend(proxies)
                    print(f"{Colors.GREEN}  ✓ Got {len(proxies)} proxies{Colors.END}")
            else:
                print(f"{Colors.YELLOW}  ⚠ Failed (status: {response.status_code}){Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}  ✗ Error: {str(e)[:50]}{Colors.END}")
        time.sleep(0.5)
    
    if all_proxies:
        all_proxies = list(dict.fromkeys(all_proxies))
        ips = all_proxies
        last_proxy_update = time.time()
        
        try:
            with open(proxy_file, 'w') as f:
                f.write(f'# Total proxies: {len(ips)}\n')
                f.write(f'# Updated: {datetime.datetime.now().isoformat()}\n\n')
                f.write('\n'.join(ips))
            print(f"{Colors.GREEN}✅ Saved {len(ips)} proxies to {proxy_file}{Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}✗ Error saving proxies: {e}{Colors.END}")
        
        # Filter proxies if enabled
        if proxy_filter_enabled:
            filtered = filter_proxies(all_proxies[:200])  # Test first 200
            if filtered:
                ips = filtered
                print(f"{Colors.GREEN}✅ Using {len(filtered)} working proxies{Colors.END}")
    else:
        print(f"{Colors.YELLOW}⚠ No proxies downloaded{Colors.END}")
    
    return all_proxies

def update_proxies_if_needed():
    """Update proxies if interval has passed"""
    global ips, last_proxy_update
    
    if auto_update_proxy and (time.time() - last_proxy_update > proxy_update_interval):
        print(f"\n{Colors.CYAN}🔄 Updating proxies...{Colors.END}")
        downloaded = download_proxies()
        if downloaded and proxy_filter_enabled:
            filtered = filter_proxies(downloaded[:200])
            if filtered:
                ips = filtered
        elif downloaded:
            ips = downloaded
        print(f"{Colors.GREEN}✅ Proxy updated! Total: {len(ips)}{Colors.END}\n")

def get_working_proxy():
    """Get a working proxy from filtered list"""
    global filtered_ips, ips, bad_proxies
    
    available = filtered_ips if filtered_ips else ips
    
    if not available:
        return None
    
    # Try to find a proxy that hasn't been marked as bad
    for _ in range(10):
        proxy = random.choice(available)
        if proxy not in bad_proxies:
            return proxy
    
    # If all proxies are bad, reset bad list and try again
    if len(bad_proxies) > len(available) * 0.5:
        print(f"{Colors.YELLOW}⚠ Many proxies failed, resetting bad list{Colors.END}")
        bad_proxies.clear()
        return random.choice(available)
    
    return random.choice(available)

def main(argv):
    global use_proxy, method, custom_headers, use_jitter, jitter_min, jitter_max, save_log
    global max_threads, timeout, request_delay, verify_ssl, follow_redirects
    global retry_count, retry_delay, auto_update_proxy, proxy_update_interval, rps_limit
    global rps_tokens, post_data, proxy_filter_enabled, proxy_test_timeout
    
    print(BANNER)
    print(f"{Colors.CYAN}🚀 CPA FLASHFLOOD V2 v{__version__} - HTTP LOAD TESTER{Colors.END}")
    print(f"{Colors.YELLOW}🔧 Auto Proxy Download & Filter | RPS Control | Multi-Thread{Colors.END}\n")
    
    try:
        opts, args = getopt.getopt(argv, 'hv:t:X:H:j:l:d:s',
            ['help', 'url=', 'timeout=', 'threads=', 'delay=', 'no-proxy',
             'method=', 'header=', 'jitter=', 'log', 'no-verify',
             'no-redirect', 'retry=', 'retry-delay=', 'rps=', 'data=',
             'data-file=', 'auto-proxy', 'proxy-interval=', 'no-filter',
             'proxy-test-timeout='])
    except getopt.GetoptError as err:
        print(f"{Colors.RED}✗ Error: {err}{Colors.END}")
        showUsage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            showUsage()
            sys.exit(0)
        elif opt in ('-v', '--url'):
            globals()['url'] = urllib.parse.unquote(arg)
        elif opt in ('-t', '--timeout'):
            try:
                timeout = int(arg)
                if timeout < 1:
                    print(f"{Colors.RED}✗ Error: Timeout must be >= 1{Colors.END}")
                    sys.exit(2)
            except ValueError:
                print(f"{Colors.RED}✗ Error: Timeout must be integer{Colors.END}")
                sys.exit(2)
        elif opt == '--threads':
            try:
                max_threads = int(arg)
                if max_threads < 1 or max_threads > 1000:
                    print(f"{Colors.RED}✗ Error: Threads must be between 1-1000{Colors.END}")
                    sys.exit(2)
            except ValueError:
                print(f"{Colors.RED}✗ Error: Threads must be integer{Colors.END}")
                sys.exit(2)
        elif opt == '--delay':
            try:
                request_delay = float(arg)
                if request_delay < 0:
                    print(f"{Colors.RED}✗ Error: Delay must be >= 0{Colors.END}")
                    sys.exit(2)
            except ValueError:
                print(f"{Colors.RED}✗ Error: Delay must be number{Colors.END}")
                sys.exit(2)
        elif opt == '--no-proxy':
            use_proxy = False
            print(f"{Colors.YELLOW}⚠️ Proxy disabled{Colors.END}")
        elif opt in ('--method', '-X'):
            method = arg.upper()
            if method not in ['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS', 'PATCH']:
                print(f"{Colors.RED}✗ Error: Invalid method{Colors.END}")
                sys.exit(2)
            print(f"{Colors.CYAN}ℹ Method: {method}{Colors.END}")
        elif opt in ('--header', '-H'):
            try:
                key, value = arg.split(':', 1)
                custom_headers[key.strip()] = value.strip()
                print(f"{Colors.CYAN}ℹ Header: {key.strip()}: {value.strip()}{Colors.END}")
            except:
                print(f"{Colors.RED}✗ Error: Invalid header format{Colors.END}")
                sys.exit(2)
        elif opt in ('--jitter', '-j'):
            use_jitter = True
            try:
                if ',' in arg:
                    parts = arg.split(',')
                    jitter_min = float(parts[0])
                    jitter_max = float(parts[1])
                else:
                    base = float(arg)
                    jitter_min = base * 0.5
                    jitter_max = base * 1.5
                print(f"{Colors.CYAN}ℹ Jitter: {jitter_min:.2f}s - {jitter_max:.2f}s{Colors.END}")
            except:
                print(f"{Colors.RED}✗ Error: Invalid jitter format{Colors.END}")
                sys.exit(2)
        elif opt in ('--log', '-l'):
            save_log = True
            print(f"{Colors.CYAN}ℹ Logging enabled{Colors.END}")
        elif opt == '--no-verify':
            verify_ssl = False
            print(f"{Colors.YELLOW}⚠️ SSL verification disabled{Colors.END}")
        elif opt == '--no-redirect':
            follow_redirects = False
            print(f"{Colors.YELLOW}⚠️ Redirects disabled{Colors.END}")
        elif opt == '--retry':
            try:
                retry_count = int(arg)
                print(f"{Colors.CYAN}ℹ Retry: {retry_count}{Colors.END}")
            except:
                print(f"{Colors.RED}✗ Error: Invalid retry count{Colors.END}")
                sys.exit(2)
        elif opt == '--retry-delay':
            try:
                retry_delay = float(arg)
                print(f"{Colors.CYAN}ℹ Retry delay: {retry_delay}s{Colors.END}")
            except:
                print(f"{Colors.RED}✗ Error: Invalid retry delay{Colors.END}")
                sys.exit(2)
        elif opt == '--rps':
            try:
                rps_limit = int(arg)
                if rps_limit < 1:
                    print(f"{Colors.RED}✗ Error: RPS must be >= 1{Colors.END}")
                    sys.exit(2)
                rps_tokens = rps_limit
                print(f"{Colors.CYAN}ℹ RPS Limit: {rps_limit}/s{Colors.END}")
            except:
                print(f"{Colors.RED}✗ Error: Invalid RPS{Colors.END}")
                sys.exit(2)
        elif opt == '--data' or opt == '-d':
            post_data = arg
            print(f"{Colors.CYAN}ℹ POST Data: {post_data[:50]}...{Colors.END}")
        elif opt == '--data-file':
            try:
                with open(arg, 'r') as f:
                    post_data = f.read()
                print(f"{Colors.CYAN}ℹ POST Data loaded from: {arg}{Colors.END}")
            except:
                print(f"{Colors.RED}✗ Error: Cannot read file{Colors.END}")
                sys.exit(2)
        elif opt == '--auto-proxy':
            auto_update_proxy = True
            print(f"{Colors.CYAN}ℹ Auto-proxy enabled (update every {proxy_update_interval//60} min){Colors.END}")
        elif opt == '--proxy-interval':
            try:
                proxy_update_interval = int(arg) * 60
                if proxy_update_interval < 60:
                    print(f"{Colors.YELLOW}⚠ Minimum interval is 1 minute{Colors.END}")
                    proxy_update_interval = 60
                print(f"{Colors.CYAN}ℹ Proxy update interval: {proxy_update_interval//60} minutes{Colors.END}")
            except:
                print(f"{Colors.RED}✗ Error: Invalid proxy interval{Colors.END}")
                sys.exit(2)
        elif opt == '--no-filter':
            proxy_filter_enabled = False
            print(f"{Colors.YELLOW}⚠️ Proxy filtering disabled{Colors.END}")
        elif opt == '--proxy-test-timeout':
            try:
                proxy_test_timeout = int(arg)
                print(f"{Colors.CYAN}ℹ Proxy test timeout: {proxy_test_timeout}s{Colors.END}")
            except:
                print(f"{Colors.RED}✗ Error: Invalid timeout{Colors.END}")
                sys.exit(2)

    if not url:
        print(f"{Colors.RED}✗ Error: URL is required!{Colors.END}")
        showUsage()
        sys.exit(2)

    parseFiles()

def parseFiles():
    global ips, ua, ref, filtered_ips
    
    ua = DEFAULT_UA.copy()
    ref = DEFAULT_REF.copy()
    
    print(f"{Colors.CYAN}📁 Loading Configuration{Colors.END}")
    
    # Load existing proxies
    if use_proxy:
        try:
            if os.path.exists(proxy_file) and os.stat(proxy_file).st_size > 0:
                with open(proxy_file, 'r') as f:
                    content = [row.rstrip() for row in f if row.rstrip() and not row.startswith('#')]
                    if content:
                        ips = content
                        print(f"{Colors.GREEN}  ✓ Loaded {len(ips)} proxies from file{Colors.END}")
                        
                        # Load filtered proxies if exists
                        if os.path.exists(proxy_filtered_file):
                            with open(proxy_filtered_file, 'r') as f:
                                filtered = [row.rstrip() for row in f if row.rstrip() and not row.startswith('#')]
                                if filtered:
                                    filtered_ips = filtered
                                    print(f"{Colors.GREEN}  ✓ Loaded {len(filtered_ips)} working proxies{Colors.END}")
        except Exception as e:
            print(f"{Colors.YELLOW}  ⚠ Error loading proxies: {e}{Colors.END}")
    
    # Auto download proxies if enabled
    if auto_update_proxy:
        downloaded = download_proxies()
        if downloaded and proxy_filter_enabled:
            filtered = filter_proxies(downloaded[:200])
            if filtered:
                ips = filtered
                filtered_ips = filtered
    
    # Load user-agents
    try:
        if os.path.exists(ua_file) and os.stat(ua_file).st_size > 0:
            with open(ua_file, 'r') as f:
                content = [row.rstrip() for row in f if row.rstrip()]
                if content:
                    ua = content
                    print(f"{Colors.GREEN}  ✓ Loaded {len(ua)} user-agents{Colors.END}")
    except:
        pass
    
    # Load referers
    try:
        if os.path.exists(ref_file) and os.stat(ref_file).st_size > 0:
            with open(ref_file, 'r') as f:
                content = [row.rstrip() for row in f if row.rstrip()]
                if content:
                    ref = content
                    print(f"{Colors.GREEN}  ✓ Loaded {len(ref)} referers{Colors.END}")
    except:
        pass
    
    proxy_status = f"{len(filtered_ips) if filtered_ips else len(ips)} proxies" if ips and use_proxy else "Direct connection"
    print(f"{Colors.CYAN}📊 Summary: {proxy_status}, {len(ua)} UAs, {len(ref)} referers{Colors.END}")
    if auto_update_proxy:
        print(f"{Colors.CYAN}📊 Auto-Proxy: Enabled (updates every {proxy_update_interval//60} min){Colors.END}")
    if proxy_filter_enabled:
        print(f"{Colors.CYAN}📊 Proxy Filter: Enabled{Colors.END}")
    print()
    
    testConnection()

def testConnection():
    print(f"{Colors.CYAN}🔗 Testing Connection{Colors.END}")
    print(f"{Colors.WHITE}URL: {Colors.GREEN}{url}{Colors.END}")
    
    try:
        if method == 'GET':
            r = requests.get(url, timeout=timeout)
        elif method == 'POST':
            r = requests.post(url, timeout=timeout)
        elif method == 'HEAD':
            r = requests.head(url, timeout=timeout)
        else:
            r = requests.request(method, url, timeout=timeout)
        
        print(f"{Colors.WHITE}Status: {Colors.GREEN}{r.status_code} | Size: {len(r.content)} bytes{Colors.END}")
        print(f"{Colors.GREEN}✅ Connection successful!{Colors.END}\n")
        startTesting()
    except Exception as e:
        print(f"{Colors.RED}❌ Connection failed: {e}{Colors.END}")
        sys.exit(1)

def request_testing(index):
    global total_requests, success_requests, failed_requests, status_codes
    
    while not ex.is_set():
        try:
            wait_for_rps_token()
            update_proxies_if_needed()
            
            if use_jitter:
                current_delay = random.uniform(jitter_min, jitter_max)
            else:
                current_delay = request_delay
            
            proxy = None
            proxy_str = 'Direct'
            
            if use_proxy:
                proxy_ip = get_working_proxy()
                if proxy_ip:
                    proxy = {
                        'http': f'http://{proxy_ip}',
                        'https': f'http://{proxy_ip}'
                    }
                    proxy_str = proxy_ip
                else:
                    # No working proxy available
                    with lock:
                        failed_requests += 1
                    time.sleep(2)
                    continue
            
            headers = {
                'User-Agent': random.choice(ua),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': random.choice(ref),
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive'
            }
            
            if custom_headers:
                headers.update(custom_headers)
            
            if not verify_ssl:
                requests.packages.urllib3.disable_warnings()
            
            success = False
            for attempt in range(retry_count + 1):
                try:
                    start_time_req = time.time()
                    
                    req_kwargs = {
                        'headers': headers,
                        'proxies': proxy,
                        'timeout': timeout,
                        'verify': verify_ssl,
                        'allow_redirects': follow_redirects
                    }
                    
                    if method in ['POST', 'PUT', 'PATCH'] and post_data:
                        req_kwargs['data'] = post_data
                        if 'Content-Type' not in headers:
                            headers['Content-Type'] = 'application/x-www-form-urlencoded'
                    
                    if method == 'GET':
                        r = requests.get(url, **req_kwargs)
                    elif method == 'POST':
                        r = requests.post(url, **req_kwargs)
                    elif method == 'HEAD':
                        r = requests.head(url, **req_kwargs)
                    else:
                        r = requests.request(method, url, **req_kwargs)
                    
                    response_time = time.time() - start_time_req
                    success = True
                    break
                except Exception as e:
                    if attempt < retry_count:
                        time.sleep(retry_delay)
                        continue
                    raise
            
            with lock:
                total_requests += 1
                
                if success:
                    status_codes[r.status_code] += 1
                    if 200 <= r.status_code < 300:
                        success_requests += 1
                        status_color = Colors.GREEN
                    elif 300 <= r.status_code < 400:
                        success_requests += 1
                        status_color = Colors.BLUE
                    else:
                        failed_requests += 1
                        status_color = Colors.YELLOW
                        if proxy_str != 'Direct':
                            bad_proxies.add(proxy_str)
                else:
                    failed_requests += 1
                    status_color = Colors.RED
                    if proxy_str != 'Direct':
                        bad_proxies.add(proxy_str)
                
                if save_log and success:
                    log_data.append({
                        'time': datetime.datetime.now().isoformat(),
                        'thread': index,
                        'status': r.status_code if success else 'ERROR',
                        'time_ms': round(response_time * 1000, 2) if success else 0,
                        'proxy': proxy_str
                    })
            
            if success:
                delay_info = f" | jitter: {current_delay:.2f}s" if use_jitter else ""
                print(f"{status_color}[{index:>2}] {r.status_code:>3} | {response_time:>5.2f}s | {proxy_str}{delay_info}{Colors.END}")
            else:
                print(f"{Colors.RED}[{index:>2}] FAILED | {proxy_str}{Colors.END}")
            
            if current_delay > 0:
                time.sleep(current_delay)
            
        except Exception as e:
            print(f"{Colors.RED}[{index:>2}] ERROR: {str(e)[:30]}{Colors.END}")
            with lock:
                total_requests += 1
                failed_requests += 1
                status_codes['ERROR'] += 1
            time.sleep(1)

def startTesting():
    global start_time
    start_time = time.time()
    
    proxy_status = f"{len(filtered_ips) if filtered_ips else len(ips)} proxies" if ips and use_proxy else "Direct"
    print(f"{Colors.GREEN}🚀 Starting Attack{Colors.END}")
    print(f"{Colors.WHITE}Threads: {Colors.GREEN}{max_threads} | Timeout: {timeout}s | Delay: {request_delay}s{Colors.END}")
    print(f"{Colors.WHITE}Method: {Colors.GREEN}{method} | Proxy: {proxy_status}{Colors.END}")
    if auto_update_proxy:
        print(f"{Colors.WHITE}Auto-Proxy: {Colors.GREEN}Enabled (update every {proxy_update_interval//60} min){Colors.END}")
    if rps_limit > 0:
        print(f"{Colors.WHITE}RPS Limit: {Colors.GREEN}{rps_limit}/s{Colors.END}")
    print(f"{Colors.YELLOW}Press Ctrl+C to stop{Colors.END}\n")
    
    threads = []
    print(f"{Colors.DIM}─── Request Log ───{Colors.END}")
    
    for i in range(max_threads):
        t = threading.Thread(target=request_testing, args=(i,))
        t.daemon = True
        t.start()
        threads.append(t)
    
    try:
        while True:
            time.sleep(1)
            if int(time.time()) % 5 == 0:
                elapsed = time.time() - start_time
                with lock:
                    print(f"\n{Colors.CYAN}📊 STATISTICS{Colors.END}")
                    print(f"{Colors.WHITE}Time: {Colors.GREEN}{elapsed:.1f}s | Requests: {total_requests} | Success: {success_requests} | Failed: {failed_requests}{Colors.END}")
                    if total_requests > 0:
                        rate = (success_requests / total_requests) * 100
                        rps = total_requests / elapsed if elapsed > 0 else 0
                        print(f"{Colors.WHITE}Success Rate: {Colors.GREEN}{rate:.1f}% | RPS: {rps:.1f}{Colors.END}")
                    if rps_limit > 0:
                        print(f"{Colors.WHITE}RPS Limit: {Colors.GREEN}{rps_limit}/s{Colors.END}")
                    print()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}🛑 Stopping...{Colors.END}")
        ex.set()
        
        if save_log and log_data:
            try:
                with open(log_file, 'w') as f:
                    json.dump(log_data, f, indent=2)
                print(f"{Colors.GREEN}✅ Log saved to {log_file}{Colors.END}")
            except:
                pass
        
        elapsed = time.time() - start_time
        print(f"\n{Colors.CYAN}📊 FINAL STATISTICS{Colors.END}")
        print(f"{Colors.WHITE}Time: {Colors.GREEN}{elapsed:.1f}s{Colors.END}")
        print(f"{Colors.WHITE}Requests: {Colors.GREEN}{total_requests}{Colors.END}")
        print(f"{Colors.WHITE}Success: {Colors.GREEN}{success_requests}{Colors.END}")
        print(f"{Colors.WHITE}Failed: {Colors.RED}{failed_requests}{Colors.END}")
        if total_requests > 0:
            rate = (success_requests / total_requests) * 100
            rps = total_requests / elapsed if elapsed > 0 else 0
            print(f"{Colors.WHITE}Success Rate: {Colors.GREEN}{rate:.1f}% | RPS: {rps:.1f}{Colors.END}")
        print(f"{Colors.GREEN}✅ CPA FLASHFLOOD V2 Stopped!{Colors.END}\n")

def showUsage():
    print(f"""
{Colors.CYAN}CPA FLASHFLOOD V2 v{__version__} - HTTP Load Tester{Colors.END}

{Colors.GREEN}Usage:{Colors.END}
  python flashV2.py --url <URL> [options]

{Colors.GREEN}Options:{Colors.END}
  --url <URL>              Target URL
  -t, --timeout <SEC>      Timeout (default: 10)
  --threads <NUM>          Threads (default: 20, max: 1000)
  --delay <SEC>            Delay between requests (default: 1.0)
  --no-proxy               Disable proxy
  -X, --method <M>         HTTP method (GET, POST, etc.)
  -H, --header <H>         Custom header (format: "Key: Value")
  -j, --jitter <V>         Random delay (min,max or single)
  -l, --log                Save log to file
  --no-verify              Disable SSL verification
  --no-redirect            Disable redirects
  --retry <NUM>            Retry count
  --retry-delay <SEC>      Retry delay
  --rps <NUM>              Rate limit per second
  -d, --data <DATA>        POST/PUT/PATCH data
  --data-file <FILE>       Load POST data from file
  --auto-proxy             Auto-download proxies
  --proxy-interval <M>     Proxy update interval (minutes)
  --no-filter              Disable proxy filtering
  --proxy-test-timeout <S> Proxy test timeout (default: 5)
  -h, --help               Show help

{Colors.GREEN}Examples:{Colors.END}
  python flashV2.py --url https://httpbin.org/get --auto-proxy --threads 30 --delay 0.05
  python flashV2.py --url https://example.com --no-proxy --threads 10 --jitter 0.5,1.5
  python flashV2.py --url https://api.example.com --method POST -d "key=value" --auto-proxy --rps 100
  python flashV2.py --url https://example.com --auto-proxy --no-filter --threads 50 --delay 0.02
{Colors.END}""")

if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Interrupted{Colors.END}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}Error: {e}{Colors.END}")
        sys.exit(1)
