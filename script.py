# -*- coding: utf-8 -*-
import sys
import os
import threading
import random
import requests
import time
import getopt
import urllib.parse
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

VERSION = (0, 1, 5)
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
proxy_working = True

def main(argv):
    print(BANNER)
    print(f"{Colors.CYAN}🚀 CPA FLASHFLOOD v{__version__} - HTTP Load Tester{Colors.END}")
    print(f"{Colors.YELLOW}⚠️  For educational and testing purposes only!{Colors.END}\n")
    
    try:
        opts, args = getopt.getopt(argv, 'hv:t:', ['help', 'url=', 'timeout=', 'threads=', 'delay=', 'no-proxy'])
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
                if arg >= 1 and arg <= 100:
                    global max_threads
                    max_threads = arg
                else:
                    print(f"{Colors.RED}✗ Error: Threads must be between 1-100{Colors.END}")
                    sys.exit(2)
            except ValueError:
                print(f"{Colors.RED}✗ Error: Threads must be integer{Colors.END}")
                sys.exit(2)
        elif opt == '--delay':
            try:
                arg = float(arg)
                if arg >= 0.1:
                    global request_delay
                    request_delay = arg
                else:
                    print(f"{Colors.RED}✗ Error: Delay must be >= 0.1{Colors.END}")
                    sys.exit(2)
            except ValueError:
                print(f"{Colors.RED}✗ Error: Delay must be number{Colors.END}")
                sys.exit(2)
        elif opt == '--no-proxy':
            global use_proxy
            use_proxy = False
            print(f"{Colors.YELLOW}⚠️  Proxy disabled, using direct connection{Colors.END}")
    
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
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15'
    ]
    default_ref = [
        'https://www.google.com/',
        'https://www.bing.com/',
        'https://www.yahoo.com/',
        'https://duckduckgo.com/',
        'https://www.facebook.com/'
    ]
    
    ua = default_ua.copy()
    ref = default_ref.copy()
    
    print(f"{Colors.CYAN}📁 Loading Configuration Files{Colors.END}")
    
    # Baca proxy
    try:
        if os.path.exists(proxy_file) and os.stat(proxy_file).st_size > 0:
            with open(proxy_file, 'r') as f:
                content = [row.rstrip() for row in f if row.rstrip() and not row.startswith('#')]
                if content:
                    ips = content
                    print(f"{Colors.GREEN}  ✓ Loaded {len(ips)} proxies from {proxy_file}{Colors.END}")
                else:
                    print(f"{Colors.YELLOW}  ⚠ No valid proxies found in {proxy_file}, using direct connection{Colors.END}")
                    ips = []
        else:
            print(f"{Colors.YELLOW}  ⚠ File {proxy_file} not found, using direct connection{Colors.END}")
            with open(proxy_file, 'w') as f:
                f.write('# Add proxies here (format: ip:port)\n')
                f.write('# Example: 192.168.1.1:8080\n')
            print(f"{Colors.GREEN}  ✓ Created {proxy_file}{Colors.END}")
    except Exception as e:
        print(f"{Colors.RED}  ✗ Error reading {proxy_file}: {e}{Colors.END}")
        ips = []
    
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
    
    proxy_status = f"{len(ips)} proxies" if ips and use_proxy else "Direct connection"
    print(f"{Colors.CYAN}📊 Summary: {proxy_status}, {len(ua)} user-agents, {len(ref)} referers{Colors.END}\n")
    testConnection()

