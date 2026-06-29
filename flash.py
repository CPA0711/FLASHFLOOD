# -*- coding: utf-8 -*-
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
import socket
import ssl
from urllib.parse import urlparse
from threading import Thread, Event
from collections import defaultdict

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

VERSION = (0, 4, 0)
__version__ = '%d.%d.%d' % VERSION[0:3]

if sys.version_info[0:2] < (3, 5):
    raise RuntimeError('Python 3.5 or higher is required!')

# Banner
BANNER = f"""
{Colors.CYAN}
    ███████╗██╗      █████╗ ███████╗██╗  ██╗██╗  ██╗ ██████╗  ██████╗ ██████╗ 
    ██╔════╝██║     ██╔══██╗██╔════╝██║  ██║██║  ██║██╔═══██╗██╔═══██╗██╔══██╗
    █████╗  ██║     ███████║███████╗███████║███████║██║   ██║██║   ██║██████╔╝
    ██╔══╝  ██║     ██╔══██║╚════██║██╔══██║██╔══██║██║   ██║██║   ██║██╔══██╗
    ██║     ███████╗██║  ██║███████║██║  ██║██║  ██║╚██████╔╝╚██████╔╝██║  ██║
    ╚═╝     ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝
{Colors.END}"""

# File konfigurasi
proxy_file = 'proxy.txt'
ua_file = 'user-agents.txt'
ref_file = 'referers.txt'
log_file = 'flashflood.log'
payload_file = 'payloads.txt'
cookies_file = 'cookies.txt'

# URL untuk auto-download proxy
PROXY_SOURCES = [
    'https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/protocols/http/data.txt',
    'https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt',
    'https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt',
]

ex = Event()
ips = []
ref = []
ua = []
payloads = []
cookies = {}
timeout = 10
proto = ''
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
use_ssl = False
verify_ssl = True
follow_redirects = True
max_redirects = 3
use_keep_alive = True
timeout_connect = 5
timeout_read = 10
retry_count = 3
retry_delay = 1
use_random_delay = False
delay_min = 0.5
delay_max = 2.0
use_sequential = False
batch_size = 10
batch_delay = 0.5
auto_update_proxy = False
proxy_update_interval = 3600  # 1 hour default
last_proxy_update = 0

def download_proxies():
    """Download proxy list from online sources"""
    global ips, last_proxy_update
    all_proxies = []
    
    print(f"{Colors.CYAN}🌐 Downloading proxies from online sources...{Colors.END}")
    
    for source in PROXY_SOURCES:
        try:
            print(f"{Colors.DIM}  ↳ Fetching: {source}{Colors.END}")
            response = requests.get(source, timeout=30)
            if response.status_code == 200:
                proxies = [line.strip() for line in response.text.split('\n') 
                          if line.strip() and not line.startswith('#')]
                # Clean proxy format (remove http:// prefix if exists)
                proxies = [p.replace('http://', '').replace('https://', '') for p in proxies]
                if proxies:
                    all_proxies.extend(proxies)
                    print(f"{Colors.GREEN}  ✓ Got {len(proxies)} proxies from {source}{Colors.END}")
            else:
                print(f"{Colors.YELLOW}  ⚠ Failed to fetch from {source} (status: {response.status_code}){Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}  ✗ Error fetching from {source}: {e}{Colors.END}")
    
    if all_proxies:
        # Remove duplicates
        all_proxies = list(dict.fromkeys(all_proxies))
        ips = all_proxies
        last_proxy_update = time.time()
        
        # Save to file
        try:
            with open(proxy_file, 'w') as f:
                f.write('# Auto-updated proxies\n')
                f.write(f'# Total: {len(ips)} proxies\n')
                f.write(f'# Updated: {datetime.datetime.now().isoformat()}\n\n')
                f.write('\n'.join(ips))
            print(f"{Colors.GREEN}✅ Saved {len(ips)} proxies to {proxy_file}{Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}✗ Error saving proxies: {e}{Colors.END}")
    else:
        print(f"{Colors.YELLOW}⚠ No proxies downloaded, using existing proxies{Colors.END}")
    
    return all_proxies

