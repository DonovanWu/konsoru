"""
A console application to lookup MAC-Vendor mapping.
Preferably run with root privilege...

Motivation
----------------
When I do arp-scan, I often find it bothering to see "(Unknown)" in the result.
However, sometimes you can look up the MAC address online.
It's just that local ieee-oui.txt and ieee-iab.txt files are not up to date.
So I made a console to look them up conveniently.

Demo
----------------
There won't be a demo this time around...
Explore how to use the script by yourself! Or just read the source code.
That's why it is called "advanced.py". It is meant for advanced users!

Suggestions
----------------
Turn on --debug and try to break it, and see what's different.
For example, set the timeout to be really low and then lookup via network.
"""

import os, json, argparse, random
import requests
from urllib.parse import urlparse

from konsoru import CLI
from konsoru import config
from konsoru.decorators import description, parameter
from konsoru.utils import ask_yes_or_no

DEFAULT_OUI_FILES = [
    '/usr/share/arp-scan/ieee-oui.txt',
    '/usr/local/share/arp-scan/ieee-oui.txt',
]
DEFAULT_IAB_FILES = [
    '/usr/share/arp-scan/ieee-iab.txt',
    '/usr/local/share/arp-scan/ieee-iab.txt',
]
RANDOM_USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:64.0) Gecko/20100101 Firefox/64.0',

    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/71.0.3578.98 Safari/537.36',

    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu '
    'Chromium/74.0.3729.169 Chrome/74.0.3729.169 Safari/537.36',

    'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; KB974488; rv:11.0) like Gecko',

    'Mozilla/5.0 (Linux; Android 8.0.0; ALP-AL00 Build/HUAWEIALP-AL00) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Version/4.0 Mobile Safari/537.36',

    'curl/7.64.0',

    'Wget/1.20.1 (linux-gnu)',

    'TROLLOLOL',
]


class KindlyRemind(Exception):
    pass


class MacAddress:
    def __init__(self, mac_addr):
        # polymorphism
        if isinstance(mac_addr, int):
            mac_addr = '%012x' % mac_addr
        elif isinstance(mac_addr, MacAddress):
            mac_addr = str(mac_addr)

        if ':' in mac_addr:
            self.delimiter = ':'
        elif '-' in mac_addr:
            self.delimiter = '-'
        else:
            self.delimiter = ''

        self.hex = mac_addr.lower().replace(self.delimiter, '')

        if len(self.hex) != 12 or not all(ch in '0123456789abcdef' for ch in self.hex):
            raise ValueError('Illegal MAC address: ' + mac_addr)

        if self.hex.startswith('0050c2') or self.hex.startswith('40d855'):
            self.prefix = self.hex[:9]
            self.category = 'iab'
        else:
            self.prefix = self.hex[:6]
            self.category = 'oui'

        self.numeric = int(self.hex, 16)

    def __str__(self):
        return self.delimiter.join(self.hex[i:i+2] for i in range(0, len(self.hex), 2))

    def print_info(self):
        print('MAC address: ' + self.__str__())
        print('Prefix: ' + self.prefix)
        print('Decimal: ' + str(self.numeric))
        print('Belongs to: ' + self.category)


@description('Load MAC-Vendor mapping data from OUI or IAB file.')
def load_mapping(filename):
    global prefix_mapping
    prev_len = len(prefix_mapping)
    print('Loading from file: %s' % filename)
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if line == '' or line[0] == '#':
                continue
            prefix, vendor = line.split(maxsplit=1)
            prefix = prefix.lower()
            prefix_mapping[prefix] = vendor
        print('Successfully loaded %d new pairs of mapping!' % (len(prefix_mapping) - prev_len))


@description('Set proxy used to send the MAC vendor lookup request.')
@parameter('proxy', metavar='url', help='Proxy URL. E.g. socks5h://127.0.0.1:1080')
def set_proxy(proxy):
    global proxies

    # lazily check if proxy url is legal
    o = urlparse(proxy)
    allowed_schemes = ['http', 'https', 'socks4', 'socks5', 'socks5h']
    if o.scheme not in allowed_schemes:
        raise KindlyRemind('Available schemes: %s' % ', '.join(allowed_schemes))

    proxies = {
        'http': proxy,
        'https': proxy,
    }

    print('Proxy set!')


@description('Spoof the User-Agent in the HTTP header of the MAC vendor lookup request.')
@parameter('agent', metavar='user-agent')
@parameter('rand', help="Choose a random user agent.")
def set_agent(agent=None, rand=False):
    global headers
    if not agent and rand:
        agent = random.choice(RANDOM_USER_AGENTS)
    if agent is None:
        raise KindlyRemind('User-Agent is not specified. Nothing is done.')

    if headers is None:
        headers = {}
    headers['User-Agent'] = agent
    print('Set User-Agent to: "%s"' % agent)


@description('Set request timeout.')
def set_timeout(seconds):
    global timeout
    timeout = float(seconds)
    print('timeout = %ss' % timeout)


