import random

import requests
from netaddr import IPNetwork


def generate_test_addresses():
    prefixes = requests.get('https://ip-ranges.amazonaws.com/ip-ranges.json').json()['prefixes']
    nets = [IPNetwork(_['ip_prefix']) for _ in prefixes if _['region'].startswith('ap-northeast-')]
    addr = [random.choice(random.choice(nets)) for _ in range(200)]
    for a in addr:
        print(a)