def main(argv):
    global use_proxy, method, custom_headers, use_jitter, jitter_min, jitter_max, save_log
    global max_threads, timeout, request_delay, use_ssl, verify_ssl, follow_redirects
    global max_redirects, use_keep_alive, timeout_connect, timeout_read, retry_count
    global retry_delay, use_random_delay, delay_min, delay_max, use_sequential
    global batch_size, batch_delay, payloads, cookies, auto_update_proxy, proxy_update_interval
    
    print(BANNER)
    print(f"{Colors.CYAN}🚀 CPA FLASHFLOOD v{__version__} - Ultimate HTTP Load Tester{Colors.END}")
    print(f"{Colors.YELLOW}⚠️  For educational and testing purposes only!{Colors.END}")
    print(f"{Colors.YELLOW}Use only on websites you own or have permission{Colors.END}\n")
    
    try:
        opts, args = getopt.getopt(argv, 'hv:t:X:H:j:l:p:c:',
            ['help', 'url=', 'timeout=', 'threads=', 'delay=', 'no-proxy',
             'method=', 'header=', 'jitter=', 'log', 'ssl', 'no-verify',
             'no-redirect', 'keep-alive', 'connect-timeout=', 'read-timeout=',
             'retry=', 'retry-delay=', 'random-delay=', 'sequential',
             'batch=', 'batch-delay=', 'payload=', 'cookie=', 'auto-proxy',
             'proxy-interval='])
    except getopt.GetoptError as err:
        print(f"{Colors.RED}✗ Error: {err}{Colors.END}")
        showUsage()
        sys.exit(2)
    
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            showUsage()
            sys.exit(2)
        elif opt in ('-v', '--url'):
            if len(arg) >= 1:
                global url, proto
                url = urllib.parse.unquote(arg)
                link = urlparse(url)
                proto = link.scheme
                if proto == 'https':
                    use_ssl = True
            else:
                print(f"{Colors.RED}✗ Error: URL cannot be empty!{Colors.END}")
                sys.exit(2)
        elif opt in ('-t', '--timeout'):
            try:
                arg = int(arg)
                if arg >= 1:
                    timeout = arg
                    timeout_connect = arg
                    timeout_read = arg
                else:
                    print(f"{Colors.RED}✗ Error: Timeout must be >= 1{Colors.END}")
                    sys.exit(2)
            except ValueError:
                print(f"{Colors.RED}✗ Error: Timeout must be integer{Colors.END}")
                sys.exit(2)
        elif opt == '--threads':
            try:
                arg = int(arg)
                if arg >= 1 and arg <= 500:
                    max_threads = arg
                else:
                    print(f"{Colors.RED}✗ Error: Threads must be between 1-500{Colors.END}")
                    sys.exit(2)
            except ValueError:
                print(f"{Colors.RED}✗ Error: Threads must be integer{Colors.END}")
                sys.exit(2)
        elif opt == '--delay':
            try:
                arg = float(arg)
                if arg >= 0:
                    request_delay = arg
                else:
                    print(f"{Colors.RED}✗ Error: Delay must be >= 0{Colors.END}")
                    sys.exit(2)
            except ValueError:
                print(f"{Colors.RED}✗ Error: Delay must be number{Colors.END}")
                sys.exit(2)
        elif opt == '--no-proxy':
            use_proxy = False
            print(f"{Colors.YELLOW}⚠️  Proxy disabled, using direct connection{Colors.END}")
        elif opt in ('--method', '-X'):
            method = arg.upper()
            if method not in ['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS', 'PATCH', 'TRACE']:
                print(f"{Colors.RED}✗ Error: Invalid method {method}{Colors.END}")
                sys.exit(2)
            print(f"{Colors.CYAN}ℹ Using method: {method}{Colors.END}")
        elif opt in ('--header', '-H'):
            try:
                key, value = arg.split(':', 1)
                custom_headers[key.strip()] = value.strip()
                print(f"{Colors.CYAN}ℹ Custom header: {key.strip()}: {value.strip()}{Colors.END}")
            except:
                print(f"{Colors.RED}✗ Error: Invalid header format. Use 'Key: Value'{Colors.END}")
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
                print(f"{Colors.CYAN}ℹ Jitter enabled: {jitter_min:.2f}s - {jitter_max:.2f}s{Colors.END}")
            except:
                print(f"{Colors.RED}✗ Error: Invalid jitter format. Use 'min,max' or single value{Colors.END}")
                sys.exit(2)
        elif opt in ('--log', '-l'):
            save_log = True
            print(f"{Colors.CYAN}ℹ Logging enabled: {log_file}{Colors.END}")
        elif opt == '--ssl':
            use_ssl = True
            print(f"{Colors.CYAN}ℹ SSL/TLS enabled{Colors.END}")
        elif opt == '--no-verify':
            verify_ssl = False
            print(f"{Colors.YELLOW}⚠️  SSL verification disabled{Colors.END}")
        elif opt == '--no-redirect':
            follow_redirects = False
            print(f"{Colors.YELLOW}⚠️  Redirects disabled{Colors.END}")
        elif opt == '--keep-alive':
            use_keep_alive = True
            print(f"{Colors.CYAN}ℹ Keep-Alive enabled{Colors.END}")
        elif opt == '--connect-timeout':
            try:
                timeout_connect = int(arg)
                print(f"{Colors.CYAN}ℹ Connect timeout: {timeout_connect}s{Colors.END}")
            except:
                print(f"{Colors.RED}✗ Error: Invalid connect timeout{Colors.END}")
                sys.exit(2)
        elif opt == '--read-timeout':
            try:
                timeout_read = int(arg)
                print(f"{Colors.CYAN}ℹ Read timeout: {timeout_read}s{Colors.END}")
            except:
                print(f"{Colors.RED}✗ Error: Invalid read timeout{Colors.END}")
                sys.exit(2)
        elif opt == '--retry':
            try:
                retry_count = int(arg)
                print(f"{Colors.CYAN}ℹ Retry count: {retry_count}{Colors.END}")
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
        elif opt == '--random-delay':
            use_random_delay = True
            try:
                if ',' in arg:
                    parts = arg.split(',')
                    delay_min = float(parts[0])
                    delay_max = float(parts[1])
                else:
                    base = float(arg)
                    delay_min = base * 0.5
                    delay_max = base * 1.5
                print(f"{Colors.CYAN}ℹ Random delay: {delay_min:.2f}s - {delay_max:.2f}s{Colors.END}")
            except:
                print(f"{Colors.RED}✗ Error: Invalid random delay format{Colors.END}")
                sys.exit(2)
        elif opt == '--sequential':
            use_sequential = True
            print(f"{Colors.CYAN}ℹ Sequential mode enabled{Colors.END}")
        elif opt == '--batch':
            try:
                batch_size = int(arg)
                print(f"{Colors.CYAN}ℹ Batch size: {batch_size}{Colors.END}")
            except:
                print(f"{Colors.RED}✗ Error: Invalid batch size{Colors.END}")
                sys.exit(2)
        elif opt == '--batch-delay':
            try:
                batch_delay = float(arg)
                print(f"{Colors.CYAN}ℹ Batch delay: {batch_delay}s{Colors.END}")
            except:
                print(f"{Colors.RED}✗ Error: Invalid batch delay{Colors.END}")
                sys.exit(2)
        elif opt in ('--payload', '-p'):
            try:
                with open(arg, 'r') as f:
                    payloads = [line.strip() for line in f if line.strip()]
                print(f"{Colors.CYAN}ℹ Loaded {len(payloads)} payloads from {arg}{Colors.END}")
            except:
                print(f"{Colors.RED}✗ Error: Cannot read payload file{Colors.END}")
                sys.exit(2)
        elif opt in ('--cookie', '-c'):
            try:
                if '=' in arg:
                    key, value = arg.split('=', 1)
                    cookies[key.strip()] = value.strip()
                    print(f"{Colors.CYAN}ℹ Cookie: {key.strip()}={value.strip()}{Colors.END}")
                elif os.path.exists(arg):
                    with open(arg, 'r') as f:
                        for line in f:
                            if '=' in line:
                                key, value = line.strip().split('=', 1)
                                cookies[key.strip()] = value.strip()
                    print(f"{Colors.CYAN}ℹ Loaded {len(cookies)} cookies from {arg}{Colors.END}")
            except:
                print(f"{Colors.RED}✗ Error: Invalid cookie format{Colors.END}")
                sys.exit(2)
        elif opt == '--auto-proxy':
            auto_update_proxy = True
            print(f"{Colors.CYAN}ℹ Auto-proxy update enabled{Colors.END}")
        elif opt == '--proxy-interval':
            try:
                proxy_update_interval = int(arg) * 60  # Convert minutes to seconds
                print(f"{Colors.CYAN}ℹ Proxy update interval: {arg} minutes{Colors.END}")
            except:
                print(f"{Colors.RED}✗ Error: Invalid proxy interval{Colors.END}")
                sys.exit(2)
    
    if not url:
        print(f"{Colors.RED}✗ Error: URL is required!{Colors.END}")
        showUsage()
        sys.exit(2)
    
    parseFiles()