@description('Reset all settings.')
def reset():
    global proxies, headers, timeout
    proxies = None
    headers = None
    timeout = None


@description('Show newly learned MAC-Vendor mapping.')
def show_learned():
    for prefix in new_mappings:
        vendor = prefix_mapping[prefix]
        print('%s\t%s' % (prefix, vendor))


@description('Display request settings.')
def show_settings():
    print('Settings')
    print('========')
    if proxies is not None:
        print('[Proxy]')
        for proto, url in proxies.items():
            print('proxy: ' + url)
            break
    if headers is not None:
        print('[HTTP header] (additional items)')
        for key, val in headers.items():
            print('%s: %s' % (key, val))
    if timeout is not None:
        print('[Timeout]')
        print('timeout = %ss' % timeout)
    if proxies is None and headers is None and timeout is None:
        print('(None)')


def lookup(mac_addr):
    global new_mappings, prefix_mapping

    mac_addr = MacAddress(mac_addr)
    prefix = mac_addr.prefix
    if prefix in prefix_mapping:
        print(prefix_mapping[prefix])
        return

    print("Failed to find the given MAC's prefix in the known list. Trying to look up online...")

    kwargs = {}
    if proxies is not None:
        kwargs['proxies'] = proxies
    if headers is not None:
        kwargs['headers'] = headers
    if timeout is not None:
        kwargs['timeout'] = timeout

    resp = requests.get('https://macvendors.co/api/%s' % mac_addr, **kwargs)

    if resp.ok:
        obj = json.loads(resp.text)
        result = obj['result']
        if 'error' in result:
            print(result['error'])
            return
        prefix, vendor = result['mac_prefix'], result['company']
        prefix = prefix.lower().replace(':', '')
        if prefix not in prefix_mapping:
            prefix_mapping[prefix] = vendor
            new_mappings.add(prefix)
        print(vendor)
    else:
        raise KindlyRemind('Lookup server returned HTTP code: %d' % resp.status_code)


@description('Update the original OUI and IAB files.')
def update():
    global new_mappings
    if not ask_yes_or_no("This is going to overwrite the OUI and IAB files you're using. Are you sure?"):
        raise KindlyRemind('Operation canceled by user!')

    if ouifile is None:
        fname_oui = './ieee-oui.txt'
        print("You're not using an OUI file... Saving to current directory...")
    else:
        fname_oui = ouifile
    if iabfile is None:
        fname_iab = './ieee-iab.txt'
        print("You're not using an IAB file... Saving to current directory...")
    else:
        fname_iab = iabfile

    with open(fname_oui, 'a') as foui, open(fname_iab, 'a') as fiab:
        for prefix in new_mappings:
            vendor = prefix_mapping[prefix]
            if len(prefix) == 6:
                foui.write('%s\t%s\n' % (prefix.upper(), vendor))
            elif len(prefix) == 9:
                fiab.write('%s\t%s\n' % (prefix.upper(), vendor))

    new_mappings.clear()
    print('Done!')


parser = argparse.ArgumentParser()
parser.add_argument('--debug', action='store_true', help='Prints more verbose information.')
parser.add_argument('--ouifile', action='store', required=False, default=None, metavar='filename')
parser.add_argument('--iabfile', action='store', required=False, default=None, metavar='filename')
args = parser.parse_args()

debug = args.debug
ouifile = args.ouifile
iabfile = args.iabfile

prefix_mapping = {}  # prefix -> vendor
new_mappings = set()

# requests parameters
proxies = None
headers = None
timeout = None

# load MAC-Vendor mapping
if config.system != 'windows':
    if ouifile is None:
        for fname in DEFAULT_OUI_FILES:
            if os.path.isfile(fname):
                ouifile = fname
                break
    if iabfile is None:
        for fname in DEFAULT_IAB_FILES:
            if os.path.isfile(fname):
                iabfile = fname
                break
if ouifile is not None:
    load_mapping(ouifile)
if iabfile is not None:
    load_mapping(iabfile)

# memory
random_mac = MacAddress(random.randint(0, 2**48 - 1))
random_mac.delimiter = ':'

config.settings['shell']['allowed_commands']['unix'].append('arp-scan')  # you need to have it to use it...
cli = CLI(prompt='$ ', goodbye_msg='See you later, alligator!',
          enable_traceback=debug, enable_shell=True, enable_eof_exit_confirmation=True)
cli.add_function(lookup)
cli.add_function(update)
cli.add_function(load_mapping, name='load')
cli.add_function(set_proxy, name='set proxy')
cli.add_function(set_agent, name='set agent')  # just for fun
cli.add_function(set_timeout, name='set timeout')
cli.add_function(show_learned, name='show learned')
cli.add_function(show_settings, name='show settings')
cli.add_function(random_mac.print_info, name='_(:3JL)_')
cli.add_exception_behavior(KindlyRemind, lambda e: print(str(e)))
cli.loop()
