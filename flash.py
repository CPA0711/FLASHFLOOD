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
    END = '\033[0m'

VERSION = (0, 1, 5)
__version__ = '%d.%d.%d' % VERSION[0:3]

if sys.version_info[0:2] < (3, 5):
    raise RuntimeError('Python 3.5 or higher is required!')

# Banner ASCII
BANNER = f"""
{Colors.CYAN}╔══════════════════════════════════════════════════════════════════╗
║                                                                          ║
║     ███████╗██╗      █████╗ ███████╗██╗  ██╗███████╗██╗      ██████╗    ║
║     ██╔════╝██║     ██╔══██╗██╔════╝██║  ██║██╔════╝██║     ██╔═══██╗   ║
║     █████╗  ██║     ███████║███████╗███████║█████╗  ██║     ██║   ██║   ║
║     ██╔══╝  ██║     ██╔══██║╚════██║██╔══██║██╔══╝  ██║     ██║   ██║   ║
║     ██║     ███████╗██║  ██║███████║██║  ██║██║     ███████╗╚██████╔╝   ║
║     ╚═╝     ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝     ╚══════╝ ╚═════╝    ║
║                                                                          ║
║     ██████╗ ██████╗  █████╗                                             ║
║     ██╔══██╗██╔══██╗██╔══██╗                                            ║
║     ██████╔╝██████╔╝███████║                                            ║
║     ██╔═══╝ ██╔══██╗██╔══██║                                            ║
║     ██║     ██║  ██║██║  ██║                                            ║
║     ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝                                            ║
║                                                                          ║
║     {Colors.GREEN}██╗  ██╗██████╗  ██████╗ ██╗   ██╗██████╗  █████╗ ██████╗ {Colors.CYAN}║
║     {Colors.GREEN}██║  ██║██╔══██╗██╔═══██╗╚██╗ ██╔╝██╔══██╗██╔══██╗██╔══██╗{Colors.CYAN}║
║     {Colors.GREEN}███████║██████╔╝██║   ██║ ╚████╔╝ ██████╔╝███████║██████╔╝{Colors.CYAN}║
║     {Colors.GREEN}██╔══██║██╔══██╗██║   ██║  ╚██╔╝  ██╔══██╗██╔══██║██╔══██╗{Colors.CYAN}║
║     {Colors.GREEN}██║  ██║██████╔╝╚██████╔╝   ██║   ██████╔╝██║  ██║██║  ██║{Colors.CYAN}║
║     {Colors.GREEN}╚═╝  ╚═╝╚═════╝  ╚═════╝    ╚═╝   ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝{Colors.CYAN}║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════╝{Colors.END}
"""

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
auth = False
auth_login = ''
auth_pass = ''
max_threads = 20
request_delay = 1
total_requests = 0
success_requests = 0
failed_requests = 0
lock = threading.Lock()

def main(argv):
    # Tampilkan banner
    print(BANNER)
    print(f"{Colors.CYAN}╔══════════════════════════════════════════════════════════════════╗{Colors.END}")
    print(f"{Colors.CYAN}║{Colors.WHITE}  CPA FLASHFLOOD v{__version__} - HTTP Request Tester{Colors.CYAN}                    ║{Colors.END}")
    print(f"{Colors.CYAN}╚══════════════════════════════════════════════════════════════════╝{Colors.END}\n")
    
    try:
        opts, args = getopt.getopt(argv, 'hv:t:', ['help', 'url=', 'timeout=', 'threads=', 'delay='])
    except getopt.GetoptError as err:
        print(f"{Colors.RED}Error: {err}{Colors.END}")
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
                print(f"{Colors.RED}Error: URL cannot be empty!{Colors.END}")
                sys.exit(2)
        elif opt in ('-t', '--timeout'):
            try:
                arg = int(arg)
                if arg >= 1:
                    global timeout
                    timeout = arg
                else:
                    print(f"{Colors.RED}Error: Timeout must be >= 1{Colors.END}")
                    sys.exit(2)
            except ValueError:
                print(f"{Colors.RED}Error: Timeout must be integer{Colors.END}")
                sys.exit(2)
        elif opt == '--threads':
            try:
                arg = int(arg)
                if arg >= 1 and arg <= 100:
                    global max_threads
                    max_threads = arg
                else:
                    print(f"{Colors.RED}Error: Threads must be between 1-100{Colors.END}")
                    sys.exit(2)
            except ValueError:
                print(f"{Colors.RED}Error: Threads must be integer{Colors.END}")
                sys.exit(2)
        elif opt == '--delay':
            try:
                arg = float(arg)
                if arg >= 0.1:
                    global request_delay
                    request_delay = arg
                else:
                    print(f"{Colors.RED}Error: Delay must be >= 0.1{Colors.END}")
                    sys.exit(2)
            except ValueError:
                print(f"{Colors.RED}Error: Delay must be number{Colors.END}")
                sys.exit(2)
    
    if not url:
        print(f"{Colors.RED}Error: URL is required!{Colors.END}")
        showUsage()
        sys.exit(2)
    
    parseFiles()

