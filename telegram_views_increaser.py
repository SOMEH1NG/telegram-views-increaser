import os
import sys
import subprocess
import threading
import requests

# Install required packages
subprocess.call(["pip", "install", "requests"])

# Package URL for installation
package_url = "https://github.com/requests/requests/archive/refs/tags/v2.26.0.tar.gz"
subprocess.call(["pip", "install", package_url])

# Semaphore for controlling maximum concurrent threads
max_threads = threading.Semaphore(value=500)

# Load proxies from file
with open('proxies.txt', 'r') as f:
    proxies = [line.strip() for line in f.readlines()]

def fetch_data(channel='google', post='1', proxy=None):
    try:
        r = requests.get(f'https://t.me/{channel}/{post}?embed=1', timeout=20, proxies={'https': proxy})
        cookie = r.headers['set-cookie'].split(';')[0]
        key = r.text.split('data-view="')[1].split('"')[0]
        if 'stel_ssid' in cookie:
            return {'key': key, 'cookie': cookie}
        else:
            return False
    except Exception as e:
        return False

def add_view_to_post(channel='google', post='1', key=None, cookie=None, proxy=None):
    try:
        r = requests.get(f'https://t.me/{channel}/{post}?embed=1&view={key}', timeout=20, headers={
            'x-requested-with': 'XMLHttpRequest',
            'user-agent': 'Mozilla/5.0 (Windows NT 6.2; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0',
            'referer': f'https://t.me/{channel}/{post}?embed=1',
            'cookie': cookie}, proxies={'https': proxy})
        return r.text
    except Exception as e:
        return False

def run(channel, post, proxy):
    max_threads.acquire()
    data = fetch_data(channel, post, 'https://' + proxy)
    if isinstance(data, dict):
        response = add_view_to_post(channel, post, data['key'], data['cookie'], 'https://' + proxy)
        if response is not False:
            print(f'Proxy {proxy} finished its job successfully!')
    max_threads.release()
    print(f'Thread with proxy {proxy} has been terminated.')

# Start threads for each proxy
threads = []
for proxy in proxies:
    p = proxy.split('\n')[0]
    thread = threading.Thread(target=run, args=(sys.argv[1], sys.argv[2], p))
    threads.append(thread)
    thread.start()
    print(f'Started new thread with proxy {p}')

# Join all threads
for thread in threads:
    thread.join()

print("All threads finished execution.")