def testConnection():
    print(f"{Colors.CYAN}🔗 Testing Connection{Colors.END}")
    print(f"{Colors.WHITE}Target URL: {Colors.GREEN}{url}{Colors.END}")
    
    try:
        r = requests.get(url, timeout=timeout)
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
    global total_requests, success_requests, failed_requests, proxy_working
    
    proxy_list = ips.copy() if ips and use_proxy else []
    proxy_index = index % len(proxy_list) if proxy_list else 0
    direct_fallback = False
    
    while not ex.is_set():
        try:
            # Pilih proxy
            proxy = None
            proxy_str = 'Direct'
            
            if proxy_list and not direct_fallback:
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
            
            # Kirim request
            start_time_req = time.time()
            if proxy:
                try:
                    r = requests.get(url, headers=headers, proxies=proxy, timeout=timeout)
                except:
                    # Jika proxy gagal, fallback ke direct
                    direct_fallback = True
                    proxy = None
                    proxy_str = 'Direct (fallback)'
                    r = requests.get(url, headers=headers, timeout=timeout)
            else:
                r = requests.get(url, headers=headers, timeout=timeout)
            
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
            
            print(f"{status_color}[{index:>2}] {r.status_code:>3} | {response_time:>5.2f}s | {proxy_str}{Colors.END}")
            
            # Jika proxy berhasil, kembali ke mode proxy
            if direct_fallback and proxy_list:
                direct_fallback = False
                print(f"{Colors.GREEN}[{index:>2}] Switching back to proxy mode{Colors.END}")
            
            time.sleep(request_delay)
            
        except requests.exceptions.ProxyError:
            print(f"{Colors.RED}[{index:>2}] PROXY ERROR | {proxy_list[proxy_index-1] if proxy_list else 'None'}{Colors.END}")
            if proxy_list:
                direct_fallback = True
                print(f"{Colors.YELLOW}[{index:>2}] Falling back to direct connection{Colors.END}")
            time.sleep(0.5)
        except requests.exceptions.Timeout:
            print(f"{Colors.YELLOW}[{index:>2}] TIMEOUT | {timeout}s{Colors.END}")
            with lock:
                total_requests += 1
                failed_requests += 1
            time.sleep(1)
        except requests.exceptions.ConnectionError:
            print(f"{Colors.YELLOW}[{index:>2}] CONNECTION ERROR{Colors.END}")
            with lock:
                total_requests += 1
                failed_requests += 1
            if proxy_list:
                direct_fallback = True
            time.sleep(1)
        except Exception as e:
            print(f"{Colors.RED}[{index:>2}] ERROR: {str(e)[:30]}{Colors.END}")
            time.sleep(1)

def startTesting():
    global start_time
    start_time = time.time()
    
    proxy_status = f"{len(ips)} proxies" if ips and use_proxy else "Direct connection"
    print(f"{Colors.GREEN}🚀 Starting FLASHFLOOD Attack{Colors.END}")
    print(f"{Colors.WHITE}Threads: {Colors.GREEN}{max_threads}{Colors.WHITE} | Timeout: {Colors.GREEN}{timeout}s{Colors.WHITE} | Delay: {Colors.GREEN}{request_delay}s{Colors.END}")
    print(f"{Colors.WHITE}Proxy: {Colors.GREEN}{proxy_status}{Colors.END}")
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
{Colors.CYAN}CPA FLASHFLOOD v{__version__} - HTTP Request Tester & Load Testing Tool{Colors.END}

{Colors.GREEN}USAGE:{Colors.END}
    python script.py {Colors.CYAN}--url{Colors.END} <URL> {Colors.DIM}[OPTIONS]{Colors.END}

{Colors.GREEN}OPTIONS:{Colors.END}
    {Colors.CYAN}-v, --url{Colors.END} <URL>       Target URL {Colors.RED}(required){Colors.END}
    {Colors.CYAN}-t, --timeout{Colors.END} <SEC>   Timeout (default: 10)
    {Colors.CYAN}--threads{Colors.END} <NUM>       Threads (default: 20, max: 100)
    {Colors.CYAN}--delay{Colors.END} <SEC>         Delay between requests (default: 1.0)
    {Colors.CYAN}--no-proxy{Colors.END}            Disable proxy
    {Colors.CYAN}-h, --help{Colors.END}            Help

{Colors.GREEN}EXAMPLES:{Colors.END}
    python script.py --url https://example.com
    python script.py --url https://example.com --no-proxy
    python script.py --url https://example.com --threads 50 --delay 0.5
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
