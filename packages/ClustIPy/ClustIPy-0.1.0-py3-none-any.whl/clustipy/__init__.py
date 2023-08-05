import numpy as np
from sklearn.cluster import KMeans, AgglomerativeClustering
from netaddr import IPAddress, IPNetwork


def agglomerative(ipaddr: [IPAddress], max_n_clusters):
    hie = AgglomerativeClustering(n_clusters=max_n_clusters).fit(np.array([[int(_)] for _ in ipaddr]))
    cidrs = []
    for c in range(max_n_clusters):
        members = np.array(ipaddr)[hie.labels_ == c]
        xor = int(min(members)) ^ int(max(members))
        xor = f"{xor:032b}"
        plen = 32 if xor.find('1') == -1 else xor.find('1')
        cidrs.append(IPNetwork(f"{max(members)}/{plen}").cidr)
    cidrs = sorted(cidrs)

    aggr = []
    for ip in ipaddr:
        a = [_ for _ in cidrs if ip in _]
        assert len(a) >= 1
        aggr.append(a[0])
    aggr = sorted(list(set(aggr)))

    return aggr


def kmeans(ipaddr: [IPAddress], max_n_clusters):
    hie = KMeans(n_clusters=max_n_clusters).fit(np.array([[int(_)] for _ in ipaddr]))
    cidrs = []
    for c in range(max_n_clusters):
        members = np.array(ipaddr)[hie.labels_ == c]
        xor = int(min(members)) ^ int(max(members))
        xor = f"{xor:032b}"
        plen = 32 if xor.find('1') == -1 else xor.find('1')
        cidrs.append(IPNetwork(f"{max(members)}/{plen}").cidr)
    cidrs = sorted(cidrs)

    aggr = []
    for ip in ipaddr:
        a = [_ for _ in cidrs if ip in _]
        assert len(a) >= 1
        aggr.append(a[0])
    aggr = sorted(list(set(aggr)))

    return aggr