def parseFiles():
    """Membaca file konfigurasi dengan error handling"""
    global ips, ua, ref
    
    # Default values
    default_ips = ['127.0.0.1:8080']
    default_ua = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    ]
    default_ref = [
        'https://www.google.com/',
        'https://www.bing.com/',
        'https://www.yahoo.com/'
    ]
    
    ips = default_ips.copy()
    ua = default_ua.copy()
    ref = default_ref.copy()
    
    # Baca proxy
    try:
        if os.path.exists(proxy_file) and os.stat(proxy_file).st_size > 0:
            with open(proxy_file, 'r') as f:
                content = [row.rstrip() for row in f if row.rstrip()]
                if content:
                    ips = content
                    print(f"{Colors.GREEN}✓ Loaded {len(ips)} proxies from {proxy_file}{Colors.END}")
                else:
                    print(f"{Colors.YELLOW}⚠ File {proxy_file} empty, using default{Colors.END}")
        else:
            print(f"{Colors.YELLOW}⚠ File {proxy_file} not found, creating default{Colors.END}")
            with open(proxy_file, 'w') as f:
                f.write('\n'.join(default_ips))
            print(f"{Colors.GREEN}✓ Created {proxy_file} with default proxies{Colors.END}")
    except Exception as e:
        print(f"{Colors.RED}✗ Error reading {proxy_file}: {e}{Colors.END}")
    
    # Baca user-agents
    try:
        if os.path.exists(ua_file) and os.stat(ua_file).st_size > 0:
            with open(ua_file, 'r') as f:
                content = [row.rstrip() for row in f if row.rstrip()]
                if content:
                    ua = content
                    print(f"{Colors.GREEN}✓ Loaded {len(ua)} user-agents from {ua_file}{Colors.END}")
                else:
                    print(f"{Colors.YELLOW}⚠ File {ua_file} empty, using default{Colors.END}")
        else:
            print(f"{Colors.YELLOW}⚠ File {ua_file} not found, creating default{Colors.END}")
            with open(ua_file, 'w') as f:
                f.write('\n'.join(default_ua))
            print(f"{Colors.GREEN}✓ Created {ua_file} with default user-agents{Colors.END}")
    except Exception as e:
        print(f"{Colors.RED}✗ Error reading {ua_file}: {e}{Colors.END}")
    
    # Baca referers
    try:
        if os.path.exists(ref_file) and os.stat(ref_file).st_size > 0:
            with open(ref_file, 'r') as f:
                content = [row.rstrip() for row in f if row.rstrip()]
                if content:
                    ref = content
                    print(f"{Colors.GREEN}✓ Loaded {len(ref)} referers from {ref_file}{Colors.END}")
                else:
                    print(f"{Colors.YELLOW}⚠ File {ref_file} empty, using default{Colors.END}")
        else:
            print(f"{Colors.YELLOW}⚠ File {ref_file} not found, creating default{Colors.END}")
            with open(ref_file, 'w') as f:
                f.write('\n'.join(default_ref))
            print(f"{Colors.GREEN}✓ Created {ref_file} with default referers{Colors.END}")
    except Exception as e:
        print(f"{Colors.RED}✗ Error reading {ref_file}: {e}{Colors.END}")
    
    print(f"\n{Colors.CYAN}📊 Summary: {len(ips)} proxies, {len(ua)} user-agents, {len(ref)} referers{Colors.END}")
    testConnection()

