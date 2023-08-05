from netaddr import IPAddress
import click

import clustipy


@click.command()
@click.argument('infile', type=click.File())
@click.option('--cluster', help='Max number of clusters', required=True, type=int)
@click.option('--algorithm', help='Clustering algorithm (default is `agglomerative`)',
              type=click.Choice(['agglomerative', 'kmeans']), default='agglomerative')
def main(infile, cluster, algorithm):
    ipaddr = [IPAddress(_) for _ in infile.readlines()]
    result = None
    if algorithm == 'agglomerative':
        result = clustipy.agglomerative(ipaddr, cluster)
    elif algorithm == 'kmeans':
        result = clustipy.kmeans(ipaddr, cluster)

    for r in result:
        print(r)


if __name__ == '__main__':
    main()