def parseFiles():
    global ips, ua, ref, last_proxy_update
    
    default_ua = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1'
    ]
    default_ref = [
        'https://www.google.com/',
        'https://www.bing.com/',
        'https://www.yahoo.com/',
        'https://duckduckgo.com/',
        'https://www.facebook.com/',
        'https://www.twitter.com/',
        'https://www.instagram.com/',
        'https://www.linkedin.com/'
    ]
    
    ua = default_ua.copy()
    ref = default_ref.copy()
    
    print(f"{Colors.CYAN}📁 Loading Configuration Files{Colors.END}")
    
    # Auto-download proxies if enabled
    if auto_update_proxy:
        downloaded = download_proxies()
        if downloaded:
            ips = downloaded
    
    # Load proxies from file if not downloaded or auto-update disabled
    if use_proxy and not ips:
        try:
            if os.path.exists(proxy_file) and os.stat(proxy_file).st_size > 0:
                with open(proxy_file, 'r') as f:
                    content = [row.rstrip() for row in f if row.rstrip() and not row.startswith('#')]
                    if content:
                        ips = content
                        print(f"{Colors.GREEN}  ✓ Loaded {len(ips)} proxies from {proxy_file}{Colors.END}")
                    else:
                        print(f"{Colors.YELLOW}  ⚠ No valid proxies found in {proxy_file}{Colors.END}")
                        ips = []
            else:
                print(f"{Colors.YELLOW}  ⚠ File {proxy_file} not found{Colors.END}")
                if auto_update_proxy:
                    # Try to download if file not exists
                    downloaded = download_proxies()
                    if downloaded:
                        ips = downloaded
                else:
                    with open(proxy_file, 'w') as f:
                        f.write('# Add proxies here (format: ip:port)\n')
                        f.write('# Example: 192.168.1.1:8080\n')
                        f.write('# Use --auto-proxy to automatically download proxies\n')
                    print(f"{Colors.GREEN}  ✓ Created {proxy_file}{Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}  ✗ Error reading {proxy_file}: {e}{Colors.END}")
            ips = []
    elif not use_proxy:
        ips = []
        print(f"{Colors.DIM}  ℹ Proxy disabled by --no-proxy flag{Colors.END}")
    
    # Baca user-agents
    try:
        if os.path.exists(ua_file) and os.stat(ua_file).st_size > 0:
            with open(ua_file, 'r') as f:
                content = [row.rstrip() for row in f if row.rstrip()]
                if content:
                    ua = content
                    print(f"{Colors.GREEN}  ✓ Loaded {len(ua)} user-agents from {ua_file}{Colors.END}")
                else:
                    print(f"{Colors.YELLOW}  ⚠ File {ua_file} empty, using default{Colors.END}")
        else:
            print(f"{Colors.YELLOW}  ⚠ File {ua_file} not found, creating default{Colors.END}")
            with open(ua_file, 'w') as f:
                f.write('\n'.join(default_ua))
            print(f"{Colors.GREEN}  ✓ Created {ua_file}{Colors.END}")
    except Exception as e:
        print(f"{Colors.RED}  ✗ Error reading {ua_file}: {e}{Colors.END}")
    
    # Baca referers
    try:
        if os.path.exists(ref_file) and os.stat(ref_file).st_size > 0:
            with open(ref_file, 'r') as f:
                content = [row.rstrip() for row in f if row.rstrip()]
                if content:
                    ref = content
                    print(f"{Colors.GREEN}  ✓ Loaded {len(ref)} referers from {ref_file}{Colors.END}")
                else:
                    print(f"{Colors.YELLOW}  ⚠ File {ref_file} empty, using default{Colors.END}")
        else:
            print(f"{Colors.YELLOW}  ⚠ File {ref_file} not found, creating default{Colors.END}")
            with open(ref_file, 'w') as f:
                f.write('\n'.join(default_ref))
            print(f"{Colors.GREEN}  ✓ Created {ref_file}{Colors.END}")
    except Exception as e:
        print(f"{Colors.RED}  ✗ Error reading {ref_file}: {e}{Colors.END}")
    
    if use_proxy:
        proxy_status = f"{len(ips)} proxies" if ips else "No proxies (direct connection)"
    else:
        proxy_status = "Direct connection (--no-proxy)"
    
    print(f"{Colors.CYAN}📊 Summary: {proxy_status}, {len(ua)} user-agents, {len(ref)} referers{Colors.END}")
    if payloads:
        print(f"{Colors.CYAN}📊 Payloads: {len(payloads)} loaded{Colors.END}")
    if cookies:
        print(f"{Colors.CYAN}📊 Cookies: {len(cookies)} loaded{Colors.END}")
    if auto_update_proxy:
        print(f"{Colors.CYAN}📊 Auto-Proxy: Enabled (updates every {proxy_update_interval//60} minutes){Colors.END}")
    print()
    testConnection()