def testConnection():
    """Testing koneksi ke URL"""
    print(f"\n{Colors.CYAN}🔗 Testing connection to: {Colors.WHITE}{url}{Colors.END}")
    try:
        r = requests.get(url, timeout=timeout)
        print(f"{Colors.GREEN}✅ Connection successful! Status: {r.status_code}{Colors.END}")
        print(f"{Colors.CYAN}📝 Response size: {len(r.content)} bytes{Colors.END}")
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
    """Testing request dengan rate limiting"""
    global total_requests, success_requests, failed_requests
    
    proxy_list = ips.copy()
    proxy_index = index % len(proxy_list) if proxy_list else 0
    local_total = 0
    local_success = 0
    local_failed = 0
    
    while not ex.is_set():
        try:
            # Pilih proxy
            proxy = None
            if proxy_list:
                proxy = {
                    'http': f'http://{proxy_list[proxy_index]}',
                    'https': f'http://{proxy_list[proxy_index]}'
                }
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
            start_time = time.time()
            if proxy:
                r = requests.get(url, headers=headers, proxies=proxy, timeout=timeout)
            else:
                r = requests.get(url, headers=headers, timeout=timeout)
            
            response_time = time.time() - start_time
            local_total += 1
            
            # Update global stats
            with lock:
                total_requests += 1
                if r.status_code == 200:
                    success_requests += 1
                    local_success += 1
                    status_color = Colors.GREEN
                else:
                    failed_requests += 1
                    local_failed += 1
                    status_color = Colors.YELLOW
            
            # Log
            if r.status_code == 200:
                print(f"{Colors.GREEN}✅ [{index}] Status: {r.status_code} | Time: {response_time:.2f}s | Proxy: {proxy_list[proxy_index-1] if proxy_list else 'None'}{Colors.END}")
            else:
                print(f"{Colors.YELLOW}⚠ [{index}] Status: {r.status_code} | Time: {response_time:.2f}s | Proxy: {proxy_list[proxy_index-1] if proxy_list else 'None'}{Colors.END}")
            
            time.sleep(request_delay)
            
        except requests.exceptions.ProxyError:
            print(f"{Colors.RED}❌ [{index}] Proxy error, skipping...{Colors.END}")
            time.sleep(0.5)
        except requests.exceptions.Timeout:
            print(f"{Colors.YELLOW}⚠ [{index}] Timeout after {timeout}s{Colors.END}")
            with lock:
                total_requests += 1
                failed_requests += 1
            time.sleep(1)
        except requests.exceptions.ConnectionError:
            print(f"{Colors.YELLOW}⚠ [{index}] Connection error{Colors.END}")
            with lock:
                total_requests += 1
                failed_requests += 1
            time.sleep(1)
        except Exception as e:
            print(f"{Colors.RED}❌ [{index}] Error: {e}{Colors.END}")
            time.sleep(1)