def testConnection():
    print(f"{Colors.CYAN}🔗 Testing Connection{Colors.END}")
    print(f"{Colors.WHITE}Target URL: {Colors.GREEN}{url}{Colors.END}")
    print(f"{Colors.WHITE}Method: {Colors.GREEN}{method}{Colors.END}")
    if custom_headers:
        print(f"{Colors.WHITE}Custom Headers: {Colors.GREEN}{len(custom_headers)}{Colors.END}")
    if cookies:
        print(f"{Colors.WHITE}Cookies: {Colors.GREEN}{len(cookies)}{Colors.END}")
    
    try:
        r = requests.request(method, url, timeout=timeout)
        print(f"{Colors.WHITE}Status: {Colors.GREEN}{r.status_code} {Colors.WHITE}| Size: {Colors.GREEN}{len(r.content)} bytes{Colors.END}")
        print(f"{Colors.GREEN}✅ Connection successful!{Colors.END}\n")
        startTesting()
    except requests.exceptions.Timeout:
        print(f"{Colors.RED}❌ Connection timeout after {timeout}s{Colors.END}")
        sys.exit(1)
    except requests.exceptions.ConnectionError:
        print(f"{Colors.RED}❌ Connection error: Unable to reach {url}{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"{Colors.RED}❌ Connection failed: {e}{Colors.END}")
        sys.exit(1)

def update_proxies_if_needed():
    """Update proxies if auto-update is enabled and interval has passed"""
    global ips, last_proxy_update
    if auto_update_proxy and (time.time() - last_proxy_update > proxy_update_interval):
        print(f"\n{Colors.CYAN}🔄 Auto-updating proxies...{Colors.END}")
        downloaded = download_proxies()
        if downloaded:
            ips = downloaded
            print(f"{Colors.GREEN}✅ Proxies updated! Total: {len(ips)}{Colors.END}\n")

def request_testing(index):
    global total_requests, success_requests, failed_requests, status_codes
    
    proxy_list = ips.copy() if ips and use_proxy else []
    proxy_index = index % len(proxy_list) if proxy_list else 0
    retry_counter = 0
    
    while not ex.is_set():
        try:
            # Update proxies if needed
            update_proxies_if_needed()
            
            # Calculate delay
            if use_jitter:
                current_delay = random.uniform(jitter_min, jitter_max)
            elif use_random_delay:
                current_delay = random.uniform(delay_min, delay_max)
            else:
                current_delay = request_delay
            
            # Batch mode
            if use_sequential:
                batch_counter = 0
                while batch_counter < batch_size:
                    if ex.is_set():
                        break
                    batch_counter += 1
                time.sleep(batch_delay)
            
            # Pilih proxy
            proxy = None
            proxy_str = 'Direct'
            
            if proxy_list and use_proxy:
                proxy = {
                    'http': f'http://{proxy_list[proxy_index]}',
                    'https': f'http://{proxy_list[proxy_index]}'
                }
                proxy_str = proxy_list[proxy_index]
                proxy_index = (proxy_index + 1) % len(proxy_list)
            
            # Headers
            headers = {
                'User-Agent': random.choice(ua),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate',
                'Referer': random.choice(ref),
                'Cache-Control': 'no-cache'
            }
            
            if use_keep_alive:
                headers['Connection'] = 'keep-alive'
            else:
                headers['Connection'] = 'close'
            
            if custom_headers:
                headers.update(custom_headers)
            
            # Cookies
            if cookies:
                headers['Cookie'] = '; '.join([f'{k}={v}' for k, v in cookies.items()])
            
            # SSL settings
            ssl_verify = verify_ssl
            if not ssl_verify:
                requests.packages.urllib3.disable_warnings()
            
            # Kirim request dengan retry
            for attempt in range(retry_count + 1):
                try:
                    start_time_req = time.time()
                    r = requests.request(
                        method, url,
                        headers=headers,
                        proxies=proxy,
                        timeout=(timeout_connect, timeout_read),
                        verify=ssl_verify,
                        allow_redirects=follow_redirects,
                        max_redirects=max_redirects
                    )
                    response_time = time.time() - start_time_req
                    break
                except:
                    if attempt < retry_count:
                        time.sleep(retry_delay)
                        continue
                    raise
            
            # Update stats
            with lock:
                total_requests += 1
                status_codes[r.status_code] += 1
                if r.status_code == 200:
                    success_requests += 1
                    status_color = Colors.GREEN
                elif 200 <= r.status_code < 300:
                    success_requests += 1
                    status_color = Colors.GREEN
                elif 300 <= r.status_code < 400:
                    success_requests += 1
                    status_color = Colors.BLUE
                else:
                    failed_requests += 1
                    status_color = Colors.YELLOW
                
                if save_log:
                    log_entry = {
                        'timestamp': datetime.datetime.now().isoformat(),
                        'thread': index,
                        'method': method,
                        'url': url,
                        'status': r.status_code,
                        'response_time': round(response_time, 3),
                        'proxy': proxy_str,
                        'size': len(r.content),
                        'headers': dict(r.headers)
                    }
                    log_data.append(log_entry)
            
            # Log hasil
            delay_info = ""
            if use_jitter:
                delay_info = f" | jitter: {current_delay:.2f}s"
            elif use_random_delay:
                delay_info = f" | rand: {current_delay:.2f}s"
            
            retry_info = f" | retry: {retry_counter}" if retry_counter > 0 else ""
            print(f"{status_color}[{index:>2}] {r.status_code:>3} | {response_time:>5.2f}s | {proxy_str}{delay_info}{retry_info}{Colors.END}")
            
            if current_delay > 0:
                time.sleep(current_delay)
            retry_counter = 0
            
        except requests.exceptions.ProxyError:
            print(f"{Colors.RED}[{index:>2}] PROXY ERROR | {proxy_list[proxy_index-1] if proxy_list else 'None'}{Colors.END}")
            time.sleep(0.5)
        except requests.exceptions.Timeout:
            print(f"{Colors.YELLOW}[{index:>2}] TIMEOUT | {timeout}s{Colors.END}")
            with lock:
                total_requests += 1
                failed_requests += 1
                status_codes['TIMEOUT'] += 1
            time.sleep(1)
        except requests.exceptions.ConnectionError:
            print(f"{Colors.YELLOW}[{index:>2}] CONNECTION ERROR{Colors.END}")
            with lock:
                total_requests += 1
                failed_requests += 1
                status_codes['CONNECTION_ERROR'] += 1
            time.sleep(1)
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
    
    proxy_status = f"{len(ips)} proxies" if ips and use_proxy else "Direct connection"
    print(f"{Colors.GREEN}🚀 Starting FLASHFLOOD Attack{Colors.END}")
    print(f"{Colors.WHITE}Threads: {Colors.GREEN}{max_threads}{Colors.WHITE} | Timeout: {Colors.GREEN}{timeout}s{Colors.WHITE} | Delay: {Colors.GREEN}{request_delay}s{Colors.END}")
    if use_jitter:
        print(f"{Colors.WHITE}Jitter: {Colors.GREEN}{jitter_min:.2f}s - {jitter_max:.2f}s{Colors.END}")
    if use_random_delay:
        print(f"{Colors.WHITE}Random Delay: {Colors.GREEN}{delay_min:.2f}s - {delay_max:.2f}s{Colors.END}")
    if use_sequential:
        print(f"{Colors.WHITE}Sequential: {Colors.GREEN}Enabled (batch: {batch_size}, delay: {batch_delay}s){Colors.END}")
    print(f"{Colors.WHITE}Method: {Colors.GREEN}{method}{Colors.END}")
    print(f"{Colors.WHITE}Proxy: {Colors.GREEN}{proxy_status}{Colors.END}")
    if custom_headers:
        print(f"{Colors.WHITE}Custom Headers: {Colors.GREEN}{len(custom_headers)}{Colors.END}")
    if cookies:
        print(f"{Colors.WHITE}Cookies: {Colors.GREEN}{len(cookies)}{Colors.END}")
    if payloads:
        print(f"{Colors.WHITE}Payloads: {Colors.GREEN}{len(payloads)}{Colors.END}")
    if save_log:
        print(f"{Colors.WHITE}Log: {Colors.GREEN}Enabled ({log_file}){Colors.END}")
    if not verify_ssl:
        print(f"{Colors.YELLOW}⚠️  SSL Verification: Disabled{Colors.END}")
    if not follow_redirects:
        print(f"{Colors.YELLOW}⚠️  Redirects: Disabled{Colors.END}")
    if retry_count > 0:
        print(f"{Colors.WHITE}Retry: {Colors.GREEN}{retry_count} times, delay: {retry_delay}s{Colors.END}")
    if auto_update_proxy:
        print(f"{Colors.WHITE}Auto-Proxy: {Colors.GREEN}Enabled (every {proxy_update_interval//60} min){Colors.END}")
    print(f"{Colors.YELLOW}Press Ctrl+C to stop{Colors.END}\n")
    
    threads = []
    thread_count = max_threads
    
    print(f"{Colors.DIM}─── Request Log ───{Colors.END}")
    
    for i in range(thread_count):
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
                    print(f"\n{Colors.CYAN}📊 REAL-TIME STATISTICS{Colors.END}")
                    print(f"{Colors.WHITE}Elapsed Time : {Colors.GREEN}{elapsed:.1f}s{Colors.END}")
                    print(f"{Colors.WHITE}Requests     : {Colors.GREEN}{total_requests:,}{Colors.END}")
                    print(f"{Colors.WHITE}Success      : {Colors.GREEN}{success_requests:,}{Colors.END}")
                    print(f"{Colors.WHITE}Failed       : {Colors.RED}{failed_requests:,}{Colors.END}")
                    if total_requests > 0:
                        success_rate = (success_requests / total_requests) * 100
                        print(f"{Colors.WHITE}Success Rate : {Colors.GREEN}{success_rate:.2f}%{Colors.END}")
                        req_per_sec = total_requests / elapsed if elapsed > 0 else 0
                        print(f"{Colors.WHITE}Requests/s   : {Colors.GREEN}{req_per_sec:.2f}{Colors.END}")
                    print(f"{Colors.WHITE}Active Thrd  : {Colors.YELLOW}{len([t for t in threads if t.is_alive()])}{Colors.END}")
                    if status_codes:
                        print(f"{Colors.WHITE}Status Codes : {Colors.END}")
                        for code, count in sorted(status_codes.items()):
                            color = Colors.GREEN if code == 200 else Colors.YELLOW if code == 404 else Colors.WHITE
                            print(f"  {color}{code}: {count}{Colors.END}")
                    print()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}🛑 Stopping FLASHFLOOD...{Colors.END}")
        ex.set()
        print(f"{Colors.CYAN}⏳ Waiting for threads to finish...{Colors.END}")
        for t in threads:
            t.join(timeout=2)
        
        if save_log and log_data:
            try:
                with open(log_file, 'w') as f:
                    json.dump(log_data, f, indent=2)
                print(f"{Colors.GREEN}✅ Log saved to {log_file} ({len(log_data)} entries){Colors.END}")
            except Exception as e:
                print(f"{Colors.RED}❌ Error saving log: {e}{Colors.END}")
        
        elapsed = time.time() - start_time
        print(f"\n{Colors.CYAN}📊 FINAL STATISTICS{Colors.END}")
        print(f"{Colors.WHITE}Total Time    : {Colors.GREEN}{elapsed:.1f}s{Colors.END}")
        print(f"{Colors.WHITE}Total Requests: {Colors.GREEN}{total_requests:,}{Colors.END}")
        print(f"{Colors.WHITE}Successful    : {Colors.GREEN}{success_requests:,}{Colors.END}")
        print(f"{Colors.WHITE}Failed        : {Colors.RED}{failed_requests:,}{Colors.END}")
        if total_requests > 0:
            success_rate = (success_requests / total_requests) * 100
            print(f"{Colors.WHITE}Success Rate  : {Colors.GREEN}{success_rate:.2f}%{Colors.END}")
            req_per_sec = total_requests / elapsed if elapsed > 0 else 0
            print(f"{Colors.WHITE}Average RPS   : {Colors.GREEN}{req_per_sec:.2f}{Colors.END}")
        if status_codes:
            print(f"{Colors.WHITE}Status Codes Distribution:{Colors.END}")
            for code, count in sorted(status_codes.items()):
                color = Colors.GREEN if code == 200 else Colors.YELLOW if code == 404 else Colors.WHITE
                print(f"  {color}{code}: {count}{Colors.END}")
        print(f"{Colors.GREEN}✅ FLASHFLOOD Stopped Successfully!{Colors.END}\n")

def showUsage():
    print(f"""
{Colors.CYAN}CPA FLASHFLOOD v{__version__} - Ultimate HTTP Load Testing Tool{Colors.END}

{Colors.GREEN}USAGE:{Colors.END}
    python flash.py {Colors.CYAN}--url{Colors.END} <URL> {Colors.DIM}[OPTIONS]{Colors.END}

{Colors.GREEN}BASIC OPTIONS:{Colors.END}
    {Colors.CYAN}-v, --url{Colors.END} <URL>       Target URL {Colors.RED}(required){Colors.END}
    {Colors.CYAN}-t, --timeout{Colors.END} <SEC>   Timeout (default: 10)
    {Colors.CYAN}--threads{Colors.END} <NUM>       Threads (default: 20, max: 500)
    {Colors.CYAN}--delay{Colors.END} <SEC>         Delay between requests (default: 1.0)
    {Colors.CYAN}--no-proxy{Colors.END}            Disable proxy
    {Colors.CYAN}-h, --help{Colors.END}            Show this help

{Colors.GREEN}ADVANCED OPTIONS:{Colors.END}
    {Colors.CYAN}-X, --method{Colors.END} <M>      HTTP method (GET, POST, PUT, DELETE, etc.)
    {Colors.CYAN}-H, --header{Colors.END} <H>      Custom header (format: "Key: Value")
    {Colors.CYAN}-j, --jitter{Colors.END} <V>      Random delay (format: "min,max" or single)
    {Colors.CYAN}-l, --log{Colors.END}             Save results to log file
    {Colors.CYAN}-p, --payload{Colors.END} <FILE>  Load payloads from file
    {Colors.CYAN}-c, --cookie{Colors.END} <V>      Cookie (format: "key=value" or file)

{Colors.GREEN}PROXY OPTIONS:{Colors.END}
    {Colors.CYAN}--auto-proxy{Colors.END}          Automatically download proxies from online sources
    {Colors.CYAN}--proxy-interval{Colors.END} <M>  Proxy update interval in minutes (default: 60)

{Colors.GREEN}NETWORK OPTIONS:{Colors.END}
    {Colors.CYAN}--ssl{Colors.END}                  Enable SSL/TLS
    {Colors.CYAN}--no-verify{Colors.END}           Disable SSL verification
    {Colors.CYAN}--no-redirect{Colors.END}         Disable redirects
    {Colors.CYAN}--keep-alive{Colors.END}          Enable Keep-Alive
    {Colors.CYAN}--connect-timeout{Colors.END} <S> Connect timeout
    {Colors.CYAN}--read-timeout{Colors.END} <S>    Read timeout

{Colors.GREEN}RETRY OPTIONS:{Colors.END}
    {Colors.CYAN}--retry{Colors.END} <NUM>         Number of retries (default: 0)
    {Colors.CYAN}--retry-delay{Colors.END} <SEC>   Retry delay (default: 1.0)

{Colors.GREEN}SCHEDULING OPTIONS:{Colors.END}
    {Colors.CYAN}--random-delay{Colors.END} <V>    Random delay (min,max)
    {Colors.CYAN}--sequential{Colors.END}          Sequential mode
    {Colors.CYAN}--batch{Colors.END} <NUM>         Batch size (default: 10)
    {Colors.CYAN}--batch-delay{Colors.END} <SEC>   Batch delay (default: 0.5)

{Colors.GREEN}EXAMPLES:{Colors.END}
    # Auto-download proxies and test
    python flash.py --url https://httpbin.org/get --auto-proxy --threads 30 --delay 0.05
    
    # Auto-proxy with custom update interval (30 minutes)
    python flash.py --url https://httpbin.org/get --auto-proxy --proxy-interval 30 --threads 50
    
    # Full featured with auto-proxy
    python flash.py --url https://httpbin.org/get --auto-proxy --jitter 0.3,0.8 --threads 50 --delay 0.05 --log
    
    # Auto-proxy with POST and headers
    python flash.py --url https://httpbin.org/post --method POST -H "Content-Type: application/json" --auto-proxy --threads 30
{Colors.END}""")

if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}🛑 Interrupted{Colors.END}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}❌ Error: {e}{Colors.END}")
        sys.exit(1)