def startTesting():
    """Start testing dengan thread management"""
    print(f"\n{Colors.CYAN}╔══════════════════════════════════════════════════════════════════╗{Colors.END}")
    print(f"{Colors.CYAN}║{Colors.GREEN}  🚀 Starting FLASHFLOOD with {max_threads} threads...{Colors.CYAN}                      ║{Colors.END}")
    print(f"{Colors.CYAN}║{Colors.GREEN}  ⏱ Timeout: {timeout}s | Delay: {request_delay}s{Colors.CYAN}                             ║{Colors.END}")
    print(f"{Colors.CYAN}║{Colors.YELLOW}  Press Ctrl+C to stop{Colors.CYAN}                                                     ║{Colors.END}")
    print(f"{Colors.CYAN}╚══════════════════════════════════════════════════════════════════╝{Colors.END}\n")
    
    threads = []
    thread_count = min(max_threads, max(1, len(ips) if ips else 1))
    
    for i in range(thread_count):
        t = threading.Thread(target=request_testing, args=(i,))
        t.daemon = True
        t.start()
        threads.append(t)
        print(f"{Colors.CYAN}🔄 Thread {i+1} started{Colors.END}")
    
    print(f"\n{Colors.GREEN}✅ All {len(threads)} threads running...{Colors.END}\n")
    
    try:
        while True:
            time.sleep(1)
            # Show stats every 5 seconds
            if int(time.time()) % 5 == 0:
                with lock:
                    print(f"\n{Colors.CYAN}╔══════════════════════════════════════════════════════════════════╗{Colors.END}")
                    print(f"{Colors.CYAN}║{Colors.WHITE}  📊 STATISTICS{Colors.CYAN}                                                     ║{Colors.END}")
                    print(f"{Colors.CYAN}╠══════════════════════════════════════════════════════════════════╣{Colors.END}")
                    print(f"{Colors.CYAN}║{Colors.WHITE}  Total Requests : {Colors.GREEN}{total_requests:>10}{Colors.CYAN}                                    ║{Colors.END}")
                    print(f"{Colors.CYAN}║{Colors.WHITE}  Successful     : {Colors.GREEN}{success_requests:>10}{Colors.CYAN}                                    ║{Colors.END}")
                    print(f"{Colors.CYAN}║{Colors.WHITE}  Failed         : {Colors.RED}{failed_requests:>10}{Colors.CYAN}                                    ║{Colors.END}")
                    if total_requests > 0:
                        success_rate = (success_requests / total_requests) * 100
                        print(f"{Colors.CYAN}║{Colors.WHITE}  Success Rate   : {Colors.GREEN}{success_rate:>9.2f}%{Colors.CYAN}                                    ║{Colors.END}")
                    print(f"{Colors.CYAN}║{Colors.WHITE}  Active Threads : {Colors.YELLOW}{len([t for t in threads if t.is_alive()]):>10}{Colors.CYAN}                                    ║{Colors.END}")
                    print(f"{Colors.CYAN}╚══════════════════════════════════════════════════════════════════╝{Colors.END}\n")
    except KeyboardInterrupt:
        print(f"\n\n{Colors.RED}╔══════════════════════════════════════════════════════════════════╗{Colors.END}")
        print(f"{Colors.RED}║{Colors.YELLOW}  🛑 Stopping FLASHFLOOD...{Colors.RED}                                          ║{Colors.END}")
        print(f"{Colors.RED}╚══════════════════════════════════════════════════════════════════╝{Colors.END}")
        ex.set()
        print(f"{Colors.CYAN}⏳ Waiting for threads to finish...{Colors.END}")
        for t in threads:
            t.join(timeout=2)
        
        # Final stats
        print(f"\n{Colors.CYAN}╔══════════════════════════════════════════════════════════════════╗{Colors.END}")
        print(f"{Colors.CYAN}║{Colors.GREEN}  ✅ FLASHFLOOD Stopped Successfully!{Colors.CYAN}                                 ║{Colors.END}")
        print(f"{Colors.CYAN}╠══════════════════════════════════════════════════════════════════╣{Colors.END}")
        print(f"{Colors.CYAN}║{Colors.WHITE}  Final Statistics:{Colors.CYAN}                                                 ║{Colors.END}")
        print(f"{Colors.CYAN}║{Colors.WHITE}  Total Requests : {Colors.GREEN}{total_requests:>10}{Colors.CYAN}                                    ║{Colors.END}")
        print(f"{Colors.CYAN}║{Colors.WHITE}  Successful     : {Colors.GREEN}{success_requests:>10}{Colors.CYAN}                                    ║{Colors.END}")
        print(f"{Colors.CYAN}║{Colors.WHITE}  Failed         : {Colors.RED}{failed_requests:>10}{Colors.CYAN}                                    ║{Colors.END}")
        if total_requests > 0:
            success_rate = (success_requests / total_requests) * 100
            print(f"{Colors.CYAN}║{Colors.WHITE}  Success Rate   : {Colors.GREEN}{success_rate:>9.2f}%{Colors.CYAN}                                    ║{Colors.END}")
        print(f"{Colors.CYAN}╚══════════════════════════════════════════════════════════════════╝{Colors.END}\n")

def showUsage():
    print(f"""
{Colors.CYAN}╔══════════════════════════════════════════════════════════════════╗
║                     CPA FLASHFLOOD v{__version__}                      ║
║                   HTTP Request Tester / Load Tester                      ║
╚══════════════════════════════════════════════════════════════════╝{Colors.END}

{Colors.GREEN}Usage:{Colors.END} python script.py [OPTIONS]

{Colors.GREEN}Options:{Colors.END}
    {Colors.CYAN}-v, --url <URL>{Colors.END}         Target URL to test (required)
    {Colors.CYAN}-t, --timeout <SEC>{Colors.END}     Timeout in seconds (default: 10)
    {Colors.CYAN}--threads <NUM>{Colors.END}         Number of threads (default: 20, max: 100)
    {Colors.CYAN}--delay <SEC>{Colors.END}           Delay between requests (default: 1.0)
    {Colors.CYAN}-h, --help{Colors.END}              Show this help message

{Colors.GREEN}Examples:{Colors.END}
    {Colors.WHITE}python script.py --url https://example.com{Colors.END}
    {Colors.WHITE}python script.py --url https://example.com --timeout 5 --threads 10{Colors.END}
    {Colors.WHITE}python script.py --url https://example.com --delay 0.5 --threads 50{Colors.END}

{Colors.GREEN}Files:{Colors.END}
    {Colors.CYAN}proxy.txt{Colors.END}         - List of proxies (format: ip:port)
    {Colors.CYAN}user-agents.txt{Colors.END}   - List of User-Agent strings
    {Colors.CYAN}referers.txt{Colors.END}      - List of Referer URLs

{Colors.YELLOW}Note: Default files will be created automatically if not found.{Colors.END}
{Colors.RED}Warning: Only use on websites you own or have permission to test!{Colors.END}
    """)

if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}🛑 Program interrupted by user{Colors.END}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}❌ Unexpected error: {e}{Colors.END}")
        sys.exit(1)
